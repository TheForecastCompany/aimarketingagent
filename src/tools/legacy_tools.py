"""
Comprehensive Tools Library - All action-oriented functions from legacy scripts
Standardized tools for external API calls, file operations, and data processing
"""

import os
import re
import json
import time
import requests
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter

class TranscriptTools:
    """Tools for transcript extraction from various sources"""
    
    @staticmethod
    async def extract_video_id(url: str) -> Dict[str, Any]:
        """
        Extract video ID from YouTube URL (including playlists)
        
        Args:
            url: YouTube video URL to extract ID from
            
        Returns:
            Dictionary with success status and video_id or error message
        """
        patterns = [
            # Standard YouTube URLs
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
            # Playlist URLs - extract the first video ID
            r'youtube\.com/watch\?.*list=.*[?&]v=([a-zA-Z0-9_-]{11})',
            r'youtube\.com/playlist\?.*list=.*[?&]v=([a-zA-Z0-9_-]{11})',
            # Short URLs
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            # Embedded players
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            # No cookie embed
            r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                return {
                    "success": True,
                    "video_id": video_id,
                    "url_type": "youtube",
                    "pattern_used": pattern
                }
        
        return {
            "success": False,
            "error": "No valid YouTube video ID found in URL",
            "url": url
        }
    
    @staticmethod
    async def extract_youtube_transcript(video_id: str, language: str = "en") -> Dict[str, Any]:
        """
        Extract transcript from YouTube video using multiple fallback methods
        
        Args:
            video_id: YouTube video ID to extract transcript from
            language: Language code for transcript (default: "en")
            
        Returns:
            Dictionary with success status, transcript text, and metadata
        """
        
        try:
            # Method 1: Try to get transcript directly
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Prefer manual transcripts, fallback to auto-generated
            transcript = None
            transcript_info = {}
            
            # Try manual transcript first
            manual_transcripts = [t for t in transcript_list if t.is_generated == False]
            if manual_transcripts:
                transcript = manual_transcripts[0]
                transcript_info["method"] = "manual"
            else:
                # Fall back to auto-generated
                auto_transcripts = [t for t in transcript_list if t.is_generated == True]
                if auto_transcripts:
                    transcript = auto_transcripts[0]
                    transcript_info["method"] = "auto_generated"
                else:
                    return {
                        "success": False,
                        "error": "No transcript available for this video",
                        "video_id": video_id
                    }
            
            # Get the actual transcript text
            transcript_text = transcript.fetch()
            
            # Format transcript
            formatter = TextFormatter()
            formatted_transcript = formatter.format_transcript(transcript_text)
            
            # Extract metadata
            transcript_info.update({
                "language": transcript.language,
                "is_generated": transcript.is_generated,
                "is_manually_created": not transcript.is_generated,
                "video_id": video_id,
                "transcript_length": len(formatted_transcript),
                "processing_time": time.time()
            })
            
            return {
                "success": True,
                "transcript": formatted_transcript,
                "metadata": transcript_info
            }
            
        except TranscriptsDisabled:
            return {
                "success": False,
                "error": "Transcripts are disabled for this video",
                "video_id": video_id
            }
        except NoTranscriptFound:
            return {
                "success": False,
                "error": "No transcript found for this video",
                "video_id": video_id
            }
        except NoTranscriptAvailable:
            return {
                "success": False,
                "error": "Transcript not available for this video",
                "video_id": video_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "video_id": video_id
            }
    
    @staticmethod
    async def extract_with_fallbacks(url: str, use_professional: bool = False) -> Dict[str, Any]:
        """Extract transcript with multiple fallback methods"""
        
        # Extract video ID
        video_id_result = await TranscriptTools.extract_video_id(url)
        if not video_id_result["success"]:
            return video_id_result
        
        video_id = video_id_result["video_id"]
        
        # Try YouTube API first
        youtube_result = await TranscriptTools.extract_youtube_transcript(video_id)
        if youtube_result["success"]:
            return youtube_result
        
        # If professional transcription is enabled and YouTube failed, try AssemblyAI
        if use_professional:
            try:
                # This would integrate with professional_transcription.py
                # For now, return the YouTube error
                return youtube_result
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Professional transcription failed: {str(e)}",
                    "video_id": video_id
                }
        
        # Return YouTube error if all methods failed
        return youtube_result

