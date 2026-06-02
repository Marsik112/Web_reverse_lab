from fastapi import FastAPI, UploadFile, HTTPException
from pathlib import Path
import os
import shutil
from app.database import database
from app.analysis import analyzer

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
    file_result = analyzer.anylyze_file_type(saved_name)
    strings_result = analyzer.analyze_file_strings(saved_name)
    database.add_analisys(file_id, file_result, strings_result)
    strings_output = []
    counts = 0
    for row in strings_result.split("\n"):
        if len(row) >= 5:
            strings_output.append(row)
            counts+=1
        if counts >=100:
            break
    return {"id": file_id, "file_result": file_result, "strings_result": strings_output}