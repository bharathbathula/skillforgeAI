import httpx
import logging
from typing import Dict, Any, Optional
from app.services.ai.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

class GeminiProvider(BaseAIProvider):
    """
    Google Gemini AI ATS Provider (supports Gemini 1.5 Flash / Pro).
    """

    def __init__(self, api_key: Optional[str] = None, model_id: str = "gemini-1.5-flash-latest"):
        super().__init__(provider_name="Gemini", model_id=model_id, api_key=api_key)

    async def analyze(
        self,
        raw_resume: str,
        raw_jd: str,
        parsed_resume: Dict[str, Any],
        parsed_job: Dict[str, Any],
        deterministic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes Gemini analysis asynchronously using REST API.
        """
        if not self.api_key or self.api_key.strip() == "":
            return self.create_fallback_response(
                self.provider_name, self.model_id, "unavailable", "Gemini API key not configured.", deterministic_data
            )

        user_prompt = self.build_user_prompt(raw_resume, raw_jd, parsed_resume, parsed_job, deterministic_data)
        system_prompt = self.get_canonical_system_prompt()

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json"
            }
        }

        models_to_try = [self.model_id, "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                last_error = ""
                for model_candidate in models_to_try:
                    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_candidate}:generateContent?key={self.api_key}"
                    response = await client.post(endpoint, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            parsed_json = self.clean_json_response(text_content)
                            if parsed_json:
                                parsed_json["provider_name"] = self.provider_name
                                parsed_json["model_id"] = model_candidate
                                parsed_json["status"] = "success"
                                return parsed_json
                    else:
                        last_error = f"HTTP {response.status_code}: {response.text[:120]}"

                return self.create_fallback_response(
                    self.provider_name, self.model_id, "error", f"Gemini API Error ({last_error})", deterministic_data
                )

        except Exception as e:
            logger.error(f"Gemini API execution error: {str(e)}")
            return self.create_fallback_response(
                self.provider_name, self.model_id, "error", f"Connection error: {str(e)}", deterministic_data
            )
