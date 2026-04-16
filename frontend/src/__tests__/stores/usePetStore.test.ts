import '@testing-library/jest-dom';
import { act } from '@testing-library/react';
import { usePetStore } from '@/stores/usePetStore';
import type { Pet } from '@/types';

const mockPets: Pet[] = [
  {
    pet_id: 'pet-001',
    user_id: 'user-001',
    name: '旺财',
    species: 'dog',
    breed: '金毛',
    gender: 'male',
    weight: 25.5,
    birth_date: '2022-03-15',
    is_vaccinated: true,
    is_neutered: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    pet_id: 'pet-002',
    user_id: 'user-001',
    name: '咪咪',
    species: 'cat',
    breed: '英短',
    gender: 'female',
    weight: 4.2,
    is_vaccinated: true,
    is_neutered: false,
    created_at: '2026-02-01T00:00:00Z',
    updated_at: '2026-02-01T00:00:00Z',
  },
];

describe('usePetStore', () => {
  beforeEach(() => {
    usePetStore.setState({
      pets: [],
      currentPetId: null,
      isLoading: false,
    });
  });

  describe('初始状态', () => {
    it('应该有正确的默认值', () => {
      const state = usePetStore.getState();
      expect(state.pets).toEqual([]);
      expect(state.currentPetId).toBeNull();
      expect(state.currentPet()).toBeUndefined();
    });
  });

  describe('setPets / addPet', () => {
    it('setPets 应设置宠物列表', () => {
      const { setPets } = usePetStore.getState();

      act(() => {
        setPets(mockPets);
      });

      expect(usePetStore.getState().pets).toEqual(mockPets);
    });

    it('addPet 应添加宠物到列表末尾', () => {
      const { addPet } = usePetStore.getState();

      act(() => {
        addPet(mockPets[0]);
        addPet(mockPets[1]);
      });

      const { pets } = usePetStore.getState();
      expect(pets).toHaveLength(2);
      expect(pets[0].name).toBe('旺财');
      expect(pets[1].name).toBe('咪咪');
    });

    it('添加第一个宠物时应自动设为当前宠物', () => {
      const { addPet } = usePetStore.getState();

      act(() => {
        addPet(mockPets[0]);
      });

      expect(usePetStore.getState().currentPetId).toBe('pet-001');
    });
  });

  describe('currentPet', () => {
    it('应返回当前选中的宠物', () => {
      const { setPets, setCurrentPetId } = usePetStore.getState();

      act(() => {
        setPets(mockPets);
        setCurrentPetId('pet-002');
      });

      expect(usePetStore.getState().currentPet()?.name).toBe('咪咪');
    });

    it('无当前宠物时应返回 undefined', () => {
      expect(usePetStore.getState().currentPet()).toBeUndefined();
    });
  });

  describe('removePet', () => {
    it('应从列表中移除指定宠物', () => {
      const { setPets, removePet } = usePetStore.getState();

      act(() => {
        setPets(mockPets);
        removePet('pet-001');
      });

      expect(usePetStore.getState().pets).toHaveLength(1);
      expect(usePetStore.getState().pets[0].pet_id).toBe('pet-002');
    });

    it('移除当前宠物时应自动切换到第一个剩余宠物', () => {
      const { setPets, setCurrentPetId, removePet } = usePetStore.getState();

      act(() => {
        setPets(mockPets);
        setCurrentPetId('pet-001');
        removePet('pet-001');
      });

      expect(usePetStore.getState().currentPetId).toBe('pet-002');
    });

    it('移除最后一个宠物时应将 currentPetId 设为 null', () => {
      const { addPet, removePet } = usePetStore.getState();

      act(() => {
        addPet(mockPets[0]);
        removePet('pet-001');
      });

      expect(usePetStore.getState().currentPetId).toBeNull();
      expect(usePetStore.getState().pets).toHaveLength(0);
    });
  });

  describe('updatePet', () => {
    it('应更新指定宠物的信息', () => {
      const { setPets, updatePet } = usePetStore.getState();

      act(() => {
        setPets(mockPets);
        updatePet('pet-001', { name: '小旺', weight: 28.0 });
      });

      const pet = usePetStore.getState().pets.find((p) => p.pet_id === 'pet-001');
      expect(pet?.name).toBe('小旺');
      expect(pet?.weight).toBe(28.0);
    });
  });
});
