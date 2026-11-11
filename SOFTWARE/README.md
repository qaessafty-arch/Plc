# Monitoring software (optional)

FastAPI + PostgreSQL + React. **Read-only towards the PLC**: it has no code path that writes to the controller, so it cannot affect control or safety.

## Run for development (no PLC, simulated data, SQLite)

```
cd SOFTWARE/BACKEND && pip install -r requirements.txt
API_TOKEN=dev-token uvicorn app.main:app --reload        # http://localhost:8000/docs
cd ../FRONTEND && npm install && npm run dev             # http://localhost:5173
(cd ../BACKEND && python3 -m pytest -q)                  # 8 API tests
```

## Run on the monitoring PC

```
cd SOFTWARE
cp BACKEND/.env.example BACKEND/.env      # set API_TOKEN, DATABASE_URL password, PLC_SOURCE=opcua, OPCUA_URL
POSTGRES_PASSWORD=... docker compose up -d --build       # web on :8080, API on :8000
```

| Part | Notes |
|---|---|
| `BACKEND/app/sources.py` | `SimulatedSource` and `OpcUaSource` (reads `DB_Machine`, `DB_Alarms`, `DB_Recipe`); OPC UA path is untested against a real CPU |
| `BACKEND/app/collector.py` | polls every 1 s, stores a sample every 10 s, records alarm raise/clear events |
| `BACKEND/app/main.py` | status, production summary and time series, alarm history and Pareto, batch records and report, maintenance records and due list, WebSocket `/ws/live` |
| `DATABASE/schema.sql` | PostgreSQL DDL generated from the models, plus report views (not yet executed against a PostgreSQL server here; tests use SQLite) |
| `FRONTEND/` | dashboard, alarms, batches, maintenance |

Security: write endpoints need `Authorization: Bearer <API_TOKEN>`; with no token configured they are disabled. Set CORS origins explicitly, keep the PC on the isolated machine subnet, put TLS (reverse proxy) in front if the web page is reachable from the office network. The token is a shared secret - adequate for a single machine cell, not a substitute for per-user accounts.

Bag weights shown are nominal (count x target): actual weights live in the weigher or checkweigher.
