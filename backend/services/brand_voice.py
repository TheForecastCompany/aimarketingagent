#!/usr/bin/env python3
"""
Brand Voice Engine - Manages brand voice personalities and styles
Provides consistent tone and style across generated content
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

class BrandVoice(Enum):
    """Predefined brand voice types"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PLAYFUL = "playful"
    AUTHORITATIVE = "authoritative"
    EMPATHETIC = "empathetic"

@dataclass
class BrandVoiceProfile:
    """Brand voice configuration"""
    name: str
    description: str
    tone_attributes: List[str]
    style_guidelines: List[str]
    vocabulary_preferences: List[str]
    avoid_words: List[str]
    sentence_structure: str
    formality_level: int  # 1-10 scale
    
    def to_prompt_extension(self) -> str:
        """Convert brand voice profile to prompt extension string"""
        extension = f"""
Brand Voice: {self.name}
Description: {self.description}
Tone: {', '.join(self.tone_attributes)}
Style Guidelines: {'; '.join(self.style_guidelines)}
Vocabulary: {', '.join(self.vocabulary_preferences)}
Avoid: {', '.join(self.avoid_words)}
Sentence Structure: {self.sentence_structure}
Formality Level: {self.formality_level}/10
        """.strip()
        return extension

class BrandVoiceEngine:
    """Engine for applying brand voice to content"""
    
    def __init__(self):
        self.profiles = self._initialize_profiles()
        print("🎯 Brand Voice Engine Initialized")
        print(f"📊 Available voices: {len(self.profiles)}")
    
    def _initialize_profiles(self) -> Dict[BrandVoice, BrandVoiceProfile]:
        """Initialize predefined brand voice profiles"""
        return {
            BrandVoice.PROFESSIONAL: BrandVoiceProfile(
                name="Professional",
                description="Formal, authoritative, and trustworthy",
                tone_attributes=["authoritative", "trustworthy", "formal", "precise"],
                style_guidelines=[
                    "Use complete sentences",
                    "Avoid slang and contractions",
                    "Maintain formal structure",
                    "Use industry-appropriate terminology"
                ],
                vocabulary_preferences=["utilize", "implement", "strategic", "optimize"],
                avoid_words=["gonna", "wanna", "cool", "awesome"],
                sentence_structure="complex",
                formality_level=8
            ),
            
            BrandVoice.CASUAL: BrandVoiceProfile(
                name="Casual",
                description="Relaxed, friendly, and approachable",
                tone_attributes=["friendly", "approachable", "relaxed", "conversational"],
                style_guidelines=[
                    "Use contractions naturally",
                    "Include conversational elements",
                    "Keep sentences shorter",
                    "Use relatable examples"
                ],
                vocabulary_preferences=["awesome", "cool", "great", "helpful"],
                avoid_words=["utilize", "implement", "leverage", "synergy"],
                sentence_structure="simple",
                formality_level=3
            ),
            
            BrandVoice.PLAYFUL: BrandVoiceProfile(
                name="Playful",
                description="Fun, lighthearted, and engaging",
                tone_attributes=["fun", "lighthearted", "engaging", "creative"],
                style_guidelines=[
                    "Use playful language",
                    "Include humor when appropriate",
                    "Keep tone upbeat",
                    "Use creative expressions"
                ],
                vocabulary_preferences=["awesome", "fantastic", "exciting", "amazing"],
                avoid_words=["boring", "dull", "serious", "formal"],
                sentence_structure="varied",
                formality_level=3
            ),
            
            BrandVoice.AUTHORITATIVE: BrandVoiceProfile(
                name="Authoritative",
                description="Expert, confident, and commanding",
                tone_attributes=["expert", "confident", "commanding", "decisive"],
                style_guidelines=[
                    "Use expert terminology",
                    "Make confident statements",
                    "Provide clear direction",
                    "Back up claims with evidence"
                ],
                vocabulary_preferences=["expert", "proven", "validated", "authoritative"],
                avoid_words=["maybe", "perhaps", "uncertain", "possibly"],
                sentence_structure="declarative",
                formality_level=7
            ),
            
            BrandVoice.EMPATHETIC: BrandVoiceProfile(
                name="Empathetic",
                description="Understanding, caring, and supportive",
                tone_attributes=["understanding", "caring", "supportive", "compassionate"],
                style_guidelines=[
                    "Use warm, inclusive language",
                    "Acknowledge user feelings",
                    "Provide supportive guidance",
                    "Show understanding of challenges"
                ],
                vocabulary_preferences=["understand", "support", "care", "compassion"],
                avoid_words=["ignore", "dismiss", "invalid", "wrong"],
                sentence_structure="gentle",
                formality_level=4
            )
        }
    
    def get_profile(self, voice: BrandVoice) -> BrandVoiceProfile:
        """Get brand voice profile"""
        return self.profiles.get(voice, self.profiles[BrandVoice.PROFESSIONAL])
    
    def apply_brand_voice(self, content: str, voice: BrandVoice) -> str:
        """Apply brand voice to content"""
        profile = self.get_profile(voice)
        
        # This is a simplified implementation
        # In a real system, you'd use NLP to transform the content
        
        # Replace vocabulary
        for word in profile.vocabulary_preferences:
            content = content.replace("good", word)
            content = content.replace("nice", word)
        
        # Remove avoided words
        for word in profile.avoid_words:
            content = content.replace(word, "")
        
        # Adjust formality
        if profile.formality_level > 6:
            # Make more formal
            content = content.replace("can't", "cannot")
            content = content.replace("won't", "will not")
        elif profile.formality_level < 4:
            # Make more casual
            content = content.replace("cannot", "can't")
            content = content.replace("will not", "won't")
        
        return content
    
    def get_style_guide(self, voice: BrandVoice) -> List[str]:
        """Get style guidelines for a brand voice"""
        profile = self.get_profile(voice)
        return profile.style_guidelines
    
    def validate_content(self, content: str, voice: BrandVoice) -> Dict[str, Any]:
        """Validate content against brand voice guidelines"""
        profile = self.get_profile(voice)
        
        validation_result = {
            "compliance_score": 0.0,
            "issues": [],
            "suggestions": []
        }
        
        # Check for avoided words
        for word in profile.avoid_words:
            if word.lower() in content.lower():
                validation_result["issues"].append(f"Contains avoided word: {word}")
                validation_result["suggestions"].append(f"Replace '{word}' with alternative")
        
        # Check vocabulary preferences
        word_count = len(content.split())
        preferred_count = sum(1 for word in profile.vocabulary_preferences if word.lower() in content.lower())
        
        if word_count > 0:
            vocabulary_score = preferred_count / word_count
            validation_result["compliance_score"] = vocabulary_score
        
        return validation_result

