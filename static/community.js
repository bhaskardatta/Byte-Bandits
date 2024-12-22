// Toggle Dark Mode (remains the same)
function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
}

// Search Topics (remains the same, but enhanced)
function searchTopics() {
    const query = document.getElementById("searchTopic").value.toLowerCase(); // Get the search query in lowercase
    const topics = document.querySelectorAll(".topic"); // Select all topic elements
    topics.forEach((topic) => {
        const title = topic.querySelector("h2").innerText.toLowerCase(); // Get topic title and convert to lowercase
        topic.style.display = title.includes(query) ? "block" : "none"; // Toggle visibility based on query match
    });
}

// Navigate to Topic Details
function navigateToTopic(topicName) {
    const topicDetails = getTopicDetails(); // Get all the topic details

    const topic = topicDetails[topicName]; // Get the selected topic by name
    const topicShowcase = document.getElementById("topicDetails");

    // If topic is not found, log an error and return
    if (!topic) {
        console.error("Topic not found.");
        return;
    }

    // Show the modal
    topicShowcase.classList.remove("hidden");

    // Update the showcase content
    document.getElementById("topicTitle").innerText = topic.title;
    document.getElementById("topicImage").src = topic.image;
    document.getElementById("topicPdf").href = topic.pdf;

    const audioElement = document.getElementById("topicAudio");
    const audioSource = audioElement.querySelector("source");
    if (audioSource) {
        audioSource.src = topic.audio;
        audioElement.load();
    }

    // Add space for the modal below the clicked topic
    document.querySelector(".topics-container").classList.add("expanded");
}

// Close Topic Details
function closeTopicDetails() {
    const topicShowcase = document.getElementById("topicDetails");
    topicShowcase.classList.add("hidden");

    // Reset the margin of the topics container
    document.querySelector(".topics-container").classList.remove("expanded");
}

// Get Topic Details
function getTopicDetails() {
    return {
        AI: {
            title: "Artificial Intelligence",
            image: "assets/ai.jpg",
            pdf: "assets/ai.pdf",
            audio: "assets/ai.mp3",
        },
        Windmills: {
            title: "Windmills",
            image: "assets/windmills.jpg",
            pdf: "assets/windmills.pdf",
            audio: "assets/windmills.mp3",
        },
        "Electric Vehicles": {
            title: "Electric Vehicles",
            image: "assets/electric-vehicles.jpg",
            pdf: "assets/electric-vehicles.pdf",
            audio: "assets/electric-vehicles.mp3",
        },
        Robotics: {
            title: "Robotics",
            image: "assets/robotics.jpg",
            pdf: "assets/robotics.pdf",
            audio: "assets/robotics.mp3",
        },
        Blockchain: {
            title: "Blockchain",
            image: "assets/blockchain.jpg",
            pdf: "assets/blockchain.pdf",
            audio: "assets/blockchain.mp3",
        },
        "Space Exploration": {
            title: "Space Exploration",
            image: "assets/space-exploration.jpg",
            pdf: "assets/space-exploration.pdf",
            audio: "assets/space-exploration.mp3",
        },
        "Quantum Computing": {
            title: "Quantum Computing",
            image: "assets/quantum-computing.jpg",
            pdf: "assets/quantum-computing.pdf",
            audio: "assets/quantum-computing.mp3",
        },
        Biotechnology: {
            title: "Biotechnology",
            image: "assets/biotechnology.jpg",
            pdf: "assets/biotechnology.pdf",
            audio: "assets/biotechnology.mp3",
        },
        Cybersecurity: {
            title: "Cybersecurity",
            image: "assets/cybersecurity.jpg",
            pdf: "assets/cybersecurity.pdf",
            audio: "assets/cybersecurity.mp3",
        },
    };
}
// Trigger Search on Enter Key
document.getElementById("searchTopic").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevents the default action of Enter (such as form submission)
        searchTopics(); // Calls the search function
    }
});

