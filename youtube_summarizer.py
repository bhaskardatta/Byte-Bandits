#!/usr/bin/env python3

import os
import time
import re
import sys
import subprocess
from typing import List
import pysrt
import webvtt
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL_SUMMARIZE = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
API_URL_TRANSLATE = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-mul-en"
API_URL_PODCAST = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
API_TOKEN = "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"

if not API_TOKEN:
    raise ValueError("API Key Not Working!")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

def query_huggingface_api(api_url: str, payload: dict) -> str:
    response = requests.post(api_url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")
    response_json = response.json()
    if isinstance(response_json, list) and "translation_text" in response_json[0]:
        return response_json[0]["translation_text"]
    if isinstance(response_json, list) and "summary_text" in response_json[0]:
        return response_json[0]["summary_text"]
    if isinstance(response_json, list) and "generated_text" in response_json[0]:
        return response_json[0]["generated_text"]
    if "error" in response_json:
        raise Exception(f"API Error: {response_json['error']}")
    raise Exception(f"Unexpected API response: {response_json}")

def detect_language(text: str) -> str:
    try:
        from langdetect import detect
        return detect(text)
    except Exception as e:
        print(f"[WARNING] Language detection failed: {e}")
        return "unknown"

def chunk_text(text: str, max_chunk_size: int) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]

def summarize_text(text_path: str, max_length: int = 300, max_retries: int = 5, retry_interval: int = 20) -> str:
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()
    chunks = chunk_text(text, max_chunk_size=700)
    summaries = []
    for idx, chunk in enumerate(chunks):
        print(f"[INFO] Summarizing chunk {idx + 1}/{len(chunks)}...")
        payload = {
            "inputs": f"Summarize the following text into a detailed and structured summary, "
                      f"including an Introduction, Highlights, and a Conclusion:\n\n{chunk}",
            "parameters": {"max_new_tokens": max_length, "temperature": 0.7}
        }
        retries = 0
        while retries < max_retries:
            try:
                summary = query_huggingface_api(API_URL_SUMMARIZE, payload)
                summaries.append(summary)
                break
            except Exception as e:
                if "currently loading" in str(e) or "503" in str(e):
                    retries += 1
                    print(f"[WARNING] Model loading. Retrying in {retry_interval} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(retry_interval)
                else:
                    print(f"[ERROR] Summarization failed for chunk {idx + 1}: {e}")
                    break
        else:
            print(f"[ERROR] Max retries reached for chunk {idx + 1}. Skipping...")
    combined_summary = " ".join(summaries) if summaries else "Summarization failed for all chunks."
    summary_path = "summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(combined_summary)
    return summary_path


def generate_podcast_script(summary_path: str) -> str:
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_text = f.read()
    prompt = (
        "Convert the following summary into a podcast-style dialogue between two people, Alex and Chris. "
        "Each sentence should have an appropriate emotion tag like [thoughtful], [excited], or [curious]. "
        "Make it conversational, engaging, and focused. Avoid repetitive phrases or filler:\n\n"
        f"{summary_text}\n\n"
        "Output the podcast dialogue with emotion tags."
    )
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 1000, "temperature": 0.7}}
    try:
        podcast_script = query_huggingface_api(API_URL_PODCAST, payload)
    except Exception as e:
        print(f"[ERROR] Podcast script generation failed: {e}")
        podcast_script = "Podcast script could not be generated."
    podcast_path = "podcast_script.txt"
    with open(podcast_path, "w", encoding="utf-8") as f:
        f.write(podcast_script)
    return podcast_path

