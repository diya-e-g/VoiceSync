// Get DOM elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');
const recordBtn = document.getElementById('record-btn');

// Update Header based on Scenario
const urlParams = new URLSearchParams(window.location.search);
const currentScenario = urlParams.get('scenario');
const headerElement = document.querySelector('.head');

if (headerElement) {
  if (currentScenario === 'job_interview') {
    headerElement.textContent = "Job Interview Bot";
  } else if (currentScenario === 'ordering_coffee') {
    headerElement.textContent = "Barista Bot";
  } else if (currentScenario === 'public_speaking') {
    headerElement.textContent = "Public Speaking Coach";
  } else {
    headerElement.textContent = "Speech Therapist Chatbot";
  }
}

let isRecording = false;
let recognition;

// Append a message to the chat box and speak bot messages
const appendMessage = (text, type) => {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add(type === 'user' ? 'user-message' : 'bot-message');
  messageDiv.textContent = text;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
  if (type === 'bot') speak(text);
};

// Use Web Speech API to speak the given text
const speak = (text) => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 1;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  }
};

// Helper to update local storage stats
const updateStats = (newStats) => {
  if (!newStats) return;
  const currentStats = JSON.parse(localStorage.getItem('dysfluencyStats')) || { blocks: 0, repetitions: 0 };
  currentStats.blocks += (newStats.blocks || 0);
  currentStats.repetitions += (newStats.repetitions || 0);
  localStorage.setItem('dysfluencyStats', JSON.stringify(currentStats));
  console.log("Stats updated:", currentStats);
};

// Handle form submission to send chat messages
chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;
  appendMessage(message, 'user');
  userInput.value = '';

  // Get scenario from URL query params
  const urlParams = new URLSearchParams(window.location.search);
  const scenario = urlParams.get('scenario') || 'general';

  // Get resume text if available
  let resumeText = localStorage.getItem('resumeText');

  // Only send resume text if we are in job interview mode, otherwise clear it/ignore it
  if (scenario !== 'job_interview') {
    resumeText = null;
  }

  try {
    const res = await fetch('http://127.0.0.1:5000/get', {
      method: 'POST',
      body: JSON.stringify({
        msg: message,
        scenario: scenario,
        resume_text: resumeText
      }),
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to get response');
    const data = await res.json();

    // Update dysfluency stats if present
    if (data.stats) {
      updateStats(data.stats);
    }

    appendMessage(data.response, 'bot');
  } catch (error) {
    console.error('Error:', error);
    appendMessage('Error communicating with the chatbot.', 'bot');
  }
});

// Handle recording button click to start/stop speech recognition
recordBtn.addEventListener('click', () => {
  if (!('webkitSpeechRecognition' in window)) {
    alert('Speech recognition not supported.');
    return;
  }
  if (!isRecording) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.start();
    recordBtn.classList.add('recording');
    recordBtn.textContent = '🔴 Recording...';
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      userInput.value = transcript;
      chatForm.dispatchEvent(new Event("submit"));
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
