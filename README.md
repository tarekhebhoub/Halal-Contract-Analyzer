# Halal Contract Analyzer

A production-ready SaaS that analyzes legal contracts (plain-text `.txt`) and
flags clauses that may carry **potential Islamic-finance compliance risks**:
**Riba**, **Gharar**, **Maysir**, and **prohibited industries** — combining
deterministic rule-based detection with LLM contextual review, and surfacing
classical Quran / Sunnah references for educational context.

The full experience is **bilingual (English ⇄ Arabic)** — UI, RTL layout,
Arabic typography, AI explanations, summary text, and on-the-fly re-analysis
in the other language.

> ⚖️ **Disclaimer**: This tool provides risk indicators based on Islamic finance
> principles and **does not replace qualified scholarly judgment**. It never
> issues fatwas; every finding is framed as a *potential* concern.

---

## Architecture

```
┌──────────────┐     ┌────────────────────────────────┐     ┌────────────┐
│ React + Vite │ ◄─► │ Django REST API (JWT, throttle)│ ◄─► │  SQLite /  │
│  (Tailwind)  │     │  ├─ contracts: upload/extract  │     │ PostgreSQL │
│  EN / AR RTL │     │  ├─ analyzer:  rules + LLM     │     └────────────┘
└──────────────┘     │  └─ accounts:  custom user     │     ┌────────────┐
                     └──────────────┬─────────────────┘ ◄─► │   Redis    │
                                    ▼                       │  (Celery)  │
                          ┌──────────────────┐              └────────────┘
                          │ Hybrid Engine    │
                          │  • Regex rules   │
                          │  • LLM (OpenAI)  │
                          │  • Evidence base │
                          │  • Risk scoring  │
                          │  • Bilingual i18n│
                          └──────────────────┘
```

### Pipeline
1. **Upload** → MIME + size + extension validation, SHA-256 hash, owner-scoped storage.
2. **Extract** → plain-text reader (`.txt` only — keeps memory/CPU footprint minimal).
3. **Segment** → legal-numbering heuristics → paragraph fallback → NLTK sentences.
4. **Analyze** → Rule layer (multilingual EN / AR) + optional LLM with strict JSON, prompted
   to reply *in the contract's selected language*.
5. **Score** → weighted aggregation, capped 0–100; high-risk clauses dominate.
6. **Explain** → multi-section structured output per clause: header → what was detected →
   why it matters → recommendation → inline Quran / Sunnah evidences → disclaimer.
7. **Report** → JSON via API, optional ReportLab PDF export.

---

## ✨ Bilingual EN / AR support

| Layer       | What happens                                                                  |
|-------------|--------------------------------------------------------------------------------|
| Frontend UI | React Context (`I18nContext`) with `localStorage` persistence; auto-toggles `<html dir="rtl">` and the `lang` attribute. |
| Typography  | **Inter** for Latin, **Noto Naskh Arabic** for Arabic (loaded via Google Fonts). |
| Layout      | All Tailwind utilities use logical properties (`text-start`, `border-s-*`, `ps-3`) → RTL-clean. |
| Backend     | `apps/analyzer/i18n.py` — category labels, long rationale paragraphs, and template fragments per language. |
| Evidences   | Each Quran / Sunnah snippet has `{en, ar}` text; Arabic is the original Arabic script with diacritics where applicable. |
| LLM         | Prompt explicitly orders the reply language (`MUST be written in English / Arabic`); reasons expanded to 2–4 sentences. |
| Re-analyze  | One click on the Analysis page re-runs the pipeline in the other language without re-uploading. |

Toggle the UI from the header switcher (**EN / ع**); your preference is saved
locally. Switch a single contract's analysis language with the
**Re-analyze in Arabic / English** button.

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
python manage.py makemigrations accounts contracts
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

> Frontend stack pinned to **Vite 5.3.1** + **@vitejs/plugin-react 4.3.1**
> for stable JSX transform. React 18.3 + Tailwind 3.4.

### Run tests
```bash
cd backend && python manage.py test
```

---

## API

All endpoints are prefixed with `/api/v1/`. Auth = JWT (`Authorization: Bearer <access>`).

