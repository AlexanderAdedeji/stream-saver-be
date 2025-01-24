from fastapi import APIRouter, HTTPException, Query
from pytube import YouTube
from fastapi.responses import FileResponse
import os

router = APIRouter()



@router.post("/yotube_download")
async def download_youtube_video(url: str = Query(..., description="URL of the YouTube video")):
    try:
        # Create a YouTube object
        yt = YouTube(url)

        # Select the highest resolution stream
        stream = yt.streams.get_highest_resolution()

        # Temporary file location
        file_path = f"./downloads/{stream.default_filename}"
        print(file_path)
        
        # Ensure the downloads directory exists
        os.makedirs("./downloads", exist_ok=True)
        
        # Download the video
        stream.download(output_path="./downloads")

        return FileResponse(file_path, filename=stream.default_filename)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")