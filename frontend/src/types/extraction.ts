/**
 * TypeScript Types for Extraction Data
 */

export type ExtractionStatus = 'pending' | 'processing' | 'completed' | 'failed';

export type OutputFormat = 'json' | 'csv' | 'xlsx';

export interface ExtractionRequest {
  url: string;
  prompt: string;
  output_format: OutputFormat;
}

export interface ExtractionJob {
  job_id: string;
  url: string;
  prompt: string;
  output_format: OutputFormat;
  status: ExtractionStatus;
  records_count?: number;
  data?: any[];
  error_message?: string;
  created_at: string;
  completed_at?: string;
  llm_provider_used?: string;
}

export interface ExtractionProgress {
  step: string;
  message: string;
}
