
export type AnalysisStatus =
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed';

export interface AnalysisResponse {
  status: AnalysisStatus;
  evidenced_requirements: string[];
  unevidenced_requirements: string[];
  gaps: string[];
  resume_issues: string[];
  suggestions: string[];
}
