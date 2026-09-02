import httpx
import logging
from typing import Dict, Any, Optional
from app.services.ai.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

class ClaudeProvider(BaseAIProvider):
    """
    Anthropic Claude ATS Provider (supports Claude 3.5 Sonnet / Claude 3 Haiku).
    """

    def __init__(self, api_key: Optional[str] = None, model_id: str = "claude-3-5-sonnet-20241022"):
        super().__init__(provider_name="Claude", model_id=model_id, api_key=api_key)

    async def analyze(
        self,
        raw_resume: str,
        raw_jd: str,
        parsed_resume: Dict[str, Any],
        parsed_job: Dict[str, Any],
        deterministic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes Claude analysis asynchronously using Anthropic Messages API.
        """
        if not self.api_key or self.api_key.strip() == "":
            return self.create_fallback_response(
                self.provider_name, self.model_id, "unavailable", "Claude API key not configured.", deterministic_data
            )

        endpoint = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        user_prompt = self.build_user_prompt(raw_resume, raw_jd, parsed_resume, parsed_job, deterministic_data)
        system_prompt = self.get_canonical_system_prompt()

        payload = {
            "model": self.model_id,
            "max_tokens": 4096,
            "temperature": 0.2,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(endpoint, headers=headers, json=payload)

                if response.status_code != 200:
                    logger.warning(f"Claude API returned status {response.status_code}: {response.text}")
                    return self.create_fallback_response(
                        self.provider_name, self.model_id, "error", f"API Error: HTTP {response.status_code}", deterministic_data
                    )

                data = response.json()
                content_blocks = data.get("content", [])
                if not content_blocks:
                    return self.create_fallback_response(
                        self.provider_name, self.model_id, "error", "No content returned by Claude.", deterministic_data
                    )

                text_content = content_blocks[0].get("text", "")
                parsed_json = self.clean_json_response(text_content)

                if not parsed_json:
                    return self.create_fallback_response(
                        self.provider_name, self.model_id, "error", "Failed to parse Claude JSON response.", deterministic_data
                    )

                parsed_json["provider_name"] = self.provider_name
                parsed_json["model_id"] = self.model_id
                parsed_json["status"] = "success"
                return parsed_json

        except Exception as e:
            logger.error(f"Claude API execution error: {str(e)}")
            return self.create_fallback_response(
                self.provider_name, self.model_id, "error", f"Connection error: {str(e)}", deterministic_data
            )
