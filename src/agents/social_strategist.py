"""
Social Media Strategist Agent - Modular version for social media content creation
Refactored from the original agents.py to use the new agentic architecture
"""

from typing import Dict, Any, List, Optional
import re

from .base import SynthesisAgent
from ..schema.models import AgentResponse, SocialMediaContent, LogLevel

class SocialStrategistAgent(SynthesisAgent):
    """Creates platform-specific social media content"""
    
    def __init__(self):
        super().__init__(
            agent_name="social_strategist",
            description="Creates platform-specific social media content with engagement optimization"
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
        """Create social media content from analysis"""
        
        await self.update_state(self.state.status.__class__.THINKING, "social_content_creation")
        
        try:
            # Extract required data
            content = self._extract_content(input_data)
            analysis = self._extract_analysis(input_data)
            detected_product = input_data.get('detected_product')
            
            if not content:
                return self.create_response(
                    success=False,
                    content=None,
                    confidence=0.0,
                    reasoning="No content provided for social media creation",
                    suggestions=["Please provide transcript or text content"]
                )
            
            await self.plan(f"Creating social media content for detected product: {detected_product}")
            
            # Create content for different platforms
            social_content = {}
            
            # LinkedIn content
            linkedin_content = await self._create_linkedin_content(content, analysis, detected_product)
            if linkedin_content:
                social_content['linkedin'] = linkedin_content
            
            # Twitter content
            twitter_content = await self._create_twitter_content(content, analysis, detected_product)
            if twitter_content:
                social_content['twitter'] = twitter_content
            
            # Facebook content (optional)
            facebook_content = await self._create_facebook_content(content, analysis, detected_product)
            if facebook_content:
                social_content['facebook'] = facebook_content
            
            await self.reason("Social media content creation completed",
                            context={
                                "platforms_created": list(social_content.keys()),
                                "total_content_pieces": len(social_content)
                            })
            
            return self.create_response(
                success=True,
                content=social_content,
                confidence=0.8,
                reasoning="Social media content created for multiple platforms with platform-specific optimization",
                suggestions=self._generate_suggestions(social_content)
            )
            
        except Exception as e:
            await self.logger.error("Social media content creation failed", e)
            return self.create_response(
                success=False,
                content=None,
                confidence=0.0,
                reasoning=f"Social media creation failed: {str(e)}",
                suggestions=["Check content format and try again"]
            )
    
    def _extract_content(self, input_data: Dict[str, Any]) -> str:
        """Extract text content from input data"""
        if 'transcript' in input_data:
            return input_data['transcript']
        elif 'content' in input_data:
            if isinstance(input_data['content'], str):
                return input_data['content']
            elif hasattr(input_data['content'], 'content'):
                return str(input_data['content'].content)
        return ""
    
    def _extract_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract analysis data from input"""
        if 'analysis' in input_data:
            analysis = input_data['analysis']
            if hasattr(analysis, 'content'):
                return analysis.content
            elif isinstance(analysis, dict):
                return analysis
        return {}
    
    async def _create_linkedin_content(self, content: str, analysis: Dict[str, Any], 
                                      detected_product: Optional[str]) -> Optional[SocialMediaContent]:
        """Create LinkedIn-optimized content"""
        
        await self.reason("Creating LinkedIn content")
        
        try:
            # Use tool for content generation
            tool_response = await self.call_tool(
                "generate_social_content",
                {
                    "content": content,
                    "platform": "linkedin",
                    "tone": "professional"
                }
            )
            
            if tool_response.success:
                generated_content = tool_response.result.get('content', '')
                
                # Enhance with product mention
                if detected_product:
                    generated_content = self._add_product_mention(generated_content, detected_product, "linkedin")
                
                # Add hashtags
                hashtags = self._generate_hashtags(content, detected_product, "linkedin")
                final_content = f"{generated_content}\n\n{hashtags}"
                
                linkedin_post = SocialMediaContent(
                    platform="linkedin",
                    content_type="post",
                    content=final_content,
                    hashtags=hashtags.split(),
                    mentions=self._extract_mentions(content),
                    character_count=len(final_content)
                )
                
                await self.reflect(f"LinkedIn content created: {linkedin_post.character_count} characters")
                return linkedin_post
                
        except Exception as e:
            await self.logger.warning("LinkedIn content creation failed", data={"error": str(e)})
        
        return None
    
    async def _create_twitter_content(self, content: str, analysis: Dict[str, Any], 
                                     detected_product: Optional[str]) -> Optional[SocialMediaContent]:
        """Create Twitter-optimized content"""
        
        await self.reason("Creating Twitter content")
        
        try:
            # Extract key points for tweets
            key_points = analysis.get('key_points', [])
            if not key_points:
                # Fallback to extracting key points
                sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
                key_points = sentences[:3]
            
            # Create tweet thread
            tweets = []
            
            # First tweet - hook
            hook = self._create_twitter_hook(content, detected_product)
            tweets.append(hook)
            
            # Additional tweets with key points
            for i, point in enumerate(key_points[:2]):  # Max 2 additional tweets
                tweet = self._format_tweet_content(point, detected_product, i + 2)
                tweets.append(tweet)
            
            # Combine into thread format
            thread_content = '\n---\n'.join(tweets)
            
            twitter_thread = SocialMediaContent(
                platform="twitter",
                content_type="thread",
                content=thread_content,
                hashtags=self._generate_hashtags(content, detected_product, "twitter").split(),
                mentions=self._extract_mentions(content),
                character_count=len(thread_content)
            )
            
            await self.reflect(f"Twitter thread created: {len(tweets)} tweets")
            return twitter_thread
            
        except Exception as e:
            await self.logger.warning("Twitter content creation failed", data={"error": str(e)})
        
        return None
    
    async def _create_facebook_content(self, content: str, analysis: Dict[str, Any], 
                                      detected_product: Optional[str]) -> Optional[SocialMediaContent]:
        """Create Facebook-optimized content"""
        
        await self.reason("Creating Facebook content")
        
        try:
            # Use tool for content generation
            tool_response = await self.call_tool(
                "generate_social_content",
                {
                    "content": content,
                    "platform": "facebook",
                    "tone": "conversational"
                }
            )
            
            if tool_response.success:
                generated_content = tool_response.result.get('content', '')
                
                # Enhance with product mention
                if detected_product:
                    generated_content = self._add_product_mention(generated_content, detected_product, "facebook")
                
                # Add engagement question
                if not generated_content.endswith('?'):
                    generated_content += "\n\nWhat are your thoughts on this?"
                
                facebook_post = SocialMediaContent(
                    platform="facebook",
                    content_type="post",
                    content=generated_content,
                    hashtags=self._generate_hashtags(content, detected_product, "facebook").split(),
                    mentions=self._extract_mentions(content),
                    character_count=len(generated_content)
                )
                
                await self.reflect(f"Facebook content created: {facebook_post.character_count} characters")
                return facebook_post
                
        except Exception as e:
            await self.logger.warning("Facebook content creation failed", data={"error": str(e)})
        
        return None
    
    def _create_twitter_hook(self, content: str, detected_product: Optional[str]) -> str:
        """Create an engaging hook for Twitter"""
        
        # Extract first compelling sentence or create hook
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 10]
        
        if sentences:
            hook = sentences[0]
            # Truncate if too long
            if len(hook) > 200:
                hook = hook[:197] + "..."
        else:
            # Create generic hook
            hook = f"Exciting insights to share!"
        
        # Add product mention if available
        if detected_product:
            hook = f"🚀 {detected_product}: {hook}"
        
        # Add emoji for engagement
        if not any(emoji in hook for emoji in ['🚀', '💡', '🔥', '⚡', '🎯']):
            hook = f"💡 {hook}"
        
        return hook
    
    def _format_tweet_content(self, point: str, detected_product: Optional[str], tweet_num: int) -> str:
        """Format content for a specific tweet in thread"""
        
        # Clean up the point
        point = point.strip()
        if point.endswith('.'):
            point = point[:-1]
        
        # Add tweet number
        formatted = f"{tweet_num}/{3}: {point}"
        
        # Add product mention if available and not already mentioned
        if detected_product and detected_product.lower() not in point.lower():
            formatted += f" #{detected_product.replace(' ', '')}"
        
        # Ensure it's within Twitter limit
        if len(formatted) > 280:
            formatted = formatted[:277] + "..."
        
        return formatted
    
    def _add_product_mention(self, content: str, product: str, platform: str) -> str:
        """Add product mention to content in platform-appropriate way"""
        
        if platform == "linkedin":
            # Professional mention
            if product.lower() not in content.lower():
                content = f"🔹 {product}: {content}"
        elif platform == "facebook":
            # Conversational mention
            if product.lower() not in content.lower():
                content = f"Talking about {product}! {content}"
        elif platform == "twitter":
            # Hashtag or mention
            if product.lower() not in content.lower():
                content = f"#{product.replace(' ', '')} {content}"
        
        return content
    
    def _generate_hashtags(self, content: str, detected_product: Optional[str], platform: str) -> str:
        """Generate relevant hashtags"""
        
        hashtags = []
        
        # Product hashtag
        if detected_product:
            if platform == "linkedin":
                hashtags.append(detected_product.replace(' ', ''))
            else:
                hashtags.append(f"#{detected_product.replace(' ', '')}")
        
        # Content-based hashtags
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['ai', 'artificial intelligence', 'machine learning']):
            hashtags.append("#AI" if platform != "linkedin" else "AI")
        
        if any(word in content_lower for word in ['technology', 'tech', 'innovation']):
            hashtags.append("#Technology" if platform != "linkedin" else "Technology")
        
        if any(word in content_lower for word in ['business', 'professional', 'career']):
            hashtags.append("#Business" if platform != "linkedin" else "Business")
        
        if any(word in content_lower for word in ['marketing', 'social media']):
            hashtags.append("#Marketing" if platform != "linkedin" else "Marketing")
        
        # Platform-specific hashtags
        if platform == "linkedin":
            hashtags.extend(["Professional", "Insights", "Leadership"])
        elif platform == "twitter":
            hashtags.extend(["#Innovation", "#Future", "#Tech"])
        elif platform == "facebook":
            hashtags.extend(["#Community", "#Discussion", "#Share"])
        
        # Limit hashtags
        max_hashtags = 5 if platform == "linkedin" else 3
        hashtags = hashtags[:max_hashtags]
        
        return ' '.join(hashtags)
    
    def _extract_mentions(self, content: str) -> List[str]:
        """Extract potential @mentions from content"""
        
        # Look for proper nouns that could be mentions
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        # Filter out common words that aren't mentions
        non_mentions = {'The', 'This', 'That', 'These', 'Those', 'I', 'You', 'We', 'They'}
        mentions = [word for word in words if word not in non_mentions and len(word) > 2]
        
        return mentions[:3]  # Limit to 3 mentions
    
    def _generate_suggestions(self, social_content: Dict[str, SocialMediaContent]) -> List[str]:
        """Generate suggestions based on created content"""
        
        suggestions = []
        
        if len(social_content) == 0:
            suggestions.append("No social media content was generated")
        elif len(social_content) == 1:
            suggestions.append("Consider creating content for additional platforms")
        else:
            suggestions.append("Great multi-platform content strategy!")
        
        # Platform-specific suggestions
        for platform, content in social_content.items():
            if platform == "twitter" and content.character_count > 280:
                suggestions.append(f"Twitter content exceeds character limit ({content.character_count} > 280)")
            elif platform == "linkedin" and content.character_count < 100:
                suggestions.append("LinkedIn content could be more detailed")
        
        if not suggestions:
            suggestions.append("Social media content looks engaging and well-optimized!")
        
        return suggestions
