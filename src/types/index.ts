/**
 * WebGuard Types & Data Contracts
 * Explainable Multi-Factor E-Commerce Fraud Risk Assessment
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface FactorScore {
  name: string;
  rawScore: number;     // 0 - 100
  weight: number;       // e.g. 0.20
  contribution: number; // rawScore * weight (rounded points)
  reason: string;
  subSignals?: string[];
  status: 'safe' | 'warning' | 'danger';
}

export interface FactorResults {
  domain: FactorScore;
  price: FactorScore;
  reviews: FactorScore;
  identity: FactorScore;
  policy: FactorScore;
  payment: FactorScore;
  behaviour: FactorScore;
}

export interface DetectedSignal {
  id: string;
  category: 'domain' | 'price' | 'reviews' | 'identity' | 'policy' | 'payment' | 'behaviour' | 'security';
  severity: 'low' | 'medium' | 'high' | 'critical' | 'safe';
  message: string;
  detail?: string;
  ruleTriggered?: string;
}

export interface AnalysisExplanation {
  factor: string;
  points: number;
  explanation: string;
  weightPercent: number;
  severity: 'info' | 'warning' | 'critical';
}

export interface AnalysisPayload {
  url: string;
  domain: string;
  pageTitle?: string;
  productName?: string;
  price?: number;
  currency?: string;
  originalPrice?: number;
  referenceMarketPrice?: number;
  reviews?: Array<{
    author?: string;
    text: string;
    rating?: number;
    date?: string;
  }>;
  rating?: number;
  reviewCount?: number;
  refundPolicyText?: string;
  returnTimelineDays?: number;
  paymentMethods?: string[];
  contactEmail?: string;
  contactPhone?: string;
  companyAddress?: string;
  isHttps?: boolean;
  domainAgeDays?: number;
  hasSuspiciousRedirects?: boolean;
  hasHiddenForms?: boolean;
  behaviourSignals?: string[];
  isCheckoutPage?: boolean;
}

export interface AnalysisResult {
  id: string;
  url: string;
  domain: string;
  productName: string;
  price: number;
  currency: string;
  riskScore: number; // 0 - 100
  riskLevel: RiskLevel;
  factors: FactorResults;
  explanations: AnalysisExplanation[];
  detectedSignals: DetectedSignal[];
  recommendation: string;
  timestamp: string;
  isPrePaymentTriggered: boolean;
  metadata?: {
    modelType: string;
    isolationForestAnomaly: boolean;
    nlpSimilarityScore: number;
    evaluationTimeMs: number;
  };
}

export interface HistoryItem {
  id: string;
  url: string;
  domain: string;
  productName: string;
  price: number;
  currency: string;
  riskScore: number;
  riskLevel: RiskLevel;
  timestamp: string;
  topReasons: string[];
  factorsSummary: {
    domain: number;
    price: number;
    reviews: number;
    identity: number;
    policy: number;
    payment: number;
    behaviour: number;
  };
}

export interface DemoTestCase {
  id: string;
  name: string;
  tagline: string;
  expectedRisk: RiskLevel;
  expectedScore: number;
  data: AnalysisPayload;
  description: string;
}
