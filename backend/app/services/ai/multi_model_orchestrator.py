import asyncio
import logging
from typing import Dict, Any
from app.core.config import settings
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.claude_provider import ClaudeProvider

logger = logging.getLogger(__name__)

class MultiModelOrchestrator:
    """
    Executes Gemini, OpenAI, and Claude AI model evaluations in parallel.
    Handles individual provider failures and returns all 3 structured responses.
    """

    @classmethod
    async def run_multi_model_evaluation(
        cls,
        raw_resume: str,
        raw_jd: str,
        parsed_resume: Dict[str, Any],
        parsed_job: Dict[str, Any],
        deterministic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes Gemini, OpenAI, and Claude concurrent evaluations.
        """
        # Instantiate providers
        gemini = GeminiProvider(api_key=settings.GEMINI_API_KEY)
        openai = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
        claude = ClaudeProvider(api_key=settings.ANTHROPIC_API_KEY)

        # Run concurrently with asyncio.gather
        tasks = [
            gemini.analyze(raw_resume, raw_jd, parsed_resume, parsed_job, deterministic_data),
            openai.analyze(raw_resume, raw_jd, parsed_resume, parsed_job, deterministic_data),
            claude.analyze(raw_resume, raw_jd, parsed_resume, parsed_job, deterministic_data)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        gemini_res = results[0] if not isinstance(results[0], Exception) else gemini.create_fallback_response("Gemini", gemini.model_id, "error", str(results[0]), deterministic_data)
        openai_res = results[1] if not isinstance(results[1], Exception) else openai.create_fallback_response("OpenAI", openai.model_id, "error", str(results[1]), deterministic_data)
        claude_res = results[2] if not isinstance(results[2], Exception) else claude.create_fallback_response("Claude", claude.model_id, "error", str(results[2]), deterministic_data)

        return {
            "gemini": gemini_res,
            "openai": openai_res,
            "claude": claude_res
        }
