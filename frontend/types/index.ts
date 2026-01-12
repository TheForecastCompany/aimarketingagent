// TypeScript types based on the backend Pydantic models
// This ensures type safety between frontend and backend

export enum AgentStatus {
  IDLE = "idle",
  THINKING = "thinking",
  ACTING = "acting",
  WAITING = "waiting",
  COMPLETED = "completed",
  FAILED = "failed",
  RETRYING = "retrying"
}

export enum ToolStatus {
  PENDING = "pending",
  EXECUTING = "executing",
  COMPLETED = "completed",
  FAILED = "failed",
  TIMEOUT = "timeout"
}

export enum LogLevel {
  DEBUG = "debug",
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
  CRITICAL = "critical"
}

export enum BrandVoice {
  PROFESSIONAL = "professional",
  CASUAL = "casual",
  PLAYFUL = "playful",
  AUTHORITATIVE = "authoritative",
  EMPATHETIC = "empathetic"
}

export enum Platform {
  LINKEDIN = "linkedin",
  TWITTER = "twitter",
  FACEBOOK = "facebook",
  INSTAGRAM = "instagram"
}

export enum ContentType {
  POST = "post",
  THREAD = "thread",
  STORY = "story",
  REEL = "reel"
}

export enum ScriptType {
  SHORT_FORM = "short_form",
  LONG_FORM = "long_form",
  EDUCATIONAL = "educational",
  PROMOTIONAL = "promotional"
}

// Core Models
export interface AgentResponse {
  success: boolean;
  content: any;
  confidence: number;
  reasoning: string;
  suggestions: string[];
  metadata: Record<string, any>;
  execution_time?: number;
  agent_name?: string;
}

export interface AgentThought {
  thought_id: string;
  agent_name: string;
  timestamp: string;
  thought_type: "planning" | "reasoning" | "reflection" | "decision";
  content: string;
  confidence?: number;
  context: Record<string, any>;
}

export interface AgentState {
  agent_name: string;
  status: AgentStatus;
  current_task?: string;
  thoughts: AgentThought[];
  last_response?: AgentResponse;
  error_count: number;
  retry_count: number;
  metadata: Record<string, any>;
}

// Tool Models
export interface ToolRequest {
  tool_name: string;
  parameters: Record<string, any>;
  request_id: string;
  agent_name: string;
  priority: "low" | "medium" | "high" | "critical";
  timeout?: number;
  metadata: Record<string, any>;
}

export interface ToolResponse {
  success: boolean;
  result: any;
  error_message?: string;
  execution_time: number;
  tool_name: string;
  request_id: string;
  metadata: Record<string, any>;
}

// Content Models
export interface ContentAnalysis {
  topics: string[];
  key_points: string[];
  sentiment: string;
  target_audience: string;
  word_count: number;
  estimated_reading_time: number;
  confidence: number;
  detected_product?: string;
}

export interface SocialMediaContent {
  platform: Platform;
  content_type: ContentType;
  content: string;
  hashtags: string[];
  mentions: string[];
  character_count: number;
  estimated_engagement?: number;
}

export interface NewsletterContent {
  subject: string;
  preview_text: string;
  body_content: string;
  call_to_action?: string;
  sections: string[];
  estimated_open_rate?: number;
}

export interface BlogPostContent {
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  tags: string[];
  category: string;
  estimated_reading_time: number;
  seo_score?: number;
}

export interface ScriptContent {
  script_type: ScriptType;
  content: string;
  estimated_duration: string;
  platform_suggestions: string[];
  visual_cues: string[];
}

// Configuration Models
export interface ProcessingConfig {
  brand_voice: BrandVoice;
  keywords: string[];
  enable_critique: boolean;
  track_costs: boolean;
  assemblyai_key?: string;
}

export interface VideoProcessingRequest {
  youtube_url: string;
  brand_voice: string;
  target_keywords: string[];
  enable_critique_loop: boolean;
}

