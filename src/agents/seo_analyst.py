"""
SEO Analyst Agent - Specialized agent for SEO keyword extraction and optimization
Converted from legacy seo_agent.py to use the new agentic architecture
"""

from typing import Dict, Any, List, Optional
import re
import os
from dotenv import load_dotenv

from .base import AnalysisAgent
from ..schema.models import AgentResponse, LogLevel
from ..config.manager import system_prompts

load_dotenv()

class SEOAnalystAgent(AnalysisAgent):
    """SEO Specialist focused on keyword extraction and content optimization"""
    
    def __init__(self):
        super().__init__(
            agent_name="seo_analyst",
            description="SEO Specialist focused on keyword extraction and content optimization"
        )
    
    async def analyze(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Perform SEO analysis on content"""
        
        await self.update_state(self.state.status.__class__.THINKING, "seo_analysis")
        
        try:
            # Extract content from input
            content = self._extract_content(input_data)
            target_keywords = input_data.get('target_keywords', [])
            
            if not content:
                return self.create_response(
                    success=False,
                    content=None,
                    confidence=0.0,
                    reasoning="No content provided for SEO analysis",
                    suggestions=["Please provide text content for SEO analysis"]
                )
            
            await self.plan(f"Analyzing SEO for {len(content)} characters with {len(target_keywords)} target keywords")
            
            # Extract keywords using tool
            tool_response = await self.call_tool(
                "extract_seo_keywords",
                {
                    "text": content,
                    "target_keywords": target_keywords,
                    "max_keywords": 20
                }
            )
            
            if not tool_response.success:
                return self.create_response(
                    success=False,
                    content=None,
                    confidence=0.0,
                    reasoning=f"SEO analysis failed: {tool_response.error_message}",
                    suggestions=["Check content format and try again"]
                )
            
            seo_analysis = tool_response.result.get('seo_analysis', {})
            
            await self.reason("SEO analysis completed", 
                            context={
                                "keywords_found": tool_response.result.get('keyword_count', 0),
                                "primary_keywords": len(seo_analysis.get('primary_keywords', [])),
                                "optimization_score": seo_analysis.get('optimization_score', 0)
                            })
            
            return self.create_response(
                success=True,
                content=seo_analysis,
                confidence=0.85,
                reasoning="SEO analysis completed using keyword extraction and optimization scoring",
                suggestions=seo_analysis.get('recommendations', [])
            )
            
        except Exception as e:
            await self.logger.error("SEO analysis failed", e)
            return self.create_response(
                success=False,
                content=None,
                confidence=0.0,
                reasoning=f"SEO analysis failed: {str(e)}",
                suggestions=["Check content format and try again"]
            )
    
    async def optimize_content(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Optimize content for SEO"""
        
        await self.update_state(self.state.status.__class__.THINKING, "seo_optimization")
        
        try:
            content = input_data.get('content', '')
            seo_analysis = input_data.get('seo_analysis', {})
            content_type = input_data.get('content_type', 'blog_post')
            
            if not content:
                return self.create_response(
                    success=False,
                    content=None,
                    confidence=0.0,
                    reasoning="No content provided for SEO optimization",
                    suggestions=["Please provide content to optimize"]
                )
            
            await self.plan(f"Optimizing {content_type} for SEO")
            
            # Use tool for optimization
            tool_response = await self.call_tool(
                "optimize_content_seo",
                {
                    "content": content,
                    "seo_analysis": seo_analysis,
                    "content_type": content_type
                }
            )
            
            if not tool_response.success:
                return self.create_response(
                    success=False,
                    content=None,
                    confidence=0.0,
                    reasoning=f"SEO optimization failed: {tool_response.error_message}",
                    suggestions=["Check content and SEO analysis format"]
                )
            
            optimized_content = tool_response.result
            
            await self.reason("SEO optimization completed")
            
            return self.create_response(
                success=True,
                content=optimized_content,
                confidence=0.8,
                reasoning="Content optimized for SEO based on keyword analysis",
                suggestions=["Review optimized content for natural flow"]
            )
            
        except Exception as e:
            await self.logger.error("SEO optimization failed", e)
            return self.create_response(
                success=False,
                content=None,
                confidence=0.0,
                reasoning=f"SEO optimization failed: {str(e)}",
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
            elif hasattr(input_data['content'], 'content'):
                return str(input_data['content'].content)
        return ""

# Legacy compatibility wrapper
class SEOKeywordExtractor:
    """Legacy compatibility wrapper for SEOKeywordExtractor"""
    
    def __init__(self, brand_voice=None):
        self.agent = SEOAnalystAgent()
        self.brand_voice = brand_voice
    
    def extract_keywords(self, transcript: str, target_keywords: List[str] = None) -> Any:
        """Legacy method for keyword extraction"""
        
        # Create legacy-style response
        input_data = {
            'transcript': transcript,
            'target_keywords': target_keywords or []
        }
        
        # For now, return a simple result structure
        # In a full implementation, this would be async
        words = re.findall(r'\b[a-zA-Z]{3,}\b', transcript.lower())
        word_freq = {}
        for word in words:
            if word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Create SEOAnalysis-like object
        class LegacySEOAnalysis:
            def __init__(self):
                self.keywords = []
                self.primary_keywords = []
                self.secondary_keywords = []
                self.long_tail_keywords = []
                self.entities = []
                self.content_gaps = []
                self.optimization_score = 0
                self.recommendations = []
            
            def to_dict(self):
                return {
                    "keywords": self.keywords,
                    "primary_keywords": self.primary_keywords,
                    "secondary_keywords": self.secondary_keywords,
                    "long_tail_keywords": self.long_tail_keywords,
                    "entities": self.entities,
                    "content_gaps": self.content_gaps,
                    "optimization_score": self.optimization_score,
                    "recommendations": self.recommendations
                }
        
        analysis = LegacySEOAnalysis()
        
        # Process keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        for word, freq in sorted_keywords[:20]:
            if len(word) >= 4 and freq >= 2:
                keyword_data = {
                    "keyword": word,
                    "frequency": freq,
                    "importance": "high" if freq >= 5 else "medium",
                    "category": "primary" if freq >= 5 else "secondary",
                    "search_intent": "informational",
                    "competition": "medium"
                }
                analysis.keywords.append(keyword_data)
                
                if len(word) > 6:
                    analysis.long_tail_keywords.append(word)
                else:
                    analysis.secondary_keywords.append(word)
        
        analysis.primary_keywords = [kw["keyword"] for kw in analysis.keywords[:5]]
        analysis.optimization_score = min(len(analysis.primary_keywords) * 10, 100)
        
        if len(analysis.primary_keywords) < 3:
            analysis.recommendations.append("Consider adding more primary keywords")
        
        return analysis
    
    def optimize_content_for_seo(self, content: str, seo_analysis, content_type: str = "blog_post") -> str:
        """Legacy method for SEO optimization"""
        
        if not seo_analysis or not hasattr(seo_analysis, 'primary_keywords'):
            return content
        
        primary_keywords = seo_analysis.primary_keywords[:5]
        
        # Simple optimization
        optimized_content = content
        
        # Add title with primary keyword if missing
        lines = content.split('\n')
        if lines and len(lines[0]) < 100:
            title = lines[0]
            if not any(keyword.lower() in title.lower() for keyword in primary_keywords[:3]):
                optimized_content = f"{primary_keywords[0].title()}: {title}\n" + '\n'.join(lines[1:])
        
        return optimized_content
