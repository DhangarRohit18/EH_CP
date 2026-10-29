# WebGuard Manifest V3 Browser Extension

WebGuard's browser extension delivers real-time consumer pre-payment fraud protection directly inside Google Chrome, Microsoft Edge, and Brave.

---

## 🚀 How to Install and Test

1. Open your browser and navigate to the extensions management page:
   - **Chrome**: `chrome://extensions/`
   - **Edge**: `edge://extensions/`
   - **Brave**: `brave://extensions/`
2. Enable **Developer mode** (toggle in the top-right corner).
3. Click the **Load unpacked** button.
4. Select the `extension/` directory from this repository.
5. The **WebGuard** extension icon will now appear in your browser toolbar!

---

## 🛡️ Architecture & Components

- `manifest.json`: Manifest V3 configuration with strict least-privilege permissions.
- `src/content/content.ts`: Content script injected into shopping pages to detect checkout actions.
- `src/content/extractor.ts`: High-precision DOM parser extracting store domain, listed product price, contact webmail, and refund policies.
- `src/warning/WarningOverlay.tsx`: Pre-payment blocking modal rendered whenever composite risk score is $\ge 60$.
- `src/background/service-worker.ts`: Background worker communicating with WebGuard API backend (`/api/v1/analyze`) and caching results.
- `src/popup/App.tsx`: Toolbar popup showing risk score and factor breakdown for the current tab.
