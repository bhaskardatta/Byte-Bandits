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
import json  # Added for JSON operations

load_dotenv()

API_URL_TRANSLATE = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-mul-en"
API_URL_SUMMARY = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
API_URL_PODCAST = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
API_TOKEN = "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"  # Updated to fetch from .env

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
    if isinstance(response_json, list):
        return response_json[0].get("generated_text") or ""
    if "error" in response_json:
        raise Exception(f"API Error: {response_json['error']}")
    else:
        generated_text = response_json.get("generated_text", "")
    print(f"[DEBUG] Prompt sent: {payload.get('inputs')}")
    print(f"[DEBUG] Response received: {generated_text}")
    return generated_text

def remove_prompt_from_response(prompt: str, response: str) -> str:
    """
    Removes the prompt from the API response using regex.

    Args:
        prompt (str): The prompt that was sent to the API.
        response (str): The raw response received from the API.

    Returns:
        str: The cleaned summary without the prompt.
    """
    # Escape the prompt to treat any special regex characters literally
    escaped_prompt = re.escape(prompt)
    
    # Remove the prompt from the response
    cleaned_summary = re.sub(escaped_prompt, '', response, flags=re.DOTALL).strip()
    
    # Additionally, handle cases where the prompt might not be present or partially present
    if response.startswith(prompt):
        cleaned_summary = response[len(prompt):].strip()
    
    print(f"[DEBUG] Original Response: {response}")
    print(f"[DEBUG] Cleaned Summary: {cleaned_summary}")
    return cleaned_summary

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

def create_directory_structure():
    base_dir = os.path.join(os.getcwd(), "summaries")
    text_summary_dir = os.path.join(base_dir, "text_summary")
    podcast_summary_dir = os.path.join(base_dir, "podcast_summary")
    os.makedirs(text_summary_dir, exist_ok=True)
    os.makedirs(podcast_summary_dir, exist_ok=True)
    return text_summary_dir, podcast_summary_dir

