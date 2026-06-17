export interface Citation {
  source_url: string;
  title: string | null;
  reliability_score: number;
}

export type VerdictLabel = "supported" | "contradicted" | "insufficient";

export interface Verdict {
  claim: string;
  label: VerdictLabel;
  confidence: number;
  rationale: string;
  citations: Citation[];
}

export interface ReliabilitySignals {
  domain_reputation: number;
  recency: number;
  corroboration: number;
}

export interface EvidenceChunk {
  content: string;
  source_url: string;
  source_domain: string;
  title: string | null;
  published_date: string | null;
  provenance: "web" | "corpus";
  reliability_score: number;
  signals: ReliabilitySignals;
  stance: string | null;
}

export interface Claim {
  text: string;
  checkable: boolean;
  reason: string | null;
}

export interface CheckResponse {
  claims: Claim[];
  verdicts: Verdict[];
  evidence: EvidenceChunk[];
  latency_ms: number;
}

export type RuntimeMessage =
  | { type: "HIGHLIGHT_SELECTED"; text: string; url: string }
  | { type: "CHECK_RESULT"; payload: CheckResponse }
  | { type: "CHECK_ERROR"; error: string }
  | { type: "CHECK_LOADING" };
