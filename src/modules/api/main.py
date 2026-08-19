import logging
import os
import tempfile
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

app = FastAPI(title="Auralis Edge-Cloud Gateway API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

security = HTTPBearer()

SECRET_KEY = os.getenv("AURALIS_JWT_SECRET", "default-unsafe-secret-for-testing")
ALGORITHM = "HS256"


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(request: LoginRequest):
    # In a real application, credentials would be validated against a database.
    # We use environment variables for this edge gateway implementation.
    admin_user = os.getenv("AURALIS_ADMIN_USER", "admin")
    admin_pass = os.getenv("AURALIS_ADMIN_PASS", "password")

    if request.username == admin_user and request.password == admin_pass:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode = {"sub": request.username, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": encoded_jwt, "token_type": "bearer"}  # nosec B105
    raise HTTPException(status_code=401, detail="Invalid credentials")


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
@limiter.limit("100/minute")
async def health_check(request: Request):
    return {"status": "ok"}


@app.post("/metadata", response_model=MetadataResponse)
@limiter.limit("10/minute")
async def create_metadata(request: Request, metadata: MetadataCreate):
    new_id = str(uuid.uuid4())
    record = metadata.model_dump()
    record["id"] = new_id
    _mock_db[new_id] = record
    return record


@app.get("/metadata/{item_id}", response_model=MetadataResponse)
@limiter.limit("60/minute")
async def get_metadata(request: Request, item_id: str):
    if item_id not in _mock_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return _mock_db[item_id]


@app.get("/sync/audio/{file_id}")
@limiter.limit("20/minute")
async def stream_audio_file(request: Request, file_id: str, token: str = Depends(verify_jwt)):
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


@app.post("/upload/audio")
@limiter.limit("5/minute")
async def upload_audio(request: Request, file: UploadFile = File(...)):
    """Accept raw audio uploads from Edge clients."""
    try:
        file_content = await file.read()
        logger.info(f"Received audio upload: {file.filename}, size: {len(file_content)} bytes")

        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(temp_path, "wb") as f:
            f.write(file_content)

        return {
            "status": "success",
            "filename": file.filename,
            "message": "File received and queued for ingestion",
        }
    except Exception as e:
        logger.error(f"Error during file upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during upload")


@app.post("/sync/state")
@limiter.limit("30/minute")
def sync_client_state(request: Request, state_data: dict):
    """Sync state from Edge client to Cloud."""
    logger.info(f"Received state sync: {state_data}")
    return {"status": "success", "message": "State synchronized successfully"}
