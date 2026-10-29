/**
 * WebGuard - Minimal & Fluent Vanilla JS + GSAP Application
 * Powered by GreenSock Animation Platform (GSAP 3)
 */

import { gsap } from 'gsap';
import { analyzePayload } from './engine/riskEngine';
import { DEMO_TEST_CASES } from './engine/testCases';
import { AnalysisResult, AnalysisPayload } from './types';

// ============================================================================
// State
// ============================================================================
let currentScore = 0;
let currentResult: AnalysisResult = analyzePayload(DEMO_TEST_CASES[0].data);
let historyList: AnalysisResult[] = DEMO_TEST_CASES.map(tc => analyzePayload(tc.data));
let activeFilter = 'ALL';

// Factor Metadata for UI Icons & Colors
const FACTOR_META: Record<string, { icon: string; color: string; label: string; maxWeight: number }> = {
  domain: { icon: '🌐', color: '#38BDF8', label: 'Domain Credibility', maxWeight: 20 },
  price: { icon: '🏷️', color: '#F43F5E', label: 'Price Anomaly (ML)', maxWeight: 20 },
  reviews: { icon: '💬', color: '#A855F7', label: 'Review Patterns (NLP)', maxWeight: 15 },
  identity: { icon: '🏢', color: '#FB923C', label: 'Website Identity', maxWeight: 15 },
  policy: { icon: '📄', color: '#FBBF24', label: 'Refund Policy', maxWeight: 10 },
  payment: { icon: '💳', color: '#EC4899', label: 'Payment Methods', maxWeight: 10 },
  behaviour: { icon: '⚡', color: '#10B981', label: 'Site Behaviour', maxWeight: 10 },
};

// ============================================================================
// DOM References
// ============================================================================
const scoreCounterEl = document.getElementById('score-counter') as HTMLElement;
const gaugeProgressEl = document.getElementById('gauge-progress') as unknown as SVGCircleElement;
const threatBadgeEl = document.getElementById('threat-level-badge') as HTMLElement;
const domainValueEl = document.getElementById('domain-value') as HTMLElement;
const productValueEl = document.getElementById('product-value') as HTMLElement;
const priceValueEl = document.getElementById('price-value') as HTMLElement;
const ageValueEl = document.getElementById('age-value') as HTMLElement;
const paymentSecurityValueEl = document.getElementById('payment-security-value') as HTMLElement;
const factorsListEl = document.getElementById('factors-list') as HTMLElement;
const waterfallBarEl = document.getElementById('waterfall-bar') as HTMLElement;
const waterfallLegendEl = document.getElementById('waterfall-legend') as HTMLElement;
const waterfallSummaryTextEl = document.getElementById('waterfall-summary-text') as HTMLElement;
const presetsContainerEl = document.getElementById('presets-container') as HTMLElement;
const urlSearchFormEl = document.getElementById('url-search-form') as HTMLFormElement;
const storeUrlInputEl = document.getElementById('store-url-input') as HTMLInputElement;
const btnSimulateCheckoutEl = document.getElementById('btn-simulate-checkout') as HTMLButtonElement;

// Modal Elements
const modalBackdropEl = document.getElementById('interceptor-modal-backdrop') as HTMLElement;
const modalDialogEl = document.getElementById('interceptor-dialog') as HTMLElement;
const modalDomainNameEl = document.getElementById('modal-domain-name') as HTMLElement;
const modalSignalsListEl = document.getElementById('modal-signals-list') as HTMLElement;
const btnModalAbortEl = document.getElementById('btn-modal-abort') as HTMLButtonElement;
const btnModalDismissEl = document.getElementById('btn-modal-dismiss') as HTMLButtonElement;

// ============================================================================
// Initial Page Setup & GSAP Entrance Animations
// ============================================================================
function initEntranceAnimations() {
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

  tl.from('#site-header', { y: -30, opacity: 0, duration: 0.6 })
    .from('#hero-controls', { y: 20, opacity: 0, duration: 0.5 }, '-=0.3')
    .from('#hero-meter-card', { x: -30, opacity: 0, duration: 0.6 }, '-=0.2')
    .from('#factors-panel', { x: 30, opacity: 0, duration: 0.6 }, '-=0.5')
    .from('#waterfall-panel', { y: 25, opacity: 0, duration: 0.5 }, '-=0.3');
}

