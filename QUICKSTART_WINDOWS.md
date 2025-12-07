# Quick Start Guide - Windows Event Log Collection

## What You Need

1. **Backend Running**: `cd backend && start.bat`
2. **Frontend Running**: `cd frontend && npm run dev`
3. **Python 3.8+** installed
4. **Administrator privileges**

## Installation (5 minutes)

### Step 1: Install Python Dependencies

```powershell
cd C:\Users\91751\OneDrive\Desktop\Socify3\agent
pip install -r requirements.txt
```

Expected output:
```
Successfully installed pywin32-306 requests-2.31.0 pyyaml-6.0 python-dateutil-2.8.2
```

### Step 2: Start the Collector

**Right-click** `start_windows_collector.bat` → **Run as Administrator**

OR manually:
```powershell
python windows_event_collector.py --config config_windows.yaml
```

Expected output:
```
Windows Event Collector initialized
Backend URL: http://localhost:8000/api/ingest
Hostname: DESKTOP-ABC123
Monitoring logs: ['Application', 'System', 'Security']
Batch sender thread started
Monitoring Application log - waiting for new events...
Monitoring System log - waiting for new events...
Monitoring Security log - waiting for new events...
```

### Step 3: Test It Works

**Generate a test event:**
```powershell
eventcreate /L Application /T ERROR /ID 1000 /SO TestApp /D "Test error for Socify SIEM"
```

**Verify:**
1. Collector console shows: `Sent 1 events to backend`
2. Backend logs show: `Indexed event: xyz123 to socify-logs-2025.11`
3. Open http://localhost:3000/monitor
4. See event appear in real-time!

## Monitoring Dashboard

Navigate to: **http://localhost:3000/monitor**

You'll see:
- ✅ Connection Status (green dot = connected)
- 📊 Statistics (total logs, alerts, by source)
- 📝 Live Log Feed (last 50 events)
- 🚨 Live Alert Feed (triggered rules)
- 📈 Alerts by Severity chart

## Testing Rule Matching

### Test 1: Trigger Application Error Rule (A002)

```powershell
# Generate 11 Application Error events to trigger threshold
for ($i=1; $i -le 11; $i++) { 
    eventcreate /L Application /T ERROR /ID 1000 /SO "Application Error" /D "Test error $i"
    Start-Sleep -Seconds 1
}
```

**Expected**: Alert appears after 10th event (threshold = 10, timeframe = 5 minutes)

### Test 2: Trigger USB Rule (USB001)

1. Plug in a USB drive
2. Check monitor dashboard for alert
3. Rule: "USB Storage Device Inserted" (Severity: Medium)

### Test 3: Trigger Failed Login Rule (SEC001)

1. Attempt wrong password 6 times
2. After 5th attempt: Alert triggers
3. Rule: "Multiple Failed Logons" (Severity: Medium)

## Verification Checklist

- [ ] Collector starts without errors
- [ ] Backend receives logs (check backend console)
- [ ] Monitor dashboard shows "Connected" (green dot)
- [ ] Test event appears in Live Log Feed
- [ ] At least one alert triggered
- [ ] Statistics update in real-time

## Troubleshooting

### "ModuleNotFoundError: No module named 'win32evtlog'"
**Solution**: `pip install pywin32`

### "Access is denied" when reading Security logs
**Solution**: Run as Administrator (Right-click → Run as Administrator)

### "Connection refused" to backend
**Solution**:
1. Check backend is running: http://localhost:8000/health
2. Check `backend_url` in `config_windows.yaml`

### "No events appearing"
**Solution**:
1. Collector only sends NEW events (not historical)
2. Generate test event: `eventcreate /L Application /T ERROR /ID 1000 /SO Test /D "Test"`
3. Check collector console for "Sent X events to backend"

## What's Next?

1. **Let it run**: Collector will send ALL Windows events as they happen
2. **Monitor real activity**: Watch USB insertions, app crashes, login attempts
3. **Review alerts**: Check which rules are triggering most often
4. **Fine-tune rules**: Adjust thresholds in `backend/app/rules/rules.json`
5. **Add custom rules**: Create rules for your specific environment

## Architecture Summary

```
Windows Events → Collector → Backend → WebSocket → Monitor Dashboard
(Real-time)     (Normalize)  (Rules)   (Stream)    (Display)
```

## Key Files

- **Collector**: `agent/windows_event_collector.py`
- **Config**: `agent/config_windows.yaml`
- **Rules**: `backend/app/rules/rules.json` (70 rules)
- **Dashboard**: `frontend/src/app/monitor/page.tsx`
- **Docs**: `agent/README_WINDOWS.md`

## Support

For detailed documentation, see:
- [README_WINDOWS.md](file:///c:/Users/91751/OneDrive/Desktop/Socify3/agent/README_WINDOWS.md)
- [walkthrough.md](file:///C:/Users/91751/.gemini/antigravity/brain/89e0c255-4d74-4a99-ab8e-68ed208c6307/walkthrough.md)

Happy hunting! 🔍🚨
