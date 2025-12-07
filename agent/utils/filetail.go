package utils

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/nxadm/tail"
)

// TailFile tails a log file and sends entries to the buffer channel
func TailFile(path string, logType string, sysInfo SystemInfo, buffer chan<- LogEntry) error {
	// Check if file exists
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return fmt.Errorf("file does not exist: %s", path)
	}

	// Start tailing
	t, err := tail.TailFile(path, tail.Config{
		Follow:    true,
		ReOpen:    true,
		MustExist: false,
		Poll:      true,
		Location:  &tail.SeekInfo{Offset: 0, Whence: os.SEEK_END},
	})
	if err != nil {
		return fmt.Errorf("failed to tail file: %w", err)
	}

	log.Printf("Tailing file: %s", path)

	// Read lines
	for line := range t.Lines {
		if line.Err != nil {
			log.Printf("Error reading line from %s: %v", path, line.Err)
			continue
		}

		// Create log entry
		entry := LogEntry{
			RawLog:     line.Text,
			SourceType: logType,
			Timestamp:  time.Now(),
			Metadata: map[string]interface{}{
				"hostname":      sysInfo.Hostname,
				"os_family":     sysInfo.OSFamily,
				"os_version":    sysInfo.OSVersion,
				"agent_version": sysInfo.AgentVersion,
				"source_file":   path,
				"tags":          sysInfo.Tags,
			},
		}

		// Send to buffer (non-blocking)
		select {
		case buffer <- entry:
			// Successfully sent
		default:
			log.Printf("Warning: Buffer full, dropping log from %s", path)
		}
	}

	return nil
}

// ReadExistingLogs reads existing log file content (for initial load)
func ReadExistingLogs(path string, logType string, sysInfo SystemInfo, buffer chan<- LogEntry, maxLines int) error {
	file, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	lineCount := 0

	for scanner.Scan() {
		if maxLines > 0 && lineCount >= maxLines {
			break
		}

		entry := LogEntry{
			RawLog:     scanner.Text(),
			SourceType: logType,
			Timestamp:  time.Now(),
			Metadata: map[string]interface{}{
				"hostname":      sysInfo.Hostname,
				"os_family":     sysInfo.OSFamily,
				"agent_version": sysInfo.AgentVersion,
				"source_file":   path,
			},
		}

		select {
		case buffer <- entry:
			lineCount++
		default:
			log.Printf("Warning: Buffer full during initial load")
			return nil
		}
	}

	if err := scanner.Err(); err != nil {
		return fmt.Errorf("error reading file: %w", err)
	}

	log.Printf("Read %d existing lines from %s", lineCount, path)
	return nil
}