// ============================================================================
// Render Calibrated Preset Pills
// ============================================================================
function renderPresets() {
  if (!presetsContainerEl) return;
  presetsContainerEl.innerHTML = '';

  DEMO_TEST_CASES.forEach((preset, index) => {
    const pill = document.createElement('button');
    pill.type = 'button';
    pill.className = `preset-pill ${index === 0 ? 'active' : ''}`;
    pill.dataset.index = index.toString();

    let dotClass = 'dot-critical';
    if (preset.name.includes('Watches')) dotClass = 'dot-high';
    if (preset.name.includes('Furnishings')) dotClass = 'dot-caution';
    if (preset.name.includes('Gadget')) dotClass = 'dot-safe';

    pill.innerHTML = `
      <span class="preset-dot ${dotClass}"></span>
      <span>${preset.data.domain}</span>
    `;

    pill.addEventListener('click', () => {
      document.querySelectorAll('.preset-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');

      storeUrlInputEl.value = preset.data.url;
      updateAnalysis(analyzePayload(preset.data));
    });

    presetsContainerEl.appendChild(pill);
  });
}

// ============================================================================
// Update Analysis Data & Run GSAP Animations
// ============================================================================
function updateAnalysis(result: AnalysisResult) {
  currentResult = result;
  const newScore = result.riskScore;
  const targetDomain = result.domain;

  // 1. Animate Numerical Score Counter
  const counterObj = { val: currentScore };
  gsap.to(counterObj, {
    val: newScore,
    duration: 1.1,
    ease: 'power2.out',
    onUpdate: () => {
      if (scoreCounterEl) {
        scoreCounterEl.textContent = Math.round(counterObj.val).toString();
      }
    },
  });
  currentScore = newScore;

  // 2. Animate Circular SVG Gauge Stroke
  // Radius = 68, circumference = 2 * PI * 68 = 427.26
  const circumference = 427.26;
  const targetOffset = circumference - (newScore / 100) * circumference;

  let gaugeColor = '#F43F5E';
  let badgeClass = 'badge-critical';
  let badgeText = 'CRITICAL FRAUD RISK';

  if (newScore >= 80) {
    gaugeColor = '#F43F5E';
    badgeClass = 'badge-critical';
    badgeText = 'CRITICAL FRAUD RISK';
  } else if (newScore >= 60) {
    gaugeColor = '#FB923C';
    badgeClass = 'badge-high';
    badgeText = 'HIGH FRAUD RISK';
  } else if (newScore >= 30) {
    gaugeColor = '#FBBF24';
    badgeClass = 'badge-caution';
    badgeText = 'MODERATE RISK';
  } else {
    gaugeColor = '#10B981';
    badgeClass = 'badge-safe';
    badgeText = 'VERIFIED SAFE';
  }

  if (gaugeProgressEl) {
    gaugeProgressEl.style.stroke = gaugeColor;
    gsap.to(gaugeProgressEl, {
      strokeDashoffset: targetOffset,
      duration: 1.2,
      ease: 'power2.out',
    });
  }

  // 3. Update Threat Badge
  if (threatBadgeEl) {
    threatBadgeEl.className = `threat-badge ${badgeClass}`;
    threatBadgeEl.textContent = badgeText;
    gsap.fromTo(threatBadgeEl, { scale: 0.9 }, { scale: 1, duration: 0.3, ease: 'back.out(2)' });
  }

  // 4. Update Storefront Details
  if (domainValueEl) domainValueEl.textContent = targetDomain;
  if (productValueEl) productValueEl.textContent = result.productName || 'Storefront Root Assessment';
  if (priceValueEl) {
    priceValueEl.textContent = `${result.currency || '₹'}${result.price ? result.price.toLocaleString() : 'N/A'}`;
  }
  if (ageValueEl) {
    const ageDays = result.factors.domain.contribution >= 15 ? '8 Days Old (<14d Critical)' : '680 Days Old (Established)';
    ageValueEl.textContent = ageDays;
  }
  if (paymentSecurityValueEl) {
    const isPrepaid = result.factors.payment.contribution >= 6;
    paymentSecurityValueEl.textContent = isPrepaid ? 'Prepaid UPI Only (High Risk)' : 'PCI-DSS Verified Gateways';
    paymentSecurityValueEl.style.color = isPrepaid ? '#F43F5E' : '#10B981';
  }

  // 5. Update Simulate Checkout Button Style
  if (btnSimulateCheckoutEl) {
    if (newScore < 60) {
      btnSimulateCheckoutEl.classList.add('safe-style');
      btnSimulateCheckoutEl.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span>Simulate Checkout (Verified Safe)</span>
      `;
    } else {
      btnSimulateCheckoutEl.classList.remove('safe-style');
      btnSimulateCheckoutEl.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="9" cy="21" r="1"></circle>
          <circle cx="20" cy="21" r="1"></circle>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
        </svg>
        <span>Simulate Checkout & Intercept</span>
      `;
    }
  }

  // 6. Render Seven Factor Cards with Accordion
  renderFactorCards(result);

  // 7. Render Waterfall Bar
  renderWaterfallBar(result);

  // 8. Prepend to History
  historyList.unshift(result);
  if (historyList.length > 25) historyList.pop();
  renderThreatStream();
}

