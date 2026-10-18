# LankaMacro AI

**Sri Lankan economic research with traceable evidence.**

Built by **Akinda Gunarathne** and **Sachin Gimahana** as an independent project.

LankaMacro AI brings economic questions, historical charts, original publications and transparent financial scenarios into one research workspace. This repository contains the first working milestone, not the complete proposed RAG platform.

## What works

| Workspace | Implemented behavior |
| --- | --- |
| Overview | Source-backed headline, food and non-food inflation cards and a historical chart |
| Research chat | Deterministic answers to supported CCPI questions, comparisons, definitions and date-specific lookups; original-source citations; relevant charts |
| Economy explorer | 13 monthly observations; rate/index selection; series toggles; date filters; line/bar charts; exact data table; CSV with provenance |
| Investor tools | Decimal-based inflation-adjusted return scenarios with visible assumptions |
| Source library | Original DCS PDF, page-4 source viewer, review metadata, SHA-256 and three reviewed evidence notes |
| Saved research | Save answers and chart snapshots locally in the browser; remove saved items |
| PDF ingestion | CLI staging with SHA-256, page extraction and explicit OCR/review status; no automatic publication |

**No paid model API key is required.** The chat is a deliberately limited reviewed-evidence baseline. It does not call an LLM or perform semantic retrieval. It refuses unsupported measures, periods, causal explanations and forecasts instead of fabricating an answer. Questions are independent; conversation context is not inferred.

## Start locally

Prerequisites: **Node.js 24**, **Python 3.12**, and [uv](https://docs.astral.sh/uv/getting-started/installation/). Run all commands from the repository root.

```sh
git clone https://github.com/akindaG/LankaMacroAI.git
cd LankaMacroAI
npm ci
uv sync --frozen
npm run dev
```

Open **http://localhost:3000**. The combined development command starts FastAPI on `127.0.0.1:8008` and Next.js on `127.0.0.1:3000`, on Windows, macOS and Linux. Stop both with Ctrl+C. A checked snapshot seeds the local SQLite database automatically. The original PDF must remain in `data/sources/`; a changed checksum stops publication.

To run the processes separately:

```sh
# Terminal 1
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8008

# Terminal 2
npm run dev:web
```

Backend API documentation: **http://localhost:8008/docs**. Next.js proxies `/api/*` to the backend. Set `BACKEND_URL` before starting/building Next.js only if the backend is elsewhere. Set `DATABASE_URL` on the backend to use PostgreSQL; `.env.example` documents both settings. The default works without an environment file.

### PostgreSQL through Docker Compose

```sh
docker compose up --build
```

Open **http://localhost:3000**. This creates PostgreSQL 17 and both application containers. Web access binds to localhost; database and API are internal. The default database password is for this isolated development setup. Docker configuration is provided but has not been exercised in the build workspace; local SQLite startup and production compilation were verified.

### Verify

```sh
uv run python -m pytest -q
uv run ruff check backend tests
uv run ruff format --check backend tests
npm run typecheck
npm run build
```

The reconstruction was verified with **37 backend tests** plus TypeScript and an optimized production build on 18 October 2026. GitHub Actions runs the same checks and adds a PostgreSQL publication check. See [verification notes](docs/verification.md) for scope and limitations.

## The real data behind the charts

- **Compiler:** Department of Census and Statistics, Sri Lanka (DCS).
- **Release:** [CCPI — September 2026](https://www.statistics.gov.lk/WebReleases/CCPI_20260930E), released 30 September 2026.
- **Location:** physical/printed **page 4**, Table 03 and Section 2.
- **Definition:** CCPI base **2021=100**. Headline, food and non-food inflation are **year-on-year percentages**; the CCPI index is in index points.
- **Coverage:** September 2025–September 2026, 13 observations for each of four series (52 values).
- **Review:** manually transcribed and visually checked against the original PDF on 18 October 2026. The relevant PDF page is scanned; it is not machine-extracted table data.
- **Archived PDF:** `data/sources/ccpi-september-2026.pdf`.
- **SHA-256:** `614ca32cf76856585f2e9bf994faacc6274ca29667c9411cf5ff8e2dc3a28129`.

Example: headline inflation moved from **1.5% in September 2025** to **8.0% in September 2026**, a change of **+6.5 percentage points**. This is not a 6.5% relative increase. CCPI is not NCPI. These observations are a historical release snapshot, not live readings or a forecast. Third-party source documents remain attributed to their publisher; including the PDF does not imply ownership or official affiliation.

## API examples

```sh
curl http://localhost:8008/api/series
curl "http://localhost:8008/api/series.csv?start=2026-08&end=2026-09"
curl -X POST http://localhost:8008/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Compare CCPI inflation September 2025 and September 2026"}'
curl -X POST http://localhost:8008/api/scenarios/real-return \
  -H "Content-Type: application/json" \
  -d '{"principal":"100000","nominal_rate":"10","inflation_rate":"8","years":1}'
```

The calculator example returns nominal LKR **110,000.00**, real purchasing power **101,851.85**, and real annual return **1.8519%**. It assumes constant annual rates, annual compounding, and no taxes, fees or cash flows.

### Stage another source

```sh
uv run python -m backend.ingest path/to/report.pdf \
  --title "Report title" \
  --publisher "Original publisher" \
  --source-url "https://example.org/original-publication"
```

This only stages a local file under ignored `var/staging/<sha256>/`. It does not download arbitrary URLs or add unreviewed data to serving tables. Scanned or partially scanned documents are flagged `needs_ocr_and_review`. A reviewer must check extraction, definitions and values before extending the reviewed snapshot and its tests.

## Code map

```text
app/                  Next.js research interface and typed API client
app/components/       Charts, original-source dialog, scenario tool
backend/              FastAPI routes, SQLAlchemy persistence, publication, staging
data/inflation.json   Reviewed observations and provenance
data/sources/         Preserved original publication
tests/                Numeric, refusal, API, validation and staging tests
docs/                 Architecture, implementation status and verification
.github/workflows/    Frontend, Python and PostgreSQL checks
```

## Next milestones

The [architecture](docs/architecture.md) describes the implementation boundaries and staged expansion. Next are evaluated document retrieval, versioned migrations, embedding/search publication, and grounded generation with claim validation. Authentication, rate limits, secure user persistence, scheduled ingestion, monitoring and deployment hardening must precede a public hosted pilot.

The public repository is **source publication**, not a deployed service. The current application has no user authentication; saved research is browser-local. No cloud sync, scheduled source refresh, live markets, investment execution, multilingual support, complete CBSL corpus or measured RAG accuracy is claimed.

LankaMacro AI is not affiliated with CBSL or DCS. Scenario outputs support research and do not constitute personal financial advice.
