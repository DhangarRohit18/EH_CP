import React, { useState, useEffect } from 'react';
import { AnalysisResult } from './types';
import { DEMO_TEST_CASES } from './engine/testCases';
import { analyzePayload } from './engine/riskEngine';
import { StorefrontSimulator } from './components/simulator/StorefrontSimulator';
import { FullAnalysisView } from './components/analysis/FullAnalysisView';
import { DeveloperDashboardView } from './components/dashboard/DeveloperDashboardView';
import { AnalysisHistoryView } from './components/history/AnalysisHistoryView';
import { ApiTesterView } from './components/api-tester/ApiTesterView';
import { ExtensionHubView } from './components/extension-view/ExtensionHubView';
import {
  Shield,
  ShoppingBag,
  FileSearch,
  BarChart2,
  History,
  Terminal,
  Package,
  Lock,
} from 'lucide-react';

type ActiveView = 'simulator' | 'analysis' | 'dashboard' | 'history' | 'api' | 'extension';

export default function App() {
  const [activeView, setActiveView] = useState<ActiveView>('simulator');
  
  // Initialize with official canonical demo case: flashdeal-electronics.local (Score: 86)
  const [currentResult, setCurrentResult] = useState<AnalysisResult>(() => {
    return analyzePayload(DEMO_TEST_CASES[0].data);
  });

  // History state initialized with the 5 demo cases
  const [historyItems, setHistoryItems] = useState<AnalysisResult[]>(() => {
    return DEMO_TEST_CASES.map(tc => analyzePayload(tc.data));
  });

  // Try fetching latest history from server on load
  useEffect(() => {
    fetch('/api/v1/history')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setHistoryItems([...data]);
        }
      })
      .catch(() => {
        // In-memory fallback
      });
  }, []);

  const handleSelectAnalysis = (newResult: AnalysisResult) => {
    setCurrentResult(newResult);
    setHistoryItems(prev => {
      const filtered = prev.filter(p => p.id !== newResult.id);
      return [newResult, ...filtered];
    });
  };

  const handleSelectHistoryItem = (item: AnalysisResult) => {
    setCurrentResult(item);
    setActiveView('analysis');
  };

  const handleClearHistory = () => {
    setHistoryItems([]);
    fetch('/api/v1/history', { method: 'DELETE' }).catch(() => null);
  };

  return (
    <div className="min-h-screen bg-white text-neutral-900 flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
      
      {/* Top Header - Pure White */}
      <header className="sticky top-0 z-40 bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-4">
            
            {/* Logo and Brand */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <Shield className="w-5 h-5 stroke-[2.2]" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold tracking-wider text-base text-neutral-900 font-mono">
                    WEBGUARD
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-neutral-100 text-neutral-700 border border-neutral-200">
                    MV3 CORE
                  </span>
                </div>
                <p className="text-[11px] text-neutral-500 font-sans hidden sm:block truncate max-w-sm">
                  Explainable Multi-Factor E-Commerce Fraud Risk Assessment
                </p>
              </div>
            </div>

            {/* Target Live Score Badge */}
            <div className="hidden md:flex items-center gap-3 bg-white border border-neutral-200 rounded-lg px-3 py-1.5 shadow-sm">
              <div className="text-right">
                <div className="text-[10px] font-mono text-neutral-400 uppercase">Target</div>
                <div className="text-xs font-semibold text-neutral-800 font-mono truncate max-w-[140px]">
                  {currentResult.domain}
                </div>
              </div>

              <div
                onClick={() => setActiveView('analysis')}
                className="px-2.5 py-1 rounded bg-blue-50 border border-blue-200 text-blue-700 font-mono font-bold text-xs flex items-center gap-1.5 cursor-pointer hover:bg-blue-100 transition-colors"
                title="View Full Forensic Dossier"
              >
                <span>{currentResult.riskScore} / 100</span>
                <span className="text-[10px] font-normal uppercase opacity-75">({currentResult.riskLevel})</span>
              </div>
            </div>

            {/* Active Shield Indicator */}
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-xs font-medium font-mono">
                <span className="w-2 h-2 rounded-full bg-blue-600" />
                <span className="hidden lg:inline">Pre-Payment Guard Active</span>
                <span className="lg:hidden">Active</span>
              </div>
            </div>

          </div>

          {/* Navigation Bar Tabs */}
          <div className="flex items-center gap-1 overflow-x-auto py-2 border-t border-neutral-200 no-scrollbar text-xs font-medium">
            <NavTab
              active={activeView === 'simulator'}
              onClick={() => setActiveView('simulator')}
              icon={<ShoppingBag className="w-3.5 h-3.5" />}
              label="Storefront Simulator"
              badge="Live Interception"
            />
            <NavTab
              active={activeView === 'analysis'}
              onClick={() => setActiveView('analysis')}
              icon={<FileSearch className="w-3.5 h-3.5" />}
              label="Forensic Report (7 Factors)"
            />
            <NavTab
              active={activeView === 'dashboard'}
              onClick={() => setActiveView('dashboard')}
              icon={<BarChart2 className="w-3.5 h-3.5" />}
              label="SOC Analytics"
            />
            <NavTab
              active={activeView === 'history'}
              onClick={() => setActiveView('history')}
              icon={<History className="w-3.5 h-3.5" />}
              label="Audit History"
              count={historyItems.length}
            />
            <NavTab
              active={activeView === 'api'}
              onClick={() => setActiveView('api')}
              icon={<Terminal className="w-3.5 h-3.5" />}
              label="Risk Engine REST API"
            />
            <NavTab
              active={activeView === 'extension'}
              onClick={() => setActiveView('extension')}
              icon={<Package className="w-3.5 h-3.5" />}
              label="Extension Hub"
            />
          </div>
        </div>
      </header>

      {/* Main App Content Viewport - Pure White */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 bg-white">
        {activeView === 'simulator' && (
          <StorefrontSimulator
            currentResult={currentResult}
            onSelectAnalysis={handleSelectAnalysis}
            onOpenFullAnalysis={() => setActiveView('analysis')}
          />
        )}

        {activeView === 'analysis' && (
          <FullAnalysisView
            result={currentResult}
            onBackToSimulator={() => setActiveView('simulator')}
          />
        )}

        {activeView === 'dashboard' && (
          <DeveloperDashboardView
            historyItems={historyItems}
            onSelectAnalysis={(item) => {
              setCurrentResult(item);
              setActiveView('analysis');
            }}
          />
        )}

        {activeView === 'history' && (
          <AnalysisHistoryView
            historyItems={historyItems}
            onSelectHistoryItem={handleSelectHistoryItem}
            onClearHistory={handleClearHistory}
          />
        )}

        {activeView === 'api' && (
          <ApiTesterView
            onAnalyzeSuccess={(res) => {
              setCurrentResult(res);
              setHistoryItems(prev => [res, ...prev.filter(p => p.id !== res.id)]);
            }}
          />
        )}

        {activeView === 'extension' && (
          <ExtensionHubView />
        )}
      </main>

      {/* Defensive Privacy & Audit Footer */}
      <footer className="bg-white border-t border-neutral-200 py-6 text-xs text-neutral-500 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Lock className="w-3.5 h-3.5 text-blue-600" />
            <span>
              <strong className="text-neutral-700">Zero-Credential Telemetry:</strong> Passwords, CVV, OTP, and payment cards are strictly exempted from DOM extraction.
            </span>
          </div>
          <div className="flex items-center gap-4 text-[11px] font-mono text-neutral-400">
            <span>Weights: Dom 20% · Price 20% · Rev 15% · Id 15% · Pol 10% · Pay 10% · Beh 10%</span>
            <span>·</span>
            <span className="text-neutral-600">WebGuard v1.0.0</span>
          </div>
        </div>
      </footer>

    </div>
  );
}

const NavTab: React.FC<{
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  badge?: string;
  count?: number;
}> = ({ active, onClick, icon, label, badge, count }) => {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-md flex items-center gap-2 whitespace-nowrap transition-colors cursor-pointer text-xs ${
        active
          ? 'bg-blue-600 text-white font-semibold'
          : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100'
      }`}
    >
      {icon}
      <span>{label}</span>
      {badge && (
        <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${
          active ? 'bg-blue-700 text-white' : 'bg-neutral-100 text-neutral-600 border border-neutral-200'
        }`}>
          {badge}
        </span>
      )}
      {typeof count === 'number' && (
        <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${
          active ? 'bg-blue-700 text-white' : 'bg-neutral-100 text-neutral-600 border border-neutral-200'
        }`}>
          {count}
        </span>
      )}
    </button>
  );
};
