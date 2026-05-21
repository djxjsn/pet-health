'use client';

import { apiClient } from './client';
import type { Pet, PetAllergy, PetVaccination, PetOwnerShare } from '@/types';
import type { PetCreateRequest, PetUpdateRequest, PaginatedResponse } from '@/types/api';

export interface PetListResponse {
  items: Pet[];
  total: number;
  page: number;
  page_size: number;
}

export const petApi = {
  // ==================== 宠物 CRUD ====================
  async list(page = 1, pageSize = 10): Promise<PetListResponse> {
    return apiClient.get<PetListResponse>('/pets', { page, page_size: pageSize });
  },

  async getById(petId: string): Promise<Pet> {
    return apiClient.get<Pet>(`/pets/${petId}`);
  },

  async create(data: PetCreateRequest): Promise<Pet> {
    return apiClient.post<Pet>('/pets', data);
  },

  async update(petId: string, data: PetUpdateRequest): Promise<Pet> {
    return apiClient.put<Pet>(`/pets/${petId}`, data);
  },

  async delete(petId: string): Promise<void> {
    return apiClient.delete(`/pets/${petId}`);
  },

  // ==================== 过敏源 ====================
  async listAllergies(petId: string, activeOnly = true): Promise<PetAllergy[]> {
    return apiClient.get<PetAllergy[]>(`/pets/${petId}/allergies`, { active_only: activeOnly });
  },

  async addAllergy(petId: string, data: {
    allergen_name: string;
    allergen_type?: string;
    severity?: string;
    confirmed_by?: string;
    reaction_desc?: string;
    first_observed?: string;
  }): Promise<PetAllergy> {
    return apiClient.post<PetAllergy>(`/pets/${petId}/allergies`, data);
  },

  async deleteAllergy(petId: string, allergyId: string): Promise<void> {
    return apiClient.delete(`/pets/${petId}/allergies/${allergyId}`);
  },

  // ==================== 疫苗 ====================
  async listVaccinations(petId: string): Promise<PetVaccination[]> {
    return apiClient.get<PetVaccination[]>(`/pets/${petId}/vaccinations`);
  },

  async addVaccination(petId: string, data: {
    vaccine_name: string;
    vaccine_type?: string;
    dose_number?: string;
    administered_date: string;
    next_due_date?: string;
    vet_name?: string;
    hospital?: string;
    batch_number?: string;
    manufacturer?: string;
    notes?: string;
  }): Promise<PetVaccination> {
    return apiClient.post<PetVaccination>(`/pets/${petId}/vaccinations`, data);
  },

  async getUpcomingVaccinations(petId: string, days = 30): Promise<PetVaccination[]> {
    return apiClient.get<PetVaccination[]>(`/pets/${petId}/vaccinations/upcoming`, { days });
  },

  async deleteVaccination(petId: string, vaccinationId: string): Promise<void> {
    return apiClient.delete(`/pets/${petId}/vaccinations/${vaccinationId}`);
  },

  // ==================== 体重追踪 ====================
  async recordWeight(petId: string, weight: number, recordedAt?: string): Promise<{ status: string; weight: number; timestamp: string }> {
    return apiClient.post(`/pets/${petId}/weight`, { weight, recorded_at: recordedAt });
  },

  async getWeightHistory(petId: string, days = 90): Promise<Array<{ pet_id: string; weight: number; unit: string; timestamp: string }>> {
    return apiClient.get(`/pets/${petId}/weight/history`, { days });
  },

  // ==================== 共享权限 ====================
  async grantAccess(petId: string, data: {
    user_id: string;
    role?: string;
    permission?: string;
    expires_at?: string;
  }): Promise<PetOwnerShare> {
    return apiClient.post<PetOwnerShare>(`/pets/${petId}/share`, { pet_id: petId, ...data });
  },

  async listSharedUsers(petId: string): Promise<PetOwnerShare[]> {
    return apiClient.get<PetOwnerShare[]>(`/pets/${petId}/share`);
  },

  async revokeAccess(petId: string, userId: string): Promise<void> {
    return apiClient.delete(`/pets/${petId}/share/${userId}`);
  },

  async listSharedWithMe(): Promise<Pet[]> {
    return apiClient.get<Pet[]>('/pets/shared-with-me');
  },
};