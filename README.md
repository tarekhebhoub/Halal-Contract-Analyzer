# Halal Contract Analyzer

A production-ready SaaS that analyzes legal contracts (plain-text `.txt`) and
flags clauses that may carry **potential Islamic-finance compliance risks**:
**Riba**, **Gharar**, **Maysir**, and **prohibited industries** — combining
deterministic rule-based detection with LLM contextual review, and surfacing
classical Quran/Sunnah references for educational context.

> ⚖️ **Disclaimer**: This tool provides risk indicators based on Islamic finance
> principles and **does not replace qualified scholarly judgment**. It never
> issues fatwas; every finding is framed as a *potential* concern.

---

## Architecture

```
┌──────────────┐     ┌────────────────────────────────┐     ┌────────────┐
│ React + Vite │ ◄─► │ Django REST API (JWT, throttle)│ ◄─► │ PostgreSQL │
│  (Tailwind)  │     │  ├─ contracts: upload/extract  │     └────────────┘
└──────────────┘     │  ├─ analyzer:  rules + LLM     │     ┌────────────┐
                     │  └─ accounts:  custom user     │ ◄─► │   Redis    │
                     └──────────────┬─────────────────┘     │  (Celery)  │
                                    ▼                        └────────────┘
                          ┌──────────────────┐
                          │ Hybrid Engine    │
                          │  • Regex rules   │
                          │  • LLM (OpenAI)  │
                          │  • Evidence base │
                          │  • Risk scoring  │
                          └──────────────────┘
```

### Pipeline
1. **Upload** → MIME + size + extension validation, SHA-256 hash, stored under owner-scoped path.
2. **Extract** → plain-text reader (`.txt` only — keeps memory/CPU footprint minimal).
3. **Segment** → Legal numbering heuristics → paragraph fallback → NLTK sentences.
4. **Analyze** → Rule layer (multilingual EN / AR / FR) + optional LLM with strict JSON.
5. **Score** → Weighted aggregation, capped 0–100; high-risk clauses dominate.
6. **Report** → JSON via API, optional ReportLab PDF export.

---

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env
# (optional) set OPENAI_API_KEY=sk-... and LLM_ENABLED=True in backend/.env
docker compose up --build
```

* API: http://localhost:8000/api/v1/
* Swagger docs: http://localhost:8000/api/docs/
* Frontend: http://localhost:5173/

Create a superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Local dev (no Docker)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

In dev `CELERY_TASK_ALWAYS_EAGER=True`, so analysis runs inline — no Redis
required. Toggle to `False` and start a worker for async:

```bash
celery -A config.celery worker -l info
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

### Run tests
```bash
cd backend && python manage.py test
```

---

## API

All endpoints are prefixed with `/api/v1/`. Auth = JWT (`Authorization: Bearer <access>`).

| Method | Endpoint                          | Purpose                              |
|--------|-----------------------------------|--------------------------------------|
| POST   | `/auth/register/`                 | Create account                       |
| POST   | `/auth/token/`                    | Obtain access + refresh tokens       |
| POST   | `/auth/token/refresh/`            | Refresh access token                 |
| GET    | `/auth/register/me/`              | Current user                         |
| POST   | `/contracts/upload/`              | Upload + analyze (multipart `file`)  |
| GET    | `/contracts/`                     | List contracts                       |
| GET    | `/contracts/{id}/`                | Contract detail (with clauses)       |
| GET    | `/contracts/{id}/analysis/`       | Aggregated analysis                  |
| POST   | `/contracts/{id}/reprocess/`      | Re-run the analysis pipeline         |
| GET    | `/contracts/{id}/report/`         | Download PDF report                  |
| DELETE | `/contracts/{id}/`                | Delete a contract                    |

### Example
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"yourpass"}' | jq -r .access)

curl -X POST http://localhost:8000/api/v1/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/sample_contracts/sample_loan.txt" \
  -F "title=Sample Loan"
```

---

## Security

* Custom user model + email login, JWT with refresh rotation.
* Per-route throttling: `user`, `anon`, `upload` scopes (`120/min`, `20/min`, `10/min`).
* Upload validation: extension + libmagic MIME sniffing + size cap (15 MB default).
* SHA-256 hashing of uploads (deduplication / audit).
* Owner-scoped queryset — users can only see their own contracts.
* Production-only HSTS, secure cookies, SSL redirect, X-Frame-Options DENY.
* Structured logging via Django's logging framework.

---

## AI integration

* `apps/analyzer/llm.py` — OpenAI client wrapper with strict JSON-mode prompt.
* The prompt explicitly forbids declarative rulings; it returns `risk_level`,
  `category`, `reason`, `confidence`.
* The LLM is **optional**: if `LLM_ENABLED=False` or no API key is set, the
  rule-based engine still produces complete analyses.
* `apps/analyzer/engine.py` merges rule + LLM verdicts conservatively
  (prefers higher risk; downgrades only when LLM strongly disagrees).
* `apps/analyzer/evidences.py` — curated Quran / Sunnah references attached to
  flagged clauses for educational context.

---

## Database models

* `accounts.User` — email-login custom user, organisation, language preference.
* `contracts.Contract` — uploaded file metadata + status FSM.
* `contracts.Clause` — segmented clause with risk, category, explanation,
  matched keywords, evidences (JSON).
* `contracts.AnalysisResult` — aggregated score, summary, breakdown.

---

## Bonus features included

* ✅ Multi-language detection keywords (English, Arabic, French)
* ✅ User language preference (EN / AR / FR)
* ✅ PDF report export (ReportLab)
* ✅ Authentication system (JWT)
* ✅ Django admin dashboard (`/admin/`)
* ✅ OpenAPI / Swagger docs (`/api/docs/`)
* ✅ Celery async pipeline (with eager-mode dev fallback)
* ✅ Sample test contract under `backend/sample_contracts/`

---

## Project layout

```
Halal_Contract_Analyzer/
├── backend/
│   ├── config/                 # Django project (settings, urls, celery)
│   ├── apps/
│   │   ├── accounts/           # Custom user, JWT auth
│   │   ├── contracts/          # Upload, extract, segment, API, reports
│   │   └── analyzer/           # Rules, LLM client, hybrid engine, scoring, evidences
│   ├── sample_contracts/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                # Axios + JWT refresh
│   │   ├── auth/               # AuthContext provider
│   │   ├── components/         # RiskBadge, …
│   │   └── pages/              # Login, Register, Dashboard, Analysis
│   ├── tailwind.config.js
│   └── Dockerfile
└── docker-compose.yml
```
