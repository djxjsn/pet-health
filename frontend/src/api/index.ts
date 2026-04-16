export { ApiClient, apiClient, ApiClientError, NetworkError } from './client';
export { authApi } from './auth';
export { petApi, type PetListResponse } from './pets';
export { chatApi, type ConversationDetail, type CreateConversationResponse } from './chat';
export { healthApi, type HealthConsultResult, type SymptomAnalysisResult, type HealthRecord } from './health';
export { behaviorApi, type BehaviorAnalyzeResult, type TrainingRecommendationResult } from './behavior';