// ============================================================================
// Render Seven Factor Cards with GSAP Stagger
// ============================================================================
function renderFactorCards(result: AnalysisResult) {
  if (!factorsListEl) return;
  factorsListEl.innerHTML = '';

  const entries = Object.entries(result.factors);

  entries.forEach(([key, factor]) => {
    const meta = FACTOR_META[key] || { icon: '🔍', color: '#38BDF8', label: factor.name, maxWeight: 10 };
    
    let ptsClass = 'pts-safe';
    if (factor.status === 'danger') ptsClass = 'pts-danger';
    else if (factor.status === 'warning') ptsClass = 'pts-warning';

    const card = document.createElement('div');
    card.className = 'factor-card';
    card.id = `factor-card-${key}`;

    card.innerHTML = `
      <div class="factor-header">
        <div class="factor-left-group">
          <div class="factor-icon-badge" style="background: rgba(255,255,255,0.05); color: ${meta.color};">
            ${meta.icon}
          </div>
          <div>
            <span class="factor-name">${factor.name}</span>
            <span class="factor-weight-pill">${meta.maxWeight}% Weight</span>
          </div>
        </div>
        <div class="factor-right-group">
          <span class="factor-points-pill ${ptsClass}">
            +${factor.contribution} pts
          </span>
          <svg class="factor-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </div>
      </div>
      <div class="factor-body">
        <p class="factor-reason-text">${factor.reason}</p>
        ${factor.subSignals ? `<div class="factor-subsignals"><span class="subsignal-tag">${factor.subSignals}</span></div>` : ''}
      </div>
    `;

    // Interactive Accordion Toggle
    card.addEventListener('click', () => {
      const isExpanded = card.classList.contains('expanded');
      // Collapse others for clean minimalism
      document.querySelectorAll('.factor-card').forEach(c => c.classList.remove('expanded'));
      if (!isExpanded) {
        card.classList.add('expanded');
      }
    });

    factorsListEl.appendChild(card);
  });

  // Stagger reveal of cards
  gsap.from('.factor-card', {
    opacity: 0,
    y: 12,
    stagger: 0.04,
    duration: 0.35,
    ease: 'power2.out',
  });
}

