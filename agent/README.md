# Socify Agent Build and Run

## Build

```bash
# Build for current platform
go build -o socify-agent agent.go

# Cross-compile for Linux
GOOS=linux GOARCH=amd64 go build -o socify-agent-linux agent.go

# Cross-compile for Windows
GOOS=windows GOARCH=amd64 go build -o socify-agent.exe agent.go

# Cross-compile for macOS
GOOS=darwin GOARCH=amd64 go build -o socify-agent-mac agent.go
```

## Run

```bash
# Run with default config
./socify-agent

# Run with custom config
./socify-agent -config /path/to/config.yaml
```

## Configuration

Edit `config.yaml` to configure:
- Backend URL
- Log files to monitor
- Batch size and flush interval
- System metadata

## Dependencies

Install dependencies:
```bash
go mod download
```
