import subprocess
from pathlib import Path
from app.database import database

def analyze_file_type(file_name):
    file_path = Path(__file__).resolve().parent.parent.parent / "uploads"
    file_result = subprocess.run(['file', file_name], cwd=file_path ,capture_output= True, text= True)
    return file_result.stdout

def analyze_file_strings(file_name):
    file_path = Path(__file__).resolve().parent.parent.parent / "uploads"
    file_result = subprocess.run(['strings', file_name], cwd=file_path ,capture_output= True, text= True) 
    return file_result.stdout

def analyze_file(file_id, saved_name):
    search_analisys =  database.get_analysis(file_id)
    if search_analisys == None:
        file_result = analyze_file_type(saved_name)
        strings_result = analyze_file_strings(saved_name)
        database.add_analisys(file_id, file_result, strings_result)
    else: 
        file_result = search_analisys["file_result"]
        strings_result = search_analisys["strings_output"]
    strings_output = []
    counts = 0
    for row in strings_result.split("\n"):
        if len(row) >= 5:
            strings_output.append(row)
            counts+=1
        if counts >=100:
            break
    return {"id": file_id, "file_result": file_result, "strings_result": strings_output}