class SEOTools:
    """Tools for SEO analysis and optimization"""
    
    @staticmethod
    async def extract_keywords(text: str, target_keywords: List[str] = None, 
                           max_keywords: int = 20) -> Dict[str, Any]:
        """Extract keywords from text with SEO analysis"""
        
        # Basic keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            # Filter out common stop words
            if word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Categorize keywords
        primary_keywords = []
        secondary_keywords = []
        long_tail_keywords = []
        
        # Add target keywords as primary
        if target_keywords:
            for target in target_keywords:
                target_lower = target.lower()
                for word, freq in sorted_keywords:
                    if word == target_lower or target_lower in word:
                        primary_keywords.append({
                            "keyword": word,
                            "frequency": freq,
                            "importance": "high",
                            "category": "primary",
                            "search_intent": "informational",
                            "competition": "medium"
                        })
                        break
        
        # Add other high-frequency keywords
        for word, freq in sorted_keywords[:max_keywords]:
            if len(word) >= 4 and freq >= 2:  # Filter out very short or rare words
                keyword_data = {
                    "keyword": word,
                    "frequency": freq,
                    "importance": "high" if freq >= 5 else "medium",
                    "category": "primary" if freq >= 5 else "secondary",
                    "search_intent": "informational",
                    "competition": "medium"
                }
                
                if word not in [kw["keyword"] for kw in primary_keywords]:
                    if len(word) > 6:
                        long_tail_keywords.append(keyword_data)
                    else:
                        secondary_keywords.append(keyword_data)
        
        # Create SEO analysis object
        seo_analysis = {
            "keywords": primary_keywords + secondary_keywords + long_tail_keywords,
            "primary_keywords": [kw["keyword"] for kw in primary_keywords],
            "secondary_keywords": [kw["keyword"] for kw in secondary_keywords],
            "long_tail_keywords": [kw["keyword"] for kw in long_tail_keywords],
            "entities": [],  # Would need NLP for entity extraction
            "content_gaps": [],
            "optimization_score": min(len(primary_keywords) * 10, 100),
            "recommendations": []
        }
        
        # Add recommendations
        if len(primary_keywords) < 3:
            seo_analysis["recommendations"].append("Consider adding more primary keywords")
        
        if len(long_tail_keywords) < 5:
            seo_analysis["recommendations"].append("Include more long-tail keywords for better SEO")
        
        return {
            "success": True,
            "seo_analysis": seo_analysis,
            "keyword_count": len(seo_analysis["keywords"])
        }
    
    @staticmethod
    async def optimize_content_for_seo(content: str, seo_analysis: Dict[str, Any], 
                                      content_type: str = "blog_post") -> str:
        """Optimize content for SEO based on analysis"""
        
        if not seo_analysis or "primary_keywords" not in seo_analysis:
            return content
        
        primary_keywords = seo_analysis["primary_keywords"][:5]  # Top 5 keywords
        
        # Simple SEO optimization
        optimized_content = content
        
        # Add keywords naturally (basic implementation)
        # In a real system, this would be more sophisticated
        keyword_density = {}
        for keyword in primary_keywords:
            keyword_density[keyword] = content.lower().count(keyword.lower())
        
        # Add title with primary keyword if missing
        lines = content.split('\n')
        if lines and len(lines[0]) < 100:
            title = lines[0]
            if not any(keyword.lower() in title.lower() for keyword in primary_keywords[:3]):
                optimized_content = f"{primary_keywords[0].title()}: {title}\n" + '\n'.join(lines[1:])
        
        return optimized_content

