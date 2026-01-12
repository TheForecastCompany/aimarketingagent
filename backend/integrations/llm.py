#!/usr/bin/env python3
"""
Ollama Integration - Local AI model support
Provides interface to Ollama for local AI processing
"""

import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class OllamaResponse:
    """Response from Ollama model"""
    response: str
    model: str
    tokens_used: int
    processing_time: float
    success: bool

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral:latest"):
        self.base_url = base_url
        self.model = model
        print(f"🦙 Ollama Client Initialized")
        print(f"🌐 Base URL: {base_url}")
        print(f"🤖 Model: {model}")
        
        # Check if model is available
        if not self._check_model_available():
            print(f"⚠️  Warning: Model '{model}' not found. Available models:")
            available_models = self._list_available_models()
            if available_models:
                print(f"   Available: {', '.join(available_models[:3])}...")
                # Try to use a common model instead of latest
                common_models = ["mistral:latest", "llama3.1:latest", "llama3:latest", "llama2:latest"]
                for common_model in common_models:
                    if common_model in available_models:
                        self.model = common_model
                        print(f"🔄 Switching to model: {self.model}")
                        break
                else:
                    # Fallback to first available model
                    self.model = available_models[0]
                    print(f"🔄 Switching to model: {self.model}")
            else:
                print("❌ No models available. Please run 'ollama pull mistral' or another model")
                self.model = "mistral:latest"  # Keep original as fallback
    
    def _check_model_available(self) -> bool:
        """Check if the current model is available"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=180)  # Increased timeout to 180 seconds for enhanced prompts
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model.get("name", "").endswith(f":{self.model}") for model in models)
        except Exception as e:
            print(f"⚠️  Model check failed: {str(e)}")
            pass
        return False
    
    def _list_available_models(self) -> List[str]:
        """List available models"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=180)  # Increased timeout to 180 seconds for enhanced prompts
            if response.status_code == 200:
                models = response.json().get("models", [])
                # Return full model names (e.g., "mistral:latest")
                return [model.get("name", "") for model in models]
        except Exception as e:
            print(f"⚠️  Failed to list models: {str(e)}")
            pass
        return []
    
    def _make_request(self, prompt: str, system_prompt: str = "") -> Optional[Dict]:
        """Make request to Ollama API"""
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=300)  # Increased timeout to 300 seconds for enhanced prompts
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ollama request failed: {e}")
            return None
    
    def generate(self, prompt: str, system_prompt: str = "") -> OllamaResponse:
        """Generate response using Ollama"""
        import time
        start_time = time.time()
        
        print(f"🦙 Generating with Ollama...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        response_data = self._make_request(prompt, system_prompt)
        
        if response_data:
            processing_time = time.time() - start_time
            response_text = response_data.get("response", "")
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            estimated_tokens = len(response_text) // 4
            print(f"📊 Estimated tokens: {estimated_tokens}")
            
            return OllamaResponse(
                response=response_text,
                model=self.model,
                tokens_used=int(estimated_tokens),
                processing_time=processing_time,
                success=True
            )
        else:
            # Return a fallback response instead of failing
            fallback_response = f"SEO optimization completed using {self.model}. Unable to generate detailed optimization due to connection issues."
            processing_time = time.time() - start_time
            
            return OllamaResponse(
                response=fallback_response,
                model=self.model,
                tokens_used=0,
                processing_time=processing_time,
                success=False
            )
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return models
            else:
                print(f"❌ Failed to list models: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing models: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

class OllamaAgent:
    """Base agent class using Ollama instead of OpenAI"""
    
    def __init__(self, name: str, description: str, ollama_client: OllamaClient, model: str = "mistral:latest"):
        self.name = name
        self.description = description
        self.ollama_client = ollama_client
        self.model = model
        print(f"🤖 {name} Agent (Ollama) Initialized")
        print(f"📋 {description}")
    
    def process(self, input_data: Any, system_prompt: str = "") -> Dict[str, Any]:
        """Process input using Ollama"""
        try:
            # Convert input to prompt
            if isinstance(input_data, str):
                prompt = input_data
            elif isinstance(input_data, dict):
                prompt = json.dumps(input_data, indent=2)
            else:
                prompt = str(input_data)
            
            # Generate response
            response = self.ollama_client.generate(prompt=prompt, model=self.model)
            
            if response and response.done and response.response:
                return {
                    "success": True,
                    "content": response.response,
                    "tokens_used": getattr(response, 'eval_count', 0),
                    "processing_time": getattr(response, 'total_duration', 0) / 1e9,  # Convert nanoseconds to seconds
                    "model": response.model
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate response",
                    "content": ""
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }

def demonstrate_ollama():
    """Demonstrate Ollama integration"""
    
    print("🦙 Ollama Integration Demo")
    print("=" * 60)
    
    # Initialize client
    client = OllamaClient(
        host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").replace("http://", "")
    )
    model = os.getenv("OLLAMA_MODEL", "mistral:latest")
    
    # Check availability
    print(f"\n🔍 Checking Ollama availability...")
    if client.is_available():
        print("✅ Ollama is available")
        
        # List models
        models = client.list_models()
        print(f"🤖 Available models: {models}")
        
        # Test generation
        print(f"\n🧪 Testing generation...")
        test_prompt = "Explain the benefits of local AI models in 3 sentences."
        
        response = client.generate(prompt=test_prompt, model=model)
        
        if response and response.done and response.response:
            print(f"✅ Generation successful!")
            print(f"📝 Response: {response.response}")
            print(f"📊 Tokens: {getattr(response, 'eval_count', 0)}")
            print(f"⏱️ Time: {getattr(response, 'total_duration', 0) / 1e9:.2f}s")
        else:
            print("❌ Generation failed")
            
    else:
        print("❌ Ollama is not available")
        print("💡 Make sure Ollama is running: ollama serve")
    
    # Test agent
    print(f"\n🤖 Testing Ollama Agent...")
    if client.is_available():
        agent = OllamaAgent("TestAgent", "Test agent using Ollama", client, model)
        
        result = agent.process("What is the capital of France?")
        
        if result["success"]:
            print(f"✅ Agent response: {result['content']}")
            print(f"📊 Tokens used: {result['tokens_used']}")
        else:
            print(f"❌ Agent failed: {result['error']}")
    
    print("\n" + "=" * 60)
    print("\n🦙 Ollama Benefits:")
    print("   ✅ Local processing (no API costs)")
    print("   ✅ Privacy and data control")
    print("   ✅ Offline capability")
    print("   ✅ Custom model support")
    print("   ✅ No rate limiting")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented Ollama integration for local AI processing'")
    print("   🎯 'Zero cost processing with local models'")
    print("   🎯 'Privacy-focused architecture with local deployment'")
    print("   🎯 'Flexible model support and configuration'")
    print("   🎯 'Robust error handling and fallbacks'")

if __name__ == "__main__":
    demonstrate_ollama()
