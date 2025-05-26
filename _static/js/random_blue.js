// // script.js

// // Function to fetch Chuck Norris joke from the API
// function fetchChuckNorrisJoke() {
//     // Make a GET request to the Chuck Norris API
//     fetch('https://api.chucknorris.io/jokes/random')
//         .then(response => response.json())
//         .then(data => {
//             // Update the HTML content with the retrieved joke
//             document.getElementById('joke-container').textContent = data.value;
//         })
//         .catch(error => {
//             // Handle any errors that occurred during the fetch
//             console.error('Error fetching Chuck Norris joke:', error);
//             document.getElementById('joke-container').textContent = 'Failed to fetch joke. Please try again later.';
//         });
// }

// // Call the function to fetch and display the Chuck Norris joke
// fetchChuckNorrisJoke();

// // Fetch quotes from the API
// fetch("https://type.fit/api/quotes")
//     .then(response => response.json())
//     .then(data => {
//         // Get a random quote
//         const randomIndex = Math.floor(Math.random() * data.length);
//         const randomQuote = data[randomIndex];

//         // Update the HTML content with the random quote
//         var quoteContainer = document.getElementById('quote-container');
//         var listItem = document.createElement('li');
//         listItem.textContent = randomQuote.text + " - " + randomQuote.author;
//         quoteContainer.appendChild(listItem);
//     })
//     .catch(error => {
//         // Handle errors
//         console.error('Error fetching quotes:', error);
//     });



// function getRandomDarkPastelBlueColor() {
//     // Generate a dark pastel blue by using higher RGB values with blue being dominant
//     const red = Math.floor(Math.random() * 50) + 100; // Keep red higher to ensure pastel tone but still dark
//     const green = Math.floor(Math.random() * 50) + 120; // Slightly higher green for pastel tone
//     const blue = Math.floor(Math.random() * 100) + 150; // Ensure blue is dominant and dark

//     return `rgb(${red}, ${green}, ${blue})`;
// }

// // Apply the random dark pastel blue color to elements with the class 'custom-card-text'
// document.addEventListener("DOMContentLoaded", function() {
//     const elements = document.querySelectorAll('.custom-card-text');
//     elements.forEach(function(element) {
//         element.style.backgroundColor = getRandomDarkPastelBlueColor();
//     });
// });


// Array of emojis
// const emojis = ['🚀', '💻', '🌟', '✨', '🔥', '📚', '🎯', '🛠️', '🧠', '📈', '🐳', '☸️', '🔧', '⚙️', '💡'];

// // Function to get a random emoji
// function getRandomEmoji() {
//     return emojis[Math.floor(Math.random() * emojis.length)];
// }

// // Apply the random emoji to elements with the class 'custom-card-text'
// document.addEventListener("DOMContentLoaded", function() {
//     const elements = document.querySelectorAll('.custom-card-text');
//     elements.forEach(function(element) {
//         const randomEmoji = getRandomEmoji();
//         element.innerHTML += ' ' + randomEmoji;
//     });
// });


