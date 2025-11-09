package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/boltdb/bolt"
	"gopkg.in/yaml.v3"
)

type Config struct {
	LogPath string `yaml:"log_path"`
	Server  string `yaml:"server"`
}

type Event struct {
	Timestamp time.Time `json:"timestamp"`
	Line      string    `json:"line"`
}

type Agent struct {
	cfg     Config
	db      *bolt.DB
	httpCli *http.Client
	cancel  context.CancelFunc
}

func NewAgent(cfgPath string) (*Agent, error) {
	f, err := os.Open(cfgPath)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	var cfg Config
	if err := yaml.NewDecoder(f).Decode(&cfg); err != nil {
		return nil, err
	}

	db, err := bolt.Open("agent-buffer.db", 0600, nil)
	if err != nil {
		return nil, err
	}

	return &Agent{
		cfg:     cfg,
		db:      db,
		httpCli: &http.Client{Timeout: 5 * time.Second},
	}, nil
}

func (a *Agent) Start(ctx context.Context) error {
	log.Printf("Starting agent — watching %s", a.cfg.LogPath)
	go TailFile(ctx, a.cfg.LogPath, func(line string) {
		ev := Event{Timestamp: time.Now(), Line: line}
		if err := a.send(ev); err != nil {
			log.Printf("send failed: %v", err)
			_ = a.buffer(ev)
		}
	})
	return nil
}

func (a *Agent) Stop() {
	a.db.Close()
}

func (a *Agent) send(ev Event) error {
	b, _ := json.Marshal(ev)
	resp, err := a.httpCli.Post(a.cfg.Server, "application/json", io.NopCloser(bytesReader(b)))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode < 200 || resp.StatusCode > 299 {
		return fmt.Errorf("bad status %d", resp.StatusCode)
	}
	return nil
}

func (a *Agent) buffer(ev Event) error {
	b, _ := json.Marshal(ev)
	return a.db.Update(func(tx *bolt.Tx) error {
		bkt, _ := tx.CreateBucketIfNotExists([]byte("events"))
		id, _ := bkt.NextSequence()
		key := itob(id)
		return bkt.Put(key, b)
	})
}

func itob(v uint64) []byte {
	b := make([]byte, 8)
	for i := uint(0); i < 8; i++ {
		b[7-i] = byte(v >> (i * 8))
	}
	return b
}

type bytesReaderT struct{ b []byte }

func bytesReader(b []byte) *bytesReaderT { return &bytesReaderT{b: b} }

func (r *bytesReaderT) Read(p []byte) (int, error) {
	if len(r.b) == 0 {
		return 0, io.EOF
	}
	n := copy(p, r.b)
	r.b = r.b[n:]
	return n, nil
}
