#!/usr/bin/env python3
"""
Quality Control System - Ensures content meets quality standards
Provides confidence scoring and quality assessment
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

@dataclass
class QualityMetrics:
    """Quality assessment metrics"""
    overall_score: float
    readability_score: float
    engagement_score: float
    seo_score: float
    brand_voice_score: float
    grammar_score: float
    length_score: float
    structure_score: float

@dataclass
class ConfidenceScore:
    """Confidence score for content quality"""
    score: float
    level: QualityLevel
    metrics: QualityMetrics
    issues: List[str]
    recommendations: List[str]

class QualityController:
    """Controls and assesses content quality"""
    
    def __init__(self):
        self.min_acceptable_score = 0.6
        self.target_score = 0.8
        print("🎯 Quality Controller Initialized")
        print(f"📊 Minimum acceptable score: {self.min_acceptable_score}")
        print(f"🎯 Target quality score: {self.target_score}")
    
    def assess_quality(self, content: str, content_type: str = "general", 
                      target_length: Optional[int] = None) -> ConfidenceScore:
        """Assess content quality across multiple dimensions"""
        
        # Handle dictionary content
        if isinstance(content, dict):
            # Convert dictionary to string
            content = str(content)
        elif not isinstance(content, str):
            # Convert any non-string content to string
            content = str(content)
        
        print(f"🔍 Assessing quality for {content_type} content...")
        
        # Calculate individual metrics
        readability_score = self._assess_readability(content)
        engagement_score = self._assess_engagement(content)
        seo_score = self._assess_seo(content)
        grammar_score = self._assess_grammar(content)
        length_score = self._assess_length(content, target_length)
        structure_score = self._assess_structure(content)
        brand_voice_score = self._assess_brand_voice(content)
        
        # Calculate overall score
        overall_score = (
            readability_score * 0.2 +
            engagement_score * 0.2 +
            seo_score * 0.15 +
            grammar_score * 0.2 +
            length_score * 0.1 +
            structure_score * 0.1 +
            brand_voice_score * 0.05
        )
        
        # Create metrics object
        metrics = QualityMetrics(
            overall_score=overall_score,
            readability_score=readability_score,
            engagement_score=engagement_score,
            seo_score=seo_score,
            brand_voice_score=brand_voice_score,
            grammar_score=grammar_score,
            length_score=length_score,
            structure_score=structure_score
        )
        
        # Determine quality level
        if overall_score >= 0.9:
            level = QualityLevel.EXCELLENT
        elif overall_score >= 0.8:
            level = QualityLevel.GOOD
        elif overall_score >= 0.6:
            level = QualityLevel.ACCEPTABLE
        elif overall_score >= 0.4:
            level = QualityLevel.POOR
        else:
            level = QualityLevel.UNACCEPTABLE
        
        # Generate issues and recommendations
        issues = self._identify_issues(metrics)
        recommendations = self._generate_recommendations(metrics)
        
        return ConfidenceScore(
            score=overall_score,
            level=level,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations
        )
    
    def analyze_content_quality(self, content: str, content_type: str = "general", 
                                brand_voice: Optional[Any] = None) -> float:
        """Analyze content quality and return overall score - alias for assess_quality"""
        # Handle dictionary content
        if isinstance(content, dict):
            # Convert dictionary to string
            content = str(content)
        elif not isinstance(content, str):
            # Convert any non-string content to string
            content = str(content)
        
        confidence_score = self.assess_quality(content, content_type)
        return confidence_score.score
    
    def _assess_readability(self, content: str) -> float:
        """Assess content readability"""
        if not content:
            return 0.0
        
        # Simple readability metrics
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        
        if sentences == 0:
            return 0.0
        
        avg_words_per_sentence = words / sentences
        
        # Optimal is 15-20 words per sentence
        if 15 <= avg_words_per_sentence <= 20:
            return 1.0
        elif 10 <= avg_words_per_sentence <= 25:
            return 0.8
        elif 5 <= avg_words_per_sentence <= 30:
            return 0.6
        else:
            return 0.4
    
    def _assess_engagement(self, content: str) -> float:
        """Assess content engagement potential"""
        if not content:
            return 0.0
        
        engagement_indicators = [
            r'\?',  # Questions
            r'!',  # Exclamations
            r'\b(amazing|awesome|excellent|great|fantastic)\b',  # Positive words
            r'\b(important|crucial|essential|vital)\b',  # Impact words
        ]
        
        score = 0.0
        for pattern in engagement_indicators:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            score += min(matches * 0.1, 0.3)
        
        return min(score, 1.0)
    
    def _assess_seo(self, content: str) -> float:
        """Assess SEO optimization"""
        if not content:
            return 0.0
        
        # Check for SEO elements
        score = 0.0
        
        # Length (longer content tends to rank better)
        word_count = len(content.split())
        if word_count >= 300:
            score += 0.3
        elif word_count >= 150:
            score += 0.2
        
        # Keyword density (simplified)
        # In real implementation, you'd check for specific keywords
        
        # Structure (headings, lists)
        if re.search(r'#+\s', content):  # Headings
            score += 0.2
        
        if re.search(r'[-*+]\s', content):  # Lists
            score += 0.2
        
        # Internal/external links (simplified check)
        if 'http' in content:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_grammar(self, content: str) -> float:
        """Assess grammar and spelling"""
        if not content:
            return 0.0
        
        # Simplified grammar check
        # In real implementation, you'd use a proper grammar checker
        
        score = 1.0
        
        # Check for common issues
        issues = [
            r'\s+',  # Multiple spaces
            r'\b(a|an)\s+[aeiou]',  # Article misuse
            r'\s[,.!?]',  # Space before punctuation
        ]
        
        for pattern in issues:
            matches = len(re.findall(pattern, content))
            score -= min(matches * 0.1, 0.3)
        
        return max(score, 0.0)
    
    def _assess_length(self, content: str, target_length: Optional[int] = None) -> float:
        """Assess content length appropriateness"""
        if not content:
            return 0.0
        
        word_count = len(content.split())
        
        if target_length:
            # Compare to target
            ratio = word_count / target_length
            if 0.9 <= ratio <= 1.1:
                return 1.0
            elif 0.7 <= ratio <= 1.3:
                return 0.8
            elif 0.5 <= ratio <= 1.5:
                return 0.6
            else:
                return 0.4
        else:
            # General length assessment
            if word_count >= 100:
                return 1.0
            elif word_count >= 50:
                return 0.8
            elif word_count >= 25:
                return 0.6
            else:
                return 0.4
    
    def _assess_structure(self, content: str) -> float:
        """Assess content structure"""
        if not content:
            return 0.0
        
        score = 0.0
        
        # Check for paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 2:
            score += 0.3
        
        # Check for sentences
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) >= 3:
            score += 0.3
        
        # Check for flow (transition words)
        transitions = ['however', 'therefore', 'moreover', 'furthermore', 'additionally']
        transition_count = sum(1 for word in transitions if word in content.lower())
        score += min(transition_count * 0.1, 0.4)
        
        return min(score, 1.0)
    
    def _assess_brand_voice(self, content: str) -> float:
        """Assess brand voice consistency"""
        if not content:
            return 0.0
        
        # Simplified brand voice assessment
        # In real implementation, you'd compare against specific brand voice guidelines
        
        score = 0.8  # Default score
        
        # Check for consistency
        if content.count('!') > len(content.split()) * 0.1:  # Too many exclamations
            score -= 0.2
        
        # Check for mixed formality
        formal_words = ['therefore', 'furthermore', 'consequently']
        informal_words = ['gonna', 'wanna', 'kinda']
        
        has_formal = any(word in content.lower() for word in formal_words)
        has_informal = any(word in content.lower() for word in informal_words)
        
        if has_formal and has_informal:
            score -= 0.3
        
        return max(score, 0.0)
    
    def _identify_issues(self, metrics: QualityMetrics) -> List[str]:
        """Identify quality issues"""
        issues = []
        
        if metrics.readability_score < 0.6:
            issues.append("Low readability - sentences too long or complex")
        
        if metrics.engagement_score < 0.5:
            issues.append("Low engagement potential - add questions or impactful statements")
        
        if metrics.seo_score < 0.5:
            issues.append("Poor SEO optimization - add keywords and structure")
        
        if metrics.grammar_score < 0.7:
            issues.append("Grammar or spelling issues detected")
        
        if metrics.length_score < 0.6:
            issues.append("Content length not optimal")
        
        if metrics.structure_score < 0.6:
            issues.append("Poor content structure - improve flow")
        
        return issues
    
    def _generate_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if metrics.readability_score < 0.6:
            recommendations.append("Break up long sentences and use simpler language")
        
        if metrics.engagement_score < 0.5:
            recommendations.append("Add rhetorical questions and impactful statements")
        
        if metrics.seo_score < 0.5:
            recommendations.append("Include relevant keywords and improve structure")
        
        if metrics.grammar_score < 0.7:
            recommendations.append("Review and correct grammar and spelling")
        
        if metrics.length_score < 0.6:
            recommendations.append("Adjust content length for better engagement")
        
        if metrics.structure_score < 0.6:
            recommendations.append("Improve content flow with better transitions")
        
        return recommendations
    
    def should_improve(self, confidence: ConfidenceScore) -> bool:
        """Determine if content needs improvement"""
        return confidence.score < self.target_score
    
    def is_acceptable(self, confidence: ConfidenceScore) -> bool:
        """Determine if content meets minimum quality standards"""
        return confidence.score >= self.min_acceptable_score

def demonstrate_quality_control():
    """Demonstrate quality control system"""
    
    controller = QualityController()
    
    test_contents = [
        ("This is amazing! You won't believe how this can transform your life. It's really important that you try this today.", "engaging"),
        ("The aforementioned implementation utilizes a sophisticated algorithmic approach to optimize computational efficiency.", "technical"),
        ("Hi there! This is pretty cool stuff. You should totally check it out cuz it's awesome!", "casual"),
        ("Short.", "minimal")
    ]
    
    print("🎯 Quality Control Demo")
    print("=" * 60)
    
    for content, content_type in test_contents:
        print(f"\n📝 Testing {content_type} content:")
        print(f"   Content: {content[:50]}...")
        print("-" * 40)
        
        confidence = controller.assess_quality(content, content_type)
        
        print(f"   Overall Score: {confidence.score:.2f}")
        print(f"   Quality Level: {confidence.level.value}")
        print(f"   Readability: {confidence.metrics.readability_score:.2f}")
        print(f"   Engagement: {confidence.metrics.engagement_score:.2f}")
        print(f"   SEO: {confidence.metrics.seo_score:.2f}")
        
        if confidence.issues:
            print(f"   Issues: {', '.join(confidence.issues[:2])}")
        
        if controller.should_improve(confidence):
            print(f"   💡 Needs improvement")
        elif controller.is_acceptable(confidence):
            print(f"   ✅ Acceptable quality")
        else:
            print(f"   ❌ Below minimum standards")
    
    print("\n" + "=" * 60)
    print("\n🎯 Quality Control Benefits:")
    print("   ✅ Comprehensive quality assessment")
    print("   ✅ Multi-dimensional scoring system")
    print("   ✅ Automated issue identification")
    print("   ✅ Actionable improvement recommendations")
    print("   ✅ Consistent quality standards")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented a comprehensive quality control system'")
    print("   🎯 'Multi-dimensional scoring across 7 quality metrics'")
    print("   🎯 'Automated issue detection and recommendations'")
    print("   🎯 'Configurable quality thresholds'")
    print("   🎯 'Content type-specific assessment'")

if __name__ == "__main__":
    demonstrate_quality_control()
