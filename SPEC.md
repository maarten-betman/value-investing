# Value Investing Tracker — Technical Specification

## 1. Overview

A personal web application that automates stock screening using Benjamin Graham's value investing methodology, focused on European and Dutch (Euronext Amsterdam) markets. The app calculates intrinsic value, identifies margin of safety, and suggests investment opportunities — with LLM-powered news sentiment analysis and Jupyter notebook integration for custom research.

**Single-user, self-hosted on a VPS via Coolify + Docker Compose.**

---

## 2. Core Concepts

The app implements Benjamin Graham's value investing framework:

| Concept | Description |
|---|---|
| **Intrinsic Value** | The true worth of a company based on fundamentals, independent of market price |
| **Margin of Safety** | The discount between intrinsic value and market price — the larger the gap, the safer the investment |
| **Mr. Market** | Market prices fluctuate irrationally; the app helps exploit undervaluations rather than follow sentiment |
| **Diversification** | Graham recommended 30-40+ positions to reduce individual stock risk |
| **Fundamental Analysis** | All decisions based on financial statements, not price momentum or speculation |

---

## 3. Architecture

### 3.1 High-Level Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        Coolify (VPS)                    │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   Frontend   │  │   Backend    │  │  JupyterHub   │  │
│  │  React/TS    │  │  FastAPI     │  │  (Notebooks)  │  │
│  │  Nginx       │  │  + APSched   │  │               │  │
│  │  :80/:443    │  │  :8000       │  │  :8888        │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘  │
│         │                 │                  │           │
│         │        ┌────────┴────────┐         │           │
│         └────────┤   PostgreSQL    ├─────────┘           │
│                  │   :5432         │                     │
│                  └────────┬────────┘                     │
│                           │                              │
│                  ┌────────┴────────┐                     │
│                  │     Redis       │                     │
│                  │  (cache/queue)  │                     │
│                  │   :6379         │                     │
│                  └─────────────────┘                     │
└─────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │   FMP    │ │  LLM API │ │ yfinance │
        │  (data)  │ │(sentiment│ │(fallback)│
        └──────────┘ └──────────┘ └──────────┘
```

### 3.2 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18+, TypeScript, Vite, TailwindCSS |
| **Charts** | Recharts or TradingView Lightweight Charts |
| **State Management** | TanStack Query (server state) + Zustand (client state) |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2 |
| **ORM** | SQLAlchemy 2.0 (async) + Alembic (migrations) |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis (API response caching, rate limit tracking) |
| **Scheduler** | APScheduler 4.x (async, persistent job store in Postgres) |
| **Auth** | JWT-based (fastapi-users or custom) |
| **Data Provider** | Financial Modeling Prep (primary), yfinance (fallback/price only) |
| **LLM** | OpenAI API or Anthropic API (configurable) |
| **Notebooks** | JupyterHub (Docker service, shared DB access) |
| **Deployment** | Docker Compose on Coolify |

### 3.3 Repository Structure

```
value-investing/
├── SPEC.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Settings via pydantic-settings
│   │   ├── database.py              # Async engine, session factory
│   │   │
│   │   ├── auth/
│   │   │   ├── router.py            # Login, register, token refresh
│   │   │   ├── models.py            # User model
│   │   │   ├── schemas.py           # Auth request/response schemas
│   │   │   ├── dependencies.py      # get_current_user dependency
│   │   │   └── security.py          # JWT, password hashing
│   │   │
│   │   ├── stocks/
│   │   │   ├── router.py            # Stock CRUD, search, details
│   │   │   ├── models.py            # Stock, FinancialStatement, PriceHistory
│   │   │   ├── schemas.py
│   │   │   └── service.py           # Business logic
│   │   │
│   │   ├── screening/
│   │   │   ├── router.py            # Screening config, results, history
│   │   │   ├── models.py            # ScreeningProfile, ScreeningResult
│   │   │   ├── schemas.py
│   │   │   ├── service.py           # Orchestrates screening runs
│   │   │   ├── criteria.py          # Graham criteria calculations
│   │   │   └── valuations.py        # Intrinsic value models
│   │   │
│   │   ├── portfolio/
│   │   │   ├── router.py            # Holdings, transactions, performance
│   │   │   ├── models.py            # Portfolio, Holding, Transaction
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   │
│   │   ├── watchlist/
│   │   │   ├── router.py            # Watchlist CRUD, alerts
│   │   │   ├── models.py            # Watchlist, WatchlistItem, Alert
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   │
│   │   ├── sentiment/
│   │   │   ├── router.py            # Sentiment scores, news feed
│   │   │   ├── models.py            # NewsArticle, SentimentScore
│   │   │   ├── schemas.py
│   │   │   ├── service.py           # Orchestrates LLM analysis
│   │   │   ├── news_fetcher.py      # Fetches news from FMP / RSS
│   │   │   └── llm_analyzer.py      # LLM prompt logic
│   │   │
│   │   ├── data_providers/
│   │   │   ├── base.py              # Abstract provider interface
│   │   │   ├── fmp.py               # Financial Modeling Prep client
│   │   │   ├── yfinance_client.py   # yfinance fallback client
│   │   │   └── cache.py             # Redis caching layer
│   │   │
│   │   └── scheduler/
│   │       ├── jobs.py              # Job definitions
│   │       └── setup.py             # APScheduler config + job registration
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_screening/
│       ├── test_portfolio/
│       ├── test_valuations/
│       └── test_data_providers/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/                      # API client (axios/fetch wrapper)
│       │   ├── client.ts
│       │   ├── stocks.ts
│       │   ├── screening.ts
│       │   ├── portfolio.ts
│       │   ├── watchlist.ts
│       │   └── sentiment.ts
│       ├── components/
│       │   ├── layout/               # Shell, sidebar, navbar
│       │   ├── charts/               # Reusable chart components
│       │   ├── tables/               # Data tables with sorting/filtering
│       │   └── common/               # Buttons, cards, modals, badges
│       ├── pages/
│       │   ├── Dashboard.tsx         # Main overview dashboard
│       │   ├── Screener.tsx          # Screening config + results
│       │   ├── StockDetail.tsx       # Individual stock deep dive
│       │   ├── Portfolio.tsx         # Holdings + performance
│       │   ├── Watchlist.tsx         # Tracked stocks + alerts
│       │   ├── Sentiment.tsx         # News + sentiment dashboard
│       │   ├── Settings.tsx          # Sectors, API keys, preferences
│       │   └── Login.tsx
│       ├── hooks/                    # Custom React hooks
│       ├── store/                    # Zustand stores
│       ├── types/                    # TypeScript type definitions
│       └── utils/                    # Formatters, helpers
│
├── jupyter/
│   ├── Dockerfile
│   ├── requirements.txt             # pandas, sqlalchemy, matplotlib, etc.
│   └── notebooks/
│       ├── examples/
│       │   ├── stock_analysis.ipynb
│       │   └── portfolio_review.ipynb
│       └── .gitkeep
│
└── docker/
    └── nginx/
        └── default.conf             # Reverse proxy config
```

---

## 4. Data Model

### 4.1 Entity Relationship Overview

```
User (1) ──── (N) Portfolio (1) ──── (N) Holding
                                          │
User (1) ──── (N) Watchlist (1) ── (N) WatchlistItem
                                          │
                                          ▼
               ScreeningProfile ────► Stock (1) ──── (N) PriceHistory
                    │                  │
                    ▼                  ├──── (N) FinancialStatement
              ScreeningResult          ├──── (N) ValuationSnapshot
                                       ├──── (N) SentimentScore
                                       └──── (1) Sector
```

### 4.2 Core Tables

#### `users`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| email | VARCHAR(255) | Unique |
| hashed_password | VARCHAR(255) | bcrypt |
| is_active | BOOLEAN | Default true |
| created_at | TIMESTAMPTZ | |

#### `stocks`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| ticker | VARCHAR(20) | e.g. `ASML.AS` |
| name | VARCHAR(255) | e.g. `ASML Holding N.V.` |
| exchange | VARCHAR(50) | e.g. `EURONEXT` |
| sector | VARCHAR(100) | e.g. `Technology` |
| industry | VARCHAR(100) | e.g. `Semiconductors` |
| currency | VARCHAR(10) | e.g. `EUR` |
| country | VARCHAR(50) | e.g. `NL` |
| is_active | BOOLEAN | Delisted tracking |
| last_data_refresh | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | |

#### `financial_statements`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| stock_id | UUID | FK → stocks |
| period_type | ENUM | `annual`, `quarterly` |
| period_end | DATE | e.g. `2025-12-31` |
| revenue | DECIMAL(20,2) | |
| net_income | DECIMAL(20,2) | |
| eps | DECIMAL(10,4) | Earnings per share |
| book_value_per_share | DECIMAL(10,4) | |
| total_assets | DECIMAL(20,2) | |
| total_liabilities | DECIMAL(20,2) | |
| current_assets | DECIMAL(20,2) | |
| current_liabilities | DECIMAL(20,2) | |
| total_debt | DECIMAL(20,2) | |
| total_equity | DECIMAL(20,2) | |
| dividends_per_share | DECIMAL(10,4) | |
| free_cash_flow | DECIMAL(20,2) | |
| operating_cash_flow | DECIMAL(20,2) | |
| raw_data | JSONB | Full API response for flexibility |

#### `price_history`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| stock_id | UUID | FK → stocks |
| date | DATE | |
| open | DECIMAL(12,4) | |
| high | DECIMAL(12,4) | |
| low | DECIMAL(12,4) | |
| close | DECIMAL(12,4) | |
| adj_close | DECIMAL(12,4) | |
| volume | BIGINT | |

*Composite index on (stock_id, date). Partitioned by year for large datasets.*

#### `valuation_snapshots`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| stock_id | UUID | FK → stocks |
| calculated_at | TIMESTAMPTZ | |
| market_price | DECIMAL(12,4) | Current price at calculation time |
| graham_number | DECIMAL(12,4) | √(22.5 × EPS × BVPS) |
| graham_formula_value | DECIMAL(12,4) | EPS × (8.5 + 2g) |
| ncav_per_share | DECIMAL(12,4) | (Current Assets − Total Liabilities) / Shares |
| dcf_value | DECIMAL(12,4) | Discounted cash flow estimate |
| pe_ratio | DECIMAL(10,4) | |
| pb_ratio | DECIMAL(10,4) | |
| current_ratio | DECIMAL(10,4) | |
| debt_to_equity | DECIMAL(10,4) | |
| dividend_yield | DECIMAL(10,4) | |
| margin_of_safety_pct | DECIMAL(10,4) | Best-estimate intrinsic value vs market price |
| earnings_stability | DECIMAL(10,4) | Consistency score over 5-10 years |
| composite_score | DECIMAL(10,4) | Weighted overall value score |

#### `screening_profiles`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users |
| name | VARCHAR(255) | e.g. `Dutch Value Stocks` |
| description | TEXT | |
| exchanges | JSONB | `["EURONEXT"]` |
| sectors | JSONB | `["Technology", "Industrials"]` |
| countries | JSONB | `["NL", "DE", "FR"]` |
| included_tickers | JSONB | Explicit include list |
| excluded_tickers | JSONB | Explicit exclude list |
| criteria | JSONB | See section 5.2 for schema |
| is_active | BOOLEAN | Whether scheduler runs this profile |
| schedule | VARCHAR(50) | Cron expression, e.g. `0 18 * * 1-5` |
| last_run_at | TIMESTAMPTZ | |

#### `screening_results`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| profile_id | UUID | FK → screening_profiles |
| stock_id | UUID | FK → stocks |
| run_at | TIMESTAMPTZ | |
| passed_criteria | JSONB | Which criteria were met |
| failed_criteria | JSONB | Which criteria were not met |
| composite_score | DECIMAL(10,4) | Ranking score |
| margin_of_safety_pct | DECIMAL(10,4) | |
| recommendation | ENUM | `strong_buy`, `buy`, `hold`, `avoid` |

#### `portfolios`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users |
| name | VARCHAR(255) | e.g. `De Giro - Value Portfolio` |
| description | TEXT | |
| currency | VARCHAR(10) | Base currency |

#### `holdings`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| portfolio_id | UUID | FK → portfolios |
| stock_id | UUID | FK → stocks |
| shares | DECIMAL(12,4) | |
| avg_cost_basis | DECIMAL(12,4) | Per share |
| first_purchased | DATE | |
| notes | TEXT | |

#### `transactions`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| portfolio_id | UUID | FK → portfolios |
| stock_id | UUID | FK → stocks |
| type | ENUM | `buy`, `sell`, `dividend` |
| shares | DECIMAL(12,4) | |
| price_per_share | DECIMAL(12,4) | |
| fees | DECIMAL(10,4) | |
| executed_at | TIMESTAMPTZ | |
| notes | TEXT | |

#### `watchlist_items`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users |
| stock_id | UUID | FK → stocks |
| target_price | DECIMAL(12,4) | Buy below this price |
| target_mos_pct | DECIMAL(10,4) | Alert when MoS exceeds this |
| notes | TEXT | |
| added_at | TIMESTAMPTZ | |

#### `news_articles`
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| stock_id | UUID | FK → stocks (nullable, can be sector-level) |
| sector | VARCHAR(100) | |
| title | VARCHAR(500) | |
| url | VARCHAR(1000) | |
| source | VARCHAR(100) | |
| published_at | TIMESTAMPTZ | |
| summary | TEXT | LLM-generated summary |
| sentiment | ENUM | `positive`, `neutral`, `negative` |
| sentiment_score | DECIMAL(5,4) | -1.0 to 1.0 |
| analysis | TEXT | LLM reasoning |
| analyzed_at | TIMESTAMPTZ | |

---

## 5. Value Investing Calculations

### 5.1 Valuation Models

#### Graham Number
```
graham_number = √(22.5 × EPS × Book Value per Share)
```
If `market_price < graham_number`, the stock may be undervalued.

#### Graham Formula (Intrinsic Value)
```
V = (EPS × (8.5 + 2g) × 4.4) / Y
```
Where:
- `EPS` = trailing twelve months earnings per share
- `g` = expected annual growth rate (5-year estimate)
- `4.4` = Graham's baseline corporate bond yield
- `Y` = current AAA corporate bond yield (adapts for interest rate environment)

#### NCAV (Net Current Asset Value)
```
NCAV per share = (Current Assets − Total Liabilities) / Shares Outstanding
```
Graham's deep-value metric. Stocks trading below NCAV are trading below liquidation value.

#### Simplified DCF
```
DCF = Σ (FCF × (1 + g)^t) / (1 + r)^t  for t=1..10  +  Terminal Value / (1 + r)^10
```
Where:
- `FCF` = free cash flow
- `g` = estimated growth rate
- `r` = discount rate (WACC or fixed hurdle rate, e.g. 10%)

#### Composite Score
Weighted combination of all models, normalized to 0-100:
```
composite = w1 × graham_number_score
          + w2 × graham_formula_score
          + w3 × ncav_score
          + w4 × dcf_score
          + w5 × quality_score
```
Default weights configurable per screening profile.

### 5.2 Graham Screening Criteria (Defaults)

These are the default thresholds, all configurable per screening profile:

| Criterion | Default | Notes |
|---|---|---|
| P/E ratio | ≤ 15 | Graham's upper limit |
| P/B ratio | ≤ 1.5 | Graham's upper limit |
| P/E × P/B | ≤ 22.5 | Combined Graham test |
| Current ratio | ≥ 2.0 | Short-term liquidity |
| Debt/Equity | ≤ 0.5 | Conservative leverage |
| Positive earnings | ≥ 5 consecutive years | Earnings stability |
| Dividend history | ≥ 5 years | Consistent payouts |
| Earnings growth | ≥ 3% avg over 10 years | Minimum growth |
| Margin of Safety | ≥ 30% | Discount to intrinsic value |

### 5.3 IFRS Considerations

European companies report under IFRS, not US GAAP. Key differences the app must handle:

- **Book value**: IFRS allows asset revaluation upward; GAAP does not. P/B comparisons need context.
- **R&D capitalization**: IFRS capitalizes development costs meeting certain criteria; GAAP expenses them. Affects EPS and book value for tech companies.
- **Inventory**: IFRS prohibits LIFO; GAAP allows it. Less of an issue for EU-only analysis.
- **Leases**: Both standards now require on-balance-sheet treatment (IFRS 16 / ASC 842), but implementation details differ.

The app should store raw financial data (JSONB) alongside normalized fields to allow manual verification.

---

## 6. Automated Screening Pipeline

### 6.1 Scheduled Jobs

| Job | Schedule | Description |
|---|---|---|
| `sync_stock_universe` | Daily 06:00 CET | Refresh list of active stocks from FMP for configured exchanges |
| `sync_eod_prices` | Daily 18:30 CET (after market close) | Fetch end-of-day prices for all tracked stocks |
| `sync_fundamentals` | Weekly Sunday 02:00 CET | Refresh financial statements (quarterly cycle, but check weekly for updates) |
| `run_screening` | Daily 19:00 CET | Execute all active screening profiles against latest data |
| `calculate_valuations` | Daily 19:30 CET | Recalculate intrinsic values and margin of safety |
| `fetch_news` | Every 4 hours | Pull recent news for tracked sectors/stocks |
| `analyze_sentiment` | Every 4 hours (after news fetch) | Run LLM sentiment analysis on new articles |
| `refresh_portfolio_metrics` | Daily 19:00 CET | Update portfolio performance with latest prices |

### 6.2 Data Sync Flow

```
FMP API ──► Rate Limiter ──► Redis Cache ──► Data Normalizer ──► PostgreSQL
                                                    │
                                              Validation Layer
                                          (reject incomplete data,
                                           flag IFRS anomalies)
```

### 6.3 Rate Limiting & Resilience

- FMP free tier: 250 requests/day. Paid tier: higher limits.
- Implement request budgeting: allocate daily API calls across jobs.
- Redis-backed response cache with TTLs (prices: 1 day, fundamentals: 7 days).
- Exponential backoff on API failures (3 retries, 2s/4s/8s).
- Circuit breaker pattern: if FMP fails repeatedly, switch to yfinance for price data.

---

## 7. LLM Sentiment Analysis

### 7.1 Pipeline

```
News Sources ──► Deduplication ──► LLM Analysis ──► Store Results
     │                                   │
     ├─ FMP News API                     ├─ Summary (1-2 sentences)
     ├─ RSS Feeds (fd.nl, rtlz.nl)       ├─ Sentiment (-1.0 to 1.0)
     └─ Configurable sources             └─ Key insights for stock
```

### 7.2 LLM Configuration

- Support multiple providers: OpenAI (gpt-4o-mini for cost), Anthropic (Claude Haiku for cost), or local (Ollama)
- Configurable in settings — API key stored encrypted in DB or via environment variable
- Structured output via JSON mode for consistent parsing
- Token budget tracking to manage API costs

### 7.3 Prompt Strategy

Each news article is analyzed with a structured prompt that extracts:
1. **Relevance** to the specific stock/sector (0-1)
2. **Sentiment** (negative/neutral/positive with score)
3. **Impact assessment** — short-term vs long-term, magnitude
4. **Value investing lens** — does this affect intrinsic value, earnings stability, or competitive moat?

Sector-level aggregation runs periodically to produce an overall sector sentiment trend.

---

## 8. API Design

### 8.1 Authentication

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register` | POST | Create account (disabled after first user, or invite-only) |
| `/api/auth/login` | POST | Returns JWT access + refresh tokens |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Current user profile |

### 8.2 Stocks

| Endpoint | Method | Description |
|---|---|---|
| `/api/stocks` | GET | List stocks (filter by exchange, sector, country) |
| `/api/stocks/search` | GET | Search by ticker or name |
| `/api/stocks/{id}` | GET | Full stock detail with latest valuation |
| `/api/stocks/{id}/financials` | GET | Financial statements (annual/quarterly) |
| `/api/stocks/{id}/prices` | GET | Price history (date range, interval) |
| `/api/stocks/{id}/valuations` | GET | Valuation history over time |
| `/api/stocks/{id}/news` | GET | Related news with sentiment |

### 8.3 Screening

| Endpoint | Method | Description |
|---|---|---|
| `/api/screening/profiles` | GET | List screening profiles |
| `/api/screening/profiles` | POST | Create new profile |
| `/api/screening/profiles/{id}` | PUT | Update profile |
| `/api/screening/profiles/{id}` | DELETE | Delete profile |
| `/api/screening/profiles/{id}/run` | POST | Trigger manual screening run |
| `/api/screening/profiles/{id}/results` | GET | Results history (paginated) |
| `/api/screening/results/latest` | GET | Latest results across all profiles |

### 8.4 Portfolio

| Endpoint | Method | Description |
|---|---|---|
| `/api/portfolios` | GET/POST | List / create portfolios |
| `/api/portfolios/{id}` | GET/PUT/DELETE | Portfolio CRUD |
| `/api/portfolios/{id}/holdings` | GET | Current holdings with live valuation |
| `/api/portfolios/{id}/transactions` | GET/POST | Transaction history / record new |
| `/api/portfolios/{id}/performance` | GET | Returns, allocation, MoS breakdown |
| `/api/portfolios/{id}/import` | POST | CSV import of transactions |

### 8.5 Watchlist

| Endpoint | Method | Description |
|---|---|---|
| `/api/watchlist` | GET/POST | List / add items |
| `/api/watchlist/{id}` | PUT/DELETE | Update / remove item |
| `/api/watchlist/alerts` | GET | Triggered alerts |

### 8.6 Sentiment

| Endpoint | Method | Description |
|---|---|---|
| `/api/sentiment/news` | GET | News feed (filter by stock, sector, date) |
| `/api/sentiment/overview` | GET | Sector-level sentiment aggregation |
| `/api/sentiment/stock/{id}` | GET | Stock-specific sentiment trend |

### 8.7 Settings

| Endpoint | Method | Description |
|---|---|---|
| `/api/settings` | GET/PUT | App settings (API keys, LLM config, defaults) |
| `/api/settings/sectors` | GET | Available sectors from synced data |
| `/api/settings/exchanges` | GET | Available exchanges |
| `/api/scheduler/jobs` | GET | List scheduled jobs and their status |
| `/api/scheduler/jobs/{id}/trigger` | POST | Manually trigger a job |

---

## 9. Frontend Pages

### 9.1 Dashboard (`/`)
The main overview page. At a glance:
- **Top opportunities** — Highest margin of safety stocks from latest screening
- **Portfolio summary** — Total value, daily change, overall MoS
- **Watchlist alerts** — Stocks that crossed target thresholds
- **Sector sentiment heatmap** — Color-coded sentiment by sector
- **Recent screening runs** — Latest results summary
- **Market overview** — AEX index performance, key movers

### 9.2 Screener (`/screener`)
- List of screening profiles with enable/disable toggle
- Profile editor: select exchanges, sectors, countries, individual tickers
- Configurable criteria thresholds with sliders/inputs
- Results table: sortable by composite score, MoS, individual metrics
- Expand row for detailed breakdown of why a stock passed/failed

### 9.3 Stock Detail (`/stocks/:id`)
- Header: ticker, name, price, daily change, sector
- **Valuation card**: Graham Number, Graham Formula, NCAV, DCF — all vs current price
- **Margin of Safety gauge**: visual indicator (red/yellow/green)
- **Financial charts**: revenue, earnings, book value trends over 5-10 years
- **Price chart**: with intrinsic value overlay
- **Key ratios table**: P/E, P/B, current ratio, D/E, dividend yield
- **News & sentiment feed**: recent articles with sentiment badges
- **Actions**: Add to watchlist, add to portfolio, run one-off valuation

### 9.4 Portfolio (`/portfolio`)
- Holdings table: stock, shares, cost basis, current value, gain/loss, MoS
- **Allocation chart**: pie/donut by sector, geography
- **Performance chart**: portfolio value over time vs AEX benchmark
- Transaction log with add/edit/delete
- CSV import functionality
- Per-holding MoS tracking — is each position still a value hold?

### 9.5 Watchlist (`/watchlist`)
- Tracked stocks with target price and target MoS
- Current price, current MoS, distance to target
- Alert history — when targets were hit
- Quick-add from screener results

### 9.6 Sentiment (`/sentiment`)
- News feed with sentiment badges (positive/neutral/negative)
- Sector sentiment trends over time (line chart)
- Filter by sector, stock, date range, sentiment type
- LLM analysis details expandable per article

### 9.7 Settings (`/settings`)
- **Data**: FMP API key, LLM API key/provider, refresh intervals
- **Screening defaults**: default criteria thresholds
- **Sectors & Exchanges**: toggle which sectors/exchanges to include in universe
- **Scheduler**: view job status, trigger manual runs
- **Account**: change password

---

## 10. Jupyter Notebook Integration

### 10.1 Setup
- JupyterHub runs as a separate Docker service
- Shares the same PostgreSQL connection (read-only recommended, or a read replica)
- Pre-installed packages: `pandas`, `sqlalchemy`, `matplotlib`, `seaborn`, `plotly`, `numpy`, `scipy`
- Connection helper pre-configured in notebook startup:

```python
# Available in every notebook automatically
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(DATABASE_URL)

# Example: load all valuation snapshots
df = pd.read_sql("SELECT * FROM valuation_snapshots", engine)
```

### 10.2 Example Notebooks
Shipped with the app as templates:
- `stock_analysis.ipynb` — Deep dive into a single stock's fundamentals
- `portfolio_review.ipynb` — Portfolio performance and risk analysis
- `screening_backtest.ipynb` — Test screening criteria against historical data
- `sector_comparison.ipynb` — Compare valuations across sectors

---

## 11. Deployment (Docker Compose)

### 11.1 Services

```yaml
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - REDIS_URL=redis://redis:6379
      - FMP_API_KEY=${FMP_API_KEY}
      - LLM_API_KEY=${LLM_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    # Nginx serves static build + proxies /api to backend

  jupyter:
    build: ./jupyter
    environment:
      - DATABASE_URL=postgresql://...  # sync driver for notebooks
    volumes:
      - jupyter_data:/home/jovyan/work

  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
```

### 11.2 Coolify Configuration
- Each service gets its own subdomain or path in Coolify
- Backend: `api.valueinvesting.yourdomain.com`
- Frontend: `valueinvesting.yourdomain.com`
- Jupyter: `jupyter.valueinvesting.yourdomain.com`
- Coolify handles SSL termination via Let's Encrypt
- PostgreSQL can be managed as a Coolify database resource (external to compose) or within compose

---

## 12. Development Phases

### Phase 1: Foundation
- Project scaffolding (FastAPI, React, Docker Compose)
- Database models + Alembic migrations
- Authentication (JWT)
- FMP data provider client with caching
- Basic stock sync (universe + prices)

### Phase 2: Core Value Investing
- Financial statement sync + storage
- Graham Number, Graham Formula, NCAV calculations
- Screening engine with configurable profiles
- Screening results API + basic results table in frontend

### Phase 3: Dashboard & Portfolio
- Dashboard page with key widgets
- Portfolio management (CRUD, transactions, CSV import)
- Watchlist with target alerts
- Stock detail page with valuation charts

### Phase 4: Sentiment & LLM
- News fetching pipeline
- LLM sentiment analysis integration
- Sentiment dashboard in frontend
- Sector sentiment heatmap

### Phase 5: Jupyter & Polish
- JupyterHub Docker integration
- Example notebooks
- APScheduler job management UI
- Performance optimization, error handling, edge cases

---

## 13. Configuration & Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/valueinvesting
DATABASE_URL_SYNC=postgresql://user:pass@postgres:5432/valueinvesting

# Redis
REDIS_URL=redis://redis:6379/0

# Auth
JWT_SECRET=<random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Financial Modeling Prep
FMP_API_KEY=<your-key>
FMP_BASE_URL=https://financialmodelingprep.com/api/v3

# LLM
LLM_PROVIDER=openai  # or "anthropic" or "ollama"
LLM_API_KEY=<your-key>
LLM_MODEL=gpt-4o-mini  # or "claude-3-haiku-20240307" or "llama3"
OLLAMA_BASE_URL=http://ollama:11434  # if using local

# Scheduler
SCHEDULER_TIMEZONE=Europe/Amsterdam

# Jupyter
JUPYTER_TOKEN=<access-token>
```

---

## 14. Non-Functional Requirements

| Concern | Approach |
|---|---|
| **Security** | JWT auth, password hashing (bcrypt), API keys encrypted at rest, CORS restricted to frontend domain |
| **Performance** | Redis caching for API responses, database indexes on foreign keys and date columns, pagination on all list endpoints |
| **Reliability** | APScheduler persistent job store (survives restarts), exponential backoff on external API calls, circuit breaker for data providers |
| **Observability** | Structured logging (structlog), health check endpoints (`/api/health`), job execution logs visible in UI |
| **Data Integrity** | Alembic migrations for all schema changes, raw API responses stored in JSONB for auditability, soft deletes where appropriate |
| **Cost Control** | API call budgeting, LLM token tracking, configurable refresh intervals to stay within free/paid tier limits |
