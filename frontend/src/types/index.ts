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

export interface WeatherData {
  available: boolean;
  temperature?: number | null;
  humidity?: number | null;
  rainfall?: number | null;
  location?: string;
  timestamp?: number;
  source?: string;
  disclaimer?: string;
  message?: string;
}

export interface StructuredParameterAnalysis {
  name: string;
  value?: number | null;
  unit?: string | null;
  reference_min?: number | null;
  reference_max?: number | null;
  reference_text?: string | null;
  status: string;
  interpretation: string;
  action_item?: string | null;
  evidence_citations: {
    source: string;
    page?: number | null;
    guideline_summary: string;
  }[];
}

export interface FinalAnalysis {
  report_metadata: {
    report_id: string;
    report_name: string;
    lab_name: string;
    date: string;
  };
  executive_summary: {
    overall_health_status: string;
    key_findings: string[];
    primary_concerns: string[];
    priority_actions: string[];
  };
  parameters: StructuredParameterAnalysis[];
  crop_suitability: {
    status: string;
    crops: any[];
    explanation?: string;
  };
  provenance_audit: {
    analysis_timestamp: string;
    total_grounded_citations: number;
    guidelines_referenced: string[];
  };
}
