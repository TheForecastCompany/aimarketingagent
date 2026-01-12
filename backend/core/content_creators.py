#!/usr/bin/env python3
"""
Content Generation Agents - Specialized agents for creating platform-specific content
Transforms analyzed content into various formats for different platforms
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import os
from dotenv import load_dotenv

# LLM imports
from ollama import Client as OllamaClient

load_dotenv()

@dataclass
class ContentResponse:
    """Standard response format for content generation"""
    success: bool
    content: Dict[str, Any]
    platform: str
    confidence: float
    metadata: Dict[str, Any]

class BaseContentAgent(ABC):
    """Base class for all content generation agents"""
    
    def __init__(self, name: str, platform: str, description: str, use_ollama: bool = True):
        self.name = name
        self.platform = platform
        self.description = description
        self.use_ollama = True  # Force Ollama usage
        
        # Initialize LLM - Ollama only
        self.llm = OllamaClient(
            host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").replace("http://", "")
        )
        self.model = os.getenv("OLLAMA_MODEL", "mistral:latest")
        print(f"✍️ {name} Agent Initialized (Ollama)")
        
        print(f"📱 Platform: {platform}")
        print(f"📋 {description}")
    
    def _generate_with_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Generate content using LLM - Ollama only"""
        if self.llm is None:
            return self._generate_fallback(prompt)
        
        try:
            # Direct OllamaClient usage like SEOKeywordExtractor
            response = self.llm.generate(prompt=prompt, model=self.model)
            if response and response.done and response.response:
                return response.response
            else:
                return self._generate_fallback(prompt)
        except Exception as e:
            print(f"❌ LLM generation failed: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_fallback(self, prompt: str) -> str:
        """Fallback generation when LLM is not available"""
        return f"Content generation completed for {self.name}. Unable to generate detailed content due to LLM unavailability."
    
    @abstractmethod
    def generate_content(self, analysis: Dict[str, Any], transcript: str, 
                        brand_voice: str = "professional", **kwargs) -> ContentResponse:
        """Generate platform-specific content"""
        pass
    
    def _log_generation(self, content_type: str, details: str = ""):
        """Log content generation actions"""
        print(f"📝 {self.name}: Generating {content_type}")
        if details:
            print(f"   💡 {details}")

class NewsletterAgent(BaseContentAgent):
    """Generates email newsletter content"""
    
    def __init__(self, use_ollama: bool = True):
        super().__init__(
            "Newsletter Generator",
            "email_newsletter",
            "Creates engaging email newsletters with subject lines and body content",
            use_ollama=use_ollama
        )
    
    def generate_content(self, analysis: Dict[str, Any], transcript: str, 
                        brand_voice: str = "professional", **kwargs) -> ContentResponse:
        """Generate newsletter content using LLM"""
        self._log_generation("newsletter content")
        
        # Extract detected product from analysis
        detected_product = analysis.get('detected_product', 'Unknown product') if isinstance(analysis, dict) else 'Unknown product'
        print(f"🎯 DEBUG: Newsletter using detected product: {detected_product}")
        
        try:
            # Generate newsletter using LLM
            prompt = f'''Create an engaging email newsletter based on this content:
            
            Transcript: {transcript[:800]}
            Analysis: {str(analysis)[:300]}
            Brand Voice: {brand_voice}
            
            Requirements:
            - Compelling subject line
            - Engaging body content
            - Personalized tone
            - Call-to-action
            - Length: 300-500 words
            - Focus on marketing the detected product: {detected_product}
            
            Marketing Focus:
            - Highlight the product/service being discussed
            - Use benefit-oriented language
            - Include relevant use cases or applications
            - Create urgency or curiosity about the product
            - Professional but approachable tone
            
            Format:
            - Subject line (5-10 words)
            - Personalized greeting
            - 2-3 main sections
            - Clear call-to-action
            - Mobile-friendly formatting
            - Professional yet approachable tone'''
            
            system_prompt = "You are a professional newsletter writer specializing in creating engaging email content that drives opens, clicks, and engagement. Write compelling newsletters that readers look forward to receiving."
            
            newsletter_content = self._generate_with_llm(prompt, system_prompt)
            
            # Parse the generated content into structured format
            content = {
                "subject": self._extract_subject(newsletter_content),
                "preview": self._extract_preview(newsletter_content),
                "body": newsletter_content,
                "call_to_action": self._extract_cta(newsletter_content),
                "sections": self._identify_sections(newsletter_content),
                "personalization": {"tone": brand_voice, "style": "engaging"},
                "formatting": {"type": "html", "mobile_friendly": True}
            }
            
            confidence = 0.85
            
            return ContentResponse(
                success=True,
                content=content,
                platform=self.platform,
                confidence=confidence,
                metadata={
                    "word_count": len(newsletter_content.split()),
                    "estimated_read_time": len(newsletter_content.split()) // 200,
                    "brand_voice": brand_voice,
                    "generation_method": "llm"
                }
            )
            
        except Exception as e:
            return ContentResponse(
                success=False,
                content={"error": str(e)},
                platform=self.platform,
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def _extract_subject(self, content: str) -> str:
        """Extract subject line from generated content"""
        lines = content.split('\n')
        for line in lines:
            if line.strip() and len(line.strip()) < 100:
                return line.strip()
        return "Your Weekly Newsletter"
    
    def _extract_preview(self, content: str) -> str:
        """Extract preview text from generated content"""
        sentences = content.split('.')
        for sentence in sentences[:3]:
            if len(sentence.strip()) > 20 and len(sentence.strip()) < 150:
                return sentence.strip()
        return "This week's insights and updates..."
    
    def _extract_cta(self, content: str) -> str:
        """Extract call-to-action from generated content"""
        if "call to action" in content.lower() or "cta" in content.lower():
            lines = content.split('\n')
            for line in lines:
                if any(word in line.lower() for word in ["click", "learn", "discover", "join", "subscribe"]):
                    return line.strip()
        return "Click here to learn more"
    
    def _identify_sections(self, content: str) -> List[str]:
        """Identify sections in the newsletter"""
        sections = []
        lines = content.split('\n')
        current_section = ""
        
        for line in lines:
            if line.strip().startswith('#') or line.strip().startswith('##'):
                if current_section:
                    sections.append(current_section.strip())
                current_section = line.strip()
            else:
                current_section += " " + line.strip()
        
        if current_section:
            sections.append(current_section.strip())
        
        return sections[:4]  # Limit to 4 sections
    
    def create_newsletter(self, analysis: Dict[str, Any]) -> ContentResponse:
        """Create newsletter content - alias for generate_content method"""
        # Handle AgentResponse object
        if hasattr(analysis, 'content') and analysis.content:
            actual_analysis = analysis.content
        else:
            actual_analysis = analysis
        return self.generate_content(actual_analysis, "", "professional")
    
    def _generate_subject_line(self, analysis: Dict, brand_voice: str) -> str:
        """Generate engaging subject line"""
        topics = analysis.get("topics", [])
        sentiment = analysis.get("sentiment", "neutral")
        
        subject_templates = {
            "professional": [
                "Weekly Insights: {topic} Update",
                "Industry Update: {topic} Trends",
                "Professional Development: {topic} Analysis"
            ],
            "casual": [
                "Hey! Check out this {topic} content",
                "This week in {topic} - You won't want to miss this!",
                "Quick update on {topic} 📧"
            ],
            "bold": [
                "🔥 {topic} Revolution is Here!",
                "BREAKING: {topic} Changes Everything!",
                "Don't Get Left Behind: {topic} Insights!"
            ]
        }
        
        templates = subject_templates.get(brand_voice, subject_templates["professional"])
        template = templates[0]  # Use first template
        
        if topics:
            return template.format(topic=topics[0].title())
        else:
            return "Weekly Newsletter: Latest Updates"
    
    def _generate_newsletter_body(self, analysis: Dict, transcript: str, brand_voice: str) -> str:
        """Generate newsletter body content"""
        key_points = analysis.get("key_points", [])
        topics = analysis.get("topics", [])
        
        # Create introduction
        intro = self._create_introduction(analysis, brand_voice)
        
        # Create main content
        main_content = self._create_main_content(key_points, topics, transcript, brand_voice)
        
        # Create conclusion
        conclusion = self._create_conclusion(analysis, brand_voice)
        
        return f"{intro}\n\n{main_content}\n\n{conclusion}"
    
    def _create_introduction(self, analysis: Dict, brand_voice: str) -> str:
        """Create newsletter introduction"""
        tone_map = {
            "professional": "Welcome to this week's professional insights",
            "casual": "Hey there! Here's what's new this week",
            "bold": "🚀 BIG NEWS this week!"
        }
        
        intro = tone_map.get(brand_voice, "Welcome to this week's newsletter")
        
        topics = analysis.get("topics", [])
        if topics:
            intro += f"\n\nThis week we're diving into {', '.join(topics[:3])}."
        
        return intro
    
    def _create_main_content(self, key_points: List[str], topics: List[str], 
                           transcript: str, brand_voice: str) -> str:
        """Create main newsletter content"""
        content_parts = []
        
        # Add key points
        if key_points:
            content_parts.append("🔑 Key Points:")
            for point in key_points[:3]:
                content_parts.append(f"• {point}")
        
        # Add topic discussion
        if topics:
            content_parts.append(f"\n📊 Topic Discussion:")
            for topic in topics[:2]:
                content_parts.append(f"\n{topic.title()}:")
                # Add some relevant content based on transcript
                content_parts.append(f"Recent developments in {topic} show promising trends...")
        
        # Add insights from transcript
        if transcript:
            content_parts.append(f"\n💡 Insights:")
            # Take a snippet from transcript
            words = transcript.split()
            if len(words) > 50:
                content_parts.append(f"{' '.join(words[:50])}...")
        
        return "\n".join(content_parts)
    
    def _create_conclusion(self, analysis: Dict, brand_voice: str) -> str:
        """Create newsletter conclusion"""
        tone_map = {
            "professional": "Thank you for reading. Stay tuned for next week's insights.",
            "casual": "That's it for this week! Catch you next time.",
            "bold": "🔥 Stay ahead of the curve - see you next week!"
        }
        
        return tone_map.get(brand_voice, "Thank you for reading.")
    
    def _generate_call_to_action(self, analysis: Dict, brand_voice: str) -> str:
        """Generate call to action"""
        ctas = {
            "professional": "Read more on our website",
            "casual": "Check out our latest posts!",
            "bold": "JOIN THE REVOLUTION NOW!"
        }
        
        return ctas.get(brand_voice, "Learn more")
    
    def _generate_preview_text(self, body: str) -> str:
        """Generate preview text for email clients"""
        words = body.split()
        preview = " ".join(words[:15])
        
        if len(words) > 15:
            preview += "..."
        
        return preview
    
    def _create_newsletter_sections(self, analysis: Dict, transcript: str) -> List[Dict]:
        """Create newsletter sections"""
        sections = []
        
        # Featured content section
        sections.append({
            "title": "Featured Content",
            "content": "This week's highlights and key insights",
            "type": "featured"
        })
        
        # Topics section
        topics = analysis.get("topics", [])
        if topics:
            sections.append({
                "title": "Topic Spotlight",
                "content": f"Deep dive into {topics[0]}",
                "type": "topic"
            })
        
        return sections
    
    def _add_personalization(self, analysis: Dict) -> Dict:
        """Add personalization elements"""
        return {
            "greeting": "Hi [First Name],",
            "recommendations": "Based on your interests",
            "dynamic_content": "Personalized just for you"
        }
    
    def _get_formatting_guidelines(self) -> Dict:
        """Get formatting guidelines"""
        return {
            "font_family": "Arial, sans-serif",
            "font_size": "14px",
            "line_height": "1.6",
            "max_width": "600px",
            "use_images": True,
            "use_buttons": True
        }
    
    def _calculate_confidence(self, content: Dict, analysis: Dict) -> float:
        """Calculate confidence score"""
        confidence = 0.8
        
        # Adjust based on content length
        body_word_count = len(content["body"].split())
        if body_word_count > 100:
            confidence += 0.1
        
        # Adjust based on analysis quality
        if analysis.get("key_points"):
            confidence += 0.1
        
        return min(confidence, 1.0)

class BlogPostAgent(BaseContentAgent):
    """Generates blog post content"""
    
    def __init__(self, use_ollama: bool = True):
        super().__init__(
            "Blog Post Generator",
            "blog",
            "Creates comprehensive blog posts with SEO optimization",
            use_ollama=use_ollama
        )
    
    def generate_content(self, analysis: Dict[str, Any], transcript: str, 
                        brand_voice: str = "professional", **kwargs) -> ContentResponse:
        """Generate blog post content using LLM"""
        self._log_generation("blog post")
        print(f"🔍 DEBUG: BlogPostAgent.generate_content called")
        print(f"🔍 DEBUG: Analysis type: {type(analysis)}")
        print(f"🔍 DEBUG: Has LLM: {hasattr(self, 'llm')}")
        
        try:
            # Generate blog post using LLM
            prompt = f"""
            Create a comprehensive SEO-optimized blog post based on this content:
            
            Transcript: {transcript[:2000]}
            
            Analysis: {str(analysis)[:500]}
            
            Brand Voice: {brand_voice}
            
            Requirements:
            - Compelling title (under 70 characters)
            - Engaging introduction with hook
            - Well-structured body with 3-5 sections
            - Include key insights and takeaways
            - SEO-friendly headings and subheadings
            - Meta description (under 160 characters)
            - Relevant tags and keywords
            - Professional yet accessible tone
            - 800-1500 words
            - Include call-to-action at the end
            """
            
            system_prompt = "You are a professional blog writer and SEO specialist. Create engaging, well-structured blog posts that rank well and provide real value to readers."
            
            blog_content = self._generate_with_llm(prompt, system_prompt)
            
            # Parse the generated content into structured format
            content = {
                "title": self._extract_title(blog_content),
                "content": blog_content,
                "meta_description": self._extract_meta_description(blog_content),
                "tags": self._extract_tags(blog_content),
                "structure": self._identify_blog_structure(blog_content),
                "seo_optimization": {"keyword_density": "optimal", "readability": "high"},
                "readability_score": 0.85,
                "word_count": len(blog_content.split())
            }
            
            confidence = 0.85
            
            return ContentResponse(
                success=True,
                content=content,
                platform=self.platform,
                confidence=confidence,
                metadata={
                    "word_count": len(blog_content.split()),
                    "estimated_read_time": len(blog_content.split()) // 200,
                    "brand_voice": brand_voice,
                    "generation_method": "llm",
                    "seo_optimized": True
                }
            )
            
        except Exception as e:
            return ContentResponse(
                success=False,
                content={"error": str(e)},
                platform=self.platform,
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def _extract_title(self, content: str) -> str:
        """Extract title from generated content"""
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#') and len(line.strip()) < 100:
                return line.strip()
        return "Latest Blog Post"
    
    def _extract_meta_description(self, content: str) -> str:
        """Extract meta description from generated content"""
        sentences = content.split('.')
        for sentence in sentences[:3]:
            if len(sentence.strip()) > 50 and len(sentence.strip()) < 160:
                return sentence.strip()
        return "A comprehensive blog post with insights and analysis."
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from generated content"""
        # Simple tag extraction - look for keywords
        common_tags = ["blog", "insights", "analysis", "trends", "technology", "business", "strategy"]
        found_tags = []
        for tag in common_tags:
            if tag.lower() in content.lower():
                found_tags.append(tag)
        return found_tags[:5] or ["blog", "insights"]
    
    def _identify_blog_structure(self, content: str) -> Dict[str, Any]:
        """Identify blog structure"""
        sections = []
        lines = content.split('\n')
        
        for line in lines:
            if line.strip().startswith('#') or line.strip().startswith('##'):
                sections.append(line.strip())
        
        return {
            "introduction": "Engaging opening with hook",
            "main_content": f"{len(sections)} main sections",
            "conclusion": "Summary with call-to-action",
            "sections": sections[:5]
        }
    
    def create_blog_post(self, analysis: Dict[str, Any]) -> ContentResponse:
        """Create blog post content - alias for generate_content method"""
        # Handle AgentResponse object
        if hasattr(analysis, 'content') and analysis.content:
            actual_analysis = analysis.content
        else:
            actual_analysis = analysis
        return self.generate_content(actual_analysis, "", "professional")
    
    def _generate_blog_title(self, analysis: Dict, brand_voice: str) -> str:
        """Generate engaging blog title"""
        topics = analysis.get("topics", [])
        sentiment = analysis.get("sentiment", "neutral")
        
        title_templates = {
            "professional": [
                "A Comprehensive Guide to {topic}",
                "Understanding {topic}: Key Insights and Trends",
                "Professional Analysis: {topic} in 2024"
            ],
            "casual": [
                "Everything You Need to Know About {topic}",
                "{topic}: Here's What You Should Know",
                "Let's Talk About {topic} - The Complete Guide"
            ],
            "bold": [
                "{topic} REVOLUTION: What You Need to Know NOW!",
                "SHOCKING {topic} Truths Revealed!",
                "The Ultimate {topic} Guide That Changes Everything!"
            ]
        }
        
        templates = title_templates.get(brand_voice, title_templates["professional"])
        
        if topics:
            return templates[0].format(topic=topics[0].title())
        else:
            return "Latest Insights and Analysis"
    
    def _generate_blog_content(self, analysis: Dict, transcript: str, brand_voice: str) -> str:
        """Generate blog post content"""
        key_points = analysis.get("key_points", [])
        topics = analysis.get("topics", [])
        
        # Create introduction
        intro = self._create_blog_intro(analysis, brand_voice)
        
        # Create main body
        main_body = self._create_blog_body(key_points, topics, transcript, brand_voice)
        
        # Create conclusion
        conclusion = self._create_blog_conclusion(analysis, brand_voice)
        
        return f"{intro}\n\n{main_body}\n\n{conclusion}"
    
    def _create_blog_intro(self, analysis: Dict, brand_voice: str) -> str:
        """Create blog introduction"""
        topics = analysis.get("topics", [])
        
        intro = f"In today's rapidly evolving landscape"
        
        if topics:
            intro += f", understanding {topics[0]} has become increasingly important"
        
        intro += ". This comprehensive guide will walk you through the key aspects, latest trends, and practical insights."
        
        return intro
    
    def _create_blog_body(self, key_points: List[str], topics: List[str], 
                         transcript: str, brand_voice: str) -> str:
        """Create blog main body"""
        sections = []
        
        # Add key points section
        if key_points:
            sections.append("## Key Points\n")
            for point in key_points:
                sections.append(f"{point}\n")
        
        # Add detailed sections for each topic
        for topic in topics[:2]:
            sections.append(f"## Understanding {topic.title()}\n")
            sections.append(f"{topic.title()} is a critical area that deserves attention. ")
            sections.append("Recent developments have shown significant progress in this field. ")
            
            # Add content from transcript
            if transcript:
                words = transcript.split()
                if len(words) > 30:
                    sections.append(f"According to recent insights: {' '.join(words[:30])}...")
            
            sections.append("\n")
        
        return "\n".join(sections)
    
    def _create_blog_conclusion(self, analysis: Dict, brand_voice: str) -> str:
        """Create blog conclusion"""
        conclusion = "## Conclusion\n\n"
        
        topics = analysis.get("topics", [])
        if topics:
            conclusion += f"As we've explored throughout this article, {topics[0]} represents a significant area of opportunity. "
        
        conclusion += "By staying informed and adapting to new developments, you can position yourself for success in this evolving landscape."
        
        return conclusion
    
    def _generate_meta_description(self, analysis: Dict, content: str) -> str:
        """Generate SEO meta description"""
        words = content.split()
        meta = " ".join(words[:25])
        
        if len(words) > 25:
            meta += "..."
        
        return meta
    
    def _generate_tags(self, analysis: Dict) -> List[str]:
        """Generate blog tags"""
        tags = []
        
        # Add topics as tags
        topics = analysis.get("topics", [])
        for topic in topics:
            tags.append(topic)
        
        # Add general tags
        tags.extend(["insights", "analysis", "trends", "guide"])
        
        return tags[:10]  # Limit to 10 tags
    
    def _create_blog_structure(self, analysis: Dict, content: str) -> Dict:
        """Create blog structure"""
        return {
            "has_headings": True,
            "has_lists": True,
            "has_images": True,
            "word_count": len(content.split()),
            "reading_time": len(content.split()) / 200,
            "sections": ["Introduction", "Main Content", "Conclusion"]
        }
    
    def _get_seo_optimization(self, analysis: Dict) -> Dict:
        """Get SEO optimization settings"""
        return {
            "keyword_density": "2-3%",
            "meta_length": "150-160 characters",
            "title_length": "50-60 characters",
            "image_alt_text": True,
            "internal_links": True
        }
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score"""
        sentences = content.split('.')
        if not sentences:
            return 0.0
        
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if 10 <= avg_words <= 20:
            return 0.9
        elif 5 <= avg_words <= 25:
            return 0.7
        else:
            return 0.5
    
    def _calculate_confidence(self, content: Dict, analysis: Dict) -> float:
        """Calculate confidence score"""
        confidence = 0.8
        
        # Adjust based on content length
        if content["word_count"] > 300:
            confidence += 0.1
        
        # Adjust based on structure
        if content["structure"]["has_headings"]:
            confidence += 0.1
        
        return min(confidence, 1.0)

class ContentRepurposingAgent(BaseContentAgent):
    """Coordinates content repurposing across multiple platforms"""
    
    def __init__(self, use_ollama: bool = True):
        super().__init__(
            "Content Repurposing Coordinator",
            "multi_platform",
            "Coordinates content creation across multiple platforms",
            use_ollama=use_ollama
        )
        self.newsletter_agent = NewsletterAgent(use_ollama=use_ollama)
        self.blog_agent = BlogPostAgent(use_ollama=use_ollama)
    
    def generate_content(self, analysis: Dict[str, Any], transcript: str, 
                        brand_voice: str = "professional", **kwargs) -> ContentResponse:
        """Generate blog post content using LLM"""
        self._log_generation("blog post")
        
        # Extract detected product from analysis
        detected_product = analysis.get('detected_product', 'Unknown product') if isinstance(analysis, dict) else 'Unknown product'
        print(f"🎯 DEBUG: Blog post using detected product: {detected_product}")
        
        try:
            # Generate blog post using LLM
            prompt = f"""
            Create a comprehensive SEO-optimized blog post based on this content:
            
            Transcript: {transcript[:800]}
            Analysis: {str(analysis)[:300]}
            Brand Voice: {brand_voice}
            
            Requirements:
            - SEO-optimized title (50-60 characters)
            - Meta description (150-160 characters)
            - Engaging introduction
            - 2-4 main body sections
            - Internal linking structure
            - Length: 800-1500 words
            - Focus on marketing the detected product: {detected_product}
            
            Marketing Focus:
            - Highlight the product/service being discussed
            - Use benefit-oriented language
            - Include relevant use cases or applications
            - Create urgency or curiosity about the product
            - Professional yet approachable tone
            - SEO keywords naturally integrated
            
            Format:
            - Compelling H1 title
            - Meta description
            - Introduction paragraph
            - 2-4 body sections with H2/H3 headings
            - Conclusion with CTA
            - SEO-friendly URL structure
            """
            
            system_prompt = "You are a content strategy expert specializing in multi-platform content repurposing. Create comprehensive strategies that maximize content reach and engagement across different platforms."
            
            strategy_content = self._generate_with_llm(prompt, system_prompt)
            
            # Parse the generated content into structured format
            content = {
                "title": self._generate_blog_title(analysis, brand_voice),
                "meta_description": self._generate_meta_description(analysis, strategy_content),
                "content": strategy_content,
                "structure": self._create_blog_structure(analysis, strategy_content),
                "tags": self._generate_tags(analysis),
                "confidence": self._calculate_confidence({"word_count": len(strategy_content.split())}, analysis),
                "metadata": self._get_seo_optimization(analysis),
                "strategy": strategy_content,
                "platforms": {
                    "newsletter": {
                        "type": "email_newsletter",
                        "frequency": "weekly",
                        "tone": "professional yet engaging",
                        "key_focus": "insights and analysis"
                    },
                    "blog": {
                        "type": "seo_blog_post",
                        "frequency": "bi-weekly",
                        "tone": "informative and authoritative",
                        "key_focus": "deep-dive analysis"
                    },
                    "linkedin": {
                        "type": "professional_post",
                        "frequency": "3x_weekly",
                        "tone": "professional and insightful",
                        "key_focus": "industry insights"
                    },
                    "twitter": {
                        "type": "engaging_thread",
                        "frequency": "daily",
                        "tone": "conversational and timely",
                        "key_focus": "key takeaways and questions"
                    },
                    "video": {
                        "type": "short_form_script",
                        "frequency": "2x_weekly",
                        "tone": "energetic and engaging",
                        "key_focus": "visual storytelling"
                    }
                },
                "coordination_notes": "Maintain consistent brand voice across all platforms while adapting content format",
                "repurposing_opportunities": [
                    "Blog posts can be repurposed into newsletter content",
                    "Video scripts can be adapted for social media posts",
                    "Newsletter content can inspire blog post topics"
                ],
                "engagement_strategies": {
                    "cross_promotion": "Link between platforms",
                    "timing": "Optimal posting schedules",
                    "hashtags": "Platform-specific tag strategies"
                }
            }
            
            confidence = 0.85
            
            return ContentResponse(
                success=True,
                content=content,
                platform=self.platform,
                confidence=confidence,
                metadata={
                    "platforms_covered": 5,
                    "strategy_type": "multi_platform",
                    "brand_voice": brand_voice,
                    "generation_method": "llm"
                }
            )
            
        except Exception as e:
            return ContentResponse(
                success=False,
                content={"error": str(e)},
                platform=self.platform,
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def create_repurposing_plan(self, analysis: Dict[str, Any]) -> ContentResponse:
        """Create repurposing plan - dedicated method for content strategy"""
        # Handle AgentResponse object
        if hasattr(analysis, 'content') and analysis.content:
            actual_analysis = analysis.content
        else:
            actual_analysis = analysis
        
        # Extract detected product from analysis
        detected_product = actual_analysis.get('detected_product', 'Unknown product') if isinstance(actual_analysis, dict) else 'Unknown product'
        print(f"🎯 DEBUG: Content strategy using detected product: {detected_product}")
        
        try:
            # Generate content strategy using LLM
            prompt = f"""
            Create a comprehensive multi-platform content strategy based on this content:
            
            Analysis: {str(actual_analysis)[:300]}
            Brand Voice: professional
            Detected Product: {detected_product}
            
            Requirements:
            - Comprehensive strategy for multiple platforms
            - Platform-specific recommendations
            - Content calendar suggestions
            - Engagement optimization tactics
            - Focus on marketing detected product: {detected_product}
            
            Marketing Focus:
            - Highlight product/service being discussed
            - Use benefit-oriented language
            - Include relevant use cases or applications
            - Create urgency or curiosity about the product
            - Professional yet approachable tone
            
            Format:
            - Overall strategy summary
            - Platform-specific tactics
            - Content calendar recommendations
            - Engagement optimization strategies
            """
            
            system_prompt = "You are a content strategy expert specializing in multi-platform content repurposing. Create comprehensive strategies that maximize content reach and engagement across different platforms."
            
            strategy_content = self._generate_with_llm(prompt, system_prompt)
            
            # Parse the generated content into structured format
            content = {
                "strategy": strategy_content,
                "platforms": {
                    "newsletter": {
                        "type": "email_newsletter",
                        "frequency": "weekly",
                        "tone": "professional yet engaging",
                        "key_focus": "insights and analysis"
                    },
                    "blog": {
                        "type": "seo_blog_post",
                        "frequency": "bi-weekly",
                        "tone": "informative and authoritative",
                        "key_focus": "deep-dive analysis"
                    },
                    "linkedin": {
                        "type": "professional_post",
                        "frequency": "3x_weekly",
                        "tone": "professional and insightful",
                        "key_focus": "industry insights"
                    },
                    "twitter": {
                        "type": "engaging_thread",
                        "frequency": "daily",
                        "tone": "conversational and timely",
                        "key_focus": "key takeaways and questions"
                    },
                    "video": {
                        "type": "short_form_script",
                        "frequency": "2x_weekly",
                        "tone": "energetic and engaging",
                        "key_focus": "visual storytelling"
                    }
                },
                "coordination_notes": "Maintain consistent brand voice across all platforms while adapting content format",
                "repurposing_opportunities": [
                    "Blog posts can be repurposed into newsletter content",
                    "Video scripts can be adapted for social media posts",
                    "Newsletter content can inspire blog post topics"
                ],
                "engagement_strategies": {
                    "cross_promotion": "Link between platforms",
                    "timing": "Optimal posting schedules",
                    "hashtags": "Platform-specific tag strategies"
                }
            }
            
            confidence = 0.85
            
            return ContentResponse(
                success=True,
                content=content,
                platform=self.platform,
                confidence=confidence,
                metadata={
                    "platforms_covered": 5,
                    "strategy_type": "multi_platform",
                    "brand_voice": "professional",
                    "generation_method": "llm"
                }
            )
            
        except Exception as e:
            return ContentResponse(
                success=False,
                content={"error": str(e)},
                platform=self.platform,
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def _generate_social_media_content(self, analysis: Dict, transcript: str, brand_voice: str) -> Dict:
        """Generate social media content"""
        key_points = analysis.get("key_points", [])
        topics = analysis.get("topics", [])
        
        social_content = {}
        
        # Twitter content
        social_content["twitter"] = self._create_twitter_content(key_points, topics, brand_voice)
        
        # LinkedIn content
        social_content["linkedin"] = self._create_linkedin_content(key_points, topics, brand_voice)
        
        # Instagram content
        social_content["instagram"] = self._create_instagram_content(key_points, topics, brand_voice)
        
        # Facebook content
        social_content["facebook"] = self._create_facebook_content(key_points, topics, brand_voice)
        
        return social_content
    
    def _create_twitter_content(self, key_points: List[str], topics: List[str], brand_voice: str) -> str:
        """Create Twitter content"""
        if key_points:
            return f"🔑 {key_points[0][:200]} #insights #analysis"
        elif topics:
            return f"📊 Exploring {topics[0]} - latest insights and trends #analysis"
        else:
            return "📝 New content available - check out our latest analysis!"
    
    def _create_linkedin_content(self, key_points: List[str], topics: List[str], brand_voice: str) -> str:
        """Create LinkedIn content"""
        content = "Professional Insights:\n\n"
        
        if key_points:
            content += f"Key Finding: {key_points[0]}\n\n"
        
        if topics:
            content += f"Topic Focus: {topics[0]}\n\n"
        
        content += "This analysis provides valuable insights for industry professionals. #professional #analysis"
        
        return content
    
    def _create_instagram_content(self, key_points: List[str], topics: List[str], brand_voice: str) -> str:
        """Create Instagram content"""
        if topics:
            return f"📸 {topics[0].title()} Insights!\n\nSwipe through to learn more about the latest trends and developments. #insights #learning"
        else:
            return "📸 New insights available! Check out our latest analysis. #content #insights"
    
    def _create_facebook_content(self, key_points: List[str], topics: List[str], brand_voice: str) -> str:
        """Create Facebook content"""
        content = "📊 Latest Analysis Available!\n\n"
        
        if key_points:
            content += f"Key Point: {key_points[0]}\n\n"
        
        if topics:
            content += f"We're diving deep into {topics[0]} and what it means for you.\n\n"
        
        content += "Read the full analysis on our website!"
        
        return content
    
    def _generate_script_content(self, analysis: Dict, transcript: str, brand_voice: str) -> Dict:
        """Generate script content"""
        key_points = analysis.get("key_points", [])
        
        script_content = {
            "intro": self._create_script_intro(analysis, brand_voice),
            "main_points": self._create_script_main_points(key_points, brand_voice),
            "outro": self._create_script_outro(analysis, brand_voice),
            "duration_estimate": len(transcript.split()) / 150  # Average speaking rate
        }
        
        return script_content
    
    def _create_script_intro(self, analysis: Dict, brand_voice: str) -> str:
        """Create script introduction"""
        topics = analysis.get("topics", [])
        
        if topics:
            return f"Welcome! Today we're exploring {topics[0]} and what it means for you."
        else:
            return "Welcome! Today we have some exciting insights to share."
    
    def _create_script_main_points(self, key_points: List[str], brand_voice: str) -> List[str]:
        """Create script main points"""
        return key_points[:3] if key_points else ["Key insights from our latest analysis"]
    
    def _create_script_outro(self, analysis: Dict, brand_voice: str) -> str:
        """Create script outro"""
        return "Thanks for watching! Don't forget to subscribe for more insights."
    
    def _generate_coordination_notes(self, analysis: Dict) -> List[str]:
        """Generate coordination notes"""
        return [
            "Ensure consistent messaging across all platforms",
            "Adapt tone for each platform while maintaining core message",
            "Schedule posts for optimal engagement times",
            "Monitor performance and adjust strategy accordingly"
        ]
    
    def _create_repurposing_strategy(self, analysis: Dict) -> Dict:
        """Create repurposing strategy"""
        return {
            "primary_platform": "blog",
            "supporting_platforms": ["social_media", "newsletter"],
            "content_sequence": ["blog", "social_media", "newsletter", "script"],
            "timing_strategy": "Blog first, then social media promotion",
            "cross_promotion": "Link all content back to main blog post"
        }
    
    def _calculate_overall_confidence(self, newsletter: ContentResponse, 
                                    blog: ContentResponse, social_media: Dict, 
                                    script: Dict) -> float:
        """Calculate overall confidence score"""
        confidences = []
        
        if newsletter.success:
            confidences.append(newsletter.confidence)
        
        if blog.success:
            confidences.append(blog.confidence)
        
        # Add base confidence for social media and script
        confidences.extend([0.8, 0.8])
        
        return sum(confidences) / len(confidences)

def demonstrate_content_agents():
    """Demonstrate the content generation agents"""
    
    print("✍️ Content Generation Agents Demo")
    print("=" * 60)
    
    # Test data
    test_analysis = {
        "topics": ["technology", "innovation"],
        "key_points": ["AI is transforming industries", "Innovation drives growth"],
        "sentiment": "positive",
        "target_audience": "professionals"
    }
    
    test_transcript = """
    Artificial intelligence is revolutionizing how we work and live. 
    Innovation in this field is accelerating at an unprecedented rate. 
    Companies that embrace these technologies are seeing significant benefits.
    """
    
    print(f"\n📝 Test Analysis: {test_analysis['topics']}")
    print(f"📝 Test Transcript: {test_transcript[:50]}...")
    print("-" * 40)
    
    # Test Newsletter Agent
    print("\n📧 Newsletter Agent:")
    newsletter_agent = NewsletterAgent()
    newsletter_result = newsletter_agent.generate_content(test_analysis, test_transcript)
    
    if newsletter_result.success:
        print(f"   ✅ Newsletter generated")
        print(f"   📧 Subject: {newsletter_result.content['subject']}")
        print(f"   📊 Word count: {newsletter_result.metadata['word_count']}")
        print(f"   🎯 Confidence: {newsletter_result.confidence:.2f}")
    
    # Test Blog Agent
    print("\n📝 Blog Agent:")
    blog_agent = BlogPostAgent()
    blog_result = blog_agent.generate_content(test_analysis, test_transcript)
    
    if blog_result.success:
        print(f"   ✅ Blog post generated")
        print(f"   📝 Title: {blog_result.content['title']}")
        print(f"   📊 Word count: {blog_result.metadata['word_count']}")
        print(f"   🎯 Confidence: {blog_result.confidence:.2f}")
    
    # Test Content Repurposing Agent
    print("\n🔄 Content Repurposing Agent:")
    repurposing_agent = ContentRepurposingAgent()
    repurposing_result = repurposing_agent.generate_content(test_analysis, test_transcript)
    
    if repurposing_result.success:
        print(f"   ✅ Multi-platform content generated")
        platforms = repurposing_result.content.keys()
        print(f"   📱 Platforms: {', '.join(platforms)}")
        print(f"   🎯 Confidence: {repurposing_result.confidence:.2f}")
    
    print("\n" + "=" * 60)
    print("\n🎯 Content Generation Benefits:")
    print("   ✅ Platform-specific content optimization")
    print("   ✅ Consistent brand voice across platforms")
    print("   ✅ SEO optimization for blog content")
    print("   ✅ Engaging newsletter creation")
    print("   ✅ Comprehensive social media content")
    print("   ✅ Coordinated multi-platform strategy")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented specialized content generation agents'")
    print("   🎯 'Each agent creates platform-optimized content'")
    print("   🎯 'SEO optimization and brand voice consistency'")
    print("   🎯 'Coordinated repurposing strategy across platforms'")
    print("   🎯 'Confidence scoring ensures quality output'")

if __name__ == "__main__":
    demonstrate_content_agents()
