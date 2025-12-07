package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

// StartLogSender starts the log sender goroutine
func StartLogSender(
	backendURL string,
	buffer <-chan LogEntry,
	batchSize int,
	flushInterval time.Duration,
	maxRetries int,
) {
	batch := make([]LogEntry, 0, batchSize)
	ticker := time.NewTicker(flushInterval)
	defer ticker.Stop()

	for {
		select {
		case entry, ok := <-buffer:
			if !ok {
				// Channel closed, send remaining batch and exit
				if len(batch) > 0 {
					sendBatch(backendURL, batch, maxRetries)
				}
				log.Println("Log sender stopped")
				return
			}

			batch = append(batch, entry)

			// Send batch if full
			if len(batch) >= batchSize {
				sendBatch(backendURL, batch, maxRetries)
				batch = make([]LogEntry, 0, batchSize)
			}

		case <-ticker.C:
			// Flush interval reached, send batch even if not full
			if len(batch) > 0 {
				sendBatch(backendURL, batch, maxRetries)
				batch = make([]LogEntry, 0, batchSize)
			}
		}
	}
}

// sendBatch sends a batch of log entries to the backend
func sendBatch(backendURL string, batch []LogEntry, maxRetries int) {
	// Use batch endpoint if available, otherwise send individually
	useBatch := len(batch) > 1

	var err error
	if useBatch {
		err = sendBatchRequest(backendURL+"/batch", batch, maxRetries)
	} else if len(batch) == 1 {
		err = sendSingleRequest(backendURL, batch[0], maxRetries)
	}

	if err != nil {
		log.Printf("Failed to send batch of %d logs: %v", len(batch), err)
	} else {
		log.Printf("Successfully sent batch of %d logs", len(batch))
	}
}

// sendBatchRequest sends multiple logs in a single request
func sendBatchRequest(url string, batch []LogEntry, maxRetries int) error {
	payload, err := json.Marshal(batch)
	if err != nil {
		return fmt.Errorf("failed to marshal batch: %w", err)
	}

	return sendWithRetry(url, payload, maxRetries)
}

// sendSingleRequest sends a single log entry
func sendSingleRequest(url string, entry LogEntry, maxRetries int) error {
	payload, err := json.Marshal(entry)
	if err != nil {
		return fmt.Errorf("failed to marshal entry: %w", err)
	}

	return sendWithRetry(url, payload, maxRetries)
}

// sendWithRetry sends HTTP request with retry logic
func sendWithRetry(url string, payload []byte, maxRetries int) error {
	var lastErr error

	for attempt := 0; attempt <= maxRetries; attempt++ {
		if attempt > 0 {
			// Exponential backoff
			backoff := time.Duration(attempt*attempt) * time.Second
			log.Printf("Retry attempt %d/%d after %v", attempt, maxRetries, backoff)
			time.Sleep(backoff)
		}

		resp, err := http.Post(url, "application/json", bytes.NewBuffer(payload))
		if err != nil {
			lastErr = fmt.Errorf("HTTP request failed: %w", err)
			continue
		}

		// Check response status
		if resp.StatusCode >= 200 && resp.StatusCode < 300 {
			resp.Body.Close()
			return nil
		}

		// Read error response
		var errorMsg string
		if resp.Body != nil {
			buf := new(bytes.Buffer)
			buf.ReadFrom(resp.Body)
			errorMsg = buf.String()
			resp.Body.Close()
		}

		lastErr = fmt.Errorf("HTTP %d: %s", resp.StatusCode, errorMsg)

		// Don't retry on client errors (4xx)
		if resp.StatusCode >= 400 && resp.StatusCode < 500 {
			return lastErr
		}
	}

	return fmt.Errorf("max retries exceeded: %w", lastErr)
}

// SendSingleLog sends a single log entry immediately (for testing)
func SendSingleLog(backendURL string, entry LogEntry) error {
	return sendSingleRequest(backendURL, entry, 3)
}
