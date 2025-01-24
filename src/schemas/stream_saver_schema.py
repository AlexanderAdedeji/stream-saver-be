from pydantic import BaseModel, Field
from typing import List, Optional

class VideoThumbnail(BaseModel):
    url: str
    width: Optional[int] = None  # Handle missing width/height
    height: Optional[int] = None
    id: Optional[str] = None  # Add if needed

class VideoFormat(BaseModel):
    format_id: str
    url: str
    ext: Optional[str] = None  # Handle missing "ext"
    resolution: Optional[str] = None
    filesize: Optional[int] = None  # Handle missing filesize
    fps: Optional[float] = None  # Allow float for FPS
    width: Optional[int] = None  # Add if needed
    height: Optional[int] = None

class VideoMetadata(BaseModel):
    id: str
    title: str
    description: Optional[str] = None  # Handle missing description
    upload_date: str
    duration: int
    view_count: int
    like_count: Optional[int] = None  # Handle missing likes
    thumbnail: Optional[str] = None  # Handle missing thumbnail
    thumbnails: List[VideoThumbnail] = []
    formats: List[VideoFormat] = []