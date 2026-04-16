'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Pet } from '@/types';

interface PetState {
  pets: Pet[];
  currentPetId: string | null;
  isLoading: boolean;

  currentPet: () => Pet | undefined;
  setPets: (pets: Pet[]) => void;
  addPet: (pet: Pet) => void;
  updatePet: (petId: string, updates: Partial<Pet>) => void;
  removePet: (petId: string) => void;
  setCurrentPetId: (petId: string | null) => void;
  setLoading: (loading: boolean) => void;
}

export const usePetStore = create<PetState>()(
  persist(
    (set, get) => ({
      pets: [],
      currentPetId: null,
      isLoading: false,

      currentPet: () => {
        const { pets, currentPetId } = get();
        return pets.find((p) => p.pet_id === currentPetId);
      },

      setPets: (pets) =>
        set({ pets }),

      addPet: (pet) =>
        set((state) => ({
          pets: [...state.pets, pet],
          currentPetId: state.currentPetId ?? pet.pet_id,
        })),

      updatePet: (petId, updates) =>
        set((state) => ({
          pets: state.pets.map((p) =>
            p.pet_id === petId
              ? { ...p, ...updates, updated_at: new Date().toISOString() }
              : p
          ),
        })),

      removePet: (petId) =>
        set((state) => {
          const remaining = state.pets.filter((p) => p.pet_id !== petId);
          return {
            pets: remaining,
            currentPetId:
              state.currentPetId === petId
                ? remaining[0]?.pet_id ?? null
                : state.currentPetId,
          };
        }),

      setCurrentPetId: (currentPetId) =>
        set({ currentPetId }),

      setLoading: (isLoading) =>
        set({ isLoading }),
    }),
    {
      name: 'pet-storage',
      partialize: (state) => ({
        pets: state.pets,
        currentPetId: state.currentPetId,
      }),
    }
  )
);
