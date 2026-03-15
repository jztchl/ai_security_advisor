import subprocess
import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def run_semgrep(filepath: str):
        result = subprocess.run(
            [
                "semgrep",
                "--json",
                filepath
            ],
            capture_output=True,
            text=True
        )
        if result.returncode not in (0, 1):
            raise RuntimeError(result.stderr)
        result_text=json.loads(result.stdout)
        logger.info("Semgrep result generated")
        return result_text.get("results", [])

