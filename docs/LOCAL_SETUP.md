# Socify SIEM - Local OpenSearch Setup Guide

## Overview

This guide covers the complete setup of Socify SIEM with **local OpenSearch installation** (no cloud dependencies).

## Prerequisites

### Required Software

1. **OpenSearch 2.11.0** (or compatible version)
   - Location: `C:\opensearch-2.11.0`
   - Download: https://opensearch.org/downloads.html

2. **Python 3.9+**
   - Download: https://www.python.org/downloads/

3. **Go 1.21+** (for agent)
   - Download: https://go.dev/dl/

### System Requirements

- **OS**: Windows 10/11, Linux, or macOS
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk**: 10GB free space
- **Network**: Localhost access to port 9200

---

## Part 1: OpenSearch Setup

### Step 1: Install OpenSearch

```powershell
# Extract OpenSearch ZIP to C:\opensearch-2.11.0
# Your installation is already at this location
```

### Step 2: Configure OpenSearch

Edit `C:\opensearch-2.11.0\config\opensearch.yml`:

```yaml
# Cluster name
cluster.name: socify-cluster

# Node name
node.name: socify-node-1

# Network settings
network.host: localhost
http.port: 9200

# Disable security plugin (for local development)
plugins.security.disabled: true

# Disable SSL
plugins.security.ssl.http.enabled: false
plugins.security.ssl.transport.enabled: false
```

### Step 3: Start OpenSearch

```powershell
# Navigate to OpenSearch bin directory
cd C:\opensearch-2.11.0\bin

# Start OpenSearch
.\opensearch.bat
```

**Wait for startup** (usually 30-60 seconds). You should see:
```
[INFO ][o.o.n.Node] [socify-node-1] started
```

### Step 4: Verify OpenSearch

```powershell
# Test connection
curl http://localhost:9200

# Expected response:
{
  "name" : "socify-node-1",
  "cluster_name" : "socify-cluster",
  "version" : {
    "number" : "2.11.0"
  }
}
```

### Step 5: Create Indices (Optional)

The backend creates indices automatically, but you can create them manually:

```powershell
# Create logs index
curl -X PUT "http://localhost:9200/socify-logs-2024.11" `
  -H "Content-Type: application/json" `
  -d '{
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  }'

# Create alerts index
curl -X PUT "http://localhost:9200/socify-alerts-2024.11" `
  -H "Content-Type: application/json" `
  -d '{
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  }'

# Verify indices
curl "http://localhost:9200/_cat/indices?v"
```

---

## Part 2: Backend Setup

### Step 1: Navigate to Backend Directory

```powershell
cd C:\Users\91751\OneDrive\Desktop\Socify3\backend
```

### Step 2: Create Virtual Environment

```powershell
# Create venv
python -m venv venv

# Activate venv
venv\Scripts\activate

# Verify activation (you should see (venv) in prompt)
```

### Step 3: Install Dependencies

```powershell
# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list
```

Expected packages:
- fastapi
- uvicorn
- opensearch-py
- pydantic
- python-dotenv

### Step 4: Configure Environment

```powershell
# Copy example env file
copy .env.example .env

# Edit .env file (use notepad or your preferred editor)
notepad .env
```

Ensure `.env` contains:
```bash
# Local OpenSearch
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_USE_SSL=false

# Backend Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
LOG_LEVEL=INFO

# Index Prefixes
LOGS_INDEX_PREFIX=socify-logs
ALERTS_INDEX_PREFIX=socify-alerts
```

### Step 5: Verify Rules File

```powershell
# Check that rules.json exists
dir app\rules\rules.json

# If not present, it should have been copied from:
# C:\Users\91751\OneDrive\Desktop\siem_predefined_rules.json
```

### Step 6: Start Backend

```powershell
# Start with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the startup script
.\start.bat
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 7: Test Backend

Open a new terminal and test:

```powershell
# Health check
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "service": "socify-backend",
  "checks": {
    "api": "ok",
    "opensearch": {
      "status": "connected",
      "version": "2.11.0",
      "cluster_name": "socify-cluster",
      "cluster_health": "green"
    }
  }
}

# API documentation
# Open in browser: http://localhost:8000/api/docs
```

---

## Part 3: Agent Setup

### Step 1: Navigate to Agent Directory

```powershell
cd C:\Users\91751\OneDrive\Desktop\Socify3\agent
```

### Step 2: Verify Agent Build

```powershell
# Check if agent is built
dir socify-agent.exe

# If not present, build it:
go build -o socify-agent.exe agent.go
```

### Step 3: Configure Agent

Edit `config.yaml`:

```yaml
backend_url: http://localhost:8000/api/ingest

log_files:
  # Windows Event Logs
  - path: C:\Windows\System32\winevt\Logs\Security.evtx
    type: windows_event
  
  # Or use a test log file
  - path: C:\logs\test.log
    type: syslog

agent:
  batch_size: 10
  flush_interval: 5s
  max_retries: 3
  buffer_size: 1000

metadata:
  hostname: my-laptop
  tags:
    - development
    - windows
```

### Step 4: Create Test Log File (Optional)

```powershell
# Create logs directory
mkdir C:\logs

# Create test log file
echo "Dec 10 06:55:46 server sshd[1234]: Failed password for admin from 192.168.1.100" > C:\logs\test.log
```

### Step 5: Run Agent

```powershell
# Run agent
.\socify-agent.exe

