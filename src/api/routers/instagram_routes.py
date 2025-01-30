import json
from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, StreamingResponse
import requests
from loguru import logger
import yt_dlp
import instaloader
from datetime import datetime
from typing import List, Optional
from pydantic import HttpUrl
from src.schemas.stream_saver_schema import InstagramPostResponse, VideoMetadata

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

# Helper Functions


def get_owner_details(post: instaloader.Post) -> dict:
    """Extract owner details from the post's node."""
    try:
        owner_data = post._node["owner"]
        return {
            "id": owner_data.get("id"),
            "username": owner_data.get("username"),
            "full_name": owner_data.get("full_name"),
            "profile_pic_url": owner_data.get("profile_pic_url"),
            "is_verified": owner_data.get("is_verified", False),
        }
    except KeyError as e:
        logger.error(f"Owner details not found: {e}")
        return {
            "id": None,
            "username": None,
            "full_name": None,
            "profile_pic_url": None,
            "is_verified": False,
        }


def extract_shortcode(url: str) -> str:
    """Extract shortcode from Instagram URL"""
    url = url.strip("/")
    for pattern in ["/reel/", "/p/", "/tv/"]:
        if pattern in url:
            return url.split(pattern)[-1].split("/")[0]
    return url.split("/")[-1]


def get_instagram_post(url: str) -> Optional[instaloader.Post]:
    """Fetch Instagram post using instaloader"""
    try:
        L = instaloader.Instaloader()
        shortcode = extract_shortcode(url)
        return instaloader.Post.from_shortcode(L.context, shortcode)
    except Exception as e:
        logger.error(f"Error fetching Instagram post: {e}")
        return None


def classify_post(post: instaloader.Post) -> str:
    """Determine post type"""
    if post.typename == "GraphReel":
        return "reel"
    if post.mediacount > 1:
        return "carousel"
    return "video" if post.is_video else "image"

def process_media(post: instaloader.Post) -> List[dict]:
    """Process media for all post types (single post, video, carousel)."""
    media = []
    
    if post._node.get("edge_sidecar_to_children"):  # Carousel posts
        for index, child in enumerate(post._node.get("edge_sidecar_to_children").get("edges", [])):
            node = child.get("node", {})
            media_type = "video" if node.get("is_video") else "image"
            media_url = node.get("video_url") if node.get("is_video") else node.get("display_resources")[-1].get("src")
            
            if not media_url:
                logger.error(f"Missing media URL for index {index}")
                continue  # Skip any media that lacks a URL
            
            media.append({
                "url": media_url,
                "index": index,
                "type": media_type  # Ensure "type" key is always included
            })

    else:  # Single image or video post
        media_type = "video" if post._node.get("is_video") else "image"
        media_url = post._node.get("video_url") if post._node.get("is_video") else post._node.get("display_url")

        if not media_url:
            logger.error("Missing media URL for single post")
            raise HTTPException(status_code=500, detail="Failed to extract media URL")

        media.append({
            "index": 0,
            "url": media_url,
            "type": media_type  # Ensure "type" key is included
        })

    logger.info(f"Processed media: {json.dumps(media, indent=2)}")  # Log output for debugging
    return media

# def process_media(post: instaloader.Post) -> List[dict]:
#     """Process media for all post types"""
#     if post._node.get("edge_sidecar_to_children"):  # Carousel posts

#         media = []
#         for child in post._node.get("edge_sidecar_to_children").get("edges"):
#             media_type = "video"  if child.get("node").get("is_video") else "image"
#             index= child.get("node").get("id")
#             media_url = child.get("node").get("video_url") if child.get("node").get("is_video") else child.get("node").get("display_resources")[-1].get("src")
    

#             media.append({"url": media_url, "index": index, "type":media_type})
#         return media

#         return post._node["edge_sidecar_to_children"]["edges"]
#     else:  # Single image or video post
#         media = [{"index": 1, 
         
#          "url":  post._node.get("video_url")
#                     if post._node.get("is_video")
#                     else post._node.get("display_url")
         
#                 }]
#         return media
#         return post._node
#         return [
#             {
#                 "index": 0,
#                 "url": (
#                     post._node.get("video_url")
#                     if post._node.get("is_video")
#                     else post._post._node.get("display_url")
#                 ),
#                 "type": post._node.get("type"),
#                 "width": post._node.get("dimensions", {}).get("width"),
#                 "height": post._node.get("dimensions", {}).get("height"),
#             }
#         ]


def get_music_info(post: instaloader.Post) -> Optional[str]:
    """Extract music information for Reels"""
    try:
        if post.typename == "GraphReel" and post.music:
            return f"{post.music.title} - {post.music.artist}"
    except AttributeError:
        pass
    return None


@router.get("/metadata")
async def instagram_metadata(url: str):
    """Fetch Instagram post metadata"""
    try:
        if "instagram.com" not in url:
            raise HTTPException(status_code=400, detail="Invalid Instagram URL")

        # Fetch post data
        post = get_instagram_post(url)

        if not post:
            raise HTTPException(status_code=404, detail="Post not found or private")

        # Extract owner details
        owner_details = get_owner_details(post)

        # Prepare response data
        response_data = {
            "id": post._node["id"],
            "shortcode": post._node["shortcode"],
            "type": classify_post(post),
            "caption": post._node.get("edge_media_to_caption", {})
            .get("edges", [{}])[0]
            .get("node", {})
            .get("text"),
            "timestamp": datetime.fromtimestamp(post._node["taken_at_timestamp"]),
            "like_count": post._node.get("edge_media_preview_like", {}).get("count"),
            "view_count": (
                post._node.get("video_view_count")
                if post._node.get("is_video")
                else None
            ),
            "media": process_media(post),
            "username": owner_details["username"],
            "user_avatar": owner_details["profile_pic_url"],
            "music": get_music_info(post),
            "is_sponsored": post._node.get("is_ad", False),
        }

        return response_data

        # return InstagramPostResponse(**response_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching Instagram metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Instagram post")


@router.get("/download")
async def download_instagram_media(
    url: str = Query(..., description="Instagram post URL"),
    media_index: int = Query(0, description="Index of media in carousel"),
):
    """Download Instagram media with correct file extension."""
    try:
        post = get_instagram_post(url)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        media = process_media(post)

        if media_index >= len(media):
            raise HTTPException(
                status_code=400, detail=f"Invalid media index {media_index}, only {len(media)} items available."
            )

        media_url = media[media_index]["url"]
        media_type = media[media_index]["type"]

        if not media_url:
            raise HTTPException(status_code=500, detail="Failed to retrieve media URL")

        # Get file extension based on media type
        file_extension = "mp4" if media_type == "video" else "jpg"

        # Fetch the media
        response = requests.get(media_url, stream=True)
        content_type = response.headers.get("Content-Type", "application/octet-stream")

        return StreamingResponse(
            response.iter_content(chunk_size=1024 * 1024),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="instagram_media_{media_index}.{file_extension}"'
            },
        )

    except Exception as e:
        logger.error(f"Error processing Instagram download: {e}")
        raise HTTPException(status_code=500, detail="Failed to process download")