def summarize_text(text_path: str, video_title: str, max_length: int = 300, max_retries: int = 5, retry_interval: int = 20) -> str:
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()
    chunks = chunk_text(text, max_chunk_size=700)
    summaries = []
    for idx, chunk in enumerate(chunks):
        print(f"[INFO] Summarizing chunk {idx + 1}/{len(chunks)}...")
        prompt = f"Summarize the following text into a high-quality, third-person, structured summary:\n\n{chunk}"
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": max_length, "temperature": 0.7},
            "echo": False
        }
        retries = 0
        while retries < max_retries:
            try:
                response = query_huggingface_api(API_URL_SUMMARY, payload)
                
                # Clean the response by removing the prompt
                cleaned_summary = remove_prompt_from_response(prompt, response)
                
                # Check if the cleaned summary is not empty
                if not cleaned_summary:
                    print(f"[WARNING] Received empty summary for chunk {idx + 1}.")
                    break
                
                summaries.append(cleaned_summary)
                break
            except Exception as e:
                if "currently loading" in str(e) or "503" in str(e):
                    retries += 1
                    print(f"[WARNING] Model loading. Retrying in {retry_interval} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(retry_interval)
                else:
                    print(f"[ERROR] Summarization failed for chunk {idx + 1}: {e}")
                    break
        if retries >= max_retries:
            print(f"[ERROR] Max retries reached for chunk {idx + 1}. Skipping...")
    combined_summary = "\n\n".join(summaries) if summaries else "Summarization failed for all chunks."
    text_summary_dir, _ = create_directory_structure()
    summary_path = os.path.join(text_summary_dir, f"{video_title}_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(combined_summary)
    return summary_path

def generate_podcast_script(summary_path: str, video_title: str) -> str:
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_text = f.read().strip()
        if not summary_text:
            raise ValueError("Summary text is empty. Cannot generate podcast script.")
        prompt = (
            "Transform the following text into a podcast-style dialogue between two people. "
            "Add an emotional tag at the beginning of each sentence to reflect the speaker's tone. "
            f"Here is the input:\n\n{summary_text}\n\nOutput a podcast dialogue with emotional annotations."
        )
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 1000, "temperature": 0.7},
            "echo": False            
        }
        retries = 0
        max_retries = 5
        retry_interval = 20
        while retries < max_retries:
            try:
                response = query_huggingface_api(API_URL_PODCAST, payload)
                
                # Clean the response by removing the prompt
                cleaned_podcast = remove_prompt_from_response(prompt, response)
                
                # Check if the cleaned podcast is not empty
                if not cleaned_podcast:
                    print(f"[WARNING] Received empty podcast script for video '{video_title}'.")
                    return None
                
                _, podcast_summary_dir = create_directory_structure()
                podcast_path = os.path.join(podcast_summary_dir, f"{video_title}_podcast_summary.txt")
                with open(podcast_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_podcast)
                print(f"[INFO] Podcast script saved to {podcast_path}")
                return podcast_path
            except Exception as e:
                if "currently loading" in str(e) or "503" in str(e):
                    retries += 1
                    print(f"[WARNING] Model loading. Retrying in {retry_interval} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(retry_interval)
                else:
                    print(f"[ERROR] Podcast script generation failed: {e}")
                    break
        if retries >= max_retries:
            print(f"[ERROR] Max retries reached for generating podcast script for video '{video_title}'. Skipping...")
            return None
    except Exception as e:
        print(f"[ERROR] Podcast script generation failed: {e}")
        return None

def parse_podcast_script(podcast_path: str, video_title: str) -> dict:
    """
    Parses the podcast script into a dictionary with index, speaker, tone, and sentence.
    
    Args:
        podcast_path (str): Path to the podcast summary txt file.
        video_title (str): Title of the video, used for naming the output dict file.
    
    Returns:
        dict: Dictionary containing the parsed podcast script.
    """
    podcast_dict = {}
    speakers = ['Chris', 'Alex']
    current_speaker_index = 0
    
    try:
        with open(podcast_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for idx, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            
            # Regex to extract tone and sentence
            # Assuming format: "[Tone] Speaker: Sentence."
            match = re.match(r"\[(.*?)\]\s*(?:\w+):\s*(.*)", line)
            if match:
                tone = match.group(1).strip()
                sentence = match.group(2).strip()
            else:
                # If format doesn't match, assume no tone, entire line is sentence
                tone = "Neutral"
                sentence = line
            
            # Assign speaker alternately
            speaker = speakers[current_speaker_index]
            current_speaker_index = (current_speaker_index + 1) % len(speakers)
            
            # Add to dict
            podcast_dict[idx] = {
                "speaker": speaker,
                "tone": tone,
                "sentence": sentence
            }
        
        # Save the dictionary to a JSON file
        output_dict_path = os.path.join(os.getcwd(), f"{video_title}_podcast_dict.json")
        with open(output_dict_path, "w", encoding="utf-8") as f:
            json.dump(podcast_dict, f, indent=4)
        
        print(f"[INFO] Podcast dictionary saved to {output_dict_path}")
        return podcast_dict
    except Exception as e:
        print(f"[ERROR] Failed to parse podcast script: {e}")
        return {}

def extract_video_title(youtube_url: str) -> str:
    command = ["yt-dlp", "--get-title", youtube_url]
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return result.stdout.strip().replace(" ", "_")
    else:
        raise ValueError("[ERROR] Could not fetch video title.")

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
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[INFO] Deleted file: {file_path}")
            except Exception as e:
                print(f"[WARNING] Could not delete file {file_path}: {e}")
        else:
            print(f"[INFO] File does not exist, skipping: {file_path}")

def parse_podcast_script(podcast_path: str, video_title: str) -> dict:
    """
    Parses the podcast script into a dictionary with index, speaker, tone, and sentence.
    
    Args:
        podcast_path (str): Path to the podcast summary txt file.
        video_title (str): Title of the video, used for naming the output dict file.
    
    Returns:
        dict: Dictionary containing the parsed podcast script.
    """
    podcast_dict = {}
    speakers = ['Chris', 'Alex']
    current_speaker_index = 0
    
    try:
        with open(podcast_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for idx, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            
            # Regex to extract tone and sentence
            # Assuming format: "[Tone] Speaker: Sentence."
            match = re.match(r"\[(.*?)\]\s*(?:\w+):\s*(.*)", line)
            if match:
                tone = match.group(1).strip()
                sentence = match.group(2).strip()
            else:
                # If format doesn't match, assume no tone, entire line is sentence
                tone = "Neutral"
                sentence = line
            
            # Assign speaker alternately
            speaker = speakers[current_speaker_index]
            current_speaker_index = (current_speaker_index + 1) % len(speakers)
            
            # Add to dict
            podcast_dict[idx] = {
                "speaker": speaker,
                "tone": tone,
                "sentence": sentence
            }
        
        # Save the dictionary to a JSON file
        output_dict_path = os.path.join(os.getcwd(), f"{video_title}_podcast_dict.json")
        with open(output_dict_path, "w", encoding="utf-8") as f:
            json.dump(podcast_dict, f, indent=4)
        
        print(f"[INFO] Podcast dictionary saved to {output_dict_path}")
        return podcast_dict
    except Exception as e:
        print(f"[ERROR] Failed to parse podcast script: {e}")
        return {}

def main():
    if len(sys.argv) < 2:
        script_name = os.path.basename(__file__)
        print(f"Usage: python {script_name} <youtube_url>")
        sys.exit(1)
    youtube_url = sys.argv[1]
    try:
        video_title = extract_video_title(youtube_url)
        print(f"[INFO] Video title: {video_title}")
        subtitle_file = download_subtitles(youtube_url)
        text_file = convert_subtitles_to_text(subtitle_file)
        english_text_file = translate_to_english_if_needed(text_file)
        summary_file = summarize_text(english_text_file, video_title)
        podcast_file = generate_podcast_script(summary_file, video_title)
        if podcast_file:
            podcast_dict = parse_podcast_script(podcast_file, video_title)
        cleanup_files(subtitle_file, text_file, english_text_file)
        print(f"[INFO] Summary saved to {summary_file}")
        if podcast_file:
            print(f"[INFO] Podcast script saved to {podcast_file}")
            print(f"[INFO] Podcast dictionary saved to {video_title}_podcast_dict.json")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
