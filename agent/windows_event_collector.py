"""
Windows Event Log Collector Agent
Monitors Windows Event Logs (Application, System, Security) in real-time
and sends them to the Socify SIEM backend for rule matching and alerting.
"""

import win32evtlog
import win32evtlogutil
import win32con
import win32api
import winerror
import time
import json
import requests
import yaml
import logging
import argparse
import socket
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from queue import Queue
from threading import Thread, Event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('windows_event_collector.log')
    ]
)
logger = logging.getLogger(__name__)


class WindowsEventCollector:
    """Collects Windows Event Logs and sends them to Socify backend"""
    
    def __init__(self, config_path: str):
        """Initialize the collector with configuration"""
        self.config = self._load_config(config_path)
        self.backend_url = self.config['backend_url']
        self.batch_size = self.config['agent']['batch_size']
        self.flush_interval = self._parse_duration(self.config['agent']['flush_interval'])
        self.max_retries = self.config['agent']['max_retries']
        
        # Event queue for batching
        self.event_queue = Queue(maxsize=10000)
        
        # Shutdown event
        self.shutdown_event = Event()
        
        # Collect system metadata
        self.metadata = self._collect_metadata()
        
        logger.info(f"Windows Event Collector initialized")
        logger.info(f"Backend URL: {self.backend_url}")
        logger.info(f"Hostname: {self.metadata['hostname']}")
        logger.info(f"Monitoring logs: {[log['name'] for log in self.config['event_logs'] if log['enabled']]}")
    
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Set defaults
            if 'agent' not in config:
                config['agent'] = {}
            config['agent'].setdefault('batch_size', 10)
            config['agent'].setdefault('flush_interval', '5s')
            config['agent'].setdefault('max_retries', 3)
            
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string (e.g., '5s', '1m') to seconds"""
        if duration_str.endswith('s'):
            return int(duration_str[:-1])
        elif duration_str.endswith('m'):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith('h'):
            return int(duration_str[:-1]) * 3600
        return 5  # Default 5 seconds
    
    def _collect_metadata(self) -> Dict[str, Any]:
        """Collect system metadata"""
        hostname = socket.gethostname()
        return {
            'hostname': hostname,
            'os_family': 'windows',
            'os_version': sys.getwindowsversion().major,
            'collector': 'windows_event_collector',
            'tags': ['windows', 'event-log']
        }
    
    def _normalize_event(self, log_name: str, event_record) -> Dict[str, Any]:
        """
        Normalize Windows Event to match rule format
        
        Maps:
        - SourceName → event.source
        - EventID → event.id
        - EventType → event.level
        - TimeGenerated → @timestamp
        - StringInserts → event.message
        """
        try:
            # Get event properties
            event_id = event_record.EventID & 0xFFFF  # Mask to get actual event ID
            source = event_record.SourceName
            time_generated = event_record.TimeGenerated
            event_type = event_record.EventType
            
            # Map event type to level
            level_map = {
                win32con.EVENTLOG_ERROR_TYPE: 'Error',
                win32con.EVENTLOG_WARNING_TYPE: 'Warning',
                win32con.EVENTLOG_INFORMATION_TYPE: 'Information',
                win32con.EVENTLOG_AUDIT_SUCCESS: 'Audit Success',
                win32con.EVENTLOG_AUDIT_FAILURE: 'Audit Failure'
            }
            level = level_map.get(event_type, 'Unknown')
            
            # Get message
            try:
                message = win32evtlogutil.SafeFormatMessage(event_record, log_name)
            except:
                # If message formatting fails, use string inserts
                if event_record.StringInserts:
                    message = ' '.join([str(s) for s in event_record.StringInserts if s])
                else:
                    message = ''
            
            # Build normalized event
            normalized = {
                '@timestamp': time_generated.isoformat(),
                'event': {
                    'source': source,
                    'id': event_id,
                    'level': level,
                    'message': message,
                    'category': event_record.EventCategory,
                    'type': event_type
                },
                'log': {
                    'source': log_name.lower(),  # application, system, security
                    'type': 'windows_event'
                },
                'host': {
                    'name': self.metadata['hostname'],
                    'os': {
                        'family': 'windows',
                        'version': str(self.metadata['os_version'])
                    }
                },
                'agent': {
                    'name': 'windows_event_collector',
                    'type': 'log-collector'
                },
                'tags': self.metadata['tags']
            }
            
            # Add computer name if available
            if hasattr(event_record, 'ComputerName'):
                normalized['host']['name'] = event_record.ComputerName
            
            # Extract additional fields from message if available
            # This helps with rules that check for specific patterns
            if message:
                normalized['event']['original'] = message
                
                # Try to extract common patterns
                if 'user' in message.lower() or 'account' in message.lower():
                    # Simple extraction - can be enhanced
                    words = message.split()
                    for i, word in enumerate(words):
                        if word.lower() in ['user:', 'account:', 'username:']:
                            if i + 1 < len(words):
                                normalized['user'] = {'name': words[i + 1].strip('.,;:')}
                                break
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing event: {e}", exc_info=True)
            return None
    
    def _send_batch(self, events: List[Dict[str, Any]]):
        """Send batch of events to backend"""
        if not events:
            return
        
        payload = {
            'logs': events,
            'source': 'windows_event_collector',
            'metadata': self.metadata
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.backend_url,
                    json=payload,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    logger.info(f"Sent {len(events)} events to backend")
                    return
                else:
                    logger.warning(f"Backend returned {response.status_code}: {response.text}")
                    
            except Exception as e:
                logger.error(f"Failed to send batch (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to send {len(events)} events after {self.max_retries} attempts")
    
    def _batch_sender(self):
        """Background thread that sends batched events"""
        batch = []
        last_flush = time.time()
        
        logger.info("Batch sender thread started")
        
        while not self.shutdown_event.is_set():
            try:
                # Try to get event with timeout
                try:
                    event = self.event_queue.get(timeout=1)
                    batch.append(event)
                except:
                    pass
                
                # Send batch if size reached or flush interval elapsed
                current_time = time.time()
                should_flush = (
                    len(batch) >= self.batch_size or
                    (batch and current_time - last_flush >= self.flush_interval)
                )
                
                if should_flush:
                    self._send_batch(batch)
                    batch = []
                    last_flush = current_time
                    
            except Exception as e:
                logger.error(f"Error in batch sender: {e}", exc_info=True)
        
        # Send remaining events on shutdown
        if batch:
            self._send_batch(batch)
        
        logger.info("Batch sender thread stopped")
    
    def _monitor_event_log(self, log_name: str):
        """Monitor a specific Windows Event Log in real-time"""
        logger.info(f"Starting monitoring for {log_name} log")
        
        try:
            # Open event log
            hand = win32evtlog.OpenEventLog(None, log_name)
            
            # Get current position (read from end)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            # Read most recent event to get current position
            try:
                events = win32evtlog.ReadEventLog(hand, flags, 0, 1)
            except:
                pass
            
            # Now read forwards from current position
            flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            logger.info(f"Monitoring {log_name} log - waiting for new events...")
            
            events_processed = 0
            
            while not self.shutdown_event.is_set():
                try:
                    # Read new events
                    events = win32evtlog.ReadEventLog(hand, flags, 0)
                    
                    if events:
                        for event in events:
                            # Normalize and queue event
                            normalized = self._normalize_event(log_name, event)
                            if normalized:
                                try:
                                    self.event_queue.put(normalized, timeout=1)
                                    events_processed += 1
                                    
                                    if events_processed % 100 == 0:
                                        logger.info(f"{log_name}: Processed {events_processed} events")
                                except:
                                    logger.warning(f"Event queue full, dropping event")
                    else:
                        # No new events, sleep briefly
                        time.sleep(0.5)
                        
                except Exception as e:
                    if isinstance(e, pywintypes.error):
                        # Check if it's just "no more data" error
                        if e.winerror == winerror.ERROR_NO_MORE_ITEMS:
                            time.sleep(0.5)
                            continue
                    logger.error(f"Error reading {log_name} log: {e}")
                    time.sleep(1)
            
            # Close event log
            win32evtlog.CloseEventLog(hand)
            logger.info(f"Stopped monitoring {log_name} log (processed {events_processed} events)")
            
        except Exception as e:
            logger.error(f"Failed to monitor {log_name} log: {e}", exc_info=True)
    
    def start(self):
        """Start collecting Windows Event Logs"""
        logger.info("Starting Windows Event Collector...")
        
        # Check if running as Administrator for Security log
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                logger.warning("Not running as Administrator - Security log may not be accessible")
        except:
            pass
        
        # Start batch sender thread
        sender_thread = Thread(target=self._batch_sender, daemon=True)
        sender_thread.start()
        
        # Start monitoring threads for each enabled log
        monitor_threads = []
        for log_config in self.config['event_logs']:
            if log_config.get('enabled', True):
                log_name = log_config['name']
                thread = Thread(target=self._monitor_event_log, args=(log_name,), daemon=True)
                thread.start()
                monitor_threads.append(thread)
        
        logger.info(f"Monitoring {len(monitor_threads)} event logs. Press Ctrl+C to stop.")
        
        try:
            # Wait for shutdown signal
            while not self.shutdown_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutdown signal received...")
        
        # Signal all threads to stop
        self.shutdown_event.set()
        
        # Wait for threads to finish
        logger.info("Waiting for threads to finish...")
        sender_thread.join(timeout=5)
        for thread in monitor_threads:
            thread.join(timeout=2)
        
        logger.info("Windows Event Collector stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Windows Event Log Collector for Socify SIEM')
    parser.add_argument('--config', default='config_windows.yaml', help='Path to configuration file')
    args = parser.parse_args()
    
    try:
        collector = WindowsEventCollector(args.config)
        collector.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    # Import pywintypes here to avoid circular import
    import pywintypes
    main()