def extract_video_id(youtube_url: str) -> str:
    patterns = [
        r"v=([A-Za-z0-9_\-]{11})",
        r"youtu\.be/([A-Za-z0-9_\-]{11})",
        r"embed/([A-Za-z0-9_\-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return ""

def download_subtitles(youtube_url: str) -> str:
    video_id = extract_video_id(youtube_url)
    if not video_id:
        raise ValueError("[ERROR] Could not extract video ID from URL.")
    output_dir = "."
    command = [
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", "en",
        "--sub-format", "srt",
        "--skip-download",
        "--output", os.path.join(output_dir, "%(id)s.%(ext)s"),
        youtube_url
    ]
    print(f"[INFO] Running command: {' '.join(command)}")
    subprocess.run(command, check=True)
    possible_srt = os.path.join(output_dir, f"{video_id}.en.srt")
    possible_vtt = os.path.join(output_dir, f"{video_id}.en.vtt")
    if os.path.isfile(possible_srt):
        return os.path.abspath(possible_srt)
    elif os.path.isfile(possible_vtt):
        return os.path.abspath(possible_vtt)
    else:
        raise FileNotFoundError("[ERROR] No .srt or .vtt subtitles found after download.")
    
def convert_subtitles_to_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    full_text = []
    if ext == ".srt":
        subs = pysrt.open(file_path)
        for sub in subs:
            full_text.append(sub.text.replace("\n", " ").strip())
    elif ext == ".vtt":
        for caption in webvtt.read(file_path):
            full_text.append(caption.text.replace("\n", " ").strip())
    else:
        raise ValueError("[ERROR] Unsupported subtitle file format. Must be .srt or .vtt")
    text_path = os.path.splitext(file_path)[0] + ".txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(" ".join(full_text))
    return text_path

def translate_to_english_if_needed(file_path: str, max_retries: int = 5, retry_interval: int = 20, chunk_size: int = 300) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    detected_language = detect_language(text)
    if detected_language == "en":
        print("[INFO] Subtitles are already in English. Skipping translation.")
        return file_path

    print(f"[INFO] Detected language: {detected_language}. Translating to English...")
    chunks = chunk_text(text, max_chunk_size=chunk_size)
    translated_chunks = []
    for idx, chunk in enumerate(chunks):
        print(f"[INFO] Translating chunk {idx + 1}/{len(chunks)}...")
        payload = {
            "inputs": chunk,
            "parameters": {
                "truncation": "only_first",
                "max_new_tokens": 400
            }
        }
        retries = 0
        while retries < max_retries:
            try:
                translated_chunk = query_huggingface_api(API_URL_TRANSLATE, payload)
                translated_chunks.append(translated_chunk)
                break
            except Exception as e:
                if "currently loading" in str(e) or "503" in str(e):
                    retries += 1
                    print(f"[WARNING] Model loading. Retrying in {retry_interval} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(retry_interval)
                elif "Input is too long" in str(e):
                    print("[ERROR] Chunk size is still too large. Consider further reducing the chunk size.")
                    raise ValueError("Chunk size exceeds model limits. Adjust the chunk size.")
                else:
                    print(f"[ERROR] Translation failed for chunk {idx + 1}: {e}")
                    break
        else:
            print(f"[ERROR] Max retries reached for chunk {idx + 1}. Skipping...")
    translated_text = " ".join(translated_chunks)
    translated_path = os.path.splitext(file_path)[0] + "_english.txt"
    with open(translated_path, "w", encoding="utf-8") as f:
        f.write(translated_text)
    return translated_path

def cleanup_files(*file_paths):
    for file_path in file_paths:
        try:
            os.remove(file_path)
            print(f"[INFO] Deleted file: {file_path}")
        except Exception as e:
            print(f"[WARNING] Could not delete file {file_path}: {e}")

def main():
    if len(sys.argv) < 2:
        script_name = os.path.basename(__file__)
        print(f"Usage: python {script_name} <youtube_url>")
        sys.exit(1)
    youtube_url = sys.argv[1]
    try:
        subtitle_file = download_subtitles(youtube_url)
        text_file = convert_subtitles_to_text(subtitle_file)
        english_text_file = translate_to_english_if_needed(text_file)
        summary_file = summarize_text(english_text_file)
        podcast_file = generate_podcast_script(summary_file)
        cleanup_files(subtitle_file, text_file, english_text_file)
        print(f"[INFO] Summary saved to {summary_file}")
        print(f"[INFO] Podcast script saved to {podcast_file}")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
