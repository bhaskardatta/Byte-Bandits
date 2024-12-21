import os
from flask import Flask, render_template, request, jsonify
import webbrowser
import time
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Path to save the transcripts
transcript_folder = '/home/gagan/whackiest/transcripts'

# Ensure the transcript folder exists
os.makedirs(transcript_folder, exist_ok=True)

# URL of the Flask application (for opening the browser)
url = 'http://127.0.0.1:5000/'  # Flask app URL

# Path to the Chrome executable (modify as per your system)
chrome_path = '/usr/bin/google-chrome'  # Modify this path if needed

# Function to save transcript to a file in the specified folder
def save_transcript_to_file(transcript, script_count):
    try:
        file_path = os.path.join(transcript_folder, f"script{script_count}.txt")
        with open(file_path, 'w') as f:
            f.write(transcript)
        print(f"Transcript saved successfully to {file_path}")
        return file_path
    except Exception as e:
        print(f"Error saving transcript: {e}")
        raise

# Function to open the URL in Chrome
def open_browser():
    try:
        # Attempt to open the URL in a new tab of Chrome
        webbrowser.get(chrome_path).open_new_tab(url)
    except Exception as e:
        print(f"Error opening browser: {e}")
        # If it fails, try opening in the default browser
        webbrowser.open(url)  # Open in the default browser if Chrome fails

# Route for the home page
@app.route('/')
def home():
    # Serve the HTML page from the 'templates' folder
    return render_template('index.html')  # Make sure 'index.html' is in the 'templates' folder

# Route to handle saving transcripts
@app.route('/save_transcript', methods=['POST'])
def save_transcript():
    try:
        data = request.get_json()
        transcript = data.get('transcript')

        if not transcript:
            print("No transcript provided")
            return jsonify({'error': 'No transcript provided'}), 400

        # Increment the script count for each transcript
        script_count = len(os.listdir(transcript_folder)) + 1

        # Save the transcript to the specified folder
        file_path = save_transcript_to_file(transcript, script_count)

        return jsonify({'message': f'Transcript saved as {file_path}'})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# Start the Flask server and open the browser automatically
if __name__ == '__main__':
    open_browser()  # Open the browser before starting the Flask app
    app.run(debug=True, use_reloader=False)  # Disable the reloader to prevent double opening of the browser