// ============================================================================
// Render Waterfall Bar & Legend
// ============================================================================
function renderWaterfallBar(result: AnalysisResult) {
  if (!waterfallBarEl || !waterfallLegendEl) return;
  waterfallBarEl.innerHTML = '';
  waterfallLegendEl.innerHTML = '';

  if (waterfallSummaryTextEl) {
    waterfallSummaryTextEl.textContent = `Total Additive Score: ${result.riskScore} / 100 points`;
  }

  const entries = Object.entries(result.factors);
  const totalScore = Math.max(result.riskScore, 1);

  entries.forEach(([key, factor]) => {
    if (factor.contribution <= 0) return;
    const meta = FACTOR_META[key] || { color: '#06B6D4', label: factor.name };
    const pct = (factor.contribution / totalScore) * 100;

    const segment = document.createElement('div');
    segment.className = 'waterfall-segment';
    segment.style.width = `${pct}%`;
    segment.style.backgroundColor = meta.color;
    segment.title = `${factor.name}: +${factor.contribution} pts`;

    waterfallBarEl.appendChild(segment);

    // Legend item
    const legItem = document.createElement('div');
    legItem.className = 'legend-item';
    legItem.innerHTML = `
      <span class="legend-color-box" style="background-color: ${meta.color};"></span>
      <span>${factor.name} (+${factor.contribution})</span>
    `;
    waterfallLegendEl.appendChild(legItem);
  });

  // GSAP animation on segments
  gsap.from('.waterfall-segment', {
    scaleX: 0,
    transformOrigin: 'left',
    stagger: 0.04,
    duration: 0.6,
    ease: 'power2.out',
  });
}

// ============================================================================
// Pre-Payment Security Interceptor Modal (GSAP Timelines)
// ============================================================================
function openSecurityWarningModal() {
  if (currentResult.riskScore < 60) {
    // Non-intrusive safe notification
    showSafeToast();
    return;
  }

  if (modalDomainNameEl) modalDomainNameEl.textContent = currentResult.domain;
  if (modalSignalsListEl) {
    modalSignalsListEl.innerHTML = '';
    const topFactors = currentResult.explanations.slice(0, 4);

    topFactors.forEach(exp => {
      const row = document.createElement('div');
      row.className = 'modal-factor-row';
      row.innerHTML = `
        <span>• ${exp.factor}: <strong style="color:#94A3B8; font-weight:normal;">${exp.explanation}</strong></span>
        <span class="modal-factor-pts">+${exp.points} pts</span>
      `;
      modalSignalsListEl.appendChild(row);
    });
  }

  // Show Backdrop
  modalBackdropEl.classList.add('open');

  // GSAP Entrance Timeline
  const tl = gsap.timeline();
  tl.fromTo(modalBackdropEl, { opacity: 0 }, { opacity: 1, duration: 0.25, ease: 'power2.out' })
    .fromTo(modalDialogEl, { scale: 0.8, opacity: 0, y: 25 }, { scale: 1, opacity: 1, y: 0, duration: 0.45, ease: 'back.out(1.6)' }, '-=0.15')
    .from('.modal-factor-row', { opacity: 0, x: -15, stagger: 0.06, duration: 0.35, ease: 'power2.out' }, '-=0.2');
}

function closeSecurityWarningModal() {
  const tl = gsap.timeline({
    onComplete: () => {
      modalBackdropEl.classList.remove('open');
    },
  });

  tl.to(modalDialogEl, { scale: 0.85, opacity: 0, y: 20, duration: 0.25, ease: 'power2.in' })
    .to(modalBackdropEl, { opacity: 0, duration: 0.2 }, '-=0.1');
}

function showSafeToast() {
  const toast = document.createElement('div');
  toast.style.position = 'fixed';
  toast.style.bottom = '30px';
  toast.style.right = '30px';
  toast.style.backgroundColor = '#10B981';
  toast.style.color = '#fff';
  toast.style.fontFamily = 'var(--font-sans)';
  toast.style.fontSize = '0.85rem';
  toast.style.fontWeight = '600';
  toast.style.padding = '12px 24px';
  toast.style.borderRadius = 'var(--radius-md)';
  toast.style.boxShadow = '0 10px 25px rgba(16, 185, 129, 0.4)';
  toast.style.zIndex = '9999';
  toast.textContent = '✓ Storefront evaluated as Low Risk. Standard payment protection active.';

  document.body.appendChild(toast);
  gsap.fromTo(toast, { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: 'back.out(2)' });

  setTimeout(() => {
    gsap.to(toast, { y: 20, opacity: 0, duration: 0.3, onComplete: () => toast.remove() });
  }, 3500);
}

