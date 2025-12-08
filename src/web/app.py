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
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from prompts.schemas import Script
from src.pipeline import run_pipeline
from src.exporters import MarkdownExporter, TXTExporter
from src.version import __version__, get_version_info, get_git_info
from src.db import CacheManager
import logging
import time

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
    version=__version__
)

# Add CORS middleware to allow cross-origin requests (for VS Code port forwarding)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Static file version for cache busting (update this when JS/CSS changes)
STATIC_VERSION = __version__

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

# Initialize cache manager
cache_manager = CacheManager()

# WebSocket manager for progress updates
class ConnectionManager:
    """Manages WebSocket connections for real-time progress updates.

    Features:
    - Message history queue for replay on late connections
    - Automatic cleanup of old message history
    - Handles race condition between task start and WebSocket connect
    """

    # Maximum messages to keep in history per job
    MAX_HISTORY_SIZE = 50
    # Time in seconds to keep history after job completion
    HISTORY_RETENTION_SECONDS = 300  # 5 minutes

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.message_history: Dict[str, list] = {}  # job_id -> list of messages
        self.job_completion_times: Dict[str, float] = {}  # job_id -> completion timestamp

    async def connect(self, job_id: str, websocket: WebSocket):
        """Accept WebSocket connection and replay message history."""
        await websocket.accept()
        self.active_connections[job_id] = websocket
        logger.info(f"WebSocket connected for job: {job_id}")

        # Replay message history if available
        if job_id in self.message_history:
            history = self.message_history[job_id]
            logger.info(f"Replaying {len(history)} historical messages for job {job_id}")
            for msg in history:
                try:
                    await websocket.send_json(msg)
                except Exception as e:
                    logger.error(f"Error replaying message for job {job_id}: {e}")
                    break

    def disconnect(self, job_id: str):
        """Disconnect WebSocket and optionally schedule history cleanup."""
        if job_id in self.active_connections:
            del self.active_connections[job_id]
            logger.info(f"WebSocket disconnected for job: {job_id}")

    async def send_progress(self, job_id: str, message: dict):
        """Send progress update to client and save to history."""
        # Always save to history first (handles race condition)
        if job_id not in self.message_history:
            self.message_history[job_id] = []

        # Add message to history
        self.message_history[job_id].append(message)

        # Trim history if too large
        if len(self.message_history[job_id]) > self.MAX_HISTORY_SIZE:
            self.message_history[job_id] = self.message_history[job_id][-self.MAX_HISTORY_SIZE:]

        # Mark completion time for cleanup scheduling
        if message.get("type") in ("complete", "error"):
            self.job_completion_times[job_id] = time.time()

        # Send to connected client if available
        if job_id in self.active_connections:
            try:
                logger.debug(f"Sending progress for job {job_id}: {message}")
                await self.active_connections[job_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending progress for job {job_id}: {e}")
                logger.error(f"Message that failed: {message}")
                self.disconnect(job_id)

    def cleanup_old_history(self):
        """Remove message history for completed jobs older than retention period."""
        current_time = time.time()
        jobs_to_clean = []

        for job_id, completion_time in self.job_completion_times.items():
            if current_time - completion_time > self.HISTORY_RETENTION_SECONDS:
                jobs_to_clean.append(job_id)

        for job_id in jobs_to_clean:
            if job_id in self.message_history:
                del self.message_history[job_id]
            if job_id in self.job_completion_times:
                del self.job_completion_times[job_id]
            logger.debug(f"Cleaned up message history for job {job_id}")

        if jobs_to_clean:
            logger.info(f"Cleaned up message history for {len(jobs_to_clean)} completed jobs")

    def get_history_stats(self) -> dict:
        """Get statistics about message history (for debugging)."""
        return {
            "active_connections": len(self.active_connections),
            "jobs_with_history": len(self.message_history),
            "total_messages": sum(len(msgs) for msgs in self.message_history.values()),
            "pending_cleanup": len(self.job_completion_times)
        }

manager = ConnectionManager()

# Background task for periodic history cleanup
async def periodic_history_cleanup():
    """Background task to periodically clean up old message history."""
    while True:
        await asyncio.sleep(60)  # Run every 60 seconds
        try:
            manager.cleanup_old_history()
        except Exception as e:
            logger.error(f"Error during history cleanup: {e}")


@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    asyncio.create_task(periodic_history_cleanup())
    logger.info("Started periodic history cleanup task")


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
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    version_info = get_version_info()
    git_info = get_git_info()
    return {
        "status": "healthy",
        "service": "screenplay-analysis",
        "version": version_info["version"],
        "version_name": version_info["name"],
        "git_commit": git_info["commit_short"],
        "git_branch": git_info["branch"],
        "build_date": version_info["build_date"],
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Cache API Endpoints (Session 16)
# ============================================================================

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics including hit rate, total entries, etc."""
    stats = cache_manager.get_stats()
    return stats.to_dict()


@app.get("/api/history")
async def list_history(
    limit: int = 20,
    offset: int = 0,
    search: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None
):
    """
    List cached analysis history with pagination and filtering.

    Args:
        limit: Maximum entries to return (default 20)
        offset: Number of entries to skip
        search: Search term for script name
        provider: Filter by LLM provider
        model: Filter by model name

    Returns:
        List of cache entries with pagination info
    """
    entries, total = cache_manager.list_all(
        limit=limit,
        offset=offset,
        search=search,
        provider=provider,
        model=model
    )

    return {
        "entries": [entry.to_dict() for entry in entries],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(entries) < total
    }


@app.get("/api/history/{cache_id}")
async def get_history_entry(cache_id: int):
    """Get a specific cache entry by ID."""
    entry = cache_manager.get_by_id(cache_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Cache entry not found")

    # Parse JSON fields back to dicts for response
    result = entry.to_dict()
    if entry.stage1_result:
        result["stage1_result"] = json.loads(entry.stage1_result)
    if entry.stage2_result:
        result["stage2_result"] = json.loads(entry.stage2_result)
    if entry.stage3_result:
        result["stage3_result"] = json.loads(entry.stage3_result)
    if entry.parsed_script:
        result["parsed_script"] = json.loads(entry.parsed_script)

    return result


@app.delete("/api/history/{cache_id}")
async def delete_history_entry(cache_id: int):
    """Delete a specific cache entry."""
    success = cache_manager.delete(cache_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    return {"status": "deleted", "id": cache_id}


@app.post("/api/cache/cleanup")
async def cleanup_expired_cache():
    """Remove expired cache entries."""
    removed = cache_manager.cleanup_expired()
    return {"status": "success", "removed_count": removed}


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Render history page for viewing cached analyses."""
    version_info = get_version_info()
    return templates.TemplateResponse("history.html", {
        "request": request,
        "version": STATIC_VERSION,
        "version_info": version_info
    })


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page with upload form."""
    # Get configured LLM provider from environment
    default_provider = os.getenv("LLM_PROVIDER", "deepseek")
    version_info = get_version_info()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "version": STATIC_VERSION,
        "default_provider": default_provider,
        "version_info": version_info
    })


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

        # Start analysis in background (pass content for cache hash)
        script_content = content.decode('utf-8')
        asyncio.create_task(run_analysis_job(
            job_id, script, provider, model, export_markdown,
            script_content=script_content
        ))

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


@app.get("/api/parsed-script/{job_id}")
async def get_parsed_script(job_id: str):
    """Get parsed script data for a completed TXT parsing job."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]

    if job["status"] == "failed":
        raise HTTPException(status_code=400, detail=job.get("error", "Parsing failed"))

    if job["status"] != "parsed":
        # Still parsing - include all progress info
        progress = job.get("progress", 0)
        message = job.get("message", "解析中...")
        logger.info(f"Polling response for {job_id}: progress={progress}, message={message}")
        return {
            "status": "parsing",
            "progress": progress,
            "message": message
        }

    # Parsing complete - return script data
    script = job.get("script")
    if not script:
        raise HTTPException(status_code=500, detail="Parsed script not available")

    return {
        "status": "complete",
        "script": script.model_dump()
    }


@app.get("/parse-preview/{job_id}", response_class=HTMLResponse)
async def parse_preview_page(request: Request, job_id: str):
    """Render parsing preview page for TXT files."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]
    return templates.TemplateResponse("parse_preview.html", {
        "request": request,
        "job_id": job_id,
        "filename": job["filename"],
        "version": STATIC_VERSION,
        "version_info": get_version_info()
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

    # Read original file content for cache hash
    script_content = None
    if "file_path" in job:
        try:
            with open(job["file_path"], 'r', encoding='utf-8') as f:
                script_content = f.read()
        except Exception as e:
            logger.warning(f"Could not read original file for cache: {e}")

    # Start analysis in background
    asyncio.create_task(run_analysis_job(
        job_id, script, provider, model, export_markdown,
        script_content=script_content
    ))

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
        "filename": job["filename"],
        "version": STATIC_VERSION,
        "version_info": get_version_info()
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
        "result": job.get("result"),
        "version": STATIC_VERSION,
        "version_info": get_version_info()
    })


@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get current job status and results."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]

    # Create a serializable version of job data (exclude Script object)
    serializable_job = {
        "job_id": job["job_id"],
        "filename": job["filename"],
        "status": job["status"],
        "progress": job.get("progress", 0),
        "stage": job.get("stage", ""),
        "created_at": job.get("created_at", ""),
        "provider": job.get("provider", ""),
        "model": job.get("model")
    }

    # Add completion timestamp if available
    if "completed_at" in job:
        serializable_job["completed_at"] = job["completed_at"]

    # Add error if failed
    if job["status"] == "failed" and "error" in job:
        serializable_job["error"] = job["error"]

    # Add result if completed (convert Pydantic models to dicts)
    if job["status"] == "completed" and "result" in job:
        serializable_job["result"] = job["result"]

    return JSONResponse(serializable_job)


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


@app.get("/api/download/report-txt/{job_id}")
async def download_report_txt(job_id: str):
    """Download TXT report for a completed job."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")

    if "txt_path" not in job:
        raise HTTPException(status_code=404, detail="TXT report not found")

    txt_path = Path(job["txt_path"])

    if not txt_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=str(txt_path),
        filename=f"{job['filename']}_report.txt",
        media_type="text/plain; charset=utf-8"
    )


