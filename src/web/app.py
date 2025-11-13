"""
FastAPI Web Application for Script Analysis System.

This module provides a web interface for uploading, analyzing, and viewing
screenplay analysis results using the three-stage pipeline.
"""

import os
import json
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from fastapi import FastAPI, Request, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from prompts.schemas import Script
from src.pipeline import run_pipeline
from src.exporters import MarkdownExporter
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="剧本叙事结构分析系统",
    description="Script Narrative Structure Analysis System - Web Interface",
    version="2.3.0"
)

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
UPLOAD_DIR = STATIC_DIR / "uploads"

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Store active analysis jobs
active_jobs: Dict[str, dict] = {}

# WebSocket manager for progress updates
class ConnectionManager:
    """Manages WebSocket connections for real-time progress updates."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_id] = websocket
        logger.info(f"WebSocket connected for job: {job_id}")

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]
            logger.info(f"WebSocket disconnected for job: {job_id}")

    async def send_progress(self, job_id: str, message: dict):
        """Send progress update to client."""
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending progress for job {job_id}: {e}")
                self.disconnect(job_id)

manager = ConnectionManager()


# Pydantic models for API
class AnalysisRequest(BaseModel):
    """Request model for analysis job."""
    provider: str = "deepseek"
    model: Optional[str] = None
    export_markdown: bool = True


class AnalysisResponse(BaseModel):
    """Response model for analysis job."""
    job_id: str
    status: str
    message: str


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page with upload form."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/upload", response_model=AnalysisResponse)
async def upload_script(
    file: UploadFile = File(...),
    provider: str = "deepseek",
    model: Optional[str] = None,
    export_markdown: bool = True
):
    """
    Upload a script file and start analysis.

    Args:
        file: JSON script file
        provider: LLM provider (deepseek, anthropic, openai)
        model: Optional model name
        export_markdown: Whether to export Markdown report

    Returns:
        AnalysisResponse with job_id and status
    """
    # Validate file type
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")

    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Save uploaded file
        file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)

        # Validate script structure
        try:
            script_data = json.loads(content)
            script = Script(**script_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid script format: {str(e)}")

        # Create job record
        active_jobs[job_id] = {
            "job_id": job_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "provider": provider,
            "model": model,
            "export_markdown": export_markdown,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "stage": "queued"
        }

        # Start analysis in background
        asyncio.create_task(run_analysis_job(job_id, script, provider, model, export_markdown))

        logger.info(f"Analysis job created: {job_id} for {file.filename}")

        return AnalysisResponse(
            job_id=job_id,
            status="queued",
            message="Analysis job started successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/parse-txt", response_model=AnalysisResponse)
async def parse_txt_script(
    file: UploadFile = File(...),
    provider: str = "deepseek",
    model: Optional[str] = None,
    use_llm_enhancement: bool = True
):
    """
    Upload a TXT script file and parse it to JSON.

    Args:
        file: TXT script file
        provider: LLM provider for enhancement (deepseek, anthropic, openai)
        model: Optional model name
        use_llm_enhancement: Whether to use LLM enhancement (Phase 2)

    Returns:
        AnalysisResponse with job_id and status
    """
    # Validate file type
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only TXT files are supported")

    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Save uploaded file
        file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)

        # Create job record for parsing
        active_jobs[job_id] = {
            "job_id": job_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "provider": provider,
            "model": model,
            "use_llm_enhancement": use_llm_enhancement,
            "status": "parsing",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "stage": "parsing"
        }

        # Start parsing in background
        asyncio.create_task(run_parsing_job(job_id, str(file_path), provider, model, use_llm_enhancement))

        logger.info(f"Parsing job created: {job_id} for {file.filename}")

        return AnalysisResponse(
            job_id=job_id,
            status="parsing",
            message="Parsing job started successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TXT upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"TXT upload failed: {str(e)}")


@app.get("/parse-preview/{job_id}", response_class=HTMLResponse)
async def parse_preview_page(request: Request, job_id: str):
    """Render parsing preview page for TXT files."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]
    return templates.TemplateResponse("parse_preview.html", {
        "request": request,
        "job_id": job_id,
        "filename": job["filename"]
    })


