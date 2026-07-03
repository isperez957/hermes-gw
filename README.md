# Hermes Gateway

Multi-tenant chat application for [Hermes Agent](https://github.com/nousresearch/hermes-agent). A React frontend connected to a FastAPI orchestrator that spawns and manages Hermes Agent gateway processes — one per user, fully isolated.

## Architecture

```
Frontend (React SPA)           Backend (FastAPI)              Hermes Gateways
─────────────────────         ─────────────────────          ────────────────
S3 + CloudFront                EC2 (Docker)                  Processes on EC2
     │                              │                              │
     │  POST /api/chat              │  proxy to gateway           │
     ├─────────────────────────────►├─────────────────────────────►│
     │                              │                              │
     │  ◄── SSE stream ───          │  ◄── SSE stream ───          │
     │                              │                              │
```

- **Frontend**: Vite + React + TypeScript chat UI, deployed to S3 + CloudFront
- **Backend**: FastAPI orchestrator running in Docker on EC2, proxying requests to per-user Hermes gateway processes
- **Gateways**: Hermes Agent processes (one per user), each with isolated profile, skills, and memories

## Repo structure

```
hermes-gw/
├── frontend/          # React SPA (Vite + TypeScript)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts           # API client (SSE streaming, sessions, auth)
│   │   └── components/      # Chat.tsx, Message.tsx
│   └── ...
├── backend/           # FastAPI orchestrator
│   ├── main.py              # API routes, SSE proxy
│   ├── gateway_manager.py   # Hermes gateway lifecycle (spawn/kill/reap)
│   ├── auth.py              # JWT authentication
│   └── Dockerfile
└── .github/workflows/
    ├── deploy-frontend.yml  # Build → S3 sync → CloudFront invalidation
    └── deploy-backend.yml   # Docker build → ECR push → SSM deploy to EC2
```

## CI/CD

Both pipelines trigger on push to `main`, filtered by `frontend/**` or `backend/**`.

### Frontend
- Builds with Vite, syncs to S3, invalidates CloudFront
- Secrets required: `FRONTEND_S3_BUCKET`, `CLOUDFRONT_DISTRIBUTION_ID`
- Optional variable: `VITE_API_URL` (API endpoint, default: `http://localhost:8080`)

### Backend
- Builds Docker image, pushes to ECR (`hermes-gw-orchestrator`), deploys to EC2 via SSM Run Command
- Prerequisites:
  - EC2 instance tagged `Name=hermes-gw-app` (created by Terraform in the `isperez957/terraform` repo)
  - EC2 instance profile needs `AmazonSSMManagedInstanceCore` policy

## Local development

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py              # starts on :8080
python main.py isaac        # generates a test JWT for user "isaac"
```

### Frontend

```bash
cd frontend
npm install
npm run dev                 # starts on :3000, proxies API to :8080
```

### Generate test tokens

```bash
cd backend
python main.py isaac   # token for user "isaac" (profile: user-isaac)
python main.py miguel  # token for user "miguel" (profile: user-miguel)
python main.py pablo   # token for user "pablo" (profile: user-pablo)
```

## Infrastructure

Infrastructure (EC2, ALB, ECR, S3, CloudFront) is managed by Terraform in [`isperez957/terraform`](https://github.com/isperez957/terraform) under `hermes-gw/`.
