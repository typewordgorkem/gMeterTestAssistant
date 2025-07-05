"""
AI Client for Local AI Model Integration
Supports Ollama, LocalAI, and custom models
"""

import json
import httpx
import time
from typing import Dict, List, Optional, Any
from loguru import logger
import yaml
from pydantic import BaseModel


class AIResponse(BaseModel):
    """AI model response structure"""
    content: str
    model: str
    tokens_used: int
    response_time: float


class AIClient:
    """Client for interacting with local AI models"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.base_url = self.config['ai']['api_url']
        self.model_name = self.config['ai']['model_name']
        self.temperature = self.config['ai']['temperature']
        self.max_tokens = self.config['ai']['max_tokens']
        self.timeout = self.config['ai']['timeout']
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise
    
    def analyze_html(self, html_content: str, url: str) -> AIResponse:
        """Analyze HTML content with AI"""
        try:
            # Limit HTML content to avoid 500 errors
            limited_content = html_content[:500] if len(html_content) > 500 else html_content
            
            # Prepare simple Turkish prompt for HTML analysis
            prompt = f"""
Web sitesi analizi:
URL: {url}

Bu web sitesi için test senaryoları öner.
Basit JSON formatında yanıtla:
{{
    "buttons": ["Giriş", "Çıkış", "Ara"],
    "forms": ["login", "search"],
    "links": ["Ana Sayfa", "Hakkımızda"]
}}
"""
            
            return self._make_request(prompt)
            
        except Exception as e:
            logger.error(f"Error in HTML analysis: {e}")
            raise
    
    def generate_bdd_scenarios(self, html_analysis: Dict) -> AIResponse:
        """Generate BDD scenarios from HTML analysis"""
        try:
            # Prepare simple Turkish prompt for BDD generation
            prompt = f"""
Bu e-ticaret sitesi için basit BDD senaryoları üret:

Senaryo 1: Sayfa yükleme
Given: Kullanıcı web sitesine girer
When: Sayfa yüklenir
Then: Başlık görünür

Senaryo 2: Navigasyon
Given: Kullanıcı ana sayfada
When: Menüye tıklar
Then: Menü açılır

Senaryo 3: Buton testi
Given: Kullanıcı sayfada
When: Butona tıklar
Then: İşlem gerçekleşir

5 basit senaryo üret.
"""
            
            return self._make_request(prompt)
            
        except Exception as e:
            logger.error(f"Error in BDD scenario generation: {e}")
            raise
    
    async def generate_automation_code(self, bdd_scenarios: str, framework: str = "selenium") -> AIResponse:
        """Generate automation code based on BDD scenarios"""
        prompt = f"""
        Aşağıdaki BDD senaryolarını {framework} kullanarak Python otomasyon koduna dönüştür:
        
        BDD Senaryolar:
        {bdd_scenarios}
        
        Lütfen şunları içeren kod oluştur:
        1. Page Object Model pattern
        2. Selenium WebDriver setup
        3. Test methods
        4. Data-driven testing
        5. Screenshot capture on failure
        6. Detailed logging
        7. Error handling
        
        Kod pytest framework'ü ile uyumlu olmalı.
        Her test metodu için docstring ve yorum ekle.
        """
        
        return await self._make_request(prompt)
    
    def _make_request(self, prompt: str) -> AIResponse:
        """Make request to AI model"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        start_time = time.time()
        
        try:
            logger.debug(f"Making request to {self.base_url}/api/generate with model: {self.model_name}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                
                logger.debug(f"Response status: {response.status_code}")
                response.raise_for_status()
                
                result = response.json()
                end_time = time.time()
                
                logger.debug(f"Response received successfully in {end_time - start_time:.2f}s")
                
                return AIResponse(
                    content=result.get('response', ''),
                    model=self.model_name,
                    tokens_used=result.get('eval_count', 0),
                    response_time=end_time - start_time
                )
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def set_model(self, model_name: str):
        """Change AI model"""
        self.model_name = model_name
        logger.info(f"AI model changed to: {model_name}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                result = response.json()
                return [model['name'] for model in result.get('models', [])]
                
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return [] 