@app.get("/analysis-from-parsed/{job_id}", response_class=HTMLResponse)
async def start_analysis_from_parsed(job_id: str):
    """
    Start three-stage analysis from a parsed TXT script.

    This endpoint redirects to the analysis page after starting the analysis job.
    """
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]

    # Check if parsing is complete
    if job["status"] != "parsed":
        raise HTTPException(status_code=400, detail="Parsing not yet completed")

    # Get the parsed script
    if "script" not in job:
        raise HTTPException(status_code=500, detail="Parsed script not available")

    script = job["script"]
    provider = job.get("provider", "deepseek")
    model = job.get("model")
    export_markdown = job.get("export_markdown", True)

    # Update job status to queued for analysis
    job["status"] = "queued"
    job["stage"] = "queued"
    job["progress"] = 0

    # Start analysis in background
    asyncio.create_task(run_analysis_job(job_id, script, provider, model, export_markdown))

    logger.info(f"Starting analysis for parsed script: {job_id}")

    # Redirect to analysis progress page
    return HTMLResponse(content=f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="0;url=/analysis/{job_id}" />
        </head>
        <body>
            <p>Starting analysis... Redirecting...</p>
        </body>
    </html>
    """)


@app.get("/analysis/{job_id}", response_class=HTMLResponse)
async def analysis_page(request: Request, job_id: str):
    """Render analysis progress page."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]
    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "job_id": job_id,
        "filename": job["filename"]
    })


@app.get("/results/{job_id}", response_class=HTMLResponse)
async def results_page(request: Request, job_id: str):
    """Render results page."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet completed")

    return templates.TemplateResponse("results.html", {
        "request": request,
        "job_id": job_id,
        "result": job.get("result")
    })


@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get current job status and results."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return JSONResponse(active_jobs[job_id])


@app.get("/api/download/report/{job_id}")
async def download_report(job_id: str):
    """Download Markdown report for a completed job."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")

    if "markdown_path" not in job:
        raise HTTPException(status_code=404, detail="Markdown report not found")

    markdown_path = Path(job["markdown_path"])

    if not markdown_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=str(markdown_path),
        filename=f"{job['filename']}_report.md",
        media_type="text/markdown"
    )


@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await manager.connect(job_id, websocket)

    try:
        # Send initial status
        if job_id in active_jobs:
            await manager.send_progress(job_id, {
                "type": "status",
                "data": active_jobs[job_id]
            })

        # Keep connection alive
        while True:
            # Wait for client messages (ping/pong)
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(job_id)


async def run_parsing_job(
    job_id: str,
    file_path: str,
    provider: str,
    model: Optional[str],
    use_llm_enhancement: bool
):
    """
    Parse TXT script file in background and update job status.

    Args:
        job_id: Unique job identifier
        file_path: Path to TXT file
        provider: LLM provider for enhancement
        model: Optional model name
        use_llm_enhancement: Whether to use LLM enhancement
    """
    try:
        # Update status to parsing
        active_jobs[job_id]["status"] = "parsing"
        active_jobs[job_id]["progress"] = 10
        await manager.send_progress(job_id, {
            "type": "progress",
            "stage": "parsing",
            "progress": 10,
            "message": "Starting to parse TXT script..."
        })

        # Import parser
        from src.parser import TXTScriptParser, LLMEnhancedParser
        from src.pipeline import create_llm

        # Choose parser based on enhancement flag
        if use_llm_enhancement:
            # Create LLM
            llm = create_llm(provider=provider, model_name=model)
            parser = LLMEnhancedParser(llm=llm)

            # Update progress for LLM enhancement
            active_jobs[job_id]["progress"] = 20
            await manager.send_progress(job_id, {
                "type": "progress",
                "stage": "parsing",
                "progress": 20,
                "message": "Parsing basic structure..."
            })
        else:
            parser = TXTScriptParser()

        # Parse the script
        logger.info(f"Parsing TXT script for job {job_id}")
        script = parser.parse(file_path)

        # Save parsed JSON
        json_path = Path(file_path).with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(script.model_dump(), f, ensure_ascii=False, indent=2)

        # Update job with parsed script
        active_jobs[job_id]["status"] = "parsed"
        active_jobs[job_id]["parsed_script_path"] = str(json_path)
        active_jobs[job_id]["script"] = script
        active_jobs[job_id]["progress"] = 100
        await manager.send_progress(job_id, {
            "type": "complete",
            "stage": "parsed",
            "progress": 100,
            "message": "Script parsed successfully!",
            "parsed_script": script.model_dump()
        })

        logger.info(f"Parsing complete for job {job_id}")

    except Exception as e:
        logger.error(f"Parsing failed for job {job_id}: {e}", exc_info=True)
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)
        await manager.send_progress(job_id, {
            "type": "error",
            "message": f"Parsing failed: {str(e)}"
        })


