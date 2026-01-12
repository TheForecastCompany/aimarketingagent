from typing import Dict, Any, List, Optional, TYPE_CHECKING
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config/.env
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / "config" / ".env")

from backend.integrations.transcription import TranscriptExtractor
from backend.integrations.transcription_enhanced import EnhancedTranscriptExtractor
from backend.core.agents import ContentAnalystAgent, SocialStrategistAgent, ScriptDoctorAgent, AgentResponse
from backend.core.optimized_product_detector import OptimizedProductDetector, SAMPLE_PRODUCT_CATALOG
from backend.core.content_creators import NewsletterAgent, BlogPostAgent, ContentRepurposingAgent
from backend.services.brand_voice import BrandVoiceEngine, BrandVoice
from backend.services.quality_control import QualityController, ConfidenceScore
from backend.integrations.seo import SEOKeywordExtractor, SEOAnalysis
from backend.core.critique import AgenticCritiqueLoop
from backend.services.cost_tracker import CostTracker, TrackedAgent, TrackedAgentWrapper, AgencyDashboard
from backend.integrations.knowledge import KnowledgeRetriever
from backend.utils.logger import PerformanceLogger, LoggedAgent, LoggedAgentWrapper

if TYPE_CHECKING:
    from typing import ForwardRef

def load_repurposer(brand_voice: BrandVoice, target_keywords: List[str], 
                   enable_critique_loop: bool, track_costs: bool, 
                   _use_ollama: bool = False):
    """Load and initialize the VideoContentRepurposer with given configuration"""
    print(f"DEBUG: load_repurposer called with enable_logging=False")
    return VideoContentRepurposer(
        brand_voice=brand_voice,
        target_keywords=target_keywords,
        enable_critique_loop=enable_critique_loop,
        track_costs=track_costs,
        enable_rag=False,  # Always False for now
        use_ollama=_use_ollama
    )

