# WebGuard Security Intelligence Platform: Architecture Audit & Implementation Plan

## 1. Executive Summary & Audit Baseline

WebGuard is being elevated from an e-commerce pre-payment fraud assessment tool into a **dual-engine Website Trust & Security Assessment Platform** for defensive cybersecurity, ethical hacking audits, and e-commerce consumer protection.

### Existing Architecture vs Target State
| Component | Existing Baseline | Target State (Security Intelligence Platform) |
| :--- | :--- | :--- |
| **Backend Core** | FastAPI + SQLAlchemy (SQLite/Postgres) | Consolidated Canonical FastAPI Engine with unified Trust & Security modules |
| **Trust Engine** | 7-factor e-commerce fraud model (weights sum to 1.00) | **Assessment A**: Website Trust Risk (Preserved & expanded, 0-100) |
| **Security Engine** | Limited TLS certificate check in domain adapter | **Assessment B**: Technical Security Risk (0-100 + Findings Breakdown) |
| **Passive OSINT** | Domain age via RDAP/DNS | Full DNS (A, AAAA, MX, NS, TXT, CAA), RDAP registrant, CT certificate telemetry |
| **Web Security** | HTTPS check | Full Security Headers (CSP, HSTS, XCTO, Referrer, Permissions), Cookie flags, redirect chains |
| **Tech Fingerprint**| Not implemented | Header/meta/script/cookie fingerprinting for servers, CMS, and frameworks with confidence |
| **Vulnerability Intel**| Not implemented | Product/version to CVE mapping (NVD API + authenticated catalog), distinguishing potential vs verified |
| **OWASP Assessment** | Not implemented | Safe, passive checks mapped to OWASP Top 10 2021 (A01-A09) with security.txt audit |
| **Attack Surface** | Not implemented | Authorized assessment scope management & asset inventory tracking |
| **Developer Security**| Not implemented | Static code analyzer & dependency auditor (Bandit/Semgrep/npm-audit patterns) |
| **Database Models** | `analyses`, `factor_results`, `detected_signals`, `domain_profiles` | Add `security_findings`, `cve_matches`, `assessment_scopes`, `discovered_assets`, `security_assessments` |
| **UI Dashboard** | GSAP 3 Trust Dashboard | Dual Trust & Security Dashboard with findings table, CVE radar, asset inventory & developer security |

---

## 2. Dual Risk Engine Architecture

```
+---------------------------------------------------------------------------------------------------+
|                                       WEGUARD DUAL ENGINE                                         |
+-------------------------------------------------+-------------------------------------------------+
|          A. WEBSITE TRUST ASSESSMENT            |         B. TECHNICAL SECURITY ASSESSMENT        |
+-------------------------------------------------+-------------------------------------------------+
| Focus: Consumer & Merchant Fraud Prevention     | Focus: Web Application & Infrastructure Defense |
| Model: 7-Factor Weighted Composite (0-100)      | Model: Vulnerability Severity Index (0-100)     |
| - Domain Credibility (20%)                      | - Cryptographic & TLS Configuration             |
| - Price Anomaly [Isolation Forest ML] (20%)     | - Security Headers & Cookie Policies            |
| - Review Patterns [TF-IDF Cosine NLP] (15%)     | - Technology Stack Fingerprints                 |
| - Website Identity & Registration (15%)         | - CVE Vulnerability Correlation                 |
| - Refund & Cancellation Policy (10%)            | - OWASP Top 10 Passive Misconfigurations        |
| - Payment Methods & Irreversible Rails (10%)    | - Discovered Attack Surface & Subdomains        |
| - Deceptive Site Behaviour & Countdown (10%)    | - security.txt & Vulnerability Disclosure       |
+-------------------------------------------------+-------------------------------------------------+
```

---

## 3. Implementation Plan: Phases 1 to 9

1. **Phase 1: Repository Audit & Baseline Verification** (Completed: 28/28 tests passing).
2. **Phase 2: Database Schema & Unified API Contracts**
   - Define SQLAlchemy models for `SecurityFinding`, `CVEMatch`, `AssessmentScope`, `DiscoveredAsset`, `SecurityAssessment`.
   - Define Pydantic v2 schemas for Technical Security requests/responses.
3. **Phase 3: Module A - Passive Reconnaissance & OSINT Adapter**
   - `backend/app/adapters/osint_adapter.py`: DNS query engine (A, AAAA, MX, NS, TXT, CAA via `dnspython`), RDAP client, CT log inspection.
4. **Phase 4: Module B - HTTPS, TLS & Security Headers Analyzer**
   - `backend/app/analyzers/security_headers.py`: Full evaluation of CSP, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, X-Frame-Options, cookie security flags (`Secure`, `HttpOnly`, `SameSite`), and TLS certificate validation.
5. **Phase 5: Modules C & D - Technology Fingerprinting & CVE Correlation**
   - `backend/app/analyzers/tech_fingerprint.py`: Detect servers (Nginx/Apache), CMS (WordPress/Shopify), frameworks (React/Vue/Django/Laravel).
   - `backend/app/adapters/cve_adapter.py`: Match software/versions to CVE identifiers, CVSS scores, descriptions, and clearly flag "potentially affected version" vs verified vulnerability.
6. **Phase 6: Modules E & F - OWASP Assessment & Scope Authorization**
   - `backend/app/analyzers/owasp_passive.py`: Safe OWASP Top 10 2021 misconfiguration checks.
   - `backend/app/utils/scope_validator.py`: Strict backend scope enforcement rejecting unauthorized targets.
   - `backend/app/api/assets.py` & `backend/app/api/scopes.py`: Asset inventory management.
7. **Phase 7: Module G - Developer Security Tooling**
   - `backend/app/utils/dev_security.py`: Built-in static analysis scanner checking code security rules and auditing project dependencies.
   - `GET /api/v1/developer-security` endpoint.
8. **Phase 8: Extension & Dashboard Integration**
   - Extend `extension/src/content/extractor.ts` and `extension/src/popup/ExtensionPopupView.tsx` to display Trust score and Technical checks.
   - Upgrade `frontend/src/app.ts` with tabs for Trust Risk, Technical Findings, Tech Stack & CVEs, Attack Surface, and DevSec.
9. **Phase 9: Comprehensive Automated Test Suite**
   - Pytest suites for OSINT, Security Headers, Technology Fingerprinting, CVE matching, Scope enforcement, Developer security.
