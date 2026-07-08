import httpx
import time
from typing import List, Dict, Any, Optional, Tuple
from examai.config import get_settings
from examai.utils.logger import logger

class AIClient:
    def __init__(self):
        self.settings = get_settings()

    def _call_openrouter(self, messages: List[Dict[str, str]], model: str, api_key: str) -> str:
        """Call OpenRouter API to generate completions."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/adityasing9/examai-cli",
            "X-Title": "ExamAI CLI"
        }
        data = {
            "model": model,
            "messages": messages
        }
        
        # Implement standard retries with exponential backoff
        max_retries = 3
        backoff = 1.5
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=45.0) as client:
                    response = client.post(url, headers=headers, json=data)
                    response.raise_for_status()
                    resp_data = response.json()
                    
                    if "choices" in resp_data and len(resp_data["choices"]) > 0:
                        return resp_data["choices"][0]["message"]["content"]
                    else:
                        raise ValueError(f"Unexpected response format from OpenRouter: {resp_data}")
            except httpx.HTTPStatusError as e:
                logger.error(f"OpenRouter HTTP Error (Attempt {attempt+1}/{max_retries}): {e.response.text}")
                if attempt == max_retries - 1:
                    status_code = e.response.status_code
                    if status_code == 402:
                        raise RuntimeError(
                            f"OpenRouter returned 402 Payment Required. Your account has no credits. "
                            f"Add credits at https://openrouter.ai/credits or switch to a free model with: "
                            f"examai settings set openrouter_model \"openrouter/auto\""
                        ) from None
                    elif status_code == 404:
                        raise RuntimeError(
                            f"OpenRouter returned 404 Not Found for model '{model}'. "
                            f"The model name may be incorrect. Check available models at https://openrouter.ai/models"
                        ) from None
                    else:
                        raise RuntimeError(f"OpenRouter API error ({e.response.status_code}): {e.response.text}") from None
            except (httpx.RequestError, Exception) as e:
                logger.error(f"OpenRouter connection/request error (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"OpenRouter connection failed: {e}") from None
            time.sleep(backoff ** attempt)
        
        raise RuntimeError("Failed to get response from OpenRouter after retries.")

    def _call_ollama(self, messages: List[Dict[str, str]], model: str, host: str) -> str:
        """Call local Ollama instance API to generate completions."""
        url = f"{host.rstrip('/')}/api/chat"
        data = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, json=data)
                response.raise_for_status()
                resp_data = response.json()
                
                if "message" in resp_data and "content" in resp_data["message"]:
                    return resp_data["message"]["content"]
                else:
                    raise ValueError(f"Unexpected response format from Ollama: {resp_data}")
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            raise RuntimeError(f"Ollama server at {host} is unreachable or returned an error: {e}") from None

    def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        provider: Optional[str] = None, 
        model: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """
        Generates completions and returns a tuple: (content, final_provider, final_model)
        Falls back to local Ollama if OpenRouter fails/is offline.
        """
        settings = get_settings()
        prov = (provider or settings.default_provider).lower()
        
        if prov == "openrouter":
            m = model or settings.openrouter_model
            api_key = settings.openrouter_api_key
            
            if not api_key:
                logger.warning("OpenRouter API key is missing. Automatically falling back to local Ollama.")
                # Fallback to Ollama
                try:
                    ollama_model = settings.ollama_model
                    res = self._call_ollama(messages, ollama_model, settings.ollama_host)
                    return res, "ollama (fallback)", ollama_model
                except Exception as e:
                    raise ValueError("OpenRouter API key is not configured, and local Ollama connection failed. Please configure settings.")
            
            try:
                res = self._call_openrouter(messages, m, api_key)
                return res, "openrouter", m
            except Exception as e:
                logger.warning(f"OpenRouter request failed: {e}. Falling back to Ollama.")
                # Attempt fallback to Ollama
                try:
                    ollama_model = settings.ollama_model
                    res = self._call_ollama(messages, ollama_model, settings.ollama_host)
                    return res, "ollama (fallback)", ollama_model
                except Exception as fallback_err:
                    # If both fail, raise the original OpenRouter error
                    raise RuntimeError(
                        f"Both OpenRouter and Ollama fallback failed. OpenRouter error: {e}. Ollama error: {fallback_err}"
                    ) from None
        else:
            m = model or settings.ollama_model
            res = self._call_ollama(messages, m, settings.ollama_host)
            return res, "ollama", m

ai_client = AIClient()