class ProductDetectionTools:
    """Tools for detecting products and services from content"""
    
    @staticmethod
    async def detect_product_from_text(text: str, llm_client=None) -> Dict[str, Any]:
        """Detect the main product/service from text using pattern matching and LLM"""
        
        if not text or len(text) < 50:
            return {
                "success": False,
                "product": "Unknown product",
                "confidence": 0.0,
                "method": "insufficient_content"
            }
        
        # Method 1: Pattern-based detection
        product_patterns = [
            # Product names with common patterns
            r'\b(iPhone|iPad|MacBook|Apple Watch)\s*\d*[A-Za-z]*\b',
            r'\b(Samsung|Galaxy)\s*\d*[A-Za-z]*\b',
            r'\b(Google|Pixel)\s*\d*[A-Za-z]*\b',
            r'\b(Microsoft|Windows|Office)\s*\d*[A-Za-z]*\b',
            r'\b(Amazon|AWS|Echo)\s*\d*[A-Za-z]*\b',
            r'\b(Tesla|Model\s*[SYE])\b',
            r'\b(Netflix|Spotify|Disney\+)\b',
            r'\b(Salesforce|CRM)\b',
            r'\b(Slack|Zoom|Teams)\b',
            # Software/services
            r'\b(AI|artificial intelligence)\s*(tools|software|platform)\b',
            r'\b(machine learning|ML)\s*(models|algorithms)\b',
            r'\b(content marketing|SEO)\s*(services|tools)\b',
            r'\b(social media)\s*(marketing|management)\b',
            r'\b(cloud computing|cloud)\s*(services|platform)\b'
        ]
        
        detected_products = []
        for pattern in product_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected_products.extend(matches)
        
        # Remove duplicates and count occurrences
        product_counts = {}
        for product in detected_products:
            product_counts[product] = product_counts.get(product, 0) + 1
        
        if product_counts:
            # Get the most mentioned product
            best_product = max(product_counts.items(), key=lambda x: x[1])
            confidence = min(best_product[1] / 10, 0.9)  # Confidence based on mentions
            
            return {
                "success": True,
                "product": best_product[0],
                "confidence": confidence,
                "method": "pattern_matching",
                "all_products": list(product_counts.keys()),
                "mention_count": best_product[1]
            }
        
        # Method 2: LLM-based detection (if available)
        if llm_client:
            try:
                prompt = f"""Analyze this text and identify the main product, service, or topic being discussed.
                
Text: {text[:500]}

Instructions:
- Identify the primary product, service, or topic
- Look for specific brand names, product names, or service descriptions
- Focus on what is being marketed, reviewed, or explained
- Return ONLY the product name (1-3 words maximum)
- If no clear product is mentioned, return "General topic discussion"
- DO NOT return generic phrases like "The primary product" or "main topic"

CRITICAL: Return ONLY the specific product name, not generic descriptions."""
                
                if hasattr(llm_client, 'generate'):
                    llm_response = llm_client.generate(prompt)
                elif hasattr(llm_client, 'chat'):
                    messages = [{"role": "user", "content": prompt}]
                    llm_response = llm_client.chat(messages)
                    llm_response = llm_response.get('content', str(llm_response))
                else:
                    llm_response = str(llm_client)
                
                # Extract product from LLM response
                product = llm_response.strip().strip('"\'')
                
                if product and len(product) > 0 and product.lower() != "general topic discussion":
                    return {
                        "success": True,
                        "product": product,
                        "confidence": 0.8,
                        "method": "llm_detection",
                        "llm_response": llm_response
                    }
                    
            except Exception as e:
                print(f"LLM product detection failed: {e}")
        
        # Fallback
        return {
            "success": False,
            "product": "Unknown product",
            "confidence": 0.0,
            "method": "no_detection"
        }

