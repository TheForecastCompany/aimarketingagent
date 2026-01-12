#!/usr/bin/env python3
"""
Agentic Critique Loop - Implements iterative improvement through AI critique
Uses multiple agents to review and improve content quality
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class CritiqueLevel(Enum):
    """Critique severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

@dataclass
class CritiquePoint:
    """Individual critique point"""
    category: str
    severity: CritiqueLevel
    description: str
    suggestion: str
    confidence: float

@dataclass
class CritiqueResult:
    """Result of content critique"""
    overall_score: float
    critique_points: List[CritiquePoint]
    improvement_suggestions: List[str]
    should_revise: bool
    revision_priority: str

class AgenticCritiqueLoop:
    """Implements iterative content improvement through critique"""
    
    def __init__(self, max_iterations: int = 3, min_quality_score: float = 0.7):
        self.max_iterations = max_iterations
        self.min_quality_score = min_quality_score
        self.critique_agents = self._initialize_critique_agents()
        print("🔄 Agentic Critique Loop Initialized")
        print(f"📊 Max iterations: {max_iterations}")
        print(f"🎯 Minimum quality score: {min_quality_score}")
    
    def _initialize_critique_agents(self) -> Dict[str, Any]:
        """Initialize specialized critique agents"""
        return {
            "grammar": GrammarCritiqueAgent(),
            "style": StyleCritiqueAgent(),
            "engagement": EngagementCritiqueAgent(),
            "seo": SEOCritiqueAgent(),
            "brand_voice": BrandVoiceCritiqueAgent()
        }
    
    def critique_and_improve(self, content: str, content_type: str, 
                           brand_voice: str = "professional") -> Dict[str, Any]:
        """Run critique loop to improve content"""
        print(f"🔄 Starting critique loop for {content_type} content")
        print(f"🔍 Debug: Input content type: {type(content)}, length: {len(content) if content else 'None'}")
        
        current_content = content
        iteration = 0
        critique_history = []
        
        while iteration < self.max_iterations:
            print(f"\n📝 Iteration {iteration + 1}/{self.max_iterations}")
            
            # Run critique on current content
            critique_result = self._run_critique(current_content, content_type, brand_voice)
            critique_history.append(critique_result)
            
            # Check if content meets quality standards
            if critique_result.overall_score >= self.min_quality_score:
                print(f"✅ Quality threshold met ({critique_result.overall_score:.2f} >= {self.min_quality_score})")
                break
            
            # Apply improvements
            if critique_result.should_revise:
                print(f"🔧 Applying improvements...")
                current_content = self._apply_improvements(current_content, critique_result)
            else:
                print("📋 No major revisions needed")
                break
            
            iteration += 1
        
        # Final assessment
        final_critique = self._run_critique(current_content, content_type, brand_voice)
        
        return {
            "original_content": content,
            "improved_content": current_content,
            "iterations": iteration + 1,
            "final_score": final_critique.overall_score,
            "critique_history": critique_history,
            "improvement_summary": self._generate_improvement_summary(content, current_content, critique_history),
            "quality_metrics": self._calculate_quality_metrics(final_critique)
        }
    
    def _run_critique(self, content: str, content_type: str, brand_voice: str) -> CritiqueResult:
        """Run all critique agents on content"""
        # Debug: Check what content we received
        print(f"   🔍 Debug: Content type: {type(content)}, length: {len(content) if content else 'None'}")
        print(f"   🔍 Debug: Content preview: {content[:100] if content else 'None'}...")
        
        if not content or not isinstance(content, str):
            print(f"   ❌ Error: Invalid content - type: {type(content)}, value: {content}")
            # Return a default critique result to avoid infinite loop
            return CritiqueResult(
                overall_score=0.5,
                critique_points=[],
                improvement_suggestions=["Content is invalid or empty"],
                should_revise=False,
                revision_priority="low"
            )
        
        all_critiques = []
        
        # Run each critique agent
        for agent_name, agent in self.critique_agents.items():
            print(f"   🔍 Running {agent_name} critique...")
            critiques = agent.critique(content, content_type, brand_voice)
            all_critiques.extend(critiques)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(all_critiques)
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(all_critiques)
        
        # Determine if revision is needed
        should_revise = overall_score < self.min_quality_score or any(
            c.severity == CritiqueLevel.CRITICAL for c in all_critiques
        )
        
        # Determine revision priority
        revision_priority = self._determine_revision_priority(all_critiques)
        
        return CritiqueResult(
            overall_score=overall_score,
            critique_points=all_critiques,
            improvement_suggestions=suggestions,
            should_revise=should_revise,
            revision_priority=revision_priority
        )
    
    def _calculate_overall_score(self, critiques: List[CritiquePoint]) -> float:
        """Calculate overall quality score from critiques"""
        if not critiques:
            return 1.0
        
        # Start with perfect score and subtract based on critiques
        score = 1.0
        
        for critique in critiques:
            if critique.severity == CritiqueLevel.CRITICAL:
                score -= 0.3
            elif critique.severity == CritiqueLevel.MAJOR:
                score -= 0.2
            elif critique.severity == CritiqueLevel.MODERATE:
                score -= 0.1
            elif critique.severity == CritiqueLevel.MINOR:
                score -= 0.05
        
        return max(score, 0.0)
    
    def _generate_suggestions(self, critiques: List[CritiquePoint]) -> List[str]:
        """Generate improvement suggestions from critiques"""
        suggestions = []
        
        # Group critiques by category
        by_category = {}
        for critique in critiques:
            if critique.category not in by_category:
                by_category[critique.category] = []
            by_category[critique.category].append(critique)
        
        # Generate suggestions for each category
        for category, category_critiques in by_category.items():
            # Get the most severe critique in each category
            most_severe = max(category_critiques, key=lambda c: c.severity.value)
            suggestions.append(most_severe.suggestion)
        
        return suggestions
    
    def _determine_revision_priority(self, critiques: List[CritiquePoint]) -> str:
        """Determine revision priority based on critiques"""
        if any(c.severity == CritiqueLevel.CRITICAL for c in critiques):
            return "critical"
        elif any(c.severity == CritiqueLevel.MAJOR for c in critiques):
            return "high"
        elif any(c.severity == CritiqueLevel.MODERATE for c in critiques):
            return "medium"
        else:
            return "low"
    
    def _apply_improvements(self, content: str, critique_result: CritiqueResult) -> str:
        """Apply improvements based on critique"""
        print(f"   🔍 Debug: _apply_improvements called with content length: {len(content)}")
        print(f"   🔍 Debug: critique_result type: {type(critique_result)}")
        
        if not critique_result or not hasattr(critique_result, 'critique_points'):
            print(f"   ❌ Error: Invalid critique_result - type: {type(critique_result)}")
            return content
        
        print(f"   🔍 Debug: critique_points length: {len(critique_result.critique_points)}")
        
        improved_content = content
        
        # Apply improvements based on severity
        for critique in critique_result.critique_points:
            print(f"   🔍 Debug: Processing critique: {critique.category} - {critique.severity}")
            if critique.severity in [CritiqueLevel.CRITICAL, CritiqueLevel.MAJOR]:
                print(f"   🔧 Applying specific improvement for {critique.category}")
                improved_content = self._apply_specific_improvement(improved_content, critique)
        
        print(f"   🔍 Debug: Final improved content length: {len(improved_content)}")
        return improved_content
    
    def _apply_specific_improvement(self, content: str, critique: CritiquePoint) -> str:
        """Apply specific improvement based on critique"""
        # This is a simplified implementation
        # In a real system, you'd use more sophisticated NLP techniques
        
        if critique.category == "grammar":
            # Apply grammar fixes
            content = content.replace("  ", " ")  # Remove double spaces
            content = content.replace(" .", ".")  # Fix spacing before periods
        
        elif critique.category == "style":
            # Apply style improvements
            if "short" in critique.description.lower():
                # Break up long sentences (simplified)
                sentences = content.split('.')
                improved_sentences = []
                for sentence in sentences:
                    if len(sentence.split()) > 30:
                        # Split long sentence
                        words = sentence.split()
                        mid = len(words) // 2
                        improved_sentences.append(' '.join(words[:mid]) + '.')
                        improved_sentences.append(' '.join(words[mid:]) + '.')
                    else:
                        improved_sentences.append(sentence + '.')
                content = ' '.join(improved_sentences)
        
        elif critique.category == "engagement":
            # Add engagement elements
            if "question" in critique.suggestion.lower():
                if not content.strip().endswith('?'):
                    content += "\n\nWhat are your thoughts on this?"
        
        return content
    
    def _generate_improvement_summary(self, original: str, improved: str, 
                                   history: List[CritiqueResult]) -> Dict[str, Any]:
        """Generate summary of improvements made"""
        return {
            "original_length": len(original.split()),
            "improved_length": len(improved.split()),
            "length_change": len(improved.split()) - len(original.split()),
            "iterations": len(history),
            "initial_score": history[0].overall_score if history else 0.0,
            "final_score": history[-1].overall_score if history else 0.0,
            "score_improvement": history[-1].overall_score - history[0].overall_score if history else 0.0,
            "major_issues_fixed": sum(1 for h in history for c in h.critique_points 
                                   if c.severity in [CritiqueLevel.CRITICAL, CritiqueLevel.MAJOR])
        }
    
    def _calculate_quality_metrics(self, final_critique: CritiqueResult) -> Dict[str, Any]:
        """Calculate final quality metrics"""
        return {
            "overall_score": final_critique.overall_score,
            "total_issues": len(final_critique.critique_points),
            "critical_issues": len([c for c in final_critique.critique_points 
                                 if c.severity == CritiqueLevel.CRITICAL]),
            "major_issues": len([c for c in final_critique.critique_points 
                              if c.severity == CritiqueLevel.MAJOR]),
            "moderate_issues": len([c for c in final_critique.critique_points 
                                  if c.severity == CritiqueLevel.MODERATE]),
            "minor_issues": len([c for c in final_critique.critique_points 
                               if c.severity == CritiqueLevel.MINOR])
        }

