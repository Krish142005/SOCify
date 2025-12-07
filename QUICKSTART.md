# Socify SIEM - Quick Start Guide (Local OpenSearch)

## 🚀 5-Minute Setup

### Step 1: Start OpenSearch (1 minute)

```powershell
cd C:\opensearch-2.11.0\bin
.\opensearch.bat
```

Wait for: `[INFO ][o.o.n.Node] started`

Test: `curl http://localhost:9200`

---

### Step 2: Start Backend (2 minutes)

```powershell
cd C:\Users\91751\OneDrive\Desktop\Socify3\backend

# First time only:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# Every time:
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or simply run:
```powershell
.\start.bat
```

Test: `curl http://localhost:8000/health`

---

### Step 3: Run Agent (1 minute)

```powershell
cd C:\Users\91751\OneDrive\Desktop\Socify3\agent

# Edit config.yaml if needed
.\socify-agent.exe
```

---

### Step 4: Verify (1 minute)

```powershell
# Send test log
curl -X POST http://localhost:8000/api/ingest `
  -H "Content-Type: application/json" `
  -d '{\"raw_log\": \"Failed password for admin from 192.168.1.100\", \"source_type\": \"syslog\", \"metadata\": {\"hostname\": \"test\"}}'

# Check logs
curl "http://localhost:8000/api/search?limit=5"

# Check alerts
curl "http://localhost:8000/api/alerts?limit=5"
```

---

## ✅ You're Done!

### Access Points

- **OpenSearch**: http://localhost:9200
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

### What's Running

1. ✅ OpenSearch (port 9200) - Log storage
2. ✅ Backend API (port 8000) - Processing & rules
3. ✅ Agent - Log collection

---

## 📊 View Your Data

### OpenSearch Queries

```powershell
# View all logs
curl "http://localhost:9200/socify-logs-*/_search?pretty&size=10"

# View all alerts
curl "http://localhost:9200/socify-alerts-*/_search?pretty&size=10"

# Count logs
curl "http://localhost:9200/socify-logs-*/_count"

# List indices
curl "http://localhost:9200/_cat/indices?v"
```

### Backend API

```powershell
# Search logs with filters
curl "http://localhost:8000/api/search?event_action=ssh_login_failed&limit=10"

# Get alerts by severity
curl "http://localhost:8000/api/alerts?severity=high&limit=10"

# Get alert statistics
curl "http://localhost:8000/api/alerts/stats/summary"
```

---

## 🔧 Configuration

### Backend (.env)

```bash
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_USE_SSL=false
```

### Agent (config.yaml)

```yaml
backend_url: http://localhost:8000/api/ingest

log_files:
  - path: C:\logs\test.log
    type: syslog
```

---

## 🐛 Troubleshooting

### OpenSearch not responding

```powershell
# Check if running
netstat -ano | findstr :9200

# Restart
cd C:\opensearch-2.11.0\bin
.\opensearch.bat
```

### Backend connection error

```powershell
# Check OpenSearch
curl http://localhost:9200

# Check .env file
type backend\.env

# Restart backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Agent not sending logs

```powershell
# Check backend
curl http://localhost:8000/health

# Check config.yaml
type agent\config.yaml

# Check log file exists
dir C:\logs\test.log
```

---

## 📚 Next Steps

1. **Add Log Sources**: Edit `agent/config.yaml`
2. **Customize Rules**: Edit `backend/app/rules/rules.json`
3. **Create Dashboards**: Install OpenSearch Dashboards
4. **Monitor**: Check `http://localhost:8000/api/alerts`

---

## 📖 Full Documentation

- [Complete Setup Guide](docs/LOCAL_SETUP.md)
- [Architecture](docs/architecture.md)
- [README](README.md)

---

**Need Help?** Check the troubleshooting section above or see [LOCAL_SETUP.md](docs/LOCAL_SETUP.md) for detailed instructions.
