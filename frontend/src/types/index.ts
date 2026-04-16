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
  gender: 'male' | 'female';
  weight?: number;
  birth_date?: string;
  is_vaccinated: boolean;
  is_neutered: boolean;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
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
