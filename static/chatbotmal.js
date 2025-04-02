const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');
const recordBtn = document.getElementById('record-btn');

let isRecording = false;
let recognition;

const appendMessage = (text, type) => {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add(type === 'user' ? 'user-message' : 'bot-message');
  messageDiv.textContent = text;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (type === 'bot') speak(text);
};

const speak = (text) => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "ml-IN";  // Set to Malayalam
    utterance.rate = 1;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  }
};

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();

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
    appendMessage(data.response, 'bot');  // Ensure correct key from Flask response
  } catch (error) {
    console.error('Error:', error);
    appendMessage('Error communicating with the chatbot.', 'bot');
  }
});

recordBtn.addEventListener('click', () => {
  if (!('webkitSpeechRecognition' in window)) {
    alert('Speech recognition not supported.');
    return;
  }

  if (!isRecording) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = "ml-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();
    recordBtn.classList.add('recording');
    recordBtn.textContent = '🔴 റെക്കോർഡിംഗ്...';

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      userInput.value = transcript;
      chatForm.dispatchEvent(new Event("submit"));  // Auto-submit after speech recognition
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
