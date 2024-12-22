# EduBreeze Project

## Overview
EduBreeze is an innovative web application designed to enhance the learning experience by combining speech-to-text capabilities, topic exploration, and community engagement. This project utilizes Flask for backend operations and modern front-end technologies for a seamless user interface.

---

## Features

### General Features
- **Speech-to-Text Processing**: Real-time transcription using speech recognition.
- **Dark Mode**: A toggleable theme for better user accessibility.

### Frontend Pages
1. **Home Page**:
   - Microphone-based input for live transcription.
   - Option to input a YouTube URL for topic-related content.
   
2. **Community Page**:
   - Search and explore topics such as AI, Robotics, Blockchain, etc.
   - View topic details, download PDFs, and listen to topic audio.

3. **Output Page**:
   - Displays the generated PDFs and audio output based on user input.

---

## Files and Directory Structure

### Backend
- **`app.py`**:
  - Flask backend for routing and serving assets.
  - Handles saving transcripts, community navigation, and real-time updates.

### Frontend
- **HTML**:
  - `index.html`: Home page.
  - `community.html`: Community page for topic exploration.
  - `output.html`: Output page for generated content.

- **CSS**:
  - `style.css`: General styles for the project.
  - `community.css`: Specific styles for the community page.
  - `output.css`: Styles for the output page.

- **JavaScript**:
  - `script.js`: Handles speech recognition and frontend interactions on the home page.
  - `community.js`: Manages topic interactions and dynamic updates on the community page.
  - `output.js`: Includes event handlers for the output page.

- **Miscellaneous**:
  - `script2.txt` and `script3.txt`: Example script files.
  - `wallpaper.png`: Background image used in the project.

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Set up the Python environment:
   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. Start the Flask server:
   ```bash
   python app.py
   ```

4. Open the application in a browser:
   ```
   http://127.0.0.1:5000
   ```

---

## Usage

1. **Home Page**:
   - Use the microphone to record your voice or input a YouTube URL for processing.
   - Navigate to the output page to view or download results.

2. **Community Page**:
   - Search for topics of interest.
   - View additional details such as PDFs and audio files.

3. **Output Page**:
   - View your processed transcript or downloaded files.

---

## Contribution
Contributions are welcome! Please fork the repository and submit a pull request with your proposed changes.

---

## License
This project is licensed under the MIT License.

