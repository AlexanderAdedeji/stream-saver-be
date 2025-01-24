from fastapi import APIRouter, HTTPException, Query
from src.schemas.stream_saver_schema import VideoMetadata
import yt_dlp

import os

router = APIRouter()

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()





def get_video_info(url):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return _clean_info(info)  # Clean the raw data

def _clean_info(raw_info):
    # Clean thumbnails
    cleaned_thumbnails = []
    for thumb in raw_info.get("thumbnails", []):
        cleaned_thumbnails.append({
            "url": thumb.get("url"),
            "width": thumb.get("width"),
            "height": thumb.get("height"),
            "id": thumb.get("id"),
        })

    # Clean formats (filter out invalid entries)
    cleaned_formats = []
    for fmt in raw_info.get("formats", []):
        if not fmt.get("url"):  # Skip formats without a URL
            continue
        cleaned_formats.append({
            "format_id": fmt.get("format_id"),
            "url": fmt.get("url"),
            "ext": fmt.get("ext"),
            "resolution": fmt.get("resolution"),
            "filesize": fmt.get("filesize"),
            "fps": fmt.get("fps"),
            "width": fmt.get("width"),
            "height": fmt.get("height"),
        })

    # Construct metadata
    return {
        "id": raw_info.get("id"),
        "title": raw_info.get("title"),
        "description": raw_info.get("description"),
        "upload_date": raw_info.get("upload_date"),
        "duration": raw_info.get("duration"),
        "view_count": raw_info.get("view_count"),
        "like_count": raw_info.get("like_count"),
        "thumbnail": raw_info.get("thumbnail"),
        "thumbnails": cleaned_thumbnails,
        "formats": cleaned_formats,
    }

@router.get("/youtube/video/metadata")
async def get_metadata(url: str):
    try:
        info = get_video_info(url)
        if not info:
            raise HTTPException(status_code=404, detail="Video not found")

        # Extract relevant metadata
        metadata = {
            "id": info.get("id"),
            "title": info.get("title"),
            "description": info.get("description"),
            "upload_date": info.get("upload_date"),
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "thumbnail": info.get("thumbnail"),
            "thumbnails": info.get("thumbnails", []),
            "formats": info.get("formats", []),
        }

    
        return VideoMetadata(**metadata)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/yotube_download")
async def download_youtube_video(url: str = Query(..., description="URL of the YouTube video")):
    try:
        # Create a YouTube object
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
            # ydl.download([url])

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")