class BaseCritiqueAgent:
    """Base class for critique agents"""
    
    def __init__(self, name: str):
        self.name = name
        print(f"🔍 {name} Critique Agent Ready")
    
    def critique(self, content: str, content_type: str, brand_voice: str) -> List[CritiquePoint]:
        """Critique content and return improvement points"""
        raise NotImplementedError

class GrammarCritiqueAgent(BaseCritiqueAgent):
    """Critiques grammar and spelling"""
    
    def __init__(self):
        super().__init__("Grammar")
    
    def critique(self, content: str, content_type: str, brand_voice: str) -> List[CritiquePoint]:
        """Critique grammar and spelling"""
        critiques = []
        
        # Check for common grammar issues
        if '  ' in content:  # Double spaces
            critiques.append(CritiquePoint(
                category="grammar",
                severity=CritiqueLevel.MINOR,
                description="Double spaces detected",
                suggestion="Remove extra spaces between words",
                confidence=0.9
            ))
        
        # Check for sentence fragments (simplified)
        sentences = content.split('.')
        short_sentences = [s for s in sentences if len(s.split()) < 3 and s.strip()]
        
        if len(short_sentences) > len(sentences) * 0.3:  # More than 30% short sentences
            critiques.append(CritiquePoint(
                category="grammar",
                severity=CritiqueLevel.MODERATE,
                description="Too many short sentences",
                suggestion="Combine short sentences for better flow",
                confidence=0.7
            ))
        
        # Check for capitalization
        if content and not content[0].isupper():
            critiques.append(CritiquePoint(
                category="grammar",
                severity=CritiqueLevel.MINOR,
                description="Content starts with lowercase",
                suggestion="Start content with uppercase letter",
                confidence=0.8
            ))
        
        return critiques

