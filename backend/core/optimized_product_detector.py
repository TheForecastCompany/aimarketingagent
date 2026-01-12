"""
Optimized Product Detection Agent with Phonetic Matching and Contextual Validation
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import Levenshtein  # You may need to install: pip install python-Levenshtein

@dataclass
class ProductDetection:
    """Structured product detection result"""
    detected_term: str
    mapped_product: str
    intent: str  # "active_use", "comparison", "historical_reference", "casual_mention"
    confidence: float  # 0-100
    speech_clarity_score: float  # 0-100
    brand: Optional[str] = None
    model: Optional[str] = None

class OptimizedProductDetector:
    """Advanced product detection with phonetic matching and contextual analysis"""
    
    def __init__(self, product_catalog: Dict[str, Dict]):
        """
        Initialize with product catalog
        
        Args:
            product_catalog: Dict mapping product names to metadata
                {
                    "Sony WH-1000XM4": {
                        "brand": "Sony",
                        "model": "WH-1000XM4",
                        "keywords": ["sony", "wh1000xm4", "xm4", "headphones"],
                        "phonetic_variants": ["sen high zer", "sony wh", "wh thousand"]
                    }
                }
        """
        self.product_catalog = product_catalog
        self.build_phonetic_index()
        
    def build_phonetic_index(self):
        """Build phonetic matching index for all products"""
        self.phonetic_index = {}
        
        for product_name, metadata in self.product_catalog.items():
            # Add exact name
            self.phonetic_index[product_name.lower()] = product_name
            
            # Add brand and model separately
            if metadata.get('brand'):
                self.phonetic_index[metadata['brand'].lower()] = product_name
            if metadata.get('model'):
                self.phonetic_index[metadata['model'].lower()] = product_name
                
            # Add phonetic variants
            for variant in metadata.get('phonetic_variants', []):
                self.phonetic_index[variant.lower()] = product_name
                
            # Add keywords
            for keyword in metadata.get('keywords', []):
                self.phonetic_index[keyword.lower()] = product_name
    
    def calculate_levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            s1, s2 = s2, s1
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
    
    def find_phonetic_matches(self, term: str, max_distance: int = 2) -> List[Tuple[str, int]]:
        """Find phonetically similar matches using Levenshtein distance"""
        term_lower = term.lower()
        matches = []
        
        for catalog_term, product_name in self.phonetic_index.items():
            distance = self.calculate_levenshtein_distance(term_lower, catalog_term)
            if distance <= max_distance:
                matches.append((product_name, distance))
        
        # Sort by distance (best match first)
        matches.sort(key=lambda x: x[1])
        return matches
    
    def analyze_contextual_intent(self, transcript: str, product_term: str) -> str:
        """
        Analyze context to determine intent behind product mention
        
        Returns:
            intent: "active_use", "comparison", "historical_reference", "casual_mention"
        """
        # Find sentences containing the product
        sentences = re.split(r'[.!?]+', transcript)
        relevant_sentences = [s.strip() for s in sentences if product_term.lower() in s.lower()]
        
        if not relevant_sentences:
            return "casual_mention"
        
        # Analyze verbs and pronouns around product mentions
        active_use_indicators = [
            "i'm using", "i am using", "currently using", "have", "got", "bought",
            "holding", "testing", "trying", "working with", "playing with"
        ]
        
        comparison_indicators = [
            "versus", "vs", "compared to", "better than", "instead of", "alternative to",
            "between", "among", "choose between"
        ]
        
        historical_indicators = [
            "used to", "had", "owned", "previously", "in the past", "before", "my old"
        ]
        
        for sentence in relevant_sentences:
            sentence_lower = sentence.lower()
            
            # Check for active use
            for indicator in active_use_indicators:
                if indicator in sentence_lower:
                    return "active_use"
            
            # Check for comparison
            for indicator in comparison_indicators:
                if indicator in sentence_lower:
                    return "comparison"
            
            # Check for historical reference
            for indicator in historical_indicators:
                if indicator in sentence_lower:
                    return "historical_reference"
        
        return "casual_mention"
    
    def calculate_speech_clarity_score(self, transcript: str) -> float:
        """
        Calculate speech clarity score based on transcript quality
        """
        score = 100.0
        
        # Penalize fragmented sentences
        sentences = re.split(r'[.!?]+', transcript)
        short_sentences = sum(1 for s in sentences if len(s.strip().split()) < 3)
        if short_sentences > len(sentences) * 0.5:
            score -= 20
        
        # Penalize grammatical issues
        if re.search(r'\b(um|uh|like|you know|kinda|sorta)\b', transcript.lower()):
            score -= 15
        
        # Penalize repeated words
        words = transcript.lower().split()
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        repetitions = sum(1 for count in word_counts.values() if count > 3)
        if repetitions > len(words) * 0.1:
            score -= 10
        
        # Penalize nonsensical phrases
        nonsensical_patterns = [
            r'\b(the thing|that thing)\b',
            r'\b(stuff|whatever|thingy)\b'
        ]
        for pattern in nonsensical_patterns:
            if re.search(pattern, transcript.lower()):
                score -= 15
        
        return max(0, min(100, score))
    
    def extract_brand_model_hierarchy(self, term: str, mapped_product: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract brand and model from detected term
        Returns (brand, model) tuple
        """
        product_metadata = self.product_catalog.get(mapped_product, {})
        
        # If catalog has explicit brand/model
        if product_metadata.get('brand') and product_metadata.get('model'):
            return product_metadata['brand'], product_metadata['model']
        
        # Try to extract from term itself
        # Look for common brand patterns
        brand_patterns = [
            r'\b(Apple|Sony|Samsung|Bose|Sennheiser|JBL|Apple|Microsoft|Google|Amazon)\b',
            r'\b(Mac|iPhone|iPad|Galaxy|Echo|Alexa|Surface|Pixel)\b'
        ]
        
        detected_brand = None
        for pattern in brand_patterns:
            match = re.search(pattern, term, re.IGNORECASE)
            if match:
                detected_brand = match.group(1) if match.groups() else match.group(0)
                break
        
        # Extract model (everything after brand)
        model = None
        if detected_brand:
            model_pattern = f"{re.escape(detected_brand)}\\s+(.+)"
            model_match = re.search(model_pattern, term, re.IGNORECASE)
            if model_match:
                model = model_match.group(1).strip()
        
        return detected_brand, model
    
    def detect_product(self, transcript: str) -> ProductDetection:
        """
        Main product detection method with optimized logic
        """
        # Calculate speech clarity score
        speech_clarity = self.calculate_speech_clarity_score(transcript)
        
        # Extract potential product terms
        words = re.findall(r'\\b\\w+\\b', transcript.lower())
        
        best_match = None
        best_confidence = 0
        
        for word in words:
            # Try exact match first
            if word in self.phonetic_index:
                mapped_product = self.phonetic_index[word]
                confidence = 95.0  # High confidence for exact match
            else:
                # Try phonetic matching
                phonetic_matches = self.find_phonetic_matches(word, max_distance=2)
                if phonetic_matches:
                    mapped_product, distance = phonetic_matches[0]
                    # Confidence decreases with distance
                    confidence = max(50, 95 - (distance * 15))
                else:
                    continue
            
            # Analyze contextual intent
            intent = self.analyze_contextual_intent(transcript, word)
            
            # Adjust confidence based on intent
            if intent == "active_use":
                confidence += 10
            elif intent == "comparison":
                confidence += 5
            elif intent == "casual_mention":
                confidence -= 20
            
            # Adjust confidence based on speech clarity
            confidence *= (speech_clarity / 100)
            
            if confidence > best_confidence:
                brand, model = self.extract_brand_model_hierarchy(word, mapped_product)
                best_match = ProductDetection(
                    detected_term=word,
                    mapped_product=mapped_product,
                    intent=intent,
                    confidence=min(100, confidence),
                    speech_clarity_score=speech_clarity,
                    brand=brand,
                    model=model
                )
                best_confidence = confidence
        
        # Fallback if no matches found
        if not best_match:
            return ProductDetection(
                detected_term="",
                mapped_product="Unknown",
                intent="no_detection",
                confidence=0.0,
                speech_clarity_score=speech_clarity
            )
        
        return best_match

