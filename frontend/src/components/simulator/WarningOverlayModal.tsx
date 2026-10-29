import React from 'react';
import { AnalysisResult } from '../../types';
import { ShieldAlert, ArrowLeft, ExternalLink } from 'lucide-react';

interface WarningOverlayModalProps {
  result: AnalysisResult;
  onGoBack: () => void;
  onViewDetails: () => void;
  onDismiss: () => void;
}

export const WarningOverlayModal: React.FC<WarningOverlayModalProps> = ({
  result,
  onGoBack,
  onViewDetails,
  onDismiss,
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-neutral-900/60 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-lg bg-white border border-neutral-300 rounded-xl p-6 sm:p-7 shadow-2xl text-neutral-900">
        
        {/* Security Warning Header */}
        <div className="flex items-center gap-2 text-blue-700 font-bold text-xs tracking-wider uppercase mb-1">
          <div className="p-1 rounded bg-blue-50 border border-blue-200">
            <ShieldAlert className="w-4 h-4 text-blue-600" />
          </div>
          <span>WEBGUARD SECURITY INTERCEPTION</span>
        </div>

        <h3 className="text-lg font-bold text-neutral-900 mt-2">
          Security advisory before proceeding to payment
        </h3>
        <p className="text-neutral-500 text-xs mt-1 mb-5">
          This website contains multiple high-risk shopping indicators detected by our multi-factor engine.
        </p>

        {/* Score Card - Pure White with Single Blue Accent */}
        <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-4 flex items-center justify-between mb-5">
          <div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500 font-semibold">
              Calculated Risk Score
            </span>
            <div className="flex items-baseline gap-1 mt-0.5">
              <span className="text-4xl font-extrabold font-mono text-neutral-900 tracking-tight">
                {result.riskScore}
              </span>
              <span className="text-sm font-medium text-neutral-500 font-mono">/ 100</span>
            </div>
          </div>
          <div className="text-right">
            <span className="inline-block px-2.5 py-1 rounded bg-blue-600 text-white font-bold text-xs tracking-wider">
              {result.riskLevel} FRAUD RISK
            </span>
            <div className="text-[11px] text-neutral-500 mt-1 font-mono">Pre-Payment Interception</div>
          </div>
        </div>

        {/* Main Reasons Bullet Points */}
        <div className="mb-6">
          <h4 className="text-xs font-bold text-neutral-800 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            Main detected indicators:
          </h4>
          <ul className="space-y-2 text-xs text-neutral-700">
            {result.explanations.slice(0, 5).map((exp, idx) => (
              <li key={idx} className="flex items-start gap-2 bg-neutral-50 p-2.5 rounded border border-neutral-200">
                <span className="text-blue-600 font-bold shrink-0 mt-0.5">•</span>
                <div className="flex-1">
                  <span className="font-semibold text-neutral-900">{exp.factor}: </span>
                  <span className="text-neutral-600">{exp.explanation}</span>
                </div>
                <span className="text-blue-700 font-mono font-bold shrink-0">+{exp.points} pts</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Defensive Action Buttons */}
        <div className="flex flex-col gap-2">
          <button
            onClick={onGoBack}
            className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs tracking-wide transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-sm"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>GO BACK TO SAFETY (Recommended)</span>
          </button>

          <button
            onClick={onViewDetails}
            className="w-full py-2.5 px-4 rounded-lg bg-white hover:bg-neutral-50 text-neutral-800 font-semibold text-xs border border-neutral-300 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <ExternalLink className="w-3.5 h-3.5 text-neutral-600" />
            <span>VIEW DETAILED FORENSIC BREAKDOWN</span>
          </button>

          <button
            onClick={onDismiss}
            className="w-full py-1.5 text-center text-xs text-neutral-400 hover:text-neutral-700 transition-colors underline cursor-pointer"
          >
            Continue at my own risk (Dismiss warning)
          </button>
        </div>

        {/* Transparency note */}
        <div className="mt-4 pt-3 border-t border-neutral-200 text-[10px] text-neutral-400 text-center font-mono">
          WebGuard is a client-side defensive protection tool. User retains absolute operational authority.
        </div>
      </div>
    </div>
  );
};
