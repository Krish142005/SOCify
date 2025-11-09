package main

import (
	"bufio"
	"context"
	"log"
	"os"
	"time"
)

// TailFile continuously reads new lines from a file and sends them to callback(line)
func TailFile(ctx context.Context, path string, callback func(string)) {
	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		f, err := os.Open(path)
		if err != nil {
			log.Printf("Failed to open %s: %v", path, err)
			time.Sleep(5 * time.Second)
			continue
		}

		// Move to end of file (only read new lines)
		f.Seek(0, os.SEEK_END)
		reader := bufio.NewReader(f)

		for {
			select {
			case <-ctx.Done():
				f.Close()
				return
			default:
			}

			line, err := reader.ReadString('\n')
			if err != nil {
				time.Sleep(1 * time.Second)
				continue
			}
			callback(line)
		}
	}
}
