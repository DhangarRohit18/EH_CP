# WebGuard System Architecture & Subfolder Classification

WebGuard is an explainable multi-factor e-commerce fraud risk evaluation platform and pre-payment protection suite. To ensure modularity, separation of concerns, and clean maintainability, the codebase is classified into dedicated top-level subfolders:

```
WebGuard/
├── frontend/             # React 19 + TypeScript + Vite + TailwindCSS 4 Web Application
│   ├── src/              # Application source code
│   │   ├── components/   # Views: Simulator, Analysis, Dashboard, History, API Tester, Extension Hub
│   │   ├── engine/       # TypeScript risk engine & calibrated test vectors
│   │   ├── types/        # TypeScript interfaces and domain models
│   │   ├── App.tsx       # Main multi-view application container
│   │   ├── main.tsx      # Application entrypoint
│   │   └── index.css     # Tailwind styling & design tokens
│   ├── index.html        # HTML entry document
│   ├── vite.config.ts    # Vite bundler configuration
│   ├── tsconfig.json     # Frontend TypeScript configuration
│   └── package.json      # Frontend package descriptor
│
├── backend/              # Dual Backend Architecture (FastAPI Python + Express Node)
│   ├── app/              # FastAPI Python 3.11 Backend
│   │   ├── analyzers/    # 7 Fraud factor analyzers (domain, price, reviews, identity, policy, payment, behaviour)
│   │   ├── api/          # REST API endpoints (analysis, history, health)
│   │   ├── engine/       # Composite risk evaluation engine
│   │   ├── ml/           # Isolation Forest anomaly detection & NLP phrase similarity
│   │   ├── models/       # SQLAlchemy ORM database models
│   │   ├── config.py     # Pydantic environment settings
│   │   ├── database.py   # Database engine and session factory
│   │   └── main.py       # FastAPI application entrypoint
│   ├── server.ts         # Full-Stack Node.js Express Server (with Vite dev middleware)
│   ├── requirements.txt  # Python package dependencies
│   ├── Dockerfile        # Container build definition for backend service
│   ├── .env.example      # Backend environment variables
│   └── README.md         # Backend setup and execution guide
│
├── extension/            # Manifest V3 Chrome & Microsoft Edge Browser Extension
│   ├── manifest.json     # Chrome Extension Manifest V3 definition
│   ├── src/
│   │   ├── background/   # Background service worker (badge telemetry, API sync)
│   │   ├── content/      # Content script, DOM product data extractor, and form interception
│   │   ├── popup/        # Browser action reactive popup UI
│   │   ├── warning/      # Client-side pre-payment modal warning overlay
│   │   └── types/        # Extension type declarations
│   └── README.md         # Extension deployment and testing guide
│
├── docs/                 # Documentation, Checklists & Architectural Specifications
│   ├── ARCHITECTURE.md   # System architecture and directory classification (this file)
│   ├── API_REFERENCE.md  # Complete REST API specification
│   └── TESTING_CHECKLIST.md # End-to-end evaluation & compliance checklist
│
├── api/                  # Vercel Serverless Function entrypoint (`api/index.js`)
├── docker-compose.yml    # Multi-container orchestration (FastAPI + PostgreSQL)
├── vercel.json           # Production deployment configuration for Vercel
├── package.json          # Root orchestration package manager scripts
└── tsconfig.json         # Workspace TypeScript configuration
```

---

## 🏛️ Subfolder Classification Details

### 1. `frontend/`
- **Purpose**: Serves the primary cybersecurity analyst and consumer protection portal.
- **Key Modules**:
  - **Storefront Simulator**: Interactive mock merchant sites (including the canonical `flashdeal-electronics.local` scenario) with real-time pre-payment modal warning interception.
  - **Forensic Report**: Detailed scoring breakdown across all 7 operational risk factors with waterfall point contributions.
  - **SOC Analytics Dashboard**: Live telemetry, risk severity distributions, and threat categorization.
  - **History Ledger**: Filterable audit trail of previous storefront analyses.
  - **API Tester**: Live interactive sandbox for testing risk engine inputs.
  - **Extension Hub**: Step-by-step developer guide and emulator for the Manifest V3 browser extension.

### 2. `backend/`
- **Purpose**: High-performance risk assessment engines with hybrid heuristic rules and machine learning.
- **Components**:
  - **Python FastAPI Service** (`backend/app/`): Implements scikit-learn Isolation Forest anomaly clustering for price deviation, NLP syntactic text analysis for fake review clusters, and SQLAlchemy ORM persistence.
  - **Node.js Express Server** (`backend/server.ts`): Provides lightweight, zero-dependency full-stack development mode mounting Vite as middleware, serving `/api/v1` routes and hosting the compiled single-page application.

### 3. `extension/`
- **Purpose**: Real-time consumer protection directly inside Chrome and Microsoft Edge.
- **Workflow**:
  1. Inspects active shopping webpage DOM at `document_idle`.
  2. Extracts product title, price, domain metadata, contact details, and payment buttons.
  3. Evaluates storefront risk via local cache or API query to `/api/v1/analyze`.
  4. Intercepts checkout and "Buy Now" clicks; if composite score $\ge 60$, displays an unignorable Pre-Payment Warning overlay before payment credentials can be entered.

### 4. `docs/`
- **Purpose**: Curated documentation, test cases, and quality assurance checklists.
- **Files**:
  - `docs/ARCHITECTURE.md`: Subfolder and component classifications.
  - `docs/API_REFERENCE.md`: Endpoints, request schemas, and sample outputs.
  - `docs/TESTING_CHECKLIST.md`: Verification steps across security, privacy, and UX metrics.

---

## 🔄 Data Flow Architecture

```
User visits shopping storefront
            │
            ▼
┌──────────────────────────────┐
│  Chrome Extension (Content)  │
│  - DOM Metadata Extractor    │
│  - Checkout Click Intercept  │
└──────────────┬───────────────┘
               │ Payload: { url, domain, price, ... }
               ▼
┌──────────────────────────────┐
│   WebGuard Risk Engine       │
│   (FastAPI / Express API)    │
│   ├─ 1. Domain Credibility   │ (20%)
│   ├─ 2. Price Anomaly (ML)   │ (20%)
│   ├─ 3. Review Patterns (NLP)│ (15%)
│   ├─ 4. Website Identity     │ (15%)
│   ├─ 5. Refund Policy        │ (10%)
│   ├─ 6. Payment Methods      │ (10%)
│   └─ 7. Site Behaviour       │ (10%)
└──────────────┬───────────────┘
               │ Composite Score (0 - 100) + Explainability Breakdown
               ▼
┌──────────────────────────────────────────────┐
│  If Score >= 60:                             │
│  Pre-Payment Warning Overlay Triggered!      │
│  - Blocks unverified payment entry           │
│  - Lists exact triggered high-risk signals   │
└──────────────────────────────────────────────┘
```
