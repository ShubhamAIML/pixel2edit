import logging
import json
from typing import Dict, Any, Optional
from config import Config
from services.prompt_service import PromptService
from services.validation_service import ValidationService

logger = logging.getLogger(__name__)
logging.getLogger("google_genai").setLevel(logging.ERROR)


class GeminiService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self._custom_api_key = api_key
        self._custom_model = model
        self._client = None

    @property
    def api_key(self) -> str:
        return self._custom_api_key or Config.get_gemini_api_key()

    @property
    def model(self) -> str:
        return self._custom_model or Config.get_gemini_model()

    def _get_client(self):
        current_key = self.api_key
        if not current_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Please add it to your .env file."
            )
        try:
            from google import genai
            return genai.Client(api_key=current_key)
        except Exception as e:
            logger.error(f"Failed to initialize google-genai client: {e}")
            raise RuntimeError(
                f"Could not initialize Google GenAI SDK: {str(e)}"
            )

    def reconstruct_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        img_width: int,
        img_height: int
    ) -> Dict[str, Any]:
        """Calls Gemini Flash and extracts structured design JSON."""
        client = self._get_client()
        from google.genai import types

        prompt = PromptService.get_reconstruction_prompt(
            img_width, img_height
        )
        image_part = types.Part.from_bytes(
            data=image_bytes, mime_type=mime_type
        )

        candidate_models = list(dict.fromkeys([
            self.model,
            "gemini-3.5-flash",
            "gemini-2.5-flash",
            "gemini-3.6-flash",
            "gemini-flash-latest"
        ]))
        last_error = None

        for model_name in candidate_models:
            try:
                logger.info(
                    f"Calling Gemini ({model_name}) for reconstruction..."
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=[image_part, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2,
                    )
                )

                raw_text = response.text
                if not raw_text:
                    raise ValueError(
                        f"Gemini {model_name} returned an empty response."
                    )

                parsed = ValidationService.extract_json_from_text(raw_text)
                normalized = ValidationService.normalize_design_json(
                    parsed, default_w=img_width, default_h=img_height
                )
                return normalized

            except Exception as e:
                logger.warning(
                    f"Model {model_name} failed: {e}. Trying next..."
                )
                last_error = e

        logger.error(
            f"All Gemini models failed. Last error: {last_error}",
            exc_info=True
        )
        raise last_error

    def edit_with_ai(
        self,
        user_instruction: str,
        current_design: Dict[str, Any],
        selected_element_id: str
    ) -> Dict[str, Any]:
        """Calls Gemini Flash to generate minimal JSON patch."""
        client = self._get_client()
        from google.genai import types

        selected_element = None
        for el in current_design.get("elements", []):
            if el.get("id") == selected_element_id:
                selected_element = el
                break

        context_json = json.dumps({
            "selected_element": selected_element,
            "canvas": current_design.get("canvas")
        }, indent=2)

        prompt = PromptService.get_ai_edit_prompt(
            user_request=user_instruction,
            current_design_json=context_json,
            selected_element_id=selected_element_id
        )

        candidate_models = list(dict.fromkeys([
            self.model, "gemini-3.5-flash", "gemini-3.6-flash"
        ]))
        last_error = None

        for model_name in candidate_models:
            try:
                logger.info(
                    f"Calling Gemini ({model_name}) for AI edit: "
                    f"{user_instruction[:50]}"
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                    )
                )

                raw_text = response.text
                if not raw_text:
                    raise ValueError(
                        f"Gemini {model_name} returned empty patch."
                    )

                parsed_patch = ValidationService.extract_json_from_text(
                    raw_text
                )
                return parsed_patch

            except Exception as e:
                logger.warning(
                    f"AI Edit {model_name} failed: {e}. Trying next..."
                )
                last_error = e

        logger.error(
            f"All Gemini candidate models failed for AI edit: {last_error}",
            exc_info=True
        )
        raise last_error
