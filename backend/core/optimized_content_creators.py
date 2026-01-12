"""
Enhanced Content Creators - Using optimized prompts for maximum accuracy and quality
Features: Structured outputs, reduced hallucinations, Chain-of-Thought reasoning
"""

import asyncio
import json
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Import base classes and optimized prompts
from src.agents.base import SynthesisAgent, AgentResponse, ContentResponse
from src.config.manager import system_prompts
from src.schema.models import AgentStatus, LogLevel


@dataclass
class EnhancedContentResponse:
    """Enhanced content response with structured data"""
    success: bool
    content: Dict[str, Any]
    platform: str
    confidence: float
    metadata: Dict[str, Any]
    structured_output: bool = True


class OptimizedScriptDoctor(SynthesisAgent):
    """Optimized Script Doctor using enhanced prompts"""
    
    def __init__(self, llm_config: Optional[Dict] = None):
        super().__init__("script_doctor", llm_config)
        self.platform = "video_script"
    
    async def synthesize(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create engaging video script using optimized prompts"""
        
        content = input_data.get('content', '')
        detected_product = input_data.get('detected_product', 'the discussed topic')
        duration = input_data.get('duration', '60 seconds')
        
        await self.plan(f"Creating optimized script for detected product: {detected_product}")
        
        try:
            # Get optimized prompt with variable validation
            prompt = system_prompts.validate_prompt_variables(
                system_prompts.SCRIPT_DOCTOR_PROMPT,
                {
                    'content': content,
                    'detected_product': detected_product,
                    'duration': duration
                }
            )
            
            # Generate with optimized system prompt
            system_prompt = system_prompts.get_optimized_prompt("script_doctor")
            script_content = await self.generate_with_llm(prompt, system_prompt)
            
            # Parse JSON response
            try:
                script_data = json.loads(script_content)
                confidence = script_data.get('engagement_elements', {}).get('viral_potential', 0.85)
                
                return AgentResponse(
                    success=True,
                    content=script_data,
                    platform=self.platform,
                    confidence=confidence,
                    metadata={
                        "generation_method": "optimized_llm",
                        "structured_output": True,
                        "prompt_type": "enhanced_with_cot"
                    }
                )
            except json.JSONDecodeError:
                # Fallback to structured parsing if JSON fails
                return self._parse_script_fallback(script_content, content, detected_product)
                
        except Exception as e:
            await self.log_error(f"Script generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                content={"error": str(e)},
                platform=self.platform,
                confidence=0.0
            )
    
    def _parse_script_fallback(self, script_content: str, content: str, detected_product: str) -> AgentResponse:
        """Fallback parsing if JSON response fails"""
        return AgentResponse(
            success=True,
            content={
                "script": {
                    "hook": self._extract_hook(script_content),
                    "main_content": self._extract_main_content(script_content),
                    "call_to_action": self._extract_cta(script_content),
                    "estimated_duration": "60 seconds",
                    "platform_optimization": "general"
                },
                "engagement_elements": {
                    "hook_strength": 0.8,
                    "viral_potential": 0.75,
                    "call_to_action_clarity": 0.8
                }
            },
            platform=self.platform,
            confidence=0.75,
            metadata={"fallback_parsing": True}
        )


class OptimizedNewsletterWriter(SynthesisAgent):
    """Optimized Newsletter Writer using enhanced prompts"""
    
    def __init__(self, llm_config: Optional[Dict] = None):
        super().__init__("newsletter_writer", llm_config)
        self.platform = "newsletter"
    
    async def synthesize(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create high-converting newsletter using optimized prompts"""
        
        content = input_data.get('content', '')
        detected_product = input_data.get('detected_product', 'the discussed topic')
        brand_voice = input_data.get('brand_voice', 'professional')
        
        await self.plan(f"Creating optimized newsletter with {brand_voice} tone for {detected_product}")
        
        try:
            # Get optimized prompt with variable validation
            prompt = system_prompts.validate_prompt_variables(
                system_prompts.NEWSLETTER_WRITER_PROMPT,
                {
                    'content': content,
                    'detected_product': detected_product,
                    'brand_voice': brand_voice
                }
            )
            
            # Generate with optimized system prompt
            system_prompt = system_prompts.get_optimized_prompt("newsletter_writer")
            newsletter_content = await self.generate_with_llm(prompt, system_prompt)
            
            # Parse JSON response
            try:
                newsletter_data = json.loads(newsletter_content)
                confidence = newsletter_data.get('optimization_metrics', {}).get('subject_open_rate_prediction', 0.85)
                
                return AgentResponse(
                    success=True,
                    content=newsletter_data,
                    platform=self.platform,
                    confidence=confidence,
                    metadata={
                        "generation_method": "optimized_llm",
                        "structured_output": True,
                        "prompt_type": "enhanced_with_cot"
                    }
                )
            except json.JSONDecodeError:
                # Fallback to structured parsing if JSON fails
                return self._parse_newsletter_fallback(newsletter_content, content, detected_product, brand_voice)
                
        except Exception as e:
            await self.log_error(f"Newsletter generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                content={"error": str(e)},
                platform=self.platform,
                confidence=0.0
            )
    
    def _parse_newsletter_fallback(self, newsletter_content: str, content: str, detected_product: str, brand_voice: str) -> AgentResponse:
        """Fallback parsing if JSON response fails"""
        return AgentResponse(
            success=True,
            content={
                "newsletter": {
                    "subject_line": self._extract_subject_line(newsletter_content),
                    "preview_text": self._extract_preview_text(newsletter_content),
                    "greeting": "Hi there,",
                    "main_sections": self._extract_sections(newsletter_content),
                    "call_to_action": {"primary": "Read more", "secondary": "Share with colleagues"},
                    "personalization": {"tone": brand_voice, "segment": "general"}
                },
                "optimization_metrics": {
                    "subject_open_rate_prediction": 0.35,
                    "click_through_rate_prediction": 0.15,
                    "mobile_optimization": 0.8
                }
            },
            platform=self.platform,
            confidence=0.7,
            metadata={"fallback_parsing": True}
        )


class OptimizedBlogWriter(SynthesisAgent):
    """Optimized Blog Writer using enhanced prompts"""
    
    def __init__(self, llm_config: Optional[Dict] = None):
        super().__init__("blog_writer", llm_config)
        self.platform = "blog"
    
    async def synthesize(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create SEO-optimized blog post using optimized prompts"""
        
        content = input_data.get('content', '')
        detected_product = input_data.get('detected_product', 'the discussed topic')
        brand_voice = input_data.get('brand_voice', 'professional')
        seo_analysis = input_data.get('seo_analysis', '{}')
        
        await self.plan(f"Creating SEO-optimized blog post with {brand_voice} tone")
        
        try:
            # Get optimized prompt with variable validation
            prompt = system_prompts.validate_prompt_variables(
                system_prompts.BLOG_WRITER_PROMPT,
                {
                    'content': content,
                    'detected_product': detected_product,
                    'brand_voice': brand_voice,
                    'seo_analysis': seo_analysis
                }
            )
            
            # Generate with optimized system prompt
            system_prompt = system_prompts.get_optimized_prompt("blog_writer")
            blog_content = await self.generate_with_llm(prompt, system_prompt)
            
            # Parse JSON response
            try:
                blog_data = json.loads(blog_content)
                confidence = blog_data.get('content_metrics', {}).get('seo_score', 0.85)
                
                return AgentResponse(
                    success=True,
                    content=blog_data,
                    platform=self.platform,
                    confidence=confidence,
                    metadata={
                        "generation_method": "optimized_llm",
                        "structured_output": True,
                        "prompt_type": "enhanced_with_cot"
                    }
                )
            except json.JSONDecodeError:
                # Fallback to structured parsing if JSON fails
                return self._parse_blog_fallback(blog_content, content, detected_product, brand_voice)
                
        except Exception as e:
            await self.log_error(f"Blog generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                content={"error": str(e)},
                platform=self.platform,
                confidence=0.0
            )
    
    def _parse_blog_fallback(self, blog_content: str, content: str, detected_product: str, brand_voice: str) -> AgentResponse:
        """Fallback parsing if JSON response fails"""
        return AgentResponse(
            success=True,
            content={
                "blog_post": {
                    "seo_title": self._extract_title(blog_content),
                    "meta_description": self._extract_meta_description(blog_content),
                    "introduction": self._extract_introduction(blog_content),
                    "main_sections": self._extract_blog_sections(blog_content),
                    "conclusion": self._extract_conclusion(blog_content)
                },
                "content_metrics": {
                    "word_count": len(blog_content.split()),
                    "readability_score": 0.8,
                    "seo_score": 0.75
                }
            },
            platform=self.platform,
            confidence=0.7,
            metadata={"fallback_parsing": True}
        )


class OptimizedSocialStrategist(SynthesisAgent):
    """Optimized Social Media Strategist using enhanced prompts"""
    
    def __init__(self, llm_config: Optional[Dict] = None):
        super().__init__("social_strategist", llm_config)
        self.platform = "social_media"
    
    async def synthesize(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create platform-specific social media content using optimized prompts"""
        
        content = input_data.get('content', '')
        detected_product = input_data.get('detected_product', 'the discussed topic')
        brand_voice = input_data.get('brand_voice', 'professional')
        platform = input_data.get('platform', 'linkedin')
        
        await self.plan(f"Creating optimized {platform} content for {detected_product}")
        
        try:
            # Get optimized prompt with variable validation
            prompt = system_prompts.validate_prompt_variables(
                system_prompts.SOCIAL_STRATEGIST_PROMPT,
                {
                    'content': content,
                    'detected_product': detected_product,
                    'brand_voice': brand_voice,
                    'platform': platform
                }
            )
            
            # Generate with optimized system prompt
            system_prompt = system_prompts.get_optimized_prompt("social_strategist")
            social_content = await self.generate_with_llm(prompt, system_prompt)
            
            # Parse JSON response
            try:
                social_data = json.loads(social_content)
                platform_content = social_data.get(platform, {})
                confidence = platform_content.get('engagement_hooks', {}).get('viral_potential', 0.85)
                
                return AgentResponse(
                    success=True,
                    content=platform_content,
                    platform=platform,
                    confidence=confidence,
                    metadata={
                        "generation_method": "optimized_llm",
                        "structured_output": True,
                        "prompt_type": "enhanced_with_cot"
                    }
                )
            except json.JSONDecodeError:
                # Fallback to structured parsing if JSON fails
                return self._parse_social_fallback(social_content, platform, content, detected_product, brand_voice)
                
        except Exception as e:
            await self.log_error(f"Social media generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                content={"error": str(e)},
                platform=platform,
                confidence=0.0
            )
    
    def _parse_social_fallback(self, social_content: str, platform: str, content: str, detected_product: str, brand_voice: str) -> AgentResponse:
        """Fallback parsing if JSON response fails"""
        return AgentResponse(
            success=True,
            content={
                "content": social_content,
                "character_count": len(social_content),
                "hashtags": self._extract_hashtags(social_content),
                "tone": brand_voice,
                "call_to_action": "Share your thoughts!"
            },
            platform=platform,
            confidence=0.7,
            metadata={"fallback_parsing": True}
        )


# Helper methods for fallback parsing
class ContentParser:
    """Helper class for parsing content when JSON response fails"""
    
    @staticmethod
    def _extract_hook(content: str) -> str:
        """Extract hook from content"""
        lines = content.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            if '?' in line or '!' in line:
                return line.strip()
        return lines[0].strip() if lines else ""
    
    @staticmethod
    def _extract_main_content(content: str) -> str:
        """Extract main content body"""
        lines = content.split('\n')
        # Skip first few lines (likely hook) and get main content
        return '\n'.join(lines[3:10]) if len(lines) > 3 else content
    
    @staticmethod
    def _extract_cta(content: str) -> str:
        """Extract call-to-action"""
        lines = content.split('\n')
        # Look for CTA in last few lines
        for line in reversed(lines[-5:]):
            if any(word in line.lower() for word in ['follow', 'share', 'subscribe', 'comment', 'click']):
                return line.strip()
        return "Follow for more updates!"
    
    @staticmethod
    def _extract_subject_line(content: str) -> str:
        """Extract subject line from newsletter content"""
        lines = content.split('\n')
        for line in lines[:5]:
            if len(line) < 100 and ('!' in line or '?' in line):
                return line.strip()
        return "Weekly Update"
    
    @staticmethod
    def _extract_preview_text(content: str) -> str:
        """Extract preview text"""
        return content[:100] + "..." if len(content) > 100 else content
    
    @staticmethod
    def _extract_sections(content: str) -> List[Dict]:
        """Extract sections from content"""
        sections = []
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            if line.strip().startswith('#') or line.strip().startswith('**'):
                if current_section:
                    sections.append(current_section)
                current_section = {"heading": line.strip(), "content": ""}
            elif current_section:
                current_section["content"] += line + "\n"
        
        if current_section:
            sections.append(current_section)
        
        return sections[:3] if sections else [{"heading": "Main Content", "content": content}]
    
    @staticmethod
    def _extract_title(content: str) -> str:
        """Extract title from blog content"""
        lines = content.split('\n')
        for line in lines[:5]:
            if line.strip().startswith('#') or line.strip().startswith('**'):
                return line.strip().replace('#', '').replace('*', '').strip()
        return "Blog Post Title"
    
    @staticmethod
    def _extract_meta_description(content: str) -> str:
        """Extract meta description"""
        # Look for first meaningful sentence
        sentences = content.split('.')
        for sentence in sentences[:3]:
            if len(sentence.strip()) > 20 and len(sentence.strip()) < 160:
                return sentence.strip() + "."
        return content[:150] + "..."
    
    @staticmethod
    def _extract_introduction(content: str) -> Dict:
        """Extract introduction section"""
        lines = content.split('\n')
        intro_lines = []
        
        for line in lines:
            if line.strip().startswith('#') or line.strip().startswith('##'):
                break
            intro_lines.append(line)
        
        return {
            "hook": intro_lines[0].strip() if intro_lines else "",
            "value_proposition": " ".join(intro_lines[1:3]) if len(intro_lines) > 2 else "",
            "what_readers_will_learn": ["Key insights", "Practical applications"]
        }
    
    @staticmethod
    def _extract_blog_sections(content: str) -> List[Dict]:
        """Extract main sections from blog"""
        return ContentParser._extract_sections(content)
    
    @staticmethod
    def _extract_conclusion(content: str) -> Dict:
        """Extract conclusion section"""
        lines = content.split('\n')
        conclusion_lines = []
        in_conclusion = False
        
        for line in lines:
            if 'conclusion' in line.lower() or line.strip().startswith('#'):
                in_conclusion = True
            if in_conclusion:
                conclusion_lines.append(line)
        
        return {
            "summary": " ".join(conclusion_lines[:2]) if conclusion_lines else "",
            "call_to_action": "Share your thoughts below",
            "next_steps": "Subscribe for updates"
        }
    
    @staticmethod
    def _extract_hashtags(content: str) -> List[str]:
        """Extract hashtags from social media content"""
        import re
        hashtags = re.findall(r'#\w+', content)
        return hashtags[:5]  # Limit to 5 hashtags
    
    @staticmethod
    def _extract_hashtags(content: str) -> List[str]:
        """Extract hashtags from social media content"""
        import re
        hashtags = re.findall(r'#\w+', content)
        return hashtags[:5]  # Limit to 5 hashtags


# Extend the optimized content creators with helper methods
OptimizedScriptDoctor._extract_hook = staticmethod(ContentParser._extract_hook)
OptimizedScriptDoctor._extract_main_content = staticmethod(ContentParser._extract_main_content)
OptimizedScriptDoctor._extract_cta = staticmethod(ContentParser._extract_cta)

OptimizedNewsletterWriter._extract_subject_line = staticmethod(ContentParser._extract_subject_line)
OptimizedNewsletterWriter._extract_preview_text = staticmethod(ContentParser._extract_preview_text)
OptimizedNewsletterWriter._extract_sections = staticmethod(ContentParser._extract_sections)
OptimizedNewsletterWriter._extract_cta = staticmethod(ContentParser._extract_cta)

OptimizedBlogWriter._extract_title = staticmethod(ContentParser._extract_title)
OptimizedBlogWriter._extract_meta_description = staticmethod(ContentParser._extract_meta_description)
OptimizedBlogWriter._extract_introduction = staticmethod(ContentParser._extract_introduction)
OptimizedBlogWriter._extract_blog_sections = staticmethod(ContentParser._extract_blog_sections)
OptimizedBlogWriter._extract_conclusion = staticmethod(ContentParser._extract_conclusion)

OptimizedSocialStrategist._extract_hashtags = staticmethod(ContentParser._extract_hashtags)