class FileOperationTools:
    """Tools for file operations and data persistence"""
    
    @staticmethod
    async def write_file(file_path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Write content to file with proper error handling"""
        
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            file_size = len(content.encode(encoding))
            
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": file_size,
                "encoding": encoding
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    @staticmethod
    async def read_file(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read content from file with proper error handling"""
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "size": len(content),
                "encoding": encoding
            }
            
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "file_path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    @staticmethod
    async def save_json(data: Dict[str, Any], file_path: str, indent: int = 2) -> Dict[str, Any]:
        """Save data as JSON file"""
        
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, default=str)
            
            return {
                "success": True,
                "file_path": file_path,
                "data_keys": list(data.keys())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

class ContentProcessingTools:
    """Tools for content processing and analysis"""
    
    @staticmethod
    async def calculate_text_metrics(text: str) -> Dict[str, Any]:
        """Calculate comprehensive text metrics"""
        
        if not text:
            return {
                "success": True,
                "metrics": {
                    "character_count": 0,
                    "word_count": 0,
                    "sentence_count": 0,
                    "paragraph_count": 0,
                    "avg_word_length": 0,
                    "avg_sentence_length": 0,
                    "reading_time_minutes": 0,
                    "complexity_score": 0
                }
            }
        
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        word_lengths = [len(word) for word in words]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Reading time (average 200 words per minute)
        reading_time = len(words) / 200
        
        # Complexity score (0-100)
        complexity_score = min(100, (
            avg_word_length * 5 +  # Word length contributes
            avg_sentence_length * 2 +  # Sentence length contributes
            len(set(words)) / len(words) * 100 +  # Vocabulary diversity
            (len(sentences) / len(words)) * 50  # Sentence density
        ))
        
        return {
            "success": True,
            "metrics": {
                "character_count": len(text),
                "word_count": len(words),
                "sentence_count": len(sentences),
                "paragraph_count": len(paragraphs),
                "avg_word_length": round(avg_word_length, 2),
                "avg_sentence_length": round(avg_sentence_length, 2),
                "reading_time_minutes": round(reading_time, 1),
                "complexity_score": round(complexity_score, 1)
            }
        }
    
    @staticmethod
    async def extract_key_points(text: str, max_points: int = 5) -> Dict[str, Any]:
        """Extract key points from text using simple heuristics"""
        
        if not text:
            return {
                "success": True,
                "key_points": [],
                "method": "no_content"
            }
        
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        # Score sentences based on various factors
        scored_sentences = []
        for sentence in sentences:
            score = 0
            
            # Length preference (not too short, not too long)
            word_count = len(sentence.split())
            if 10 <= word_count <= 25:
                score += 2
            elif 5 <= word_count <= 35:
                score += 1
            
            # Keywords that indicate importance
            importance_words = ['important', 'key', 'main', 'primary', 'critical', 'essential', 'significant', 'major', 'crucial']
            if any(word in sentence.lower() for word in importance_words):
                score += 2
            
            # Numbers and data points
            if re.search(r'\d+', sentence):
                score += 1
            
            # Questions (often indicate key points)
            if '?' in sentence:
                score += 1
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and get top points
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        key_points = [sentence for sentence, score in scored_sentences[:max_points]]
        
        return {
            "success": True,
            "key_points": key_points,
            "method": "heuristic_scoring",
            "total_sentences": len(sentences)
        }

# Register all tools with the tool registry
def register_legacy_tools():
    """Register all legacy tools with the tool registry"""
    
    from ..tools.executor import tool_registry
    
    # Transcript tools
    tool_registry.register_tool(
        name="extract_video_id",
        description="Extract YouTube video ID from URL",
        parameters={"url": {"type": "string", "required": True}},
        agent_permissions=["all"],
        implementation=TranscriptTools.extract_video_id
    )
    
    tool_registry.register_tool(
        name="extract_youtube_transcript",
        description="Extract transcript from YouTube video",
        parameters={
            "video_id": {"type": "string", "required": True},
            "language": {"type": "string", "default": "en"}
        },
        agent_permissions=["all"],
        implementation=TranscriptTools.extract_youtube_transcript
    )
    
    tool_registry.register_tool(
        name="extract_transcript_with_fallbacks",
        description="Extract transcript with multiple fallback methods",
        parameters={
            "url": {"type": "string", "required": True},
            "use_professional": {"type": "boolean", "default": False}
        },
        agent_permissions=["all"],
        implementation=TranscriptTools.extract_with_fallbacks
    )
    
    # SEO tools
    tool_registry.register_tool(
        name="extract_seo_keywords",
        description="Extract SEO keywords from text",
        parameters={
            "text": {"type": "string", "required": True},
            "target_keywords": {"type": "array", "default": []},
            "max_keywords": {"type": "integer", "default": 20}
        },
        agent_permissions=["content_analyst", "seo_analyst"],
        implementation=SEOTools.extract_keywords
    )
    
    tool_registry.register_tool(
        name="optimize_content_seo",
        description="Optimize content for SEO",
        parameters={
            "content": {"type": "string", "required": True},
            "seo_analysis": {"type": "object", "required": True},
            "content_type": {"type": "string", "default": "blog_post"}
        },
        agent_permissions=["seo_analyst", "blog_writer"],
        implementation=SEOTools.optimize_content_for_seo
    )
    
    # Product detection tools
    tool_registry.register_tool(
        name="detect_product",
        description="Detect product from text content",
        parameters={
            "text": {"type": "string", "required": True}
        },
        agent_permissions=["content_analyst", "product_detector"],
        implementation=ProductDetectionTools.detect_product_from_text
    )
    
    # File operation tools
    tool_registry.register_tool(
        name="write_file",
        description="Write content to file",
        parameters={
            "file_path": {"type": "string", "required": True},
            "content": {"type": "string", "required": True},
            "encoding": {"type": "string", "default": "utf-8"}
        },
        agent_permissions=["all"],
        implementation=FileOperationTools.write_file
    )
    
    tool_registry.register_tool(
        name="read_file",
        description="Read content from file",
        parameters={
            "file_path": {"type": "string", "required": True},
            "encoding": {"type": "string", "default": "utf-8"}
        },
        agent_permissions=["all"],
        implementation=FileOperationTools.read_file
    )
    
    tool_registry.register_tool(
        name="save_json",
        description="Save data as JSON file",
        parameters={
            "data": {"type": "object", "required": True},
            "file_path": {"type": "string", "required": True},
            "indent": {"type": "integer", "default": 2}
        },
        agent_permissions=["all"],
        implementation=FileOperationTools.save_json
    )
    
    # Content processing tools
    tool_registry.register_tool(
        name="calculate_text_metrics",
        description="Calculate comprehensive text metrics",
        parameters={
            "text": {"type": "string", "required": True}
        },
        agent_permissions=["content_analyst", "quality_controller"],
        implementation=ContentProcessingTools.calculate_text_metrics
    )
    
    tool_registry.register_tool(
        name="extract_key_points",
        description="Extract key points from text",
        parameters={
            "text": {"type": "string", "required": True},
            "max_points": {"type": "integer", "default": 5}
        },
        agent_permissions=["content_analyst", "quality_controller"],
        implementation=ContentProcessingTools.extract_key_points
    )

# Auto-register tools when module is imported
register_legacy_tools()
