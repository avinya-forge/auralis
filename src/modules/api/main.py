import time
import uuid
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

app = FastAPI(title="Auralis Edge-Cloud Gateway API")

security = HTTPBearer()


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "valid-jwt-token":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return credentials.credentials


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


class MetadataCreate(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    year: Optional[int] = None


class MetadataResponse(BaseModel):
    id: str
    title: str
    artist: str
    album: Optional[str] = None
    year: Optional[int] = None


# Mock database
_mock_db: Dict[str, Any] = {}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/metadata", response_model=MetadataResponse)
async def create_metadata(metadata: MetadataCreate):
    new_id = str(uuid.uuid4())
    record = metadata.model_dump()
    record["id"] = new_id
    _mock_db[new_id] = record
    return record


@app.get("/metadata/{item_id}", response_model=MetadataResponse)
async def get_metadata(item_id: str):
    if item_id not in _mock_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return _mock_db[item_id]


@app.get("/sync/audio/{file_id}")
async def stream_audio_file(file_id: str, token: str = Depends(verify_jwt)):
    """
    Stream audio file sync endpoint with JWT authentication.
    """

    # Mock audio streaming
    def iterfile():
        # Yield fake audio bytes
        yield b"fake "
        yield b"audio "
        yield b"data"

    return StreamingResponse(iterfile(), media_type="audio/mpeg")