# Example Product Catalog
SAMPLE_PRODUCT_CATALOG = {
    "Sony WH-1000XM4": {
        "brand": "Sony",
        "model": "WH-1000XM4",
        "keywords": ["sony", "wh1000xm4", "xm4", "headphones", "wh-1000"],
        "phonetic_variants": ["sen high zer", "sony wh", "wh thousand", "double you ex em four"]
    },
    "Apple MacBook Pro": {
        "brand": "Apple", 
        "model": "MacBook Pro",
        "keywords": ["apple", "macbook", "mac", "macbook pro", "laptop"],
        "phonetic_variants": ["mac book pro", "mac book", "mack book"]
    },
    "Sennheiser HD 660S": {
        "brand": "Sennheiser",
        "model": "HD 660S", 
        "keywords": ["sennheiser", "hd660s", "hd 660s", "headphones"],
        "phonetic_variants": ["sen high zer", "sen heiser", "h d six sixty s"]
    },
    "Bose QuietComfort 45": {
        "brand": "Bose",
        "model": "QuietComfort 45",
        "keywords": ["bose", "quietcomfort", "qc45", "headphones"],
        "phonetic_variants": ["boz", "quiet comfort", "q c forty five"]
    }
}

# Few-shot examples for handling common phonetic misspellings
FEW_SHOT_EXAMPLES = {
    "phonetic_misspellings": [
        {
            "transcript": "I'm testing these new Sen High Zer headphones",
            "expected_detection": {
                "detected_term": "Sen High Zer",
                "mapped_product": "Sennheiser HD 660S",
                "intent": "active_use",
                "confidence": 75,
                "speech_clarity_score": 85,
                "brand": "Sennheiser",
                "model": "HD 660S"
            }
        },
        {
            "transcript": "The Sony WH sounds amazing compared to my old Bose",
            "expected_detection": {
                "detected_term": "Sony WH",
                "mapped_product": "Sony WH-1000XM4", 
                "intent": "comparison",
                "confidence": 80,
                "speech_clarity_score": 90,
                "brand": "Sony",
                "model": "WH-1000XM4"
            }
        },
        {
            "transcript": "I used to have a Mac Book Pro but now I have a regular laptop",
            "expected_detection": {
                "detected_term": "Mac Book Pro",
                "mapped_product": "Apple MacBook Pro",
                "intent": "historical_reference", 
                "confidence": 85,
                "speech_clarity_score": 95,
                "brand": "Apple",
                "model": "MacBook Pro"
            }
        },
        {
            "transcript": "Just got this thing from Amazon, it's pretty good",
            "expected_detection": {
                "detected_term": "thing",
                "mapped_product": "Unknown",
                "intent": "casual_mention",
                "confidence": 25,
                "speech_clarity_score": 70,
                "brand": None,
                "model": None
            }
        }
    ]
}

