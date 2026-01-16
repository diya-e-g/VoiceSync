// Get DOM elements for chat form, input, chat box, and record button
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');
const recordBtn = document.getElementById('record-btn');

let isRecording = false; // Flag to check if recording is active
let recognition;         // Variable for speech recognition instance

// Append a message to the chat box; speak if it's a bot message
const appendMessage = (text, type) => {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add(type === 'user' ? 'user-message' : 'bot-message');
  messageDiv.textContent = text;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
  if (type === 'bot') speak(text);
};

// Use backend gTTS to speak the given text in Malayalam
const speak = async (text) => {
  try {
    const response = await fetch('/generate_audio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text, lang: 'mal' })
    });

    if (response.ok) {
      const data = await response.json();
      // Append current time to prevent caching
      const audio = new Audio(data.audio_url + "?t=" + new Date().getTime());
      audio.play();
    } else {
      console.error("TTS Error:", await response.text());
    }
  } catch (error) {
    console.error("TTS Fetch Error:", error);
  }
};

// Handle chat form submission: send user message and display bot response
chatForm.addEventListener('submit', async (e) => {
  e.preventDefault(); // Prevent default form submission
  const message = userInput.value.trim();
  if (!message) return;
  appendMessage(message, 'user');
  userInput.value = '';
  try {
    const res = await fetch('http://127.0.0.1:5000/getmal', {
      method: 'POST',
      body: JSON.stringify({ msg: message }),
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to get response');
    const data = await res.json();
    appendMessage(data.response, 'bot');
  } catch (error) {
    console.error('Error:', error);
    appendMessage('Error communicating with the chatbot.', 'bot');
  }
});

// Handle record button click: toggle speech recognition for Malayalam
recordBtn.addEventListener('click', () => {
  if (!('webkitSpeechRecognition' in window)) {
    alert('Speech recognition not supported.');
    return;
  }
  if (!isRecording) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = "ml-IN"; // Set recognition language to Malayalam
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.start();
    recordBtn.classList.add('recording');
    recordBtn.textContent = '🔴 റെക്കോർഡിംഗ്...';
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      userInput.value = transcript;
      chatForm.dispatchEvent(new Event("submit")); // Auto-submit after speech recognition
    };
    recognition.onend = () => {
      recordBtn.classList.remove('recording');
      recordBtn.textContent = '🎙️';
      isRecording = false;
    };
    isRecording = true;
  } else {
    recognition.stop();
    isRecording = false;
    recordBtn.classList.remove('recording');
    recordBtn.textContent = '🎙️';
  }
});
