from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import yt_dlp
import os
import re

def get_video_id(youtube_url):
    """
    Extracts the video ID from the given YouTube URL.
    """
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", youtube_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL format. Unable to extract video ID.")

def fetch_video_title(youtube_url):
    """
    Fetch the video title using yt-dlp.
    """
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info.get("title", "Unknown_Title").replace(" ", "_").replace("|", "_")
    except Exception as e:
        return f"Error_Fetching_Title_{e}"