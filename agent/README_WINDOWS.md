# Windows Event Log Collector

Real-time Windows Event Log collection for Socify SIEM.

## Overview

This Python-based agent monitors Windows Event Logs (Application, System, Security) in real-time and sends them to the Socify SIEM backend for rule matching and alert generation.

## Features

- ✅ Real-time monitoring of Windows Event Logs
- ✅ Automatic field normalization to match detection rules
- ✅ Batch sending for efficient network usage
- ✅ Automatic retry on connection failures
- ✅ Supports Application, System, and Security logs

## Requirements

- **Python 3.8 or higher**
- **Administrator privileges** (required for Security log access)
- **Active Socify backend** (running on http://localhost:8000)

## Installation

### 1. Install Python Dependencies

```powershell
cd agent
pip install -r requirements.txt
```

The following packages will be installed:
- `pywin32` - Windows Event Log API
- `requests` - HTTP client
- `pyyaml` - Configuration file parsing
- `python-dateutil` - Date/time handling

### 2. Configure the Agent

Edit `config_windows.yaml` if needed:

```yaml
backend_url: "http://localhost:8000/api/ingest"

event_logs:
  - name: "Application"
    enabled: true
  - name: "System"
    enabled: true
  - name: "Security"
    enabled: true

agent:
  batch_size: 10          # Number of logs to batch before sending
  flush_interval: "5s"    # Maximum time to wait before sending batch
  max_retries: 3          # Number of retry attempts on failure
```

## Usage

### Quick Start (Recommended)

1. **Right-click** `start_windows_collector.bat` → **Run as Administrator**

This script will:
- Check for Python installation
- Install dependencies if needed
- Warn if not running as Administrator
- Start the collector

### Manual Start

```powershell
# Run as Administrator!
python windows_event_collector.py --config config_windows.yaml
```

### Verify It's Working

1. **Check Console Output** - You should see:
   ```
   Windows Event Collector initialized
   Monitoring logs: ['Application', 'System', 'Security']
   Monitoring Application log - waiting for new events...
   Monitoring System log - waiting for new events...
   Monitoring Security log - waiting for new events...
   ```

2. **Generate a Test Event**:
   ```powershell
   # Create a test Application event
   eventcreate /L Application /T ERROR /ID 1000 /SO TestApp /D "Test error message for Socify SIEM"
   ```

3. **Check Backend Logs** - Backend should log:
   ```
   Indexed event: xyz123 to socify-logs-2025.11
   ```

4. **Check Frontend** - Navigate to http://localhost:3000/monitor
   - You should see the event appear in real-time
   - If a rule matches, an alert will appear

## Field Mapping

The collector normalizes Windows Event Logs to match your detection rules:

| Windows Event Field | Normalized Field | Example |
|---------------------|------------------|---------|
| `SourceName` | `event.source` | `.NET Runtime`, `Kernel-Power` |
| `EventID` | `event.id` | `4625`, `41`, `1000` |
| `EventType` | `event.level` | `Error`, `Warning`, `Information` |
| `TimeGenerated` | `@timestamp` | `2025-11-22T09:50:00Z` |
| `Message` | `event.message` | Full event message |
| `Log Name` | `log.source` | `application`, `system`, `security` |

## Troubleshooting

### "Not running as Administrator"

**Problem**: Security logs cannot be read without admin privileges.

**Solution**: Right-click the script → "Run as Administrator"

### "Failed to connect to backend"

**Problem**: Backend is not running or wrong URL.

**Solution**:
1. Check backend is running: `http://localhost:8000/health`
2. Update `backend_url` in `config_windows.yaml`

### "No events being sent"

**Possible causes**:
1. **No new events** - The collector only sends NEW events, not historical ones
2. **Generate a test event**:
   ```powershell
   eventcreate /L Application /T ERROR /ID 1000 /SO TestApp /D "Test"
   ```

### "Events sent but no alerts"

**Possible causes**:
1. **No matching rules** - Check `rules.json` has rules for your event
2. **Field mismatch** - Check debug logs to see rule evaluation

## Event Examples

### Application Log Event (Normalized)
```json
{
  "@timestamp": "2025-11-22T09:50:00Z",
  "event": {
    "source": "Application Error",
    "id": 1000,
    "level": "Error",
    "message": "Faulting application name: app.exe"
  },
  "log": {
    "source": "application",
    "type": "windows_event"
  },
  "host": {
    "name": "DESKTOP-ABC123"
  }
}
```

This would match rule `A002` (Application Error Spike) if threshold is met.

### Security Log Event (Normalized)
```json
{
  "@timestamp": "2025-11-22T09:50:00Z",
  "event": {
    "source": "Microsoft-Windows-Security-Auditing",
    "id": 4625,
    "level": "Audit Failure",
    "message": "An account failed to log on"
  },
  "log": {
    "source": "security",
    "type": "windows_event"
  }
}
```

This would match rules `SEC001` (Multiple Failed Logons) or `SEC002` (Brute Force).

## Matching Rules

The agent sends normalized logs that match against 70+ detection rules:

- **Application Rules (A001-A015)**: .NET crashes, installers, Outlook, SQL Server
- **System Rules (S001-S020)**: Disk errors, drivers, services, network
- **Security Rules (SEC001-SEC025)**: Failed logins, privilege escalation, audit events
- **USB Rules (USB001-USB010)**: Device insertion, suspicious USB devices

See `backend/app/rules/rules.json` for the complete rule list.

## Logs

- **Console**: Real-time status and events
- **windows_event_collector.log**: Detailed log file

## Stopping the Collector

Press `Ctrl+C` in the console window.

The collector will:
1. Send any remaining batched events
2. Close Windows Event Log handles
3. Shut down gracefully

## Advanced Configuration

### Monitor Only Specific Logs

```yaml
event_logs:
  - name: "Application"
    enabled: true
  - name: "System"
    enabled: false  # Disable System log monitoring
  - name: "Security"
    enabled: true
```

### Adjust Batch Settings

For high-volume environments:
```yaml
agent:
  batch_size: 50          # Larger batches
  flush_interval: "10s"   # Longer flush interval
  max_retries: 5
```

For real-time alerting:
```yaml
agent:
  batch_size: 1           # Send immediately
  flush_interval: "1s"    # Minimal delay
```

## Performance

- **CPU Usage**: ~1-2% idle, up to 5% under heavy load
- **Memory**: ~50-100 MB
- **Network**: Minimal (batched sends)
- **Event Processing**: ~1000 events/second

## Security Considerations

1. **Admin Privileges**: Only grant to trusted systems
2. **Network**: Uses HTTP by default (consider HTTPS in production)
3. **Sensitive Data**: Event messages may contain sensitive information
4. **Log Retention**: Backend stores all events in OpenSearch

## Next Steps

1. Start the backend: `cd backend && start.bat`
2. Start the frontend: `cd frontend && npm run dev`
3. Start the collector: `cd agent && start_windows_collector.bat` (as Admin)
4. Open monitor dashboard: http://localhost:3000/monitor
5. Generate test events and watch them appear in real-time!

## Support

For issues or questions, check:
- Backend logs: `backend/logs/`
- Collector logs: `agent/windows_event_collector.log`
- Frontend console: Browser Developer Tools (F12)
