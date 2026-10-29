import React, { useState } from 'react';
import {
  Package,
  Layers,
  Copy,
  Check,
  Lock,
  ArrowRight
} from 'lucide-react';

export const ExtensionHubView: React.FC = () => {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const manifestCode = `{
  "manifest_version": 3,
  "name": "WebGuard: E-Commerce Fraud Risk Protection",
  "version": "1.0.0",
  "description": "Explainable multi-factor pre-payment fraud protection.",
  "permissions": [
    "activeTab",
    "storage",
    "scripting"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "background": {
    "service_worker": "background/service-worker.js"
  },
  "action": {
    "default_popup": "popup/index.html",
    "default_title": "WebGuard Security Shield"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content/content.js"],
      "run_at": "document_idle"
    }
  ]
}`;

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <div className="flex flex-col gap-6 bg-white text-neutral-900">
      {/* Header */}
      <div className="border-b border-neutral-200 pb-5">
        <h1 className="text-2xl font-extrabold text-neutral-900 tracking-tight flex items-center gap-2.5">
          <Package className="w-6 h-6 text-blue-600" />
          <span>Chrome & Edge Manifest V3 Extension Hub</span>
        </h1>
        <p className="text-xs text-neutral-500 mt-1">
          Install and verify the WebGuard browser extension to protect your live checkout sessions.
        </p>
      </div>

      {/* 3 Step Installation Flow */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-neutral-200 rounded-xl p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="w-7 h-7 rounded-full bg-blue-50 border border-blue-200 text-blue-700 font-bold font-mono text-xs flex items-center justify-center mb-3">
              1
            </div>
            <h3 className="font-bold text-sm text-neutral-900 mb-1">Open Extensions Manager</h3>
            <p className="text-xs text-neutral-500 leading-relaxed">
              Open your browser and navigate to <code className="text-neutral-800 bg-neutral-100 px-1 py-0.5 rounded font-mono">chrome://extensions</code> or <code className="text-neutral-800 bg-neutral-100 px-1 py-0.5 rounded font-mono">edge://extensions</code>.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-neutral-100 text-[11px] text-neutral-400 font-mono">
            Step 1 of 3
          </div>
        </div>

        <div className="bg-white border border-neutral-200 rounded-xl p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="w-7 h-7 rounded-full bg-blue-50 border border-blue-200 text-blue-700 font-bold font-mono text-xs flex items-center justify-center mb-3">
              2
            </div>
            <h3 className="font-bold text-sm text-neutral-900 mb-1">Enable Developer Mode</h3>
            <p className="text-xs text-neutral-500 leading-relaxed">
              Toggle the <strong>Developer mode</strong> switch in the top right corner of the Extensions management screen.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-neutral-100 text-[11px] text-neutral-400 font-mono">
            Step 2 of 3
          </div>
        </div>

        <div className="bg-white border border-neutral-200 rounded-xl p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="w-7 h-7 rounded-full bg-blue-50 border border-blue-200 text-blue-700 font-bold font-mono text-xs flex items-center justify-center mb-3">
              3
            </div>
            <h3 className="font-bold text-sm text-neutral-900 mb-1">Load Unpacked Extension</h3>
            <p className="text-xs text-neutral-500 leading-relaxed">
              Click <strong>"Load unpacked"</strong> and choose the <code className="text-neutral-800 bg-neutral-100 px-1 py-0.5 rounded font-mono">/extension</code> directory from this project workspace.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-neutral-100 text-[11px] text-neutral-400 font-mono">
            Step 3 of 3
          </div>
        </div>
      </div>

      {/* Code Inspector & Manifest Review */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left: Manifest File (7 Cols) */}
        <div className="lg:col-span-7 bg-white border border-neutral-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              <span className="font-mono text-xs font-bold text-neutral-900 uppercase">
                extension/manifest.json
              </span>
            </div>

            <button
              onClick={() => handleCopy(manifestCode, 'manifest')}
              className="px-2.5 py-1 rounded bg-white hover:bg-neutral-100 text-neutral-700 text-xs font-mono border border-neutral-300 flex items-center gap-1 transition-colors cursor-pointer"
            >
              {copiedCode === 'manifest' ? <Check className="w-3 h-3 text-blue-600" /> : <Copy className="w-3 h-3" />}
              <span>{copiedCode === 'manifest' ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          <pre className="p-4 bg-neutral-50 border border-neutral-200 rounded-lg font-mono text-xs text-neutral-800 overflow-x-auto max-h-[360px]">
            {manifestCode}
          </pre>
        </div>

        {/* Right: Security & Privacy Guarantees (5 Cols) */}
        <div className="lg:col-span-5 bg-white border border-neutral-200 rounded-xl p-5 shadow-xs space-y-4">
          <h3 className="font-bold text-sm text-neutral-900 uppercase tracking-wider flex items-center gap-2">
            <Lock className="w-4 h-4 text-blue-600" />
            Zero-Credential Safety Verification
          </h3>

          <div className="space-y-2.5 text-xs text-neutral-600">
            <div className="p-3 rounded-lg border border-neutral-200 bg-neutral-50">
              <span className="font-bold text-neutral-900 block mb-0.5">Explicit Input Filter</span>
              <p>The extractor excludes all password inputs, credit card inputs, CVVs, and auth tokens from DOM querying.</p>
            </div>

            <div className="p-3 rounded-lg border border-neutral-200 bg-neutral-50">
              <span className="font-bold text-neutral-900 block mb-0.5">Non-Persistent Service Worker</span>
              <p>Runs ephemerally in accordance with Manifest V3 standards, minimizing background memory footprint.</p>
            </div>

            <div className="p-3 rounded-lg border border-neutral-200 bg-neutral-50">
              <span className="font-bold text-neutral-900 block mb-0.5">Pre-Payment Interceptor</span>
              <p>Hooks the checkout DOM buttons to display defensive warnings before card submission.</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
