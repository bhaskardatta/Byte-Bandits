import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import webbrowser

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Path to save the transcripts
transcript_folder = './transcripts'  # Changed to relative path for portability
os.makedirs(transcript_folder, exist_ok=True)  # Ensure the folder exists

# Function to save transcript to a file
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

# Route to serve the favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')  # Ensure 'index.html' is in the 'templates' folder

# Route to handle saving transcripts
@app.route('/save_transcript', methods=['POST'])
def save_transcript():
    try:
        data = request.get_json()
        transcript = data.get('transcript')

        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400

        # Increment the script count for each transcript
        script_count = len(os.listdir(transcript_folder)) + 1

        # Save the transcript to the specified folder
        file_path = save_transcript_to_file(transcript, script_count)

        return jsonify({'message': f'Transcript saved as {file_path}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start the Flask server
if __name__ == '__main__':
    # Set to host='0.0.0.0' for deployment, and port=5000
    app.run(host='0.0.0.0', port=5000)
