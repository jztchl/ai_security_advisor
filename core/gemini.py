from config import settings
from google import genai
from google.api_core import exceptions as api_exceptions
from google.genai.types import (
    GenerateContentConfig,
)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from utils.to_json import to_json
client=genai.Client(api_key=settings.GEMINI_API_KEY)


def gemini_generate_content(instruction: str, context: str) -> str:
    try:
        result= client.models.generate_content(
            model="gemini-2.5-flash",
            config=GenerateContentConfig(
                system_instruction=instruction,
            ),
            contents=context,
        )

        if result:
            result_text = result.text
            parsed_result = to_json(result_text)
                

            return parsed_result
    except api_exceptions.GoogleAPICallError as e:
        logger.error(f"Error calling Gemini: {e}")
        return  None