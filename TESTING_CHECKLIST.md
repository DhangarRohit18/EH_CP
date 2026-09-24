# WebGuard: Evaluation & Testing Checklist
Use this checklist during academic evaluations, cybersecurity demonstrations, or test automation:
| Step | Test Objective | Target / Action | Expected Result | Pass/Fail |
| :---: | :--- | :--- | :--- | :---: |
| **01** | **Backend Health Check** | `GET /api/v1/health` | HTTP 200 OK, `status: "online"`, ML models loaded, weights sum to 1.00. | [ ] |
| **02** | **Official Demo Scenario** | Load `flashdeal-electronics.local` in Simulator | Risk score: **86 / 100**, Level: `HIGH`, Factors decompose to +24, +20, +15, +12, +10, +5. | [ ] |
| **03** | **Pre-Payment Warning Modal** | Click *"BUY NOW - PROCEED TO CHECKOUT"* in Simulator | Fullscreen security warning appears with score 86, main indicators, and *"GO BACK"* action. | [ ] |
| **04** | **Legitimate Store Verification** | Select Scenario 1 (`croma-electronics.com`) | Score: **12 / 100**, Level: `LOW`, No warning triggered on checkout. | [ ] |
| **05** | **Fake Luxury Impersonator** | Select Scenario 3 (`luxurystore-vip-deals.shop`) | Score: **94 / 100**, Level: `CRITICAL FRAUD RISK`, Immediate high-severity flag. | [ ] |
| **06** | **Prepaid Trap Store** | Select Scenario 4 (`quickcart-direct-sales.top`) | Score: **76 / 100**, Level: `HIGH`, Payment factor triggers maximum risk. | [ ] |
| **07** | **Brand Typosquatting Mimic** | Select Scenario 5 (`amaz0n-prime-security-checkout.co`) | Score: **84 / 100**, Domain factor triggers typosquatting alert. | [ ] |
| **08** | **Extension Manifest V3 Inspection** | Inspect `extension/manifest.json` | Manifest version 3, non-persistent service worker, declarative content scripts. | [ ] |
| **09** | **Safe Extraction Privacy Audit** | Review `extension/src/content/extractor.ts` | Verification that `input[type="password"]` and card numbers are excluded. | [ ] |
| **10** | **Custom API Sandbox Execution** | Execute custom payload in API Sandbox | Real-time response JSON rendered with full mathematical breakdown. | [ ] |
| **11** | **Audit History Persistence** | Review *"Audit History"* view | Scans persisted with search, filtering by risk level, and JSON export. | [ ] |
| **12** | **SOC Analytics Telemetry** | Review *"SOC Analytics"* view | Risk proportion bar, average factor contributions, and feed updated. | [ ] |