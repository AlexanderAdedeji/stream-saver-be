from fastapi import FastAPI, HTTPException, Depends, status, Query, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import re
import os
import requests
from typing import Optional

# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

# Initialize FastAPI app
router = APIRouter()

# # Rate limiting configuration
# limiter = Limiter(key_func=get_remote_address)
# router.state.limiter = limiter
# router.add_exception_handler(RateLimitExceeded, lambda _, exc: JSONResponse(
#     status_code=429,
#     content={"detail": "Too many requests"}
# ))


# Configuration
FACEBOOK_API_VERSION = "v22.0"
DEFAULT_FIELDS = "id,message,created_time,from,likes.limit(0).summary(true),comments.limit(0).summary(true),attachments,permalink_url,engagement"


class FacebookPostRequest(BaseModel):
    url: str
    access_token: str = Query(
        ..., description="Facebook access token with required permissions"
    )
    fields: Optional[str] = Query(
        DEFAULT_FIELDS, description="Graph API fields to return"
    )


class PostAuthor(BaseModel):
    id: str
    name: str
    category: Optional[str]


class MediaAttachment(BaseModel):
    type: str
    url: Optional[str]
    title: Optional[str]
    description: Optional[str]


class PostEngagement(BaseModel):
    reaction_count: int
    comment_count: int
    share_count: int


class FacebookPostResponse(BaseModel):
    post_id: str
    message: Optional[str]
    created_time: datetime
    author: PostAuthor
    attachments: list[MediaAttachment]
    permalink_url: str
    engagement: PostEngagement


def extract_post_id(url: str) -> str:
    patterns = [
        r"(?:https?:\/\/)?(?:www\.|m\.)?facebook\.com\/.*\/(\d+)\/?",
        r"(?:https?:\/\/)?(?:www\.|m\.)?facebook\.com\/.*\/posts\/(\d+)\/?",
        r"(?:https?:\/\/)?(?:www\.|m\.)?facebook\.com\/.*\/videos\/(\d+)\/?",
        r"(?:https?:\/\/)?(?:www\.|m\.)?facebook\.com\/photo\/\?fbid=(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise HTTPException(status_code=400, detail="Invalid Facebook post URL format")


@router.post("/api/facebook/metadata", response_model=FacebookPostResponse)
async def get_facebook_post_metadata(
    request: FacebookPostRequest):
    """
    Retrieve metadata for a Facebook post using its URL

    Required permissions:
    - For public Page posts: pages_manage_posts
    - For user posts: user_posts
    """
    try:
        # Extract post ID from URL
        post_id = extract_post_id(request.url)

        # Build Graph API URL
        api_url = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/{post_id}"

        params = {"access_token": request.access_token, "fields": request.fields}

        # Make API request
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Transform response
        return {
            "post_id": data["id"],
            "message": data.get("message"),
            "created_time": datetime.fromisoformat(data["created_time"]),
            "author": {
                "id": data["from"]["id"],
                "name": data["from"]["name"],
                "category": data["from"].get("category"),
            },
            "attachments": [
                {
                    "type": attachment["type"],
                    "url": attachment.get("url"),
                    "title": attachment.get("title"),
                    "description": attachment.get("description"),
                }
                for attachment in data.get("attachments", {}).get("data", [])
            ],
            "permalink_url": data["permalink_url"],
            "engagement": {
                "reaction_count": data["engagement"]["reaction_count"],
                "comment_count": data["engagement"]["comment_count"],
                "share_count": data["engagement"]["share_count"],
            },
        }

    except requests.HTTPError as e:
        error_data = e.response.json()
        detail = f"Facebook API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
        raise HTTPException(status_code=e.response.status_code, detail=detail)

    except KeyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Missing expected data in Facebook API response: {str(e)}",
        )
