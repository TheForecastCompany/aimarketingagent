from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from ollama import Client as OllamaClient
import re
import os
from dotenv import load_dotenv
from backend.services.brand_voice import BrandVoice

load_dotenv()

@dataclass
class SEOKeyword:
    """SEO keyword data structure"""
    keyword: str
    frequency: int
    importance: str  # high, medium, low
    category: str  # primary, secondary, entity
    search_intent: str  # informational, commercial, transactional
    competition: str  # high, medium, low
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyword": self.keyword,
            "frequency": self.frequency,
            "importance": self.importance,
            "category": self.category,
            "search_intent": self.search_intent,
            "competition": self.competition
        }

@dataclass
class SEOAnalysis:
    """Complete SEO analysis results"""
    keywords: List[SEOKeyword]
    entities: List[str]
    primary_keywords: List[str]
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    content_gaps: List[str]
    optimization_score: int
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "keywords": [kw.to_dict() for kw in self.keywords],
            "entities": self.entities,
            "primary_keywords": self.primary_keywords,
            "secondary_keywords": self.secondary_keywords,
            "long_tail_keywords": self.long_tail_keywords,
            "content_gaps": self.content_gaps,
            "optimization_score": self.optimization_score,
            "recommendations": self.recommendations
        }

class SEOKeywordExtractor:
    """SEO Specialist Agent - Extracts and analyzes keywords for content optimization"""
    
    def __init__(self, brand_voice: BrandVoice = None):
        self.llm = OllamaClient(
            host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").replace("http://", "")
        )
        self.model = os.getenv("OLLAMA_MODEL", "mistral:latest")
        self.brand_voice = brand_voice
        
        # SEO patterns and indicators
        self.commercial_indicators = [
            'buy', 'price', 'cost', 'deal', 'discount', 'cheap', 'best', 'review',
            'service', 'provider', 'company', 'agency', 'solution', 'product'
        ]
        
        self.technical_indicators = [
            'api', 'software', 'tool', 'platform', 'system', 'technology', 'framework',
            'algorithm', 'data', 'analytics', 'automation', 'integration'
        ]
        
        self.business_indicators = [
            'strategy', 'growth', 'revenue', 'profit', 'marketing', 'sales',
            'business', 'customer', 'client', 'b2b', 'b2c', 'enterprise'
        ]
    
    def extract_keywords(self, transcript: str, target_keywords: List[str] = None, **kwargs) -> SEOAnalysis:
        """Extract and analyze keywords from transcript"""
        
        # Clean and preprocess text
        clean_text = self._preprocess_text(transcript)
        
        # Extract entities using NLP patterns
        entities = self._extract_entities(clean_text)
        
        # Extract keywords from transcript
        extracted_keywords = self._extract_keywords_from_text(clean_text)
        
        # Merge with target keywords if provided
        if target_keywords:
            target_keyword_objects = self._create_target_keywords(target_keywords, clean_text)
            extracted_keywords.extend(target_keyword_objects)
        
        # Categorize and analyze keywords
        categorized_keywords = self._categorize_keywords(extracted_keywords)
        
        # Generate SEO insights
        primary_keywords = self._identify_primary_keywords(categorized_keywords)
        secondary_keywords = self._identify_secondary_keywords(categorized_keywords)
        long_tail_keywords = self._generate_long_tail_keywords(categorized_keywords)
        
        # Identify content gaps
        content_gaps = self._identify_content_gaps(categorized_keywords, target_keywords)
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(categorized_keywords)
        
        # Generate recommendations
        recommendations = self._generate_seo_recommendations(
            categorized_keywords, content_gaps, optimization_score
        )
        
        return SEOAnalysis(
            keywords=categorized_keywords,
            entities=entities,
            primary_keywords=primary_keywords,
            secondary_keywords=secondary_keywords,
            long_tail_keywords=long_tail_keywords,
            content_gaps=content_gaps,
            optimization_score=optimization_score,
            recommendations=recommendations
        )
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for keyword extraction"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities (products, companies, technologies)"""
        entities = []
        
        # Pattern for capitalized words/phrases (potential entities)
        # This is a simplified approach - in production, use proper NLP
        entity_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper nouns
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+\.\w+\b',  # Domain names
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        # Filter common words and duplicates
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        entities = [e for e in entities if e.lower() not in stop_words and len(e) > 2]
        
        return list(set(entities))
    
    def _extract_keywords_from_text(self, text: str) -> List[SEOKeyword]:
        """Extract keywords from text using frequency and importance analysis"""
        words = text.split()
        word_freq = {}
        
        # Count word frequencies
        for word in words:
            if len(word) > 3:  # Ignore very short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Filter for meaningful frequency
        meaningful_words = {word: freq for word, freq in word_freq.items() if freq >= 2}
        
        # Create SEOKeyword objects
        keywords = []
        for word, freq in meaningful_words.items():
            importance = self._determine_importance(word, freq)
            category = self._determine_category(word)
            search_intent = self._determine_search_intent(word)
            competition = self._estimate_competition(word)
            
            keywords.append(SEOKeyword(
                keyword=word,
                frequency=freq,
                importance=importance,
                category=category,
                search_intent=search_intent,
                competition=competition
            ))
        
        return keywords
    
    def _create_target_keywords(self, target_keywords: List[str], text: str) -> List[SEOKeyword]:
        """Create SEOKeyword objects for user-provided target keywords"""
        keywords = []
        text_lower = text.lower()
        
        for target in target_keywords:
            target_lower = target.lower()
            frequency = text_lower.count(target_lower)
            
            importance = "high"  # Target keywords are always high importance
            category = "primary"
            search_intent = self._determine_search_intent(target_lower)
            competition = self._estimate_competition(target_lower)
            
            keywords.append(SEOKeyword(
                keyword=target,
                frequency=frequency,
                importance=importance,
                category=category,
                search_intent=search_intent,
                competition=competition
            ))
        
        return keywords
    
    def _determine_importance(self, word: str, frequency: int) -> str:
        """Determine keyword importance based on frequency and context"""
        if frequency >= 5:
            return "high"
        elif frequency >= 3:
            return "medium"
        else:
            return "low"
    
    def _determine_category(self, word: str) -> str:
        """Categorize keyword based on its nature"""
        if any(indicator in word for indicator in self.commercial_indicators):
            return "commercial"
        elif any(indicator in word for indicator in self.technical_indicators):
            return "technical"
        elif any(indicator in word for indicator in self.business_indicators):
            return "business"
        else:
            return "general"
    
    def _determine_search_intent(self, word: str) -> str:
        """Determine search intent for keyword"""
        if any(indicator in word for indicator in self.commercial_indicators):
            return "commercial"
        elif word in ['how', 'what', 'why', 'when', 'where', 'guide', 'tutorial']:
            return "informational"
        else:
            return "transactional"
    
    def _estimate_competition(self, word: str) -> str:
        """Estimate keyword competition (simplified)"""
        # In production, this would use actual SEO data
        high_competition_words = ['marketing', 'business', 'software', 'technology', 'data']
        
        if word in high_competition_words or len(word) < 4:
            return "high"
        elif len(word) > 8:
            return "low"
        else:
            return "medium"
    
    def _categorize_keywords(self, keywords: List[SEOKeyword]) -> List[SEOKeyword]:
        """Sort and categorize keywords by importance"""
        return sorted(keywords, key=lambda x: (x.importance != "high", x.frequency), reverse=True)
    
    def _identify_primary_keywords(self, keywords: List[SEOKeyword]) -> List[str]:
        """Identify primary keywords (high importance, high frequency)"""
        primary = [kw.keyword for kw in keywords if kw.importance == "high" and kw.frequency >= 3]
        return primary[:5]  # Top 5 primary keywords
    
    def _identify_secondary_keywords(self, keywords: List[SEOKeyword]) -> List[str]:
        """Identify secondary keywords (medium importance)"""
        secondary = [kw.keyword for kw in keywords if kw.importance == "medium"]
        return secondary[:10]  # Top 10 secondary keywords
    
    def _generate_long_tail_keywords(self, keywords: List[SEOKeyword]) -> List[str]:
        """Generate long-tail keyword suggestions"""
        primary_keywords = [kw.keyword for kw in keywords if kw.importance == "high"][:3]
        
        long_tail = []
        templates = [
            "{} guide", "{} tutorial", "{} best practices", "{} for beginners",
            "how to use {}", "{} vs alternatives", "{} pricing", "{} review"
        ]
        
        for keyword in primary_keywords:
            for template in templates:
                long_tail.append(template.format(keyword))
        
        return long_tail[:15]  # Top 15 long-tail suggestions
    
    def _identify_content_gaps(self, keywords: List[SEOKeyword], target_keywords: List[str]) -> List[str]:
        """Identify content gaps based on missing keywords"""
        found_keywords = {kw.keyword.lower() for kw in keywords}
        
        gaps = []
        if target_keywords:
            for target in target_keywords:
                if target.lower() not in found_keywords:
                    gaps.append(f"Target keyword '{target}' not found in content")
        
        # Check for missing important categories
        categories = {kw.category for kw in keywords}
        if "commercial" not in categories:
            gaps.append("Missing commercial intent keywords")
        
        if len(gaps) == 0:
            gaps.append("No significant content gaps identified")
        
        return gaps
    
    def _calculate_optimization_score(self, keywords: List[SEOKeyword]) -> int:
        """Calculate SEO optimization score (0-100)"""
        score = 0
        
        # Keyword diversity (max 20 points)
        unique_categories = len({kw.category for kw in keywords})
        score += min(unique_categories * 5, 20)
        
        # Keyword frequency (max 30 points)
        high_freq_keywords = len([kw for kw in keywords if kw.frequency >= 3])
        score += min(high_freq_keywords * 6, 30)
        
        # Search intent diversity (max 20 points)
        unique_intents = len({kw.search_intent for kw in keywords})
        score += min(unique_intents * 7, 20)
        
        # Long-tail potential (max 30 points)
        medium_freq_keywords = len([kw for kw in keywords if kw.frequency == 2])
        score += min(medium_freq_keywords * 10, 30)
        
        return min(score, 100)
    
    def _generate_seo_recommendations(self, keywords: List[SEOKeyword], 
                                    content_gaps: List[str], score: int) -> List[str]:
        """Generate SEO optimization recommendations"""
        recommendations = []
        
        if score < 60:
            recommendations.append("SEO optimization needed - focus on keyword diversity and frequency")
        
        # Keyword recommendations
        primary_count = len([kw for kw in keywords if kw.importance == "high"])
        if primary_count < 3:
            recommendations.append("Add more primary keywords (3-5 high-importance keywords)")
        
        # Category recommendations
        categories = {kw.category for kw in keywords}
        if "commercial" not in categories:
            recommendations.append("Include commercial intent keywords for better conversion")
        
        # Content gap recommendations
        for gap in content_gaps:
            if "not found" in gap:
                recommendations.append(f"Address content gap: {gap}")
        
        # Frequency recommendations
        low_freq_keywords = [kw for kw in keywords if kw.frequency < 3 and kw.importance == "high"]
        if low_freq_keywords:
            missing_keywords = [kw.keyword for kw in low_freq_keywords[:3]]
            recommendations.append(f"Increase frequency of important keywords: {', '.join(missing_keywords)}")
        
        # General recommendations
        recommendations.append("Ensure keywords appear naturally in headings and subheadings")
        recommendations.append("Use keywords in meta descriptions and image alt texts")
        
        return recommendations
    
    def optimize_content_for_seo(self, content: str, seo_analysis: SEOAnalysis, 
                                 content_type: str) -> str:
        """Optimize content based on SEO analysis"""
        
        brand_guidelines = ""
        if self.brand_voice:
            try:
                brand_guidelines = self.brand_voice.to_prompt_extension()
            except AttributeError:
                # Handle BrandVoice enum
                brand_guidelines = f"""
Brand Voice: {self.brand_voice.value if hasattr(self.brand_voice, 'value') else str(self.brand_voice)}
Tone: Professional and engaging
Style: Clear, concise, and informative
                """.strip()
        
        prompt = f"""
        You are an SEO Content Specialist. Optimize this {content_type} for search engines.
        
        {brand_guidelines}
        
        SEO Analysis:
        - Primary Keywords: {', '.join(seo_analysis.primary_keywords[:5]) if seo_analysis and hasattr(seo_analysis, 'primary_keywords') else 'N/A'}
        - Secondary Keywords: {', '.join(seo_analysis.secondary_keywords[:5]) if seo_analysis and hasattr(seo_analysis, 'secondary_keywords') else 'N/A'}
        - Target Search Intent: Mix of informational and commercial
        - Optimization Score: {seo_analysis.optimization_score if seo_analysis and hasattr(seo_analysis, 'optimization_score') else 'N/A'}
        
        Original Content:
        {content}
        
        Optimization Requirements:
        1. Naturally integrate 2-3 primary keywords
        2. Include 3-4 secondary keywords
        3. Maintain brand voice and readability
        4. Add SEO-friendly headings if applicable
        5. Include a call-to-action with keyword
        6. Keep content engaging and valuable
        
        Return the optimized content:
        """
        
        try:
            response = self.llm.generate(prompt=prompt, model=self.model)
            if response and response.done and response.response:
                return response.response
            else:
                print(f"SEO optimization failed: No response from Ollama")
                return content
        except Exception as e:
            print(f"SEO optimization failed: {e}")
            return content
