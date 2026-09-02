import json
import os
import requests
from typing import Optional, Dict, Any, List
from app.core.config import settings

class GeminiService:
    @staticmethod
    def is_available() -> bool:
        return bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())

    @staticmethod
    def generate_json_response(prompt: str, system_instruction: str = "") -> Optional[Dict[str, Any]]:
        """
        Call Google Gemini API via REST endpoint to generate structured JSON output.
        Returns parsed dict or None if API key missing or request fails.
        """
        if not GeminiService.is_available():
            return None

        api_key = settings.GEMINI_API_KEY.strip()
        # Gemini 1.5 Flash endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        headers = {"Content-Type": "application/json"}
        
        full_prompt = f"{system_instruction}\n\n{prompt}\n\nIMPORTANT: Return ONLY a valid, raw JSON object. Do not include markdown code block syntax (like ```json ... ```)."
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                result_json = response.json()
                text_content = result_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Strip ```json fences if returned despite prompt instruction
                if text_content.startswith("```json"):
                    text_content = text_content[7:]
                if text_content.startswith("```"):
                    text_content = text_content[3:]
                if text_content.endswith("```"):
                    text_content = text_content[:-3]
                
                return json.loads(text_content.strip())
            else:
                return None
        except Exception:
            return None
