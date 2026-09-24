import React from 'react';
import { AnalysisResult } from '../../types';
import {
  BarChart3,
  Globe,
  TrendingUp,
  PieChart,
  ShieldAlert
} from 'lucide-react';

interface DeveloperDashboardViewProps {
  historyItems: AnalysisResult[];
  onSelectAnalysis: (res: AnalysisResult) => void;
}

export const DeveloperDashboardView: React.FC<DeveloperDashboardViewProps> = ({
  historyItems,
  onSelectAnalysis,
}) => {
  const total = historyItems.length;
  const criticalCount = historyItems.filter(i => i.riskScore >= 80).length;
  const highCount = historyItems.filter(i => i.riskScore >= 60 && i.riskScore < 80).length;
  const mediumCount = historyItems.filter(i => i.riskScore >= 30 && i.riskScore < 60).length;
  const lowCount = historyItems.filter(i => i.riskScore < 30).length;

  // Average factor contributions
  const avgFactors = {
    domain: Math.round(historyItems.reduce((acc, cur) => acc + cur.factors.domain.contribution, 0) / (total || 1)),
    price: Math.round(historyItems.reduce((acc, cur) => acc + cur.factors.price.contribution, 0) / (total || 1)),
    reviews: Math.round(historyItems.reduce((acc, cur) => acc + cur.factors.reviews.contribution, 0) / (total || 1)),
    identity: Math.round(historyItems.reduce((acc, cur) => acc + cur.factors.identity.contribution, 0) / (total || 1)),
    policy: Math.round(historyItems.reduce((acc, cur) => acc + cur.factors.policy.contribution, 0) / (total || 1)),
    payment: Math.round(historyItems.reduce((acc, cur) => acc + cur.factors.payment.contribution, 0) / (total || 1)),
    behaviour: Math.round(historyItems.reduce((acc, cur) => acc + cur.factors.behaviour.contribution, 0) / (total || 1)),
  };

  return (
    <div className="flex flex-col gap-6 bg-white text-neutral-900">
      {/* Header */}
      <div className="border-b border-neutral-200 pb-5">
        <h1 className="text-2xl font-extrabold text-neutral-900 tracking-tight flex items-center gap-2.5">
          <BarChart3 className="w-6 h-6 text-blue-600" />
          <span>Security Operations & Analytics Dashboard</span>
        </h1>
        <p className="text-xs text-neutral-500 mt-1">
          Real-time threat intelligence telemetry, multi-factor weight diagnostics, and risk telemetry.
        </p>
      </div>

      {/* Metric Cards Row - Pure White with Single Blue Accent */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3.5">
        <MetricCard
          label="Total Scanned"
          value={total.toString()}
          subtext="Audited storefronts"
          icon={<Globe className="w-4 h-4 text-blue-600" />}
        />
        <MetricCard
          label="Critical Risk"
          value={criticalCount.toString()}
          subtext="Score ≥ 80 / 100"
          icon={<ShieldAlert className="w-4 h-4 text-neutral-500" />}
        />
        <MetricCard
          label="High Risk"
          value={highCount.toString()}
          subtext="Score 60 - 79"
          icon={<ShieldAlert className="w-4 h-4 text-neutral-500" />}
        />
        <MetricCard
          label="Medium Risk"
          value={mediumCount.toString()}
          subtext="Score 30 - 59"
          icon={<ShieldAlert className="w-4 h-4 text-neutral-500" />}
        />
        <MetricCard
          label="Low Risk (Safe)"
          value={lowCount.toString()}
          subtext="Score 0 - 29"
          icon={<ShieldAlert className="w-4 h-4 text-neutral-500" />}
        />
      </div>

      {/* Two Column Section: Risk Distribution & Factor Contribution Average */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Risk Severity Distribution Bar (5 Cols) */}
        <div className="lg:col-span-5 bg-white border border-neutral-200 rounded-xl p-6 flex flex-col justify-between shadow-xs">
          <div>
            <h3 className="text-sm font-bold text-neutral-900 uppercase tracking-wider mb-1 flex items-center gap-2">
              <PieChart className="w-4 h-4 text-blue-600" />
              Risk Severity Proportion
            </h3>
            <p className="text-xs text-neutral-500 mb-4">
              Distribution of storefronts across threat bands
            </p>

            {/* Segmented Horizontal Progress using single color gradients/tints */}
            <div className="w-full h-3 rounded-full bg-neutral-100 overflow-hidden flex border border-neutral-200 mb-4">
              <div
                style={{ width: `${(criticalCount / (total || 1)) * 100}%` }}
                className="bg-blue-800 h-full"
                title={`Critical: ${criticalCount}`}
              />
              <div
                style={{ width: `${(highCount / (total || 1)) * 100}%` }}
                className="bg-blue-600 h-full"
                title={`High: ${highCount}`}
              />
              <div
                style={{ width: `${(mediumCount / (total || 1)) * 100}%` }}
                className="bg-blue-400 h-full"
                title={`Medium: ${mediumCount}`}
              />
              <div
                style={{ width: `${(lowCount / (total || 1)) * 100}%` }}
                className="bg-blue-200 h-full"
                title={`Low: ${lowCount}`}
              />
            </div>

            {/* Legend items */}
            <div className="space-y-2 text-xs">
              <DistributionRow label="Critical (80-100)" count={criticalCount} total={total} color="bg-blue-800" />
              <DistributionRow label="High (60-79)" count={highCount} total={total} color="bg-blue-600" />
              <DistributionRow label="Medium (30-59)" count={mediumCount} total={total} color="bg-blue-400" />
              <DistributionRow label="Low (0-29)" count={lowCount} total={total} color="bg-blue-200" />
            </div>
          </div>

          <div className="pt-4 border-t border-neutral-200 text-[11px] text-neutral-500 mt-4 flex items-center justify-between">
            <span>Isolation Forest Anomaly Rate</span>
            <span className="font-mono text-neutral-900 font-bold">
              {Math.round(((criticalCount + highCount) / (total || 1)) * 100)}%
            </span>
          </div>
        </div>

        {/* Right: Average Factor Contribution Bar Chart (7 Cols) */}
        <div className="lg:col-span-7 bg-white border border-neutral-200 rounded-xl p-6 shadow-xs">
          <div className="flex items-center justify-between mb-1">
            <h3 className="text-sm font-bold text-neutral-900 uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-600" />
              Factor Contribution Average (Historical Corpus)
            </h3>
            <span className="text-[11px] font-mono text-neutral-400">Mean Points Added</span>
          </div>
          <p className="text-xs text-neutral-500 mb-4">
            Which factors triggered the most risk points across tested sites
          </p>

          <div className="space-y-2.5">
            {[
              { name: 'Price Anomaly', pts: avgFactors.price, max: 20, weight: '20%' },
              { name: 'Domain Credibility', pts: avgFactors.domain, max: 20, weight: '20%' },
              { name: 'Review Patterns', pts: avgFactors.reviews, max: 15, weight: '15%' },
              { name: 'Website Identity', pts: avgFactors.identity, max: 15, weight: '15%' },
              { name: 'Refund Policy', pts: avgFactors.policy, max: 10, weight: '10%' },
              { name: 'Payment Methods', pts: avgFactors.payment, max: 10, weight: '10%' },
              { name: 'Site Behaviour', pts: avgFactors.behaviour, max: 10, weight: '10%' },
            ].map((f, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-neutral-700 font-medium">{f.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-neutral-400 font-mono">Weight: {f.weight}</span>
                    <span className="font-mono font-bold text-blue-700 text-xs">+{f.pts} pts</span>
                  </div>
                </div>
                <div className="w-full h-2 rounded-full bg-neutral-100 overflow-hidden border border-neutral-200">
                  <div
                    className="h-full bg-blue-600 rounded-full"
                    style={{ width: `${Math.min(100, (f.pts / f.max) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Latest Analyzed Websites Feed */}
      <div className="bg-white border border-neutral-200 rounded-xl p-6 shadow-xs">
        <h3 className="text-sm font-bold text-neutral-900 uppercase tracking-wider mb-4">
          Latest Storefront Telemetry Feed
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {historyItems.slice(0, 3).map((item) => (
            <div
              key={item.id}
              onClick={() => onSelectAnalysis(item)}
              className="bg-neutral-50 border border-neutral-200 rounded-lg p-4 hover:border-blue-600 transition-all cursor-pointer space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono font-bold text-neutral-900 text-xs truncate max-w-[160px] group-hover:text-blue-700">
                  {item.domain}
                </span>
                <span className="font-mono font-bold text-sm text-neutral-900">
                  {item.riskScore} <span className="text-[10px] text-neutral-400">/ 100</span>
                </span>
              </div>
              <p className="text-xs text-neutral-600 truncate">{item.productName}</p>
              <div className="pt-2 border-t border-neutral-200 flex items-center justify-between text-[11px] text-neutral-500">
                <span>{item.riskLevel}</span>
                <span className="text-blue-600 text-[10px] group-hover:underline">Examine Audit →</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const MetricCard: React.FC<{
  label: string;
  value: string;
  subtext: string;
  icon: React.ReactNode;
}> = ({ label, value, subtext, icon }) => (
  <div className="bg-white border border-neutral-200 rounded-xl p-4 flex flex-col justify-between shadow-xs">
    <div className="flex items-center justify-between text-neutral-500 mb-2">
      <span className="text-[11px] font-mono uppercase tracking-wider">{label}</span>
      {icon}
    </div>
    <div>
      <div className="text-2xl sm:text-3xl font-extrabold font-mono tracking-tight text-neutral-900">
        {value}
      </div>
      <div className="text-[10px] text-neutral-400 font-mono mt-0.5">{subtext}</div>
    </div>
  </div>
);

const DistributionRow: React.FC<{
  label: string;
  count: number;
  total: number;
  color: string;
}> = ({ label, count, total, color }) => (
  <div className="flex items-center justify-between text-neutral-700">
    <div className="flex items-center gap-2">
      <span className={`w-2.5 h-2.5 rounded-full ${color}`} />
      <span>{label}</span>
    </div>
    <div className="font-mono text-neutral-500">
      <span className="text-neutral-900 font-bold">{count}</span> ({Math.round((count / (total || 1)) * 100)}%)
    </div>
  </div>
);