class StyleCritiqueAgent(BaseCritiqueAgent):
    """Critiques writing style and tone"""
    
    def __init__(self):
        super().__init__("Style")
    
    def critique(self, content: str, content_type: str, brand_voice: str) -> List[CritiquePoint]:
        """Critique writing style"""
        critiques = []
        
        # Check sentence length variety
        sentences = content.split('.')
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            
            if avg_length > 25:
                critiques.append(CritiquePoint(
                    category="style",
                    severity=CritiqueLevel.MODERATE,
                    description="Sentences are too long on average",
                    suggestion="Break up long sentences for better readability",
                    confidence=0.8
                ))
            elif avg_length < 10:
                critiques.append(CritiquePoint(
                    category="style",
                    severity=CritiqueLevel.MODERATE,
                    description="Sentences are too short on average",
                    suggestion="Combine short sentences for better flow",
                    confidence=0.8
                ))
        
        # Check for passive voice (simplified)
        passive_indicators = ['is', 'are', 'was', 'were', 'been', 'being']
        passive_count = sum(1 for word in passive_indicators if word in content.lower().split())
        
        if passive_count > len(content.split()) * 0.1:  # More than 10% passive
            critiques.append(CritiquePoint(
                category="style",
                severity=CritiqueLevel.MINOR,
                description="High passive voice usage",
                suggestion="Use more active voice for engaging content",
                confidence=0.6
            ))
        
        return critiques

