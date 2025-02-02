# from fastapi import APIRouter, HTTPException, Query, Depends, Request
# from fastapi.responses import FileResponse
# from src.limiter import limiter
# import yt_dlp
# import os
# from datetime import datetime
# from typing import Optional, List
# from loguru import logger
# from src.schemas.youtube_schema import YoutubeVideoMetadata, VideoThumbnail, VideoFormat


# #  Initialize FastAPI Router
# router = APIRouter()


# #  Create Downloads Directory if Not Exists
# DOWNLOADS_FOLDER = "./downloads"
# os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)


# def get_video_info(url: str) -> dict:
#     """Fetch YouTube video metadata using yt-dlp."""
#     try:
#         ydl_opts = {"quiet": True, "no_warnings": True}
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             return ydl.extract_info(url, download=False)
#     except Exception as e:
#         logger.error(f"Failed to fetch video info: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch video metadata.")


# def format_video_metadata(raw_info: dict) -> YoutubeVideoMetadata:
#     """Formats and structures the YouTube video metadata to match the schema."""
#     try:
#         # Convert Thumbnails
#         thumbnails = [
#             VideoThumbnail(
#                 url=thumb.get("url"),
#                 width=thumb.get("width"),
#                 height=thumb.get("height"),
#             )
#             for thumb in raw_info.get("thumbnails", [])
#         ]

#         # Extract Available Video Qualities
#         video_qualities = []
#         seen_qualities = set()

#         for fmt in raw_info.get("formats", []):
#             if fmt.get("height") and fmt.get("vcodec") != "none":  # Ensure it's a video format
#                 quality = f"{fmt['height']}p"
                
#                 if quality not in seen_qualities:
#                     seen_qualities.add(quality)

#                     video_qualities.append(VideoFormat(
#                         format_id=fmt.get("format_id", ""),
#                         url=fmt.get("url", ""),
#                         ext=fmt.get("ext", "mp4"),
#                         resolution=quality,
#                         filesize=fmt.get("filesize"),  # File size in bytes
#                         fps=fmt.get("fps"),
#                         width=fmt.get("width"),
#                         height=fmt.get("height"),
#                     ))

#         # Sort resolutions from highest to lowest (e.g., 1080p -> 720p -> 480p)
#         video_qualities.sort(key=lambda x: int(x.resolution[:-1]), reverse=True)

#         # Format Metadata According to Schema
#         metadata = YoutubeVideoMetadata(
#             id=raw_info.get("id", ""),
#             title=raw_info.get("title", "Unknown Title"),
#             description=raw_info.get("description", ""),
#             upload_date=datetime.strptime(
#                 raw_info.get("upload_date", "19700101"), "%Y%m%d"
#             ).strftime("%Y-%m-%d"),
#             duration=raw_info.get("duration", 0),
#             view_count=raw_info.get("view_count", 0),
#             like_count=raw_info.get("like_count"),
#             thumbnail=raw_info.get("thumbnail"),
#             thumbnails=thumbnails,
#             formats=video_qualities,
#         )

#         return metadata

#     except Exception as e:
#         logger.error(f"Error formatting metadata: {e}")
#         raise HTTPException(status_code=500, detail="Error formatting video metadata.")


# @router.get("/video/metadata", 
            
#             # dependencies=[Depends(limiter.limit("10/minute"))]
            
#             )
# async def youtube_metadata(url: str) -> YoutubeVideoMetadata:
#     """Fetch and return YouTube video metadata in the correct schema format."""
#     raw_info = get_video_info(url)
#     # return raw_info
#     if not raw_info:
#         raise HTTPException(status_code=404, detail="Video not found")

#     formatted_metadata = format_video_metadata(raw_info)
#     return formatted_metadata



# # def download_youtube_video_backend(url: str, quality: str) -> str:
# #     """Download YouTube video with fallback to highest available quality."""
# #     ydl_opts = {
# #         "outtmpl": f"{DOWNLOADS_FOLDER}/%(title)s.%(ext)s",
# #         "merge_output_format": "mp4",
# #     }

