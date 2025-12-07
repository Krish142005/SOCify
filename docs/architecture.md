# Socify SIEM - System Architecture

## Overview

Socify is a cloud-native Security Information and Event Management (SIEM) platform designed for real-time threat detection and security monitoring. The system follows a microservices architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Endpoints                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Server 1 │  │ Server 2 │  │ Server 3 │  │ Server N │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │             │              │
│  ┌────▼─────────────▼──────────────▼─────────────▼────┐        │
│  │          Socify Agent (Go)                          │        │
│  │  • File Tailing  • Metadata Collection             │        │
│  │  • Batching      • HTTP Sender                     │        │
│  └────────────────────┬────────────────────────────────┘        │
└────────────────────────┼─────────────────────────────────────────┘
                         │ HTTP POST /api/ingest
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Ingest     │  │   Search     │  │   Alerts     │          │
│  │   Endpoint   │  │   Endpoint   │  │   Endpoint   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│  ┌──────▼──────────────────▼──────────────────▼───────┐         │
│  │           Normalization Engine                     │         │
│  │  • Grok Patterns  • ECS Transformation             │         │
│  └──────────────────────┬─────────────────────────────┘         │
│                         │                                        │
│  ┌──────────────────────▼─────────────────────────────┐         │
│  │           Rule Engine                              │         │
│  │  • Boolean Rules    • Threshold Rules              │         │
│  │  • Correlation      • Pattern Matching             │         │
│  └──────────────────────┬─────────────────────────────┘         │
│                         │                                        │
│  ┌──────────────────────▼─────────────────────────────┐         │
│  │      OpenSearch Client (SigV4 Auth)                │         │
│  └──────────────────────┬─────────────────────────────┘         │
└────────────────────────┼──────────────────────────────────────────┘
                         │ HTTPS + AWS SigV4
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│           AWS OpenSearch Serverless                              │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │  socify-logs-*      │  │  socify-alerts-*    │               │
│  │  • @timestamp       │  │  • alert_id         │               │
│  │  • event.action     │  │  • rule_name        │               │
│  │  • source.ip        │  │  • severity         │               │
│  │  • user.name        │  │  • mitre_tactics    │               │
│  │  • ECS fields       │  │  • matched_events   │               │
│  └─────────────────────┘  └─────────────────────┘               │
└────────────────────────┬─────────────────────────────────────────┘
                         │ Query API
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│                  Frontend (Next.js)                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   Logs   │  │  Alerts  │  │  Rules   │  │Dashboard │        │
│  │   Page   │  │   Page   │  │   Page   │  │   Page   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  • Real-time Dashboards  • Alert Management                     │
│  • Log Search & Filtering • Rule Configuration                  │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Agent Layer (Go)

**Purpose**: Lightweight log collection from endpoints

**Components**:
- `agent.go`: Main orchestrator
- `filetail.go`: File monitoring using fsnotify
- `send.go`: HTTP client with retry logic
- `sysinfo.go`: System metadata collector

**Features**:
- Real-time file tailing with rotation handling
- Configurable batching (default: 10 logs per batch)
- Exponential backoff retry mechanism
- Low resource footprint (<50MB RAM)

**Data Flow**:
1. Monitor log files for changes
2. Enrich with system metadata (hostname, OS, timestamp)
3. Buffer logs in memory channel
4. Batch and send via HTTP POST
5. Retry on failure with exponential backoff

### 2. Backend Layer (Python/FastAPI)

**Purpose**: Central processing and orchestration

**Components**:
- `main.py`: FastAPI application initialization
- `ingest.py`: Log ingestion endpoint
- `search.py`: Log search and aggregation
- `alerts.py`: Alert management
- `rule_engine.py`: Detection logic
- `opensearch_client.py`: AWS OpenSearch interface
- `parsers/normalize.py`: ECS normalization
- `parsers/grok_patterns.py`: Regex patterns