// ============================================================================
// Factor Matrix View Population
// ============================================================================
function renderMatrixCards() {
  const container = document.getElementById('matrix-cards-container');
  if (!container) return;
  container.innerHTML = '';

  const matrixData = [
    { name: 'Domain Credibility', weight: '20%', desc: 'Detects domains registered <14 days ago, high-abuse registrar TLDs (.xyz, .top, .live), brand typosquatting, and missing TLS encryption.', tech: 'WHOIS Telemetry + Levenshtein Distance' },
    { name: 'Price Anomaly Engine', weight: '20%', desc: 'Flags aggressive unrealistic discounts (>70% off authenticated MSRP benchmarks) leveraging machine learning anomaly clustering.', tech: 'Isolation Forest ML + Scikit-Learn' },
    { name: 'Review Patterns & NLP', weight: '15%', desc: 'Identifies synthetic reviews using syntactic n-gram duplicates, 100% 5-star artificial ratings, and narrow publication bursts.', tech: 'NLP Syntactic N-Grams + Cosine Distance' },
    { name: 'Merchant Identity Verification', weight: '15%', desc: 'Validates presence of official corporate support emails (flagging free Gmail/Proton addresses), corporate phone lines, and physical addresses.', tech: 'Corporate DNS MX Records + MCA Verification' },
    { name: 'Refund & Returns Policy', weight: '10%', desc: 'Parses store policies to detect missing return documents, unreasonable 24-hour return windows, and aggressive 35%+ restocking penalty traps.', tech: 'DOM Semantic Text Parsing + NLP Classifier' },
    { name: 'Payment Method Safety', weight: '10%', desc: 'Intercepts prepaid-only enforcement, unverified personal UPI VPAs / QR codes, wire traps, and absence of buyer-protected payment gateways.', tech: 'Payment Gateway Script & DOM Analyzer' },
    { name: 'Site Behaviour & Urgency', weight: '10%', desc: 'Identifies artificial countdown ticking urgency timers, hidden checkout redirects, and deceptive DOM elements designed to force impulsive checkout.', tech: 'DOM Mutation Observer + Event Interceptor' },
  ];

  matrixData.forEach(item => {
    const card = document.createElement('div');
    card.className = 'matrix-card glass-panel';
    card.innerHTML = `
      <div class="matrix-card-header">
        <h3 class="panel-title" style="font-size: 1rem;">${item.name}</h3>
        <span class="matrix-weight-badge">${item.weight}</span>
      </div>
      <p class="matrix-desc">${item.desc}</p>
      <span class="matrix-tech-badge">${item.tech}</span>
    `;
    container.appendChild(card);
  });
}

// ============================================================================
// Real-Time Threat Stream View
// ============================================================================
function renderThreatStream() {
  const streamContainer = document.getElementById('threat-stream-list');
  if (!streamContainer) return;
  streamContainer.innerHTML = '';

  const filtered = historyList.filter(item => {
    if (activeFilter === 'ALL') return true;
    if (activeFilter === 'CRITICAL') return item.riskLevel === 'CRITICAL';
    if (activeFilter === 'HIGH') return item.riskLevel === 'HIGH';
    if (activeFilter === 'SAFE') return item.riskLevel === 'LOW';
    return true;
  });

  filtered.forEach(item => {
    const row = document.createElement('div');
    row.className = 'stream-item';

    let color = '#F43F5E';
    if (item.riskLevel === 'HIGH') color = '#FB923C';
    if (item.riskLevel === 'MEDIUM') color = '#FBBF24';
    if (item.riskLevel === 'LOW') color = '#10B981';

    row.innerHTML = `
      <div style="display:flex; align-items:center; gap:12px;">
        <span style="width:8px; height:8px; border-radius:50%; background-color:${color}; box-shadow:0 0 6px ${color};"></span>
        <div>
          <div style="font-family:var(--font-mono); font-size:0.84rem; font-weight:600; color:#fff;">${item.domain}</div>
          <div style="font-size:0.75rem; color:var(--text-dim);">${item.productName || 'Catalog Assessment'} • ${item.recommendation.slice(0, 55)}...</div>
        </div>
      </div>
      <div style="text-align:right;">
        <div style="font-family:var(--font-mono); font-size:1rem; font-weight:800; color:${color};">${item.riskScore} / 100</div>
        <div style="font-size:0.68rem; font-family:var(--font-mono); color:var(--text-dim); text-transform:uppercase;">${item.riskLevel}</div>
      </div>
    `;

    streamContainer.appendChild(row);
  });
}