class VideoContentRepurposer:
    """Main pipeline that orchestrates all agents"""
    
    def __init__(self, brand_voice: BrandVoice = None, target_keywords: List[str] = None, 
                 enable_critique_loop: bool = False, track_costs: bool = True, 
                 enable_rag: bool = False, use_ollama: bool = False):
        print("DEBUG: VideoContentRepurposer.__init__ called")
        self.transcript_extractor = TranscriptExtractor()
        self.brand_voice = brand_voice
        self.target_keywords = target_keywords or []
        self.enable_critique_loop = enable_critique_loop
        self.track_costs = track_costs
        self.enable_rag = enable_rag
        self.use_professional_transcription = True  # Always enabled
        self.use_ollama = use_ollama
        
        # Initialize optimized product detector
        self.product_detector = OptimizedProductDetector(SAMPLE_PRODUCT_CATALOG)
        
        # Initialize agents
        self.analyst = ContentAnalystAgent()
        self.social_strategist = SocialStrategistAgent(use_ollama=use_ollama)
        self.script_doctor = ScriptDoctorAgent(use_ollama=use_ollama)
        self.newsletter_agent = NewsletterAgent(use_ollama=use_ollama)
        self.blog_agent = BlogPostAgent(use_ollama=use_ollama)
        self.content_repurposer = ContentRepurposingAgent(use_ollama=use_ollama)
        
        # Initialize service components
        self.quality_controller = QualityController()
        self.seo_analyzer = SEOKeywordExtractor()
        self.critique_loop = AgenticCritiqueLoop()
        self.cost_tracker = CostTracker()
        self.knowledge_retriever = KnowledgeRetriever()
        self.performance_logger = PerformanceLogger()
        
        # Initialize cost tracking
        self.dashboard = AgencyDashboard(self.cost_tracker) if track_costs else None
        
        # Initialize knowledge retrieval (always False for now)
        self.knowledge_retriever = None
        
        # Initialize enhanced transcript extractor - always use professional transcription
        self.transcript_extractor = EnhancedTranscriptExtractor(
            use_professional=True,
            use_ollama=self.use_ollama
        )
        print("🎙️ Using Enhanced Transcript Extractor (Professional)")
        
        # Brand and quality systems
        self.brand_engine = BrandVoiceEngine()
        self.quality_controller = QualityController()
        self.critique_loop = AgenticCritiqueLoop(max_iterations=3, min_quality_score=0.7) if enable_critique_loop else None
        
        # Initialize agents with all enhancements
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agents with direct LLM access (no wrapping)"""
        base_agents = {
            "analyst": ContentAnalystAgent(),
            "social_strategist": SocialStrategistAgent(use_ollama=self.use_ollama),
            "script_doctor": ScriptDoctorAgent(use_ollama=self.use_ollama),
            "newsletter_agent": NewsletterAgent(use_ollama=self.use_ollama),
            "blog_agent": BlogPostAgent(use_ollama=self.use_ollama),
            "repurposing_agent": ContentRepurposingAgent(use_ollama=self.use_ollama),
            "seo_agent": SEOKeywordExtractor(self.brand_voice)
        }
        
        # Apply enhancements based on settings - but skip wrapping for LLM agents
        for name, agent in base_agents.items():
            # Start with the base agent
            enhanced_agent = agent
            
            # Only wrap non-LLM agents or when not using Ollama
            if name in ["analyst", "seo_agent", "social_strategist", "blog_agent", "newsletter_agent", "script_doctor", "repurposing_agent"] or not self.use_ollama:
            # Add cost tracking if enabled
                if self.track_costs:
                    enhanced_agent = TrackedAgentWrapper(enhanced_agent, self.cost_tracker)
            
            # Store the enhanced agent
            setattr(self, name, enhanced_agent)
    
    def process_video(self, youtube_url: str) -> Dict[str, Any]:
        """Process a YouTube video through the complete pipeline"""
        
        # Step 1: Extract transcript
        print("🎥 Extracting transcript...")
        print(f"📹 Processing URL: {youtube_url}")
        
        transcript_result = self.transcript_extractor.get_transcript(youtube_url)
        
        if not transcript_result:
            print("❌ Transcript extraction failed!")
            print("🔍 Debugging information:")
            print(f"   • URL: {youtube_url}")
            print(f"   • Video ID: {self.transcript_extractor.extract_video_id(youtube_url)}")
            
            print("💡 Professional Transcription Options:")
            print("   • Check ASSEMBLYAI_API_KEY environment variable")
            print("   • Verify AssemblyAI API key is valid")
            print("   • Try a different video")
            print("   • Check internet connection")
            
            return {"error": "Failed to extract transcript. The video may not have subtitles available. Check the console for detailed debugging information."}
        
        transcript = transcript_result.get("transcript", "")
        transcription_metadata = transcript_result.get("transcription_metadata", {})
        
        if not transcript:
            print("❌ Transcript extraction failed!")
            print("🔍 Debugging information:")
            print(f"   • URL: {youtube_url}")
            print(f"   • Video ID: {self.transcript_extractor.extract_video_id(youtube_url)}")
            
            print("💡 Professional Transcription Options:")
            print("   • Check ASSEMBLYAI_API_KEY environment variable")
            print("   • Verify AssemblyAI API key is valid")
            print("   • Try a different video")
            print("   • Check internet connection")
            
            return {"error": "Failed to extract transcript. The video may not have subtitles available. Check the console for detailed debugging information."}
        
        print(f"✅ Transcript extracted successfully ({len(transcript)} characters)")
        print(f"📝 Transcript preview: {transcript[:150]}...")
        
        # Add transcription metadata to results for downstream processing
        transcription_info = {
            "method": transcription_metadata.get("method", "youtube_api"),
            "has_speaker_diarization": transcription_metadata.get("has_speaker_diarization", False),
            "confidence_score": transcription_metadata.get("confidence_score", 0.0),
            "processing_time": transcription_metadata.get("processing_time", 0.0),
            "audio_duration": transcription_metadata.get("audio_duration", 0.0),
            "speakers": transcription_metadata.get("speakers", 0)
        }
        
        # Display transcription quality information
        if transcription_info["method"] == "assemblyai":
            print(f"🎙️ Professional Transcription Quality:")
            print(f"   • Confidence Score: {transcription_info['confidence_score']:.2f}")
            print(f"   • Speakers Detected: {transcription_info['speakers']}")
            print(f"   • Audio Duration: {transcription_info['audio_duration']:.2f}s")
            print(f"   • Processing Time: {transcription_info['processing_time']:.2f}s")
        else:
            print(f"📹 YouTube Transcription:")
            print(f"   • Method: {transcription_info['method']}")
            print(f"   • Speaker Diarization: {'Yes' if transcription_info['has_speaker_diarization'] else 'No'}")
        
        # Step 2: SEO Analysis - Extract keywords first
        print("🔍 Running SEO keyword analysis...")
        if self.track_costs:
            seo_analysis = self.seo_agent.track_operation(
                "keyword_extraction",
                self.seo_agent.agent.extract_keywords,
                transcript, 
                target_keywords=self.target_keywords
            )
        else:
            seo_analysis = self.seo_agent.extract_keywords(transcript, self.target_keywords)
        
        print(f"✅ SEO analysis complete - Found {len(seo_analysis.keywords)} keywords")
        
        # Step 3: Agent A - Analysis (now SEO-aware with optimized product detection)
        print("🧠 Running content analysis...")
        
        # Detect product from transcript first using optimized detector
        print("🔍 Detecting product from transcript...")
        product_detection = self.product_detector.detect_product(transcript)
        detected_product = product_detection.mapped_product
        print(f"🎯 Detected Product: {detected_product}")
        print(f"🎯 Detection Confidence: {product_detection.confidence}%")
        print(f"🎯 Speech Clarity: {product_detection.speech_clarity_score}%")
        
        if self.track_costs:
            def process_analysis(*args, **kwargs):
                # Handle both positional and keyword arguments
                if args:
                    transcript = args[0]
                else:
                    transcript = kwargs.get('transcript')
                return self.analyst.process(transcript)
            
            analysis = self.analyst.track_operation(
                "content_analysis",
                process_analysis,
                transcript,
                cost_per_operation=0.001
            )
        else:
            analysis = self.analyst.process(transcript)
        
        # Add product detection metadata to analysis
        if hasattr(analysis, 'content') and analysis.content:
            print(f"🔍 DEBUG: Analysis type before adding product: {type(analysis)}")
            print(f"🔍 DEBUG: Analysis has content attr: {hasattr(analysis, 'content')}")
            if isinstance(analysis.content, dict):
                # Add comprehensive product detection data
                analysis.content['transcript'] = transcript
                analysis.content['detected_product'] = detected_product
                analysis.content['product_detection'] = {
                    'detected_term': product_detection.detected_term,
                    'intent': product_detection.intent,
                    'confidence': product_detection.confidence,
                    'speech_clarity_score': product_detection.speech_clarity_score,
                    'brand': product_detection.brand,
                    'model': product_detection.model
                }
                print(f"🔍 DEBUG: Added transcript and comprehensive product detection to analysis.content dict")
                print(f"🔍 DEBUG: Transcript length: {len(transcript)}")
                print(f"🔍 DEBUG: Added detected_product: {detected_product}")
            else:
                # Convert to dict and add both transcript and product
                analysis_dict = {
                    'transcript': transcript,
                    'detected_product': detected_product,
                    'product_detection': {
                        'detected_term': product_detection.detected_term,
                        'intent': product_detection.intent,
                        'confidence': product_detection.confidence,
                        'speech_clarity_score': product_detection.speech_clarity_score,
                        'brand': product_detection.brand,
                        'model': product_detection.model
                    },
                    'analysis_content': str(analysis.content)
                }
                analysis.content = analysis_dict
                print(f"🔍 DEBUG: Created new dict with transcript and comprehensive product detection: {detected_product}")
        else:
            print(f"🔍 DEBUG: Analysis has no content attribute, creating new dict")
            # Create new content dict with transcript and product
            analysis.content = {
                'transcript': transcript,
                'detected_product': detected_product,
                'product_detection': {
                    'detected_term': product_detection.detected_term,
                    'intent': product_detection.intent,
                    'confidence': product_detection.confidence,
                    'speech_clarity_score': product_detection.speech_clarity_score,
                    'brand': product_detection.brand,
                    'model': product_detection.model
                }
            }
        
        print("✅ Analysis complete")
        
        # Step 4: Agent B - Social Media Content (with critique loop if enabled)
        print("📱 Creating social media content...")
        
        if self.enable_critique_loop:
            print("🔄 Running Writer-Editor critique loop...")
            
            # Generate social media content first, then apply critique loop
            print("🔍 DEBUG: Generating initial social media content...")
            brand_voice_tone = self.brand_voice.value if self.brand_voice else 'professional'
            
            if self.track_costs:
                linkedin_post = self.social_strategist.track_operation(
                    "linkedin_creation",
                    self.social_strategist.create_linkedin_post,
                    analysis,
                    brand_voice_tone=brand_voice_tone
                )
                twitter_thread = self.social_strategist.track_operation(
                    "twitter_creation",
                    self.social_strategist.create_twitter_thread,
                    analysis,
                    brand_voice_tone=brand_voice_tone
                )
            else:
                linkedin_post = self.social_strategist.create_linkedin_post(analysis, brand_voice_tone)
                twitter_thread = self.social_strategist.create_twitter_thread(analysis, brand_voice_tone)
            
            # Ensure detected_product is properly set in the analysis object
            if hasattr(analysis, 'content') and analysis.content and isinstance(analysis.content, dict):
                analysis.content['detected_product'] = detected_product
            
            # Update linkedin_post and twitter_thread with the latest analysis
            if self.track_costs:
                linkedin_post = self.social_strategist.track_operation(
                    "linkedin_creation",
                    self.social_strategist.create_linkedin_post,
                    analysis,
                    brand_voice_tone=brand_voice_tone
                )
                twitter_thread = self.social_strategist.track_operation(
                    "twitter_creation", 
                    self.social_strategist.create_twitter_thread,
                    analysis,
                    brand_voice_tone=brand_voice_tone
                )
            else:
                linkedin_post = self.social_strategist.create_linkedin_post(analysis, brand_voice_tone)
                twitter_thread = self.social_strategist.create_twitter_thread(analysis, brand_voice_tone)
            
            print("🔍 DEBUG: Applying critique loop to generated content...")
            # Extract content for critique
            if hasattr(linkedin_post, 'content') and linkedin_post.content:
                linkedin_content = linkedin_post.content if isinstance(linkedin_post.content, str) else str(linkedin_post.content)
            else:
                linkedin_content = str(linkedin_post)
                
            if hasattr(twitter_thread, 'content') and twitter_thread.content:
                twitter_content = twitter_thread.content if isinstance(twitter_thread.content, str) else str(twitter_thread.content)
            else:
                twitter_content = str(twitter_thread)
            
            # Fallback to transcript if no content
            analysis_content = linkedin_content or twitter_content or transcript if transcript else str(analysis)
            
            print(f"🔍 Debug: Final content for critique: {analysis_content[:100] if analysis_content else 'None'}...")
            
            if self.track_costs:
                linkedin_loop = self.critique_loop.critique_and_improve(analysis_content, "linkedin_post")
                twitter_loop = self.critique_loop.critique_and_improve(analysis_content, "twitter_thread")
            else:
                linkedin_loop = self.critique_loop.critique_and_improve(analysis_content, "linkedin_post")
                twitter_loop = self.critique_loop.critique_and_improve(analysis_content, "twitter_thread")
            
            linkedin_post = AgentResponse(
                success=True,
                content=linkedin_loop["improved_content"],
                confidence=linkedin_loop.get("final_score", 0.7),
                reasoning="Content improved through critique loop",
                suggestions=["Consider adding more examples", "Include relevant hashtags"]
            )
            linkedin_review = linkedin_loop["final_score"]
            
            twitter_thread = AgentResponse(
                success=True,
                content=twitter_loop["improved_content"],
                confidence=twitter_loop.get("final_score", 0.7),
                reasoning="Content improved through critique loop",
                suggestions=["Add engaging questions", "Use thread structure"]
            )
            twitter_review = twitter_loop["final_score"]
            
            print(f"✅ Social content created with {linkedin_loop['iterations']} LinkedIn revisions")
            print(f"✅ Twitter thread created with {twitter_loop['iterations']} revisions")
        else:
            brand_voice_tone = self.brand_voice.value if self.brand_voice else 'professional'
            if self.track_costs:
                twitter_thread = self.social_strategist.logged_operation(
                    "twitter_creation",
                    self.social_strategist.create_twitter_thread,
                    analysis,
                    brand_voice_tone=brand_voice_tone
                )
            elif self.track_costs:
                linkedin_post = self.social_strategist.track_operation(
                    "linkedin_creation",
                    self.social_strategist.create_linkedin_post,
                    analysis,
                    brand_voice_tone=brand_voice_tone
                )
                twitter_thread = self.social_strategist.track_operation(
                    "twitter_creation",
                    self.social_strategist.create_twitter_thread,
                    analysis,
                    brand_voice_tone=brand_voice_tone
                )
            else:
                linkedin_post = self.social_strategist.create_linkedin_post(analysis, brand_voice_tone)
                twitter_thread = self.social_strategist.create_twitter_thread(analysis, brand_voice_tone)
            
            linkedin_review = None
            twitter_review = None
            print("✅ Social content created")
        
        # Step 5: Agent C - Short-form Scripts
        print("🎬 Generating short-form scripts...")
        # Direct call without wrapper - pass the full analysis with transcript and product
        short_scripts = self.script_doctor.create_short_scripts(analysis)
        print("✅ Scripts generated")
        
        # Step 6: Agent D - Newsletter
        print("📧 Creating newsletter...")
        # Direct call without wrapper
        newsletter = self.newsletter_agent.create_newsletter(analysis)
        # Apply brand voice to newsletter content
        if hasattr(newsletter, 'content') and newsletter.content:
            if isinstance(newsletter.content, dict):
                newsletter.content['brand_voice'] = self.brand_voice.value if self.brand_voice else 'professional'
            else:
                # Convert to dict if it's not already
                newsletter.content = {'brand_voice': self.brand_voice.value if self.brand_voice else 'professional', 'content': str(newsletter.content)}
        print("✅ Newsletter created")
        
        # Step 7: Agent E - Blog Post (SEO-optimized)
        print("📝 Writing SEO-optimized blog post...")
        # Direct call without wrapper
        blog_post = self.blog_agent.create_blog_post(analysis)
        # Apply brand voice to blog post content
        if hasattr(blog_post, 'content') and blog_post.content:
            if isinstance(blog_post.content, dict):
                blog_post.content['brand_voice'] = self.brand_voice.value if self.brand_voice else 'professional'
            else:
                # Convert to dict if it's not already
                blog_post.content = {'brand_voice': self.brand_voice.value if self.brand_voice else 'professional', 'content': str(blog_post.content)}
        
        # Apply SEO optimization to blog post content
        seo_blog_post = blog_post  # Initialize with original blog_post
        
        if hasattr(blog_post, 'content') and blog_post.content:
            if isinstance(blog_post.content, dict):
                # Get the original content for SEO optimization
                original_content = str(blog_post.content.get('content', ''))
                seo_optimized_content = self.seo_agent.optimize_content_for_seo(original_content, seo_analysis, "blog_post")
                
                # Update the blog post with SEO optimized content but keep the ContentResponse structure
                blog_post.content['content'] = seo_optimized_content
                blog_post.content['seo_optimized'] = True
                seo_blog_post = blog_post  # Update the SEO optimized version
            else:
                # Handle case where content is not a dict
                original_content = str(blog_post.content)
                seo_optimized_content = self.seo_agent.optimize_content_for_seo(original_content, seo_analysis, "blog_post")
                blog_post.content = {'content': seo_optimized_content, 'seo_optimized': True, 'brand_voice': self.brand_voice.value if self.brand_voice else 'professional'}
                seo_blog_post = blog_post
        # else: seo_blog_post already initialized with original blog_post
        
        print("✅ SEO blog post created")
        
        # Step 8: Agent F - Content Repurposing Strategy
        print("🔄 Developing content strategy...")
        # Direct call without wrapper
        repurposing_plan = self.repurposing_agent.create_repurposing_plan(analysis)
        # Apply brand voice to strategy content
        if hasattr(repurposing_plan, 'content') and repurposing_plan.content:
            if isinstance(repurposing_plan.content, dict):
                repurposing_plan.content['brand_voice'] = self.brand_voice.value if self.brand_voice else 'professional'
            else:
                # Convert to dict if it's not already
                repurposing_plan.content = {'brand_voice': self.brand_voice.value if self.brand_voice else 'professional', 'content': str(repurposing_plan.content)}
        print("✅ Strategy developed")
        
        # Step 9: Quality Control - Analyze all content
        print("🔍 Running quality control...")
        quality_scores = self._analyze_quality({
            "linkedin_post": linkedin_post.content if hasattr(linkedin_post, 'content') and not isinstance(linkedin_post.content, dict) else (linkedin_post.content if hasattr(linkedin_post, 'content') else str(linkedin_post)),
            "twitter_thread": twitter_thread.content if hasattr(twitter_thread, 'content') and not isinstance(twitter_thread.content, dict) else (twitter_thread.content if hasattr(twitter_thread, 'content') else str(twitter_thread)),
            "short_scripts": short_scripts.content if hasattr(short_scripts, 'content') and not isinstance(short_scripts.content, dict) else (short_scripts.content if hasattr(short_scripts, 'content') else str(short_scripts)),
            "newsletter": newsletter.content if hasattr(newsletter, 'content') and not isinstance(newsletter.content, dict) else (newsletter.content if hasattr(newsletter, 'content') else str(newsletter)),
            "blog_post": blog_post.content if hasattr(blog_post, 'content') and not isinstance(blog_post.content, dict) else (blog_post.content if hasattr(blog_post, 'content') else str(blog_post)),
            "repurposing_plan": repurposing_plan.content if hasattr(repurposing_plan, 'content') and not isinstance(repurposing_plan.content, dict) else (repurposing_plan.content if hasattr(repurposing_plan, 'content') else str(repurposing_plan))
        })
        print("✅ Quality analysis complete")
        
        # Update metrics
        if self.cost_tracker:
            self.cost_tracker.current_metrics.video_count += 1
            self.cost_tracker.current_metrics.content_pieces_generated += 6  # 6 content pieces per video
            self.cost_tracker.video_count += 1
            self.cost_tracker.content_pieces_generated += 6
        
        # Return all results
        results = {
            "transcript": transcript,
            "analysis": analysis,
            "seo_analysis": seo_analysis.to_dict(),
            "linkedin_post": linkedin_post,
            "twitter_thread": twitter_thread,
            "short_scripts": short_scripts,
            "newsletter": newsletter,
            "blog_post": seo_blog_post,
            "repurposing_plan": repurposing_plan,
            "quality_scores": quality_scores
        }
        
        # Add critique loop results if enabled
        if self.enable_critique_loop:
            results["critique_loop"] = {
                "linkedin": linkedin_loop,
                "twitter": twitter_loop
            }
        
        # Add cost tracking results if enabled
        if self.track_costs:
            results["cost_metrics"] = self.cost_tracker.get_session_summary()
            results["dashboard_data"] = self.dashboard.generate_dashboard()  # Use existing method
        
        # Add transcription metadata to results for dashboard
        results["transcription_metadata"] = transcription_info
        
        # Add comprehensive product detection data to results
        if hasattr(analysis, 'content') and analysis.content and isinstance(analysis.content, dict):
            product_detection = analysis.content.get('product_detection', {})
            results["product_detection"] = product_detection
            results["detected_product"] = analysis.content.get('detected_product', 'Unknown')
        else:
            results["product_detection"] = {}
            results["detected_product"] = detected_product
        
        return results
    
    def _detect_product_from_transcript(self, transcript: str) -> str:
        """Detect main product/service from transcript using optimized phonetic matching"""
        if not transcript or len(transcript) < 50:
            return "Unknown product"
        
        try:
            # Use optimized product detector
            detection = self.product_detector.detect_product(transcript)
            
            if detection.confidence > 50:  # Only use if confidence is reasonable
                print(f"🎯 Optimized Product Detection:")
                print(f"  Detected Term: {detection.detected_term}")
                print(f"  Mapped Product: {detection.mapped_product}")
                print(f"  Intent: {detection.intent}")
                print(f"  Confidence: {detection.confidence}%")
                print(f"  Speech Clarity: {detection.speech_clarity_score}%")
                print(f"  Brand: {detection.brand}")
                print(f"  Model: {detection.model}")
                
                return detection.mapped_product
            else:
                print(f"⚠️ Low confidence detection ({detection.confidence}%), using fallback")
                return "Unknown product"
                
        except Exception as e:
            print(f"❌ Product detection error: {e}")
            return "Unknown product"
    
    def _analyze_quality(self, content_dict: Dict[str, str]) -> Dict[str, Dict[str, float]]:
        """Analyze quality of all generated content with timeout and error handling"""
        import time
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
        from typing import Dict, Any
        
        quality_scores = {}
        
        content_types = {
            "linkedin_post": "linkedin_post",
            "twitter_thread": "twitter_thread", 
            "short_scripts": "video_scripts",
            "newsletter": "newsletter",
            "blog_post": "blog_post",
            "repurposing_plan": "content_strategy"
        }
        
        def process_content(key: str, content: str) -> tuple[str, Dict[str, Any]]:
            """Process single content item with timeout and error handling"""
            try:
                content_type = content_types.get(key, "general")
                print(f"🔍 Assessing quality for {content_type} content...")
                start_time = time.time()
                
                # Get the actual content if it's an AgentResponse object
                content_str = content.content if hasattr(content, 'content') else str(content)
                
                # Limit content length to prevent timeouts
                if len(content_str) > 5000:
                    content_str = content_str[:5000] + "... [content truncated for quality assessment]"
                
                # Call with timeout
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        self.quality_controller.analyze_content_quality,
                        content_str, content_type, self.brand_voice
                    )
                    try:
                        result = future.result(timeout=30)  # 30 second timeout per content type
                        elapsed = time.time() - start_time
                        print(f"✅ Quality assessment for {content_type} completed in {elapsed:.1f}s")
                        return key, {
                            'score': float(result.overall_score) if hasattr(result, 'overall_score') else 0.8,
                            'status': 'completed',
                            'time_elapsed': elapsed
                        }
                    except FutureTimeout:
                        print(f"⚠️  Quality assessment for {content_type} timed out after 30 seconds")
                        return key, {'score': 0.7, 'status': 'timeout', 'time_elapsed': 30}
                    
            except Exception as e:
                print(f"⚠️  Error in quality assessment for {key}: {str(e)}")
                return key, {'score': 0.7, 'status': 'error', 'error': str(e)}
        
        # Process all content types in parallel with timeout
        with ThreadPoolExecutor(max_workers=3) as executor:  # Limit concurrent assessments
            futures = []
            for key, content in content_dict.items():
                futures.append(executor.submit(process_content, key, content))
            
            # Wait for all futures to complete with a total timeout
            for future in futures:
                try:
                    key, result = future.result(timeout=60)  # 1 minute total timeout
                    quality_scores[key] = result
                except Exception as e:
                    print(f"⚠️  Error processing quality assessment: {str(e)}")
        
        # Ensure we have at least a default score for each content type
        for key in content_dict.keys():
            if key not in quality_scores:
                quality_scores[key] = {'score': 0.8, 'status': 'skipped', 'reason': 'quality assessment failed'}
        
        print(f"✅ Quality analysis complete - {len(quality_scores)} items assessed")
        return quality_scores
    
    def apply_correction(self, content_type: str, original_content: str, 
                        correction_instruction: str) -> str:
        """Apply human correction to specific content"""
        from quality_control import CorrectionLoop
        correction_loop = CorrectionLoop()
        
        return correction_loop.apply_correction(
            original_content, correction_instruction, content_type, self.brand_voice
        )
    
    def get_summary(self, results: Dict[str, Any]) -> str:
        """Get a quick summary of the processing results"""
        if "error" in results:
            return f"❌ Error: {results['error']}"
        
        brand_info = f"\n🎨 Brand Voice: {self.brand_voice.value if self.brand_voice else 'Default'}" if self.brand_voice else ""
        seo_info = ""
        critique_info = ""
        cost_info = ""
        rag_info = ""
        logging_info = ""
        
        if "seo_analysis" in results:
            seo_data = results["seo_analysis"]
            keyword_count = len(seo_data.get("keywords", []))
            optimization_score = seo_data.get("optimization_score", 0)
            seo_info = f"\n🔍 SEO: {keyword_count} keywords, {optimization_score}/100 score"
        
        if "critique_loop" in results and self.enable_critique_loop:
            linkedin_revisions = results["critique_loop"]["linkedin"]["revision_count"]
            twitter_revisions = results["critique_loop"]["twitter"]["revision_count"]
            critique_info = f"\n🔄 Critique Loop: {linkedin_revisions + twitter_revisions} total revisions"
        
        if "cost_metrics" in results and self.track_costs:
            cost_data = results["cost_metrics"]
            total_cost = cost_data["current_metrics"]["total_cost"]
            total_tokens = cost_data["current_metrics"]["total_tokens"]
            cost_info = f"\n💰 Cost: ${total_cost:.4f}, {total_tokens} tokens"
        
        # RAG is always disabled for now
        rag_info = ""
        
        return f"""
✅ Multi-Channel Content Repurposing Complete!{brand_info}{seo_info}{critique_info}{cost_info}{rag_info}{logging_info}

📊 Analysis: {len(results['analysis'])} characters
🔍 SEO Analysis: {len(results['seo_analysis'])} keywords analyzed
📝 LinkedIn Post: {len(results['linkedin_post'])} characters  
🐦 Twitter Thread: {len(results['twitter_thread'])} characters
🎬 Short Scripts: {len(results['short_scripts'])} characters
📧 Newsletter: {len(results['newsletter'])} characters
📝 SEO Blog Post: {len(results['blog_post'])} characters
🔄 Content Strategy: {len(results['repurposing_plan'])} characters

🚀 Ready to publish across 6+ channels with full agency intelligence!
        """
