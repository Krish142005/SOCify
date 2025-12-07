"""
Grok Patterns for Log Parsing
Regular expression patterns for common log formats
"""

# Base patterns
USERNAME = r'[a-zA-Z0-9._-]+'
USER = USERNAME
WORD = r'\b\w+\b'
NOTSPACE = r'\S+'
SPACE = r'\s*'
DATA = r'.*?'
GREEDYDATA = r'.*'
QUOTEDSTRING = r'"(?:[^"\\]|\\.)*"'
INT = r'[+-]?(?:[0-9]+)'
NUMBER = r'(?:[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+))'
BASE10NUM = NUMBER

# Network patterns
IP = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
IPV4 = IP
IPV6 = r'(?:(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|(?:[0-9A-Fa-f]{1,4}:){1,7}:|(?:[0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4})'
HOSTNAME = r'\b(?:[0-9A-Za-z][0-9A-Za-z-]{0,62})(?:\.(?:[0-9A-Za-z][0-9A-Za-z-]{0,62}))*\.?\b'
PORT = r'\b(?:[0-9]{1,5})\b'
HOSTPORT = f'{HOSTNAME}:{PORT}'

# Date/Time patterns
MONTH = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b'
MONTHNUM = r'(?:0?[1-9]|1[0-2])'
MONTHDAY = r'(?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9])'
DAY = r'(?:Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)'
YEAR = r'(?:\d{4})'
HOUR = r'(?:2[0123]|[01]?[0-9])'
MINUTE = r'(?:[0-5][0-9])'
SECOND = r'(?:(?:[0-5]?[0-9]|60)(?:[:.,][0-9]+)?)'
TIME = f'{HOUR}:{MINUTE}(?::{SECOND})?'

# Syslog patterns
SYSLOGTIMESTAMP = f'{MONTH} +{MONTHDAY} {TIME}'
SYSLOGPROG = f'{WORD}(?:\\[{INT}\\])?'
SYSLOGHOST = HOSTNAME
SYSLOGFACILITY = r'<[0-9]+>'

# HTTP patterns
URIPROTO = r'[A-Za-z]+(?:\+[A-Za-z+]+)?'
URIHOST = f'{HOSTNAME}(?::{PORT})?'
URIPATH = r'(?:/[A-Za-z0-9$.+!*\'(){},~:;=@#%_\-]*)*'
URIPARAM = r'\?[A-Za-z0-9$.+!*\'|(){},~@#%&/=:;_?\-\[\]]*'
URIPATHPARAM = f'{URIPATH}(?:{URIPARAM})?'
URI = f'{URIPROTO}://{URIHOST}{URIPATH}(?:{URIPARAM})?'

# HTTP methods and status
HTTPMETHOD = r'(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH|TRACE|CONNECT)'
HTTPVERSION = r'HTTP/[0-9.]+'
HTTPSTATUS = r'[0-9]{3}'

# Compiled patterns for common log formats
PATTERNS = {
    # Syslog format: Dec 10 06:55:46 server sshd[1234]: Failed password for admin from 192.168.1.100
    "SYSLOG": (
        f'(?P<timestamp>{SYSLOGTIMESTAMP})\\s+'
        f'(?P<host>{HOSTNAME})\\s+'
        f'(?P<process>{WORD})(?:\\[(?P<pid>{INT})\\])?:\\s+'
        f'(?P<message>{GREEDYDATA})'
    ),
    
    # Apache/Nginx access log: 192.168.1.1 - - [10/Dec/2024:06:55:46 +0000] "GET /index.html HTTP/1.1" 200 1234
    "APACHE_ACCESS": (
        f'(?P<client_ip>{IP})\\s+'
        f'(?P<ident>{NOTSPACE})\\s+'
        f'(?P<auth>{NOTSPACE})\\s+'
        f'\\[(?P<timestamp>[^\\]]+)\\]\\s+'
        f'"(?P<method>{HTTPMETHOD})\\s+'
        f'(?P<path>{URIPATHPARAM})\\s+'
        f'(?P<http_version>{HTTPVERSION})"\\s+'
        f'(?P<status>{HTTPSTATUS})\\s+'
        f'(?P<bytes>{NUMBER})'
    ),
    
    # SSH failed login: Failed password for admin from 192.168.1.100 port 22 ssh2
    "SSH_FAILED_LOGIN": (
        f'Failed password for (?:invalid user )?(?P<user>{USERNAME})\\s+'
        f'from (?P<source_ip>{IP})(?:\\s+port (?P<port>{INT}))?'
    ),
    
    # SSH successful login: Accepted password for admin from 192.168.1.100 port 22 ssh2
    "SSH_SUCCESSFUL_LOGIN": (
        f'Accepted (?:password|publickey) for (?P<user>{USERNAME})\\s+'
        f'from (?P<source_ip>{IP})(?:\\s+port (?P<port>{INT}))?'
    ),
    
    # Windows Event Log (simplified): EventID=4625 User=admin Source=192.168.1.100
    "WINDOWS_EVENT": (
        f'EventID=(?P<event_id>{INT})\\s+'
        f'User=(?P<user>{USERNAME})\\s+'
        f'Source=(?P<source_ip>{IP})'
    ),
    
    # Firewall log: DENY TCP 192.168.1.100:12345 -> 10.0.0.1:80
    "FIREWALL": (
        f'(?P<action>ALLOW|DENY)\\s+'
        f'(?P<protocol>TCP|UDP|ICMP)\\s+'
        f'(?P<source_ip>{IP}):(?P<source_port>{INT})\\s*->\\s*'
        f'(?P<dest_ip>{IP}):(?P<dest_port>{INT})'
    ),
    
    # Process execution: Process started: cmd.exe PID=1234 User=admin
    "PROCESS_START": (
        f'Process started:\\s+(?P<process_name>{NOTSPACE})\\s+'
        f'PID=(?P<pid>{INT})\\s+'
        f'User=(?P<user>{USERNAME})'
    ),
    
    # File operation: File created: C:\Users\admin\document.txt
    "FILE_OPERATION": (
        f'File (?P<operation>created|modified|deleted):\\s+'
        f'(?P<file_path>{GREEDYDATA})'
    ),
}

# Export all patterns
__all__ = ['PATTERNS', 'IP', 'HOSTNAME', 'USERNAME', 'HTTPMETHOD', 'HTTPSTATUS']
