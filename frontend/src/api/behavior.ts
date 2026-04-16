'use client';

import { apiClient } from './client';
import type { BehaviorAnalysis } from '@/types';
import type {
  BehaviorAnalyzeRequest,
  TrainingRecommendationRequest,
} from '@/types/api';

export interface BehaviorAnalyzeResult {
  analysis_id: string;
  pet_id: string;
  behavior_category?: string;
  possible_causes: string[];
  breed_analysis?: Record<string, unknown>;
  recommendations: string[];
  severity_level: number;
}

export interface TrainingRecommendationResult {
  pet_id: string;
  pet_name?: string;
  behavior_category?: string;
  breed_specific_advice: string[];
  training_plan: Array<{
    step: number;
    title: string;
    description: string;
    duration_days?: number;
  }>;
  tips: string[];
}

export const behaviorApi = {
  async analyze(data: BehaviorAnalyzeRequest): Promise<BehaviorAnalyzeResult> {
    return apiClient.post<BehaviorAnalyzeResult>('/behavior/analyze', data);
  },

  async listHistory(skip = 0, limit = 20): Promise<BehaviorAnalysis[]> {
    return apiClient.get<BehaviorAnalysis[]>('/behavior/history', { skip, limit });
  },

  async listPetHistory(petId: string, skip = 0, limit = 20): Promise<BehaviorAnalysis[]> {
    return apiClient.get<BehaviorAnalysis[]>(`/behavior/history/${petId}`, { skip, limit });
  },

  async getTrainingRecommendations(data: TrainingRecommendationRequest): Promise<TrainingRecommendationResult> {
    return apiClient.post<TrainingRecommendationResult>('/behavior/training', data);
  },
};