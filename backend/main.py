#!/usr/bin/env python3
"""
Content Repurposing Agency - FastAPI Backend
Professional modular architecture with clear separation of concerns
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import logging
import uuid
import asyncio
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from config/.env
load_dotenv(project_root / "config" / ".env")

# Create FastAPI application
app = FastAPI(
    title="Content Repurposing Agency API",
    description="Backend API for video content repurposing services",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory job storage (in production, use Redis or database)
job_storage: Dict[str, Dict[str, Any]] = {}
processed_videos: List[Dict[str, Any]] = []

# Job status enum
class JobStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Pydantic models for job tracking
class JobSubmissionResponse(BaseModel):
    success: bool
    job_id: str
    message: Optional[str] = None
    estimated_duration: Optional[int] = None

class JobStatusResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Pydantic model for video processing request
class VideoProcessingRequest(BaseModel):
    youtube_url: str
    brand_voice: str = "professional"
    target_keywords: List[str] = []
    enable_critique_loop: bool = False

# Pre-import heavy modules to prevent blocking during job submission
try:
    from backend.core.pipeline import load_repurposer
    from backend.services.brand_voice import BrandVoice
    logger.info("✅ Pre-loaded heavy modules for faster background processing")
except ImportError as e:
    logger.warning(f"⚠️ Could not pre-load modules: {e}")
    load_repurposer = None
    BrandVoice = None

# Background processing function
async def process_video_background(job_id: str, video_request: VideoProcessingRequest):
    """Background task to process video without blocking HTTP response"""
    logger.info(f"🔄 Starting background processing for job {job_id}")
    
    try:
        # Update job status to processing
        job_storage[job_id].update({
            "status": JobStatus.PROCESSING,
            "current_step": "Initializing video repurposer...",
            "progress": 10,
            "started_at": datetime.now().isoformat()
        })
        
        # Check for duplicate processing
        existing_job = None
        for stored_job_id, stored_job in job_storage.items():
            if (stored_job_id != job_id and 
                stored_job.get("video_url") == video_request.youtube_url and
                stored_job.get("status") in [JobStatus.PENDING, JobStatus.PROCESSING]):
                existing_job = stored_job_id
                break
        
        if existing_job:
            logger.warning(f"⚠️ Duplicate video URL detected. Job {existing_job} is already processing this video.")
            job_storage[job_id].update({
                "status": JobStatus.FAILED,
                "error": f"This video is already being processed by job {existing_job}",
                "current_step": "Duplicate detected",
                "progress": 0
            })
            return
        
        # Yield control back to allow immediate HTTP response
        await asyncio.sleep(0.1)
        
        # Import required modules (always import in background task)
        from backend.core.pipeline import load_repurposer
        from backend.services.brand_voice import BrandVoice
        
        job_storage[job_id].update({
            "current_step": "Loading repurposer...",
            "progress": 20
        })
        
        # Convert brand voice string to enum
        brand_voice_map = {
            "professional": BrandVoice.PROFESSIONAL,
            "casual": BrandVoice.CASUAL,
            "playful": BrandVoice.PLAYFUL,
            "authoritative": BrandVoice.AUTHORITATIVE,
            "empathetic": BrandVoice.EMPATHETIC
        }
        brand_voice = brand_voice_map.get(video_request.brand_voice.lower(), BrandVoice.PROFESSIONAL)
        
        # Initialize repurposer
        repurposer = load_repurposer(
            brand_voice=brand_voice,
            target_keywords=video_request.target_keywords,
            enable_critique_loop=video_request.enable_critique_loop,
            track_costs=True,
            _use_ollama=True
        )
        
        job_storage[job_id].update({
            "current_step": "Starting video analysis...",
            "progress": 30
        })
        
        # Process the video
        results = repurposer.process_video(video_request.youtube_url)
        
        if "error" in results:
            logger.error(f"❌ Video processing failed for job {job_id}: {results['error']}")
            job_storage[job_id].update({
                "status": JobStatus.FAILED,
                "error": results["error"],
                "current_step": "Processing failed",
                "progress": 0
            })
            return
        
        job_storage[job_id].update({
            "current_step": "Finalizing results...",
            "progress": 90
        })
        
        # Store successful results and create processed video entry
        def extract_clean_content(obj, default=""):
            """Extract clean content from AgentResponse objects or return string content"""
            if hasattr(obj, 'content'):
                # This is an AgentResponse object
                content = obj.content
                if isinstance(content, dict):
                    # If content is a dict, look for common content fields
                    if 'script' in content:
                        return content['script']
                    elif 'content' in content:
                        return str(content['content'])
                    elif 'body' in content:
                        return content['body']
                    else:
                        # Return the first string value found in the dict
                        for key, value in content.items():
                            if isinstance(value, str) and len(value) > 10:
                                return value
                        return str(content)
                else:
                    # Content is already a string or other type
                    return str(content)
            else:
                # Not an AgentResponse, convert to string directly
                return str(obj) if obj else default
        
        # Create processed video entry
        new_video = {
            "id": f"video_{len(processed_videos) + 1}",
            "title": f"Processed Video {len(processed_videos) + 1}",
            "description": f"Video processed from {video_request.youtube_url}",
            "platforms": ["LinkedIn", "Twitter", "Blog", "Newsletter"],  # Fixed: Standard platforms
            "created_at": datetime.now().isoformat() + "Z",
            "status": "completed",
            "thumbnail_url": f"https://picsum.photos/seed/video{len(processed_videos) + 1}/400/400",
            "content_snippets": {},
            "job_id": job_id
        }
        
        # Add content to snippets - FIXED: Pipeline returns dict with direct keys
        if isinstance(results, dict):
            logger.info(f"🔍 DEBUG: Processing results dict with keys: {list(results.keys())}")
            
            # Extract cost metrics and critique loop if available
            cost_metrics = results.get("cost_metrics")
            critique_loop = results.get("critique_loop")
            
            # Social media content - Use clean content extraction
            if results.get("linkedin_post"):
                content = extract_clean_content(results["linkedin_post"])
                new_video["content_snippets"]["LinkedIn"] = content
                logger.info(f"✅ Mapped LinkedIn content ({len(content)} chars)")
            else:
                logger.warning("⚠️ No LinkedIn content found")
                
            if results.get("twitter_thread"):
                content = extract_clean_content(results["twitter_thread"])
                new_video["content_snippets"]["Twitter"] = content
                logger.info(f"✅ Mapped Twitter content ({len(content)} chars)")
            else:
                logger.warning("⚠️ No Twitter content found")
            
            # Newsletter content - Use clean content extraction
            if results.get("newsletter"):
                content = extract_clean_content(results["newsletter"])
                new_video["content_snippets"]["Newsletter"] = content
                logger.info(f"✅ Mapped Newsletter content ({len(content)} chars)")
            else:
                logger.warning("⚠️ No Newsletter content found")
            
            # Blog content - Use clean content extraction
            if results.get("blog_post"):
                content = extract_clean_content(results["blog_post"])
                new_video["content_snippets"]["Blog"] = content
                logger.info(f"✅ Mapped Blog content ({len(content)} chars)")
            else:
                logger.warning("⚠️ No Blog content found")
            
            # Scripts content - Use clean content extraction with special handling for script field
            if results.get("short_scripts"):
                scripts = results["short_scripts"]
                if isinstance(scripts, dict):
                    for script_type, content in scripts.items():
                        content_str = extract_clean_content(content)
                        new_video["content_snippets"][script_type.title()] = content_str
                        logger.info(f"✅ Mapped {script_type} script ({len(content_str)} chars)")
                else:
                    content_str = extract_clean_content(scripts)
                    new_video["content_snippets"]["Scripts"] = content_str
                    logger.info(f"✅ Mapped Scripts content ({len(content_str)} chars)")
            else:
                logger.warning("⚠️ No Scripts content found")
            
            # Add cost metrics if available
            if cost_metrics:
                new_video["cost_metrics"] = cost_metrics
                logger.info(f"✅ Added cost metrics to video data")
            
            # Add critique loop results if available
            if critique_loop:
                new_video["critique_loop"] = critique_loop
                logger.info(f"✅ Added critique loop results to video data")
            
            # Log final mapping results
            logger.info(f"📊 Final content_snippets keys: {list(new_video['content_snippets'].keys())}")
            for key, value in new_video['content_snippets'].items():
                logger.info(f"📝 {key}: {len(str(value))} characters")
        else:
            logger.error(f"🔍 DEBUG: Results is not a dict, type: {type(results)}")
        
        # Add to processed videos list
        processed_videos.append(new_video)
        logger.info(f"📝 Saved processed video with ID: {new_video['id']} for job {job_id}")
        logger.info(f"📊 Total processed videos in memory: {len(processed_videos)}")
        logger.info(f"📋 Video keys: {list(new_video.keys())}")
        logger.info(f"📋 Content snippets keys: {list(new_video['content_snippets'].keys())}")
        
        # Store successful results
        job_storage[job_id].update({
            "status": JobStatus.COMPLETED,
            "result": results,
            "video_id": new_video["id"],
            "current_step": "Completed successfully",
            "progress": 100,
            "completed_at": datetime.now().isoformat()
        })
        
        logger.info(f"✅ Background processing completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"❌ Background processing failed for job {job_id}: {str(e)}")
        job_storage[job_id].update({
            "status": JobStatus.FAILED,
            "error": str(e),
            "current_step": "Error occurred",
            "progress": 0
        })

# Exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    logger.error(f"❌ Validation Error Details:")
    logger.error(f"   Request URL: {request.url}")
    logger.error(f"   Request Method: {request.method}")
    
    # Try to get raw request body for debugging
    try:
        body = await request.body()
        if body:
            logger.error(f"   Raw Request Body: {body.decode()}")
    except Exception as e:
        logger.error(f"   Could not read request body: {e}")
    
    # Log validation errors
    for error in exc.errors():
        logger.error(f"   Field: {' -> '.join(str(loc) for loc in error['loc'])}")
        logger.error(f"   Message: {error['msg']}")
        logger.error(f"   Type: {error['type']}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed",
            "details": exc.errors(),
            "message": f"Invalid request format. Check field: {' -> '.join(str(loc) for loc in exc.errors()[0]['loc']) if exc.errors() else 'unknown'}"
        }
    )

# Pydantic models for API responses
class ProcessedVideo(BaseModel):
    id: str
    title: str
    description: str
    platforms: List[str]
    created_at: str
    status: str
    thumbnail_url: str
    content_snippets: Dict[str, str]

class VideoContent(BaseModel):
    platform: str
    content: str
    word_count: int
    created_at: str

# Note: processed_videos is already declared at module level (line 52)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Content Repurposing Agency API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/v1/status")
async def get_status():
    """Get application status"""
    return {
        "status": "operational",
        "services": {
            "backend": "running",
            "database": "not configured",
            "ai_models": "available"
        }
    }

@app.get("/api/v1/videos", response_model=List[ProcessedVideo])
async def get_processed_videos():
    """Get all processed videos"""
    logger.info(f"📊 API: Returning {len(processed_videos)} processed videos")
    if processed_videos:
        logger.info(f"📋 API: Video IDs: {[v['id'] for v in processed_videos]}")
    return processed_videos

@app.get("/api/v1/debug/add-test-video")
async def add_test_video():
    """Debug endpoint to add a test video"""
    test_video = {
        "id": f"video_{len(processed_videos) + 1}",
        "title": "Test Video for Debug",
        "description": "This is a test video added via debug endpoint",
        "platforms": ["LinkedIn", "Twitter", "Blog"],
        "created_at": datetime.now().isoformat() + "Z",
        "status": "completed",
        "thumbnail_url": "https://picsum.photos/seed/test/400/400",
        "content_snippets": {
            "LinkedIn": "This is a test LinkedIn post content",
            "Twitter": "This is a test Twitter post content",
            "Blog": "This is a test blog post content with more details",
            "Newsletter": "This is a test newsletter content"
        }
    }
    processed_videos.append(test_video)
    logger.info(f"🔧 Debug: Added test video {test_video['id']}. Total videos: {len(processed_videos)}")
    return {"success": True, "video_id": test_video["id"], "total_videos": len(processed_videos)}

@app.get("/api/v1/videos/{video_id}", response_model=ProcessedVideo)
async def get_video_details(video_id: str):
    """Get details for a specific video"""
    video = next((v for v in processed_videos if v["id"] == video_id), None)
    if not video:
        return {"error": "Video not found"}
    return video

@app.get("/api/v1/videos/{video_id}/content", response_model=List[VideoContent])
async def get_video_content(video_id: str):
    """Get all generated content for a specific video"""
    video = next((v for v in processed_videos if v["id"] == video_id), None)
    if not video:
        return {"error": "Video not found"}
    
    if "content_snippets" in video:
        return [{"platform": platform, "content": content, "word_count": len(content.split()), "created_at": video["created_at"]} for platform, content in video["content_snippets"].items()]
    else:
        return {"error": "Content not available for this video"}

@app.post("/api/v1/process-video")
async def process_video(request: Request, background_tasks: BackgroundTasks):
    """Fire-and-forget video processing - returns immediately with job_id"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Parse request
        body = await request.body()
        request_data = json.loads(body.decode())
        video_request = VideoProcessingRequest(**request_data)
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job storage
        job_storage[job_id] = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "video_url": video_request.youtube_url,
            "brand_voice": video_request.brand_voice,
            "target_keywords": video_request.target_keywords,
            "enable_critique_loop": video_request.enable_critique_loop,
            "current_step": "Queued for processing...",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        logger.info(f"🎬 Video processing job {job_id} queued for: {video_request.youtube_url}")
        
        # Add background task
        background_tasks.add_task(process_video_background, job_id, video_request)
        
        # Return immediately with job_id
        return {
            "success": True,
            "job_id": job_id,
            "status": "pending",
            "message": "Video processing started. Use job_id to check status.",
            "check_url": f"/api/processing-status/{job_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to queue video processing: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to start processing: {str(e)}",
            "status": "failed"
        }

