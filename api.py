from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
from business_model_stress_tester import BusinessModelStressTester
import json
import uuid
import os
from datetime import datetime

# API key security
API_KEY_NAME = "GROQ_API_KEY"
API_KEY = os.getenv("API_KEY", "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")  # Set this securely
api_key_header = APIKeyHeader(name=API_KEY_NAME)

app = FastAPI(
    title="Business Model Stress Tester API",
    description="API for analyzing business models and generating stress test reports",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for async job status
jobs = {}

class BusinessModel(BaseModel):
    name: str
    industry: str
    target_market: str
    value_proposition: str
    revenue_streams: List[str]
    cost_structure: List[str]
    key_resources: List[str]
    key_partners: List[str]
    competitors: List[str]
    current_challenges: str
    financials: Optional[Dict[str, str]] = None

class StressTestResponse(BaseModel):
    job_id: str
    status: str
    report_url: Optional[str] = None

# API key verification
async def verify_api_key(api_key: str = Header(..., alias=API_KEY_NAME)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key

@app.post("/analyze", response_model=StressTestResponse)
async def analyze_business_model(
    model: BusinessModel,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze a business model and generate stress test report
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "started_at": datetime.now().isoformat()}
    
    background_tasks.add_task(run_analysis, job_id, model.dict())
    
    return StressTestResponse(
        job_id=job_id,
        status="pending"
    )

@app.get("/status/{job_id}", response_model=StressTestResponse)
async def get_job_status(job_id: str):
    """
    Get the status of an analysis job
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return StressTestResponse(
        job_id=job_id,
        status=jobs[job_id]["status"],
        report_url=jobs[job_id].get("report_url")
    )

def run_analysis(job_id: str, business_model: Dict[str, Any]):
    """
    Run the stress test analysis in background
    """
    try:
        stress_tester = BusinessModelStressTester()
        report = stress_tester.run_stress_test(business_model)
        
        # Save report
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{reports_dir}/{business_model['name'].lower().replace(' ', '_')}_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        jobs[job_id].update({
            "status": "completed",
            "report_url": f"/reports/{os.path.basename(filename)}",
            "completed_at": datetime.now().isoformat()
        })
    
    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })

@app.get("/reports/{filename}")
async def get_report(filename: str):
    """
    Get a generated report by filename
    """
    filepath = f"reports/{filename}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {"content": content}