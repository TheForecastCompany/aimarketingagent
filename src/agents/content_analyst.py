"""
Content Analyst Agent - Modular version for content analysis and topic extraction
Refactored from the original agents.py to use the new agentic architecture
"""

from typing import Dict, Any, List, Optional
import re
import json

from .base import AnalysisAgent
from ..schema.models import AgentResponse, ContentAnalysis, LogLevel
from ..config.manager import system_prompts

class ContentAnalystAgent(AnalysisAgent):
    """Analyzes content structure, topics, and quality"""
    
    def __init__(self):
        super().__init__(
            agent_name="content_analyst",
            description="Analyzes content structure, topics, and engagement potential"
        )
    
    async def analyze(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Analyze transcript content"""
        
        await self.update_state(self.state.status.__class__.THINKING, "content_analysis")
        
        try:
            # Extract content from input
            content = self._extract_content(input_data)
            
            if not content:
                return self.create_response(
                    success=False,
                    content=None,
                    confidence=0.0,
                    reasoning="No content provided for analysis",
                    suggestions=["Please provide transcript or text content"]
                )
            
            await self.plan(f"Analyzing content of {len(content)} characters")
            
            # Perform analysis steps
            topics = await self._extract_topics(content)
            key_points = await self._extract_key_points(content)
            sentiment = await self._analyze_sentiment(content)
            target_audience = await self._identify_audience(content)
            structure = await self._analyze_structure(content)
            
            # Create analysis object
            analysis = ContentAnalysis(
                topics=topics,
                key_points=key_points,
                sentiment=sentiment,
                target_audience=target_audience,
                word_count=len(content.split()),
                estimated_reading_time=len(content.split()) / 200,
                confidence=self._calculate_confidence(topics, key_points)
            )
            
            # Try to detect product if not already done
            detected_product = input_data.get('detected_product')
            if not detected_product:
                detected_product = await self._detect_product(content)
                if detected_product:
                    analysis.detected_product = detected_product
            
            await self.reason("Content analysis completed", 
                            confidence=analysis.confidence,
                            context={
                                "topics_count": len(topics),
                                "key_points_count": len(key_points),
                                "sentiment": sentiment
                            })
            
            return self.create_response(
                success=True,
                content=analysis,
                confidence=analysis.confidence,
                reasoning="Content analysis completed using topic modeling and sentiment analysis",
                suggestions=self._generate_suggestions(analysis)
            )
            
        except Exception as e:
            await self.logger.error("Content analysis failed", e)
            return self.create_response(
                success=False,
                content=None,
                confidence=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                suggestions=["Check content format and try again"]
            )
    
    def _extract_content(self, input_data: Dict[str, Any]) -> str:
        """Extract text content from various input formats"""
        
        if 'transcript' in input_data:
            return input_data['transcript']
        elif 'text' in input_data:
            return input_data['text']
        elif 'content' in input_data:
            if isinstance(input_data['content'], str):
                return input_data['content']
            elif isinstance(input_data['content'], dict):
                return input_data['content'].get('text', '')
        return ""
    
    async def _extract_topics(self, content: str) -> List[str]:
        """Extract main topics from content"""
        
        await self.reason("Extracting topics from content")
        
        # Use tool for topic extraction
        try:
            tool_response = await self.call_tool(
                "text_analysis",
                {"text": content, "analysis_type": "topics"}
            )
            
            if tool_response.success and 'topics' in tool_response.result:
                topics = tool_response.result['topics']
                await self.reflect(f"Topics extracted: {len(topics)} topics found")
                return topics[:5]  # Limit to top 5 topics
        except Exception as e:
            await self.logger.warning("Tool-based topic extraction failed, using fallback", data={"error": str(e)})
        
        # Fallback to simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        for word in words:
            if word not in ['that', 'this', 'with', 'from', 'they', 'have', 'been']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return [topic for topic, freq in topics]
    
    async def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content"""
        
        await self.reason("Extracting key points from content")
        
        # Use tool for key point extraction
        try:
            tool_response = await self.call_tool(
                "text_analysis",
                {"text": content, "analysis_type": "key_points"}
            )
            
            if tool_response.success and 'key_points' in tool_response.result:
                key_points = tool_response.result['key_points']
                await self.reflect(f"Key points extracted: {len(key_points)} points found")
                return key_points
        except Exception as e:
            await self.logger.warning("Tool-based key point extraction failed, using fallback", data={"error": str(e)})
        
        # Fallback to sentence extraction
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        
        # Score sentences based on length and keywords
        scored_sentences = []
        for sentence in sentences:
            score = len(sentence.split())  # Prefer longer sentences
            if any(word in sentence.lower() for word in ['important', 'key', 'main', 'primary', 'critical']):
                score += 2
            scored_sentences.append((sentence, score))
        
        # Return top 3 sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sentence for sentence, score in scored_sentences[:3]]
    
    async def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of content"""
        
        await self.reason("Analyzing sentiment")
        
        # Use tool for sentiment analysis
        try:
            tool_response = await self.call_tool(
                "text_analysis",
                {"text": content, "analysis_type": "sentiment"}
            )
            
            if tool_response.success and 'sentiment' in tool_response.result:
                sentiment = tool_response.result['sentiment']
                await self.reflect(f"Sentiment analyzed: {sentiment}")
                return sentiment
        except Exception as e:
            await self.logger.warning("Tool-based sentiment analysis failed, using fallback", data={"error": str(e)})
        
        # Fallback to simple sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'best', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'poor', 'disappointing']
        
        words = content.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def _identify_audience(self, content: str) -> str:
        """Identify target audience"""
        
        await self.reason("Identifying target audience")
        
        # Simple audience detection based on content clues
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['business', 'professional', 'corporate', 'enterprise']):
            return "Business Professionals"
        elif any(word in content_lower for word in ['developer', 'programming', 'code', 'technical']):
            return "Developers/Technical Users"
        elif any(word in content_lower for word in ['student', 'education', 'learning', 'academic']):
            return "Students/Educators"
        elif any(word in content_lower for word in ['marketing', 'sales', 'customer', 'client']):
            return "Marketing/Sales Professionals"
        else:
            return "General Audience"
    
    async def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        
        await self.reason("Analyzing content structure")
        
        sentences = content.split('.')
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        return {
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "avg_sentence_length": sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            "has_clear_structure": len(paragraphs) > 1
        }
    
    def _calculate_confidence(self, topics: List[str], key_points: List[str]) -> float:
        """Calculate confidence score based on analysis quality"""
        
        confidence = 0.5  # Base confidence
        
        # More topics = higher confidence
        if len(topics) >= 3:
            confidence += 0.2
        elif len(topics) >= 1:
            confidence += 0.1
        
        # More key points = higher confidence
        if len(key_points) >= 3:
            confidence += 0.2
        elif len(key_points) >= 1:
            confidence += 0.1
        
        return min(confidence, 0.95)  # Cap at 95%
    
    async def _detect_product(self, content: str) -> Optional[str]:
        """Detect product mentions in content"""
        
        await self.reason("Attempting to detect product mentions")
        
        # Use tool for product detection
        try:
            tool_response = await self.call_tool(
                "text_analysis",
                {"text": content, "analysis_type": "product_detection"}
            )
            
            if tool_response.success:
                await self.reflect("Product detection completed")
                return tool_response.result.get('product')
        except Exception as e:
            await self.logger.warning("Product detection failed", data={"error": str(e)})
        
        return None
    
    def _generate_suggestions(self, analysis: ContentAnalysis) -> List[str]:
        """Generate suggestions based on analysis"""
        
        suggestions = []
        
        if analysis.confidence < 0.7:
            suggestions.append("Consider providing more content for better analysis")
        
        if len(analysis.topics) < 2:
            suggestions.append("Content could benefit from more diverse topics")
        
        if len(analysis.key_points) < 3:
            suggestions.append("Consider highlighting more key takeaways")
        
        if analysis.sentiment == "neutral":
            suggestions.append("Consider adding more engaging or emotional elements")
        
        if not suggestions:
            suggestions.append("Content analysis looks good!")
        
        return suggestions
