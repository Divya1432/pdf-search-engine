from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pymongo import MongoClient
from ocr_utils import extract_text_from_pdf, extract_metadata, validate_text

app = FastAPI()

# ✅ CORS fix (very important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["acts_db"]
collection = db["acts"]

@app.get("/")
def home():
    return {"message": "API running"}

# 📤 Upload API
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):

    # 🔁 Duplicate check
    if collection.find_one({"filename": file.filename}):
        return {"message": "File already exists"}

    file_location = f"temp_{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 📄 Extract text
    with open(file_location, "rb") as f:
        text = extract_text_from_pdf(f)

    # ❌ Empty check
    if not text.strip():
        os.remove(file_location)
        return {"message": "No text extracted"}

    # 🔍 Metadata + validation
    metadata = extract_metadata(text)
    validation = validate_text(text)

    # 💾 Save to DB
    collection.insert_one({
        "filename": file.filename,
        "text": text,
        "metadata": metadata,
        "validation": validation
    })

    os.remove(file_location)

    return {"message": "Uploaded successfully"}

# 🔍 Search API
@app.get("/search/")
def search(q: str):
    result = collection.find({
        "text": {"$regex": q, "$options": "i"}
    })

    return [{**doc, "_id": str(doc["_id"])} for doc in result]

# 🧹 Delete API (optional)
@app.get("/delete_all/")
def delete_all():
    collection.delete_many({})
    return {"message": "All deleted"}