import React, { useState } from 'react';
import { AnalysisPayload, AnalysisResult } from '../../types';
import { DEMO_TEST_CASES } from '../../engine/testCases';
import { analyzePayload } from '../../engine/riskEngine';
import {
  Terminal,
  Play,
  RotateCw,
  Copy,
  Check
} from 'lucide-react';

interface ApiTesterViewProps {
  onAnalyzeSuccess: (res: AnalysisResult) => void;
}

export const ApiTesterView: React.FC<ApiTesterViewProps> = ({
  onAnalyzeSuccess,
}) => {
  const [jsonInput, setJsonInput] = useState<string>(() => {
    return JSON.stringify(DEMO_TEST_CASES[0].data, null, 2);
  });
  const [responseOutput, setResponseOutput] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRunAnalysis = async () => {
    setErrorMsg(null);
    setLoading(true);

    try {
      const parsedPayload: AnalysisPayload = JSON.parse(jsonInput);

      // Attempt to hit live FastAPI backend or Express proxy first
      try {
        const res = await fetch('/api/v1/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(parsedPayload),
        });

        if (res.ok) {
          const result: AnalysisResult = await res.json();
          setResponseOutput(result);
          onAnalyzeSuccess(result);
          setLoading(false);
          return;
        }
      } catch {
        // Fall back to client risk engine
      }

      // Client engine execution
      const localResult = analyzePayload(parsedPayload);
      setResponseOutput(localResult);
      onAnalyzeSuccess(localResult);
    } catch (err: any) {
      setErrorMsg(`JSON Parse / Engine Error: ${err?.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = (sampleIndex: number) => {
    setJsonInput(JSON.stringify(DEMO_TEST_CASES[sampleIndex].data, null, 2));
    setErrorMsg(null);
  };

  const handleCopyResponse = () => {
    if (!responseOutput) return;
    navigator.clipboard.writeText(JSON.stringify(responseOutput, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col gap-6 bg-white text-neutral-900">
      {/* Header */}
      <div className="border-b border-neutral-200 pb-5">
        <h1 className="text-2xl font-extrabold text-neutral-900 tracking-tight flex items-center gap-2.5">
          <Terminal className="w-6 h-6 text-blue-600" />
          <span>Risk Engine REST API Sandbox</span>
        </h1>
        <p className="text-xs text-neutral-500 mt-1">
          Interactive client for testing <code className="text-blue-700 font-mono font-semibold">POST /api/v1/analyze</code> with custom JSON payloads.
        </p>
      </div>

      {/* Preset Quick Loader Buttons */}
      <div className="flex items-center gap-2 overflow-x-auto text-xs pb-1">
        <span className="text-neutral-500 font-mono text-[11px] shrink-0">Load Scenario:</span>
        {DEMO_TEST_CASES.map((tc, idx) => (
          <button
            key={tc.id}
            onClick={() => handleLoadSample(idx)}
            className="px-2.5 py-1 rounded bg-neutral-100 hover:bg-neutral-200 text-neutral-700 text-xs font-mono transition-colors whitespace-nowrap cursor-pointer border border-neutral-200"
          >
            {tc.name}
          </button>
        ))}
      </div>

      {/* Two Column Sandbox Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left: JSON Request Body Editor (6 Cols) */}
        <div className="lg:col-span-6 bg-white border border-neutral-200 rounded-xl p-5 shadow-xs flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-neutral-800 uppercase">
                HTTP Request Body
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-bold">
                POST /api/v1/analyze
              </span>
            </div>
          </div>

          <textarea
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            rows={19}
            className="w-full p-3.5 bg-neutral-50 border border-neutral-200 rounded-lg text-xs font-mono text-neutral-900 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 resize-none"
            placeholder="Paste AnalysisPayload JSON here..."
          />

          {errorMsg && (
            <div className="mt-3 p-2.5 rounded bg-neutral-100 border border-neutral-300 text-xs text-neutral-800 font-mono">
              {errorMsg}
            </div>
          )}

          <div className="mt-4 flex items-center justify-between">
            <span className="text-[11px] text-neutral-400 font-mono">
              Content-Type: application/json
            </span>

            <button
              onClick={handleRunAnalysis}
              disabled={loading}
              className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 transition-colors cursor-pointer disabled:opacity-50 shadow-xs"
            >
              {loading ? (
                <>
                  <RotateCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Evaluating Risk...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Execute Analysis</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right: API Response View (6 Cols) */}
        <div className="lg:col-span-6 bg-white border border-neutral-200 rounded-xl p-5 shadow-xs flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-neutral-800 uppercase">
                JSON Response Outcome
              </span>
              {responseOutput && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-bold">
                  200 OK ({responseOutput.riskScore}/100)
                </span>
              )}
            </div>

            {responseOutput && (
              <button
                onClick={handleCopyResponse}
                className="px-2.5 py-1 rounded bg-white hover:bg-neutral-100 text-neutral-600 text-xs font-mono border border-neutral-300 flex items-center gap-1 transition-colors cursor-pointer"
              >
                {copied ? <Check className="w-3 h-3 text-blue-600" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            )}
          </div>

          <div className="w-full h-[380px] p-3.5 bg-neutral-50 border border-neutral-200 rounded-lg overflow-y-auto font-mono text-xs text-neutral-800">
            {responseOutput ? (
              <pre>{JSON.stringify(responseOutput, null, 2)}</pre>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center text-neutral-400">
                <Terminal className="w-8 h-8 mb-2 stroke-1 text-neutral-300" />
                <p>Click "Execute Analysis" to run payload against engine</p>
              </div>
            )}
          </div>

          {responseOutput && (
            <div className="mt-4 pt-3 border-t border-neutral-200 flex items-center justify-between text-xs text-neutral-600 font-mono">
              <span>Risk: <strong>{responseOutput.riskLevel}</strong></span>
              <span>Pre-Payment Warning: <strong>{responseOutput.isPrePaymentTriggered ? 'Triggered' : 'None'}</strong></span>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
