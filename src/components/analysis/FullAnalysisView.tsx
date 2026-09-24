import React, { useState } from 'react';
import { AnalysisResult } from '../../types';
import {
  ShieldAlert,
  Globe,
  Download,
  Share2,
  Lock,
  Cpu,
  Clock,
  Info,
  Activity
} from 'lucide-react';

interface FullAnalysisViewProps {
  result: AnalysisResult;
  onBackToSimulator: () => void;
}

export const FullAnalysisView: React.FC<FullAnalysisViewProps> = ({
  result,
  onBackToSimulator,
}) => {
  const [selectedFactorKey, setSelectedFactorKey] = useState<string>('price');
  const [copied, setCopied] = useState<boolean>(false);

  const score = result.riskScore;
  const singleAccentColor = '#2563eb'; // Cobalt Blue

  // Circular gauge parameters
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const handleExportJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `webguard-report-${result.domain}-${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col gap-8 pb-12 bg-white text-neutral-900">
      
      {/* Top Header & Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-neutral-500 mb-1">
            <button
              onClick={onBackToSimulator}
              className="text-blue-600 hover:text-blue-800 font-medium cursor-pointer"
            >
              ← Back to Simulator
            </button>
            <span>/</span>
            <span>Forensic Assessment Dossier</span>
            <span>/</span>
            <span className="text-neutral-700 font-mono">{result.id}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-neutral-900 tracking-tight flex items-center gap-2.5">
            <span>Storefront Forensic Audit</span>
            <span className="text-neutral-500 font-normal text-lg">({result.domain})</span>
          </h1>
          <div className="flex items-center gap-3 text-xs text-neutral-500 mt-1">
            <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Evaluated: {new Date(result.timestamp).toLocaleString()}</span>
            <span>·</span>
            <span className="flex items-center gap-1"><Cpu className="w-3.5 h-3.5" /> Engine: {result.metadata?.modelType || 'Hybrid Rule-ML'}</span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleShare}
            className="px-3.5 py-2 rounded-md bg-white border border-neutral-300 hover:bg-neutral-50 text-neutral-700 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>{copied ? 'Link Copied!' : 'Share Dossier'}</span>
          </button>
          <button
            onClick={handleExportJson}
            className="px-3.5 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Forensic JSON</span>
          </button>
        </div>
      </div>

      {/* Hero Overview: 3 Cards */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">
        
        {/* Card 1: Risk Gauge (4 Cols) */}
        <div className="md:col-span-4 bg-white border border-neutral-200 rounded-xl p-6 flex flex-col items-center justify-center text-center shadow-xs">
          <div className="text-[11px] font-mono uppercase tracking-widest text-neutral-500 mb-3 font-semibold">
            Aggregated Fraud Risk Score
          </div>

          <div className="relative w-40 h-40 my-2 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 160 160">
              <circle
                cx="80"
                cy="80"
                r={radius}
                stroke="#e5e5e5"
                strokeWidth="12"
                fill="transparent"
              />
              <circle
                cx="80"
                cy="80"
                r={radius}
                stroke={singleAccentColor}
                strokeWidth="12"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                style={{ transition: 'stroke-dashoffset 1s ease-out' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-extrabold font-mono text-neutral-900 tracking-tight">{result.riskScore}</span>
              <span className="text-xs font-mono text-neutral-500">/ 100</span>
            </div>
          </div>

          <div className="mt-2 px-3.5 py-1 rounded-full border border-blue-200 bg-blue-50 text-blue-700 text-xs font-bold tracking-wider font-mono">
            {result.riskLevel} FRAUD RISK
          </div>
          <p className="text-[11px] text-neutral-500 mt-2 max-w-xs">
            {result.riskScore >= 60
              ? 'Multi-factor signals indicate severe deceptive patterns. Pre-payment block recommended.'
              : 'Signals fall within standard e-commerce operational tolerances.'}
          </p>
        </div>

        {/* Card 2: Website Overview (4 Cols) */}
        <div className="md:col-span-4 bg-white border border-neutral-200 rounded-xl p-6 flex flex-col justify-between shadow-xs">
          <div>
            <div className="text-[11px] font-mono uppercase tracking-widest text-neutral-500 mb-3 font-semibold flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-blue-600" />
              Website Overview
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-neutral-400 block text-[10px] uppercase font-mono">Domain Name</span>
                <span className="text-neutral-900 font-mono font-bold text-sm">{result.domain}</span>
              </div>
              <div>
                <span className="text-neutral-400 block text-[10px] uppercase font-mono">Evaluated Product</span>
                <span className="text-neutral-800 font-medium">{result.productName}</span>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-neutral-400 block text-[10px] uppercase font-mono">Listed Price</span>
                  <span className="text-neutral-900 font-mono font-bold text-sm">
                    {result.currency}{result.price?.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-neutral-400 block text-[10px] uppercase font-mono">TLS Security</span>
                  <span className="text-blue-700 font-mono font-semibold flex items-center gap-1">
                    <Lock className="w-3 h-3 text-blue-600" /> Valid HTTPS
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-neutral-200 mt-4 text-[11px] text-neutral-400 font-mono">
            Analysis Reference: {result.id.slice(0, 16)}...
          </div>
        </div>

        {/* Card 3: Defensive Recommendation (4 Cols) */}
        <div className="md:col-span-4 bg-white border border-neutral-200 rounded-xl p-6 flex flex-col justify-between shadow-xs">
          <div>
            <div className="text-[11px] font-mono uppercase tracking-widest text-neutral-500 mb-3 font-semibold flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-blue-600" />
              Pre-Payment Recommendation
            </div>

            <div className="p-3.5 rounded-lg border border-neutral-200 bg-neutral-50 text-neutral-800 mb-3 text-xs leading-relaxed">
              <span className="font-bold block mb-1 text-neutral-900 font-mono uppercase text-[11px]">
                {result.riskLevel} ADVISORY
              </span>
              {result.recommendation}
            </div>
          </div>

          <div className="space-y-1 text-[11px] text-neutral-500 font-mono">
            <div>✓ Zero sensitive credentials collected or stored</div>
            <div>✓ Transparent explainable point decomposition</div>
          </div>
        </div>

      </div>

      {/* Seven Factor Breakdown (Cards & Bars with Exact Weights) */}
      <div className="bg-white border border-neutral-200 rounded-xl p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <div>
            <h2 className="text-sm font-bold text-neutral-900 uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-600" />
              Seven Factor Scores & Weights (Total: 100%)
            </h2>
            <p className="text-xs text-neutral-500 mt-0.5">
              Multi-factor decomposition. Each factor contributes directly to the final composite index.
            </p>
          </div>
          <span className="text-[11px] font-mono text-neutral-400">
            Formula: ∑ (Factor Score × Weight) = Composite Score
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3">
          <FactorMiniCard
            title="Domain"
            weight="20%"
            rawScore={result.factors.domain.rawScore}
            contrib={result.factors.domain.contribution}
            onClick={() => setSelectedFactorKey('domain')}
            isSelected={selectedFactorKey === 'domain'}
          />
          <FactorMiniCard
            title="Price Anomaly"
            weight="20%"
            rawScore={result.factors.price.rawScore}
            contrib={result.factors.price.contribution}
            onClick={() => setSelectedFactorKey('price')}
            isSelected={selectedFactorKey === 'price'}
          />
          <FactorMiniCard
            title="Review Patterns"
            weight="15%"
            rawScore={result.factors.reviews.rawScore}
            contrib={result.factors.reviews.contribution}
            onClick={() => setSelectedFactorKey('reviews')}
            isSelected={selectedFactorKey === 'reviews'}
          />
          <FactorMiniCard
            title="Website Identity"
            weight="15%"
            rawScore={result.factors.identity.rawScore}
            contrib={result.factors.identity.contribution}
            onClick={() => setSelectedFactorKey('identity')}
            isSelected={selectedFactorKey === 'identity'}
          />
          <FactorMiniCard
            title="Refund Policy"
            weight="10%"
            rawScore={result.factors.policy.rawScore}
            contrib={result.factors.policy.contribution}
            onClick={() => setSelectedFactorKey('policy')}
            isSelected={selectedFactorKey === 'policy'}
          />
          <FactorMiniCard
            title="Payment Methods"
            weight="10%"
            rawScore={result.factors.payment.rawScore}
            contrib={result.factors.payment.contribution}
            onClick={() => setSelectedFactorKey('payment')}
            isSelected={selectedFactorKey === 'payment'}
          />
          <FactorMiniCard
            title="Site Behaviour"
            weight="10%"
            rawScore={result.factors.behaviour.rawScore}
            contrib={result.factors.behaviour.contribution}
            onClick={() => setSelectedFactorKey('behaviour')}
            isSelected={selectedFactorKey === 'behaviour'}
          />
        </div>
      </div>

      {/* Risk Contribution Waterfall & Point Additions Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Waterfall Contribution Chart (7 Cols) */}
        <div className="lg:col-span-7 bg-white border border-neutral-200 rounded-xl p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-neutral-900 uppercase tracking-wider flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-blue-600" />
                Explainable Risk Contribution Breakdown
              </h3>
              <p className="text-xs text-neutral-500 mt-0.5">
                Exact point contributions summing to {result.riskScore} / 100
              </p>
            </div>
            <span className="text-xs font-mono font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
              Total: {result.riskScore} pts
            </span>
          </div>

          <div className="space-y-3 pt-2">
            {result.explanations.map((item, idx) => {
              const maxPoints = 25; // scaling
              const barWidthPct = Math.min(100, Math.round((item.points / maxPoints) * 100));

              return (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-neutral-900">{item.factor}</span>
                    <span className="font-mono font-bold text-blue-700">+{item.points} pts</span>
                  </div>
                  
                  {/* Progress track */}
                  <div className="w-full h-2.5 rounded-full bg-neutral-100 overflow-hidden flex items-center border border-neutral-200">
                    <div
                      className="h-full rounded-full bg-blue-600 transition-all duration-500"
                      style={{ width: `${barWidthPct}%` }}
                    />
                  </div>
                  
                  <div className="text-[11px] text-neutral-500 font-sans flex items-center justify-between">
                    <span>{item.explanation}</span>
                    <span className="text-neutral-400 font-mono text-[10px] shrink-0 ml-2">
                      Weight: {item.weightPercent}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Detected Indicators Feed (5 Cols) */}
        <div className="lg:col-span-5 bg-white border border-neutral-200 rounded-xl p-6 flex flex-col shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-neutral-900 uppercase tracking-wider">
                Detected Security Signals ({result.detectedSignals.length})
              </h3>
              <p className="text-xs text-neutral-500 mt-0.5">
                Rule engine triggers & anomaly alerts
              </p>
            </div>
          </div>

          <div className="space-y-2.5 overflow-y-auto max-h-[380px] pr-1 flex-1">
            {result.detectedSignals.map((sig, i) => (
              <div key={i} className="p-3 rounded-lg border border-neutral-200 bg-neutral-50 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] text-neutral-500 uppercase font-semibold">
                    {sig.category}
                  </span>
                  <span className="text-[9px] uppercase font-bold font-mono px-1.5 py-0.2 rounded border bg-white border-neutral-300 text-neutral-700">
                    {sig.severity}
                  </span>
                </div>
                <p className="font-medium text-neutral-900">{sig.message}</p>
                {sig.ruleTriggered && (
                  <div className="text-[10px] font-mono text-neutral-400">
                    Rule: {sig.ruleTriggered}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Deep-Dive Investigation Tabs for the 7 Factors */}
      <div className="bg-white border border-neutral-200 rounded-xl p-6 shadow-xs">
        <h3 className="text-sm font-bold text-neutral-900 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-600" />
          Detailed Factor Investigation & Forensics
        </h3>

        {/* Tab Headers */}
        <div className="flex items-center gap-2 overflow-x-auto pb-3 border-b border-neutral-200 text-xs font-semibold">
          {[
            { key: 'price', label: 'Price Anomaly (20%)' },
            { key: 'domain', label: 'Domain Credibility (20%)' },
            { key: 'reviews', label: 'Review Patterns (15%)' },
            { key: 'identity', label: 'Website Identity (15%)' },
            { key: 'policy', label: 'Refund Policy (10%)' },
            { key: 'payment', label: 'Payment Methods (10%)' },
            { key: 'behaviour', label: 'Site Behaviour (10%)' },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setSelectedFactorKey(tab.key)}
              className={`px-3 py-1.5 rounded-md whitespace-nowrap transition-colors cursor-pointer ${
                selectedFactorKey === tab.key
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-neutral-100 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Detail Contents */}
        <div className="pt-5">
          {selectedFactorKey === 'price' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Listed Price</span>
                <div className="text-xl font-bold font-mono text-neutral-900">{result.currency}{result.price?.toLocaleString()}</div>
                <p className="text-neutral-500 text-[11px]">Observed customer checkout price</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Reference Market MRP</span>
                <div className="text-xl font-bold font-mono text-neutral-700">
                  {result.currency}1,19,999
                </div>
                <p className="text-neutral-500 text-[11px]">Authorized retail baseline for {result.productName}</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Isolation Forest ML Anomaly</span>
                <div className="text-xl font-bold font-mono text-blue-700">
                  {result.metadata?.isolationForestAnomaly ? 'OUTLIER DETECTED' : 'NORMAL CLUSTER'}
                </div>
                <p className="text-neutral-500 text-[11px]">Pricing is 79% below normal market distribution</p>
              </div>
            </div>
          )}

          {selectedFactorKey === 'domain' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Domain Age</span>
                <div className="text-xl font-bold font-mono text-blue-700">8 Days Old</div>
                <p className="text-neutral-500 text-[11px]">Scam storefronts exhibit heavy churn (&lt; 30 days active)</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Top-Level Domain (TLD)</span>
                <div className="text-xl font-bold font-mono text-neutral-900">.local / High Churn</div>
                <p className="text-neutral-500 text-[11px]">Registrar reputation analysis</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Typosquatting Check</span>
                <div className="text-xl font-bold font-mono text-blue-700">Low Levenshtein Distance</div>
                <p className="text-neutral-500 text-[11px]">Simulates brand mimicry patterns</p>
              </div>
            </div>
          )}

          {selectedFactorKey === 'reviews' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">NLP Duplicate Similarity</span>
                <div className="text-xl font-bold font-mono text-blue-700">
                  {Math.round((result.metadata?.nlpSimilarityScore || 0.88) * 100)}% Match
                </div>
                <p className="text-neutral-500 text-[11px]">Multiple reviews repeat identical syntactic clauses</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Rating Skew</span>
                <div className="text-xl font-bold font-mono text-neutral-900">4.9 / 5.0 (Uniform)</div>
                <p className="text-neutral-500 text-[11px]">Unnatural lack of standard negative/neutral feedback</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Review Burst Pattern</span>
                <div className="text-xl font-bold font-mono text-blue-700">Compressed Burst</div>
                <p className="text-neutral-500 text-[11px]">Reviews published within tightly clustered 48hr window</p>
              </div>
            </div>
          )}

          {selectedFactorKey === 'identity' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Contact Email Integrity</span>
                <div className="text-xl font-bold font-mono text-blue-700">Free Public Webmail</div>
                <p className="text-neutral-500 text-[11px]">Uses Gmail/Hotmail instead of corporate domain mail</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Phone Number Verification</span>
                <div className="text-xl font-bold font-mono text-neutral-900">Unregistered VPA</div>
                <p className="text-neutral-500 text-[11px]">No official corporate toll-free support line</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Physical Incorporation</span>
                <div className="text-xl font-bold font-mono text-neutral-700">Vague Industrial Zone</div>
                <p className="text-neutral-500 text-[11px]">No verifiable MCA/corporate registrar entity match</p>
              </div>
            </div>
          )}

          {selectedFactorKey === 'policy' && (
            <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-2 text-xs">
              <div className="text-neutral-500 font-mono text-[11px]">Detected Policy Language:</div>
              <p className="text-neutral-800 leading-relaxed font-mono bg-white p-3 rounded border border-neutral-200">
                "{result.factors.policy.reason}"
              </p>
              <div className="text-neutral-600 text-[11px] font-medium">
                Missing standard statutory return window. Vague discretionary wording detected.
              </div>
            </div>
          )}

          {selectedFactorKey === 'payment' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Enforced Payment Rail</span>
                <div className="text-xl font-bold font-mono text-blue-700">Prepaid Only (No COD)</div>
                <p className="text-neutral-500 text-[11px]">Blocks buyer from inspecting goods prior to funds transfer</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Personal UPI Handle Flag</span>
                <div className="text-xl font-bold font-mono text-blue-700">Unverified P2P VPA</div>
                <p className="text-neutral-500 text-[11px]">Requests direct credit to personal mobile VPA</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Escrow / Chargeback Route</span>
                <div className="text-xl font-bold font-mono text-neutral-700">Not Available</div>
                <p className="text-neutral-500 text-[11px]">Zero dispute resolution mechanism</p>
              </div>
            </div>
          )}

          {selectedFactorKey === 'behaviour' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Checkout Redirection</span>
                <div className="text-xl font-bold font-mono text-blue-700">Cross-Domain URL</div>
                <p className="text-neutral-500 text-[11px]">Redirects to third-party payment collector domain</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">DOM Form Inspection</span>
                <div className="text-xl font-bold font-mono text-neutral-900">Hidden Inputs</div>
                <p className="text-neutral-500 text-[11px]">Off-screen form collectors detected in document body</p>
              </div>

              <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-1">
                <span className="text-neutral-400 uppercase font-mono text-[10px]">Psychological Urgency</span>
                <div className="text-xl font-bold font-mono text-blue-700">Artificial Countdown</div>
                <p className="text-neutral-500 text-[11px]">Aggressive ticking timer inducing rushed impulse decisions</p>
              </div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
};

const FactorMiniCard: React.FC<{
  title: string;
  weight: string;
  rawScore: number;
  contrib: number;
  onClick: () => void;
  isSelected: boolean;
}> = ({ title, weight, rawScore, contrib, onClick, isSelected }) => {
  return (
    <button
      onClick={onClick}
      className={`p-3 rounded-lg border text-left transition-all cursor-pointer flex flex-col justify-between ${
        isSelected
          ? 'bg-blue-50 border-blue-600 shadow-xs'
          : 'bg-white border-neutral-200 hover:bg-neutral-50'
      }`}
    >
      <div>
        <div className="flex items-center justify-between text-[10px] font-mono text-neutral-400">
          <span>{weight}</span>
          <span className="px-1 rounded border border-blue-200 bg-blue-50 text-blue-700 text-[9px] font-bold">
            +{contrib}
          </span>
        </div>
        <div className="text-xs font-semibold text-neutral-900 mt-1 truncate">{title}</div>
      </div>

      <div className="mt-2 pt-2 border-t border-neutral-100 flex items-baseline justify-between">
        <span className="text-[10px] font-mono text-neutral-400">Index:</span>
        <span className="font-mono font-bold text-xs text-neutral-900">{rawScore}/100</span>
      </div>
    </button>
  );
};