async def run_analysis_job(
    job_id: str,
    script: Script,
    provider: str,
    model: Optional[str],
    export_markdown: bool
):
    """
    Run analysis pipeline in background and update job status.

    Args:
        job_id: Unique job identifier
        script: Validated script object
        provider: LLM provider
        model: Optional model name
        export_markdown: Whether to export Markdown report
    """
    try:
        # Update status to running
        active_jobs[job_id]["status"] = "running"
        active_jobs[job_id]["stage"] = "stage1"
        active_jobs[job_id]["progress"] = 10
        await manager.send_progress(job_id, {
            "type": "progress",
            "stage": "stage1",
            "progress": 10,
            "message": "Starting Stage 1: Discovering TCCs..."
        })

        # Run pipeline (this is synchronous, runs in background task)
        logger.info(f"Running pipeline for job {job_id}")
        final_state = run_pipeline(script, provider=provider, model=model)

        # Stage 1 complete
        active_jobs[job_id]["stage"] = "stage2"
        active_jobs[job_id]["progress"] = 40
        await manager.send_progress(job_id, {
            "type": "progress",
            "stage": "stage2",
            "progress": 40,
            "message": "Stage 1 complete. Starting Stage 2: Auditing rankings..."
        })

        # Stage 2 complete (simulated delay for demo)
        await asyncio.sleep(1)
        active_jobs[job_id]["stage"] = "stage3"
        active_jobs[job_id]["progress"] = 70
        await manager.send_progress(job_id, {
            "type": "progress",
            "stage": "stage3",
            "progress": 70,
            "message": "Stage 2 complete. Starting Stage 3: Modifying structure..."
        })

        # Stage 3 complete
        await asyncio.sleep(1)
        active_jobs[job_id]["progress"] = 90
        await manager.send_progress(job_id, {
            "type": "progress",
            "stage": "export",
            "progress": 90,
            "message": "Stage 3 complete. Generating report..."
        })

        # Export Markdown if requested
        markdown_path = None
        if export_markdown:
            try:
                exporter = MarkdownExporter()
                result = {
                    "tccs": final_state["discoverer_output"].tccs if final_state["discoverer_output"] else [],
                    "rankings": final_state["auditor_output"].rankings if final_state["auditor_output"] else None,
                    "modifications": {
                        "modifications": final_state["modifier_output"].modification_log if final_state["modifier_output"] else [],
                        "total_issues": final_state["modifier_output"].validation.total_issues if final_state["modifier_output"] else 0,
                    },
                    "_metrics": final_state.get("_metrics", {}),
                    "script_json": final_state.get("script_json", {}),
                }

                markdown_path = UPLOAD_DIR / f"{job_id}_report.md"
                script_name = active_jobs[job_id]["filename"].replace(".json", "")
                exporter.export(result, markdown_path, script_name=script_name)

                active_jobs[job_id]["markdown_path"] = str(markdown_path)
                logger.info(f"Markdown report generated: {markdown_path}")

            except Exception as e:
                logger.error(f"Failed to generate Markdown report: {e}")

        # Analysis complete
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = 100
        active_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        active_jobs[job_id]["result"] = {
            "discoverer_output": final_state["discoverer_output"].model_dump() if final_state["discoverer_output"] else None,
            "auditor_output": final_state["auditor_output"].model_dump() if final_state["auditor_output"] else None,
            "modifier_output": final_state["modifier_output"].model_dump() if final_state["modifier_output"] else None,
            "errors": final_state["errors"],
            "retry_count": final_state["retry_count"],
            "metrics": final_state.get("_metrics", {})
        }

        await manager.send_progress(job_id, {
            "type": "complete",
            "progress": 100,
            "message": "Analysis completed successfully!",
            "result_url": f"/results/{job_id}"
        })

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)

        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)
        active_jobs[job_id]["failed_at"] = datetime.now().isoformat()

        await manager.send_progress(job_id, {
            "type": "error",
            "message": f"Analysis failed: {str(e)}"
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