@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await manager.connect(job_id, websocket)

    try:
        # Send initial status
        if job_id in active_jobs:
            job = active_jobs[job_id]

            # If parsing is complete, send completion summary
            if job["status"] == "parsed":
                await manager.send_progress(job_id, {
                    "type": "complete",
                    "stage": "parsed",
                    "progress": 100,
                    "message": "Script parsed successfully!",
                    "scene_count": len(job["script"].scenes) if "script" in job else 0,
                    "character_count": len(set(char for scene in job["script"].scenes for char in scene.characters)) if "script" in job else 0
                })
            else:
                # Create a serializable version of job data without Script object
                job_data = {
                    "job_id": job["job_id"],
                    "filename": job["filename"],
                    "status": job["status"],
                    "progress": job.get("progress", 0),
                    "stage": job.get("stage", ""),
                    "created_at": job.get("created_at", "")
                }
                await manager.send_progress(job_id, {
                    "type": "status",
                    "data": job_data
                })

        # Keep connection alive
        while True:
            try:
                # Wait for client messages (ping/pong)
                await websocket.receive_text()
            except RuntimeError as e:
                # Handle "WebSocket is not connected" error gracefully
                if "not connected" in str(e).lower():
                    break
                raise

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}")
    finally:
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
        active_jobs[job_id]["progress"] = 8
        await manager.send_progress(job_id, {
            "type": "progress",
            "stage": "init",
            "progress": 8,
            "message": "正在初始化解析器..."
        })

        # Import parser
        from src.parser import TXTScriptParser, LLMEnhancedParser
        from src.pipeline import create_llm

        # Define progress callback for LLM enhancement
        # Now receives current/total as LLM call counts (5 per scene)
        async def on_scene_progress(current: int, total: int, message: str):
            """Report per-LLM-call progress during LLM enhancement.

            Args:
                current: Current LLM call number (1 to total)
                total: Total number of LLM calls (num_scenes * 5)
                message: Progress message from parser (includes scene info)
            """
            # Calculate progress: 25% base + 65% for LLM enhancement (25-90%)
            llm_progress = 25 + int(65 * current / total)
            active_jobs[job_id]["progress"] = llm_progress
            active_jobs[job_id]["message"] = message
            logger.info(f"[POLLING] Updated job {job_id}: progress={llm_progress}, message={message}")

            await manager.send_progress(job_id, {
                "type": "progress",
                "stage": "llm_enhancement",
                "progress": llm_progress,
                "message": message,  # Already formatted by parser
                "current_step": current,
                "total_steps": total
            })

        # Choose parser based on enhancement flag
        if use_llm_enhancement:
            # Update progress - creating LLM
            active_jobs[job_id]["progress"] = 12
            await manager.send_progress(job_id, {
                "type": "progress",
                "stage": "init",
                "progress": 12,
                "message": f"正在连接 {provider.upper()} 模型..."
            })

            # Create LLM
            llm = create_llm(provider=provider, model=model)
            parser = LLMEnhancedParser(llm=llm, progress_callback=on_scene_progress)

            # Update progress for basic structure parsing
            active_jobs[job_id]["progress"] = 18
            await manager.send_progress(job_id, {
                "type": "progress",
                "stage": "basic_parsing",
                "progress": 18,
                "message": "正在解析剧本基础结构..."
            })
        else:
            parser = TXTScriptParser()
            # Update progress for non-LLM parsing
            active_jobs[job_id]["progress"] = 15
            await manager.send_progress(job_id, {
                "type": "progress",
                "stage": "basic_parsing",
                "progress": 15,
                "message": "正在解析剧本结构 (无 LLM 增强)..."
            })

        # Parse the script (await if async parser)
        logger.info(f"Parsing TXT script for job {job_id}")

        # Send parsing start message
        await manager.send_progress(job_id, {
            "type": "progress",
            "stage": "parsing",
            "progress": 22,
            "message": "正在分割场景并提取角色..."
        })

        if use_llm_enhancement:
            # LLMEnhancedParser.parse() is async
            script = await parser.parse(file_path)
        else:
            # TXTScriptParser.parse() is sync
            script = parser.parse(file_path)

        # Send finalizing message
        await manager.send_progress(job_id, {
            "type": "progress",
            "stage": "finalizing",
            "progress": 92,
            "message": "正在保存解析结果..."
        })

        # Save parsed JSON
        json_path = Path(file_path).with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(script.model_dump(), f, ensure_ascii=False, indent=2)

        # Calculate statistics
        scene_count = len(script.scenes)
        all_characters = set()
        key_event_count = 0
        for scene in script.scenes:
            all_characters.update(scene.characters)
            if scene.key_events:
                key_event_count += len(scene.key_events)

        # Update job with parsed script
        active_jobs[job_id]["status"] = "parsed"
        active_jobs[job_id]["parsed_script_path"] = str(json_path)
        active_jobs[job_id]["script"] = script
        active_jobs[job_id]["progress"] = 100

        # Send completion message with detailed stats
        await manager.send_progress(job_id, {
            "type": "complete",
            "stage": "parsed",
            "progress": 100,
            "message": f"解析完成! 共 {scene_count} 个场景，{len(all_characters)} 个角色，{key_event_count} 个关键事件",
            "scene_count": scene_count,
            "character_count": len(all_characters),
            "key_event_count": key_event_count
        })

        logger.info(f"Parsing complete for job {job_id}: {scene_count} scenes, {len(all_characters)} characters")

    except Exception as e:
        logger.error(f"Parsing failed for job {job_id}: {e}", exc_info=True)
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)
        await manager.send_progress(job_id, {
            "type": "error",
            "message": f"解析失败: {str(e)}"
        })


