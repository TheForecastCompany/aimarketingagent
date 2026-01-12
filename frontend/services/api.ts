import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { 
  VideoProcessingRequest, 
  ContentRepurposingResult, 
  ProcessingStatusResponse,
  JobSubmissionResponse,
  ApiResponse,
  AgentStatus
} from '@/types';

class ApiClient {
  private client: AxiosInstance;
  private maxRetries = 3;
  private retryDelay = 1000;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000', // Updated to port 8000
      timeout: 0, // Infinity timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        const fullUrl = `${config.baseURL}${config.url}`;
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${fullUrl}`);
        console.log(`📋 Request Headers:`, config.headers);
        console.log(`📦 Request Data:`, config.data);
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as any;
        
        console.error(`❌ API Error Details:`);
        console.error(`  - Status: ${error.response?.status || 'No Response'}`);
        console.error(`  - URL: ${error.config?.url}`);
        console.error(`  - Method: ${error.config?.method?.toUpperCase()}`);
        console.error(`  - Error Code: ${error.code}`);
        console.error(`  - Message: ${error.message}`);
        console.error(`  - Full Error:`, error);
        
        if (error.response) {
          console.error(`  - Response Data:`, error.response.data);
          console.error(`  - Response Headers:`, error.response.headers);
        }

        // Retry logic for network errors
        if (!error.response && originalRequest && !originalRequest._retryCount) {
          originalRequest._retryCount = 0;
        }

        if (
          (!error.response || error.response?.status >= 500) && 
          originalRequest && 
          originalRequest._retryCount < this.maxRetries
        ) {
          originalRequest._retryCount += 1;
          console.log(`🔄 Retrying request (${originalRequest._retryCount}/${this.maxRetries})`);
          
          await this.delay(this.retryDelay * originalRequest._retryCount);
          return this.client(originalRequest);
        }

        return Promise.reject(this.handleError(error));
      }
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private handleError(error: AxiosError): Error {
    if (error.code === 'ECONNREFUSED' || error.code === 'ECONNRESET') {
      return new Error('Server Offline - Backend is not running. Please start the backend server.');
    }
    
    if (error.code === 'ETIMEDOUT' || error.message?.includes('timeout')) {
      if (error.config?.url?.includes('/process-video')) {
        return new Error('Job submission is taking longer than expected. The video may still be processing in the background. Please wait a moment and check the status.');
      }
      return new Error('Connection timeout. The server may be busy or experiencing issues.');
    }
    
    if (error.response) {
      // Server responded with error status
      const data = error.response.data as any;
      const message = data?.error || data?.message || `Server error: ${error.response.status}`;
      return new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Server Offline - Network error. Please check your connection and ensure backend is running.');
    } else {
      // Something happened in setting up the request
      return new Error(error.message || 'An unexpected error occurred.');
    }
  }

  // Video Processing Endpoints
  async submitVideoProcessingJob(request: VideoProcessingRequest): Promise<JobSubmissionResponse> {
    try {
      // Create a custom axios instance with no timeout for job submission
      const response = await this.client.post('/api/v1/process-video', request);
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Job submission failed');
      }
      
      return response.data;
    } catch (error) {
      console.error('Job submission error:', error);
      throw error;
    }
  }

  async processVideo(request: VideoProcessingRequest): Promise<ContentRepurposingResult> {
    try {
      // Direct call with no timeout - wait indefinitely
      const response = await this.client.post('/api/v1/process-video', request);
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Processing failed');
      }
      
      return response.data;
    } catch (error) {
      console.error('Video processing error:', error);
      throw error;
    }
  }

  async getProcessingStatus(jobId: string): Promise<ProcessingStatusResponse> {
    try {
      const response = await this.client.get<ApiResponse<ProcessingStatusResponse>>(
        `/api/processing-status/${jobId}`
      );
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to get status');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Status check error:', error);
      throw error;
    }
  }

  async getVideoByJobId(jobId: string): Promise<any> {
    try {
      const response = await this.client.get(`/api/v1/videos/by-job/${jobId}`);
      
      if (response.data.error) {
        throw new Error(response.data.error);
      }
      
      return response.data;
    } catch (error) {
      console.error('Get video by job ID error:', error);
      throw error;
    }
  }

  async cancelProcessing(workflowId: string): Promise<void> {
    try {
      await this.client.post(`/api/cancel-processing/${workflowId}`);
    } catch (error) {
      console.error('Cancel processing error:', error);
      throw error;
    }
  }

  // Configuration Endpoints
  async getBrandVoices(): Promise<string[]> {
    try {
      const response = await this.client.get<ApiResponse<string[]>>('/api/brand-voices');
      return response.data.data || [];
    } catch (error) {
      console.error('Get brand voices error:', error);
      throw error;
    }
  }

  async validateVideoUrl(url: string): Promise<{ valid: boolean; title?: string; duration?: string }> {
    try {
      const response = await this.client.post<ApiResponse<{ valid: boolean; title?: string; duration?: string }>>(
        '/api/validate-video',
        { url }
      );
      
      return response.data.data || { valid: false };
    } catch (error) {
      console.error('Video validation error:', error);
      throw error;
    }
  }

  // Export Endpoints
  async exportToPDF(workflowId: string): Promise<Blob> {
    try {
      const response = await this.client.get(`/api/export/pdf/${workflowId}`, {
        responseType: 'blob',
      });
      
      return response.data;
    } catch (error) {
      console.error('PDF export error:', error);
      throw error;
    }
  }

  async exportToJSON(workflowId: string): Promise<any> {
    try {
      const response = await this.client.get<ApiResponse<any>>(`/api/export/json/${workflowId}`);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Export failed');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('JSON export error:', error);
      throw error;
    }
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await this.client.get<ApiResponse<{ status: string; timestamp: string }>>(
        '/api/health'
      );
      
      return response.data.data || { status: 'unknown', timestamp: new Date().toISOString() };
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  // Video Results Endpoints
  async getVideos(): Promise<any[]> {
    try {
      const response = await this.client.get('/api/v1/videos');
      return response.data;
    } catch (error) {
      console.error('Get videos error:', error);
      throw error;
    }
  }

  // Utility method to download files
  downloadFile(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

// Create singleton instance
export const apiClient = new ApiClient();

// Export types for use in components
export type { ApiClient };