# Expected output:
Socify Agent starting...
Backend URL: http://localhost:8000/api/ingest
Monitoring 1 log files
System Info: Hostname=my-laptop, OS=windows
Starting tail for: C:\logs\test.log (type: syslog)
```

---

## Part 4: Verification

### Test Complete Flow

#### 1. Ingest Test Log

```powershell
curl -X POST http://localhost:8000/api/ingest `
  -H "Content-Type: application/json" `
  -d '{
    "raw_log": "Dec 10 06:55:46 server sshd[1234]: Failed password for admin from 192.168.1.100 port 22 ssh2",
    "source_type": "syslog",
    "metadata": {
      "hostname": "test-server",
      "os_family": "linux"
    }
  }'
```

**Expected response:**
```json
{
  "status": "success",
  "event_id": "abc123...",
  "index": "socify-logs-2024.11",
  "timestamp": "2024-11-22T02:00:00Z"
}
```

#### 2. Search Logs

```powershell
curl "http://localhost:8000/api/search?limit=10"
```

#### 3. Check Alerts

```powershell
curl "http://localhost:8000/api/alerts?limit=10"
```

#### 4. Query OpenSearch Directly

```powershell
# Get all logs
curl "http://localhost:9200/socify-logs-*/_search?pretty"

# Get all alerts
curl "http://localhost:9200/socify-alerts-*/_search?pretty"

# Count documents
curl "http://localhost:9200/socify-logs-*/_count"
```

---

## Part 5: OpenSearch Dashboards (Optional)

### Install OpenSearch Dashboards

1. Download OpenSearch Dashboards 2.11.0
2. Extract to `C:\opensearch-dashboards-2.11.0`
3. Configure `config\opensearch_dashboards.yml`:

```yaml
server.host: "localhost"
server.port: 5601
opensearch.hosts: ["http://localhost:9200"]
opensearch.ssl.verificationMode: none
opensearch.security.enabled: false
```

4. Start Dashboards:

```powershell
cd C:\opensearch-dashboards-2.11.0\bin
.\opensearch-dashboards.bat
```

5. Access: http://localhost:5601

### Create Visualizations

1. Go to **Management** → **Index Patterns**
2. Create pattern: `socify-logs-*`
3. Set time field: `@timestamp`
4. Go to **Discover** to view logs
5. Create dashboards in **Dashboards**

---

## Troubleshooting

### OpenSearch Won't Start

**Issue**: Port 9200 already in use

```powershell
# Check what's using port 9200
netstat -ano | findstr :9200

# Kill the process
taskkill /PID <PID> /F
```

**Issue**: Java not found

```powershell
# Set JAVA_HOME
setx JAVA_HOME "C:\Program Files\Java\jdk-17"
```

### Backend Connection Error

**Issue**: Cannot connect to OpenSearch

```powershell
# Verify OpenSearch is running
curl http://localhost:9200

# Check backend .env file
type .env

# Check backend logs for errors
```

**Issue**: Module not found

```powershell
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Agent Not Sending Logs

**Issue**: Connection refused

```powershell
# Verify backend is running
curl http://localhost:8000/health

# Check config.yaml backend_url
type config.yaml
```

**Issue**: File not found

```powershell
# Verify log file path exists
dir C:\logs\test.log

# Check file permissions
```

### No Alerts Generated

**Issue**: Rules not loading

```powershell
# Verify rules.json exists
dir backend\app\rules\rules.json

# Check backend logs for rule loading errors
```

**Issue**: Events not matching rules

```powershell
# Check normalized event format
curl "http://localhost:8000/api/search?limit=1"

# Verify rule conditions match event fields
```

---

## Performance Tuning

### OpenSearch Performance

Edit `C:\opensearch-2.11.0\config\jvm.options`:

```
# Increase heap size for better performance
-Xms2g
-Xmx2g
```

### Backend Performance

```bash
# Use multiple workers
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Agent Performance

Edit `config.yaml`:

```yaml
agent:
  batch_size: 50      # Increase batch size
  flush_interval: 10s # Increase flush interval
  buffer_size: 5000   # Increase buffer
```

---

## Maintenance

### Index Management

```powershell
# List all indices
curl "http://localhost:9200/_cat/indices?v"

# Delete old indices
curl -X DELETE "http://localhost:9200/socify-logs-2024.10"

# Optimize indices
curl -X POST "http://localhost:9200/socify-logs-*/_forcemerge?max_num_segments=1"
```

### Backup

```powershell
# Backup OpenSearch data
xcopy /E /I C:\opensearch-2.11.0\data C:\backups\opensearch-data

# Backup rules
copy backend\app\rules\rules.json C:\backups\rules.json
```

### Monitoring

```powershell
# Check cluster health
curl "http://localhost:9200/_cluster/health?pretty"

# Check node stats
curl "http://localhost:9200/_nodes/stats?pretty"

# Check index stats
curl "http://localhost:9200/socify-logs-*/_stats?pretty"
```

---

## Next Steps

1. **Customize Rules**: Edit `backend/app/rules/rules.json`
2. **Add Log Sources**: Update agent `config.yaml`
3. **Create Dashboards**: Use OpenSearch Dashboards
4. **Set Up Alerts**: Configure alert notifications
5. **Monitor Performance**: Check OpenSearch metrics

---

## Support

For issues:
1. Check OpenSearch logs: `C:\opensearch-2.11.0\logs\`
2. Check backend logs in console
3. Check agent logs in console
4. Review this guide's troubleshooting section
