import os
from pydub import AudioSegment
import re

def stitch_audio_files(input_folder, output_filename='black_hole.wav'):
    """
    Finds all WAV files in the specified folder, sorts them by index in filename,
    and concatenates them into a single audio file.
    
    Args:
        input_folder (str): Path to the folder containing WAV files
        output_filename (str): Name of the output file (default: 'final_audio.wav')
    """
    # Get all .wav files in the folder
    wav_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.wav')]
    
    if not wav_files:
        print(f"No WAV files found in {input_folder}")
        return
    
    # Extract index from filename and sort
    def get_index(filename):
        # Find all numbers in the filename
        numbers = re.findall(r'\d+', filename)
        if numbers:
            return int(numbers[0])
        return 0
    
    # Sort files by their index
    wav_files.sort(key=get_index)
    
    print(f"Found {len(wav_files)} WAV files. Processing in order:")
    for f in wav_files:
        print(f"- {f}")
    
    # Initialize with first audio file
    combined_audio = AudioSegment.from_wav(os.path.join(input_folder, wav_files[0]))
    
    # Append remaining files
    for wav_file in wav_files[1:]:
        try:
            audio_segment = AudioSegment.from_wav(os.path.join(input_folder, wav_file))
            combined_audio += audio_segment
            print(f"Added: {wav_file}")
        except Exception as e:
            print(f"Error processing {wav_file}: {str(e)}")
    
    # Export final audio
    output_path = os.path.join(input_folder, output_filename)
    combined_audio.export(output_filename, format="wav")
    print(f"\nSuccessfully created: {output_path}")
    print(f"Final duration: {len(combined_audio)/1000:.2f} seconds")

# Example usage
if __name__ == "__main__":
    # Replace with your folder path
    folder_path = "audio"
    stitch_audio_files(folder_path)