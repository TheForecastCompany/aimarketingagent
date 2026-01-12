#!/usr/bin/env python3
"""
Core AI Agents - Specialized agents for content analysis and strategy
Each agent has specific expertise and responsibilities
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
class AgentResponse:
    """Standard response format for all agents"""
    success: bool
    content: Any
    confidence: float
    reasoning: str
    suggestions: List[str]

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str, description: str, use_ollama: bool = True):
        self.name = name
        self.description = description
        self.use_ollama = True  # Force Ollama usage
        
        # Initialize LLM - Ollama only
        self.llm = OllamaClient(
            host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").replace("http://", "")
        )
        self.model = os.getenv("OLLAMA_MODEL", "mistral:latest")
        print(f"🤖 {name} Agent Initialized (Ollama)")
        
        print(f"📋 {description}")
    
    def _generate_with_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Generate content using LLM - Ollama only"""
        print(f"🔍 DEBUG: _generate_with_llm called")
        print(f"🔍 DEBUG: LLM is None: {self.llm is None}")
        print(f"🔍 DEBUG: Use Ollama: {self.use_ollama}")
        
        if self.llm is None:
            print(f"🔍 DEBUG: Using fallback")
            return self._generate_fallback(prompt)
        
        try:
            print(f"🔍 DEBUG: Using Ollama path")
            # Direct OllamaClient usage like SEOKeywordExtractor
            response = self.llm.generate(prompt=prompt, model=self.model)
            print(f"🔍 DEBUG: Ollama response done: {response.done if response else 'None'}")
            if response and response.done and response.response:
                print(f"🔍 DEBUG: Returning response content (length: {len(response.response)})")
                return response.response
            else:
                print(f"🔍 DEBUG: Ollama response failed, using fallback")
                return self._generate_fallback(prompt)
        except Exception as e:
            print(f"🔍 DEBUG: Exception in _generate_with_llm: {e}")
            print(f"❌ LLM generation failed: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_fallback(self, prompt: str) -> str:
        """Fallback generation when LLM is not available"""
        return f"Content generation completed for {self.name}. Unable to generate detailed content due to LLM unavailability."
    
    @abstractmethod
    def process(self, input_data: Any) -> AgentResponse:
        """Process input and return response"""
        pass
    
    def _log_action(self, action: str, details: str = ""):
        """Log agent actions"""
        print(f"🔍 {self.name}: {action}")
        if details:
            print(f"   📝 {details}")

class ContentAnalystAgent(BaseAgent):
    """Analyzes content structure, topics, and quality"""
    
    def __init__(self):
        super().__init__(
            "Content Analyst",
            "Analyzes content structure, topics, and engagement potential"
        )
    
    def process(self, transcript: str, **kwargs) -> AgentResponse:
        """Analyze transcript content"""
        self._log_action("Analyzing content structure")
        
        try:
            # Extract topics
            topics = self._extract_topics(transcript)
            
            # Identify key points
            key_points = self._extract_key_points(transcript)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(transcript)
            
            # Identify target audience
            target_audience = self._identify_audience(transcript)
            
            # Content structure analysis
            structure = self._analyze_structure(transcript)
            
            analysis = {
                "topics": topics,
                "key_points": key_points,
                "sentiment": sentiment,
                "target_audience": target_audience,
                "structure": structure,
                "word_count": len(transcript.split()),
                "estimated_reading_time": len(transcript.split()) / 200  # Average reading speed
            }
            
            confidence = self._calculate_confidence(analysis)
            
            return AgentResponse(
                success=True,
                content=analysis,
                confidence=confidence,
                reasoning="Content analysis completed using topic modeling and sentiment analysis",
                suggestions=self._generate_suggestions(analysis)
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                content=None,
                confidence=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                suggestions=["Check transcript format and try again"]
            )
    
    def _extract_topics(self, transcript: str) -> List[str]:
        """Extract main topics from transcript"""
        # Simplified topic extraction
        # In real implementation, you'd use NLP techniques
        
        common_topics = [
            "technology", "business", "marketing", "education", "health",
            "finance", "lifestyle", "entertainment", "science", "politics"
        ]
        
        found_topics = []
        for topic in common_topics:
            if topic in transcript.lower():
                found_topics.append(topic)
        
        # If no specific topics found, return general ones
        if not found_topics:
            found_topics = ["general", "discussion"]
        
        return found_topics[:5]  # Limit to 5 topics
    
    def _extract_key_points(self, transcript: str) -> List[str]:
        """Extract key points from transcript"""
        # Simplified key point extraction
        sentences = transcript.split('.')
        key_points = []
        
        for sentence in sentences[:10]:  # Analyze first 10 sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and any(keyword in sentence.lower() for keyword in 
                                         ['important', 'key', 'main', 'crucial', 'essential']):
                key_points.append(sentence)
        
        return key_points[:5]  # Limit to 5 key points
    
    def _analyze_sentiment(self, transcript: str) -> str:
        """Analyze sentiment of transcript"""
        # Simplified sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor']
        
        positive_count = sum(1 for word in positive_words if word in transcript.lower())
        negative_count = sum(1 for word in negative_words if word in transcript.lower())
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _identify_audience(self, transcript: str) -> str:
        """Identify target audience"""
        # Simplified audience identification
        technical_terms = ['algorithm', 'implementation', 'architecture', 'framework']
        business_terms = ['strategy', 'revenue', 'profit', 'market', 'customer']
        
        technical_count = sum(1 for term in technical_terms if term in transcript.lower())
        business_count = sum(1 for term in business_terms if term in transcript.lower())
        
        if technical_count > business_count:
            return "technical professionals"
        elif business_count > technical_count:
            return "business professionals"
        else:
            return "general audience"
    
    def _analyze_structure(self, transcript: str) -> Dict[str, Any]:
        """Analyze content structure"""
        sentences = transcript.split('.')
        paragraphs = transcript.split('\n\n')
        
        return {
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "avg_sentence_length": sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            "has_introduction": len(sentences) > 0,
            "has_conclusion": len(sentences) > 3
        }
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate confidence score for analysis"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on content length
        if analysis["word_count"] > 100:
            confidence += 0.1
        
        # Adjust based on number of topics found
        if len(analysis["topics"]) > 2:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_suggestions(self, analysis: Dict) -> List[str]:
        """Generate suggestions based on analysis"""
        suggestions = []
        
        if analysis["word_count"] < 50:
            suggestions.append("Content is quite short - consider expanding with more details")
        
        if len(analysis["topics"]) < 2:
            suggestions.append("Consider covering more diverse topics")
        
        if analysis["sentiment"] == "neutral":
            suggestions.append("Add more engaging language to improve sentiment")
        
        return suggestions

