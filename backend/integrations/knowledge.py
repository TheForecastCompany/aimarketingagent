#!/usr/bin/env python3
"""
Knowledge Retrieval System - Enhances content with external knowledge
Provides context-aware information retrieval and integration
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import re

@dataclass
class KnowledgeItem:
    """Individual knowledge item"""
    content: str
    source: str
    relevance_score: float
    category: str
    timestamp: str

@dataclass
class RetrievalResult:
    """Result of knowledge retrieval"""
    items: List[KnowledgeItem]
    query: str
    total_items: int
    processing_time: float

class KnowledgeRetriever:
    """Retrieves and manages knowledge for content enhancement"""
    
    def __init__(self):
        self.knowledge_base = self._initialize_knowledge_base()
        self.retrieval_cache = {}
        print("🧠 Knowledge Retriever Initialized")
        print(f"📚 Knowledge base size: {len(self.knowledge_base)} items")
    
    def _initialize_knowledge_base(self) -> Dict[str, List[KnowledgeItem]]:
        """Initialize knowledge base with sample data"""
        knowledge_base = {
            "technology": [
                KnowledgeItem(
                    content="Artificial Intelligence is transforming industries through automation and intelligent decision-making",
                    source="Tech Trends 2024",
                    relevance_score=0.9,
                    category="AI",
                    timestamp="2024-01-01"
                ),
                KnowledgeItem(
                    content="Machine Learning algorithms can process vast amounts of data to identify patterns and make predictions",
                    source="ML Handbook",
                    relevance_score=0.85,
                    category="ML",
                    timestamp="2024-01-02"
                ),
                KnowledgeItem(
                    content="Cloud computing enables scalable infrastructure and reduces operational costs",
                    source="Cloud Guide",
                    relevance_score=0.8,
                    category="Cloud",
                    timestamp="2024-01-03"
                )
            ],
            "business": [
                KnowledgeItem(
                    content="Digital transformation is essential for business competitiveness in the modern economy",
                    source="Business Strategy",
                    relevance_score=0.9,
                    category="Strategy",
                    timestamp="2024-01-01"
                ),
                KnowledgeItem(
                    content="Customer experience optimization leads to increased loyalty and revenue",
                    source="CX Insights",
                    relevance_score=0.85,
                    category="Customer Experience",
                    timestamp="2024-01-02"
                ),
                KnowledgeItem(
                    content="Data-driven decision making improves business outcomes and reduces risks",
                    source="Analytics Guide",
                    relevance_score=0.8,
                    category="Analytics",
                    timestamp="2024-01-03"
                )
            ],
            "marketing": [
                KnowledgeItem(
                    content="Content marketing builds brand authority and drives organic traffic",
                    source="Marketing Playbook",
                    relevance_score=0.9,
                    category="Content Marketing",
                    timestamp="2024-01-01"
                ),
                KnowledgeItem(
                    content="Social media engagement requires authentic communication and consistent value delivery",
                    source="Social Media Guide",
                    relevance_score=0.85,
                    category="Social Media",
                    timestamp="2024-01-02"
                ),
                KnowledgeItem(
                    content="SEO optimization involves technical excellence, quality content, and user experience",
                    source="SEO Handbook",
                    relevance_score=0.8,
                    category="SEO",
                    timestamp="2024-01-03"
                )
            ],
            "general": [
                KnowledgeItem(
                    content="Continuous learning and adaptation are key to personal and professional growth",
                    source="Self Development",
                    relevance_score=0.8,
                    category="Personal Growth",
                    timestamp="2024-01-01"
                ),
                KnowledgeItem(
                    content="Effective communication requires clarity, empathy, and active listening",
                    source="Communication Skills",
                    relevance_score=0.85,
                    category="Communication",
                    timestamp="2024-01-02"
                ),
                KnowledgeItem(
                    content="Innovation thrives in environments that encourage creativity and calculated risk-taking",
                    source="Innovation Culture",
                    relevance_score=0.8,
                    category="Innovation",
                    timestamp="2024-01-03"
                )
            ]
        }
        
        return knowledge_base
    
    def retrieve_knowledge(self, query: str, topics: List[str], max_items: int = 5) -> RetrievalResult:
        """Retrieve relevant knowledge based on query and topics"""
        import time
        start_time = time.time()
        
        print(f"🔍 Retrieving knowledge for: {query}")
        print(f"📚 Topics: {topics}")
        
        # Check cache first
        cache_key = f"{query}_{','.join(sorted(topics))}_{max_items}"
        if cache_key in self.retrieval_cache:
            print("📋 Using cached results")
            return self.retrieval_cache[cache_key]
        
        # Retrieve relevant items
        relevant_items = []
        
        # Search in topic-specific knowledge
        for topic in topics:
            if topic in self.knowledge_base:
                topic_items = self.knowledge_base[topic]
                for item in topic_items:
                    relevance = self._calculate_relevance(query, item.content)
                    if relevance > 0.3:  # Minimum relevance threshold
                        relevant_items.append(item)
        
        # Search in general knowledge if needed
        if len(relevant_items) < max_items:
            general_items = self.knowledge_base.get("general", [])
            for item in general_items:
                relevance = self._calculate_relevance(query, item.content)
                if relevance > 0.3:
                    relevant_items.append(item)
        
        # Sort by relevance and limit results
        relevant_items.sort(key=lambda x: x.relevance_score, reverse=True)
        relevant_items = relevant_items[:max_items]
        
        # Update relevance scores based on query match
        for item in relevant_items:
            item.relevance_score = self._calculate_relevance(query, item.content)
        
        # Sort again by updated relevance
        relevant_items.sort(key=lambda x: x.relevance_score, reverse=True)
        
        processing_time = time.time() - start_time
        
        result = RetrievalResult(
            items=relevant_items,
            query=query,
            total_items=len(relevant_items),
            processing_time=processing_time
        )
        
        # Cache result
        self.retrieval_cache[cache_key] = result
        
        print(f"✅ Retrieved {len(relevant_items)} items in {processing_time:.3f}s")
        
        return result
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score between query and content"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        # Simple word overlap calculation
        overlap = len(query_words.intersection(content_words))
        total_words = len(query_words.union(content_words))
        
        if total_words == 0:
            return 0.0
        
        base_relevance = overlap / total_words
        
        # Boost for exact phrase matches
        if query.lower() in content.lower():
            base_relevance += 0.3
        
        # Boost for partial matches
        for word in query_words:
            if word in content.lower():
                base_relevance += 0.1
        
        return min(base_relevance, 1.0)
    
    def enhance_content(self, content: str, topics: List[str], max_enhancements: int = 3) -> Dict[str, Any]:
        """Enhance content with relevant knowledge"""
        print(f"🚀 Enhancing content with knowledge...")
        
        # Create query from content
        query = self._extract_key_terms(content)
        
        # Retrieve relevant knowledge
        retrieval_result = self.retrieve_knowledge(query, topics, max_enhancements * 2)
        
        # Select best enhancements
        enhancements = []
        for item in retrieval_result.items[:max_enhancements]:
            enhancement = {
                "knowledge": item.content,
                "source": item.source,
                "category": item.category,
                "relevance": item.relevance_score,
                "integration_point": self._find_integration_point(content, item.content)
            }
            enhancements.append(enhancement)
        
        # Create enhanced content
        enhanced_content = self._create_enhanced_content(content, enhancements)
        
        return {
            "original_content": content,
            "enhanced_content": enhanced_content,
            "enhancements": enhancements,
            "retrieval_stats": {
                "items_found": retrieval_result.total_items,
                "processing_time": retrieval_result.processing_time,
                "topics_searched": topics
            }
        }
    
    def _extract_key_terms(self, content: str) -> str:
        """Extract key terms from content"""
        # Simple keyword extraction
        words = content.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just'}
        
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return top terms
        return ' '.join(key_terms[:5])
    
    def _find_integration_point(self, content: str, knowledge: str) -> str:
        """Find best integration point for knowledge"""
        # Simple integration point detection
        content_lower = content.lower()
        knowledge_lower = knowledge.lower()
        
        # Look for common themes
        integration_points = []
        
        if "ai" in content_lower and "ai" in knowledge_lower:
            integration_points.append("AI discussion")
        
        if "business" in content_lower and "business" in knowledge_lower:
            integration_points.append("business context")
        
        if "technology" in content_lower and "technology" in knowledge_lower:
            integration_points.append("technology focus")
        
        if integration_points:
            return integration_points[0]
        
        return "general enhancement"
    
    def _create_enhanced_content(self, content: str, enhancements: List[Dict]) -> str:
        """Create enhanced content with knowledge integration"""
        enhanced = content
        
        # Add knowledge as contextual enhancements
        for enhancement in enhancements:
            knowledge = enhancement["knowledge"]
            integration_point = enhancement["integration_point"]
            
            # Add knowledge as a contextual note
            enhanced += f"\n\n💡 **Additional Insight**: {knowledge}\n*Source: {enhancement['source']}*"
        
        return enhanced
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of knowledge base"""
        summary = {
            "total_categories": len(self.knowledge_base),
            "total_items": sum(len(items) for items in self.knowledge_base.values()),
            "categories": {}
        }
        
        for category, items in self.knowledge_base.items():
            summary["categories"][category] = {
                "item_count": len(items),
                "categories": list(set(item.category for item in items))
            }
        
        return summary

