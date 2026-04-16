'use client';

import { apiClient } from './client';
import type { HealthConsultation } from '@/types';
import type {
  HealthConsultRequest,
  SymptomAnalysisRequest,
  PaginatedResponse,
} from '@/types/api';

export interface HealthConsultResult {
  consultation_id: string;
  pet_id: string;
  diagnosis_result: {
    possible_conditions: string[];
    severity: string;
  };
  recommendations: string[];
  urgency_level: number;
}

export interface SymptomAnalysisResult {
  possible_conditions: string[];
  urgency_level: number;
  recommendations: string[];
}

export type ConsultationRecord = HealthConsultation;

export interface HealthRecord {
  record_id: string;
  pet_id: string;
  record_type: string;
  title?: string;
  description?: string;
  value?: Record<string, unknown>;
  created_at: string;
}

export const healthApi = {
  async consult(data: HealthConsultRequest): Promise<HealthConsultResult> {
    return apiClient.post<HealthConsultResult>('/health/consult', data);
  },

  async analyzeSymptoms(data: SymptomAnalysisRequest): Promise<SymptomAnalysisResult> {
    return apiClient.post<SymptomAnalysisResult>('/health/analyze', data);
  },

  async listConsultations(skip = 0, limit = 20): Promise<HealthConsultation[]> {
    return apiClient.get<HealthConsultation[]>('/health/consultations', { skip, limit });
  },

  async getConsultation(consultationId: string): Promise<HealthConsultation> {
    return apiClient.get<HealthConsultation>(`/health/consultations/${consultationId}`);
  },

  async createHealthRecord(petId: string, data: unknown): Promise<HealthRecord> {
    return apiClient.post<HealthRecord>(`/health/records`, data, { params: { pet_id: petId } });
  },

  async getHealthRecords(petId: string, skip = 0, limit = 20): Promise<HealthRecord[]> {
    return apiClient.get<HealthRecord[]>(`/health/records/${petId}`, { skip, limit });
  },
};