# WebGuard REST API Reference (v1)

Both the **Node.js Express Server** (`backend/server.ts`) and **Python FastAPI Backend** (`backend/app/main.py`) expose consistent REST API v1 routes.

Base URLs:
- Node.js Full-Stack Server: `http://localhost:3000/api/v1`
- Python FastAPI Backend: `http://localhost:8000/api/v1`
- Vercel Serverless Function: `https://<deployment-url>/api/v1`

---

## 1. System Health Check
- **Endpoint**: `GET /api/v1/health`
- **Description**: Returns engine status, active machine learning model components, and operational risk factor weights.

### Response `200 OK`:
```json
{
  "status": "online",
  "service": "WebGuard E-Commerce Fraud Risk Engine",
  "timestamp": "2026-10-29T12:00:00.000Z",
  "weights": {
    "domain": 0.20,
    "price": 0.20,
    "reviews": 0.15,
    "identity": 0.15,
    "policy": 0.10,
    "payment": 0.10,
    "behaviour": 0.10,
    "total": 1.00
  },
  "ml_models": {
    "isolation_forest": "active",
    "nlp_similarity": "active"
  }
}
```

---

## 2. Storefront Risk Analysis
- **Endpoint**: `POST /api/v1/analyze`
- **Description**: Evaluates an online shopping store across seven fraud indicators and returns a composite score with point-by-point explainability.

### Request Body (`application/json`):
```json
{
  "url": "https://flashdeal-electronics.local/products/iphone-16-pro",
  "domain": "flashdeal-electronics.local",
  "domainAgeDays": 8,
  "isHttps": true,
  "productTitle": "Apple iPhone 16 Pro 256GB",
  "price": 24999,
  "marketPrice": 119999,
  "discountPercent": 79.1,
  "reviews": [
    {
      "author": "Rahul S.",
      "rating": 5,
      "text": "Great product arrived in 2 days, best price ever!",
      "timestamp": "2026-10-20"
    },
    {
      "author": "Amit K.",
      "rating": 5,
      "text": "Great product arrived in 2 days, best price ever!",
      "timestamp": "2026-10-20"
    }
  ],
  "contactEmail": "flashdeal.support@gmail.com",
  "contactPhone": "",
  "physicalAddress": "",
  "refundPolicyText": "All sales are final. Discretionary 24h return window with 35% restocking fee.",
  "paymentMethods": ["UPI", "Direct QR Code"],
  "isPrepaidOnly": true,
  "hasCountdownTimer": true,
  "hasSuspiciousRedirect": false
}
```

### Response `200 OK`:
```json
{
  "id": "analysis-1730200000000",
  "domain": "flashdeal-electronics.local",
  "compositeScore": 86,
  "riskLevel": "CRITICAL",
  "isPrePaymentTriggered": true,
  "factors": {
    "domain": {
      "name": "Domain Credibility",
      "rawScore": 100,
      "weight": 0.20,
      "contribution": 20,
      "reason": "Extremely new domain registered only 8 days ago",
      "status": "danger"
    },
    "price": {
      "name": "Price Anomaly",
      "rawScore": 100,
      "weight": 0.20,
      "contribution": 20,
      "reason": "Extreme price discount (79% off market benchmark ₹1,19,999)",
      "status": "danger"
    },
    "reviews": {
      "name": "Review Patterns",
      "rawScore": 100,
      "weight": 0.15,
      "contribution": 15,
      "reason": "High duplicate phrase clustering and unnatural 100% 5-star uniformity",
      "status": "danger"
    },
    "identity": {
      "name": "Website Identity",
      "rawScore": 100,
      "weight": 0.15,
      "contribution": 15,
      "reason": "Free webmail address (@gmail.com) used with no physical address",
      "status": "danger"
    },
    "policy": {
      "name": "Refund Policy",
      "rawScore": 80,
      "weight": 0.10,
      "contribution": 8,
      "reason": "Restrictive return window with aggressive penalty deductions",
      "status": "danger"
    },
    "payment": {
      "name": "Payment Methods",
      "rawScore": 80,
      "weight": 0.10,
      "contribution": 8,
      "reason": "Prepaid-only enforcement via unverified personal UPI QR",
      "status": "danger"
    },
    "behaviour": {
      "name": "Site Behaviour",
      "rawScore": 50,
      "weight": 0.10,
      "contribution": 5,
      "reason": "Artificial countdown timer inducing false urgency",
      "status": "warning"
    }
  },
  "recommendation": "CRITICAL RISK: Pre-payment warning displayed. Do not enter card numbers, UPI PINs, or credentials."
}
```

---

## 3. Analysis History
- **Endpoint**: `GET /api/v1/history`
- **Query Parameters**:
  - `risk_level`: Filter by `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
  - `domain`: Substring search on domain name
- **Description**: Returns recent storefront evaluations for SOC analysis and auditing.

---

## 4. Clear History
- **Endpoint**: `DELETE /api/v1/history`
- **Description**: Clears the in-memory or persisted telemetry store.
