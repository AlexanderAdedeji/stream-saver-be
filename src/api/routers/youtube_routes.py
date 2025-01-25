from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from loguru import logger
from src.commonLib.lib import utils
import yt_dlp
import instaloader
from datetime import datetime
from typing import List, Optional
from pydantic import HttpUrl
from src.schemas.stream_saver_schema import InstagramPostResponse, VideoMetadata

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()



# Include router in the app
app.include_router(router)
def get_video_info(url: str):
    """Fetch YouTube video information using yt_dlp"""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# def clean_video_info(raw_info):
#     """Clean and structure YouTube video information"""
#     return {
#         "id": raw_info.get("id"),
#         "title": raw_info.get("title"),
#         "description": raw_info.get("description"),
#         "upload_date": raw_info.get("upload_date"),
#         "duration": raw_info.get("duration"),
#         # "view_count": raw_info.get("view_count"),
#         # "like_count": raw_info.get("like_count"),
#         "thumbnail": raw_info.get("thumbnail"),
#         "thumbnails": raw_info.get("thumbnails", []),
#         "formats": [
#             {
#                 "format_id": fmt.get("format_id"),
#                 "url": fmt.get("url"),
#                 "ext": fmt.get("ext"),
#                 "resolution": fmt.get("resolution"),
#                 "filesize": fmt.get("filesize"),
#                 "fps": fmt.get("fps"),
#                 "width": fmt.get("width"),
#                 "height": fmt.get("height"),
#             }
#             for fmt in raw_info.get("formats", [])
#             if fmt.get("url")
#         ],
#     }




def clean_video_info(raw_info):
    """Clean and structure YouTube video information"""
    # Extract video qualities (height in pixels)
    seen_qualities = set()
    video_qualities = []
    
    for fmt in raw_info.get('formats', []):
        if fmt.get('height') and fmt.get('vcodec') != 'none':
            quality = f"{fmt['height']}p"
            if quality not in seen_qualities:
                seen_qualities.add(quality)
                video_qualities.append(quality)
    
    # Sort qualities descending (1440p > 1080p > 720p etc.)
    video_qualities.sort(key=lambda x: int(x[:-1]), reverse=True)

    return {
        "id":raw_info.get("title"),
        "title": raw_info.get("title"),
        "description": raw_info.get("description"),
        "thumbnail": raw_info.get("thumbnail"),
        "duration": utils.seconds_to_hms(raw_info.get("duration")),
        "upload_date": raw_info.get("upload_date"),
        "video_qualities": video_qualities,
    }


@router.get("/video/metadata")
async def youtube_metadata(url: str):
    """Fetch YouTube video metadata"""
    try:
        raw_info = get_video_info(url)
        if not raw_info:
            raise HTTPException(status_code=404, detail="Video not found")

        cleaned_info = clean_video_info(raw_info)
        # return VideoMetadata(**cleaned_info)
        return cleaned_info
    except Exception as e:
        logger.error(f"Error fetching YouTube metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to process YouTube video")

@router.post("/youtube/download")
async def download_youtube_video(url: str = Query(..., description="URL of the YouTube video")):
    """Download YouTube video"""
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
            return {"download_url": info["url"]}
    except Exception as e:
        logger.error(f"Error downloading YouTube video: {e}")
        raise HTTPException(status_code=500, detail="Failed to process video download")

