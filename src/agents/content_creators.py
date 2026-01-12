"""
Script Doctor Agent - Specialized agent for script creation and optimization
Converted from legacy agents.py to use the new agentic architecture
"""

from typing import Dict, Any, List, Optional
import re

from .base import SynthesisAgent
from ..schema.models import AgentResponse, ScriptContent, LogLevel
from ..config.manager import system_prompts

class ScriptDoctorAgent(SynthesisAgent):
    """Creates and refines content scripts for better engagement"""
    
    def __init__(self):
        super().__init__(
            agent_name="script_doctor",
            description="Improves and refines content scripts for better engagement"
        )
    
    async def create(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create content - alternative to synthesize"""
        return await self.synthesize(input_data)
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Default process method calls synthesize or create"""
        if hasattr(self, 'synthesize'):
            return await self.synthesize(input_data)
        elif hasattr(self, 'create'):
            return await self.create(input_data)
        else:
            raise ValueError(f"Synthesis agent {self.agent_name} must implement synthesize or create")
    
    async def synthesize(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create short-form scripts from analysis"""
        
        await self.update_state(self.state.status.__class__.THINKING, "script_creation")
        
        try:
            # Extract content and context
            content = self._extract_content(input_data)
            detected_product = input_data.get('detected_product')
            
            if not content:
                return self.create_response(
                    success=False,
                    content=None,
                    confidence=0.0,
                    reasoning="No content provided for script creation",
                    suggestions=["Please provide transcript or analysis data"]
                )
            
            await self.plan(f"Creating short-form script for detected product: {detected_product}")
            
            # Generate script using LLM
            prompt = self._create_script_prompt(content, detected_product)
            script_content = await self.generate_with_llm(prompt)
            
            # Create script content object
            script = ScriptContent(
                script_type="short_form",
                content=script_content,
                estimated_duration="45 seconds",
                platform_suggestions=["TikTok", "Instagram Reels", "YouTube Shorts"],
                visual_cues=self._extract_visual_cues(script_content)
            )
            
            await self.reason("Script creation completed",
                            context={
                                "script_length": len(script_content),
                                "estimated_duration": script.estimated_duration,
                                "platform_suggestions": script.platform_suggestions
                            })
            
            return self.create_response(
                success=True,
                content=script,
                confidence=0.8,
                reasoning="Short-form script created with focus on detected product and engagement",
                suggestions=self._generate_script_suggestions(script)
            )
            
        except Exception as e:
            await self.logger.error("Script creation failed", e)
            return self.create_response(
                success=False,
                content=None,
                confidence=0.0,
                reasoning=f"Script creation failed: {str(e)}",
                suggestions=["Check content format and try again"]
            )
    
    async def create_short_scripts(self, analysis: Dict[str, Any]) -> AgentResponse:
        """Legacy compatibility method - alias for synthesize"""
        return await self.synthesize(analysis)
    
    def _extract_content(self, input_data: Dict[str, Any]) -> str:
        """Extract transcript content from analysis object"""
        
        if 'transcript' in input_data:
            return input_data['transcript']
        elif 'content' in input_data:
            if isinstance(input_data['content'], str):
                return input_data['content']
            elif isinstance(input_data['content'], dict):
                return input_data['content'].get('transcript', '')
        return ""
    
    def _create_script_prompt(self, content: str, detected_product: Optional[str]) -> str:
        """Create a comprehensive prompt for script generation"""
        
        # Limit content to avoid token limits
        content_preview = content[:1000] if len(content) > 1000 else content
        
        prompt = f"""Create an engaging short-form script based on this content:
        
        {content_preview}
        
        Requirements:
        - Convert to conversational, engaging script format
        - Include hook, main content, and call-to-action
        - Optimize for short-form video platforms (TikTok, Reels, Shorts)
        - 30-60 seconds read time
        - Include visual cues and pacing notes
        - Make it shareable and engaging
        - Focus on marketing the detected product: {detected_product}
        
        Marketing Focus:
        - Highlight the product/service being discussed
        - Use benefit-oriented language
        - Include relevant use cases or applications
        - Create urgency or curiosity about the product
        - Make it compelling for short-form video
        
        Format the script with clear sections:
        [HOOK] - Opening attention-grabber
        [MAIN] - Core content with key points
        [CTA] - Call to action
        
        Platform Considerations:
        - TikTok: Fast-paced, trending sounds, quick cuts
        - Instagram Reels: Visual-first, aesthetic appeal
        - YouTube Shorts: Educational value, retention hooks"""
        
        return prompt
    
    def _extract_visual_cues(self, script_content: str) -> List[str]:
        """Extract visual cues from script content"""
        
        visual_cues = []
        
        # Look for visual indicators in the script
        visual_patterns = [
            r'\[VISUAL:\s*([^\]]+)\]',  # [VISUAL: description]
            r'\[SCENE:\s*([^\]]+)\]',  # [SCENE: description]
            r'\[CAMERA:\s*([^\]]+)\]', # [CAMERA: instruction]
            r'\[GRAPHIC:\s*([^\]]+)\]', # [GRAPHIC: description]
            r'\[TEXT:\s*([^\]]+)\]',   # [TEXT: on-screen text]
        ]
        
        for pattern in visual_patterns:
            matches = re.findall(pattern, script_content, re.IGNORECASE)
            visual_cues.extend(matches)
        
        # Look for action words that suggest visuals
        action_words = ['show', 'display', 'demonstrate', 'reveal', 'present', 'highlight', 'feature', 'showcase']
        lines = script_content.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in action_words):
                # Extract the part with the action word
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() in action_words:
                        # Get context around the action word
                        start = max(0, i - 2)
                        end = min(len(words), i + 3)
                        context = ' '.join(words[start:end])
                        visual_cues.append(f"Visual: {context}")
                        break
        
        return list(set(visual_cues))  # Remove duplicates
    
    def _generate_script_suggestions(self, script: ScriptContent) -> List[str]:
        """Generate suggestions for script improvement"""
        
        suggestions = []
        
        # Length suggestions
        if len(script.content) < 200:
            suggestions.append("Consider adding more content for better engagement")
        elif len(script.content) > 800:
            suggestions.append("Consider shortening for better retention on short-form platforms")
        
        # Platform suggestions
        if script.platform_suggestions:
            suggestions.append(f"Consider optimizing for: {', '.join(script.platform_suggestions[:3])}")
        
        # Visual cues suggestions
        if len(script.visual_cues) < 3:
            suggestions.append("Add more visual cues to enhance video engagement")
        
        # CTA suggestions
        if "call to action" not in script.content.lower() and "cta" not in script.content.lower():
            suggestions.append("Include a clear call to action")
        
        # Product focus suggestions
        if script.content and "product" not in script.content.lower():
            suggestions.append("Ensure the script focuses on the product/service")
        
        if not suggestions:
            suggestions.append("Script looks engaging and well-structured!")
        
        return suggestions

class NewsletterWriterAgent(SynthesisAgent):
    """Creates professional newsletter content"""
    
    def __init__(self):
        super().__init__(
            agent_name="newsletter_writer",
            description="Creates professional newsletter content with engagement optimization"
        )
    
    async def synthesize(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Synthesize content - alternative to create_newsletter"""
        return await self.create_newsletter(input_data)
    
    async def create(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create content - alternative to create_newsletter"""
        return await self.create_newsletter(input_data)
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Default process method calls create_newsletter"""
        return await self.create_newsletter(input_data)
    
    async def create_newsletter(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create newsletter content from analysis"""
        
        await self.update_state(self.state.status.__class__.THINKING, "newsletter_creation")
        
        try:
            # Extract content and context
            content = self._extract_content(input_data)
            detected_product = input_data.get('detected_product')
            brand_voice = input_data.get('brand_voice', 'professional')
            
            if not content:
                return self.create_response(
                    success=False,
                    content=None,
                    confidence=0.0,
                    reasoning="No content provided for newsletter creation",
                    suggestions=["Please provide analysis data with content"]
                )
            
            await self.plan(f"Creating newsletter with {brand_voice} tone for {detected_product}")
            
            # Generate newsletter using LLM
            prompt = self._create_newsletter_prompt(content, detected_product, brand_voice)
            newsletter_content = await self.generate_with_llm(prompt)
            
            # Create newsletter content object
            newsletter = self._parse_newsletter_content(newsletter_content)
            
            await self.reason("Newsletter creation completed")
            
            return self.create_response(
                success=True,
                content=newsletter,
                confidence=0.8,
                reasoning="Newsletter created with professional tone and engagement optimization",
                suggestions=self._generate_newsletter_suggestions(newsletter)
            )
            
        except Exception as e:
            await self.logger.error("Newsletter creation failed", e)
            return self.create_response(
                success=False,
                content=None,
                confidence=0.0,
                reasoning=f"Newsletter creation failed: {str(e)}",
                suggestions=["Check content format and try again"]
            )
    
    def _extract_content(self, input_data: Dict[str, Any]) -> str:
        """Extract content from analysis object"""
        
        if 'content' in input_data:
            if isinstance(input_data['content'], str):
                return input_data['content']
            elif isinstance(input_data['content'], dict):
                # Try to get transcript or main content
                return input_data['content'].get('transcript', '') or input_data['content'].get('content', '')
        return ""
    
    def _create_newsletter_prompt(self, content: str, detected_product: Optional[str], brand_voice: str) -> str:
        """Create a comprehensive prompt for newsletter generation"""
        
        content_preview = content[:800] if len(content) > 800 else content
        
        prompt = f"""Create a professional newsletter based on this content:
        
        {content_preview}
        
        Newsletter Requirements:
        - Professional {brand_voice} tone
        - Compelling subject line with high open rate potential
        - Scannable content with clear hierarchy
        - Strong call-to-action
        - Balance of promotional and value-driven content
        - Personalized feel for subscribers
        
        Structure:
        1. Subject Line (compelling, under 60 characters)
        2. Preview Text (brief, engaging)
        3. Main Content (structured with headings)
        4. Call-to-Action (clear, actionable)
        
        Content Focus:
        - Highlight insights from the content
        - Provide value to subscribers
        - Include relevant use cases or applications
        - Mention {detected_product} where relevant
        - Create engagement opportunities
        
        Tone Guidelines:
        - {brand_voice} and authoritative
        - Conversational yet professional
        - Value-driven, not overly promotional
        - Personal and engaging
        
        Format the response as:
        {{
            "subject": "Subject line here",
            "preview_text": "Preview text here",
            "body_content": "Main newsletter content",
            "call_to_action": "Clear CTA here",
            "sections": ["Section 1", "Section 2", ...]
        }}"""
        
        return prompt
    
    def _parse_newsletter_content(self, content: str) -> Dict[str, Any]:
        """Parse LLM response into newsletter content object"""
        
        try:
            # Try to parse as JSON
            import json
            if content.strip().startswith('{'):
                newsletter_data = json.loads(content)
                return newsletter_data
        except:
            pass
        
        # Fallback: create structured content from plain text
        lines = content.split('\n')
        
        subject = lines[0] if lines else "Newsletter Update"
        preview_text = lines[1] if len(lines) > 1 else "Latest updates and insights"
        body_content = '\n'.join(lines[2:]) if len(lines) > 2 else content
        
        return {
            "subject": subject,
            "preview_text": preview_text,
            "body_content": body_content,
            "call_to_action": "Click here for more information",
            "sections": self._extract_sections(body_content),
            "brand_voice": "professional"
        }
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract sections from newsletter content"""
        
        sections = []
        lines = content.split('\n')
        
        current_section = []
        for line in lines:
            line = line.strip()
            
            # Check if line is a header (starts with # or is short and in caps)
            if (line.startswith('#') or 
                (len(line) < 50 and line.isupper() and line.endswith(':'))):
                
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
                
                current_section.append(line)
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def _generate_newsletter_suggestions(self, newsletter: Dict[str, Any]) -> List[str]:
        """Generate suggestions for newsletter improvement"""
        
        suggestions = []
        
        # Subject line suggestions
        subject = newsletter.get('subject', '')
        if len(subject) > 60:
            suggestions.append("Consider shortening subject line for better open rates")
        elif len(subject) < 20:
            suggestions.append("Consider making subject line more descriptive")
        
        # Content suggestions
        body_content = newsletter.get('body_content', '')
        if len(body_content) < 200:
            suggestions.append("Consider adding more substantial content")
        elif len(body_content) > 2000:
            suggestions.append("Consider breaking up long content for better readability")
        
        # CTA suggestions
        cta = newsletter.get('call_to_action', '')
        if not cta or 'click' not in cta.lower():
            suggestions.append("Add a clear call-to-action")
        
        if not suggestions:
            suggestions.append("Newsletter structure looks good!")
        
        return suggestions

class BlogPostAgent(SynthesisAgent):
    """Creates SEO-optimized blog posts"""
    
    def __init__(self):
        super().__init__(
            agent_name="blog_writer",
            description="Creates SEO-optimized blog posts with professional writing"
        )
    
    async def synthesize(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Synthesize content - alternative to create_blog_post"""
        return await self.create_blog_post(input_data)
    
    async def create(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create content - alternative to create_blog_post"""
        return await self.create_blog_post(input_data)
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Default process method calls create_blog_post"""
        return await self.create_blog_post(input_data)
    
    async def create_blog_post(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create SEO-optimized blog post"""
        
        await self.update_state(self.state.status.__class__.THINKING, "blog_creation")
        
        try:
            content = self._extract_content(input_data)
            detected_product = input_data.get('detected_product')
            brand_voice = input_data.get('brand_voice', 'professional')
            seo_analysis = input_data.get('seo_analysis', {})
            
            if not content:
                return self.create_response(
                    success=False,
                    content=None,
                    confidence=0.0,
                    reasoning="No content provided for blog post creation",
                    suggestions=["Please provide analysis data with content"]
                )
            
            await self.plan(f"Creating SEO-optimized blog post with {brand_voice} tone")
            
            # Generate blog post using LLM
            prompt = self._create_blog_prompt(content, detected_product, brand_voice, seo_analysis)
            blog_content = await self.generate_with_llm(prompt)
            
            # Create blog post object
            blog_post = self._parse_blog_content(blog_content)
            
            await self.reason("Blog post creation completed")
            
            return self.create_response(
                success=True,
                content=blog_post,
                confidence=0.8,
                reasoning="SEO-optimized blog post created with professional writing",
                suggestions=self._generate_blog_suggestions(blog_post)
            )
            
        except Exception as e:
            await self.logger.error("Blog post creation failed", e)
            return self.create_response(
                success=False,
                content=None,
                confidence=0.0,
                reasoning=f"Blog post creation failed: {str(e)}",
                suggestions=["Check content format and try again"]
            )
    
    def _extract_content(self, input_data: Dict[str, Any]) -> str:
        """Extract content from analysis object"""
        
        if 'content' in input_data:
            if isinstance(input_data['content'], str):
                return input_data['content']
            elif isinstance(input_data['content'], dict):
                return input_data['content'].get('transcript', '') or input_data['content'].get('content', '')
        return ""
    
    def _create_blog_prompt(self, content: str, detected_product: Optional[str], 
                          brand_voice: str, seo_analysis: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for blog post generation"""
        
        content_preview = content[:1000] if len(content) > 1000 else content
        primary_keywords = seo_analysis.get('primary_keywords', [])[:5]
        
        prompt = f"""Create an SEO-optimized blog post based on this content:
        
        {content_preview}
        
        Blog Post Requirements:
        - Professional {brand_voice} tone
        - SEO-optimized with keywords: {', '.join(primary_keywords)}
        - Compelling headline and introduction
        - Clear structure with headings
        - 800-1500 words for optimal readability
        - Internal and external linking opportunities
        - Meta description for search engines
        
        SEO Optimization:
        - Include primary keywords naturally
        - Use keyword variations and synonyms
        - Optimize for featured snippets
        - Include relevant internal links
        - Write compelling meta description
        
        Structure:
        1. Headline (H1) - Compelling and keyword-rich
        2. Introduction - Hook readers and state purpose
        3. Main Body - 2-3 sections with subheadings
        4. Conclusion - Summary and call-to-action
        5. Meta Description (150-160 characters)
        
        Content Guidelines:
        - Write for the target audience
        - Include practical examples and insights
        - Mention {detected_product} where relevant
        - Use short paragraphs (2-4 sentences)
        - Include bullet points for readability
        - Add internal links to related content
        
        Format the response as:
        {{
            "title": "Blog post title",
            "slug": "url-friendly-slug",
            "content": "Full blog post content",
            "excerpt": "Brief description",
            "tags": ["tag1", "tag2", ...],
            "category": "category",
            "meta_description": "SEO meta description"
        }}"""
        
        return prompt
    
    def _parse_blog_content(self, content: str) -> Dict[str, Any]:
        """Parse LLM response into blog post object"""
        
        try:
            # Try to parse as JSON
            import json
            if content.strip().startswith('{'):
                blog_data = json.loads(content)
                return blog_data
        except:
            pass
        
        # Fallback: create structured content from plain text
        lines = content.split('\n')
        
        title = lines[0] if lines else "Blog Post"
        blog_content = '\n'.join(lines[1:]) if len(lines) > 1 else content
        
        # Generate slug from title
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug.strip())
        
        # Generate excerpt
        excerpt = blog_content[:200] + "..." if len(blog_content) > 200 else blog_content
        
        # Generate meta description
        meta_description = blog_content[:150] + "..." if len(blog_content) > 150 else blog_content
        
        return {
            "title": title,
            "slug": slug,
            "content": blog_content,
            "excerpt": excerpt,
            "tags": ["blog", "content", "insights"],
            "category": "content-marketing",
            "meta_description": meta_description
        }
    
    def _generate_blog_suggestions(self, blog_post: Dict[str, Any]) -> List[str]:
        """Generate suggestions for blog post improvement"""
        
        suggestions = []
        
        # Title suggestions
        title = blog_post.get('title', '')
        if len(title) < 30:
            suggestions.append("Consider making title more descriptive for SEO")
        elif len(title) > 60:
            suggestions.append("Consider shortening title for better display")
        
        # Content suggestions
        content = blog_post.get('content', '')
        if len(content) < 500:
            suggestions.append("Consider adding more substantial content")
        elif len(content) > 2000:
            suggestions.append("Consider breaking up long content for better readability")
        
        # Meta description suggestions
        meta_desc = blog_post.get('meta_description', '')
        if len(meta_desc) < 120:
            suggestions.append("Consider expanding meta description for better SEO")
        elif len(meta_desc) > 160:
            suggestions.append("Consider shortening meta description to 150-160 characters")
        
        if not suggestions:
            suggestions.append("Blog post structure looks good!")
        
        return suggestions
