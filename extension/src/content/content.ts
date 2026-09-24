/**
 * WebGuard Content Script
 * Orchestrates safe public extraction, behaviour tracking, and warning overlay injection.
 */

import { WebGuardExtractor } from './extractor';
import { BehaviourMonitor } from './behaviour-monitor';
import { renderWarningOverlay } from '../warning/WarningOverlay';
import { AnalysisResult } from '../types';

declare const chrome: any;

let currentAnalysisResult: AnalysisResult | null = null;
let overlayEl: HTMLElement | null = null;
let userDismissedWarning = false;

// Initialize Behavior Monitor
const monitor = new BehaviourMonitor((isCheckout, url) => {
  console.log('[WebGuard] Navigation / DOM trigger detected:', { isCheckout, url });
  runAnalysis(isCheckout);
});

async function runAnalysis(isCheckout: boolean = false): Promise<void> {
  try {
    const payload = WebGuardExtractor.extractPageData();
    payload.isCheckoutPage = isCheckout || payload.isCheckoutPage;

    // Send payload to Background Service Worker for analysis
    chrome.runtime.sendMessage(
      { type: 'ANALYZE_PAGE', payload },
      (response: { success: boolean; result?: AnalysisResult; error?: string }) => {
        if (response && response.success && response.result) {
          currentAnalysisResult = response.result;
          handleRiskOutcome(response.result);
        } else {
          console.warn('[WebGuard] Analysis response error or fallback:', response?.error);
        }
      }
    );
  } catch (err) {
    console.error('[WebGuard Content] Extraction failure:', err);
  }
}

function handleRiskOutcome(result: AnalysisResult): void {
  // If high/critical risk and on checkout/payment page, or overall risk >= 75
  const shouldWarn = result.isPrePaymentTriggered || result.riskScore >= 75;

  if (shouldWarn && !userDismissedWarning) {
    showPrePaymentWarning(result);
  }
}

function showPrePaymentWarning(result: AnalysisResult): void {
  if (overlayEl) {
    overlayEl.remove();
  }

  overlayEl = renderWarningOverlay(
    result,
    () => {
      // Go back to safety
      window.history.back();
    },
    () => {
      // View full forensic details
      chrome.runtime.sendMessage({ type: 'OPEN_FULL_ANALYSIS', analysisId: result.id });
    },
    () => {
      // Continue at own risk
      userDismissedWarning = true;
      if (overlayEl) {
        overlayEl.remove();
        overlayEl = null;
      }
    }
  );

  document.body.appendChild(overlayEl);
}

// Initial analysis on load
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  setTimeout(() => runAnalysis(WebGuardExtractor.isCheckoutOrPaymentUrl()), 600);
} else {
  window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => runAnalysis(WebGuardExtractor.isCheckoutOrPaymentUrl()), 600);
  });
}
