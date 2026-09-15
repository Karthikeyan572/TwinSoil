export interface Evidence {
  source: string;
  page?: number | null;
  text: string;
  relevance: string;
}

export interface SoilParameter {
  id?: string;
  name: string;
  value?: number | null;
  unit?: string | null;
  reference_min?: number | null;
  reference_max?: number | null;
  reference_text?: string | null;
  lab_status?: string | null;
  computed_status?: string | null;
  status?: string | null;
  explanation?: string;
  why_it_matters?: string;
  confidence?: string;
  evidence?: Evidence[];
}

export interface PipelineStep {
  step: string;
  detail: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
}

export interface Summary {
  overall_observation: string;
  key_findings: string[];
}

export interface CropPrediction {
  crop: string;
  probability: number;
  confidence_label: string;
  disclaimer: string;
}

export interface CropSuitabilityResponse {
  status: 'READY' | 'INSUFFICIENT_INPUTS';
  missing_inputs?: string[];
  current_inputs?: Record<string, number>;
  inputs?: Record<string, number>;
  predictions?: CropPrediction[];
  explanation?: string;
  limitations?: string[];
  message?: string;
}

export interface ReportAnalysis {
  report_id: string;
  summary: Summary;
  parameters: SoilParameter[];
  crop_suitability: {
    enabled: boolean;
    status: string;
    missing_inputs: string[];
    crops: any[];
  };
  pipeline_steps?: PipelineStep[];
}

export interface ChatCitation {
  source: string;
  page?: number | null;
  text: string;
}

export interface ChatResponse {
  question: string;
  answer: string;
  citations: ChatCitation[];
  provider?: string;
}
