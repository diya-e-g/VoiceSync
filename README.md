# VoiceSync

Voicesync is a real-time stuttering detection and resolution system designed to support individuals with speech disfluencies. It captures stuttered speech via a microphone, transcribes it using speech recognition, and applies Natural Language Processing (NLP) techniques to correct disruptions in real time. The fluent output is then converted into clear, synthesized speech in both English and Malayalam. Additionally, Voicesync features an integrated chatbot that acts as a virtual speech therapy assistant, guiding users through exercises to improve fluency over time. The system is accessible via desktop platforms, promoting confident communication in everyday interactions and fostering inclusivity.

## 📋 Features

- **Speech Processing**: Corrects stuttered speech and repetitive patterns.
- **Multilingual Support**: Currently supports English and Malayalam.
- **Interactive Chatbot**: AI-powered speech therapist chatbot for personalized guidance.
- **Text-to-Speech**: Generate audio from corrected speech for practice.
- **User Authentication**: Secure login/signup system via Supabase.
- **Responsive Design**: Optimized for both desktop and mobile devices.

## 🚀 Live Demo

[Visit VoiceSync App](https://voicesync-dyp0.onrender.com)

## 🛠️ Technologies

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Flask (Python)
- **AI**: Google Gemini Pro API
- **Authentication**: Supabase
- **Speech Synthesis**: Web Speech API, gTTS
- **Natural Language Processing**: NLTK

## ⚙️ Installation

1. Clone the repository
```bash
git clone https://github.com/diya_e_g/VoiceSync.git
cd VoiceSync
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your API keys
```
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
PORT=your_port
```

5. Run the application
```
python app.py
```

## 📱 Usage

1. Register or log in to your account.
2. Select your preferred language (English or Malayalam).
3. Use the speech input to record your speech.
4. View the corrected speech and compare.
5. Play the corrected speech audio to practice pronunciation.
6. Chat with the AI speech therapist for additional guidance.

## 🤖 AI Speech Therapy

VoiceSync uses Google's Gemini Pro model to power an AI speech therapist that:
- Analyzes speech patterns.
- Identifies stuttering and repetition.
- Provides feedback on fluency.
- Offers personalized improvement tips.

## 🧩 Project Structure

```
VoiceSync/
│
├── static/            # Static assets (CSS, JS)
├── templates/         # HTML templates
├── app.py             # Flask application
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## 👥 Contributors

- [Aswini P](https://github.com/aswini1212)
- [Adhina Anup](https://github.com/adhinaanup)
- [Lamiya Yasmin A S](https://github.com/LAMIYA16)
- [Diya Elsa George](https://github.com/diya_e_g)
