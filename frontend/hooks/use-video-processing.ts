import { useState, useCallback, useRef } from 'react';
import { useAppActions, useProcessing } from './use-app-store';
import { apiClient } from '@/services/api';
import { VideoProcessingRequest, ContentRepurposingResult, Platform, ContentType, ScriptType, AgentStatus, JobSubmissionResponse } from '@/types';

export function useVideoProcessing() {
  const [isPolling, setIsPolling] = useState(false);
  const { setProcessing, addResult, resetProcessing } = useAppActions();
  const processing = useProcessing();
  const isProcessingRef = useRef(false); // State lock to prevent duplicates

  const pollJobStatus = useCallback(async (jobId: string): Promise<any> => {
    const pollInterval = 3000; // 3 seconds
    const maxPollTime = 600000; // 10 minutes max polling time
    let pollCount = 0;
    const maxPolls = Math.floor(maxPollTime / pollInterval);

    console.log(`🔄 Starting polling for job ${jobId} every ${pollInterval}ms`);

    while (pollCount < maxPolls) {
      try {
        const status = await apiClient.getProcessingStatus(jobId);
        
        console.log(`📊 Poll ${pollCount + 1}/${maxPolls}: Status=${status.status}, Progress=${status.progress}%, Step=${status.current_step}`);
        
        // Update UI with current status
        setProcessing({
          currentStep: status.current_step,
          progress: status.progress
        });
        
        if (status.status === 'completed' && status.video_id) {
          console.log(`✅ Job ${jobId} completed with video_id: ${status.video_id}`);
          return { video_id: status.video_id, job_id: jobId };
        }
        
        if (status.status === 'failed') {
          throw new Error(status.error || 'Video processing failed on backend');
        }
        
        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, pollInterval));
        pollCount++;
      } catch (error) {
        if (pollCount === 0) {
          // If first poll fails, throw immediately
          throw error;
        }
        // For subsequent polls, continue and retry
        console.warn(`Poll attempt ${pollCount + 1} failed, retrying...`, error);
        await new Promise(resolve => setTimeout(resolve, pollInterval));
        pollCount++;
      }
    }
    
    throw new Error('Processing timeout - job may still be running in background');
  }, [setProcessing]);

  const processVideo = useCallback(async (request: VideoProcessingRequest) => {
    // Fire-and-forget processing with polling
    if (isProcessingRef.current) {
      console.warn('⚠️ Video processing already in progress, ignoring duplicate request');
      return;
    }

    try {
      // Set processing lock
      isProcessingRef.current = true;
      
      // Reset and set processing state
      resetProcessing();
      setProcessing({ 
        isProcessing: true, 
        progress: 0, 
        currentStep: 'Submitting job...',
        error: undefined 
      });

      // Submit job and get job_id immediately
      const jobSubmission = await apiClient.submitVideoProcessingJob(request);
      
      if (!jobSubmission.success || !jobSubmission.job_id) {
        throw new Error(jobSubmission.error || 'Failed to submit job');
      }

      console.log(`🎬 Job submitted with ID: ${jobSubmission.job_id}`);
      
      // Start polling for status
      setIsPolling(true);
      const result = await pollJobStatus(jobSubmission.job_id);
      
      // Get the full video details
      const videoDetails = await apiClient.getVideoByJobId(jobSubmission.job_id);
      
      // Complete processing
      setProcessing({ 
        currentStep: 'Complete!', 
        progress: 100, 
        isProcessing: false,
        result: videoDetails 
      });

      // Add to results history
      addResult(videoDetails);
      
      setIsPolling(false);
      isProcessingRef.current = false;

      return videoDetails;
    } catch (error) {
      console.error('Processing error:', error);
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      
      setProcessing({ 
        isProcessing: false, 
        error: errorMessage,
        currentStep: 'Error occurred'
      });
      
      setIsPolling(false);
      isProcessingRef.current = false;
      throw error;
    }
  }, [setProcessing, addResult, resetProcessing, pollJobStatus]);

  const cancelProcessing = useCallback(async () => {
    try {
      if (processing.job_id) {
        // Could add cancellation endpoint if needed
        console.log(`🛑 Cancelling processing for job: ${processing.job_id}`);
      }
      
      resetProcessing();
      setIsPolling(false);
      isProcessingRef.current = false; // Release lock on cancel
    } catch (error) {
      console.error('Cancel error:', error);
    }
  }, [processing.job_id, resetProcessing]);

  const clearError = useCallback(() => {
    setProcessing({ error: undefined });
  }, [setProcessing]);

  return {
    processVideo,
    cancelProcessing,
    clearError,
    isPolling,
    processing,
    isLocked: isProcessingRef.current
  };
}
