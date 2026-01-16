from config import settings
from mistralai import Mistral
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
api_key = settings.MISTRAL_API_KEY
model = "devstral-small-latest"
client = Mistral(api_key=api_key)
from utils.to_json import to_json
def generate_content_mistral(instruction: str, context: str) -> str:
    try:
        content=instruction+"\n\n"+context
        resposne=client.chat.complete(
    model = model,
    messages = [
        {
            "role": "user",
            "content": content,
        },
    ]
)
        parsed_result = to_json(resposne.choices[0].message.content)
        return parsed_result
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return None