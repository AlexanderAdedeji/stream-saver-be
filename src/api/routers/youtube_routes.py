import os
import uuid
import yt_dlp
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import FileResponse
from slowapi.util import get_remote_address
from slowapi import Limiter
from src.commonLib.utils.logger_config import logger
from src.commonLib.utils.utils import utils
from src.schemas.stream_saver_schema import VideoMetadata


from src.limiter import limiter

router = APIRouter()

#  Ensure the downloads folder exists
DOWNLOADS_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

def get_video_info(url: str):
    """Fetch YouTube video metadata using yt_dlp"""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def clean_video_info(raw_info):
    """Structure YouTube video metadata in a readable format."""
    seen_qualities = set()
    video_qualities = []

    for fmt in raw_info.get("formats", []):
        if fmt.get("height") and fmt.get("vcodec") != "none":
            quality = f"{fmt['height']}p"
            if quality not in seen_qualities:
                seen_qualities.add(quality)
                size_in_mb = (
                    f"{round(fmt['filesize'] / (1024 * 1024), 1)} MB"
                    if fmt.get("filesize")
                    else "Unknown"
                )
                video_qualities.append({
                    "quality": quality,
                    "format": fmt.get("ext", "mp4"),
                    "size": size_in_mb,
                })

    video_qualities.sort(key=lambda x: int(x["quality"][:-1]), reverse=True)

    def format_large_number(num):
        if not num:
            return "Unknown"
        if num >= 1_000_000:
            return f"{num // 1_000_000}M"
        elif num >= 1_000:
            return f"{num // 1_000}K"
        return str(num)

    return {
        "title": raw_info.get("title", "Unknown Title"),
        "thumbnail": raw_info.get("thumbnail", ""),
        "duration": utils.seconds_to_hms(raw_info.get("duration", 0)),  # Convert duration to HH:MM:SS
        "views": format_large_number(raw_info.get("view_count", 0)),
        "publishDate": datetime.strptime(
            raw_info.get("upload_date", "19700101"), "%Y%m%d"
        ).strftime("%Y-%m-%d"),
        "likes": format_large_number(raw_info.get("like_count", 0)),
        "qualities": video_qualities,
    }

@router.get("/video/metadata", dependencies=[Depends(limiter.limit("10/minute"))])
async def youtube_metadata(url: str, request: Request):
    """Fetch YouTube video metadata with rate-limiting."""
    trace_id = str(uuid.uuid4())
    try:
        raw_info = get_video_info(url)
        if not raw_info:
            raise HTTPException(status_code=404, detail="Video not found")
        cleaned_info = clean_video_info(raw_info)

        logger.info(f"[TRACE {trace_id}] 🎬 Video metadata retrieved: {url}")
        return cleaned_info
    except Exception as e:
        logger.error(f"[TRACE {trace_id}]  Error fetching YouTube metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to process YouTube video")

def download_youtube_video_backend(url: str, quality: str) -> str:
    """Download YouTube video with fallback to highest available quality."""
    ydl_opts = {
        "outtmpl": f"{DOWNLOADS_FOLDER}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            available_formats = sorted(
                [
                    (f["format_id"], f["height"])
                    for f in info_dict["formats"]
                    if f.get("height") and f.get("acodec") != "none"
                ],
                key=lambda x: x[1],
                reverse=True,
            )

            if not available_formats:
                raise HTTPException(status_code=404, detail="No suitable video formats available")

            matching_format = next((f for f in available_formats if f[1] == int(quality)), None)
            if not matching_format:
                matching_format = available_formats[0]  # Fallback to best quality
                logger.warning(f"Requested quality {quality}p not available. Falling back to {matching_format[1]}p.")

            ydl_opts["format"] = matching_format[0]
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return ydl.prepare_filename(info_dict)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")

@router.post("/video/download", dependencies=[Depends(limiter.limit("5/minute"))])
async def download_video(request: Request,url: str = Query(...),   quality: str = Query("720")):
    """Download a YouTube video with rate-limiting."""
    trace_id = str(uuid.uuid4())
    try:
        file_path = download_youtube_video_backend(url, quality)

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Video not found or failed to download.")

        logger.info(f"[TRACE {trace_id}]  Video downloaded: {file_path}")
        return FileResponse(file_path, media_type="video/mp4", filename=os.path.basename(file_path))

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"[TRACE {trace_id}]  Error processing YouTube download: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