// ============================================================================
// Tab Navigation Handling
// ============================================================================
function setupNavigationTabs() {
  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      if (!targetId) return;

      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const allViews = document.querySelectorAll('.tab-view');
      allViews.forEach(view => {
        (view as HTMLElement).style.display = 'none';
      });

      const activeView = document.getElementById(targetId);
      if (activeView) {
        activeView.style.display = 'block';
        gsap.fromTo(activeView, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' });
      }

      if (targetId === 'tab-matrix') renderMatrixCards();
      if (targetId === 'tab-feed') renderThreatStream();
    });
  });

  // Filter Buttons in Threat Feed
  const filterBtns = document.querySelectorAll('.feed-filter-btn');
  filterBtns.forEach(fbtn => {
    fbtn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      fbtn.classList.add('active');
      activeFilter = fbtn.getAttribute('data-filter') || 'ALL';
      renderThreatStream();
    });
  });
}

// ============================================================================
// URL Search Form Handler
// ============================================================================
function setupSearchForm() {
  if (!urlSearchFormEl) return;

  urlSearchFormEl.addEventListener('submit', async e => {
    e.preventDefault();
    const inputVal = storeUrlInputEl.value.trim();
    if (!inputVal) return;

    // Check if input matches one of our demo cases
    const matchedPreset = DEMO_TEST_CASES.find(
      tc => inputVal.includes(tc.data.domain) || tc.data.domain.includes(inputVal)
    );

    if (matchedPreset) {
      updateAnalysis(analyzePayload(matchedPreset.data));
      return;
    }

    // Try fetching from server API /api/v1/analyze
    try {
      const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: inputVal,
          domain: inputVal.replace(/^https?:\/\//, '').split('/')[0],
        }),
      });

      if (response.ok) {
        const data: AnalysisResult = await response.json();
        updateAnalysis(data);
        return;
      }
    } catch {
      // Local fallback
    }

    // Create ad-hoc evaluation
    const domainClean = inputVal.replace(/^https?:\/\//, '').split('/')[0];
    const adhocPayload: AnalysisPayload = {
      url: inputVal.startsWith('http') ? inputVal : `https://${inputVal}`,
      domain: domainClean,
      domainAgeDays: 45,
      isHttps: inputVal.startsWith('https://'),
      productName: `Storefront Assessment: ${domainClean}`,
      price: 1999,
      referenceMarketPrice: 3999,
    };

    updateAnalysis(analyzePayload(adhocPayload));
  });
}

// ============================================================================
// Event Listeners Initialization
// ============================================================================
function initEventListeners() {
  if (btnSimulateCheckoutEl) {
    btnSimulateCheckoutEl.addEventListener('click', openSecurityWarningModal);
  }

  if (btnModalAbortEl) {
    btnModalAbortEl.addEventListener('click', closeSecurityWarningModal);
  }

  if (btnModalDismissEl) {
    btnModalDismissEl.addEventListener('click', closeSecurityWarningModal);
  }

  if (modalBackdropEl) {
    modalBackdropEl.addEventListener('click', e => {
      if (e.target === modalBackdropEl) {
        closeSecurityWarningModal();
      }
    });
  }

  setupSearchForm();
  setupNavigationTabs();
}

// ============================================================================
// App Bootstrap
// ============================================================================
function bootstrap() {
  renderPresets();
  updateAnalysis(analyzePayload(DEMO_TEST_CASES[0].data));
  initEntranceAnimations();
  initEventListeners();
}

// Run on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}