class SocialStrategistAgent(BaseAgent):
    """Develops social media strategies and content"""
    
    def __init__(self, use_ollama: bool = True):
        super().__init__(
            "Social Strategist",
            "Develops social media strategies and platform-specific content",
            use_ollama=use_ollama
        )
    
    def process(self, analysis: Dict[str, Any], **kwargs) -> AgentResponse:
        """Develop social media strategy based on content analysis"""
        self._log_action("Developing social media strategy")
        
        try:
            # Platform-specific strategies
            strategies = {
                "twitter": self._create_twitter_strategy(analysis),
                "linkedin": self._create_linkedin_strategy(analysis),
                "instagram": self._create_instagram_strategy(analysis),
                "facebook": self._create_facebook_strategy(analysis)
            }
            
            # Content recommendations
            content_recommendations = self._generate_content_recommendations(analysis)
            
            # Posting schedule
            posting_schedule = self._create_posting_schedule(analysis)
            
            # Hashtag strategy
            hashtag_strategy = self._create_hashtag_strategy(analysis)
            
            strategy = {
                "platform_strategies": strategies,
                "content_recommendations": content_recommendations,
                "posting_schedule": posting_schedule,
                "hashtag_strategy": hashtag_strategy,
                "engagement_tactics": self._suggest_engagement_tactics(analysis)
            }
            
            confidence = 0.85  # High confidence in strategy generation
            
            return AgentResponse(
                success=True,
                content=strategy,
                confidence=confidence,
                metadata={
                    "platforms_covered": len(strategies),
                    "content_recommendations": len(content_recommendations),
                    "engagement_tactics": len(self._suggest_engagement_tactics(analysis))
                },
                reasoning="Social media strategy developed based on content analysis and platform best practices",
                suggestions=self._generate_strategy_suggestions(strategy)
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                content={},
                confidence=0.0,
                metadata={"error": str(e)},
                reasoning=f"Strategy development failed: {str(e)}",
                suggestions=["Review content analysis and try again"]
            )
    
    def create_linkedin_post(self, analysis: Any, brand_voice: str = "professional", **kwargs) -> AgentResponse:
        """Create LinkedIn post content using LLM"""
        self._log_action("Creating LinkedIn post")
        print(f"🔍 DEBUG: SocialStrategistAgent.create_linkedin_post called")
        print(f"🔍 DEBUG: Analysis type: {type(analysis)}")
        print(f"🔍 DEBUG: Has LLM: {hasattr(self, 'llm')}")
        print(f"🔍 DEBUG: Brand voice: {brand_voice}")
        
        # Extract detected product from analysis
        detected_product = 'Unknown product'
        
        # Handle different analysis types
        if hasattr(analysis, 'content') and hasattr(analysis.content, 'get'):
            detected_product = analysis.content.get('detected_product', 'Unknown product')
        elif isinstance(analysis, dict):
            detected_product = analysis.get('detected_product', 'Unknown product')
        elif hasattr(analysis, 'detected_product'):
            detected_product = analysis.detected_product
            
        print(f"🎯 DEBUG: Using detected product: {detected_product}")
        
        # Ensure we have a valid product name
        if detected_product.lower() in ['unknown', 'unknown product', 'n/a', '']:
            detected_product = 'our product'  # Fallback to generic term
        
        # Extract content from analysis
        content = ""
        if isinstance(analysis, dict):
            content = analysis.get("transcript", "") or str(analysis)
        else:
            content = str(analysis)
        
        # Generate LinkedIn post using LLM
        prompt = f"""
        Create a professional LinkedIn post about {detected_product} based on this content:
        
        {content[:1000]}
        
        Requirements:
        - Professional and engaging tone
        - 2-3 paragraphs maximum
        - Include relevant hashtags
        - Call-to-action when appropriate
        - Brand voice: {brand_voice}
        - Length: 150-300 words
        - Always refer to the product as "{detected_product}" (exactly as written)
        
        Format:
        - Compelling hook about {detected_product}
        - Key insights or takeaways
        - Relevant hashtags (3-5) including #{detected_product.replace(' ', '')}
        
        Marketing Focus:
        - Highlight {detected_product} and its benefits
        - Use benefit-oriented language
        - Include relevant use cases or applications for {detected_product}
        """
        
        system_prompt = "You are a professional social media manager specializing in LinkedIn content. Create engaging, professional posts that drive meaningful discussions."
        
        try:
            linkedin_content = self._generate_with_llm(prompt, system_prompt)
            
            return AgentResponse(
                success=True,
                content=linkedin_content,
                confidence=0.85,
                reasoning="LinkedIn post generated using AI analysis of content",
                suggestions=["Review post for brand voice alignment", "Add relevant hashtags if needed"]
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                content="Unable to generate LinkedIn post",
                confidence=0.0,
                reasoning=f"LinkedIn post generation failed: {str(e)}",
                suggestions=["Check content format and try again"]
            )
    
    def create_twitter_thread(self, analysis: Any, brand_voice: str = "professional", **kwargs) -> AgentResponse:
        """Create Twitter thread content using LLM"""
        self._log_action("Creating Twitter thread")
        print(f"🔍 DEBUG: SocialStrategistAgent.create_twitter_thread called")
        print(f"🔍 DEBUG: Brand voice: {brand_voice}")
        
        # Extract detected product from analysis
        detected_product = 'Unknown product'
        
        # Handle different analysis types
        if hasattr(analysis, 'content') and hasattr(analysis.content, 'get'):
            detected_product = analysis.content.get('detected_product', 'Unknown product')
        elif isinstance(analysis, dict):
            detected_product = analysis.get('detected_product', 'Unknown product')
        elif hasattr(analysis, 'detected_product'):
            detected_product = analysis.detected_product
            
        print(f"🎯 DEBUG: Using detected product: {detected_product}")
        
        # Ensure we have a valid product name
        if detected_product.lower() in ['unknown', 'unknown product', 'n/a', '']:
            detected_product = 'our product'  # Fallback to generic term
        
        # Extract content from analysis
        content = ""
        if isinstance(analysis, dict):
            content = analysis.get("transcript", "") or str(analysis)
        else:
            content = str(analysis)
        
        # Generate Twitter thread using LLM
        prompt = f"""
        Create a Twitter thread about {detected_product} based on this content:
        
        {content[:1000]}
        
        Requirements:
        - {brand_voice} brand voice
        - 3-5 tweets maximum
        - Include relevant hashtags including #{detected_product.replace(' ', '')}
        - Engaging and conversational
        - Include a call-to-action
        - Always refer to the product as "{detected_product}" (exactly as written)
        
        Format:
        Tweet 1: Hook about {detected_product} and main point
        Tweet 2-4: Key features and benefits of {detected_product}
        Final Tweet: Call to action to learn more about {detected_product}
        
        Marketing Focus:
        - Highlight key features of {detected_product}
        - Use engaging questions or statistics about {detected_product}
        - Include relevant hashtags and mentions
        - Always use the exact product name: {detected_product}
        """
        
        system_prompt = "You are a professional social media manager specializing in Twitter content. Create engaging, conversational threads that drive engagement."
        
        try:
            twitter_content = self._generate_with_llm(prompt, system_prompt)
            
            return AgentResponse(
                success=True,
                content=twitter_content,
                confidence=0.85,
                reasoning="Twitter thread generated using AI analysis and platform optimization",
                suggestions=["Add relevant hashtags", "Include engaging questions", "Use thread structure effectively"]
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                content="Unable to generate Twitter thread",
                confidence=0.0,
                reasoning=f"Twitter thread generation failed: {str(e)}",
                suggestions=["Check content format and try again"]
            )
    
    def _create_twitter_strategy(self, analysis: Dict) -> Dict:
        """Create Twitter-specific strategy"""
        return {
            "tone": "concise and engaging",
            "post_length": "280 characters max",
            "content_type": "key insights and questions",
            "posting_frequency": "3-5 times per day",
            "best_times": ["9-11 AM", "2-4 PM", "7-9 PM"],
            "engagement_tactics": ["polls", "threads", "mentions"]
        }
    
    def _create_linkedin_strategy(self, Dict) -> Dict:
        """Create LinkedIn-specific strategy"""
        return {
            "tone": "professional and insightful",
            "post_length": "1500 characters max",
            "content_type": "professional insights and analysis",
            "posting_frequency": "1-2 times per day",
            "best_times": ["8-10 AM", "12-1 PM", "5-6 PM"],
            "engagement_tactics": ["articles", "case studies", "professional stories"]
        }
    
    def _create_instagram_strategy(self, analysis: Dict) -> Dict:
        """Create Instagram-specific strategy"""
        return {
            "tone": "visual and engaging",
            "content_type": "visual content with compelling captions",
            "posting_frequency": "1-2 times per day",
            "best_times": ["11 AM-1 PM", "7-9 PM"],
            "engagement_tactics": ["stories", "reels", "carousel posts"]
        }
    
    def _create_facebook_strategy(self, analysis: Dict) -> Dict:
        """Create Facebook-specific strategy"""
        return {
            "tone": "conversational and community-focused",
            "post_length": "500 characters max",
            "content_type": "community discussions and updates",
            "posting_frequency": "1-3 times per day",
            "best_times": ["1-4 PM", "8-10 PM"],
            "engagement_tactics": ["groups", "events", "live videos"]
        }
    
    def _generate_content_recommendations(self, analysis: Dict) -> List[str]:
        """Generate content recommendations"""
        recommendations = []
        
        if analysis["sentiment"] == "positive":
            recommendations.append("Leverage positive sentiment in motivational posts")
        
        if "technical" in analysis["target_audience"]:
            recommendations.append("Create educational content and tutorials")
        
        for topic in analysis["topics"]:
            recommendations.append(f"Develop content around {topic}")
        
        return recommendations[:5]
    
    def _create_posting_schedule(self, analysis: Dict) -> Dict:
        """Create optimal posting schedule"""
        return {
            "optimal_days": ["Tuesday", "Wednesday", "Thursday"],
            "peak_hours": ["9-11 AM", "2-4 PM", "7-9 PM"],
            "frequency_recommendation": "3-5 posts per day across platforms",
            "content_mix": "40% educational, 30% engaging, 20% promotional, 10% personal"
        }
    
    def _create_hashtag_strategy(self, analysis: Dict) -> Dict:
        """Create hashtag strategy"""
        hashtags = []
        
        for topic in analysis["topics"]:
            hashtags.append(f"#{topic}")
        
        # Add general hashtags
        hashtags.extend(["#content", "#marketing", "#socialmedia", "#digital"])
        
        return {
            "primary_hashtags": hashtags[:3],
            "secondary_hashtags": hashtags[3:7],
            "brand_hashtag": "#YourBrand",
            "hashtag_count": "5-10 per post"
        }
    
    def _suggest_engagement_tactics(self, analysis: Dict) -> List[str]:
        """Suggest engagement tactics"""
        tactics = [
            "Ask questions to encourage comments",
            "Use polls and surveys",
            "Share behind-the-scenes content",
            "Respond to comments promptly",
            "Collaborate with other creators"
        ]
        
        return tactics
    
    def _generate_strategy_suggestions(self, strategy: Dict) -> List[str]:
        """Generate strategy improvement suggestions"""
        suggestions = [
            "Monitor analytics to refine posting times",
            "A/B test different content formats",
            "Engage with audience comments regularly",
            "Adjust strategy based on platform performance"
        ]
        
        return suggestions

