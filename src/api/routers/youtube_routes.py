import json
import requests
import instaloader
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Request, Depends
from fastapi.responses import StreamingResponse
from src.commonLib.utils.logger_config import logger
from src.schemas.stream_saver_schema import InstagramPostResponse

router = APIRouter()

# Helper Functions
def extract_shortcode(url: str) -> str:
    """Extract shortcode from Instagram URL"""
    url = url.strip("/")
    for pattern in ["/reel/", "/p/", "/tv/"]:
        if pattern in url:
            return url.split(pattern)[-1].split("/")[0]
    return url.split("/")[-1]

def get_instagram_post(url: str) -> instaloader.Post:
    """Fetch Instagram post using instaloader"""
    try:
        loader = instaloader.Instaloader()
        shortcode = extract_shortcode(url)
        return instaloader.Post.from_shortcode(loader.context, shortcode)
    except Exception as e:
        logger.error(f" Error fetching Instagram post: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Instagram post")

def classify_post(post: instaloader.Post) -> str:
    """Determine post type"""
    if post.typename == "GraphReel":
        return "reel"
    if post.mediacount > 1:
        return "carousel"
    return "video" if post.is_video else "image"

def process_media(post: instaloader.Post) -> list:
    """Process media for all post types (single post, video, carousel)."""
    media = []
    
    if post._node.get("edge_sidecar_to_children"):  # Carousel posts
        for index, child in enumerate(post._node["edge_sidecar_to_children"]["edges"]):
            node = child["node"]
            media_type = "video" if node.get("is_video") else "image"
            media_url = node.get("video_url") if node.get("is_video") else node["display_resources"][-1]["src"]

            if not media_url:
                logger.warning(f"⚠️ Missing media URL for index {index}")
                continue  

            media.append({"url": media_url, "index": index, "type": media_type})

    else:  # Single image or video post
        media_type = "video" if post._node["is_video"] else "image"
        media_url = post._node.get("video_url") if post._node["is_video"] else post._node["display_url"]

        if not media_url:
            logger.error(" Missing media URL for single post")
            raise HTTPException(status_code=500, detail="Failed to extract media URL")

        media.append({"index": 0, "url": media_url, "type": media_type})

    logger.info(f" Processed media: {json.dumps(media, indent=2)}")
    return media

def get_owner_details(post: instaloader.Post) -> dict:
    """Extract owner details from the post's node."""
    try:
        owner = post._node["owner"]
        return {
            "id": owner.get("id"),
            "username": owner.get("username"),
            "full_name": owner.get("full_name"),
            "profile_pic_url": owner.get("profile_pic_url"),
            "is_verified": owner.get("is_verified", False),
        }
    except KeyError:
        return {"id": None, "username": None, "full_name": None, "profile_pic_url": None, "is_verified": False}

def get_music_info(post: instaloader.Post) -> str:
    """Extract music info from Instagram Reels."""
    try:
        return f"{post.music.title} - {post.music.artist}" if post.typename == "GraphReel" and post.music else None
    except AttributeError:
        return None

#  Instagram Metadata Route
@router.get("/metadata")
async def instagram_metadata(url: str, request: Request):
    """Fetch Instagram post metadata"""
    trace_id = str(uuid.uuid4())

    if "instagram.com" not in url:
        raise HTTPException(status_code=400, detail="Invalid Instagram URL")

    post = get_instagram_post(url)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found or private")

    metadata = {
        "id": post._node["id"],
        "shortcode": post._node["shortcode"],
        "type": classify_post(post),
        "caption": post._node.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text"),
        "timestamp": datetime.fromtimestamp(post._node["taken_at_timestamp"]),
        "like_count": post._node.get("edge_media_preview_like", {}).get("count"),
        "view_count": post._node.get("video_view_count") if post._node.get("is_video") else None,
        "media": process_media(post),
        "username": get_owner_details(post)["username"],
        "user_avatar": get_owner_details(post)["profile_pic_url"],
        "music": get_music_info(post),
        "is_sponsored": post._node.get("is_ad", False),
    }

    logger.info(f"[TRACE {trace_id}]  Instagram metadata retrieved successfully")
    return metadata

#  Instagram Download Route
@router.get("/download")
async def download_instagram_media(
    background_tasks: BackgroundTasks,
      request: Request,
    url: str = Query(..., description="Instagram post URL"),
    media_index: int = Query(0, description="Index of media in carousel")
  
):
    """Download Instagram media with correct file extension."""
    trace_id = str(uuid.uuid4())

    post = get_instagram_post(url)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    media = process_media(post)
    if media_index >= len(media):
        raise HTTPException(status_code=400, detail=f"Invalid media index {media_index}, only {len(media)} items available.")

    media_url = media[media_index]["url"]
    media_type = media[media_index]["type"]
    file_extension = "mp4" if media_type == "video" else "jpg"

    logger.info(f"[TRACE {trace_id}] 📥 Downloading Instagram {media_type}")

    # Fetch media from Instagram
    response = requests.get(media_url, stream=True)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch media from Instagram")

    #  Schedule file deletion after sending
    temp_file = f"temp_instagram_media_{media_index}.{file_extension}"
    with open(temp_file, "wb") as f:
        for chunk in response.iter_content(1024 * 1024):
            f.write(chunk)

    def delete_temp_file():
        if os.path.exists(temp_file):
            os.remove(temp_file)
            logger.info(f"🗑️ Deleted temp file: {temp_file}")

    background_tasks.add_task(delete_temp_file)

    return StreamingResponse(
        open(temp_file, "rb"),
        media_type=f"video/{file_extension}" if media_type == "video" else f"image/{file_extension}",
        headers={"Content-Disposition": f'attachment; filename="{temp_file}"'}
    )
