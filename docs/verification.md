# Verification record

Date: 18 October 2026. This records the rebuilt repository contents after workspace maintenance removed the earlier unpublished checkout. Earlier test counts do not substitute for these checks.

## Verified locally

- `uv run python -m pytest -q`: **37 passed**. Coverage includes exact source hash, first/last checked observations, idempotent publication, source metadata, PDF streaming, CSV provenance and filtered ranges, deterministic numerical answers, percentage-point/index-point units, out-of-corpus refusal, date resolution, partial-year disclosure, exact real returns, deflation, input validation and scanned-PDF review staging.
- `npm run typecheck`: passed.
- `npm run build`: Next.js optimized production compilation passed.
- The DCS original PDF was recovered from its official release URL. Its SHA-256 matches the previously reviewed source. Physical page 4 was rendered and all 13 monthly rows visually verified.

## Limits

- These are functional correctness checks for one reviewed release, not measured RAG accuracy, retrieval recall, load performance or financial forecasts.
- A final browser visual/mobile recheck of the prior build was blocked by browser URL security policy. The reconstructed UI requires a new browser verification when an allowed preview is available; no final visual pass is claimed here.
- Docker Compose is provided but not locally exercised; PostgreSQL publication is a separate GitHub Actions job, whose remote result must be checked after publication.
- The current FastAPI/Starlette test wrapper emits a deprecation warning for its HTTPX adapter. Tests pass; this warning does not establish future adapter compatibility.
- No public deployment, account security review, penetration test, production recovery drill, cross-browser audit or accessibility certification has been performed.

The React review checks typed API boundaries, effect cleanup, request locking, independent concurrent initial reads, dynamic chart loading, stable list keys, native dialog focus handling, visible labels, chart-table alternatives and versioned browser storage. This is an implementation review, not a browser accessibility audit.
