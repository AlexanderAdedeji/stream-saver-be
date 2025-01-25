from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Union
from datetime import datetime

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




class InstagramUser(BaseModel):
    id: str
    username: str
    full_name: Optional[str] = None
    profile_pic_url: Optional[HttpUrl] = None
    is_verified: Optional[bool] = False

class InstagramMedia(BaseModel):
    type: str  # "image", "video", "carousel"
    url: HttpUrl
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None  # Video duration in seconds
    thumbnail_url: Optional[HttpUrl] = None
    has_audio: Optional[bool] = None  # For videos
    accessibility_caption: Optional[str] = None
    is_published: Optional[bool] = True

class InstagramLocation(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class InstagramPost(BaseModel):
    id: str
    shortcode: str
    caption: Optional[str] = None
    timestamp: datetime
    like_count: Optional[int] = None
    view_count: Optional[int] = None  # For videos
    comment_count: Optional[int] = None
    media_count: Optional[int] = None  # For carousels
    media: List[InstagramMedia]
    owner: InstagramUser
    location: Optional[InstagramLocation] = None
    tags: List[str] = []
    mentions: List[str] = []
    is_video: bool
    is_sponsored: Optional[bool] = False
    product_type: Optional[str] = None  # "feed", "reel", "story", etc.
    music: Optional[str] = None  # For Reels
    video_dash_manifest: Optional[str] = None  # For video formats
    example_response: dict = {
        "id": "1234567890",
        "shortcode": "CxYzAbC123",
        "caption": "Check out this amazing view! 🌄",
        "timestamp": "2023-10-01T12:34:56",
        "like_count": 1500,
        "view_count": 50000,
        "comment_count": 42,
        "media_count": 1,
        "media": [
            {
                "type": "video",
                "url": "https://instagram.fabc123.cdn/video.mp4",
                "width": 1080,
                "height": 1920,
                "duration": 15.5,
                "thumbnail_url": "https://instagram.fabc123.cdn/thumbnail.jpg",
                "has_audio": True,
                "accessibility_caption": "Video by Example User"
            }
        ],
        "owner": {
            "id": "987654321",
            "username": "example_user",
            "full_name": "Example User",
            "profile_pic_url": "https://instagram.fabc123.cdn/profile.jpg",
            "is_verified": False
        },
        "location": {
            "name": "Grand Canyon",
            "slug": "grand-canyon-national-park",
            "lat": 36.106965,
            "lng": -112.112997
        },
        "tags": ["nature", "landscape"],
        "mentions": ["@photographer"],
        "is_video": True,
        "product_type": "reel",
        "music": "Popular Song - Artist"
    }


class InstagramMediaItem(BaseModel):
    index: int
    url: HttpUrl
    type: str  # "image" or "video"
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None

class InstagramPostResponse(BaseModel):
    id: str
    shortcode: str
    type: str  # "reel", "single_image", "single_video", "carousel"
    caption: Optional[str] = None
    timestamp: datetime
    like_count: Optional[int] = None
    view_count: Optional[int] = None  # For videos/reels
    media: List[InstagramMediaItem]
    owner_username: str
    owner_profile_pic: Optional[HttpUrl] = None
    music: Optional[str] = None  # For Reels
    is_sponsored: bool = False



class YoutubeDownloadForm(BaseModel):
    url: str
    quality: str  # "1080p", "720p", "480p", "