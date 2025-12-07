# Socify Agent - Build Instructions

## Prerequisites
- Go 1.21 or higher installed
- Internet connection for downloading dependencies

## Setup and Build

### 1. Download Dependencies

```bash
cd agent
go mod download
go mod tidy
```

This will download:
- `github.com/nxadm/tail` - File tailing library
- `gopkg.in/yaml.v3` - YAML parsing
- Other transitive dependencies

### 2. Build the Agent

```bash
# Build for current platform
go build -o socify-agent agent.go

# Or use go run for testing
go run agent.go -config config.yaml
```

### 3. Cross-Compile for Different Platforms

```bash
# Linux (64-bit)
GOOS=linux GOARCH=amd64 go build -o socify-agent-linux agent.go

# Windows (64-bit)
GOOS=windows GOARCH=amd64 go build -o socify-agent.exe agent.go

# macOS (64-bit Intel)
GOOS=darwin GOARCH=amd64 go build -o socify-agent-mac agent.go

# macOS (ARM64 - M1/M2)
GOOS=darwin GOARCH=arm64 go build -o socify-agent-mac-arm agent.go
```

## Troubleshooting

### Error: "could not import gopkg.in/yaml.v3"

**Solution**: Run `go mod download` to fetch dependencies

```bash
cd agent
go mod download
go mod tidy
```

### Error: "package agent/utils is not in GOROOT"

**Solution**: Make sure you're in the agent directory and run:

```bash
go mod tidy
go build -o socify-agent agent.go
```

### Error: "cannot find module providing package"

**Solution**: Clean and rebuild:

```bash
go clean -modcache
go mod download
go build -o socify-agent agent.go
```

## Running the Agent

### Basic Usage

```bash
# Run with default config
./socify-agent

# Run with custom config
./socify-agent -config /path/to/config.yaml
```

### Configuration

Edit `config.yaml`:

```yaml
backend_url: http://localhost:8000/api/ingest

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

### Running as a Service

#### Linux (systemd)

Create `/etc/systemd/system/socify-agent.service`:

```ini
[Unit]
Description=Socify SIEM Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/socify-agent
ExecStart=/opt/socify-agent/socify-agent -config /opt/socify-agent/config.yaml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable socify-agent
sudo systemctl start socify-agent
sudo systemctl status socify-agent
```

#### Windows (Service)

Use NSSM (Non-Sucking Service Manager):

```powershell
# Download NSSM from https://nssm.cc/download
nssm install SocifyAgent "C:\Program Files\Socify\socify-agent.exe" "-config C:\Program Files\Socify\config.yaml"
nssm start SocifyAgent
```

## Verification

Check that the agent is running:

```bash
# View logs
tail -f /var/log/socify-agent.log

# Or if running as systemd service
journalctl -u socify-agent -f

# Check backend connectivity
curl http://localhost:8000/health
```

## Performance

- **Memory Usage**: ~30-50MB
- **CPU Usage**: <5% (idle), ~10-15% (active tailing)
- **Network**: Depends on log volume and batch size

## Development

### Running Tests

```bash
cd agent
go test ./...
```

### Adding New Log Types

1. Add parser in `utils/filetail.go`
2. Update `config.yaml` with new log type
3. Rebuild agent

### Debugging

Run with verbose logging:

```bash
go run agent.go -config config.yaml 2>&1 | tee agent.log
```
