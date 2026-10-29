import React, { useState } from 'react';
import { AnalysisResult } from '../../types';
import {
  History,
  Search,
  Download,
  Trash2,
  ExternalLink,
  Lock
} from 'lucide-react';

interface AnalysisHistoryViewProps {
  historyItems: AnalysisResult[];
  onSelectHistoryItem: (item: AnalysisResult) => void;
  onClearHistory: () => void;
}

export const AnalysisHistoryView: React.FC<AnalysisHistoryViewProps> = ({
  historyItems,
  onSelectHistoryItem,
  onClearHistory,
}) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');

  const filteredItems = historyItems.filter(item => {
    const matchesSearch =
      item.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.productName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.id.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesRisk =
      riskFilter === 'ALL' || item.riskLevel.toUpperCase() === riskFilter;

    return matchesSearch && matchesRisk;
  });

  const handleExportJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(historyItems, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `webguard-audit-history-${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="flex flex-col gap-6 bg-white text-neutral-900">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-neutral-900 tracking-tight flex items-center gap-2.5">
            <History className="w-6 h-6 text-blue-600" />
            <span>Storefront Forensic Audit History</span>
          </h1>
          <p className="text-xs text-neutral-500 mt-1">
            Persisted scans with full 7-factor decomposition and timestamp verification.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExportJson}
            className="px-3.5 py-2 rounded-md bg-white border border-neutral-300 hover:bg-neutral-50 text-neutral-700 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer shadow-xs"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export History JSON</span>
          </button>
          <button
            onClick={onClearHistory}
            className="px-3.5 py-2 rounded-md bg-white border border-neutral-300 hover:bg-neutral-50 text-neutral-600 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar - Pure White */}
      <div className="bg-white border border-neutral-200 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-3 shadow-xs">
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-neutral-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search domain, product, ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-neutral-300 rounded-md text-xs text-neutral-900 placeholder:text-neutral-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
          />
        </div>

        {/* Risk Level Filter Buttons */}
        <div className="flex items-center gap-1 w-full md:w-auto overflow-x-auto text-xs">
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(lvl => (
            <button
              key={lvl}
              onClick={() => setRiskFilter(lvl)}
              className={`px-3 py-1.5 rounded-md font-mono transition-colors cursor-pointer text-xs ${
                riskFilter === lvl
                  ? 'bg-blue-600 text-white font-bold'
                  : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* History Items Table - Pure White */}
      <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-neutral-50 border-b border-neutral-200 text-neutral-500 font-mono text-[11px] uppercase">
              <tr>
                <th className="py-3 px-4">Storefront Domain</th>
                <th className="py-3 px-4">Product Inspected</th>
                <th className="py-3 px-4 text-right">Listed Price</th>
                <th className="py-3 px-4 text-center">Risk Score</th>
                <th className="py-3 px-4">Risk Severity</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-neutral-400">
                    No matching audit records found.
                  </td>
                </tr>
              ) : (
                filteredItems.map(item => (
                  <tr
                    key={item.id}
                    className="hover:bg-neutral-50 transition-colors group cursor-pointer"
                    onClick={() => onSelectHistoryItem(item)}
                  >
                    <td className="py-3 px-4">
                      <div className="font-mono font-bold text-neutral-900 group-hover:text-blue-700 flex items-center gap-1.5">
                        <Lock className="w-3 h-3 text-blue-600" />
                        <span>{item.domain}</span>
                      </div>
                      <div className="text-[10px] text-neutral-400 font-mono">{item.id}</div>
                    </td>

                    <td className="py-3 px-4 text-neutral-800 font-medium truncate max-w-[200px]">
                      {item.productName}
                    </td>

                    <td className="py-3 px-4 text-right font-mono font-semibold text-neutral-900">
                      {item.currency}{item.price?.toLocaleString()}
                    </td>

                    <td className="py-3 px-4 text-center">
                      <span className="font-mono font-bold text-sm text-neutral-900">
                        {item.riskScore}
                        <span className="text-[10px] text-neutral-400 font-normal"> / 100</span>
                      </span>
                    </td>

                    <td className="py-3 px-4">
                      <span className="inline-block px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-neutral-100 text-neutral-800 border border-neutral-200">
                        {item.riskLevel}
                      </span>
                    </td>

                    <td className="py-3 px-4 text-neutral-500 font-mono text-[11px]">
                      {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} · {new Date(item.timestamp).toLocaleDateString()}
                    </td>

                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectHistoryItem(item);
                        }}
                        className="px-2.5 py-1 rounded bg-white hover:bg-neutral-100 text-blue-700 text-xs font-semibold border border-neutral-300 transition-colors inline-flex items-center gap-1 cursor-pointer"
                      >
                        <span>Inspect</span>
                        <ExternalLink className="w-3 h-3 text-blue-600" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
