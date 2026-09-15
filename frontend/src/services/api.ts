import type { ReportAnalysis, CropSuitabilityResponse, ChatResponse } from '../types';

const API_BASE = '/api';

export const api = {
  async healthCheck() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async uploadReport(file: File): Promise<{ report_id: string; filename: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/reports/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload report');
    }
    return res.json();
  },

  async analyzeReport(reportId: string): Promise<ReportAnalysis> {
    const res = await fetch(`${API_BASE}/reports/${reportId}/analyze`, {
      method: 'POST',
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to analyze report');
    }
    return res.json();
  },

  async loadDemoDuffyRear(): Promise<ReportAnalysis> {
    const res = await fetch(`${API_BASE}/reports/demo/duffy-rear`, {
      method: 'POST',
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to load demo report');
    }
    return res.json();
  },

  async getReportEvidence(reportId: string) {
    const res = await fetch(`${API_BASE}/reports/${reportId}/evidence`);
    if (!res.ok) throw new Error('Failed to fetch evidence');
    return res.json();
  },

  async getCropRecommendations(
    reportId: string,
    inputs: Record<string, number | undefined>
  ): Promise<CropSuitabilityResponse> {
    const res = await fetch(`${API_BASE}/reports/${reportId}/crops`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputs),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to fetch crop suitability');
    }
    return res.json();
  },

  async askSoilAi(reportId: string, question: string): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/reports/${reportId}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to answer question');
    }
    return res.json();
  },
};
