#!/usr/bin/env python3
"""
Enhanced Transcript Extractor - Professional transcription with fallback
Uses AssemblyAI as primary, YouTube API as fallback
"""

import os
from typing import Dict, Any, Optional
from backend.integrations.transcription import TranscriptExtractor
from backend.integrations.transcription_pro import ProfessionalTranscriptionService

class EnhancedTranscriptExtractor:
    """Enhanced transcript extractor with professional transcription fallback"""
    
    def __init__(self, use_professional: bool = True, use_ollama: bool = False):
        self.use_professional = use_professional
        self.use_ollama = use_ollama
        self.fallback_extractor = TranscriptExtractor()
        
        # Initialize professional service if API key is available
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if api_key and use_professional:
            try:
                self.professional_service = ProfessionalTranscriptionService.from_environment()
                print("🎙️ Enhanced Transcript Extractor Initialized")
                print("📊 Primary: AssemblyAI (professional)")
                print("🔄 Fallback: YouTube API (when needed)")
            except ValueError as e:
                print(f"⚠️ Professional transcription unavailable: {e}")
                self.professional_service = None
                if use_ollama:
                    print("🦙 Ollama Enhanced Transcript Extractor Initialized")
                    print("📊 Using: YouTube API only (AssemblyAI unavailable)")
                else:
                    print("📹 Enhanced Transcript Extractor Initialized")
                    print("📊 Using: YouTube API only (AssemblyAI unavailable)")
        else:
            self.professional_service = None
            if use_ollama:
                print("🦙 Ollama Enhanced Transcript Extractor Initialized")
                print("📊 Primary: AssemblyAI (professional)")
                print("🔄 Fallback: YouTube API (when needed)")
            else:
                print("📹 Enhanced Transcript Extractor Initialized")
                print("📊 Using: YouTube API only")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL (including playlists)"""
        import re
        
        patterns = [
            # Standard YouTube URLs
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
            # Playlist URLs - extract first video ID
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
                print(f"📹 Extracted video ID: {video_id}")
                return video_id
        
        # If no video ID found but it's a playlist, try to get playlist ID
        playlist_match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
        if playlist_match:
            playlist_id = playlist_match.group(1)
            print(f"📋 Playlist detected: {playlist_id}")
            print("⚠️  Playlist URLs require individual video IDs")
            print("💡 Please provide a direct video URL or specific video from playlist")
        
        return None
    
    def _get_professional_transcript(self, video_url: str) -> Dict[str, Any]:
        """Get transcript using professional transcription service"""
        if not self.professional_service:
            print("🔄 Professional transcription not available, using YouTube API")
            return self._get_youtube_transcript(video_url)
        
        try:
            print(f"🎙️ Using professional transcription service for: {video_url}")
            result = self.professional_service.process_video(video_url)
            
            if result:
                print(f"✅ Professional transcription successful!")
                print(f"📊 Quality: {result.confidence_score:.2f} confidence")
                print(f"👥 Speakers: {len(result.speakers)} detected")
                print(f"⏱️ Processing time: {result.processing_time:.2f}s")
                print(f"🎯 Audio duration: {result.audio_duration:.2f}s")
                
                # Format transcript with speaker labels
                formatted_transcript = self._format_transcript_with_speakers(result)
                
                return {
                    "transcript": formatted_transcript,
                    "transcription_metadata": {
                        "method": "assemblyai",
                        "has_speaker_diarization": True,
                        "confidence_score": result.confidence_score,
                        "processing_time": getattr(result, 'processing_time', 0.0),  # Handle missing attribute
                        "speakers": len(result.speakers),
                        "audio_duration": getattr(result, 'audio_duration', 0.0)  # Handle missing attribute
                    }
                }
            else:
                print("❌ Professional transcription failed, falling back to YouTube API")
                print("🔄 This is likely due to AssemblyAI connectivity issues")
                return self._get_youtube_transcript(video_url)
                
        except Exception as e:
            print(f"❌ Professional transcription error: {type(e).__name__}: {e}")
            print("🔄 Falling back to YouTube API due to AssemblyAI issues")
            return self._get_youtube_transcript(video_url)
    
    def _get_youtube_transcript(self, video_url: str) -> Dict[str, Any]:
        """Get transcript using YouTube API as fallback"""
        try:
            print(f"📹 Using YouTube API fallback for: {video_url}")
            result = self.fallback_extractor.get_transcript_with_metadata(video_url)
            
            if result["transcript"]:
                print(f"✅ YouTube API transcript successful!")
                print(f"📝 Length: {len(result['transcript'])} characters")
                
                return {
                    "transcript": result["transcript"],
                    "transcription_metadata": result["metadata"]
                }
            else:
                print(f"❌ YouTube API also failed")
                return {
                    "transcript": None,
                    "transcription_metadata": {
                        "method": "none",
                        "error": "Both professional and YouTube transcription failed"
                    }
                }
                
        except Exception as e:
            print(f"❌ YouTube API error: {type(e).__name__}: {e}")
            return {
                "transcript": None,
                "transcription_metadata": {
                    "method": "none",
                    "error": f"YouTube API error: {str(e)}"
                }
            }
    
    def _format_transcript_with_speakers(self, result) -> str:
        """Format transcript with speaker labels"""
        try:
            if not result.speakers:
                return result.transcript
            
            formatted_parts = []
            for utterance in result.speakers:
                speaker = utterance.speaker if hasattr(utterance, 'speaker') else f"Speaker {utterance.get('speaker', 'Unknown')}"
                text = utterance.text if hasattr(utterance, 'text') else utterance.get('text', '')
                
                if text:
                    formatted_parts.append(f"{speaker}: {text}")
            
            return ' '.join(formatted_parts)
            
        except Exception as e:
            print(f"⚠️ Error formatting transcript with speakers: {e}")
            return result.transcript
    
    def get_transcript(self, video_url: str) -> Dict[str, Any]:
        """Get transcript using professional service with fallback"""
        try:
            print(f"🎙️ Extracting transcript...")
            print(f"📹 Processing URL: {video_url}")
            
            # Try professional transcription first if enabled
            if self.use_professional and self.professional_service:
                return self._get_professional_transcript(video_url)
            else:
                # Use YouTube API directly
                return self._get_youtube_transcript(video_url)
                
        except Exception as e:
            print(f"❌ Enhanced transcript extractor error: {type(e).__name__}: {e}")
            return {
                "transcript": None,
                "transcription_metadata": {
                    "method": "none",
                    "error": f"Enhanced extractor error: {str(e)}"
                }
            }

def demonstrate_enhanced_extractor():
    """Demonstrate the enhanced transcript extractor"""
    
    # Test with professional transcription
    print("🎙️ Testing Enhanced Extractor with Professional Transcription")
    print("=" * 70)
    
    extractor = EnhancedTranscriptExtractor(use_professional=True)
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"\n📹 Test URL: {test_url}")
    print("-" * 50)
    
    result = extractor.get_transcript(test_url)
    
    if result["transcript"]:
        print(f"✅ SUCCESS: Transcript extracted")
        print(f"📝 Preview: {result['transcript'][:200]}...")
        metadata = result["transcription_metadata"]
        print(f"📊 Method: {metadata['method']}")
        print(f"🎯 Confidence: {metadata.get('confidence_score', 'N/A')}")
        print(f"👥 Speakers: {metadata.get('speakers', 'N/A')}")
        print(f"⏱️ Processing time: {metadata.get('processing_time', 'N/A')}s")
    else:
        print(f"❌ FAILED: {result['transcription_metadata'].get('error', 'Unknown error')}")
    
    # Test with YouTube only
    print("\n\n📹 Testing Enhanced Extractor with YouTube Only")
    print("=" * 70)
    
    extractor_youtube = EnhancedTranscriptExtractor(use_professional=False)
    
    result_youtube = extractor_youtube.get_transcript(test_url)
    
    if result_youtube["transcript"]:
        print(f"✅ SUCCESS: Transcript extracted")
        print(f"📝 Preview: {result_youtube['transcript'][:200]}...")
        metadata = result_youtube["transcription_metadata"]
        print(f"📊 Method: {metadata['method']}")
        print(f"🎯 Confidence: {metadata.get('confidence_score', 'N/A')}")
    else:
        print(f"❌ FAILED: {result_youtube['transcription_metadata'].get('error', 'Unknown error')}")
    
    print("\n" + "=" * 70)
    print("\n🎯 Enhanced Extractor Benefits:")
    print("   ✅ Professional transcription with speaker diarization")
    print("   ✅ Automatic fallback to YouTube API")
    print("   ✅ High confidence scores and quality metrics")
    print("   ✅ Speaker identification and labeling")
    print("   ✅ Robust error handling and logging")
    print("   ✅ Production-ready reliability")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented a hybrid transcription system'")
    print("   🎯 'Primary: AssemblyAI for professional quality'")
    print("   🎯 'Fallback: YouTube API for reliability'")
    print("   🎯 'Speaker diarization for better content analysis'")
    print("   🎯 'Comprehensive metadata for downstream processing'")
    print("   🎯 'Production-grade error handling and monitoring'")

if __name__ == "__main__":
    demonstrate_enhanced_extractor()
