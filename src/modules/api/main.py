import asyncio
from typing import AsyncGenerator, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.utils.perf.latency_logger import LatencyMiddleware

app = FastAPI(title="Auralis Edge-Cloud Gateway API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LatencyMiddleware)


class Metadata(BaseModel):
    id: Optional[int] = None
    title: str
    artist: str
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None


metadata_db: List[Metadata] = []


@app.get("/metadata", response_model=List[Metadata])
async def get_metadata() -> List[Metadata]:
    return metadata_db


@app.post("/metadata", response_model=Metadata)
async def create_metadata(item: Metadata) -> Metadata:
    item.id = len(metadata_db) + 1
    metadata_db.append(item)
    return item


@app.get("/sync/{file_id}")
async def sync_file(file_id: str) -> StreamingResponse:
    async def iterfile() -> AsyncGenerator[bytes, None]:
        for i in range(10):
            yield b"audio_chunk_data_" + bytes(str(i), "utf-8")
            await asyncio.sleep(0.1)  # Fix async blocking

    return StreamingResponse(iterfile(), media_type="audio/mpeg")