@app.get("/api/processing-status/{job_id}")
async def get_processing_status(job_id: str):
    """Get the status of a video processing job"""
    logger.info(f"📊 Status check requested for job {job_id}")
    
    if job_id not in job_storage:
        logger.warning(f"❌ Job {job_id} not found")
        return JobStatusResponse(
            success=False,
            error=f"Job {job_id} not found"
        )
    
    job = job_storage[job_id]
    
    # Map job status to frontend status
    status_mapping = {
        JobStatus.PENDING: "idle",
        JobStatus.PROCESSING: "acting", 
        JobStatus.COMPLETED: "completed",
        JobStatus.FAILED: "failed"
    }
    
    response_data = {
        "status": status_mapping.get(job["status"], "idle"),
        "progress": job["progress"],
        "current_step": job["current_step"],
        "job_id": job_id
    }
    
    # Include result if completed
    if job["status"] == JobStatus.COMPLETED and job.get("result"):
        response_data["result"] = job["result"]
        response_data["video_id"] = job.get("video_id")
    
    # Include error if failed
    if job["status"] == JobStatus.FAILED and job.get("error"):
        response_data["error"] = job["error"]
    
    logger.info(f"✅ Status check completed for job {job_id}: {job['status']}")
    
    return JobStatusResponse(
        success=True,
        data=response_data
    )

@app.get("/api/v1/videos/by-job/{job_id}")
async def get_video_by_job_id(job_id: str):
    """Get video details by job ID"""
    logger.info(f"📊 Video lookup requested for job {job_id}")
    
    if job_id not in job_storage:
        logger.warning(f"❌ Job {job_id} not found")
        return {"error": f"Job {job_id} not found"}
    
    job = job_storage[job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        return {
            "error": "Job not completed",
            "status": job["status"],
            "current_step": job.get("current_step", "Unknown"),
            "progress": job.get("progress", 0)
        }
    
    video_id = job.get("video_id")
    if not video_id:
        return {"error": "Video ID not found for completed job"}
    
    video = next((v for v in processed_videos if v["id"] == video_id), None)
    if not video:
        return {"error": "Video not found"}
    
    return video

def main():
    """Main function for running app directly"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
