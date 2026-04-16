'use client';

import { apiClient } from './client';
import type { Pet } from '@/types';
import type { PetCreateRequest, PetUpdateRequest, PaginatedResponse } from '@/types/api';

export interface PetListResponse {
  items: Pet[];
  total: number;
  page: number;
  page_size: number;
}

export const petApi = {
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
};