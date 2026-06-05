from fastapi import FastAPI, UploadFile, HTTPException
from pathlib import Path
import os
import shutil
from app.database import database
from app.analysis import analyzer
from app.analysis import ghidra_headless_analyzer
import json

app = FastAPI()
database.init_db()

available_extensions = [".exe", ".elf", ".bin", ".so", ".dll"]
max_file_size = 50 # MB
save_path = Path(__file__).resolve().parent.parent / 'uploads' 

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/files")
async def upload_file(file: UploadFile):
    file_extension = os.path.splitext(file.filename)[1]

    if file_extension not in available_extensions:
        raise HTTPException(status_code = 400, detail = "Неверное расширение")
    
    fs = await file.read()
    await file.seek(0)

    if len(fs) > max_file_size * 1024 * 1024:
        raise HTTPException(status_code = 413, detail = "Слишком большой файл(>50МБ)")
    
    file_id = database.add_file(file.filename, len(fs), "uploaded")
    new_filename = str(file_id) + file_extension
    file_path = save_path / new_filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"id": file_id, "filename": file.filename, "stored_name": new_filename,"extension": file_extension, "length": len(fs)}

@app.get("/files")
async def get_files_list():
    file_data = database.list_files()
    return file_data

@app.get("/files/{file_id}")
async def get_file_info(file_id: int):
    file_info = database.file_info(file_id)
    if file_info == None:
        raise HTTPException(status_code = 404, detail = "Файла с таким id не существует")
    file_info["saved_name"] = str(file_info["id"]) + os.path.splitext(file_info["filename"])[1]
    return file_info

@app.get("/files/{file_id}/analysis")
async def get_file_analyze(file_id: int):
    file_info = database.file_info(file_id)
    if file_info == None:
        raise HTTPException(status_code = 404, detail = "Файла с таким id не существует")
    saved_name = str(file_info["id"]) + os.path.splitext(file_info["filename"])[1]
    analisis_result = analyzer.analyze_file(file_id, saved_name)
    return analisis_result

@app.delete("/files/{file_id}")
def delete_file(file_id: int):
    file_info = database.file_info(file_id)
    if file_info == None:
        raise HTTPException(status_code = 404, detail = "Файла с таким id не существует")
    path =Path(__file__).resolve().parent.parent / 'uploads' / (str(file_info["id"]) + os.path.splitext(file_info["filename"])[1])
    path.unlink(missing_ok=True)
    database.delete_file(file_id)
    return {'status': 'deleted', "file_id": file_id}

@app.get("/files/{file_id}/ghidra")
def ghidra_analyze(file_id: int):
    file_info = database.file_info(file_id)       
    if file_info == None:
        raise HTTPException(status_code = 404, detail = "Файла с таким id не существует")
    ghidra_info = database.get_ghidra(file_id)
    if ghidra_info == None:
        saved_name = str(file_info["id"]) + os.path.splitext(file_info["filename"])[1]
        data = ghidra_headless_analyzer.run_ghidra_analysis(saved_name)
        if data == None:
           raise HTTPException(status_code = 400, detail = "Ошибка рабыты ghidra")
        database.add_ghidra(file_id, data)
    ghidra_info = database.get_ghidra(file_id)
    data = json.loads(ghidra_info['func_json'])
    analysis_time = ghidra_info["analysis_time"]

    return {"id": file_id, "time": analysis_time, "ghidra_func": data}