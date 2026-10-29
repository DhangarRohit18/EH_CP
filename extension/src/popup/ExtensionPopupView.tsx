import React, { useState } from 'react';
import { AnalysisResult } from '../types';
import { ShieldCheck, ExternalLink, ChevronRight, Lock, Globe } from 'lucide-react';

interface ExtensionPopupProps {
  result: AnalysisResult | null;
  onViewFullAnalysis?: () => void;
  onContinueCarefully?: () => void;
  isCompact?: boolean;
}

export const ExtensionPopupView: React.FC<ExtensionPopupProps> = ({
  result,
  onViewFullAnalysis,
  onContinueCarefully,
  isCompact = false,
}) => {
  const [expandedFactor, setExpandedFactor] = useState<string | null>(null);

  if (!result) {
    return (
      <div className="w-[360px] min-h-[460px] bg-white text-neutral-900 p-5 flex flex-col items-center justify-center text-center font-sans border border-neutral-200">
        <div className="w-10 h-10 rounded-full border-2 border-blue-600 border-t-transparent animate-spin mb-4" />
        <h3 className="text-xs font-semibold tracking-wider text-neutral-800 uppercase">Scanning Storefront</h3>
        <p className="text-xs text-neutral-500 mt-1 max-w-[200px]">
          Extracting DOM signals & evaluating multi-factor risk engine...
        </p>
      </div>
    );
  }

  const score = result.riskScore;
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  const singleAccentColor = '#2563eb';

  return (
    <div className={`w-[360px] bg-white text-neutral-900 font-sans border border-neutral-300 shadow-md flex flex-col ${isCompact ? '' : 'rounded-xl overflow-hidden'}`}>
      <div className="bg-white px-4 py-3 border-b border-neutral-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-blue-600 flex items-center justify-center text-white">
            <ShieldCheck className="w-3.5 h-3.5" />
          </div>
          <div>
            <span className="font-extrabold text-xs tracking-wider text-neutral-900 font-mono">WEBGUARD</span>
            <span className="text-[10px] text-neutral-400 ml-1.5 font-mono">v1.0</span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] font-mono text-neutral-600">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
          <span>SHIELD ON</span>
        </div>
      </div>

      <div className="bg-neutral-50 px-4 py-2 border-b border-neutral-200 flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5 truncate max-w-[240px]">
          <Globe className="w-3.5 h-3.5 text-neutral-400 shrink-0" />
          <span className="font-mono font-medium text-neutral-800 truncate">{result.domain}</span>
        </div>
        <span className="text-[10px] font-mono text-neutral-500 flex items-center gap-0.5">
          <Lock className="w-2.5 h-2.5 text-blue-600" /> TLS
        </span>
      </div>

      <div className="p-4 flex items-center justify-between border-b border-neutral-200 bg-white">
        <div className="flex items-center gap-3">
          <div className="relative w-20 h-20 flex items-center justify-center shrink-0">
            <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r={radius}
                stroke="#e5e5e5"
                strokeWidth="8"
                fill="transparent"
              />
              <circle
                cx="50"
                cy="50"
                r={radius}
                stroke={singleAccentColor}
                strokeWidth="8"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                style={{ transition: 'stroke-dashoffset 0.8s ease-in-out' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-xl font-black font-mono tracking-tight text-neutral-900 leading-none">
                {score}
              </span>
              <span className="text-[9px] font-mono text-neutral-400">/ 100</span>
            </div>
          </div>

          <div>
            <span className="inline-block px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200">
              {result.riskLevel} FRAUD RISK
            </span>
            <div className="text-xs font-semibold text-neutral-800 mt-1 line-clamp-1">
              {result.productName}
            </div>
            <div className="text-[11px] font-mono text-neutral-500 mt-0.5">
              Listed: <strong className="text-neutral-900">{result.currency}{result.price?.toLocaleString()}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="px-4 py-3 bg-neutral-50 border-b border-neutral-200">
        <div className="text-[10px] font-mono uppercase tracking-wider text-neutral-500 font-bold mb-2">
          Point Contribution Breakdown
        </div>
        <div className="space-y-1.5">
          {result.explanations.slice(0, 4).map((exp, idx) => (
            <div key={idx} className="flex items-center justify-between text-xs bg-white p-2 rounded border border-neutral-200">
              <span className="text-neutral-700 truncate pr-2">{exp.factor}</span>
              <span className="font-mono font-bold text-blue-700 shrink-0 text-[11px]">
                +{exp.points} pts
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-3 bg-white space-y-1 flex-1 overflow-y-auto max-h-[160px]">
        {Object.entries(result.factors).map(([key, factor]) => {
          const isExpanded = expandedFactor === key;

          return (
            <div key={key} className="border border-neutral-200 rounded-md overflow-hidden bg-white text-xs">
              <button
                onClick={() => setExpandedFactor(isExpanded ? null : key)}
                className="w-full p-2 flex items-center justify-between hover:bg-neutral-50 transition-colors text-left cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium text-neutral-800">{factor.name}</span>
                </div>
                <div className="flex items-center gap-1.5 font-mono">
                  <span className="text-blue-700 font-bold">+{factor.contribution}</span>
                  <ChevronRight className={`w-3.5 h-3.5 text-neutral-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
                </div>
              </button>

              {isExpanded && (
                <div className="p-2 bg-neutral-50 border-t border-neutral-200 text-[11px] text-neutral-600 leading-snug">
                  <p>{factor.reason}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="p-3 bg-neutral-50 border-t border-neutral-200 flex flex-col gap-1.5">
        <button
          onClick={onViewFullAnalysis}
          className="w-full py-2 px-3 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs tracking-wide transition-colors flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
        >
          <span>View Full Forensic Dossier</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </button>

        {onContinueCarefully && (
          <button
            onClick={onContinueCarefully}
            className="w-full py-1 text-center text-[11px] text-neutral-400 hover:text-neutral-600 cursor-pointer"
          >
            Dismiss popup
          </button>
        )}
      </div>
    </div>
  );
};

export default ExtensionPopupView;
