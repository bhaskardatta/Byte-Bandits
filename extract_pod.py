def parse_podcast_transcript(transcript_text):
    """
    Converts a podcast transcript with emotional cues into a structured dictionary format,
    standardizing speaker names and assigning gender.
    
    Args:
        transcript_text (str): Raw podcast transcript text
    
    Returns:
        dict: Structured podcast data with standardized speakers and gender information
    """
    # Initialize the structure
    podcast_data = {
        "title": "",
        "series": []
    }
    
    # Speaker mapping dictionary
    speaker_mapping = {
        'HOST': {'gender': 'host', 'aliases': ['HOST', 'H', 'HOST (H)', 'H:', 'HOST:', 'Host (H):']},
        'GUEST': {'gender': 'sarah', 'aliases': ['SARAH', 'S', 'SARAH (S)', 'S:', 'SARAH:', 'Sarah (S):']}
    }
    
    def normalize_speaker(raw_speaker):
        """Helper function to normalize speaker names and add gender"""
        raw_speaker = raw_speaker.upper()
        for speaker_type, info in speaker_mapping.items():
            if any(alias in raw_speaker for alias in info['aliases']):
                return {
                    'name': speaker_type,
                    'display_name': 'Host' if speaker_type == 'HOST' else 'Sarah',
                    'gender': info['gender']
                }
        return None
    
    # Split into lines and process
    lines = [line.strip() for line in transcript_text.split('\n') if line.strip()]
    series_index = 1
    
    for line in lines:
        # Extract title
        if line.startswith('**Podcast:'):
            podcast_data['title'] = line.replace('**Podcast:', '').replace('**', '').strip()
            continue
            
        # Skip empty lines
        if not line:
            continue
            
        # Process dialogue lines
        if ':**' in line:
            # Extract speaker
            raw_speaker = line.split(':**')[0].replace('**', '').strip()
            content = line.split(':**')[1].strip()
            
            # Get normalized speaker info
            speaker_info = normalize_speaker(raw_speaker)
            if not speaker_info:
                continue
                
            # Split into emotional segments
            segments = content.split('[')
            for segment in segments:
                if not segment:
                    continue
                    
                # Extract emotion and text if emotion is present
                if ']' in segment:
                    emotion, text = segment.split(']')
                    text = text.strip()
                    if text:  # Only add if there's actual text content
                        entry = {
                            "index": series_index,
                            "speaker": speaker_info['display_name'],
                            "speaker_gender": speaker_info['gender'],
                            "tone": emotion.strip(),
                            "sentence": text.strip()
                        }
                        podcast_data["series"].append(entry)
                        series_index += 1
                        
    return podcast_data

# Example usage:
example_transcript = """**Podcast: Empowerment and the Journey of Life**

**Host (H):** [Excitement] Welcome to "The Empowerment Journey," where we dive into the essence of taking charge of our lives and embracing the challenges that come our way. [Gratitude] Today, we have a special guest, Sarah, who has a wealth of wisdom to share about empowerment and resilience. [Warmth] Sarah, thank you so much for joining us.

**Sarah (S):** [Gratitude] Thank you, Host! It's an honor to be here. [Excitement] I'm excited to share some thoughts on empowerment and how it can transform our lives.

**H:** [Agreement] Absolutely. Let's start with the basics. [Curiosity] What does empowerment mean to you?"""

with open("ex_pod.txt", "r") as file:
    # Read the entire content into a string variable
    content = file.read()

# Parse the transcript
parsed_data = parse_podcast_transcript(content)

# Print result (for demonstration)
import json
from parl_gen import audio_generator, parl_loader, describe_speaker
print(json.dumps(parsed_data, indent=2))

model, tokenizer, description_tokenizer = parl_loader()
speaker_tokens = {}
for entry in parsed_data["series"]:
    if entry['speaker_gender'] not in speaker_tokens.keys():
        speaker_tokens[entry['speaker_gender']] = list(describe_speaker(speaker=entry['speaker_gender']))
    print(f"Index: {entry['index']}")
    print(f"Speaker: {entry['speaker_gender']}")
    print(f"Tone: {entry['tone']}")
    print(f"Sentence: {entry['sentence']}")
    print(len(speaker_tokens))
    audio_generator(model, tokenizer, speaker_tokens[entry['speaker_gender']][0], speaker_tokens[entry['speaker_gender']][1],"cpu", entry['sentence'], str(entry['index']), entry['speaker_gender'], "happy")
    print("-" * 40)  # Separator for readability