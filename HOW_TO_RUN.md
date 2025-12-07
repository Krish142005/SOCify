# 🚀 Socify SIEM - Complete Running Guide

> **Step-by-step guide to run the complete Socify SIEM platform**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Start OpenSearch](#step-1-start-opensearch)
3. [Step 2: Start Backend](#step-2-start-backend)
4. [Step 3: Start Agent](#step-3-start-agent)
5. [Step 4: Start Frontend (Optional)](#step-4-start-frontend)
6. [Verification Steps](#verification-steps)
7. [Troubleshooting](#troubleshooting)
8. [Demo Preparation](#demo-preparation)

---

## Prerequisites {#prerequisites}

### ✅ Check karo ye sab installed hai:

1. **OpenSearch 2.11.0**
   - Location: `C:\opensearch-2.11.0`
   - Check: `dir C:\opensearch-2.11.0`

2. **Python 3.9+**
   - Check: `python --version`
   - Should show: `Python 3.9.x` or higher

3. **Go 1.21+** (Optional - Agent already compiled hai)
   - Check: `go version`
   - Should show: `go1.21` or higher

4. **Node.js** (Frontend ke liye)
   - Check: `node --version`
   - Should show: `v16.x` or higher

### 📁 Required Files Check:

```powershell
# Socify folder mein ye sab hona chahiye:
cd C:\Users\91751\Downloads\Socify

# Check structure
dir backend
dir agent
dir frontend
dir backend\app\rules\rules.json
```

---

## STEP 1: Start OpenSearch {#step-1-start-opensearch}

### 🔍 OpenSearch ko start karo (Terminal 1)

```powershell
# Terminal 1 kholo (PowerShell)
# OpenSearch directory mein jao
cd C:\opensearch-2.11.0\bin

# OpenSearch start karo
.\opensearch.bat
```

### ⏱️ Wait karo:

- OpenSearch start hone mein **30-60 seconds** lagta hai
- Screen par bahut saare logs dikhenge
- Jab ye message dikhe toh ready hai:
  ```
  [INFO] Node started
  [INFO] Cluster health status changed from [RED] to [GREEN]
  ```

### ✅ Verify karo OpenSearch running hai:

```powershell
# Naya terminal kholo (Terminal 2 temporarily)
curl http://localhost:9200
```

**Expected Response:**
```json
{
  "name" : "...",
  "cluster_name" : "opensearch",
  "version" : {
    "number" : "2.11.0"
  }
}
```

✅ **Agar ye response aaya toh OpenSearch ready hai!**

### 🔴 Troubleshooting (agar start nahi hua):

```powershell
# Check if port 9200 already in use
netstat -ano | findstr :9200

# Agar koi process hai toh kill karo
taskkill /PID <process_id> /F

# Check OpenSearch logs
type C:\opensearch-2.11.0\logs\opensearch.log
```

---

## STEP 2: Start Backend {#step-2-start-backend}

### 🐍 Python Backend ko start karo (Terminal 2)

```powershell
# Terminal 2 (ya naya terminal) kholo
cd C:\Users\91751\Downloads\Socify\backend
```

### Option A: Agar virtual environment already hai

```powershell
# Virtual environment activate karo
.\venv\Scripts\activate

# Terminal mein (venv) dikhai dega

# Backend start karo
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option B: Agar pehli baar setup kar rahe ho

```powershell
# Step 1: Virtual environment banao
python -m venv venv

# Step 2: Activate karo
.\venv\Scripts\activate

# Step 3: Dependencies install karo
pip install -r requirements.txt

# Step 4: Backend start karo
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### ⏱️ Wait karo:

Backend start hone mein **5-10 seconds** lagta hai

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Loaded 70 detection rules
```

### ✅ Verify karo Backend running hai:

```powershell
# Naya terminal kholo (Terminal 3 temporarily)
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "opensearch": "connected"
}
```

✅ **Backend ready hai!**

### 🔴 Troubleshooting:

```powershell
# Agar OpenSearch connection error aaye
# 1. OpenSearch running hai verify karo (Step 1)
# 2. Port 9200 accessible hai check karo
curl http://localhost:9200

# Agar port 8000 already in use
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

---

## STEP 3: Start Agent {#step-3-start-agent}

### 🤖 Go Agent ko start karo (Terminal 3)

```powershell
# Naya terminal kholo (Terminal 3 or 4)
cd C:\Users\91751\Downloads\Socify\agent
```

### Option A: Pre-compiled binary use karo (Recommended)

```powershell
# Direct agent run karo
.\socify-agent.exe
```

### Option B: Source se run karo

```powershell
# Go se direct run karo
go run agent.go
```

### 📊 Kya dikhega:

Agent start hone ke baad ye messages dikhenge:
```
[INFO] Socify Agent started
[INFO] Backend URL: http://localhost:8000/api/ingest
[INFO] Monitoring 10 log files
[INFO] Reading logs...
[INFO] Sending batch of 10 logs
[INFO] Successfully sent logs to backend
```

### ✅ Verify karo Agent working hai:

**Agent terminal mein:**
- `Sending batch...` messages dikhai dene chahiye
- `Successfully sent` messages dikhai dene chahiye

**Backend terminal mein:**
- `Received log from agent` messages dikhai dene chahiye
- `Indexed document to socify-logs-*` dikhai dena chahiye

✅ **Agent successfully logs bhej raha hai!**

### 🔴 Troubleshooting:

```powershell
# Agar "connection refused" error aaye
# Backend running hai check karo
curl http://localhost:8000/health

# Config file check karo
type config.yaml
# backend_url: http://localhost:8000/api/ingest (ye hona chahiye)

# Windows Event Logs accessible hain check karo (Admin rights chahiye)
# Agent ko "Run as Administrator" karo
```

---

## STEP 4: Start Frontend (Optional) {#step-4-start-frontend}

### 💻 Next.js Frontend ko start karo (Terminal 4 or 5)

```powershell
# Naya terminal kholo
cd C:\Users\91751\Downloads\Socify\frontend
```

### Option A: Agar dependencies already installed hain

```powershell
# Development server start karo
npm run dev
```

### Option B: Pehli baar setup

```powershell
# Step 1: Dependencies install karo (5-10 minutes lagega)
npm install

# Step 2: Dev server start karo
npm run dev
```

### ⏱️ Wait karo:

Frontend build hone mein **10-20 seconds** lagta hai

**Expected Output:**
```
> socify-frontend@1.0.0 dev
> next dev

- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled successfully
```

### ✅ Access Frontend:

```
Browser mein jao: http://localhost:3000
```

**Pages jo dikhne chahiye:**
- 📊 **Dashboard** - Statistics aur overview
- 📝 **Logs** - All logs with search/filter
- 🚨 **Alerts** - Generated alerts
- 📋 **Rules** - Detection rules

✅ **Frontend ready hai!**

---

## Verification Steps {#verification-steps}

### 🔍 Complete System Check

### 1. OpenSearch Verification

```powershell
# Health check
curl http://localhost:9200/_cluster/health

# Indices check - socify indices dikhne chahiye
curl http://localhost:9200/_cat/indices?v
```

**Expected Output:**
```
yellow open socify-logs-2024.12   ...
yellow open socify-alerts-2024.12 ...
```

### 2. Backend API Verification

```powershell
# Health endpoint
curl http://localhost:8000/health

# Search logs
curl http://localhost:8000/api/search

# Get alerts
curl http://localhost:8000/api/alerts

# Get rules
curl http://localhost:8000/api/rules
```

### 3. Data Flow Verification

```powershell
# OpenSearch mein logs check karo
curl "http://localhost:9200/socify-logs-*/_search?size=5&pretty"

# Latest alerts check karo
curl "http://localhost:9200/socify-alerts-*/_search?size=5&pretty"
```

### 4. Complete Flow Test

```powershell
# Test log ingest karo manually
curl -X POST http://localhost:8000/api/ingest `
  -H "Content-Type: application/json" `
  -d '{
    "raw_log": "Failed password for admin from 192.168.1.100",
    "source_type": "syslog",
    "metadata": {"hostname": "test-server"}
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Log ingested successfully"
}
```

---

## Troubleshooting {#troubleshooting}

### ❌ Common Issues aur Solutions

### Issue 1: OpenSearch start nahi ho raha

**Symptoms:**
- "Address already in use" error
- Port 9200 accessible nahi hai

**Solution:**
```powershell
# Port check karo
netstat -ano | findstr :9200

# Process kill karo
taskkill /PID <process_id> /F

# Phir se start karo
cd C:\opensearch-2.11.0\bin
.\opensearch.bat
```

### Issue 2: Backend OpenSearch se connect nahi ho raha

**Symptoms:**
- "Connection refused" error
- Health check fail ho rahi hai

**Solution:**
```powershell
# OpenSearch running hai verify karo
curl http://localhost:9200

# Backend restart karo
# Terminal 2 mein CTRL+C press karo
# Phir se start karo
uvicorn app.main:app --reload
```

### Issue 3: Agent logs nahi bhej raha

**Symptoms:**
- "Connection refused to backend"
- No logs in backend terminal

**Solution:**
```powershell
# Backend running hai check karo
curl http://localhost:8000/health

# Config file verify karo
type agent\config.yaml
# backend_url sahi hona chahiye

# Agent ko Admin rights ke saath run karo
# Right-click → Run as Administrator
```

### Issue 4: Frontend load nahi ho raha

**Symptoms:**
- Blank page
- "Module not found" errors

**Solution:**
```powershell
# Node modules delete karke reinstall karo
cd frontend
rm -r node_modules
rm package-lock.json
npm install
npm run dev
```

### Issue 5: No data dikhai nahi de raha

**Symptoms:**
- Dashboard empty hai
- No logs/alerts

**Solution:**
```powershell
# Agent running hai check karo (Terminal 3)
# Backend logs aa rahe hain check karo (Terminal 2)

# Manually test log bhejo
curl -X POST http://localhost:8000/api/ingest `
  -H "Content-Type: application/json" `
  -d '{"raw_log": "Test log", "source_type": "syslog"}'

# OpenSearch mein data check karo
curl "http://localhost:9200/socify-logs-*/_search?pretty"
```

---

## Demo Preparation {#demo-preparation}

### 🎬 Presentation ke liye Setup

### 5 Minutes Before Presentation:

**Step 1: Sab start karo**
```powershell
# Terminal 1: OpenSearch
cd C:\opensearch-2.11.0\bin
.\opensearch.bat

# Terminal 2: Backend (wait for OpenSearch first!)
cd C:\Users\91751\Downloads\Socify\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 3: Agent (wait for Backend first!)
cd C:\Users\91751\Downloads\Socify\agent
.\socify-agent.exe

# Terminal 4: Frontend
cd C:\Users\91751\Downloads\Socify\frontend
npm run dev
```

**Step 2: Verify sab chal raha hai**
```powershell
curl http://localhost:9200        # OpenSearch
curl http://localhost:8000/health # Backend
# Browser: http://localhost:3000   # Frontend
```

**Step 3: Browser tabs ready rakho**
- Tab 1: Dashboard (http://localhost:3000)
- Tab 2: Logs page (http://localhost:3000/logs)
- Tab 3: Alerts page (http://localhost:3000/alerts)
- Tab 4: OpenSearch (http://localhost:9200/_cat/indices?v)

### Live Demo Script:

**1. Architecture Explanation (2 min)**
- Terminal windows dikhao (4 terminals running)
- Flow explain karo: Agent → Backend → OpenSearch → Frontend

**2. Real-time Monitoring (3 min)**
- Terminal 3 (Agent) mein live logs dikhai denge
- Terminal 2 (Backend) mein processing dikhai dega
- Frontend Dashboard mein real-time stats

**3. Alert Generation (4 min)**
```powershell
# Test alert generate karo
cd C:\Users\91751\Downloads\Socify\scripts
python generate_alerts.py
```
- OpenSearch mein new alert dikhai dega
- Frontend Alerts page refresh karo
- Alert details dikhao (severity, MITRE mapping)

**4. Search & Filter Demo (2 min)**
- Logs page mein search dikhao
- Filter by severity
- Time range selection

---

## Quick Reference Commands {#quick-reference}

### Start Everything (Order mein)

```powershell
# 1. OpenSearch
cd C:\opensearch-2.11.0\bin && .\opensearch.bat

# 2. Backend (new terminal)
cd C:\Users\91751\Downloads\Socify\backend && .\venv\Scripts\activate && uvicorn app.main:app --reload

# 3. Agent (new terminal)
cd C:\Users\91751\Downloads\Socify\agent && .\socify-agent.exe

# 4. Frontend (new terminal)
cd C:\Users\91751\Downloads\Socify\frontend && npm run dev
```

### Stop Everything

```
Press CTRL+C in each terminal
```

### Health Checks

```powershell
# All-in-one health check
curl http://localhost:9200 && curl http://localhost:8000/health && curl http://localhost:3000
```

### View Logs

```powershell
# OpenSearch logs
curl "http://localhost:9200/socify-logs-*/_search?size=10&pretty"

# Alerts
curl "http://localhost:9200/socify-alerts-*/_search?size=10&pretty"
```

---

## 📊 Expected State Diagram

```
┌────────────────────────────────────────────────────┐
│ Terminal 1: OpenSearch Running (Port 9200)         │
│ Status: ✅ GREEN - Node started                    │
└────────────────────────────────────────────────────┘
                       ↓
┌────────────────────────────────────────────────────┐
│ Terminal 2: Backend Running (Port 8000)            │
│ Status: ✅ Application startup complete            │
│ Logs: Receiving from agent, Indexing to OpenSearch│
└────────────────────────────────────────────────────┘
                       ↑
┌────────────────────────────────────────────────────┐
│ Terminal 3: Agent Running                          │
│ Status: ✅ Sending batch of X logs                 │
│ Monitoring: 10 Windows Event Logs                 │
└────────────────────────────────────────────────────┘
                       ↓
┌────────────────────────────────────────────────────┐
│ Terminal 4: Frontend Running (Port 3000)           │
│ Status: ✅ Ready on http://localhost:3000          │
│ Pages: Dashboard, Logs, Alerts, Rules             │
└────────────────────────────────────────────────────┘
```

---

## 🎯 Summary Checklist

Before presenting, verify:

- [ ] OpenSearch running (localhost:9200 accessible)
- [ ] Backend running (localhost:8000/health returns success)
- [ ] Agent sending logs (terminal shows "Sending batch...")
- [ ] Frontend accessible (localhost:3000 loads)
- [ ] Data flowing (logs visible in OpenSearch)
- [ ] Alerts generating (rules working)
- [ ] All 4 terminals visible aur organized
- [ ] Browser tabs ready (Dashboard, Logs, Alerts)

---

## 💡 Pro Tips

1. **Terminals ko arrange karo** - 4 terminals ek saath dikhai denge presentation mein
2. **Logs readable rakho** - Font size badha lo terminals mein
3. **Browser zoom thoda increase karo** - UI clearly dikhai de
4. **Demo script pehle practice karo** - Smooth flow ke liye
5. **Backup plan** - Agar kuch fail ho toh screenshots ready rakho

---

## 🚀 All Ready!

Ab tum completely prepared ho. Steps follow karo, verify karo sab kuch, aur confident presentation do! 

**Good luck! 🎉**

---

**Quick Help:**
- Config issues: Check `config.yaml` in agent folder
- Connection issues: Verify order (OpenSearch → Backend → Agent)
- Data issues: Check if all components running
- Performance issues: Close other heavy applications

**Last updated:** December 2024
