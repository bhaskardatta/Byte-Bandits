// Wait for the DOM to be fully loaded before adding the event listener
window.addEventListener('DOMContentLoaded', (event) => {
    // Add event listener to the Go Back Button
    document.getElementById('goBackButton').addEventListener('click', function() {
        // Redirect to the home page (index route)
        window.location.href = '/';  // This will redirect to the homepage
    });
});

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


