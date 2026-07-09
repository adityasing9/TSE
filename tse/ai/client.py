import httpx
import time
from typing import List, Dict, Any, Optional, Tuple
from tse.config import get_settings
from tse.utils.logger import logger

class AIClient:
    def __init__(self):
        self.settings = get_settings()

    def _call_openrouter(self, messages: List[Dict[str, str]], model: str, api_key: str) -> str:
        """Call OpenRouter API to generate completions."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/adityasing9/TSE",
            "X-Title": "TSE CLI"
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
                            f"Add credits at https://openrouter.ai/credits or switch to free Gemini provider with: "
                            f"tse settings set provider \"gemini\""
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

    def _call_gemini(self, messages: List[Dict[str, str]], model: str, api_key: str) -> str:
        """Call Google AI Studio (Gemini) REST API directly. Free tier supported."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        # Convert OpenAI-style messages to Gemini format
        gemini_contents = []
        system_instruction = None
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                # Gemini uses systemInstruction separately
                system_instruction = content
            elif role == "user":
                gemini_contents.append({"role": "user", "parts": [{"text": content}]})
            elif role == "assistant":
                gemini_contents.append({"role": "model", "parts": [{"text": content}]})
        
        data = {"contents": gemini_contents}
        if system_instruction:
            data["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, json=data)
                response.raise_for_status()
                resp_data = response.json()
                
                if "candidates" in resp_data and len(resp_data["candidates"]) > 0:
                    candidate = resp_data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        return candidate["content"]["parts"][0]["text"]
                
                raise ValueError(f"Unexpected response format from Gemini: {resp_data}")
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 400:
                raise RuntimeError(f"Gemini API error: Invalid request. Check your API key and model name '{model}'.") from None
            elif status_code == 403:
                raise RuntimeError(f"Gemini API key is invalid or doesn't have access. Get a free key at https://aistudio.google.com/apikey") from None
            elif status_code == 429:
                raise RuntimeError(f"Gemini rate limit exceeded. Wait a moment and try again.") from None
            else:
                raise RuntimeError(f"Gemini API error ({status_code}): {e.response.text}") from None
        except Exception as e:
            logger.error(f"Gemini connection error: {e}")
            raise RuntimeError(f"Gemini API call failed: {e}") from None

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

    def _try_fallbacks(self, messages: List[Dict[str, str]], primary_error: str, skip_provider: str = "") -> Tuple[str, str, str]:
        """Try fallback providers: Gemini → Ollama. Returns (content, provider, model) or raises."""
        settings = get_settings()
        errors = [primary_error]
        
        # Try Gemini fallback (if not the primary)
        if skip_provider != "gemini" and settings.gemini_api_key:
            try:
                gemini_model = settings.gemini_model
                logger.info("Falling back to Gemini...")
                res = self._call_gemini(messages, gemini_model, settings.gemini_api_key)
                return res, "gemini (fallback)", gemini_model
            except Exception as e:
                errors.append(f"Gemini: {e}")
        
        # Try Ollama fallback (if not the primary)
        if skip_provider != "ollama":
            try:
                ollama_model = settings.ollama_model
                logger.info("Falling back to Ollama...")
                res = self._call_ollama(messages, ollama_model, settings.ollama_host)
                return res, "ollama (fallback)", ollama_model
            except Exception as e:
                errors.append(f"Ollama: {e}")
        
        raise RuntimeError(" | ".join(errors)) from None

    def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        provider: Optional[str] = None, 
        model: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """
        Generates completions and returns a tuple: (content, final_provider, final_model)
        Falls back through available providers if the primary fails.
        Fallback chain: primary → gemini → ollama
        """
        settings = get_settings()
        prov = (provider or settings.default_provider).lower()
        
        if prov == "gemini":
            m = model or settings.gemini_model
            api_key = settings.gemini_api_key
            
            if not api_key:
                raise RuntimeError(
                    "Gemini API key is not configured. Get a free key at https://aistudio.google.com/apikey "
                    "then run: tse settings set gemini_api_key \"YOUR_KEY\""
                ) from None
            
            try:
                res = self._call_gemini(messages, m, api_key)
                return res, "gemini", m
            except Exception as e:
                logger.warning(f"Gemini request failed: {e}. Trying fallbacks...")
                return self._try_fallbacks(messages, f"Gemini: {e}", skip_provider="gemini")
        
        elif prov == "openrouter":
            m = model or settings.openrouter_model
            api_key = settings.openrouter_api_key
            
            if not api_key:
                logger.warning("OpenRouter API key is missing. Trying fallbacks...")
                return self._try_fallbacks(messages, "OpenRouter API key is not configured", skip_provider="openrouter")
            
            try:
                res = self._call_openrouter(messages, m, api_key)
                return res, "openrouter", m
            except Exception as e:
                logger.warning(f"OpenRouter request failed: {e}. Trying fallbacks...")
                return self._try_fallbacks(messages, f"OpenRouter: {e}", skip_provider="openrouter")
        
        else:  # ollama
            m = model or settings.ollama_model
            try:
                res = self._call_ollama(messages, m, settings.ollama_host)
                return res, "ollama", m
            except Exception as e:
                logger.warning(f"Ollama request failed: {e}. Trying fallbacks...")
                return self._try_fallbacks(messages, f"Ollama: {e}", skip_provider="ollama")

ai_client = AIClient()
