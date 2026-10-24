"""
Auralis - Interactive Multi-Loop Feedback Server & Live Dry-Run Review
Provides a real-time web UI where:
- Tracks are audited 1 by 1 in dry-run mode.
- Users can approve (✅ Tick) or reject (❌ Cross) with corrections.
- Rejections & corrections are stored directly in `engine_human_feedback.json` & `engine_decision_cache.json`.
- Engine continuously reads feedback, refines classifications, and computes live accuracy rate!
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.master_dry_run_engine import MasterDryRunEngine, load_decision_cache, save_decision_cache

logger = logging.getLogger("auralis.feedback_server")

FEEDBACK_FILE = os.path.join(PROJECT_ROOT, "engine_human_feedback.json")

def load_human_feedback() -> Dict[str, Any]:
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_human_feedback(data: Dict[str, Any]) -> None:
    try:
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save human feedback: {e}")

# Global in-memory state
app = FastAPI(title="Auralis Multi-Loop Feedback Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = MasterDryRunEngine(
    root_paths=[r"D:\Songs\organized", r"D:\Songs\unorganized"],
    min_folder_threshold=3
)
DRY_RUN_CACHE_FILE = os.path.join(PROJECT_ROOT, "cached_dry_run_results.json")
cached_run_result = None

def get_or_run_dry_run(force_refresh: bool = False):
    global cached_run_result
    if not force_refresh and cached_run_result is not None:
        return cached_run_result

    if not force_refresh and os.path.exists(DRY_RUN_CACHE_FILE):
        try:
            with open(DRY_RUN_CACHE_FILE, "r", encoding="utf-8") as f:
                cached_run_result = json.load(f)
                return cached_run_result
        except Exception as e:
            logger.warning(f"Failed to read cached dry run results: {e}")

    logger.info("Executing fresh dry-run pass across audio library...")
    cached_run_result = engine.execute_dry_run()
    try:
        with open(DRY_RUN_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cached_run_result, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to cache dry run results: {e}")
    return cached_run_result

@app.get("/api/status")
def get_status():
    res = get_or_run_dry_run()
    fb = load_human_feedback()
    tracks = res["tracks"]
    
    total = len(tracks)
    approved_count = sum(1 for t in tracks if fb.get(t["audio_hash"], {}).get("status") == "approved")
    rejected_count = sum(1 for t in tracks if fb.get(t["audio_hash"], {}).get("status") == "rejected")
    reviewed_count = approved_count + rejected_count
    accuracy = round((approved_count / reviewed_count * 100), 1) if reviewed_count > 0 else 100.0

    return {
        "total_scanned": total,
        "unique_tracks": res["summary"]["unique_tracks"],
        "duplicates": res["summary"]["duplicate_tracks"],
        "generic_resolved": res["summary"]["generic_resolved"],
        "approved": approved_count,
        "rejected": rejected_count,
        "accuracy_rate": accuracy,
        "languages": res["summary"]["languages"],
        "folder_types": res["summary"]["folder_types"]
    }

@app.get("/api/tracks")
def get_tracks(page: int = 1, page_size: int = 50, lang: Optional[str] = None, filter_type: Optional[str] = None, search: Optional[str] = None):
    res = get_or_run_dry_run()
    fb = load_human_feedback()
    tracks = res["tracks"]

    filtered = []
    for t in tracks:
        h = t["audio_hash"]
        user_fb = fb.get(h, {})
        t_copy = dict(t)
        t_copy["user_feedback"] = user_fb.get("status", "pending") # pending, approved, rejected
        t_copy["user_correction"] = user_fb.get("correction", "")

        # Language filter
        if lang and t["language"] != lang:
            continue
        # Filter type
        if filter_type == "generic" and not t["is_generic"]:
            continue
        if filter_type == "duplicate" and not t["is_duplicate"]:
            continue
        if filter_type == "pending" and t_copy["user_feedback"] != "pending":
            continue
        if filter_type == "rejected" and t_copy["user_feedback"] != "rejected":
            continue
        # Search
        if search:
            s_low = search.lower()
            text = f"{t['title']} {t['artist']} {t['category']} {t['source_path']}".lower()
            if s_low not in text:
                continue

        filtered.append(t_copy)

    total_filtered = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = filtered[start:end]

    return {
        "total": total_filtered,
        "page": page,
        "page_size": page_size,
        "tracks": page_data
    }

@app.post("/api/feedback")
def submit_feedback(payload: Dict[str, Any] = Body(...)):
    """
    Submits user tick (approve) or cross (reject) with optional correction.
    Updates human feedback file and persists into decision cache for next engine loop.
    """
    audio_hash = payload.get("audio_hash")
    status = payload.get("status") # "approved" or "rejected"
    correction = payload.get("correction", {})

    if not audio_hash or status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid payload")

    fb = load_human_feedback()
    fb[audio_hash] = {
        "status": status,
        "correction": correction,
        "timestamp": os.path.getmtime(FEEDBACK_FILE) if os.path.exists(FEEDBACK_FILE) else 0
    }
    save_human_feedback(fb)

    # If rejected with correction, update the persistent decision cache immediately!
    if status == "rejected" and correction:
        cache = load_decision_cache()
        cache[audio_hash] = {
            "language": correction.get("language"),
            "category": correction.get("category"),
            "artist": correction.get("artist"),
            "album": correction.get("album"),
            "title": correction.get("title"),
            "confidence": 1.0,
            "decision_source": "Human Correction (100% Ground Truth)"
        }
        save_decision_cache(cache)

    return {"status": "success", "audio_hash": audio_hash, "review_status": status}

@app.post("/api/re-run")
def trigger_rerun():
    """Triggers an instantaneous re-run of the Master Dry-Run Engine incorporating all new feedback!"""
    global cached_run_result
    logger.info("Re-running master engine dry-run loop with updated feedback & decision cache...")
    engine.decision_cache = load_decision_cache()
    cached_run_result = engine.execute_dry_run()
    return {"status": "re_run_complete", "metrics": get_status()}

from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

@app.get("/api/stream")
def stream_audio(path: str, alt_path: Optional[str] = None):
    """Streams the raw audio file to the HTML5 browser player for instant sampling."""
    actual_path = None
    for p in [path, alt_path]:
        if p and os.path.exists(p):
            actual_path = p
            break

    if not actual_path:
        raise HTTPException(status_code=404, detail="Audio file not found on disk")
    ext = os.path.splitext(actual_path)[1].lower()
    media_type = "audio/mpeg" if ext == ".mp3" else ("audio/x-ms-wma" if ext == ".wma" else "audio/octet-stream")
    return FileResponse(actual_path, media_type=media_type)

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(PROJECT_ROOT, "src", "gui", "feedback_dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Feedback dashboard HTML not found.</h1>"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="info")
