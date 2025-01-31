from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class VideoThumbnail(BaseModel):
    """Represents a YouTube video thumbnail."""
    url: HttpUrl
    width: Optional[int] = None
    height: Optional[int] = None

class VideoFormat(BaseModel):
    """Represents an available format for a YouTube video."""
    format_id: str
    url: HttpUrl
    ext: Optional[str] = "mp4"  # Default to mp4 if not provided
    resolution: Optional[str] = None
    filesize: Optional[int] = None  # File size in bytes
    fps: Optional[float] = None  # Frame rate
    width: Optional[int] = None
    height: Optional[int] = None

class VideoMetadata(BaseModel):
    """Represents metadata for a YouTube video."""
    id: str
    title: str
    description: Optional[str] = None
    upload_date: str
    duration: int  # Duration in seconds
    view_count: int
    like_count: Optional[int] = None
    thumbnail: Optional[HttpUrl] = None
    thumbnails: List[VideoThumbnail] = []
    formats: List[VideoFormat] = []

class YoutubeDownloadForm(BaseModel):
    """Schema for requesting a YouTube video download."""
    url: HttpUrl
    quality: str  # Example: "1080p", "720p", etc.
