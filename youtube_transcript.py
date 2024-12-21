from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import yt_dlp
import os
import re

def get_video_id(youtube_url):
    """
    Extracts the video ID from the given YouTube URL.
    :param youtube_url: URL of the YouTube video
    :return: Video ID as a string
    """
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", youtube_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL format. Unable to extract video ID.")
