document.getElementById('send-btn').addEventListener('click', function(event) {
    event.preventDefault();
    sendUserInput();
});

document.getElementById('user-input').addEventListener('click', function() {
    this.classList.add('expanded');
});

document.getElementById('user-input').addEventListener('blur', function() {
    this.classList.remove('expanded');
});

document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        sendUserInput();
    }
});

function appendChat(role, message) {
    var chatContainer = document.getElementById('chat-container');
    var chatBubble = document.createElement('div');
    chatBubble.classList.add('chat-bubble');
    chatBubble.classList.add(role);
    chatBubble.innerText = message;
    chatBubble.addEventListener('click', function() {
        this.classList.add('expanded');
    });
    chatBubble.addEventListener('blur', function() {
        this.classList.remove('expanded');
    });
    chatContainer.appendChild(chatBubble);
    document.getElementById('user-input').value = ''; // Clear input field after sending
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to bottom of chat
}

function displayOptions(options) {
    var chatContainer = document.getElementById('chat-container');
    var optionsContainer = document.createElement('div');
    optionsContainer.classList.add('options-container');
    var optionsHtml = '<div class="chat-bubble robot"><ul class="options-list">';
    options.forEach(option => {
        optionsHtml += `<li><button class="option-button" onclick="sendOption('${option}')">${option}</button></li>`;
    });
    optionsHtml += '</ul></div>';
    optionsContainer.innerHTML = optionsHtml;
    chatContainer.appendChild(optionsContainer);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to bottom of chat
}

function sendOption(option) {
    appendChat("user", option);
    showLoading(); // Show loading indicator
    fetch('/process_final_option', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'user_input=' + encodeURIComponent(option)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(); // Hide loading indicator
        if (data.response) {
            appendChat("robot", data.response);
            triggerConfetti(); // Trigger confetti when response is received
        }
    })
    .catch(error => {
        hideLoading(); // Hide loading indicator
        console.error('Error:', error);
    });
}

function showLoading() {
    var chatContainer = document.getElementById('chat-container');
    var loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'loading-indicator';
    loadingIndicator.classList.add('chat-bubble', 'robot');
    loadingIndicator.innerText = '...'; // Loading dots
    chatContainer.appendChild(loadingIndicator);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to bottom of chat
}

function hideLoading() {
    var loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

function triggerConfetti() {
    var end = Date.now() + (2 * 1000); // Confetti duration: 2 seconds
    var colors = ['#bb0000', '#ffffff'];

    function frame() {
        confetti({
            particleCount: 2,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: colors
        });
        confetti({
            particleCount: 2,
            angle: 120,
            spread: 55,
            origin: { x: 1 },
            colors: colors
        });

        if (Date.now() < end) {
            requestAnimationFrame(frame);
        }
    }

    frame();
}
