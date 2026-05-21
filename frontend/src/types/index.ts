export interface User {
  user_id: string;
  phone?: string;
  email?: string;
  nickname?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Pet {
  pet_id: string;
  user_id: string;
  name: string;
  species: string;
  breed?: string;
  gender?: string;
  weight?: number;
  birth_date?: string;
  is_vaccinated: boolean;
  is_neutered: boolean;
  photo_url?: string;
  // P1 扩展字段
  microchip_id?: string;
  blood_type?: string;
  current_status?: string;
  diet_type?: string;
  spay_neuter_date?: string;
  emergency_contact?: string;
  source?: string;
  created_at: string;
  updated_at: string;
}

export interface PetAllergy {
  allergy_id: string;
  pet_id: string;
  allergen_name: string;
  allergen_type: string;
  severity: string;
  confirmed_by: string;
  reaction_desc?: string;
  first_observed?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PetVaccination {
  vaccination_id: string;
  pet_id: string;
  vaccine_name: string;
  vaccine_type: string;
  dose_number?: string;
  administered_date: string;
  next_due_date?: string;
  vet_name?: string;
  hospital?: string;
  batch_number?: string;
  manufacturer?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PetOwnerShare {
  id: string;
  pet_id: string;
  user_id: string;
  role: string;
  permission: string;
  granted_by?: string;
  granted_at: string;
  expires_at?: string;
  is_active: boolean;
  created_at: string;
}

export interface Message {
  message_id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  image_urls?: string[];
  created_at: string;
}

export interface Conversation {
  conversation_id: string;
  user_id: string;
  pet_id?: string;
  title?: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface HealthConsultation {
  consultation_id: string;
  pet_id: string;
  user_id: string;
  symptoms: string[];
  description?: string;
  image_urls?: string[];
  diagnosis_result?: Record<string, unknown>;
  recommendations?: string[];
  urgency_level?: number;
  status: 'pending' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface BehaviorAnalysis {
  analysis_id: string;
  pet_id: string;
  user_id: string;
  behavior_description: string;
  behavior_category?: string;
  behavior_category_result?: string;
  possible_causes?: string[];
  breed_analysis?: Record<string, unknown>;
  recommendations?: string[];
  severity_level?: number;
  status: 'pending' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}