def demonstrate_brand_voice():
    """Demonstrate brand voice engine"""
    
    engine = BrandVoiceEngine()
    
    test_content = "This is a good product that can help people achieve their goals."
    
    print("🎯 Brand Voice Engine Demo")
    print("=" * 60)
    
    print(f"\n📝 Original Content: {test_content}")
    print("-" * 40)
    
    for voice in BrandVoice:
        print(f"\n🔊 {voice.value.title()} Voice:")
        
        # Get profile
        profile = engine.get_profile(voice)
        print(f"   Description: {profile.description}")
        print(f"   Tone: {', '.join(profile.tone_attributes[:3])}")
        
        # Apply brand voice
        transformed = engine.apply_brand_voice(test_content, voice)
        print(f"   Transformed: {transformed}")
        
        # Validate
        validation = engine.validate_content(transformed, voice)
        print(f"   Compliance: {validation['compliance_score']:.2f}")
        
        if validation['issues']:
            print(f"   Issues: {', '.join(validation['issues'])}")
    
    print("\n" + "=" * 60)
    print("\n🎯 Brand Voice Benefits:")
    print("   ✅ Consistent tone across all content")
    print("   ✅ Tailored messaging for different audiences")
    print("   ✅ Brand identity reinforcement")
    print("   ✅ Content validation and quality control")
    print("   ✅ Flexible voice switching")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented a comprehensive brand voice system'")
    print("   🎯 'Multiple predefined voices for different contexts'")
    print("   🎯 'Content transformation and validation'")
    print("   🎯 'Vocabulary and tone management'")
    print("   🎯 'Quality control and compliance scoring'")

if __name__ == "__main__":
    demonstrate_brand_voice()
