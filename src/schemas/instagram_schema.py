from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class InstagramUser(BaseModel):
    """Represents an Instagram user."""
    id: str
    username: str
    full_name: Optional[str] = None
    profile_pic_url: Optional[HttpUrl] = None
    is_verified: Optional[bool] = False

class InstagramMedia(BaseModel):
    """Represents an Instagram media item (image or video)."""
    type: str  # "image" or "video"
    url: HttpUrl
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None  # Only for videos
    thumbnail_url: Optional[HttpUrl] = None
    has_audio: Optional[bool] = None  # Only for videos
    accessibility_caption: Optional[str] = None

class InstagramLocation(BaseModel):
    """Represents the location tag on an Instagram post."""
    id: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class InstagramPost(BaseModel):
    """Represents a full Instagram post response."""
    id: str
    shortcode: str
    caption: Optional[str] = None
    timestamp: datetime
    like_count: Optional[int] = None
    view_count: Optional[int] = None  # Only for videos
    comment_count: Optional[int] = None
    media_count: Optional[int] = None  # Only for carousel posts
    media: List[InstagramMedia]
    owner: InstagramUser
    location: Optional[InstagramLocation] = None
    tags: List[str] = []
    mentions: List[str] = []
    is_video: bool
    is_sponsored: Optional[bool] = False
    product_type: Optional[str] = None  # "feed", "reel", "story"
    music: Optional[str] = None  # Only for Reels

class InstagramMediaItem(BaseModel):
    """Represents an item in an Instagram carousel post."""
    index: int
    url: HttpUrl
    type: str  # "image" or "video"
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None

class InstagramPostResponse(BaseModel):
    """Represents the API response for an Instagram post."""
    id: str
    shortcode: str
    type: str  # "reel", "single_image", "single_video", "carousel"
    caption: Optional[str] = None
    timestamp: datetime
    like_count: Optional[int] = None
    view_count: Optional[int] = None  # Only for videos/reels
    media: List[InstagramMediaItem]
    owner_username: str
    owner_profile_pic: Optional[HttpUrl] = None
    music: Optional[str] = None  # Only for Reels
    is_sponsored: bool = False