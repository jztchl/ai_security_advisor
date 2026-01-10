from typing import Dict, Any
import logging
from config import settings
from google import genai
from google.api_core import exceptions as api_exceptions
from google.genai.types import (
    GenerateContentConfig,
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client=genai.Client(api_key=settings.GEMINI_API_KEY)

async def analyze_code_security(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code for security vulnerabilities using Gemini AI
    """
    try :
        instruction = f"""
        Analyze the following {language} code for security vulnerabilities.
        Provide a detailed security assessment with:
        1. Potential vulnerabilities found
        2. Severity level (Critical/High/Medium/Low/Info)
        3. Recommended fixes
        4. Secure coding best practices

        Format your response as JSON with this structure:
        {{
            "analysis_id": "generated-uuid",
            "overall_severity": "High",
            "vulnerabilities": [
                {{
                    "type": "SQL Injection",
                    "severity": "High",
                    "description": "Direct string concatenation in SQL query",
                    "location": "file.py:42",
                    "fix": "Use parameterized queries",
                    "code_snippet": "query = f\\"SELECT * FROM users WHERE id = {code}\\""
                }}
            ],
            "recommendations": [
                "Use parameterized queries",
                "Implement input validation",
                "Add proper error handling"
            ],
            "score": 75
        }}
        """
        context=f"""Code:       
        {language}
        ```
        {code}
        ```
        """

        
        return client.models.generate_content(
            model="gemini-2.5-flash-lite",
            config=GenerateContentConfig(
                system_instruction=instruction,
            ),
            contents=context,
        )
    except api_exceptions.GoogleAPICallError as e:
        logger.error(f"Error calling Gemini: {e}")
        return None