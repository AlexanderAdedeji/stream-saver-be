from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, StreamingResponse
from loguru import logger
from src.commonLib.lib.utils import utils
import yt_dlp
import instaloader
from datetime import datetime
from typing import List, Optional
from pydantic import HttpUrl

import os
from src.schemas.stream_saver_schema import (
    InstagramPostResponse,
    VideoMetadata,
    YoutubeDownloadForm,
)

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




def clean_video_info(raw_info):
    """Clean and structure YouTube video information"""
    # Extract video qualities with details
    seen_qualities = set()
    video_qualities = []

    for fmt in raw_info.get("formats", []):
        if fmt.get("height") and fmt.get("vcodec") != "none":
            quality = f"{fmt['height']}p"
            if quality not in seen_qualities:
                seen_qualities.add(quality)

                # Calculate file size in MB if available
                size_in_mb = (
                    f"{round(fmt['filesize'] / (1024 * 1024), 1)} MB"
                    if fmt.get("filesize")
                    else "Unknown"
                )

                video_qualities.append({
                    "quality": quality,
                    "format": fmt.get("ext", "mp4"),  # Default to mp4 if not provided
                    "size": size_in_mb,
                })

    # Sort qualities descending (1440p > 1080p > 720p etc.)
    video_qualities.sort(key=lambda x: int(x["quality"][:-1]), reverse=True)

    # Convert views and likes into readable formats
    def format_large_number(num):
        if not num:
            return "Unknown"
        if num >= 1_000_000:
            return f"{num // 1_000_000}M"
        elif num >= 1_000:
            return f"{num // 1_000}K"
        return str(num)

    # Format the response to match the required structure
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


# @router.post("/video/download")
# async def download_youtube_video(url: str, quality: str):
#     """Download YouTube video in specified quality"""
#     try:
#         # Validate quality format
#         if not quality.endswith("p") or not quality[:-1].isdigit():
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid quality format: {quality}. Use format like '720p'",
#             )

#         # Extract available formats
#         ydl_opts = {
#             "quiet": True,
#             "no_warnings": True,
#         }

#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=False)
#             formats = info.get("formats", [])

#             # Filter formats by the desired quality
#             # target_height = int(video.quality[:-1])
#             # selected_format = None
#             # for fmt in formats:
#             #     if fmt.get("height") == target_height and fmt.get("acodec") != "none":
#             #         selected_format = fmt
#             #         break
#             # return formats
#             # if not selected_format:
#             #     raise HTTPException(
#             #         status_code=404,
#             #         detail=f"Requested quality {video.quality} not available. Please choose from available qualities.",
#             #     )

#             # # Prepare download options
#             # ydl_opts.update(
#             #     {
#             #         "format": selected_format["format_id"],
#             #         "outtmpl": f"{info['title']}.%(ext)s",
#             #     }
#             # )

#             # Download the video

#         ydl.download([url])

#         filename = ydl.prepare_filename(info)

#         def file_iterator(file_path: str):
#             with open(file_path, "rb") as f:
#                 yield from f

#         response = StreamingResponse(
#             file_iterator(filename),
#             media_type="video/mp4",
#         )
#         response.headers["Content-Disposition"] = (
#             f'attachment; filename="{os.path.basename(filename)}"'
#         )

#         return response

#         # return {
#         #     "message": f"Video '{info['title']}' downloaded successfully in {quality} quality.",
#         #     "title": info["title"],
#         #     "duration": info["duration"],
#         #     "thumbnail": info["thumbnail"],
#         #     "available_qualities": list(
#         #         set(fmt.get("height") for fmt in formats if fmt.get("height"))
#         #     ),
#         # }

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Video download failed: {str(e)}")

import httpx

@router.post("/video/download")
async def download_youtube_video(url: str, quality: str):
    """Download YouTube video in specified quality"""
    try:
        # Validate quality format
        if not quality.endswith("p") or not quality[:-1].isdigit():
            raise HTTPException(400, "Invalid quality format")

        # Get video info
        ydl_opts = {"quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
            
            # Find best format
            height = int(quality[:-1])
            selected_format = next(
                (f for f in formats 
                 if f.get('height') == height 
                 and f.get('vcodec') != 'none'),
                None
            )

            if not selected_format:
                raise HTTPException(404, "Quality not available")

            # Get direct download URL
            video_url = selected_format['url']

        # Stream the video content
        async def stream_video():
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", video_url) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk

        # Set download headers
        filename = f"{info['title']}_{quality}.mp4"
        return StreamingResponse(
            stream_video(),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "video/mp4"
            }
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, f"Download failed: {str(e)}")