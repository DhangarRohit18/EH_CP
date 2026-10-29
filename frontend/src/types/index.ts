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

// ============================================================================
// Technical Security Intelligence Types
// ============================================================================

export interface SecurityFinding {
  id: string;
  finding_id: string;
  category: string;
  title: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  confidence: number;
  evidence: string;
  security_impact: string;
  remediation: string;
  verification_status: string;
  owasp_category?: string;
  affected_url?: string;
}

export interface CVEMatch {
  id?: string;
  cve_id: string;
  source: string;
  cvss_score: number;
  severity: string;
  description: string;
  affected_product: string;
  affected_version?: string;
  verification_status: 'potentially_affected' | 'verified_vulnerable' | 'unaffected';
  reference_url?: string;
}

export interface TechItem {
  name: string;
  category: 'web_server' | 'runtime' | 'cms' | 'frontend_framework' | 'client_library' | 'infrastructure';
  version?: string;
  confidence: number;
  evidence: string;
}

export interface SecurityAssessmentResult {
  id: string;
  target_url: string;
  domain: string;
  technical_security_score: number;
  security_posture_level: string;
  scan_duration_ms: number;
  findings: SecurityFinding[];
  technologies: TechItem[];
  cve_matches: CVEMatch[];
  owasp_summary?: Record<string, any>;
  dns_telemetry?: Record<string, any>;
  tls_telemetry?: Record<string, any>;
  rdap_telemetry?: Record<string, any>;
  timestamp: string;
}

export interface ScopeItem {
  id: string;
  domain: string;
  is_authorized: boolean;
  active_probing_allowed: boolean;
  authorized_by: string;
  environment: string;
  created_at: string;
}

export interface AssetItem {
  id: string;
  domain: string;
  hostname: string;
  asset_type: string;
  ip_address?: string;
  port?: number;
  discovery_method: string;
  first_observed: string;
}

export interface DevSecFinding {
  file: string;
  line: number;
  rule_id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  code_snippet: string;
  remediation: string;
}

export interface DevSecResult {
  scan_timestamp: string;
  repository_status: string;
  scanned_files_count: number;
  findings: DevSecFinding[];
  dependencies: {
    python: { total_checked: number; audited_with: string };
    npm: { total_checked: number; audited_with: string };
  };
}