# #     try:
# #         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
# #             info_dict = ydl.extract_info(url, download=False)

# #             available_formats = sorted(
# #                 [
# #                     (f["format_id"], f["height"])
# #                     for f in info_dict["formats"]
# #                     if f.get("height") and f.get("acodec") != "none"
# #                 ],
# #                 key=lambda x: x[1],
# #                 reverse=True,
# #             )

# #             if not available_formats:
# #                 raise HTTPException(status_code=404, detail="No suitable video formats available")

# #             matching_format = next((f for f in available_formats if f[1] == int(quality)), None)

# #             if not matching_format:
# #                 matching_format = available_formats[0]
# #                 logger.warning(f"Requested quality {quality}p not available. Falling back to {matching_format[1]}p.")

# #             ydl_opts["format"] = matching_format[0]
# #             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
# #                 ydl.download([url])

# #             return ydl.prepare_filename(info_dict)

# #     except Exception as e:
# #         logger.error(f"Error downloading video: {e}")
# #         raise HTTPException(status_code=500, detail="Error downloading video.")


def cleanup_downloaded_file(file_path: str):
    """Deletes the downloaded video file after serving."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted downloaded file: {file_path}")
        else:
            logger.warning(f"Tried to delete file but it does not exist: {file_path}")
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {e}")


# @router.post("/video/download",
#             #   dependencies=[Depends(limiter.limit("10/minute"))]
#               )
# async def download_video(request: Request, url: str = Query(...), quality: str = Query("720")):
#     """Download and serve the YouTube video, then delete it from the server."""
#     file_path = download_youtube_video_backend(url, quality)

#     if not file_path:
#         raise HTTPException(status_code=404, detail="Video not found or failed to download.")

#     response = FileResponse(file_path, media_type="video/mp4", filename=os.path.basename(file_path))

#     #  Schedule cleanup after response
#     request.app.add_event_handler("shutdown", lambda: cleanup_downloaded_file(file_path))

#     return response







# def download_youtube_video_backend(url: str, quality: str) -> str:
#     """Download YouTube video with fallback to the closest available quality."""
#     ydl_opts = {
#         "outtmpl": f"{DOWNLOADS_FOLDER}/%(title)s.%(ext)s",
#         "merge_output_format": "mp4",
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info_dict = ydl.extract_info(url, download=False)

#             # Extract available formats with video
#             available_formats = sorted(
#                 [
#                     (f["format_id"], f["height"])
#                     for f in info_dict["formats"]
#                     if f.get("height") and f.get("vcodec") != "none"
#                 ],
#                 key=lambda x: x[1],  # Sort by height (resolution)
#                 reverse=True,  # Higher resolution first
#             )

#             if not available_formats:
#                 raise HTTPException(status_code=404, detail="No suitable video formats available.")

#             # Convert quality string (e.g., "720p") to integer for comparison
#             requested_height = int(quality.replace("p", ""))

#             # Find the exact quality match
#             matching_format = next((f for f in available_formats if f[1] == requested_height), None)

#             # If no exact match, find the closest available resolution
#             if not matching_format:
#                 closest_format = min(available_formats, key=lambda x: abs(x[1] - requested_height))
#                 logger.warning(f"Requested quality {quality} not available. Using {closest_format[1]}p instead.")
#                 matching_format = closest_format

#             # Set the chosen format
#             ydl_opts["format"] = matching_format[0]

#             # Download video
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 ydl.download([url])

#             return ydl.prepare_filename(info_dict)

#     except Exception as e:
#         logger.error(f"Error downloading video: {e}")
#         raise HTTPException(status_code=500, detail="Error downloading video.")



from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse
import yt_dlp
import os
import subprocess
from datetime import datetime
from typing import Optional, List
from loguru import logger
from src.schemas.youtube_schema import YoutubeVideoMetadata, VideoThumbnail, VideoFormat

router = APIRouter()

DOWNLOADS_FOLDER = "./downloads"
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
COOKIES_PATH = os.path.join(ROOT_DIR, "cookies.txt")

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        logger.info(f"FFmpeg Version: {result.stdout.splitlines()[0]}")
        return True
    except Exception as e:
        logger.error("FFmpeg is not installed. Install FFmpeg to process videos.")
        return False

if not check_ffmpeg():
    raise RuntimeError("FFmpeg is required but not found. Please install it.")

def get_video_info(url: str) -> dict:
    """Fetch YouTube video metadata using yt-dlp."""
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "cookies": COOKIES_PATH, }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as e:
        logger.error(f"Failed to fetch video info: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch video metadata.")

def format_video_metadata(raw_info: dict) -> YoutubeVideoMetadata:
    """Format YouTube metadata into a structured schema."""
    thumbnails = [
        VideoThumbnail(
            url=thumb.get("url"),
            width=thumb.get("width"),
            height=thumb.get("height"),
        )
        for thumb in raw_info.get("thumbnails", [])
    ]
    video_qualities = []
    seen_qualities = set()
    for fmt in raw_info.get("formats", []):
        if fmt.get("height") and fmt.get("vcodec") != "none":
            quality = f"{fmt['height']}p"
            if quality not in seen_qualities:
                seen_qualities.add(quality)
                video_qualities.append(VideoFormat(
                    format_id=fmt.get("format_id", ""),
                    url=fmt.get("url", ""),
                    ext=fmt.get("ext", "mp4"),
                    resolution=quality,
                    filesize=fmt.get("filesize"),
                    fps=fmt.get("fps"),
                    width=fmt.get("width"),
                    height=fmt.get("height"),
                ))
    video_qualities.sort(key=lambda x: int(x.resolution[:-1]), reverse=True)
    return YoutubeVideoMetadata(
        id=raw_info.get("id", ""),
        title=raw_info.get("title", "Unknown Title"),
        description=raw_info.get("description", ""),
        upload_date=datetime.strptime(raw_info.get("upload_date", "19700101"), "%Y%m%d").strftime("%Y-%m-%d"),
        duration=raw_info.get("duration", 0),
        view_count=raw_info.get("view_count", 0),
        like_count=raw_info.get("like_count"),
        thumbnail=raw_info.get("thumbnail"),
        thumbnails=thumbnails,
        formats=video_qualities,
    )

@router.get("/video/metadata")
async def youtube_metadata(url: str) -> YoutubeVideoMetadata:
    """Fetch and return YouTube video metadata."""
    raw_info = get_video_info(url)
    return format_video_metadata(raw_info)

def download_youtube_video_backend(url: str, quality: str) -> str:
    """
    Download YouTube video with yt-dlp automatically merging video & audio.
    The final file will be named after the video title.
    """
    # First, get video metadata to determine the title.
    info = get_video_info(url)
    title = info.get("title", "video")
    # It is advisable to sanitize the title if needed (yt-dlp with restrict_filenames can help)
    final_output = f"{title}.mp4"
    output_path = os.path.join(DOWNLOADS_FOLDER, final_output)

    ydl_opts = {
        "format": f"bv*[height={quality}]+ba/b",
        "paths": {"home": DOWNLOADS_FOLDER},
        # Use the title-based template so the merged file is named after the video title.
        "outtmpl": os.path.join("%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
        # Optionally, restrict filenames to ASCII-compatible characters:
        "restrict_filenames": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if os.path.exists(output_path):
            return output_path
        else:
            raise HTTPException(status_code=404, detail="Video download failed.")
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise HTTPException(status_code=500, detail="Error downloading video.")

@router.post("/video/download")
async def download_video(request: Request,
                        #  background_tasks:BackgroundTask,
                           url: str = Query(...), quality: str = Query("720")):
    """Download and serve the YouTube video, then delete it after serving."""
    file_path = download_youtube_video_backend(url, quality)
    if not file_path:
        raise HTTPException(status_code=404, detail="Video not found or failed to download.")

    response = FileResponse(file_path, media_type="video/mp4", filename=os.path.basename(file_path))
    request.app.add_event_handler("shutdown", lambda: os.remove(file_path))
    return response