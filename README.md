Project Structure : 
```
SOCify/
 ├── agent/                  ← Lightweight forwarder (Go)
 │   ├── buffer/             ← Local DB, retry queue
 │   ├── config/
 │   ├── collector/
 │   ├── sender/
 │   ├── tls/
 │   ├── auth/
 │   ├── main.go
 │   └── go.mod

 ├── server/                 ← Master server (Go)
 │   ├── api/
 │   ├── db/
 │   ├── storage/
 │   ├── ingestion/
 │   ├── auth/
 │   ├── tls/
 │   ├── models/
 │   ├── handlers/
 │   ├── main.go
 │   └── go.mod

 ├── dashboard/              ← Next.js dashboard
 │   ├── app/
 │   ├── components/
 │   ├── lib/
 │   ├── public/
 │   ├── tailwind.config.js
 │   ├── package.json
 │   └── README.md

 ├── infrastructure/
 │   ├── docker/
 │   ├── compose.yaml
 │   ├── aws/
 │   ├── scripts/
 │   └── monitoring/

 ├── docs/
 │   ├── architecture.md
 │   ├── api-spec.md
 │   ├── agent-flow.md
 │   ├── server-flow.md
 │   ├── commit-guidelines.md
 │   └── tasks/

 ├── scripts/
 │   ├── install-agent.ps1
 │   ├── install-agent.sh
 │   └── build-all.sh
─ README.md
```
