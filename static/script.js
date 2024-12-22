const ttsWindow = document.getElementById("ttsWindow");
const ttsStatus = document.getElementById("ttsStatus");
let realTimeTranscript = ""; // To store the live transcript
let listeningMessage = document.querySelector("#ttsWindow h2"); // Select the h2 element
let recognition;
let isProcessing = false; // Flag to prevent multiple submissions
let isListening = false;  // Flag to track whether the mic is currently listening
let listeningHeader = document.getElementById("listeningHeader");  // Get the h2 element

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
            if (isListening) {
                ttsStatus.textContent = `Final Transcript: "${realTimeTranscript}"`;
                if (listeningMessage) listeningMessage.style.display = "block"; // Reset for next session
                saveTranscriptToBackend(realTimeTranscript); // Save the transcript when recognition ends
            }
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
    if (isProcessing) return;  // Prevent triggering if already processing

    if (isListening) {
        // Stop listening
        recognition.stop();
        ttsStatus.innerText = 'Processing...'; // Change status to processing
        if (listeningHeader) listeningHeader.style.display = "none"; // Hide "Listening..." message during processing
        isListening = false; // Update the listening flag
        isProcessing = true;  // Set the processing flag to true

        // Show processing window for 5 seconds
        setTimeout(function () {
            ttsWindow.style.display = 'none'; // Hide processing window
            window.location.href = '/output';  // Redirect to output page after processing
        }, 5000);  // 5 seconds delay
    } else {
        // Start listening
        ttsWindow.style.display = 'block';
        ttsStatus.innerText = 'Listening...';

        // Start speech recognition and request microphone access
        if (recognition && recognition.state !== "active") {
            recognition.start(); // This should trigger the microphone permission prompt
            isListening = true;  // Update the listening flag
        }

        // After starting the recognition, wait for the results
        recognition.onstart = () => {
            ttsStatus.innerText = 'Listening...'; // Change status to listening once recognition starts
            if (listeningHeader) listeningHeader.style.display = "block"; // Ensure "Listening..." message is visible when listening
        };
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

// Fetch and process (this function also prevents double submission)
function fetchAndSpeak() {
    if (isProcessing) return;  // Prevent triggering if already processing

    // Show processing window for 5 seconds
    ttsWindow.style.display = 'block';
    ttsStatus.innerText = 'Processing...';

    // Simulate processing (5 seconds delay)
    isProcessing = true;  // Set the processing flag
    setTimeout(function () {
        ttsWindow.style.display = 'none';  // Hide processing window
        window.location.href = '/output';  // Redirect to output page after processing
    }, 5000);  // 5 seconds delay
}

document.getElementById('goBackButton').addEventListener('click', function() {
    // Redirect to the home page (or any other page)
    window.location.href = '/';  // Or replace with '/home' if that's your desired path
});



document.addEventListener("DOMContentLoaded", function() {
    // Check if dark mode is already set in localStorage
    const currentMode = localStorage.getItem('theme');
    
    // If dark mode is set in localStorage, apply it
    if (currentMode === 'dark') {
        document.body.classList.add('dark-mode');
        document.querySelector('.dark-mode-toggle').innerHTML = '🌞'; // Optional: Change button to indicate light mode
    } else {
        document.body.classList.remove('dark-mode');
        document.querySelector('.dark-mode-toggle').innerHTML = '🌙'; // Optional: Change button to indicate dark mode
    }

    // Dark mode toggle button click handler
    document.querySelector('.dark-mode-toggle').addEventListener('click', function() {
        if (document.body.classList.contains('dark-mode')) {
            // Switch to light mode
            document.body.classList.remove('dark-mode');
            document.querySelector('.dark-mode-toggle').innerHTML = '🌙'; // Change button to dark mode
            localStorage.setItem('theme', 'light'); // Save theme preference in localStorage
        } else {
            // Switch to dark mode
            document.body.classList.add('dark-mode');
            document.querySelector('.dark-mode-toggle').innerHTML = '🌞'; // Change button to light mode
            localStorage.setItem('theme', 'dark'); // Save theme preference in localStorage
        }
    });
});
