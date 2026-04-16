'use client';

import { useState, useRef, useEffect, memo } from 'react';
import { Pet } from '@/types';

interface PetSwitcherProps {
  pets: Pet[];
  currentPetId?: string;
  onPetChange?: (petId: string) => void;
  onAddNew?: () => void;
  className?: string;
}

function PetSwitcher({
  pets,
  currentPetId,
  onPetChange,
  onAddNew,
  className = '',
}: PetSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentPet = pets.find(pet => pet.pet_id === currentPetId) || pets[0];

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close on escape key
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const handleSelectPet = (petId: string) => {
    onPetChange?.(petId);
    setIsOpen(false);
  };

  const getPetEmoji = (species: string): string => {
    const speciesLower = species.toLowerCase();
    if (speciesLower.includes('dog') || speciesLower.includes('犬')) return '🐕';
    if (speciesLower.includes('cat') || speciesLower.includes('猫')) return '🐱';
    if (speciesLower.includes('bird') || speciesLower.includes('鸟')) return '🐦';
    if (speciesLower.includes('rabbit') || speciesLower.includes('兔')) return '🐰';
    if (speciesLower.includes('hamster') || speciesLower.includes('仓鼠')) return '🐹';
    if (speciesLower.includes('fish') || speciesLower.includes('鱼')) return '🐟';
    return '🐾';
  };

  const formatAge = (birthDate?: string): string => {
    if (!birthDate) return '';
    
    const birth = new Date(birthDate);
    const now = new Date();
    const months = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth());
    
    if (months < 1) return '新生儿';
    if (months < 12) return `${months}个月`;
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;
    return remainingMonths > 0 ? `${years}岁${remainingMonths}月` : `${years}岁`;
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors
          ${isOpen
            ? 'bg-gray-100 text-gray-900'
            : 'text-gray-700 hover:bg-gray-50'
          }
        `}
      >
        {currentPet && (
          <>
            <span className="text-lg">{getPetEmoji(currentPet.species)}</span>
            <span className="max-w-[100px] truncate font-semibold">{currentPet.name}</span>
          </>
        )}
        
        {!currentPet && (
          <>
            <span className="text-lg">🐾</span>
            <span className="text-gray-500">选择宠物</span>
          </>
        )}

        <svg
          className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute left-0 top-full z-50 mt-2 w-72 origin-top-left rounded-xl border border-gray-200 bg-white py-2 shadow-lg">
          {/* Current Pet Section */}
          <div className="px-3 py-2">
            <p className="mb-2 px-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
              当前对话宠物
            </p>
            
            {pets.map(pet => (
              <button
                key={pet.pet_id}
                onClick={() => handleSelectPet(pet.pet_id)}
                className={`
                  flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left transition-colors
                  ${pet.pet_id === currentPet?.pet_id
                    ? 'bg-primary-50 text-primary-700 ring-1 ring-primary-200'
                    : 'hover:bg-gray-50 text-gray-700'
                  }
                `}
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-xl">
                  {getPetEmoji(pet.species)}
                </span>
                
                <div className="flex-1 min-w-0">
                  <p className={`font-medium ${pet.pet_id === currentPet?.pet_id ? 'text-primary-700' : ''}`}>
                    {pet.name}
                    {pet.pet_id === currentPet?.pet_id && (
                      <span className="ml-1.5 text-xs font-normal text-primary-500">(当前)</span>
                    )}
                  </p>
                  <p className="text-xs text-gray-500">
                    {pet.breed || pet.species}
                    {formatAge(pet.birth_date) && ` · ${formatAge(pet.birth_date)}`}
                  </p>
                </div>

                {pet.pet_id === currentPet?.pet_id && (
                  <svg className="h-5 w-5 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            ))}
          </div>

          {/* Divider */}
          <div className="my-2 border-t border-gray-100" />

          {/* Other Pets Section - only show if more than one pet */}
          {pets.length > 0 && (
            <div className="px-3 py-2">
              <button
                onClick={() => {
                  onAddNew?.();
                  setIsOpen(false);
                }}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-lg">
                  +
                </span>
                <span className="font-medium">添加新宠物</span>
              </button>
            </div>
          )}

          {/* Empty State */}
          {pets.length === 0 && (
            <div className="px-4 py-6 text-center">
              <p className="text-sm text-gray-500">还没有添加宠物</p>
              <button
                onClick={() => {
                  onAddNew?.();
                  setIsOpen(false);
                }}
                className="mt-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                添加第一只宠物
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default memo(PetSwitcher);
