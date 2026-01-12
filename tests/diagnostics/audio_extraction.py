#!/usr/bin/env python3
"""
Diagnostic Script - Identify audio extraction issues
"""

import os
import tempfile
import yt_dlp
from dotenv import load_dotenv

def diagnose_audio_extraction():
    """Diagnose audio extraction issues"""
    
    print("🔍 Audio Extraction Diagnostic")
    print("=" * 60)
    
    # Test URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Simple video
        "https://www.youtube.com/watch?v=FQz2LruhAjI",  # Different video
    ]
    
    # Load API key
    load_dotenv()
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    
    if not api_key:
        print("❌ No AssemblyAI API key found")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-10:]}")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🧪 Test {i}: {url}")
        print("-" * 40)
        
        try:
            # Test with professional transcription service
            from professional_transcription import ProfessionalTranscriptionService
            
            service = ProfessionalTranscriptionService(api_key)
            
            print("🎥 Testing audio extraction...")
            audio_path = service.extract_audio_from_video(url)
            
            if audio_path:
                print(f"✅ Audio extracted: {audio_path}")
                print(f"📊 File size: {os.path.getsize(audio_path)} bytes")
                
                # Test transcription
                print("🎙️ Testing transcription...")
                result = service.transcribe_audio(audio_path)
                
                if result:
                    print(f"✅ Transcription successful!")
                    print(f"📝 Length: {len(result.transcript)} characters")
                    print(f"👥 Speakers: {len(result.speakers)}")
                    print(f"🎯 Confidence: {result.confidence_score:.2f}")
                else:
                    print("❌ Transcription failed")
                    
            else:
                print("❌ Audio extraction failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc_exc()
    
    print("\n" + "=" * 60)
    print("🔧 Diagnostic Suggestions:")
    print("   1. Check if yt-dlp is installed: pip install yt-dlp")
    print("   2. Check FFmpeg installation: ffmpeg -version")
    print("   3. Try with different video URLs")
    print("   4. Check network connectivity")
    print("   5. Verify file permissions in temp directory")

if __name__ == "__main__":
    diagnose_audio_extraction()
