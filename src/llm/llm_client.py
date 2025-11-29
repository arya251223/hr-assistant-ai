import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from ..utils.logger import logger

load_dotenv()

class LLMClient:
    """Universal LLM client supporting multiple providers"""
    
    def __init__(self, provider: str = "ollama", model: str = "phi3:3.8b"):
        self.provider = provider.lower()
        self.model = model
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "180"))
        
        # Google AI Studio config
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.google_base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system: Optional[str] = None
    ) -> str:
        """Generate text using configured LLM"""
        
        if self.provider == "ollama":
            return self._ollama_generate(prompt, temperature, max_tokens, system)
        elif self.provider == "google" or self.provider == "gemini":
            return self._google_generate(prompt, temperature, max_tokens, system)
        elif self.provider == "openai":
            return self._openai_generate(prompt, temperature, max_tokens, system)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _check_ollama_health(self) -> bool:
        """Check if Ollama server is reachable"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _ollama_generate(
        self, 
        prompt: str, 
        temperature: float,
        max_tokens: int,
        system: Optional[str]
    ) -> str:
        """Generate using Ollama with improved error handling"""
        
        if not self._check_ollama_health():
            error_msg = "❌ Ollama server not responding. Please start Ollama."
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system:
                payload["system"] = system
            
            logger.info(f"Generating with model {self.model} (timeout: {self.timeout}s)")
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json().get("response", "")
            logger.info(f"Generation completed ({len(result)} chars)")
            return result
            
        except requests.exceptions.Timeout:
            error_msg = f"⏱️ Request timed out after {self.timeout}s"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except requests.exceptions.ConnectionError:
            error_msg = "❌ Cannot connect to Ollama"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return f"Error: {str(e)}"
    
    def _google_generate(
        self, 
        prompt: str, 
        temperature: float,
        max_tokens: int,
        system: Optional[str]
    ) -> str:
        """Generate using Google AI Studio (Gemini) - FULLY IMPLEMENTED"""
        
        if not self.google_api_key:
            error_msg = "❌ GOOGLE_API_KEY not set in .env file"
            logger.error(error_msg)
            return f"Error: {error_msg}\n\nGet your FREE key at: https://makersuite.google.com/app/apikey"
        
        try:
            # Use gemini-pro model
            model = self.model if self.model.startswith("gemini") else "gemini-pro"
            
            url = f"{self.google_base_url}/models/{model}:generateContent?key={self.google_api_key}"
            
            # Build prompt with system instruction if provided
            full_prompt = prompt
            if system:
                full_prompt = f"{system}\n\n{prompt}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                }
            }
            
            logger.info(f"Generating with Google {model}")
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract text from response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    logger.info(f"Generation completed ({len(text)} chars)")
                    return text
            
            return "Error: No response generated"
            
        except requests.exceptions.Timeout:
            error_msg = "⏱️ Google API timeout"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Google API error: {e.response.status_code}"
            if e.response.status_code == 429:
                error_msg += " - Rate limit exceeded. Wait 1 minute or upgrade plan."
            elif e.response.status_code == 403:
                error_msg += " - Invalid API key. Check GOOGLE_API_KEY in .env"
            logger.error(f"{error_msg} - {e.response.text}")
            return f"Error: {error_msg}"
            
        except Exception as e:
            logger.error(f"Google generation error: {e}")
            return f"Error: {str(e)}"
    
    def _openai_generate(
        self, 
        prompt: str, 
        temperature: float,
        max_tokens: int,
        system: Optional[str]
    ) -> str:
        """Generate using OpenAI (placeholder)"""
        logger.warning("OpenAI integration not yet implemented")
        return "OpenAI integration pending"
    
    def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """Chat-style generation"""
        
        if self.provider == "ollama":
            if not self._check_ollama_health():
                return "Error: Ollama not running"
            
            try:
                url = f"{self.base_url}/api/chat"
                
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                
                return response.json().get("message", {}).get("content", "")
                
            except Exception as e:
                logger.error(f"Ollama chat error: {e}")
                return f"Error: {str(e)}"
        
        else:
            # For Google/OpenAI, convert to simple generate
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            return self.generate(prompt, temperature, max_tokens)