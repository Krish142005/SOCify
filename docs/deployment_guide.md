# Socify SIEM - Complete Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [AWS Infrastructure Setup](#aws-infrastructure-setup)
3. [Backend Deployment](#backend-deployment)
4. [Agent Deployment](#agent-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- **AWS CLI** (v2.x): `aws --version`
- **Python** (3.9+): `python3 --version`
- **Go** (1.21+): `go version`
- **Node.js** (18+): `node --version`
- **Terraform** (optional): `terraform --version`

### AWS Account Requirements
- AWS account with admin access
- IAM user with programmatic access
- AWS CLI configured: `aws configure`

## AWS Infrastructure Setup

### Option 1: Using Terraform (Recommended)

```bash
cd infrastructure/aws/terraform

# Initialize Terraform
terraform init

# Review the plan
terraform plan \
  -var="collection_name=socify-logs" \
  -var="backend_principal_arn=arn:aws:iam::YOUR_ACCOUNT_ID:user/YOUR_USERNAME"

# Apply configuration
terraform apply \
  -var="collection_name=socify-logs" \
  -var="backend_principal_arn=arn:aws:iam::YOUR_ACCOUNT_ID:user/YOUR_USERNAME"

# Save outputs
terraform output -json > outputs.json
OPENSEARCH_ENDPOINT=$(terraform output -raw collection_endpoint)
```

### Option 2: Using CloudFormation

```bash
cd infrastructure/aws

# Deploy stack
aws cloudformation create-stack \
  --stack-name socify-opensearch \
  --template-body file://cloudformation/opensearch-serverless.yaml \
  --parameters \
    ParameterKey=CollectionName,ParameterValue=socify-logs \
    ParameterKey=BackendPrincipalArn,ParameterValue=arn:aws:iam::YOUR_ACCOUNT_ID:user/YOUR_USERNAME \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name socify-opensearch \
  --region us-east-1

# Get endpoint
OPENSEARCH_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name socify-opensearch \
  --query 'Stacks[0].Outputs[?OutputKey==`CollectionEndpoint`].OutputValue' \
  --output text)
```

### Create Index Mappings

```bash
# Install awscurl for SigV4 signing
pip install awscurl

# Create logs index template
awscurl --service aoss \
  --region us-east-1 \
  -X PUT \
  "https://$OPENSEARCH_ENDPOINT/_index_template/socify-logs-template" \
  -H "Content-Type: application/json" \
  -d @index-mappings/logs-mapping.json

# Create alerts index template
awscurl --service aoss \
  --region us-east-1 \
  -X PUT \
  "https://$OPENSEARCH_ENDPOINT/_index_template/socify-alerts-template" \
  -H "Content-Type: application/json" \
  -d @index-mappings/alerts-mapping.json
```

## Backend Deployment

### Local Development

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your values
nano .env
```

Edit `.env`:
```bash
OPENSEARCH_ENDPOINT=your-collection-id.us-east-1.aoss.amazonaws.com
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
LOG_LEVEL=INFO
LOGS_INDEX_PREFIX=socify-logs
ALERTS_INDEX_PREFIX=socify-alerts
```

```bash
# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the startup script
chmod +x start.sh
./start.sh  # Linux/Mac
# start.bat  # Windows
```

### Production Deployment (AWS ECS)

```bash
# Build Docker image
cd backend
docker build -t socify-backend:latest .

# Tag for ECR
aws ecr create-repository --repository-name socify-backend --region us-east-1
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag socify-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/socify-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/socify-backend:latest

# Create ECS task definition (use AWS Console or Terraform)
# Set environment variables in task definition
```

## Agent Deployment

### Build Agent

```bash
cd agent

# Install dependencies
go mod download

# Build for your platform
go build -o socify-agent agent.go

# Or cross-compile
GOOS=linux GOARCH=amd64 go build -o socify-agent-linux agent.go
GOOS=windows GOARCH=amd64 go build -o socify-agent.exe agent.go
```

### Configure Agent

Edit `config.yaml`:
```yaml
backend_url: http://YOUR_BACKEND_IP:8000/api/ingest

log_files:
  - path: /var/log/auth.log
    type: syslog
  - path: /var/log/apache2/access.log
    type: apache

agent:
  batch_size: 10
  flush_interval: 5s
  max_retries: 3
  buffer_size: 1000
```

### Run Agent

```bash
# Linux/Mac
./socify-agent -config config.yaml

# Windows
socify-agent.exe -config config.yaml

# Run as systemd service (Linux)
sudo cp socify-agent /usr/local/bin/
sudo nano /etc/systemd/system/socify-agent.service
```

Systemd service file:
```ini
[Unit]
Description=Socify SIEM Agent
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/socify-agent -config /etc/socify/config.yaml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable socify-agent
sudo systemctl start socify-agent
sudo systemctl status socify-agent
```

## Frontend Deployment

### Local Development

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# Start development server
npm run dev
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start

# Or export static site
npm run build && npm run export
```

### Deploy to AWS Amplify

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize Amplify
amplify init

# Add hosting
amplify add hosting

# Publish
amplify publish
```

## Verification

### 1. Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "socify-backend",
  "checks": {
    "api": "ok",
    "opensearch": "ok"
  }
}
```

### 2. Test Log Ingestion

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "raw_log": "Dec 10 06:55:46 server sshd[1234]: Failed password for admin from 192.168.1.100",
    "source_type": "syslog",
    "metadata": {
      "hostname": "test-server",
      "os_family": "linux"
    }
  }'
```

### 3. Search Logs

```bash
curl "http://localhost:8000/api/search?limit=10"
```

### 4. Check Alerts

```bash
curl "http://localhost:8000/api/alerts?limit=10"
```

### 5. Verify Agent

Check agent logs:
```bash
# If running in foreground, check console output
# If running as service:
sudo journalctl -u socify-agent -f
```

## Troubleshooting

### Backend Issues

**OpenSearch Connection Failed**
```bash
# Test connectivity
curl -I https://your-endpoint.aoss.amazonaws.com

# Verify credentials
aws sts get-caller-identity

# Check IAM permissions
aws opensearchserverless list-collections
```

**Import Errors**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Agent Issues

**File Not Found**
```bash
# Check file permissions
ls -la /var/log/auth.log

# Run agent with sudo if needed
sudo ./socify-agent
```

**Connection Refused**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check firewall rules
sudo ufw status
```

### OpenSearch Issues

**Index Creation Failed**
```bash
# Check index templates
awscurl --service aoss \
  --region us-east-1 \
  "https://$OPENSEARCH_ENDPOINT/_index_template"

# Manually create index
awscurl --service aoss \
  --region us-east-1 \
  -X PUT \
  "https://$OPENSEARCH_ENDPOINT/socify-logs-2024.11"
```

## Monitoring

### Backend Logs

```bash
# View logs
tail -f backend/logs/app.log

# Or if using systemd
journalctl -u socify-backend -f
```

### OpenSearch Metrics

```bash
# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/AOSS \
  --metric-name SearchRate \
  --dimensions Name=CollectionName,Value=socify-logs \
  --start-time 2024-11-22T00:00:00Z \
  --end-time 2024-11-22T23:59:59Z \
  --period 3600 \
  --statistics Average
```

### Agent Status

```bash
# Check agent status
systemctl status socify-agent

# View agent logs
journalctl -u socify-agent --since "1 hour ago"
```

## Next Steps

1. **Configure Alerts**: Customize rules in `backend/app/rules/rules.json`
2. **Set Up Dashboards**: Use OpenSearch Dashboards to create visualizations
3. **Enable HTTPS**: Configure SSL/TLS for production
4. **Add Authentication**: Implement JWT or API key authentication
5. **Scale Infrastructure**: Add load balancers and auto-scaling
6. **Monitor Performance**: Set up CloudWatch alarms and dashboards

## Support

For issues and questions:
- Check logs: Backend, Agent, OpenSearch
- Review AWS CloudWatch logs
- Verify network connectivity
- Check IAM permissions
