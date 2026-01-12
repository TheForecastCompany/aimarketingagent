"""
FastAPI Backend for Content Repurposing Agency
Robust API with authentication, rate limiting, and comprehensive endpoints
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Security, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.background import BackgroundTasks
from pydantic import BaseModel, Field, validator
import uvicorn
import jwt
from passlib.context import CryptContext
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import existing business logic
from pipeline import load_repurposer, VideoContentRepurposer
from brand_voice import BrandVoice
from display_components import display_metrics, display_transcript, display_analysis
from pdf_generator_enhanced_new import create_comprehensive_pdf, create_summary_pdf

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Redis for session management
try:
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()
except:
    redis_client = None

# Pydantic Models
class VideoProcessingRequest(BaseModel):
    video_url: str = Field(..., description="YouTube or video URL to process")
    brand_voice: str = Field(..., description="Brand voice style")
    keywords: List[str] = Field(default=[], description="Target keywords for SEO")
    enable_critique: bool = Field(default=True, description="Enable AI critique loop")
    track_costs: bool = Field(default=True, description="Track API costs")
    
    @validator('brand_voice')
    def validate_brand_voice(cls, v):
        valid_voices = ["Professional", "Casual", "Playful", "Authoritative", "Empathetic"]
        if v not in valid_voices:
            raise ValueError(f"Brand voice must be one of: {valid_voices}")
        return v
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Valid video URL is required")
        return v

class ProcessingStatus(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: int  # 0-100
    current_step: str
    message: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Global task storage (in production, use Redis or database)
processing_tasks: Dict[str, ProcessingStatus] = {}

# Authentication functions
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

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Background task for video processing
async def process_video_background(task_id: str, request: VideoProcessingRequest):
    """Background task to process video"""
    try:
        # Update task status
        processing_tasks[task_id].status = "processing"
        processing_tasks[task_id].progress = 10
        processing_tasks[task_id].current_step = "Initializing"
        processing_tasks[task_id].updated_at = datetime.utcnow()
        
        # Validate API keys
        assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY", "")
        if not assemblyai_key:
            processing_tasks[task_id].status = "failed"
            processing_tasks[task_id].error = "AssemblyAI API key required for transcription"
            processing_tasks[task_id].updated_at = datetime.utcnow()
            return
        
        # Create brand voice object
        brand_voices = {
            "Professional": BrandVoice.PROFESSIONAL,
            "Casual": BrandVoice.CASUAL,
            "Playful": BrandVoice.PLAYFUL,
            "Authoritative": BrandVoice.AUTHORITATIVE,
            "Empathetic": BrandVoice.EMPATHETIC
        }
        brand_voice_obj = brand_voices[request.brand_voice]
        
        # Load repurposer
        processing_tasks[task_id].progress = 20
        processing_tasks[task_id].current_step = "Loading AI agents"
        processing_tasks[task_id].updated_at = datetime.utcnow()
        
        repurposer = load_repurposer(
            brand_voice_obj,
            request.keywords,
            request.enable_critique,
            request.track_costs,
            True,  # Always use professional transcription
            _use_ollama=True
        )
        
        # Process video
        processing_tasks[task_id].progress = 30
        processing_tasks[task_id].current_step = "Extracting transcript"
        processing_tasks[task_id].updated_at = datetime.utcnow()
        
        results = repurposer.process_video(request.video_url)
        
        if not results:
            processing_tasks[task_id].status = "failed"
            processing_tasks[task_id].error = "Failed to process video. Please check the URL and try again."
            processing_tasks[task_id].updated_at = datetime.utcnow()
            return
        
        # Complete processing
        processing_tasks[task_id].status = "completed"
        processing_tasks[task_id].progress = 100
        processing_tasks[task_id].current_step = "Completed"
        processing_tasks[task_id].message = "Video processed successfully!"
        processing_tasks[task_id].results = results
        processing_tasks[task_id].updated_at = datetime.utcnow()
        
    except Exception as e:
        processing_tasks[task_id].status = "failed"
        processing_tasks[task_id].error = str(e)
        processing_tasks[task_id].updated_at = datetime.utcnow()

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Content Repurposing API starting up...")
    yield
    # Shutdown
    print("👋 Content Repurposing API shutting down...")

# FastAPI app
app = FastAPI(
    title="Content Repurposing Agency API",
    description="Professional API for video content repurposing and multi-platform content generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routes
@app.get("/", response_model=APIResponse)
@limiter.limit("100/minute")
async def root():
    """Root endpoint - API health check"""
    return APIResponse(
        success=True,
        message="Content Repurposing Agency API is running",
        data={"version": "1.0.0", "status": "healthy"}
    )

@app.post("/auth/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(auth_request: AuthRequest):
    """Authenticate user and return JWT token"""
    # Simple authentication (in production, use proper user database)
    if auth_request.username == "admin" and auth_request.password == "admin123":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": auth_request.username}, expires_delta=access_token_expires
        )
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.post("/process/video", response_model=APIResponse)
@limiter.limit("5/minute")
async def process_video(
    request: VideoProcessingRequest,
    background_tasks: BackgroundTasks,
    username: str = Depends(verify_token)
):
    """Start video processing in background"""
    try:
        # Generate unique task ID
        task_id = f"task_{datetime.utcnow().timestamp()}_{username}"
        
        # Create task status
        task_status = ProcessingStatus(
            task_id=task_id,
            status="pending",
            progress=0,
            current_step="Queued",
            message="Video processing queued",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store task
        processing_tasks[task_id] = task_status
        
        # Start background processing
        background_tasks.add_task(process_video_background, task_id, request)
        
        return APIResponse(
            success=True,
            message="Video processing started",
            data={"task_id": task_id, "status": "pending"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start video processing: {str(e)}"
        )

@app.get("/process/status/{task_id}", response_model=ProcessingStatus)
@limiter.limit("60/minute")
async def get_processing_status(
    task_id: str,
    username: str = Depends(verify_token)
):
    """Get processing status for a task"""
    if task_id not in processing_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return processing_tasks[task_id]

@app.get("/process/results/{task_id}", response_model=APIResponse)
@limiter.limit("30/minute")
async def get_processing_results(
    task_id: str,
    username: str = Depends(verify_token)
):
    """Get processing results for a completed task"""
    if task_id not in processing_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task = processing_tasks[task_id]
    
    if task.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task not completed. Current status: {task.status}"
        )
    
    if not task.results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not available"
        )
    
    # Process results to extract clean content from AgentResponse objects
    processed_results = {}
    if isinstance(task.results, dict):
        for key, value in task.results.items():
            if key in ["linkedin_post", "twitter_thread", "short_scripts", "newsletter", "blog_post"]:
                # Extract clean content for content fields
                processed_results[key] = extract_clean_content(value)
            else:
                # Keep other fields as-is (transcript, analysis, cost_metrics, critique_loop, etc.)
                processed_results[key] = value
    else:
        processed_results = task.results
    
    return APIResponse(
        success=True,
        message="Results retrieved successfully",
        data=processed_results
    )

@app.get("/export/pdf/{task_id}/comprehensive")
@limiter.limit("10/minute")
async def export_comprehensive_pdf(
    task_id: str,
    username: str = Depends(verify_token)
):
    """Export comprehensive PDF report"""
    if task_id not in processing_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task = processing_tasks[task_id]
    
    if task.status != "completed" or not task.results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No results available for PDF export"
        )
    
    try:
        pdf_bytes = create_comprehensive_pdf(task.results)
        
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=comprehensive_report_{task_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )

@app.get("/export/pdf/{task_id}/summary")
@limiter.limit("10/minute")
async def export_summary_pdf(
    task_id: str,
    username: str = Depends(verify_token)
):
    """Export summary PDF report"""
    if task_id not in processing_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task = processing_tasks[task_id]
    
    if task.status != "completed" or not task.results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No results available for PDF export"
        )
    
    try:
        pdf_bytes = create_summary_pdf(task.results)
        
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=summary_report_{task_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )

@app.get("/config/brand-voices", response_model=APIResponse)
@limiter.limit("60/minute")
async def get_brand_voices(username: str = Depends(verify_token)):
    """Get available brand voices"""
    voices = [
        {"id": "Professional", "name": "Professional", "description": "Formal and authoritative tone"},
        {"id": "Casual", "name": "Casual", "description": "Relaxed and conversational tone"},
        {"id": "Playful", "name": "Playful", "description": "Fun and engaging tone"},
        {"id": "Authoritative", "name": "Authoritative", "description": "Expert and confident tone"},
        {"id": "Empathetic", "name": "Empathetic", "description": "Understanding and supportive tone"}
    ]
    
    return APIResponse(
        success=True,
        message="Brand voices retrieved successfully",
        data={"brand_voices": voices}
    )

@app.get("/config/features", response_model=APIResponse)
@limiter.limit("60/minute")
async def get_features(username: str = Depends(verify_token)):
    """Get available features and configuration"""
    features = {
        "ai_critique": {
            "available": True,
            "description": "AI-powered content improvement and quality control"
        },
        "cost_tracking": {
            "available": True,
            "description": "Track API costs and usage metrics"
        },
        "export_formats": {
            "pdf": True,
            "json": True,
            "csv": False
        },
        "transcription": {
            "available": bool(os.getenv("ASSEMBLYAI_API_KEY")),
            "description": "High-accuracy professional transcription with AssemblyAI",
            "required": True
        }
    }
    
    return APIResponse(
        success=True,
        message="Features retrieved successfully",
        data=features
    )

@app.get("/health", response_model=APIResponse)
@limiter.limit("100/minute")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "api": "healthy",
        "redis": "connected" if redis_client else "disconnected",
        "assemblyai": "configured" if os.getenv("ASSEMBLYAI_API_KEY") else "not_configured",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return APIResponse(
        success=True,
        message="Health check completed",
        data=health_status
    )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "error": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