| Method | Endpoint                          | Purpose                                            |
|--------|-----------------------------------|----------------------------------------------------|
| POST   | `/auth/register/`                 | Create account                                     |
| POST   | `/auth/token/`                    | Obtain access + refresh tokens                     |
| POST   | `/auth/token/refresh/`            | Refresh access token                               |
| GET    | `/auth/register/me/`              | Current user                                       |
| POST   | `/contracts/upload/`              | Upload + analyze (multipart `file`, optional `language=en\|ar`) |
| GET    | `/contracts/`                     | List contracts                                     |
| GET    | `/contracts/{id}/`                | Contract detail (with clauses + evidences)         |
| GET    | `/contracts/{id}/analysis/`       | Aggregated analysis                                |
| POST   | `/contracts/{id}/reprocess/`      | Re-run pipeline. Body or query: `lang=en\|ar` to switch language. |
| GET    | `/contracts/{id}/report/`         | Download PDF report                                |
| DELETE | `/contracts/{id}/`                | Delete a contract                                  |

The contracts viewset accepts both `multipart/form-data` (for upload) and
`application/json` (for `reprocess` and other actions).

### Example
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"yourpass"}' | jq -r .access)

# Upload (analysis language defaults to user's preference)
curl -X POST http://localhost:8000/api/v1/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/sample_contracts/sample_loan.txt" \
  -F "title=Sample Loan" \
  -F "language=en"

# Re-analyze the same contract in Arabic
curl -X POST http://localhost:8000/api/v1/contracts/<id>/reprocess/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lang":"ar"}'
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

* `apps/analyzer/llm.py` — OpenAI client wrapper (default model `gpt-4o-mini`)
  with strict JSON-mode prompt and a `language` parameter.
* The prompt explicitly forbids declarative rulings; it returns `risk_level`,
  `category`, `reason` (2–4 sentences quoting the triggering phrase), `confidence`.
* The LLM is **optional**: if `LLM_ENABLED=False` or no API key is set, the
  rule-based engine still produces complete analyses.
* `apps/analyzer/engine.py` (v1.1.0) merges rule + LLM verdicts conservatively
  (prefers higher risk; downgrades only when LLM strongly disagrees) and assembles
  the multi-section explanation block.
* `apps/analyzer/evidences.py` — curated Quran / Sunnah references with full
  bilingual text attached to flagged clauses for educational context.
* `apps/analyzer/i18n.py` — single source of truth for translatable category
  labels, rationale paragraphs, and explanation templates.

---

## Database models

* `accounts.User` — email-login custom user, organisation, language preference.
* `contracts.Contract` — uploaded file metadata + status FSM + analysis language.
* `contracts.Clause` — segmented clause with risk, category, structured
  multi-paragraph explanation, matched keywords, evidences (JSON).
* `contracts.AnalysisResult` — aggregated score, localized summary, breakdown.

---

## Bonus features included

* ✅ **Bilingual UI (EN / AR) with full RTL** + Arabic webfont
* ✅ **Per-contract language switching** (re-analyze in Arabic / English)
* ✅ **Detailed structured explanations** (header → detection → rationale → recommendation → evidences → disclaimer)
* ✅ Multi-language detection keywords (English, Arabic)
* ✅ User language preference (EN / AR)
* ✅ PDF report export (ReportLab)
* ✅ Authentication system (JWT with refresh rotation)
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
│   │   └── analyzer/           # Rules, LLM client, hybrid engine, scoring,
│   │                           # evidences (bilingual), i18n templates
│   ├── sample_contracts/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                # Axios + JWT refresh
│   │   ├── auth/               # AuthContext provider
│   │   ├── i18n/               # I18nContext + EN/AR string maps
│   │   ├── components/         # RiskBadge, LanguageSwitcher, …
│   │   └── pages/              # Login, Register, Dashboard, Analysis
│   ├── index.html              # Loads Inter + Noto Naskh Arabic
│   ├── tailwind.config.js
│   └── Dockerfile
└── docker-compose.yml
```

---

## Troubleshooting

| Symptom                                                        | Fix                                                                 |
|----------------------------------------------------------------|----------------------------------------------------------------------|
| `no such table: accounts_user`                                 | Run `python manage.py makemigrations accounts contracts && migrate`. |
| `415 Unsupported Media Type` on `/reprocess/`                  | Ensure backend is up to date — the contracts viewset registers `JSONParser`. |
| Vite JSX / plugin errors                                       | Use the pinned versions: Vite 5.3.1 + `@vitejs/plugin-react` 4.3.1.  |
| LLM not running                                                | Set `LLM_ENABLED=True` and `OPENAI_API_KEY=sk-...` in `backend/.env`. Otherwise the rule engine alone is used. |
| Arabic text shows as boxes                                     | Make sure `index.html` loads the Noto Naskh Arabic Google Font and you have internet access on first load. |
