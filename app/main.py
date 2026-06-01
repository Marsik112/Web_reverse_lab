from fastapi import FastAPI, UploadFile, HTTPException
import os
import shutil

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/files")
async def upload_file(file: UploadFile):
    file_extension = os.path.splitext(file.filename)[1]

    available_extensions = [".exe", ".elf", ".bin", ".so", ".dll"]
    max_file_size = 50 # MB
    save_path = "/Web_reverse_lab/uploads"

    if file_extension not in available_extensions:
        raise HTTPException(status_code = 400, detail = "Неверное расширение")
    
    fs = await file.read()
    
    if len(fs) > max_file_size * 1024 * 1024:
        raise HTTPException(status_code = 413, detail = "Слишком большой файл(>50МБ)")
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "ok", "filename": file.filename, "extension": file_extension, "length": len(fs)}
    