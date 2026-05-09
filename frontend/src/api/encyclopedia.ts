import { apiClient } from './client';
import type { ApiResponse } from '@/types/api';

// ============================================================
// Types
// ============================================================

export interface BreedFeatures {
  origin: string;
  size: string;
  weight: string;
  lifespan: string;
  coat: string;
  colors: string[];
}

export interface BreedCare {
  exercise: string;
  grooming: string;
  diet: string;
  training: string;
}

export interface BreedSummary {
  id: string;
  name: string;
  english_name: string;
  species: string;
  summary: string;
  image_emoji: string;
  popularity: number;
}

export interface BreedDetail extends BreedSummary {
  category: string;
  description: string;
  features: BreedFeatures;
  personality: string[];
  care_requirements: BreedCare;
  health_issues: string[];
  suitable_for: string[];
}

export interface HealthConditionSummary {
  id: string;
  name: string;
  species: string;
  category: string;
  severity: string;
  image_emoji: string;
}

export interface HealthCondition extends HealthConditionSummary {
  description: string;
  symptoms: string[];
  urgent_symptoms: string[];
  possible_causes: string[];
  treatment: string[];
  home_care: string[];
  prevention: string[];
}

export interface HealthCategoryGroup {
  category: string;
  category_label: string;
  conditions: HealthConditionSummary[];
}

export const SEVERITY_CONFIG: Record<string, { label: string; variant: 'safe' | 'warning' | 'danger' | 'emergency' }> = {
  mild: { label: '轻微', variant: 'safe' },
  moderate: { label: '中等', variant: 'warning' },
  severe: { label: '严重', variant: 'danger' },
  emergency: { label: '紧急', variant: 'emergency' },
};

export const CATEGORY_CONFIG: Record<string, { label: string; emoji: string }> = {
  digestive: { label: '消化系统', emoji: '🍽️' },
  respiratory: { label: '呼吸系统', emoji: '🫁' },
  skin: { label: '皮肤系统', emoji: '🧴' },
  urinary: { label: '泌尿系统', emoji: '💧' },
  eye: { label: '眼部疾病', emoji: '👁️' },
  dental: { label: '口腔疾病', emoji: '🦷' },
  parasite: { label: '寄生虫', emoji: '🪱' },
  infectious: { label: '传染病', emoji: '🦠' },
  skeletal: { label: '骨骼关节', emoji: '🦴' },
};

// ============================================================
// API Functions
// ============================================================

export const encyclopediaApi = {
  getBreeds: async (species: string): Promise<BreedSummary[]> => {
    const res = await apiClient.get<ApiResponse<{ species: string; breeds: BreedSummary[] }>>(
      `/api/v1/encyclopedia/breeds/${species}`
    );
    return res.data?.breeds || [];
  },

  getBreedDetail: async (breedId: string): Promise<BreedDetail | null> => {
    const res = await apiClient.get<ApiResponse<{ breed: BreedDetail }>>(
      `/api/v1/encyclopedia/breed/${breedId}`
    );
    return res.data?.breed || null;
  },

  getHealthConditions: async (species: string): Promise<HealthCategoryGroup[]> => {
    const res = await apiClient.get<ApiResponse<{ species: string; categories: HealthCategoryGroup[] }>>(
      `/api/v1/encyclopedia/health/${species}`
    );
    return res.data?.categories || [];
  },

  getHealthDetail: async (conditionId: string): Promise<HealthCondition | null> => {
    const res = await apiClient.get<ApiResponse<{ condition: HealthCondition }>>(
      `/api/v1/encyclopedia/health/detail/${conditionId}`
    );
    return res.data?.condition || null;
  },

  searchKnowledge: async (query: string): Promise<{ breeds: BreedSummary[]; conditions: HealthConditionSummary[] }> => {
    const res = await apiClient.get<ApiResponse<{ breeds: BreedSummary[]; conditions: HealthConditionSummary[] }>>(
      `/api/v1/encyclopedia/search`,
      { query }
    );
    return res.data || { breeds: [], conditions: [] };
  },
};
