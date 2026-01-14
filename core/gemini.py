from config import settings
from google import genai
from google.api_core import exceptions as api_exceptions
from google.genai.types import (
    GenerateContentConfig,
)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import json
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
            if '```json' in result_text:
                    json_start = result_text.find('```json') + 7
                    json_end = result_text.find('```', json_start)
                    json_text = result_text[json_start:json_end].strip()
            elif '```' in result_text:
                    json_start = result_text.find('```') + 3
                    json_end = result_text.find('```', json_start)
                    json_text = result_text[json_start:json_end].strip()
            else:
                    json_text = result_text.strip()
                
            try:
                    print(f"{type(json_text)} *********************************")
                    parsed_result = json.loads(json_text)
            except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"Attempted to parse: {json_text}")
                    parsed_result = {
                        "error": f"JSON parsing error: {str(e)}",
                        "status": "analysis_error",
                        "raw_response": result_text
                    }
                    print(parsed_result)
                

            return parsed_result
    except api_exceptions.GoogleAPICallError as e:
        logger.error(f"Error calling Gemini: {e}")
        return  None