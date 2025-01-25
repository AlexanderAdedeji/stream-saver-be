from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
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
        owner_data = post._node['owner']
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
    """Process media for all post types"""
    if post._node.get('edge_sidecar_to_children'):  # Carousel posts
        return [
            {
                "index": idx,
                "url": node.get('video_url') if node.get('is_video') else node['display_url'],
                "type": "video" if node.get('is_video') else "image",
                "duration": node.get('video_duration'),
                "width": node.get('dimensions', {}).get('width'),
                "height": node.get('dimensions', {}).get('height'),
            }
            for idx, node in enumerate(post._node['edge_sidecar_to_children']['edges'])
        ]
    else:  # Single image or video post
        return [
            {
                "index": 0,
                "url": post._node.get('video_url') if post._node.get('is_video') else post._node['display_url'],
                "type": "video" if post._node.get('is_video') else "image",
                "duration": post._node.get('video_duration'),
                "width": post._node.get('dimensions', {}).get('width'),
                "height": post._node.get('dimensions', {}).get('height'),
            }
        ]



def get_music_info(post: instaloader.Post) -> Optional[str]:
    """Extract music information for Reels"""
    try:
        if post.typename == "GraphReel" and post.music:
            return f"{post.music.title} - {post.music.artist}"
    except AttributeError:
        pass
    return None





@router.get("/instagram/metadata", response_model=InstagramPostResponse)
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
            "id": post._node['id'],
            "shortcode": post._node['shortcode'],
            "type": classify_post(post),
            "caption": post._node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text'),
            "timestamp": datetime.fromtimestamp(post._node['taken_at_timestamp']),
            "like_count": post._node.get('edge_media_preview_like', {}).get('count'),
            "view_count": post._node.get('video_view_count') if post._node.get('is_video') else None,
            "media": process_media(post),
            "owner_username": owner_details["username"],
            "owner_profile_pic": owner_details["profile_pic_url"],
            "music": get_music_info(post),
            "is_sponsored": post._node.get('is_ad', False),
        }

        return InstagramPostResponse(**response_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching Instagram metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Instagram post")




@router.get("/instagram/download")
async def download_instagram_media(url: str, media_index: int = 0):
    """Redirect to downloadable Instagram media URL"""
    try:
        post = get_instagram_post(url)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        media = process_media(post)
        if media_index >= len(media):
            raise HTTPException(status_code=400, detail="Invalid media index")

        return RedirectResponse(media[media_index]["url"])
    except Exception as e:
        logger.error(f"Error processing Instagram download: {e}")
        raise HTTPException(status_code=500, detail="Failed to process download")


