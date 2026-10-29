/**
 * WebGuard Background Service Worker (Manifest V3)
 * Handles API calls, caching, tab badges, and forensic session state.
 */

import { AnalysisPayload, AnalysisResult } from '../types';
import { analyzePayload } from '../../../frontend/src/engine/riskEngine';

declare const chrome: any;

const API_BASE_URL = 'http://localhost:8000/api/v1'; // FastAPI backend default
const FALLBACK_API_URL = 'http://localhost:3000/api/v1'; // Express local fallback

// Memory cache for recent domain analyses
const analysisCache = new Map<string, { result: AnalysisResult; timestamp: number }>();
const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes

chrome.runtime.onInstalled.addListener(() => {
  console.log('[WebGuard Service Worker] Extension installed and active.');
});

chrome.runtime.onMessage.addListener((message: any, sender: any, sendResponse: any) => {
  if (message.type === 'ANALYZE_PAGE') {
    handlePageAnalysis(message.payload, sender.tab?.id)
      .then(result => sendResponse({ success: true, result }))
      .catch(err => {
        console.error('[WebGuard Service Worker] Analysis failed:', err);
        // Fallback to local rule+ML engine
        const fallbackResult = analyzePayload(message.payload);
        if (sender.tab?.id) updateBadge(sender.tab.id, fallbackResult);
        sendResponse({ success: true, result: fallbackResult, fallback: true });
      });
    return true; // Keep message channel open for async response
  }

  if (message.type === 'GET_CACHED_ANALYSIS') {
    const domain = message.domain;
    const cached = analysisCache.get(domain);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
      sendResponse({ success: true, result: cached.result });
    } else {
      sendResponse({ success: false });
    }
    return true;
  }

  if (message.type === 'OPEN_FULL_ANALYSIS') {
    chrome.tabs.create({
      url: chrome.runtime.getURL(`dist/popup/index.html?view=full&id=${message.analysisId || ''}`)
    });
    sendResponse({ success: true });
    return true;
  }
});

async function handlePageAnalysis(payload: AnalysisPayload, tabId?: number): Promise<AnalysisResult> {
  const cacheKey = payload.domain || payload.url;
  const cached = analysisCache.get(cacheKey);

  if (cached && (Date.now() - cached.timestamp < CACHE_TTL_MS)) {
    if (tabId) updateBadge(tabId, cached.result);
    return cached.result;
  }

  // Attempt backend API call
  let result: AnalysisResult;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);

    let res = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal
    }).catch(async () => {
      // Try local fallback express server
      return await fetch(`${FALLBACK_API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal
      });
    });

    clearTimeout(timeoutId);

    if (res && res.ok) {
      result = await res.json();
    } else {
      // Local engine fallback
      result = analyzePayload(payload);
    }
  } catch (e) {
    // Graceful offline fallback
    result = analyzePayload(payload);
  }

  // Store in cache
  analysisCache.set(cacheKey, { result, timestamp: Date.now() });

  if (tabId) {
    updateBadge(tabId, result);
  }

  return result;
}

function updateBadge(tabId: number, result: AnalysisResult): void {
  try {
    const scoreStr = result.riskScore.toString();
    chrome.action.setBadgeText({ tabId, text: scoreStr });

    let badgeColor = '#10B981'; // Green (LOW)
    if (result.riskScore >= 80) {
      badgeColor = '#EF4444'; // Red (CRITICAL)
    } else if (result.riskScore >= 60) {
      badgeColor = '#F97316'; // Orange (HIGH)
    } else if (result.riskScore >= 30) {
      badgeColor = '#F59E0B'; // Amber (MEDIUM)
    }

    chrome.action.setBadgeBackgroundColor({ tabId, color: badgeColor });
  } catch (err) {
    // Non-fatal extension badge error
  }
}
