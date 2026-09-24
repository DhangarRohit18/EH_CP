/**
 * WebGuard Pre-Payment Security Warning Overlay
 * Injected into checkout / payment pages when fraud score is high or critical.
 * Styled in pure white theme with single blue color.
 */

import { AnalysisResult } from '../types';

export function renderWarningOverlay(
  result: AnalysisResult,
  onGoBack: () => void,
  onViewDetails: () => void,
  onDismiss: () => void
): HTMLElement {
  const container = document.createElement('div');
  container.id = 'webguard-security-overlay-root';
  container.style.position = 'fixed';
  container.style.inset = '0';
  container.style.zIndex = '2147483647';
  container.style.backgroundColor = 'rgba(15, 23, 42, 0.6)';
  container.style.backdropFilter = 'blur(4px)';
  container.style.display = 'flex';
  container.style.alignItems = 'center';
  container.style.justifyContent = 'center';
  container.style.fontFamily = 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  container.style.color = '#0f172a';
  container.style.padding = '16px';

  // Modal card - Pure White
  const card = document.createElement('div');
  card.style.maxWidth = '520px';
  card.style.width = '100%';
  card.style.backgroundColor = '#ffffff';
  card.style.border = '1px solid #d1d5db';
  card.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.25)';
  card.style.borderRadius = '12px';
  card.style.padding = '24px';
  card.style.boxSizing = 'border-box';

  // Header badge
  const headerBadge = document.createElement('div');
  headerBadge.style.display = 'flex';
  headerBadge.style.alignItems = 'center';
  headerBadge.style.gap = '8px';
  headerBadge.style.color = '#1d4ed8';
  headerBadge.style.fontWeight = '700';
  headerBadge.style.fontSize = '12px';
  headerBadge.style.letterSpacing = '1px';
  headerBadge.style.textTransform = 'uppercase';
  headerBadge.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
    <span>WEBGUARD SECURITY INTERCEPTION</span>
  `;
  card.appendChild(headerBadge);

  // Subtitle
  const subTitle = document.createElement('p');
  subTitle.style.color = '#64748b';
  subTitle.style.fontSize = '12px';
  subTitle.style.margin = '4px 0 16px 0';
  subTitle.textContent = 'High-risk indicators detected before funds transfer or card submission.';
  card.appendChild(subTitle);

  // Score Box
  const scoreBox = document.createElement('div');
  scoreBox.style.backgroundColor = '#f8fafc';
  scoreBox.style.border = '1px solid #e2e8f0';
  scoreBox.style.borderRadius = '8px';
  scoreBox.style.padding = '14px';
  scoreBox.style.display = 'flex';
  scoreBox.style.justifyContent = 'space-between';
  scoreBox.style.alignItems = 'center';
  scoreBox.style.marginBottom = '16px';
  scoreBox.innerHTML = `
    <div>
      <div style="font-size: 10px; font-family: monospace; color: #64748b; text-transform: uppercase;">Fraud Risk Score</div>
      <div style="display: flex; align-items: baseline; gap: 4px; margin-top: 2px;">
        <span style="font-size: 32px; font-weight: 800; font-family: monospace; color: #0f172a;">${result.riskScore}</span>
        <span style="font-size: 13px; color: #64748b; font-family: monospace;">/ 100</span>
      </div>
    </div>
    <div style="text-align: right;">
      <span style="display: inline-block; background-color: #2563eb; color: #ffffff; font-weight: 700; font-size: 11px; padding: 4px 10px; border-radius: 4px; font-family: monospace;">
        ${result.riskLevel} FRAUD RISK
      </span>
      <div style="font-size: 10px; color: #64748b; margin-top: 4px; font-family: monospace;">Pre-Payment Intercept</div>
    </div>
  `;
  card.appendChild(scoreBox);

  // Indicators list
  const listTitle = document.createElement('div');
  listTitle.style.fontSize = '11px';
  listTitle.style.fontWeight = '700';
  listTitle.style.color = '#334155';
  listTitle.style.textTransform = 'uppercase';
  listTitle.style.letterSpacing = '0.5px';
  listTitle.style.marginBottom = '8px';
  listTitle.textContent = 'Main Detected Indicators:';
  card.appendChild(listTitle);

  const list = document.createElement('div');
  list.style.display = 'flex';
  list.style.flexDirection = 'column';
  list.style.gap = '6px';
  list.style.marginBottom = '20px';

  result.explanations.slice(0, 4).forEach((exp) => {
    const item = document.createElement('div');
    item.style.backgroundColor = '#f8fafc';
    item.style.border = '1px solid #e2e8f0';
    item.style.padding = '8px 10px';
    item.style.borderRadius = '6px';
    item.style.display = 'flex';
    item.style.justifyContent = 'space-between';
    item.style.alignItems = 'center';
    item.style.fontSize = '11px';
    item.innerHTML = `
      <div style="color: #1e293b; max-width: 380px;">
        <strong>${exp.factor}:</strong> ${exp.explanation}
      </div>
      <span style="font-family: monospace; font-weight: 700; color: #2563eb; margin-left: 8px; white-space: nowrap;">
        +${exp.points} pts
      </span>
    `;
    list.appendChild(item);
  });
  card.appendChild(list);

  // Actions
  const btnContainer = document.createElement('div');
  btnContainer.style.display = 'flex';
  btnContainer.style.flexDirection = 'column';
  btnContainer.style.gap = '8px';

  const backBtn = document.createElement('button');
  backBtn.textContent = '← GO BACK TO SAFETY (Recommended)';
  backBtn.style.padding = '10px 16px';
  backBtn.style.backgroundColor = '#2563eb';
  backBtn.style.color = '#ffffff';
  backBtn.style.fontWeight = '700';
  backBtn.style.fontSize = '12px';
  backBtn.style.border = 'none';
  backBtn.style.borderRadius = '6px';
  backBtn.style.cursor = 'pointer';
  backBtn.onclick = onGoBack;
  btnContainer.appendChild(backBtn);

  const detailBtn = document.createElement('button');
  detailBtn.textContent = 'View Detailed Forensic Dossier';
  detailBtn.style.padding = '8px 16px';
  detailBtn.style.backgroundColor = '#ffffff';
  detailBtn.style.color = '#1e293b';
  detailBtn.style.fontWeight = '600';
  detailBtn.style.fontSize = '12px';
  detailBtn.style.border = '1px solid #cbd5e1';
  detailBtn.style.borderRadius = '6px';
  detailBtn.style.cursor = 'pointer';
  detailBtn.onclick = onViewDetails;
  btnContainer.appendChild(detailBtn);

  const dismissBtn = document.createElement('button');
  dismissBtn.textContent = 'Continue at own risk (Dismiss)';
  dismissBtn.style.padding = '6px';
  dismissBtn.style.backgroundColor = 'transparent';
  dismissBtn.style.color = '#94a3b8';
  dismissBtn.style.fontSize = '11px';
  dismissBtn.style.border = 'none';
  dismissBtn.style.textDecoration = 'underline';
  dismissBtn.style.cursor = 'pointer';
  dismissBtn.onclick = onDismiss;
  btnContainer.appendChild(dismissBtn);

  card.appendChild(btnContainer);
  container.appendChild(card);
  return container;
}
