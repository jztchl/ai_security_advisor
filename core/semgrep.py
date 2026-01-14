import subprocess
import json
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
        return result_text["results"]
