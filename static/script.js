const ttsWindow = document.getElementById("ttsWindow");
const ttsStatus = document.getElementById("ttsStatus");
let realTimeTranscript = ""; // To store the live transcript
let listeningMessage = document.querySelector("#ttsWindow h2"); // Select the h2 element
let recognition;

// Dark-mode toggle
function toggleDarkMode() {
    const body = document.body;
    const darkModeButton = document.querySelector('.dark-mode-toggle');
    
    body.classList.toggle('dark-mode');
    
    // Change emoji based on the current theme
    if (body.classList.contains('dark-mode')) {
        darkModeButton.textContent = '🌞'; // Sun emoji for light mode
    } else {
        darkModeButton.textContent = '🌙'; // Moon emoji for dark mode
    }
}

// Initialize Speech Recognition
function initializeSpeechRecognition() {
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = true; // Allow interim results for real-time updates
        recognition.continuous = true; // Keep listening continuously

        // Event: When speech is recognized
        recognition.onresult = (event) => {
            if (listeningMessage) listeningMessage.style.display = "none"; // Hide "Listening..." message
        
            // Update the live transcript
            realTimeTranscript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join(' ');

            // Handle punctuation marks and capitalize the first letter of each sentence
            realTimeTranscript = addPunctuation(realTimeTranscript);
            realTimeTranscript = capitalizeSentences(realTimeTranscript);
        
            // Display the live transcript
            ttsStatus.textContent = realTimeTranscript;
        };

        // Event: When recognition ends
        recognition.onend = () => {
            ttsStatus.textContent = `Final Transcript: "${realTimeTranscript}"`;
            if (listeningMessage) listeningMessage.style.display = "block"; // Reset for next session
            saveTranscriptToBackend(realTimeTranscript); // Save the transcript when recognition ends
        };

        // Event: If there's an error
        recognition.onerror = (event) => {
            ttsStatus.textContent = `Error: ${event.error}`;
            console.error('Speech recognition error:', event.error); // Log the error for debugging
        };
    } else {
        alert("Speech recognition is not supported in your browser.");
    }
}

// Function to add punctuation marks to the transcript
function addPunctuation(transcript) {
    // A simple rule to add punctuation (could be enhanced further)
    transcript = transcript.replace(/\s+\./g, '.'); // Remove space before period
    transcript = transcript.replace(/\s+\,/g, ','); // Remove space before comma

    // Add punctuation where necessary (this can be made more advanced based on your requirements)
    if (!transcript.endsWith('.') && transcript.length > 0) {
        transcript += '.'; // Add a full stop if no punctuation at the end
    }

    return transcript;
}

// Function to capitalize the first letter of each sentence
function capitalizeSentences(transcript) {
    // Capitalize the first letter of each sentence
    return transcript.replace(/(^\s*|[\.\?\!]\s+)([a-z])/g, function(match, separator, char) {
        return separator + char.toUpperCase();
    });
}

// Toggle the TTS window and start/stop recognition
function toggleMicModal() {
    // Toggle visibility of TTS window and mic functionality
    toggleTTSWindow();  // Use the toggle function for TTS window

    if (ttsWindow.style.display === "block") {
        realTimeTranscript = ""; // Reset transcript
        ttsStatus.textContent = "Listening...";
        if (listeningMessage) listeningMessage.style.display = "block"; // Show "Listening..."

        // Start recognition only if not already started
        if (recognition && recognition.state !== "active") {
            recognition.start(); // This should trigger the microphone permission prompt
        }
    } else {
        if (recognition && recognition.state === "active") {
            recognition.stop();
        }
    }
}

// Save the transcript to the backend (Flask)
function saveTranscriptToBackend(transcript) {
    fetch('http://localhost:5000/save_transcript', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ transcript: transcript })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response:', data);
        if (data.message) {
            alert('Transcript saved successfully!');
        }
    })
    .catch(error => {
        console.error('Error saving transcript:', error);
    });
}

// Function to toggle TTS window visibility
function toggleTTSWindow() {
    ttsWindow.style.display = ttsWindow.style.display === 'block' ? 'none' : 'block';
}

// Initialize on page load
initializeSpeechRecognition();



