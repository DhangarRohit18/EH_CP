import React, { useEffect, useState } from 'react';
import { ExtensionPopupView } from './ExtensionPopupView';
import { AnalysisResult } from '../types';
import { analyzePayload } from '../../../frontend/src/engine/riskEngine';
import { DEMO_TEST_CASES } from '../../../frontend/src/engine/testCases';

declare const chrome: any;

export const ExtensionApp: React.FC = () => {
  const [result, setResult] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    // Attempt to query active Chrome tab
    if (typeof chrome !== 'undefined' && chrome.tabs && chrome.tabs.query) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs: any) => {
        const activeTab = tabs[0];
        if (activeTab && activeTab.id) {
          chrome.tabs.sendMessage(activeTab.id, { type: 'GET_PAGE_DATA' }, (response: any) => {
            if (response && response.data) {
              setResult(analyzePayload(response.data));
            } else {
              // Default to demo scenario if on arbitrary page
              setResult(analyzePayload(DEMO_TEST_CASES[0].data));
            }
          });
        } else {
          setResult(analyzePayload(DEMO_TEST_CASES[0].data));
        }
      });
    } else {
      // Local development fallback: load official demo case
      setResult(analyzePayload(DEMO_TEST_CASES[0].data));
    }
  }, []);

  const handleViewFullAnalysis = () => {
    if (typeof chrome !== 'undefined' && chrome.tabs) {
      chrome.tabs.create({ url: 'dashboard/index.html' });
    } else {
      window.open('#/analysis', '_blank');
    }
  };

  const handleContinueCarefully = () => {
    window.close();
  };

  return (
    <div className="w-[360px] min-h-[500px] bg-white">
      <ExtensionPopupView
        result={result}
        onViewFullAnalysis={handleViewFullAnalysis}
        onContinueCarefully={handleContinueCarefully}
        isCompact={true}
      />
    </div>
  );
};

export default ExtensionApp;