async def run_analysis_job(
    job_id: str,
    script: Script,
    provider: str,
    model: Optional[str],
    export_markdown: bool,
    no_cache: bool = False,
    script_content: Optional[str] = None
):
    """
    Run analysis pipeline in background and update job status.

    Args:
        job_id: Unique job identifier
        script: Validated script object
        provider: LLM provider
        model: Optional model name
        export_markdown: Whether to export Markdown report
        no_cache: If True, skip cache lookup and force fresh analysis
        script_content: Original script content for cache hash computation
    """
    start_time = time.time()
    api_calls = 0
    from_cache = False

    try:
        # Compute content hash for cache lookup
        content_hash = None
        effective_model = model or "default"

        if script_content:
            content_hash = cache_manager.compute_hash(script_content)
        else:
            # Fallback: hash the JSON representation
            content_hash = cache_manager.compute_hash(json.dumps(script.model_dump(), ensure_ascii=False, sort_keys=True))

        # Check cache if not disabled
        if not no_cache and content_hash:
            await manager.send_progress(job_id, {
                "type": "progress",
                "stage": "cache_check",
                "progress": 5,
                "message": "Checking cache..."
            })

            cached = cache_manager.get(content_hash, provider, effective_model)
            if cached and cached.stage1_result and cached.stage2_result and cached.stage3_result:
                logger.info(f"Cache HIT for job {job_id}")
                from_cache = True

                # Restore results from cache
                active_jobs[job_id]["status"] = "completed"
                active_jobs[job_id]["progress"] = 100
                active_jobs[job_id]["completed_at"] = datetime.now().isoformat()
                active_jobs[job_id]["from_cache"] = True
                active_jobs[job_id]["cache_id"] = cached.id
                active_jobs[job_id]["result"] = {
                    "discoverer_output": json.loads(cached.stage1_result),
                    "auditor_output": json.loads(cached.stage2_result),
                    "modifier_output": json.loads(cached.stage3_result),
                    "errors": [],
                    "retry_count": 0,
                    "metrics": {"from_cache": True, "cache_id": cached.id}
                }

                await manager.send_progress(job_id, {
                    "type": "complete",
                    "progress": 100,
                    "message": "Analysis loaded from cache!",
                    "result_url": f"/results/{job_id}",
                    "from_cache": True
                })

                logger.info(f"Job {job_id} completed from cache (id={cached.id})")
                return

        # No cache hit - run fresh analysis
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

        # Run pipeline (synchronous, but in background task so won't block main loop)
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

        # Prepare export result data
        export_result = {
            "tccs": final_state["discoverer_output"].tccs if final_state["discoverer_output"] else [],
            "rankings": final_state["auditor_output"].rankings if final_state["auditor_output"] else None,
            "modifications": {
                "modifications": final_state["modifier_output"].modification_log if final_state["modifier_output"] else [],
                "total_issues": final_state["modifier_output"].validation.total_issues if final_state["modifier_output"] else 0,
            },
            "_metrics": final_state.get("_metrics", {}),
            "script_json": final_state.get("script_json", {}),
        }
        script_name = active_jobs[job_id]["filename"].replace(".json", "").replace(".txt", "")

        # Export Markdown if requested
        if export_markdown:
            try:
                md_exporter = MarkdownExporter()
                markdown_path = UPLOAD_DIR / f"{job_id}_report.md"
                md_exporter.export(export_result, markdown_path, script_name=script_name)

                active_jobs[job_id]["markdown_path"] = str(markdown_path)
                logger.info(f"Markdown report generated: {markdown_path}")

            except Exception as e:
                logger.error(f"Failed to generate Markdown report: {e}")

        # Always generate TXT report as well
        try:
            txt_exporter = TXTExporter()
            txt_path = UPLOAD_DIR / f"{job_id}_report.txt"
            txt_exporter.export(export_result, txt_path, script_name=script_name)

            active_jobs[job_id]["txt_path"] = str(txt_path)
            logger.info(f"TXT report generated: {txt_path}")

        except Exception as e:
            logger.error(f"Failed to generate TXT report: {e}")

        # Calculate processing time and API calls
        processing_time = time.time() - start_time
        metrics = final_state.get("_metrics", {})
        api_calls = metrics.get("total_llm_calls", 3)  # Default to 3 (one per stage)

        # Build result dict
        result_dict = {
            "discoverer_output": final_state["discoverer_output"].model_dump() if final_state["discoverer_output"] else None,
            "auditor_output": final_state["auditor_output"].model_dump() if final_state["auditor_output"] else None,
            "modifier_output": final_state["modifier_output"].model_dump() if final_state["modifier_output"] else None,
            "errors": final_state["errors"],
            "retry_count": final_state["retry_count"],
            "metrics": final_state.get("_metrics", {})
        }

        # Save to cache (only if all three stages completed successfully)
        all_stages_completed = (
            result_dict["discoverer_output"] is not None and
            result_dict["auditor_output"] is not None and
            result_dict["modifier_output"] is not None
        )
        if content_hash and all_stages_completed:
            try:
                tcc_count = len(final_state["discoverer_output"].tccs) if final_state["discoverer_output"] else 0
                cache_id = cache_manager.set(
                    content_hash=content_hash,
                    script_name=script_name,
                    provider=provider,
                    model=effective_model,
                    parsed_script=script.model_dump(),
                    stage1_result=result_dict["discoverer_output"],
                    stage2_result=result_dict["auditor_output"],
                    stage3_result=result_dict["modifier_output"],
                    scene_count=len(script.scenes),
                    tcc_count=tcc_count,
                    processing_time=processing_time,
                    api_calls=api_calls,
                )
                active_jobs[job_id]["cache_id"] = cache_id
                logger.info(f"Analysis cached: id={cache_id}, hash={content_hash[:8]}...")
            except Exception as e:
                logger.error(f"Failed to cache analysis result: {e}")
        elif content_hash and not all_stages_completed:
            logger.warning(f"Analysis not cached: incomplete results (Stage 1: {result_dict['discoverer_output'] is not None}, Stage 2: {result_dict['auditor_output'] is not None}, Stage 3: {result_dict['modifier_output'] is not None})")

        # Analysis complete
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = 100
        active_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        active_jobs[job_id]["from_cache"] = False
        active_jobs[job_id]["result"] = result_dict

        await manager.send_progress(job_id, {
            "type": "complete",
            "progress": 100,
            "message": "Analysis completed successfully!",
            "result_url": f"/results/{job_id}",
            "from_cache": False
        })

        logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s")

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
