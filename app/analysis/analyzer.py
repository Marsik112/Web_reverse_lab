import subprocess
from pathlib import Path

def anylyze_file_type(file_name):
    file_path = Path(__file__).resolve().parent.parent.parent / "uploads"
    file_result = subprocess.run(['file', file_name], cwd=file_path ,capture_output= True, text= True)
    return file_result.stdout

def analyze_file_strings(file_name):
    file_path = Path(__file__).resolve().parent.parent.parent / "uploads"
    file_result = subprocess.run(['strings', file_name], cwd=file_path ,capture_output= True, text= True) 
    return file_result.stdout