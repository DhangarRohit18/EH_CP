# WebGuard
### Explainable Multi-Factor E-Commerce Fraud Risk Assessment and Pre-Payment Protection

WebGuard is a production-grade cybersecurity research prototype designed to evaluate online shopping storefronts **before** a consumer enters payment credentials or transfers funds. 

Rather than relying purely on static domain blocklists (which fail against zero-day scam sites), WebGuard evaluates **seven distinct operational fraud factors** using a hybrid **Rule-Based Engine + Machine Learning (Isolation Forest & NLP pattern analysis)** to produce an explainable fraud risk index.

---

## 🛡️ Core Highlights

1. **Client-Side Pre-Payment Warning:** Intercepts checkout and "Buy Now" user actions to display a prominent modal warning with exact risk factors before sensitive information is entered.
2. **Explainable Additive Scoring:** Every score from 0 to 100 is decomposed into transparent point contributions (e.g., `+24 pts Price Anomaly`, `+20 pts Domain Age`, `+15 pts Review Patterns`).
3. **Strict Privacy Architecture:** Zero collection or inspection of credit cards, CVVs, passwords, OTPs, or authentication cookies.
4. **Manifest V3 Chrome/Edge Extension:** Production-compliant service worker, declarative content scripts, and reactive popup.
5. **FastAPI Python Backend + Express Full-Stack Server:** Modular REST API (`POST /api/v1/analyze`, `GET /api/v1/history`, `GET /api/v1/health`) with SQLite / PostgreSQL persistence.

---

## 📊 Seven Risk Factors & Exact Mathematical Weights

| Risk Factor | Weight | Detection Methodology |
| :--- | :---: | :--- |
| **Domain Credibility** | **20%** | Domain age (<14 days critical), registrar abuse TLDs (`.top`, `.shop`, `.xyz`), typosquatting brand mimicry, TLS certificate status. |
| **Price Anomaly** | **20%** | Deviation from authenticated retail MRP, discount percentage, and **Isolation Forest ML** anomaly clustering. |
| **Review Patterns** | **15%** | **NLP Syntactic Analysis**, duplicate n-gram phrase clustering, rating uniformity, burst publication windows. |
| **Website Identity** | **15%** | Verification of corporate domain email (flagging free webmail like Gmail/Proton), official phone line, physical MCA/corporate address. |
| **Refund Policy** | **10%** | Detection of missing return policy documents, vague timelines, or strict "all sales final / no refund" clauses. |
| **Payment Methods** | **10%** | Detection of prepaid-only enforcement, unverified personal UPI VPAs, cryptocurrency/wire traps, absence of buyer-protected gateways. |
| **Site Behaviour** | **10%** | Hidden DOM elements, suspicious cross-domain checkout redirections, countdown urgency timers inducing psychological pressure. |
| **Total Weight** | **100%** | **Composite Aggregated Risk Score (0 - 100)** |

### Risk Classification Thresholds
- **0 - 29:** `LOW RISK` (Proceed normally)
- **30 - 59:** `MEDIUM RISK` (Exercise caution, verify merchant)
- **60 - 79:** `HIGH RISK` (Pre-payment warning displayed, high deception indicators)
- **80 - 100:** `CRITICAL FRAUD RISK` (Pre-payment blocked, imminent loss risk)

---

## 🎯 Official College Demo Scenario: `flashdeal-electronics.local`

WebGuard includes an official calibrated evaluation scenario to demonstrate how multi-factor signals combine:

- **Target Website:** `https://flashdeal-electronics.local`
- **Product:** Apple iPhone 16 Pro 256GB
- **Price:** **₹24,999** (Market benchmark: ₹1,19,999 — **79% discount**)
- **Domain Age:** Registered **8 days ago**
- **Customer Reviews:** 4 reviews containing identical praise clauses (*"Great product arrived in 2 days..."*)
- **Refund Policy:** Discretionary 24-hour window with 35% restocking deduction
- **Payment Method:** **Prepaid Only** via Personal UPI QR code
- **Psychological Trigger:** 5-minute ticking urgency countdown banner

### 🎯 Expected Scoring Decomposition:
```
Price Anomaly:       +24 points
Domain Credibility:  +20 points
Review Patterns:     +15 points
Refund Policy:       +12 points
Payment Method:      +10 points
Site Behaviour:       +5 points
-------------------------------
Composite Score:      86 / 100 (HIGH FRAUD RISK)
Action:              Pre-Payment Security Warning Overlay Triggered!
```

---

## 📁 Repository Structure & Subfolder Classification

The codebase is organized into dedicated subfolders for modularity and maintainability:

| Subfolder | Classification | Description |
| :--- | :--- | :--- |
| [`frontend/`](file:///frontend) | **Web Application UI** | React 19 + TypeScript + Vite + TailwindCSS 4 dashboard, Storefront Simulator, and Forensic Analytics. |
| [`backend/`](file:///backend) | **API & Risk Engines** | Python FastAPI ML service (`app/`) + Full-Stack Node.js Express server (`server.ts`). |
| [`extension/`](file:///extension) | **Browser Extension** | Manifest V3 Chrome & Edge extension for client-side pre-payment interception. |
| [`docs/`](file:///docs) | **Documentation** | [System Architecture](file:///docs/ARCHITECTURE.md), [REST API Reference](file:///docs/API_REFERENCE.md), and [Testing Checklist](file:///docs/TESTING_CHECKLIST.md). |
| [`api/`](file:///api) | **Serverless Entry** | Vercel serverless function wrapper for cloud deployment. |

---

## 🚀 Quickstart & Local Execution

### 1. Web Application & Dashboard (Full-Stack Express + React)
```bash
# Install dependencies
npm install

# Run full-stack dev server (starts on http://localhost:3000)
npm run dev

# Or run frontend standalone (starts Vite on http://localhost:5173)
npm run dev:frontend
```

Visit `http://localhost:3000` to interact with:
- **Storefront Simulator:** Test live pre-payment warning interception across 5 test scenarios.
- **Forensic Report:** Interactive 7-factor scores, waterfall charts, and signal logs.
- **SOC Analytics:** Threat severity proportions and historical risk telemetry.
- **REST API Tester:** Live sandbox for `POST /api/v1/analyze`.
- **Extension Hub:** Manifest V3 extension inspector and deployment guides.

### 2. Python FastAPI Backend (Standalone)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation available at `http://localhost:8000/docs`.

### 3. Chrome / Edge Browser Extension (Manifest V3)
1. Open Google Chrome or Microsoft Edge and navigate to `chrome://extensions/`.
2. Toggle **Developer mode** (top right switch).
3. Click **Load unpacked**.
4. Select the `extension/` directory from this repository.
5. The WebGuard shield icon will appear in your browser toolbar!

---

## 🔒 Privacy & Defense-First Ethics

WebGuard is strictly engineered with **Zero-Credential Inspection**:
- Passwords, Credit/Debit card numbers, CVVs, and OTPs are **never** queried, read, or transmitted.
- Only publicly displayed catalog metadata (product title, listed price, public return terms) is processed.
- The user retains ultimate authority — warnings can be dismissed with transparent risk disclosure.
