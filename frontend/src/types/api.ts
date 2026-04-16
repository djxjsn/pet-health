export interface ApiError {
  detail: string;
  status?: number;
  code?: string;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  phone: string;
  email?: string;
  password: string;
}

export interface ForgotPasswordRequest {
  phone: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface PetCreateRequest {
  name: string;
  species: string;
  breed?: string;
  gender?: 'male' | 'female';
  weight?: number;
  birth_date?: string;
  is_vaccinated?: boolean;
  is_neutered?: boolean;
  avatar_url?: string;
}

export interface PetUpdateRequest {
  name?: string;
  breed?: string;
  gender?: 'male' | 'female';
  weight?: number;
  birth_date?: string;
  is_vaccinated?: boolean;
  is_neutered?: boolean;
  avatar_url?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  pet_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  relevant_context?: Array<{
    source: string;
    content: string;
    relevance: number;
  }>;
}

export interface ConversationCreateRequest {
  pet_id?: string;
  title?: string;
}

// ========== Health Consultation Types (OPT-H-03 Structured) ==========

export interface ConditionItem {
  name: string;
  description: string;
  confidence: number;
}

export interface SymptomAnalysisResult {
  possible_conditions: ConditionItem[];
  recommendations: string[];
  severity: '轻微' | '中等' | '严重' | '紧急';
  vet_recommended: boolean;
}

export interface HealthConsultRequest {
  pet_id: string;
  symptoms: string[];
  description?: string;
  image_urls?: string[];
}

export interface SymptomAnalysisRequest {
  pet_id: string;
  symptoms: string[];
  description?: string;
}

export interface HealthConsultResult {
  pet_id: string;
  pet_name: string;
  symptoms: string[];
  diagnosis_result: SymptomAnalysisResult;
  urgency_level: number;
  urgency_reasoning: string;
  recommendations: string[];
  disclaimer: string;
}

export interface HealthRecord {
  record_id: string;
  pet_id: string;
  record_type: string;
  symptoms: string[];
  diagnosis: string | null;
  prescription: string | null;
  vet_name: string | null;
  hospital: string | null;
  record_date: string;
  next_checkup_date: string | null;
  notes: string | null;
}

export interface ConsultationRecord {
  consultation_id: string;
  pet_id: string;
  user_id: string;
  symptoms: string[];
  diagnosis: string | null;
  recommendations: string[];
  severity: string;
  created_at: string;
  updated_at: string;
}

// ========== Behavior Analysis Types (OPT-B-03 Structured) ==========

export interface BehaviorCauseItem {
  cause: string;
  probability: number;
  category: 'breed' | 'age' | 'environment' | 'health' | 'training';
}

export interface BehaviorAnalysisResult {
  possible_causes: BehaviorCauseItem[];
  recommendations: string[];
}

export interface BehaviorAnalyzeRequest {
  pet_id: string;
  behavior_description: string;
  behavior_category?: string;
}

export interface BehaviorAnalyzeResult {
  pet_id: string;
  pet_name: string;
  behavior_category: string;
  possible_causes: BehaviorCauseItem[];
  breed_analysis: {
    breed: string;
    energy_level: string;
    traits: string[];
    common_issues: string[];
    exercise_need: string;
    matched_issues: string[];
    relevance: 'high' | 'low' | 'unknown';
  };
  recommendations: string[];
  severity_level: number;
  disclaimer: string;
}

export interface TrainingRecommendationRequest {
  pet_id: string;
  behavior_category: string;
}

export interface TrainingRecommendationResult {
  pet_id: string;
  pet_name: string;
  behavior_category: string;
  breed_specific_advice: string[];
  training_plan: Array<{
    name: string;
    description: string;
    duration: string;
  }>;
  tips: string[];
  disclaimer: string;
}

// ========== WebSocket Types ==========

export interface WsMessage {
  type: 'auth' | 'message' | 'heartbeat' | 'ping' | 'error' | 'connected' | 'processing' | 'response';
  data?: Record<string, unknown>;
  message?: string;
  user_id?: string;
  status?: string;
}
