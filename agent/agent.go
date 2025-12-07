package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"agent/utils"

	"gopkg.in/yaml.v3"
)

// Config represents the agent configuration
type Config struct {
	BackendURL string `yaml:"backend_url"`
	LogFiles   []struct {
		Path string `yaml:"path"`
		Type string `yaml:"type"`
	} `yaml:"log_files"`
	Agent struct {
		BatchSize     int    `yaml:"batch_size"`
		FlushInterval string `yaml:"flush_interval"`
		MaxRetries    int    `yaml:"max_retries"`
		RetryDelay    string `yaml:"retry_delay"`
		BufferSize    int    `yaml:"buffer_size"`
	} `yaml:"agent"`
	Metadata struct {
		Hostname string   `yaml:"hostname"`
		OSFamily string   `yaml:"os_family"`
		Tags     []string `yaml:"tags"`
	} `yaml:"metadata"`
}

var (
	configPath = flag.String("config", "config.yaml", "Path to configuration file")
	config     Config
)

func main() {
	flag.Parse()

	// Load configuration
	if err := loadConfig(*configPath); err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	log.Printf("Socify Agent starting...")
	log.Printf("Backend URL: %s", config.BackendURL)
	log.Printf("Monitoring %d log files", len(config.LogFiles))

	// Collect system metadata
	sysInfo := utils.CollectSystemInfo()

	// Override with config if provided
	if config.Metadata.Hostname != "" {
		sysInfo.Hostname = config.Metadata.Hostname
	}
	if config.Metadata.OSFamily != "" {
		sysInfo.OSFamily = config.Metadata.OSFamily
	}
	if len(config.Metadata.Tags) > 0 {
		sysInfo.Tags = config.Metadata.Tags
	}

	log.Printf("System Info: Hostname=%s, OS=%s", sysInfo.Hostname, sysInfo.OSFamily)

	// Create log buffer channel
	logBuffer := make(chan utils.LogEntry, config.Agent.BufferSize)

	// Parse flush interval
	flushInterval, err := time.ParseDuration(config.Agent.FlushInterval)
	if err != nil {
		log.Printf("Invalid flush interval, using default 5s: %v", err)
		flushInterval = 5 * time.Second
	}

	// Start log sender goroutine
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		utils.StartLogSender(
			config.BackendURL,
			logBuffer,
			config.Agent.BatchSize,
			flushInterval,
			config.Agent.MaxRetries,
		)
	}()

	// Start file tailers
	for _, logFile := range config.LogFiles {
		wg.Add(1)
		go func(path, logType string) {
			defer wg.Done()
			log.Printf("Starting tail for: %s (type: %s)", path, logType)

			if err := utils.TailFile(path, logType, sysInfo, logBuffer); err != nil {
				log.Printf("Error tailing %s: %v", path, err)
			}
		}(logFile.Path, logFile.Type)
	}

	// Handle graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	<-sigChan
	log.Println("Shutdown signal received, stopping agent...")

	// Close log buffer to signal sender to stop
	close(logBuffer)

	// Wait for all goroutines to finish
	wg.Wait()

	log.Println("Agent stopped gracefully")
}

func loadConfig(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("failed to read config file: %w", err)
	}

	if err := yaml.Unmarshal(data, &config); err != nil {
		return fmt.Errorf("failed to parse config: %w", err)
	}

	// Set defaults
	if config.Agent.BatchSize == 0 {
		config.Agent.BatchSize = 10
	}
	if config.Agent.FlushInterval == "" {
		config.Agent.FlushInterval = "5s"
	}
	if config.Agent.MaxRetries == 0 {
		config.Agent.MaxRetries = 3
	}
	if config.Agent.RetryDelay == "" {
		config.Agent.RetryDelay = "2s"
	}
	if config.Agent.BufferSize == 0 {
		config.Agent.BufferSize = 1000
	}

	return nil
}
