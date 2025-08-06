"""
LLM Integration for TRUE AI-powered Healthcare Agents
Supports Ollama (free, local) and OpenAI
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
import aiohttp
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Generate a response from the LLM"""
        pass

class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference"""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Generate response using Ollama"""
        
        # Combine system and user prompts
        full_prompt = ""
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nHuman: {prompt}\n\nAssistant:"
        else:
            full_prompt = prompt
            
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        print(f"Ollama error: {response.status}")
                        return ""
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return ""

class OpenAIProvider(LLMProvider):
    """OpenAI provider (requires API key)"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Generate response using OpenAI"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        print(f"OpenAI error: {response.status}")
                        return ""
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return ""

class LLMManager:
    """Manager for LLM operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.provider = self._initialize_provider()
            self.initialized = True
    
    def _initialize_provider(self) -> LLMProvider:
        """Initialize the appropriate LLM provider based on environment"""
        provider_type = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        if provider_type == "ollama":
            model = os.getenv("OLLAMA_MODEL", "llama2")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            print(f"🤖 Using Ollama with model: {model}")
            return OllamaProvider(model=model, base_url=base_url)
            
        elif provider_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️  No OpenAI API key found, falling back to Ollama")
                return OllamaProvider()
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            print(f"🤖 Using OpenAI with model: {model}")
            return OpenAIProvider(api_key=api_key, model=model)
            
        else:
            print(f"⚠️  Unknown LLM provider: {provider_type}, using Ollama")
            return OllamaProvider()
    
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Generate a response from the LLM"""
        if not self.provider:
            print("❌ No LLM provider available")
            return ""
        
        response = await self.provider.generate(prompt, system_prompt, temperature)
        return response.strip()
    
    async def generate_json(self, prompt: str, system_prompt: str = None, temperature: float = 0.3) -> Dict:
        """Generate a JSON response from the LLM"""
        
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON. No explanations, no text outside the JSON. Do not include comments or annotations in the JSON."
        
        response = await self.generate(json_prompt, system_prompt, temperature)
        
        # Try to parse JSON
        try:
            # Clean up response - remove markdown if present
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            # Remove any text in parentheses that might break JSON
            import re
            # Fix common issues like "360.00 (10-30% of total)"
            response = re.sub(r'(\d+\.?\d*)\s*\([^)]*\)', r'\1', response)
            
            # Try to fix incomplete JSON
            if response.count('{') > response.count('}'):
                response += '}' * (response.count('{') - response.count('}'))
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {response}")
            # Return a default structure based on what we expect
            return self._get_default_response(prompt)
    
    def _get_default_response(self, prompt: str) -> Dict:
        """Return a default response structure based on the prompt"""
        if "emergency alert" in prompt.lower():
            return {
                "show_alert": False,
                "severity": "low",
                "title": "",
                "urgency_reasons": [],
                "action_required": "",
                "personalized_warnings": []
            }
        elif "admission plan" in prompt.lower():
            return {
                "expected_stay": "2-3 days",
                "reasons": [],
                "daily_plan": {},
                "why_not_home": [],
                "what_to_bring": []
            }
        elif "cost estimate" in prompt.lower():
            return {
                "total_estimated": 10000,
                "breakdown": {},
                "insurance_estimate": {
                    "with_insurance": 2000,
                    "deductible_info": "Check your plan",
                    "coverage_note": "Varies by insurance"
                },
                "financial_options": [],
                "cost_without_treatment": ""
            }
        elif "decision support" in prompt.lower():
            return {
                "recommended_action": "",
                "recommendation_strength": "",
                "alternatives": [],
                "questions_for_doctor": [],
                "red_flags": []
            }
        return {}

# Singleton instance
llm_manager = LLMManager()