def demonstrate_knowledge_retrieval():
    """Demonstrate knowledge retrieval system"""
    
    print("🧠 Knowledge Retrieval Demo")
    print("=" * 60)
    
    # Initialize retriever
    retriever = KnowledgeRetriever()
    
    # Show knowledge base summary
    summary = retriever.get_knowledge_summary()
    print(f"\n📚 Knowledge Base Summary:")
    print(f"   📂 Categories: {summary['total_categories']}")
    print(f"   📄 Total Items: {summary['total_items']}")
    
    # Test knowledge retrieval
    query = "artificial intelligence business impact"
    topics = ["technology", "business"]
    
    print(f"\n🔍 Testing Knowledge Retrieval:")
    print(f"   Query: {query}")
    print(f"   Topics: {topics}")
    print("-" * 40)
    
    result = retriever.retrieve_knowledge(query, topics, max_items=3)
    
    print(f"\n📊 Retrieval Results:")
    print(f"   📄 Items found: {result.total_items}")
    print(f"   ⏱️ Processing time: {result.processing_time:.3f}s")
    
    for i, item in enumerate(result.items, 1):
        print(f"\n   {i}. {item.content[:80]}...")
        print(f"      📂 Category: {item.category}")
        print(f"      📊 Relevance: {item.relevance_score:.2f}")
        print(f"      📚 Source: {item.source}")
    
    # Test content enhancement
    test_content = "AI is transforming how businesses operate and make decisions."
    
    print(f"\n🚀 Testing Content Enhancement:")
    print(f"   Original: {test_content}")
    print("-" * 40)
    
    enhancement_result = retriever.enhance_content(test_content, topics, max_enhancements=2)
    
    print(f"\n✨ Enhanced Content:")
    print(f"   {enhancement_result['enhanced_content'][:200]}...")
    
    print(f"\n📊 Enhancement Stats:")
    stats = enhancement_result['retrieval_stats']
    print(f"   📄 Items found: {stats['items_found']}")
    print(f"   ⏱️ Processing time: {stats['processing_time']:.3f}s")
    
    print("\n" + "=" * 60)
    print("\n🧠 Knowledge Retrieval Benefits:")
    print("   ✅ Context-aware information retrieval")
    print("   ✅ Content enhancement with relevant knowledge")
    print("   ✅ Intelligent integration point detection")
    print("   ✅ Relevance scoring and ranking")
    print("   ✅ Cached results for performance")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented a knowledge retrieval system for content enhancement'")
    print("   🎯 'Context-aware retrieval based on content analysis'")
    print("   🎯 'Relevance scoring and intelligent integration'")
    print("   🎯 'Cached retrieval for improved performance'")
    print("   🎯 'Multi-category knowledge base with structured data'")

if __name__ == "__main__":
    demonstrate_knowledge_retrieval()