class EngagementCritiqueAgent(BaseCritiqueAgent):
    """Critiques engagement potential"""
    
    def __init__(self):
        super().__init__("Engagement")
    
    def critique(self, content: str, content_type: str, brand_voice: str) -> List[CritiquePoint]:
        """Critique engagement potential"""
        critiques = []
        
        # Check for questions
        if '?' not in content:
            critiques.append(CritiquePoint(
                category="engagement",
                severity=CritiqueLevel.MODERATE,
                description="No questions to engage readers",
                suggestion="Add rhetorical questions to increase engagement",
                confidence=0.7
            ))
        
        # Check for emotional words
        emotional_words = ['amazing', 'exciting', 'wonderful', 'fantastic', 'incredible', 
                          'important', 'crucial', 'essential', 'powerful']
        emotional_count = sum(1 for word in emotional_words if word in content.lower())
        
        if emotional_count == 0:
            critiques.append(CritiquePoint(
                category="engagement",
                severity=CritiqueLevel.MINOR,
                description="No emotional language detected",
                suggestion="Add emotional words to increase engagement",
                confidence=0.6
            ))
        
        # Check for call to action
        cta_phrases = ['click here', 'learn more', 'find out', 'discover', 'explore']
        has_cta = any(phrase in content.lower() for phrase in cta_phrases)
        
        if not has_cta and content_type in ['blog', 'newsletter']:
            critiques.append(CritiquePoint(
                category="engagement",
                severity=CritiqueLevel.MODERATE,
                description="No clear call to action",
                suggestion="Add a clear call to action for readers",
                confidence=0.8
            ))
        
        return critiques

class SEOCritiqueAgent(BaseCritiqueAgent):
    """Critiques SEO optimization"""
    
    def __init__(self):
        super().__init__("SEO")
    
    def critique(self, content: str, content_type: str, brand_voice: str) -> List[CritiquePoint]:
        """Critique SEO optimization"""
        critiques = []
        
        word_count = len(content.split())
        
        # Check content length
        if content_type == 'blog' and word_count < 300:
            critiques.append(CritiquePoint(
                category="seo",
                severity=CritiqueLevel.MAJOR,
                description="Blog content too short for SEO",
                suggestion="Expand content to at least 300 words for better SEO",
                confidence=0.9
            ))
        
        # Check for structure (headings)
        if content_type in ['blog'] and '#' not in content:
            critiques.append(CritiquePoint(
                category="seo",
                severity=CritiqueLevel.MODERATE,
                description="No headings detected",
                suggestion="Add headings to improve content structure and SEO",
                confidence=0.8
            ))
        
        # Check for keyword density (simplified)
        # In real implementation, you'd check for specific keywords
        
        return critiques

