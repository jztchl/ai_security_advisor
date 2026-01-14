from typing import Dict, Any
import logging
import uuid
from .gemini import gemini_generate_content
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_code_security(code: str, language: str = "python",task_id:uuid.UUID = None,
filepath:str = None,semgrep_result=[],mode="gemini") -> Dict[str, Any]:

    if semgrep_result:
        semgrep_result_str = "\n".join(semgrep_result)
    else:
        semgrep_result_str = "not found"
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

        here is the semgrep result:
        {semgrep_result_str}

        Format your response as JSON with this structure:
        {{
            "analysis_id": "{task_id}",
            "overall_severity": "High",
            "vulnerabilities": [
                {{
                    "type": "SQL Injection",
                    "severity": "High",
                    "description": "Direct string concatenation in SQL query",
                    "location": "{filepath}",
                    "fix": "Use parameterized queries",
                    "code_snippet": " {code}"
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
        please do not markdown text formating in response
        do not mention semgrep in response only use it as a reference
        """
        if mode == "gemini":
            response = gemini_generate_content(instruction, context)  
            if not response:
                logger.error("Failed to get response from Gemini")
                return None
        elif mode =="local":
            # TODO: Implement local AI analysis
            pass

        return response
        
    except Exception as e:
        logging.error(f"Error analyzing code: {e}")
        return None