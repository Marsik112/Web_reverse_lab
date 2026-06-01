from fastapi import FastAPI, UploadFile, HTTPException
from pathlib import Path
import os
import shutil
from app.database import database

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
    