class BrandVoiceCritiqueAgent(BaseCritiqueAgent):
    """Critiques brand voice consistency"""
    
    def __init__(self):
        super().__init__("Brand Voice")
    
    def critique(self, content: str, content_type: str, brand_voice: str) -> List[CritiquePoint]:
        """Critique brand voice consistency"""
        critiques = []
        
        # Check formality consistency
        formal_words = ['therefore', 'furthermore', 'consequently', 'however']
        informal_words = ['gonna', 'wanna', 'kinda', 'sorta', 'awesome', 'cool']
        
        has_formal = any(word in content.lower() for word in formal_words)
        has_informal = any(word in content.lower() for word in informal_words)
        
        if brand_voice == "professional" and has_informal:
            critiques.append(CritiquePoint(
                category="brand_voice",
                severity=CritiqueLevel.MODERATE,
                description="Informal language in professional content",
                suggestion="Replace informal words with professional alternatives",
                confidence=0.8
            ))
        elif brand_voice == "casual" and has_formal:
            critiques.append(CritiquePoint(
                category="brand_voice",
                severity=CritiqueLevel.MINOR,
                description="Formal language in casual content",
                suggestion="Use more conversational language",
                confidence=0.6
            ))
        
        return critiques

def demonstrate_agentic_critique():
    """Demonstrate the agentic critique loop"""
    
    print("🔄 Agentic Critique Loop Demo")
    print("=" * 60)
    
    # Test content
    test_content = """
    this is a test content. it has some issues. the sentences are short. 
    there are no questions. it needs improvement for seo. the content is 
    too short for a blog post.
    """
    
    print(f"\n📝 Original Content: {test_content[:100]}...")
    print("-" * 40)
    
    # Test critique loop
    critique_loop = AgenticCritiqueLoop(max_iterations=2, min_quality_score=0.7)
    
    result = critique_loop.critique_and_improve(
        content=test_content,
        content_type="blog",
        brand_voice="professional"
    )
    
    print(f"\n📊 Results:")
    print(f"   ✅ Iterations: {result['iterations']}")
    print(f"   📈 Initial score: {result['improvement_summary']['initial_score']:.2f}")
    print(f"   📈 Final score: {result['improvement_summary']['final_score']:.2f}")
    print(f"   📈 Improvement: {result['improvement_summary']['score_improvement']:.2f}")
    print(f"   🔧 Major issues fixed: {result['improvement_summary']['major_issues_fixed']}")
    
    print(f"\n📝 Improved Content: {result['improved_content'][:200]}...")
    
    print(f"\n📊 Quality Metrics:")
    metrics = result['quality_metrics']
    print(f"   📊 Overall score: {metrics['overall_score']:.2f}")
    print(f"   🔍 Total issues: {metrics['total_issues']}")
    print(f"   ⚠️ Critical issues: {metrics['critical_issues']}")
    print(f"   🔴 Major issues: {metrics['major_issues']}")
    
    print("\n" + "=" * 60)
    print("\n🎯 Agentic Critique Benefits:")
    print("   ✅ Iterative content improvement")
    print("   ✅ Multiple specialized critique agents")
    print("   ✅ Quality scoring and threshold management")
    print("   ✅ Automatic improvement application")
    print("   ✅ Comprehensive quality metrics")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented an agentic critique loop for content improvement'")
    print("   🎯 'Multiple specialized agents critique different aspects'")
    print("   🎯 'Iterative refinement until quality thresholds are met'")
    print("   🎯 'Automatic improvement suggestions and application'")
    print("   🎯 'Comprehensive quality metrics and tracking'")

if __name__ == "__main__":
    demonstrate_agentic_critique()
