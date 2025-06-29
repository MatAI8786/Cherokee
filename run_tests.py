import json
import subprocess
import re
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
RESULT_FILE = BASE_DIR / "test_results.json"


def main():
    proc = subprocess.run([
        sys.executable,
        "-m",
        "pytest",
        "-vv",
        "tests"
    ], capture_output=True, text=True)
    output = proc.stdout + proc.stderr
    def extract(pattern):
        match = re.search(pattern, output)
        return int(match.group(1)) if match else 0
    passed = extract(r"(\d+)\s+passed")
    failed = extract(r"(\d+)\s+failed")
    errors = extract(r"(\d+)\s+errors?")
    warnings = extract(r"(\d+)\s+warnings?")
    RESULT_FILE.write_text(json.dumps({
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "warnings": warnings,
        "output": output
    }, indent=2))
    print(output)


if __name__ == "__main__":
    main()
