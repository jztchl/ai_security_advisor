import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def to_json(data):
    try:
        logger.info("Converting to JSON")
        if '```json' in data:
                    json_start = data.find('```json') + 7
                    json_end = data.find('```', json_start)
                    json_text = data[json_start:json_end].strip()
        elif '```' in data:
                    json_start = data.find('```') + 3
                    json_end = data.find('```', json_start)
                    json_text = data[json_start:json_end].strip()
        else:
                    json_text = data.strip()
        try:
                    parsed_result = json.loads(json_text)
        except json.JSONDecodeError as e:
                
                    parsed_result = {
                        "error": f"JSON parsing error: {str(e)}",
                        "status": "analysis_error",
                        "raw_response": data
                    }
        return parsed_result
    except Exception as e:
        logger.error(f"Error converting to JSON: {e}")
        return str(e)