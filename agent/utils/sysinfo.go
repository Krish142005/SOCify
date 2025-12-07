package utils

import (
	"os"
	"runtime"
	"time"
)

// SystemInfo contains system metadata
type SystemInfo struct {
	Hostname     string   `json:"hostname"`
	OSFamily     string   `json:"os_family"`
	OSVersion    string   `json:"os_version"`
	AgentVersion string   `json:"agent_version"`
	Tags         []string `json:"tags"`
}

// LogEntry represents a log entry to be sent
type LogEntry struct {
	RawLog     string                 `json:"raw_log"`
	SourceType string                 `json:"source_type"`
	Metadata   map[string]interface{} `json:"metadata"`
	Timestamp  time.Time              `json:"timestamp"`
}

// CollectSystemInfo gathers system metadata
func CollectSystemInfo() SystemInfo {
	hostname, err := os.Hostname()
	if err != nil {
		hostname = "unknown"
	}

	return SystemInfo{
		Hostname:     hostname,
		OSFamily:     runtime.GOOS,
		OSVersion:    runtime.GOARCH,
		AgentVersion: "1.0.0",
		Tags:         []string{},
	}
}