# System Instructions for the Agent
SYSTEM_INSTRUCTIONS = """
You are an advanced Product Detection Agent with phonetic matching capabilities.

CORE PRINCIPLES:
1. Phonetic & Fuzzy Matching:
   - Account for transcription errors and phonetic similarity
   - Use Levenshtein distance (max 2) for fuzzy matching
   - Prioritize exact matches, then phonetic variants
   - Common misspellings: "Sen High Zer" → "Sennheiser", "Mac Book" → "MacBook"

2. Contextual Intent Validation:
   - Active Use: "I'm using", "currently have", "holding", "testing"
   - Comparison: "versus", "vs", "better than", "instead of"  
   - Historical: "used to have", "had", "previously owned"
   - Casual: vague mentions without clear ownership context

3. Brand-Model Hierarchy:
   - Always return most granular SKU available
   - "MacBook Pro" → "Apple MacBook Pro" (not just "Apple")
   - "WH-1000XM4" → "Sony WH-1000XM4" (not just "Sony")

4. Confidence Scoring:
   - Base: 95% for exact matches, decreases with phonetic distance
   - Intent bonus: +10% active use, +5% comparison, -20% casual
   - Speech clarity multiplier: adjust based on transcript quality
   - Fragmented speech = lower confidence

5. JSON Output Structure:
   {
     "detected_term": "exact string from transcript",
     "mapped_product": "catalog product name", 
     "intent": "active_use|comparison|historical_reference|casual_mention",
     "confidence": 0-100,
     "speech_clarity_score": 0-100,
     "brand": "brand_name",
     "model": "model_name"
   }

HANDLING EDGE CASES:
- Multiple products in one sentence → detect comparison intent
- Fragmented transcript → lower speech_clarity_score
- Generic terms ("thing", "stuff") → mark as casual_mention
- Brand only → find most specific model match
- Phonetic distance > 2 → no match, return Unknown

Always provide structured JSON response with all fields populated.
"""

if __name__ == "__main__":
    # Initialize detector with sample catalog
    detector = OptimizedProductDetector(SAMPLE_PRODUCT_CATALOG)
    
    # Test few-shot examples
    for example in FEW_SHOT_EXAMPLES["phonetic_misspellings"]:
        transcript = example["transcript"]
        expected = example["expected_detection"]
        
        print(f"\\n{'='*60}")
        print(f"Transcript: {transcript}")
        
        detection = detector.detect_product(transcript)
        
        print(f"\\nDetection Result:")
        print(f"  Detected Term: {detection.detected_term}")
        print(f"  Mapped Product: {detection.mapped_product}")
        print(f"  Intent: {detection.intent}")
        print(f"  Confidence: {detection.confidence}%")
        print(f"  Speech Clarity: {detection.speech_clarity_score}%")
        print(f"  Brand: {detection.brand}")
        print(f"  Model: {detection.model}")
        
        # Verify against expected
        if (detection.detected_term.lower() == expected["detected_term"].lower() and
            detection.mapped_product == expected["mapped_product"] and
            detection.intent == expected["intent"]):
            print("✅ PASS: Matches expected detection")
        else:
            print("❌ FAIL: Does not match expected")
            print(f"Expected: {expected}")
