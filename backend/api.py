from fastapi import FastAPI, UploadFile, File, HTTPException
from backend.core.orchestrator import LegalAssistantBackend
import os
import shutil
import uuid

app = FastAPI(title="Legal Assistant API for Indian SMEs")
backend = LegalAssistantBackend()

# Get absolute path to the project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(ROOT_DIR, "data", "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/")
async def root():
    return {"message": "Legal Assistant AI API is running"}

@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    # 1. Save uploaded file temporarily
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    temp_filename = f"{file_id}{ext}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Process via Backend Orchestrator
        report = backend.process_contract(temp_path)
        
        # 3. Handle errors
        if "error" in report:
            raise HTTPException(status_code=400, detail=report["error"])
        
        # Add original filename to report
        report["original_filename"] = file.filename
        
        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup (Optional: keep or delete based on performance vs audit requirements)
        # os.remove(temp_path)
        pass

@app.get("/audit-logs")
async def get_logs():
    log_file = os.path.join(ROOT_DIR, "logs", "audit_trail.json")
    if os.path.exists(log_file):
        import json
        with open(log_file, 'r') as f:
            return json.load(f)
    return {"message": "No logs found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