// Result Models
export interface ContentRepurposingResult {
  success: boolean;
  workflow_id: string;
  total_execution_time: number;
  transcript?: string;
  analysis?: ContentAnalysis;
  social_media: Record<Platform, SocialMediaContent>;
  newsletter?: NewsletterContent;
  blog_post?: BlogPostContent;
  scripts: Record<string, ScriptContent>;
  seo_analysis?: Record<string, any>;
  quality_scores: Record<string, number>;
  detected_product?: string;
  processing_metrics: Record<string, any>;
  errors: string[];
  warnings: string[];
  metadata: Record<string, any>;
  critique_loop?: {
    linkedin: {
      original_content: string;
      improved_content: string;
      iterations: number;
      final_score: number;
      critique_history: any[];
      improvement_summary: string;
      quality_metrics: any;
    };
    twitter: {
      original_content: string;
      improved_content: string;
      iterations: number;
      final_score: number;
      critique_history: any[];
      improvement_summary: string;
      quality_metrics: any;
    };
  };
  cost_metrics?: {
    total_cost: number;
    total_tokens: number;
    total_calls: number;
    session_duration: number;
    agents_count: number;
    video_count: number;
    content_pieces_generated: number;
    current_metrics: {
      video_count: number;
      content_pieces_generated: number;
      total_cost: number;
      total_tokens: number;
      total_calls: number;
    };
    cost_breakdown?: Record<string, {
      total_cost: number;
      total_tokens: number;
      total_calls: number;
      avg_cost_per_call: number;
      avg_tokens_per_call: number;
    }>;
  };
  dashboard_data?: any;
}

// UI State Models  
export interface ProcessingState {
  isProcessing: boolean;
  progress: number;
  currentStep: string;
  error?: string;
  result?: ContentRepurposingResult;
  job_id?: string;
}

// Video Result Models
export interface ProcessedVideo {
  id: string;
  title: string;
  description: string;
  platforms: string[];
  created_at: string;
  status: string;
  thumbnail_url: string;
  content_snippets?: Record<string, string>;
  cost_metrics?: {
    total_cost: number;
    total_tokens: number;
    total_calls: number;
    session_duration: number;
    agents_count: number;
    video_count: number;
    content_pieces_generated: number;
    current_metrics: {
      video_count: number;
      content_pieces_generated: number;
      total_cost: number;
      total_tokens: number;
      total_calls: number;
    };
    cost_breakdown?: Record<string, {
      total_cost: number;
      total_tokens: number;
      total_calls: number;
      avg_cost_per_call: number;
      avg_tokens_per_call: number;
    }>;
  };
  critique_loop?: {
    linkedin: {
      original_content: string;
      improved_content: string;
      iterations: number;
      final_score: number;
      critique_history: any[];
      improvement_summary: string;
      quality_metrics: any;
    };
    twitter: {
      original_content: string;
      improved_content: string;
      iterations: number;
      final_score: number;
      critique_history: any[];
      improvement_summary: string;
      quality_metrics: any;
    };
  };
}

export interface DashboardMetrics {
  totalPlatforms: number;
  totalAgents: number;
  totalBrandVoices: number;
  totalQualityChecks: number;
}

// API Response Models
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ProcessingStatusResponse {
  status: AgentStatus;
  progress: number;
  current_step: string;
  job_id: string;
  estimated_time_remaining?: number;
  video_id?: string;
  result?: ContentRepurposingResult;
  error?: string;
}

export interface JobSubmissionResponse {
  success: boolean;
  job_id: string;
  status: string;
  message?: string;
  estimated_duration?: number;
  check_url?: string;
  error?: string;
}

// Form Models
export interface VideoUrlForm {
  video_url: string;
}

export interface ConfigurationForm {
  brand_voice: BrandVoice;
  keywords: string;
  enable_critique: boolean;
  track_costs: boolean;
}

// Component Props
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface LoadingProps extends BaseComponentProps {
  message?: string;
  progress?: number;
}

export interface ErrorProps extends BaseComponentProps {
  error: string;
  onRetry?: () => void;
}

export interface EmptyStateProps extends BaseComponentProps {
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}
