import json
import subprocess
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

GHIDRA_HEADLESS = "/opt/ghidra/support/analyzeHeadless"

GHIDRA_PROJECTS_DIR = BASE_DIR / "ghidra_projects"
GHIDRA_RESULTS_DIR = BASE_DIR / "ghidra_results"
SCRIPT_DIR = BASE_DIR / "ghidra_scripts"

def run_ghidra_analysis(file_name: str):


    binary_path = PROJECT_ROOT / "uploads" / file_name

    if not binary_path.exists():
        return {"status": "error", "message": "Binary file not found"}

    GHIDRA_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    GHIDRA_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    project_name = f"project_{uuid4().hex}"
    output_path = GHIDRA_RESULTS_DIR / f"{uuid4().hex}.json"

    command = [
        GHIDRA_HEADLESS,
        str(GHIDRA_PROJECTS_DIR),
        project_name,
        "-import",
        str(binary_path),
        "-scriptPath",
        str(SCRIPT_DIR),
        "-postScript",
        "ExportFunctions.java",
        str(output_path),
        "-deleteProject",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "stderr": "Ghidra analysis timed out after 120 seconds."
        }
    if not output_path.exists():
        return {
            "status": "error",
            "reason": "Ghidra did not create output JSON",
            "exit_code": result.returncode,
            "stderr": result.stderr,
            "stdout": result.stdout[-2000:] if result.stdout else ""
        }

    # Если файл успешно создан на диске — забираем данные
    try:
        with open(output_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Чистим за собой временный файл результатов
        output_path.unlink(missing_ok=True)

        return {
            "status": "ok",
            "functions_count": len(data),
            "functions": data,
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": f"Failed to read JSON: {str(e)}"
        }
