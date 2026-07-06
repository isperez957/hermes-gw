# Hermes Gateway

Multi-tenant chat application for [Hermes Agent](https://github.com/nousresearch/hermes-agent). A React frontend connected to a FastAPI orchestrator that spawns and manages Hermes Agent gateway processes — one per user, fully isolated.

**Users**: isaac, miguel, pablo  
**URL**: https://dksxf20f9gjfl.cloudfront.net  
**AWS**: eu-west-1 | account 649091762015

---

## Architecture

```
Browser (HTTPS)
    │
    ▼
CloudFront (CDN)
    ├── /api/*  → ALB → EC2:8080 (FastAPI orchestrator)
    └── /*      → S3 (React SPA)
                    │
EC2 (t3.medium, Docker)              │
├── hermes-orchestrator (FastAPI)    │
│   ├── /api/chat        ← SSE stream (keepalive 15s)
│   ├── /api/sessions    ← session list
│   ├── /api/auth/login  ← JWT auth
│   └── gateway_manager  ← spawns per-user gateways
│       ├── user-isaac  → hermes -p user-isaac gateway run (port 8642)
│       ├── user-miguel → hermes -p user-miguel gateway run (port 8643)
│       └── user-pablo  → hermes -p user-pablo gateway run (port 8644)
│
├── /home/ec2-user/.hermes/  ← mounted volume
│   └── profiles/
│       ├── user-isaac/  (config.yaml, .env, skills/, sessions/)
│       ├── user-miguel/
│       └── user-pablo/
│
└── /opt/hermes-gw/  ← scripts + DB (mounted readonly)
    ├── docker-compose.yml
    ├── mysql-mcp-server.py
    └── sample_company.db
```

---

## Repo Structure

```
hermes-gw/
├── frontend/                  # React SPA (Vite + TypeScript)
│   ├── src/
│   │   ├── App.tsx            # Login screen + app shell
│   │   ├── api.ts             # API client (SSE, sessions, auth)
│   │   └── components/
│   │       ├── Chat.tsx       # Chat UI, SSE streaming, keepalive
│   │       └── Message.tsx    # Message bubble with markdown
│   ├── index.html             # Inter + JetBrains Mono fonts
│   └── App.css                # Dark theme, tables, code blocks
│
├── backend/                   # FastAPI orchestrator
│   ├── main.py                # API routes, SSE proxy, keepalive, CORS
│   ├── gateway_manager.py     # Spawn/kill/reap Hermes gateways
│   ├── auth.py                # JWT (users: isaac/miguel/pablo)
│   ├── requirements.txt
│   └── Dockerfile             # Python 3.12 + hermes-agent
│
├── profiles/shared/           # Deployed to ALL user profiles via CI
│   ├── config.yaml            # Model config + MCP servers
│   ├── sample_company.db      # SQLite sample DB (4 tables)
│   └── skills/                # 15 shared finance skills
│       └── finanzas/
│           ├── yahoo-finance-stocks
│           ├── company-financials
│           ├── macro-indicators
│           ├── portfolio-analysis
│           ├── sector-comparison
│           ├── fixed-income
│           ├── etf-research
│           ├── commodities
│           ├── forex-markets
│           ├── asset-allocation
│           ├── risk-metrics
│           ├── global-markets-snapshot
│           ├── alternatives-overview
│           ├── earnings-analysis
│           └── investment-ideas
│
├── scripts/
│   ├── patch-reasoning.py     # Patches hermes-agent API to emit reasoning_content
│   ├── mysql-mcp-server.py    # Custom MCP server for MySQL
│   └── create-sample-db.py    # Generates sample_company.db
│
└── .github/workflows/
    ├── deploy-frontend.yml     # Build → S3 → CloudFront invalidation
    ├── deploy-backend.yml      # Docker build → ECR → SSM deploy
    └── deploy-skills.yml       # Deploy profiles/shared/ → all users
```

---

## Shared Skills (15 financial skills)

All skills are in `profiles/shared/skills/finanzas/` and deployed to all 3 user profiles via CI.

| Skill | Trigger phrases | What it does |
|-------|----------------|--------------|
| **yahoo-finance-stocks** | "precio de BBVA", "cotización Santander" | Stock quotes, historical, volume, dividends via yfinance |
| **company-financials** | "fundamentales de Inditex", "balance de Repsol" | Balance sheet, P&L, cash flow, ratios (PER, ROE, margins) |
| **macro-indicators** | "datos macro de España", "PIB, inflación" | GDP, CPI, interest rates, PMI, employment |
| **portfolio-analysis** | "analiza mi cartera", "Sharpe, VaR" | Risk/return metrics, correlation, drawdown, beta |
| **sector-comparison** | "compara BBVA y Santander" | Peer comparison tables with valuation metrics |
| **fixed-income** | "curva de tipos", "yield bono alemán" | Sovereign bonds, yield curves, credit spreads |
| **etf-research** | "compara ETFs del S&P 500" | TER, AUM, tracking error, holdings |
| **commodities** | "precio del oro", "petróleo Brent" | Gold, oil, copper, grains via futures |
| **forex-markets** | "cambio euro dólar", "DXY" | Currency pairs, cross rates, EUR impact |
| **asset-allocation** | "distribución de cartera", "perfil moderado" | Strategic/tactical allocation, rebalancing |
| **risk-metrics** | "VaR de mi cartera", "stress test" | VaR, CVaR, Sharpe, Sortino, Calmar, drawdown |
| **global-markets-snapshot** | "cómo están los mercados" | Cross-asset overview: equities, bonds, FX, commodities |
| **alternatives-overview** | "REITs europeos", "cripto institucional" | REITs, infra, PE proxies, crypto institutional |
| **earnings-analysis** | "resultados de Inditex", "earnings" | Quarterly surprises, guidance, analyst consensus |
| **investment-ideas** | "ideas de inversión value" | Screening by value/quality/momentum/dividends |

### Adding a new skill

1. Create `profiles/shared/skills/finanzas/<name>/SKILL.md`
2. Push to `main` → pipeline deploys to all profiles automatically

---

## MCP: SQLite Sample Database

An MCP (Model Context Protocol) server exposes a sample company database to the agent.

### Configuration

```yaml
# profiles/shared/config.yaml
mcp_servers:
  sqlite:
    command: mcp-server-sqlite
    args:
      - --db-path
      - /opt/hermes-gw/sample_company.db
    transport: stdio
```

### Sample Database

`profiles/shared/sample_company.db` — SQLite, 4 tables:

| Table | Rows | Description |
|-------|------|-------------|
| companies | 8 | TechNova, FinServ Global, GreenEnergy Plus... |
| departments | 10 | Engineering, Sales, Finance, HR, R&D... |
| employees | 15 | Ana García, Marcus Johnson, Sophie Dubois... |
| projects | 8 | CloudMigration, AIChatbot, RiskEngine... |

### Agent Tools

When the agent connects to this MCP, it gains these tools:

- `mcp_sqlite_list_tables` — list all tables
- `mcp_sqlite_describe_table` — show table schema
- `mcp_sqlite_read_query` — execute SELECT queries

### Example Queries

```
qué tablas hay en la base de datos
```
```
cuántos empleados hay por departamento y su salario medio
```
```
dime los proyectos activos y su presupuesto
```
```
lista los empleados que ganan más de 80000 ordenados por salario
```
```
cuál es la empresa con más empleados y en qué sector está
```

---

## CI/CD Pipelines

### deploy-frontend.yml
Trigger: push to `frontend/**`  
1. `npm ci` → `npm run build`  
2. `aws s3 sync dist/ s3://hermes-gw-frontend-649091762015/ --cache-control "max-age=3600"`  
3. `aws s3 cp dist/index.html ... --cache-control "no-cache"`  ← prevents stale HTML  
4. CloudFront invalidation `/*`

### deploy-backend.yml
Trigger: push to `backend/**`  
1. Docker build + push to ECR  
2. SSM send-command to EC2: `docker compose pull && up -d`  
3. Applies `scripts/patch-reasoning.py` for reasoning in SSE

### deploy-skills.yml (Deploy Shared Profiles)
Trigger: push to `profiles/shared/**`  
1. Packs `profiles/shared/` as tarball  
2. SSM send-command to EC2:  
   - Extracts tarball  
   - Copies `skills/` → all profiles (`cp -rn`, never overwrites agent-created skills)  
   - Copies `config.yaml` → all profiles  
   - Copies `sample_company.db` → `/opt/hermes-gw/`  
3. Restarts orchestrator container

---

## Key Design Decisions

### Frontend
- **Only final response shown**: tool output, reasoning, and intermediate text are stripped
- **SSE reset on tool calls**: `streamContent` cleared on each `hermes.tool.progress` event
- **No post-stream reload**: `loadMessages()` removed after streaming to avoid server-side noise
- **Index.html no-cache**: prevents stale JS/CSS references after deploys

### Backend
- **15s SSE keepalive**: `asyncio.Queue` + `ensure_future` pattern injects `: keepalive\n\n`
- **CORS enabled**: allows direct ALB access if needed
- **30s gateway startup timeout**: increased from 15s for slow hermes-agent init
- **Lock file cleanup**: stale `gateway.lock`/`gateway.pid` removed on spawn failure

### Infrastructure
- **CloudFront HTTP/1.1**: HTTP/2 caused `ERR_HTTP2_PROTOCOL_ERROR` with SSE
- **ALB idle timeout 300s**: increased from 60s for long tool executions
- **CloudFront origin read timeout 60s**: max allowed, keepalives prevent drops
- **Docker image prune**: run periodically to prevent disk full (50GB EC2)

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `e.map is not a function` | Backend returning JSON wrapper instead of array | Backend extracts `.data` from `{object:"list", data:[...]}` |
| `ERR_HTTP2_PROTOCOL_ERROR` | CloudFront HTTP/2 + SSE | Forced CloudFront to HTTP/1.1 |
| Empty response / bubble stops | CloudFront 60s timeout | 15s keepalive injection |
| Gateway fails to start (port 864X) | Stale lock files or disk full | `docker image prune -a -f`, clean locks |
| Raw tool output in chat | `loadMessages()` overwrites clean messages | Removed post-stream reload, reset on tool events |
| `(empty response)` | MCP config format error (list vs dict) | MCP servers must be a dict keyed by name |
| `'list' object has no attribute 'items'` | Wrong MCP config format | Changed from list to dict format |

---

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py              # starts on :8080
python main.py isaac        # generate test JWT

# Frontend
cd frontend
npm install
npm run dev                 # starts dev server

# Generate tokens
python backend/main.py isaac   # profile: user-isaac
python backend/main.py miguel  # profile: user-miguel
python backend/main.py pablo   # profile: user-pablo
```

---

## Infrastructure

Managed by Terraform in [`isperez957/terraform`](https://github.com/isperez957/terraform) → `hermes-gw/`:

| Resource | ID/Name |
|----------|---------|
| EC2 | `i-0c0f8dd5d194ceaf2` (t3.medium, 50GB) |
| ALB | `hermes-gw-alb` |
| ECR | `hermes-gw-orchestrator` |
| S3 | `hermes-gw-frontend-649091762015` |
| CloudFront | `E18SDGI3H66ZQE` |
| IAM OIDC | `terraform-ci-oidc` (GitHub Actions) |