**API Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ingest` | POST | Receive logs from agents |
| `/api/ingest/batch` | POST | Batch log ingestion |
| `/api/search` | GET | Query logs with filters |
| `/api/alerts` | GET | Fetch alerts |
| `/api/alerts/{id}` | GET/PUT | Get/update specific alert |
| `/health` | GET | Health check |

**Processing Pipeline**:
1. Receive raw log from agent
2. Parse using Grok patterns
3. Normalize to ECS format
4. Index to OpenSearch
5. Evaluate against detection rules
6. Generate alerts if rules match
7. Store alerts in separate index

### 3. Storage Layer (AWS OpenSearch Serverless)

**Purpose**: Scalable log and alert storage

**Indices**:

**socify-logs-YYYY.MM**:
- Time-series index for log events
- ECS-compliant field mapping
- Optimized for write-heavy workloads
- Automatic monthly rollover

**socify-alerts-YYYY.MM**:
- Alert storage with MITRE ATT&CK mapping
- Status tracking (open, acknowledged, resolved)
- Linked to triggering events

**Features**:
- Serverless architecture (no infrastructure management)
- Automatic scaling based on workload
- AWS SigV4 authentication
- Encryption at rest and in transit
- Time-series optimized storage

### 4. Detection Layer (Rule Engine)

**Purpose**: Real-time threat detection

**Rule Types**:

1. **Boolean Rules**: Simple field matching
   ```json
   {
     "type": "boolean",
     "condition": {
       "field": "event.action",
       "operator": "equals",
       "value": "ssh_login_failed"
     }
   }
   ```

2. **Threshold Rules**: Aggregate counting
   ```json
   {
     "type": "threshold",
     "condition": {
       "field": "event.action",
       "value": "ssh_login_failed",
       "threshold": 5,
       "timeframe": "5m",
       "group_by": "source.ip"
     }
   }
   ```

3. **Correlation Rules**: Multi-condition logic
   ```json
   {
     "type": "correlation",
     "conditions": [
       {"field": "event.action", "value": "login_failed"},
       {"field": "event.action", "value": "privilege_escalation"}
     ],
     "correlation_key": "user.name"
   }
   ```

4. **Pattern Rules**: Regex matching
   ```json
   {
     "type": "pattern",
     "condition": {
       "field": "file.extension",
       "pattern": "\\.(encrypted|locked|crypto)$"
     }
   }
   ```

**Detection Coverage**:
- Authentication attacks (brute force, credential stuffing)
- Malware and ransomware
- Lateral movement
- Privilege escalation
- Data exfiltration
- Command and control
- Defense evasion

### 5. Presentation Layer (Next.js)

**Purpose**: User interface for monitoring and management

**Pages**:
- `/logs`: Log search and viewing
- `/alerts`: Alert dashboard
- `/rules`: Rule management
- `/dashboard`: Overview and statistics

**Features**:
- Real-time data updates
- Advanced filtering and search
- Alert acknowledgment and assignment
- Rule enable/disable
- MITRE ATT&CK visualization

## Data Flow

### Log Ingestion Flow

```
1. Log Generated on Endpoint
   ↓
2. Agent Tails File → Enriches with Metadata
   ↓
3. Agent Batches Logs → HTTP POST to Backend
   ↓
4. Backend Receives → Validates Request
   ↓
5. Normalization Engine → Parses with Grok → Converts to ECS
   ↓
6. OpenSearch Client → Signs Request (SigV4) → Indexes Document
   ↓
7. Rule Engine → Evaluates Rules → Generates Alerts (if matched)
   ↓
8. Alert Stored in OpenSearch
   ↓
9. Frontend Queries → Displays Logs and Alerts
```

### Alert Generation Flow

```
1. Event Indexed in OpenSearch
   ↓
2. Rule Engine Triggered
   ↓
3. For Each Rule:
   - Check if filter matches event
   - Evaluate condition based on rule type
   - Query OpenSearch for threshold/correlation rules
   ↓
4. If Rule Matches:
   - Generate alert document
   - Include MITRE ATT&CK mapping
   - Add matched event details
   ↓
5. Store Alert in socify-alerts-* index
   ↓
6. Frontend Polls /api/alerts → Displays New Alert
```

## Security Architecture

### Authentication & Authorization

1. **Agent → Backend**: API key or mTLS
2. **Backend → OpenSearch**: AWS SigV4 signing
3. **Frontend → Backend**: JWT tokens (future)

### Network Security

- All communications over HTTPS/TLS 1.3
- OpenSearch in private VPC (production)
- Backend behind Application Load Balancer
- WAF rules for API protection

### Data Security

- Encryption at rest (AWS KMS)
- Encryption in transit (TLS)
- Field-level encryption for PII
- Audit logging of all access

## Scalability

### Horizontal Scaling

- **Agent**: Deploy on each endpoint
- **Backend**: Multiple instances behind ALB
- **OpenSearch**: Automatic serverless scaling
- **Frontend**: CDN distribution

### Performance Optimization

- Agent batching reduces API calls
- Backend async processing
- OpenSearch bulk indexing
- Frontend caching and pagination

### Resource Requirements

| Component | CPU | RAM | Storage |
|-----------|-----|-----|---------|
| Agent | 0.1 core | 50MB | Minimal |
| Backend | 1-2 cores | 2GB | Minimal |
| OpenSearch | Auto-scaled | Auto-scaled | Based on retention |
| Frontend | 0.5 core | 512MB | Minimal |

## High Availability

- Multi-AZ OpenSearch deployment
- Backend auto-scaling group
- Agent automatic restart on failure
- Health checks and monitoring

## Monitoring & Observability

### Metrics

- Log ingestion rate
- Alert generation rate
- Rule evaluation latency
- OpenSearch query performance
- Agent connection status

### Logging

- Backend application logs → CloudWatch
- Agent logs → Local file + syslog
- OpenSearch audit logs
- API access logs

### Alerting

- CloudWatch alarms for infrastructure
- SIEM alerts for security events
- PagerDuty integration for critical alerts

## Future Enhancements

1. **Machine Learning**: Anomaly detection using AWS SageMaker
2. **SOAR Integration**: Automated response playbooks
3. **Threat Intelligence**: Integration with threat feeds
4. **Multi-tenancy**: Support for multiple organizations
5. **Advanced Analytics**: User behavior analytics (UEBA)
