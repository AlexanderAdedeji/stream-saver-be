from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, StreamingResponse,FileResponse
import requests
from loguru import logger
from src.commonLib.lib.utils import utils
import yt_dlp


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

router = APIRouter()



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





# def download_youtube_video_backend(url: str, quality: str) -> str:
#     ydl_opts = {
#         "outtmpl": "./downloads/%(title)s.%(ext)s",  # Output path
#     }
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             # Fetch available formats
#             info_dict = ydl.extract_info(url, download=False)  # Fetch metadata
#             available_formats = [
#                 (f["format_id"], f["height"])
#                 for f in info_dict["formats"]
#                 if f.get("height") and f.get("acodec") != "none"  # Ensure both video and audio
#             ]

#             # Check if the requested quality is available
#             matching_format = next(
#                 (f for f in available_formats if f[1] == int(quality)), None
#             )

#             if not matching_format:
#                 raise HTTPException(
#                     status_code=404,
#                     detail=f"Requested quality {quality}p not available. Available qualities: {[f[1] for f in available_formats]}",
#                 )

#             # Update options to download the matching format
#             ydl_opts["format"] = matching_format[0]
#             ydl = yt_dlp.YoutubeDL(ydl_opts)
#             ydl.download([url])

#             # Prepare the filename
#             return ydl.prepare_filename(info_dict)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")


def download_youtube_video_backend(url: str, quality: str) -> str:
    """Download YouTube video with fallback to highest available quality."""

    ydl_opts = {
        "outtmpl": "./downloads/%(title)s.%(ext)s",  # Output path
        "merge_output_format": "mp4",  # Ensure output is always MP4
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ✅ Fetch available formats
            info_dict = ydl.extract_info(url, download=False)  
            
            available_formats = sorted(
                [
                    (f["format_id"], f["height"])
                    for f in info_dict["formats"]
                    if f.get("height") and f.get("acodec") != "none"  # Ensure video has audio
                ],
                key=lambda x: x[1],  # Sort by height
                reverse=True,  # Highest quality first
            )

            if not available_formats:
                raise HTTPException(status_code=404, detail="No suitable video formats available")

            # ✅ Check if requested quality is available
            matching_format = next((f for f in available_formats if f[1] == int(quality)), None)

            if not matching_format:
                # ✅ Fallback to the highest available quality
                matching_format = available_formats[0]
                fallback_quality = matching_format[1]
                logger.warning(f"Requested quality {quality}p not available. Falling back to {fallback_quality}p.")

            # ✅ Update options to download the best-matched format
            ydl_opts["format"] = matching_format[0]
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # ✅ Prepare filename
            return ydl.prepare_filename(info_dict)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")


@router.post("/video/download")
async def download_video(url: str = Query(...), quality: str = Query("720")):
    try:
        file_path = download_youtube_video_backend(url, quality)

        if not file_path:
            raise HTTPException(status_code=404, detail="Video not found or failed to download.")

        return FileResponse(file_path, media_type="video/mp4", filename=file_path.split("/")[-1])

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing YouTube download: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
