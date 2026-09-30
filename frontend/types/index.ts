export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
}

export interface Finding {
  category: string;
  severity: string;
  confidence: number;
  rule_id: string;
  title: string;
  description: string;
  line?: number;
  column?: number;
  evidence?: string;
  recommendation?: string;
}

export interface TestRun {
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  execution_output?: string;
}

export interface AnalysisReport {
  analysis_id: string;
  status: string;
  overall_score: number;
  syntax_valid: boolean;
metrics: Record<string, unknown>;
  findings: Finding[];
  test_runs?: TestRun[];
  created_at: string;
}

