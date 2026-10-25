
export type AnalysisStatus =
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed';

export interface AnalysisResponse {
  analysis_id?: string;
  status: AnalysisStatus;
  evidenced_requirements: string[];
  unevidenced_requirements: string[];
  gaps: string[];
  resume_issues: string[];
  suggestions: string[];
}