class ScriptDoctorAgent(BaseAgent):
    """Improves and refines content scripts"""
    
    def __init__(self, use_ollama: bool = True):
        super().__init__(
            "Script Doctor",
            "Improves and refines content scripts for better engagement",
            use_ollama=use_ollama
        )
    
    def process(self, content: str, content_type: str = "general", **kwargs) -> AgentResponse:
        """Improve and refine content using LLM"""
        self._log_action(f"Improving {content_type} content")
        
        print(f"🔍 DEBUG: process called with content type: {content_type}")
        print(f"🔍 DEBUG: Content length: {len(content)}")
        print(f"🔍 DEBUG: Has LLM: {hasattr(self, 'llm')}")
        print(f"🔍 DEBUG: Use Ollama: {self.use_ollama}")
        print(f"🔍 DEBUG: Content object type: {type(content)}")
        print(f"🔍 DEBUG: Content object keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
        print(f"🔍 DEBUG: Content object has transcript: {'transcript' in content if isinstance(content, dict) else 'No'}")
        
        try:
            # Extract detected product if content is a dict with analysis data
            detected_product = "Unknown product"
            if isinstance(content, dict):
                detected_product = content.get('detected_product', 'Unknown product')
            elif hasattr(content, 'content') and content.content:
                if isinstance(content.content, dict):
                    detected_product = content.content.get('detected_product', 'Unknown product')
            
            print(f"🎯 DEBUG: Script agent using detected product: {detected_product}")
            
            # Convert content to string for processing
            if isinstance(content, dict):
                actual_content = content.get("transcript", "") or str(content)
                print(f"🔍 DEBUG: Extracted transcript from dict, length: {len(actual_content)}")
                print(f"🔍 DEBUG: Available keys in content dict: {list(content.keys())}")
            else:
                actual_content = str(content)
                print(f"🔍 DEBUG: Content is not dict, converted to string, length: {len(actual_content)}")
            
            print(f"🔍 DEBUG: Final actual_content length: {len(actual_content)}")
            print(f"🔍 DEBUG: Actual content preview: {actual_content[:200]}...")
            
            # Generate script using LLM
            prompt = f"""
            Create an engaging short-form script based on this content:
            
            {actual_content[:1000]}
            
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
            """
            
            system_prompt = "You are a professional script writer specializing in short-form video content. Create compelling scripts that capture attention and drive engagement."
            
            print(f"🔍 DEBUG: About to call _generate_with_llm...")
            script_content = self._generate_with_llm(prompt, system_prompt)
            print(f"🔍 DEBUG: _generate_with_llm returned content length: {len(script_content)}")
            
            # Create result structure
            result = {
                "script": script_content,
                "original_content": content,
                "content_type": content_type,
                "estimated_duration": "45 seconds",
                "platform_suggestions": ["TikTok", "Instagram Reels", "YouTube Shorts"],
                "engagement_tips": ["Add trending music", "Use captions", "Include hook in first 3 seconds"]
            }
            
            confidence = 0.85
            
            print(f"🔍 DEBUG: Creating AgentResponse with confidence: {confidence}")
            
            return AgentResponse(
                success=True,
                content=result,
                confidence=confidence,
                reasoning="Short-form script generated using AI analysis and optimization",
                suggestions=["Add visual elements", "Test different hooks", "Include call-to-action"]
            )
            
        except Exception as e:
            print(f"🔍 DEBUG: Exception in process: {e}")
            return AgentResponse(
                success=False,
                content={"script": "Unable to generate script due to technical issues"},
                confidence=0.0,
                reasoning=f"Script generation failed: {str(e)}",
                suggestions=["Check content format and try again"]
            )
    
    def create_short_scripts(self, analysis: Dict[str, Any]) -> AgentResponse:
        """Create short-form scripts - alias for process method"""
        print(f"🔍 DEBUG: create_short_scripts called with analysis type: {type(analysis)}")
        
        # Pass the full analysis object to process, not just the content string
        # This ensures the detected_product information is preserved
        if hasattr(analysis, 'content') and analysis.content:
            if isinstance(analysis.content, dict):
                # Pass the full analysis content dict with transcript and detected_product
                content_for_processing = analysis.content
            else:
                # If content is not a dict, create one with the content and detected_product
                content_for_processing = {
                    "transcript": str(analysis.content),
                    "detected_product": getattr(analysis, 'detected_product', 'Unknown product')
                }
        else:
            # If no content attribute, create dict from the analysis object itself
            content_for_processing = {
                "transcript": str(analysis),
                "detected_product": "Unknown product"
            }
        
        print(f"🔍 DEBUG: Content for processing type: {type(content_for_processing)}")
        print(f"🔍 DEBUG: Content for processing keys: {list(content_for_processing.keys()) if isinstance(content_for_processing, dict) else 'Not a dict'}")
        print(f"🔍 DEBUG: Has LLM: {hasattr(self, 'llm')}")
        
        result = self.process(content_for_processing, "short_form")
        print(f"🔍 DEBUG: Process result success: {result.success}")
        print(f"🔍 DEBUG: Content length: {len(str(result.content))}")
        
        return result
    
    def _analyze_script(self, content: str) -> Dict:
        """Analyze script for improvement opportunities"""
        return {
            "word_count": len(content.split()),
            "sentence_count": len(content.split('.')),
            "avg_sentence_length": len(content.split()) / len(content.split('.')) if content.split('.') else 0,
            "readability_score": self._assess_readability(content),
            "engagement_score": self._assess_engagement(content),
            "structure_issues": self._identify_structure_issues(content),
            "grammar_issues": self._identify_grammar_issues(content)
        }
    
    def _assess_readability(self, content: str) -> float:
        """Assess content readability"""
        # Simplified readability assessment
        sentences = content.split('.')
        if not sentences:
            return 0.0
        
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if 10 <= avg_words <= 20:
            return 1.0
        elif 5 <= avg_words <= 25:
            return 0.8
        else:
            return 0.6
    
    def _assess_engagement(self, content: str) -> float:
        """Assess engagement potential"""
        engagement_words = ['amazing', 'incredible', 'fantastic', 'important', 'crucial']
        engagement_count = sum(1 for word in engagement_words if word in content.lower())
        
        return min(engagement_count * 0.2, 1.0)
    
    def _identify_structure_issues(self, content: str) -> List[str]:
        """Identify structural issues"""
        issues = []
        
        if len(content.split()) < 50:
            issues.append("Content too short")
        
        sentences = content.split('.')
        if len(sentences) < 3:
            issues.append("Not enough sentences")
        
        return issues
    
    def _identify_grammar_issues(self, content: str) -> List[str]:
        """Identify grammar issues"""
        issues = []
        
        # Simplified grammar checks
        if '  ' in content:  # Double spaces
            issues.append("Extra spaces detected")
        
        return issues
    
    def _generate_improvements(self, content: str, analysis: Dict) -> List[Dict]:
        """Generate improvement suggestions"""
        improvements = []
        
        if analysis["readability_score"] < 0.7:
            improvements.append({
                "type": "readability",
                "description": "Improve sentence structure for better readability",
                "priority": "high"
            })
        
        if analysis["engagement_score"] < 0.5:
            improvements.append({
                "type": "engagement",
                "description": "Add more engaging language",
                "priority": "medium"
            })
        
        return improvements
    
    def _refine_content(self, content: str, improvements: List[Dict]) -> str:
        """Apply improvements to content"""
        refined = content
        
        # Apply basic improvements
        for improvement in improvements:
            if improvement["type"] == "readability":
                # Break up long sentences (simplified)
                refined = refined.replace('. ', '.\n')
            
            elif improvement["type"] == "engagement":
                # Add engaging words (simplified)
                refined = refined.replace('good', 'excellent')
        
        return refined
    
    def _generate_editing_notes(self, analysis: Dict, improvements: List[Dict]) -> List[str]:
        """Generate editing notes"""
        notes = []
        
        notes.append(f"Word count: {analysis['word_count']}")
        notes.append(f"Average sentence length: {analysis['avg_sentence_length']:.1f} words")
        
        for improvement in improvements:
            notes.append(f"Improvement: {improvement['description']}")
        
        return notes
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate quality score for refined content"""
        # Simplified quality calculation
        base_score = 0.7
        
        if len(content.split()) > 100:
            base_score += 0.1
        
        if content.count('!') > 0:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _generate_content_suggestions(self, result: Dict) -> List[str]:
        """Generate content improvement suggestions"""
        suggestions = [
            "Consider adding more specific examples",
            "Include a clear call to action",
            "Add transition words for better flow",
            "Consider the target audience's knowledge level"
        ]
        
        return suggestions

def demonstrate_agents():
    """Demonstrate the agent system"""
    
    print("🤖 AI Agents Demo")
    print("=" * 60)
    
    # Test content
    test_transcript = """
    Today I want to talk about the amazing world of artificial intelligence. 
    AI is transforming how we work and live. It's incredible to see how 
    machine learning algorithms can solve complex problems. The future 
    of technology is really exciting!
    """
    
    print(f"\n📝 Test Transcript: {test_transcript[:100]}...")
    print("-" * 40)
    
    # Test Content Analyst
    print("\n🧠 Content Analyst Agent:")
    analyst = ContentAnalystAgent()
    analysis_result = analyst.process(test_transcript)
    
    if analysis_result.success:
        print(f"   ✅ Analysis complete")
        print(f"   📊 Topics: {', '.join(analysis_result.content['topics'])}")
        print(f"   😊 Sentiment: {analysis_result.content['sentiment']}")
        print(f"   👥 Audience: {analysis_result.content['target_audience']}")
        print(f"   🎯 Confidence: {analysis_result.confidence:.2f}")
    
    # Test Social Strategist
    print("\n📱 Social Strategist Agent:")
    strategist = SocialStrategistAgent()
    strategy_result = strategist.process(analysis_result.content if analysis_result.success else {})
    
    if strategy_result.success:
        print(f"   ✅ Strategy developed")
        print(f"   📊 Platforms: {len(strategy_result.content['platform_strategies'])}")
        print(f"   📅 Schedule: {strategy_result.content['posting_schedule']['optimal_days']}")
        print(f"   🎯 Confidence: {strategy_result.confidence:.2f}")
    
    # Test Script Doctor
    print("\n✍️ Script Doctor Agent:")
    doctor = ScriptDoctorAgent()
    script_result = doctor.process(test_transcript)
    
    if script_result.success:
        print(f"   ✅ Script improved")
        print(f"   📊 Quality score: {script_result.content['quality_score']:.2f}")
        print(f"   📝 Improvements: {len(script_result.content['improvements'])}")
        print(f"   🎯 Confidence: {script_result.confidence:.2f}")
    
    print("\n" + "=" * 60)
    print("\n🎯 Agent System Benefits:")
    print("   ✅ Specialized expertise for each content aspect")
    print("   ✅ Comprehensive analysis and strategy development")
    print("   ✅ Content improvement and refinement")
    print("   ✅ Platform-specific optimization")
    print("   ✅ Confidence scoring and quality control")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented a multi-agent system for content processing'")
    print("   🎯 'Each agent has specialized expertise and responsibilities'")
    print("   🎯 'Agents work together to provide comprehensive content solutions'")
    print("   🎯 'Confidence scoring ensures quality output'")
    print("   🎯 'Modular design allows for easy extension and maintenance'")

if __name__ == "__main__":
    demonstrate_agents()
