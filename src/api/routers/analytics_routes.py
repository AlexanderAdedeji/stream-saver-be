from fastapi import APIRouter, Request
from src.commonLib.utils.logger_config import logger
from datetime import datetime
from src.models.visits_model import visits_collection

router = APIRouter()


@router.post("/track_visit")
async def track_visit(request: Request):
    """Logs frontend visits to the database."""
    client_host = request.client.host 
    user_agent = request.headers.get("User-Agent", "Unknown")
    referrer = request.headers.get("Referer", "Direct Visit") 

    visit_data = {
        "ip": client_host,
        "user_agent": user_agent,
        "referrer": referrer,
        "timestamp": datetime.now(),
    }

    # Store visit in MongoDB
    try:
        visits_collection.insert_one(visit_data)
        logger.info(f" Visitor logged: {visit_data}")
        return {"message": "Visit tracked successfully"}
    except Exception as e:
        logger.error(f" Error logging visitor: {e}")
        return {"error": "Failed to log visit"}