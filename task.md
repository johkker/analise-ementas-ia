# Tasks

- [x] Debug and Fix Ingestion Errors
    - [x] Fix multi-year range constraint (400 Bad Request)
    - [x] Fix ForeignKey violations (Missing Politico IDs)
    - [x] Implement 90-day chunking logic for 180+ day requests
- [x] Implement Deputados Expenses Ingestion
    - [x] Add `fetch_gastos_task` to `data_fetcher.py`
    - [x] Fix `ResilienceIngestor` batch loop
    - [x] Update `manual_ingest.py`
- [x] API & Entrypoints
- [x] Deployment Config
- [x] Feature: Full Deputy Ingestion (Refined)
    - [x] Update `src/schemas/camara_api.py` for full Deputado data.
    - [x] Update `src/models/politico.py` with `id_legislatura`.
    - [x] Refine `ResilienceIngestor` with party linking and batch upserts.
    - [x] Verify population.
- [x] Feature: Dashboard Improvements & Expense Exploration
    - [x] Update `/stats/dashboard` to filter by current year.
    - [x] Create `/gastos/exploration` API for filtering/searching.
    - [x] Update Dashboard Frontend with year-filtered data.
    - [x] Implement Expense Exploration Page with detailed filters.
    - [x] Add "Curiosity Cards" (Top spenders, anomalous clusters).

- [x] Feature: Advanced Data Exploration & Deputy Insights
    - [x] Extend `/gastos/exploration` with `data_inicio/fim` filters.
    - [x] Implement Date Range Picker/Period Filter on Expenses page.
    - [x] Implement Dynamic Sorting (Date/Value) on Expenses page.
    - [x] Add React Query for robust frontend caching.
    - [x] Create `/deputados` exploration page.
    - [x] Implement `DeputyDetailsModal` (Expenses, Votes, Projects).
    - [x] Create About page with data disclaimers and developer info.

- [/] Deployment & DevOps
    - [/] Deploy Frontend to Vercel.
    - [ ] Configure Environment Variables on Vercel Dashboard.
    - [ ] Verify Production API Connectivity.
