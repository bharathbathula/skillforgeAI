import httpx
import logging
from typing import Dict, Any, Optional
from app.services.ai.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseAIProvider):
    """
    OpenAI ChatGPT ATS Provider (supports GPT-4o / GPT-4o-mini / GPT-3.5-turbo).
    """

    def __init__(self, api_key: Optional[str] = None, model_id: str = "gpt-4o-mini"):
        super().__init__(provider_name="OpenAI", model_id=model_id, api_key=api_key)

    async def analyze(
        self,
        raw_resume: str,
        raw_jd: str,
        parsed_resume: Dict[str, Any],
        parsed_job: Dict[str, Any],
        deterministic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes OpenAI analysis asynchronously using standard REST API.
        """
        if not self.api_key or self.api_key.strip() == "":
            return self.create_fallback_response(
                self.provider_name, self.model_id, "unavailable", "OpenAI API key not configured.", deterministic_data
            )

        endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        user_prompt = self.build_user_prompt(raw_resume, raw_jd, parsed_resume, parsed_job, deterministic_data)
        system_prompt = self.get_canonical_system_prompt()

        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(endpoint, headers=headers, json=payload)

                if response.status_code != 200:
                    logger.warning(f"OpenAI API returned status {response.status_code}: {response.text}")
                    return self.create_fallback_response(
                        self.provider_name, self.model_id, "error", f"API Error: HTTP {response.status_code}", deterministic_data
                    )

                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    return self.create_fallback_response(
                        self.provider_name, self.model_id, "error", "No choices returned by OpenAI.", deterministic_data
                    )

                content_str = choices[0].get("message", {}).get("content", "")
                parsed_json = self.clean_json_response(content_str)

                if not parsed_json:
                    return self.create_fallback_response(
                        self.provider_name, self.model_id, "error", "Failed to parse OpenAI JSON response.", deterministic_data
                    )

                parsed_json["provider_name"] = self.provider_name
                parsed_json["model_id"] = self.model_id
                parsed_json["status"] = "success"
                return parsed_json

        except Exception as e:
            logger.error(f"OpenAI API execution error: {str(e)}")
            return self.create_fallback_response(
                self.provider_name, self.model_id, "error", f"Connection error: {str(e)}", deterministic_data
            )
