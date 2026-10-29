import React, { useState } from 'react';
import { AnalysisResult, DemoTestCase } from '../../types';
import { DEMO_TEST_CASES } from '../../engine/testCases';
import { analyzePayload } from '../../engine/riskEngine';
import { ExtensionPopupView } from '../extension-view/ExtensionPopupView';
import { WarningOverlayModal } from './WarningOverlayModal';
import {
  Lock,
  RotateCw,
  ShoppingCart,
  Clock,
  Star,
  Truck,
  ShieldCheck,
  Building,
  Mail,
  Phone,
  Layers,
  ArrowRight
} from 'lucide-react';

interface StorefrontSimulatorProps {
  onSelectAnalysis: (result: AnalysisResult) => void;
  onOpenFullAnalysis: () => void;
  currentResult: AnalysisResult;
}

export const StorefrontSimulator: React.FC<StorefrontSimulatorProps> = ({
  onSelectAnalysis,
  onOpenFullAnalysis,
  currentResult,
}) => {
  const [selectedCaseId, setSelectedCaseId] = useState<string>('test-case-2-official');
  const [showExtensionPopup, setShowExtensionPopup] = useState<boolean>(true);
  const [showWarningModal, setShowWarningModal] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'product' | 'reviews' | 'policy' | 'payment'>('product');
  const [userDismissedForCurrent, setUserDismissedForCurrent] = useState<boolean>(false);

  const currentCase = DEMO_TEST_CASES.find(c => c.id === selectedCaseId) || DEMO_TEST_CASES[0];
  const payload = currentCase.data;

  const handleSelectCase = (testCase: DemoTestCase) => {
    setSelectedCaseId(testCase.id);
    setUserDismissedForCurrent(false);
    setShowWarningModal(false);
    const newResult = analyzePayload(testCase.data);
    onSelectAnalysis(newResult);
  };

  const handleProceedToCheckout = () => {
    // If high or critical risk, trigger the pre-payment security warning!
    if (currentResult.riskScore >= 60 && !userDismissedForCurrent) {
      setShowWarningModal(true);
    } else {
      alert(`Proceeding to checkout for ${payload.productName}. (Risk Score: ${currentResult.riskScore}/100)`);
    }
  };

  return (
    <div className="flex flex-col gap-6 bg-white">
      {/* Test Case Selector Bar - Pure White */}
      <div className="bg-white border border-neutral-200 rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
          <div>
            <h3 className="text-xs font-mono uppercase tracking-widest text-neutral-500 font-semibold">
              CYBERSECURITY EVALUATION SCENARIOS
            </h3>
            <p className="text-xs text-neutral-500 mt-0.5">
              Select an e-commerce test vector to evaluate risk detection:
            </p>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-medium">
            5 Test Vectors Loaded
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5">
          {DEMO_TEST_CASES.map(tc => {
            const isSelected = tc.id === selectedCaseId;

            return (
              <button
                key={tc.id}
                onClick={() => handleSelectCase(tc)}
                className={`p-2.5 rounded-lg border text-left transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-blue-50/70 border-blue-600 shadow-sm'
                    : 'bg-white border-neutral-200 hover:bg-neutral-50'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono text-neutral-500 truncate max-w-[120px]">
                    {tc.id === 'test-case-2-official' ? '★ OFFICIAL DEMO' : tc.expectedRisk}
                  </span>
                  <span className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded border ${
                    isSelected ? 'bg-blue-600 text-white border-blue-600' : 'bg-neutral-100 text-neutral-700 border-neutral-200'
                  }`}>
                    {tc.expectedScore}/100
                  </span>
                </div>
                <div className="text-xs font-semibold text-neutral-900 truncate">{tc.name}</div>
                <div className="text-[10px] text-neutral-500 truncate mt-0.5 font-mono">{tc.data.domain}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Dual-Pane Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left: Simulated Web Browser (8 Cols) - Pure White */}
        <div className="lg:col-span-8 bg-white border border-neutral-200 rounded-xl overflow-hidden shadow-sm flex flex-col">
          
          {/* Simulated Browser Chrome Top Bar */}
          <div className="bg-neutral-50 px-4 py-2.5 border-b border-neutral-200 flex items-center justify-between gap-3">
            <div className="flex items-center gap-1.5 shrink-0">
              <span className="w-2.5 h-2.5 rounded-full bg-neutral-300 inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-neutral-300 inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-neutral-300 inline-block" />
            </div>

            {/* Address Bar */}
            <div className="flex-1 max-w-xl mx-auto bg-white border border-neutral-200 rounded-md px-3 py-1 flex items-center justify-between text-xs text-neutral-700 font-mono shadow-xs">
              <div className="flex items-center gap-1.5 truncate">
                <Lock className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span className="text-neutral-400">https://</span>
                <span className="text-neutral-900 font-semibold">{payload.domain}</span>
                <span className="text-neutral-400 truncate">/products/{payload.productName?.toLowerCase().replace(/\s+/g, '-').slice(0, 20)}</span>
              </div>
              <RotateCw className="w-3.5 h-3.5 text-neutral-400 hover:text-neutral-700 cursor-pointer shrink-0 ml-2" />
            </div>

            {/* Browser Action: WebGuard Extension Button */}
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => setShowExtensionPopup(!showExtensionPopup)}
                className={`px-2.5 py-1 rounded-md border flex items-center gap-1.5 text-xs font-mono font-bold transition-all cursor-pointer ${
                  showExtensionPopup
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white border-neutral-300 text-neutral-700 hover:bg-neutral-50'
                }`}
                title="Toggle WebGuard Extension Popup"
              >
                <span>WebGuard</span>
                <span className={`px-1 rounded text-[10px] ${
                  showExtensionPopup ? 'bg-blue-800 text-white' : 'bg-blue-50 text-blue-700 border border-blue-200'
                }`}>
                  {currentResult.riskScore}
                </span>
              </button>
            </div>
          </div>

          {/* Storefront Page Content - Pure White */}
          <div className="p-6 bg-white flex-1">
            {/* Top Store Notice / Urgency Banner */}
            {payload.behaviourSignals && payload.behaviourSignals.length > 0 && (
              <div className="mb-4 bg-neutral-50 border border-neutral-300 rounded-lg p-2.5 flex items-center justify-between text-xs text-neutral-800">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-blue-600" />
                  <span className="font-semibold tracking-wide">
                    {payload.behaviourSignals[0]}
                  </span>
                </div>
                <span className="font-mono bg-neutral-200 px-2 py-0.5 rounded text-neutral-800 font-bold">
                  04:59 REMAINING
                </span>
              </div>
            )}

            {/* Store Header */}
            <div className="flex items-center justify-between border-b border-neutral-200 pb-4 mb-6">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white text-base">
                  {payload.domain.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h1 className="text-base font-bold text-neutral-900 tracking-tight">{payload.domain}</h1>
                  <p className="text-[11px] text-neutral-500">Online Storefront Catalog</p>
                </div>
              </div>
              <div className="flex items-center gap-3 text-xs text-neutral-500">
                <span className="flex items-center gap-1"><Truck className="w-3.5 h-3.5 text-neutral-400" /> Fast Shipping</span>
                <span className="flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5 text-neutral-400" /> Buyer Protection</span>
              </div>
            </div>

            {/* Product Hero Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-6 border-b border-neutral-200">
              
              {/* Product Visual Box */}
              <div className="aspect-square bg-neutral-50 border border-neutral-200 rounded-lg flex flex-col items-center justify-center p-6 relative">
                <div className="w-32 h-32 rounded-xl bg-white border border-neutral-200 flex items-center justify-center text-4xl shadow-xs">
                  📱
                </div>
                <div className="mt-4 text-center">
                  <span className="text-xs font-semibold text-neutral-800">{payload.productName}</span>
                  <div className="text-[10px] text-neutral-500 mt-1">Official Boxed Edition · Direct Dispatch</div>
                </div>

                {/* Discount Badge */}
                {payload.originalPrice && payload.price && payload.originalPrice > payload.price && (
                  <span className="absolute top-3 left-3 bg-neutral-900 text-white font-mono font-bold text-xs px-2 py-0.5 rounded shadow-xs">
                    -{Math.round(((payload.originalPrice - payload.price) / payload.originalPrice) * 100)}% OFF
                  </span>
                )}
              </div>

              {/* Product Info & Pricing */}
              <div className="flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex items-center text-blue-600 text-xs">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star key={i} className={`w-3.5 h-3.5 ${i < Math.floor(payload.rating || 5) ? 'fill-blue-600' : 'text-neutral-300'}`} />
                      ))}
                    </div>
                    <span className="text-xs font-mono text-neutral-700 font-bold">{payload.rating}</span>
                    <span className="text-xs text-neutral-500">({payload.reviewCount} reviews)</span>
                  </div>

                  <h2 className="text-lg font-bold text-neutral-900 leading-snug mb-3">
                    {payload.productName}
                  </h2>

                  {/* Pricing Box */}
                  <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-4 mb-4">
                    <div className="flex items-baseline gap-3">
                      <span className="text-3xl font-extrabold text-neutral-900 font-mono">
                        {payload.currency}{payload.price?.toLocaleString()}
                      </span>
                      {payload.originalPrice && (
                        <span className="text-sm text-neutral-400 line-through font-mono">
                          M.R.P. {payload.currency}{payload.originalPrice?.toLocaleString()}
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-neutral-600 font-medium mt-1">
                      Includes all import taxes. Free Express Doorstep Delivery.
                    </div>
                  </div>

                  {/* Highlights */}
                  <div className="space-y-1.5 text-xs text-neutral-600 mb-4">
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                      <span>100% Brand Sealed in Original Manufacturer Box</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                      <span>Instant IMEI Registration with 1-Year Global Warranty</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                      <span>{payload.paymentMethods?.[0] || 'Standard checkout'}</span>
                    </div>
                  </div>
                </div>

                {/* Pre-Payment Action Trigger */}
                <div className="pt-2 flex flex-col gap-2">
                  <button
                    onClick={handleProceedToCheckout}
                    className="w-full py-3 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs tracking-wider uppercase transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-sm"
                  >
                    <ShoppingCart className="w-4 h-4" />
                    <span>BUY NOW · PROCEED TO CHECKOUT</span>
                  </button>

                  <p className="text-[10px] text-neutral-500 text-center">
                    Clicking "Buy Now" triggers WebGuard's pre-payment warning interception.
                  </p>
                </div>
              </div>
            </div>

            {/* Deep-Dive Tabs */}
            <div className="mt-6">
              <div className="flex items-center gap-2 border-b border-neutral-200 text-xs font-semibold mb-4">
                <button
                  onClick={() => setActiveTab('product')}
                  className={`pb-2 px-1 border-b-2 transition-colors cursor-pointer ${
                    activeTab === 'product'
                      ? 'border-blue-600 text-blue-700'
                      : 'border-transparent text-neutral-500 hover:text-neutral-800'
                  }`}
                >
                  Merchant Info
                </button>
                <button
                  onClick={() => setActiveTab('reviews')}
                  className={`pb-2 px-1 border-b-2 transition-colors cursor-pointer ${
                    activeTab === 'reviews'
                      ? 'border-blue-600 text-blue-700'
                      : 'border-transparent text-neutral-500 hover:text-neutral-800'
                  }`}
                >
                  Customer Reviews ({payload.reviews?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('policy')}
                  className={`pb-2 px-1 border-b-2 transition-colors cursor-pointer ${
                    activeTab === 'policy'
                      ? 'border-blue-600 text-blue-700'
                      : 'border-transparent text-neutral-500 hover:text-neutral-800'
                  }`}
                >
                  Refund & Return Policy
                </button>
                <button
                  onClick={() => setActiveTab('payment')}
                  className={`pb-2 px-1 border-b-2 transition-colors cursor-pointer ${
                    activeTab === 'payment'
                      ? 'border-blue-600 text-blue-700'
                      : 'border-transparent text-neutral-500 hover:text-neutral-800'
                  }`}
                >
                  Accepted Payment Rails
                </button>
              </div>

              {/* Tab Contents */}
              {activeTab === 'product' && (
                <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <div className="flex items-start gap-2">
                    <Building className="w-4 h-4 text-neutral-400 shrink-0 mt-0.5" />
                    <div>
                      <div className="text-neutral-500 text-[10px] uppercase font-mono">Company Address</div>
                      <div className="text-neutral-800 font-medium">{payload.companyAddress || 'None provided'}</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Mail className="w-4 h-4 text-neutral-400 shrink-0 mt-0.5" />
                    <div>
                      <div className="text-neutral-500 text-[10px] uppercase font-mono">Support Email</div>
                      <div className="text-neutral-800 font-mono font-medium">{payload.contactEmail || 'None provided'}</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Phone className="w-4 h-4 text-neutral-400 shrink-0 mt-0.5" />
                    <div>
                      <div className="text-neutral-500 text-[10px] uppercase font-mono">Support Phone</div>
                      <div className="text-neutral-800 font-mono font-medium">{payload.contactPhone || 'None provided'}</div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'reviews' && (
                <div className="space-y-2">
                  {payload.reviews?.map((r, i) => (
                    <div key={i} className="bg-neutral-50 p-3 rounded-lg border border-neutral-200 text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-neutral-900">{r.author || `Verified Buyer #${i + 1}`}</span>
                        <div className="flex items-center text-blue-600 text-[10px]">
                          {'★'.repeat(r.rating || 5)}
                        </div>
                      </div>
                      <p className="text-neutral-600">{r.text}</p>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'policy' && (
                <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 text-xs text-neutral-800 leading-relaxed font-mono">
                  {payload.refundPolicyText}
                </div>
              )}

              {activeTab === 'payment' && (
                <div className="bg-neutral-50 p-4 rounded-lg border border-neutral-200 space-y-2 text-xs">
                  <div className="text-neutral-500 text-[11px] mb-1">Declared Gateway & Payment Methods:</div>
                  <div className="flex flex-wrap gap-2">
                    {payload.paymentMethods?.map((m, i) => (
                      <span key={i} className="px-2.5 py-1 rounded bg-white border border-neutral-200 text-neutral-800 font-mono">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

          </div>
        </div>

        {/* Right: Live Extension Popup Inspector (4 Cols) */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-neutral-800">
                Extension Popup View
              </h3>
            </div>
            <span className="text-[10px] text-neutral-400 font-mono">Manifest V3</span>
          </div>

          {/* Render the Extension Popup */}
          <div className="flex justify-center">
            <ExtensionPopupView
              result={currentResult}
              onViewFullAnalysis={onOpenFullAnalysis}
              onContinueCarefully={() => setShowWarningModal(false)}
            />
          </div>

          {/* Explanation Card */}
          <div className="bg-white border border-neutral-200 rounded-xl p-4 text-xs text-neutral-600 space-y-2 shadow-xs">
            <div className="flex items-center gap-1.5 text-neutral-800 font-bold uppercase tracking-wider text-[10px]">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
              Why WebGuard is different
            </div>
            <p className="text-[11px] leading-relaxed text-neutral-600">
              Unlike static domain blocklists that only look at URLs, WebGuard runs a multi-factor risk engine analyzing live prices, reviews, refund policies, and payment terms in real time before checkout.
            </p>
            <button
              onClick={onOpenFullAnalysis}
              className="text-blue-600 hover:text-blue-800 font-semibold text-xs flex items-center gap-1 cursor-pointer pt-1"
            >
              <span>Explore 7-Factor Forensic Report</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

      </div>

      {/* Security Pre-Payment Warning Modal */}
      {showWarningModal && (
        <WarningOverlayModal
          result={currentResult}
          onGoBack={() => setShowWarningModal(false)}
          onViewDetails={() => {
            setShowWarningModal(false);
            onOpenFullAnalysis();
          }}
          onDismiss={() => {
            setShowWarningModal(false);
            setUserDismissedForCurrent(true);
          }}
        />
      )}
    </div>
  );
};
