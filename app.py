from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
import os
import re
import nltk
from flask_cors import CORS  
from gtts import gTTS  
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app with CORS enabled
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/*": {"origins": "*"}})

# Download required NLTK tokenizer data
nltk.download('punkt')

# Retrieve API keys and configuration values from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing in the .env file")

# Configure the generative AI model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# Define custom correction mappings for English and Malayalam
custom_corrections = {
    "en": {
        "helo": "hello", "wrld": "world", "pythonn": "python",
        "heloo": "hello", "woorrrld": "world", "myy": "my",
        "naame": "name", "naem": "name", "naam": "name",
        "iz": "is", "iis": "is", "nam": "name"
    },
    "mal": {
        "ഹലോ": "ഹലോ", "പൈത്തോൺ": "പൈത്തോൺ", "വേൾഡ്": "വേൾഡ്",
        "മൈ": "എന്റെ", "പേര്": "പേര്", "ആണ്": "ആണ്"
    }
}

# Create folder for storing generated audio if it doesn't exist
AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# --- Text Processing Functions ---

# Remove special characters from text, preserving alphanumeric and Malayalam characters.
def remove_special_characters(text):
    return re.sub(r"[^a-zA-Z0-9\sഀ-ൿ]", "", text)

# Replace repeated characters in a word with a single occurrence.
def remove_repeated_characters(word):
    return re.sub(r"(.)\1+", r"\1", word)

# Normalize a word to lowercase and apply custom corrections for the specified language.
def normalize_word(word, lang="en"):
    word = word.lower()
    return custom_corrections.get(lang, {}).get(word, word)

# Remove duplicate words from a sentence while preserving the original order.
def remove_duplicate_words(sentence):
    words = sentence.split()
    seen = set()
    unique_words = [word for word in words if not (word in seen or seen.add(word))]
    return " ".join(unique_words)

# Process a sentence: normalize, remove repeated characters, and eliminate duplicate words.
def process_sentence(sentence, lang="en"):
    words = sentence.split()
    processed_words = [normalize_word(remove_repeated_characters(word), lang) for word in words]
    return remove_duplicate_words(" ".join(processed_words))

# Remove duplicate sentences, case-insensitively.
def remove_duplicate_sentences(sentences):
    seen = set()
    unique_sentences = [sentence for sentence in sentences if not (sentence.lower() in seen or seen.add(sentence.lower()))]
    return unique_sentences

# Convert structured text into normal text by cleaning, tokenizing, processing, and removing duplicate sentences.
def convert_structured_to_normal_text(text, lang="en"):
    text = text.lower()
    text = remove_special_characters(text)
    cleaned_text = re.sub(r"[\-\*\•\d]+\s", "", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    sentences = nltk.sent_tokenize(cleaned_text)
    processed_sentences = [process_sentence(sentence, lang) for sentence in sentences]
    unique_sentences = remove_duplicate_sentences(processed_sentences)
    return " ".join(unique_sentences)

# --- Route Handlers ---

# Render the home page.
@app.route('/')
def home():
    return render_template('index.html')

# Return configuration details.
@app.route('/config')
def get_config():
    return jsonify({
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": SUPABASE_KEY
    })

# Render index page.
@app.route('/index.html')
def index_page():
    return render_template('index.html')

# Render index1 page.
@app.route('/index1.html')
def index1_page():
    return render_template('index1.html')

# Render signup page.
@app.route('/signup.html')
def signup_page():
    return render_template('signup.html')

# Render login page.
@app.route('/login.html')
def login_page():
    return render_template('login.html')

# Render logout page.
@app.route('/logout.html')
def logout_page():
    return render_template('logout.html')

# Render language selection page.
@app.route('/sel_page.html')
def select_language():
    return render_template('sel_page.html')

# Redirect user based on selected language.
@app.route('/set_language', methods=['POST'])
def set_language():
    lang = request.form.get('language')
    return redirect(url_for('mal_index2' if lang == 'mal' else 'eng_index2'))

# Render English index2 page.
@app.route('/index2.html')
def eng_index2():
    return render_template('index2.html')

# Render English index3 page.
@app.route('/index3.html')
def eng_index3():
    return render_template('index3.html')

# Render Malayalam index2 page.
@app.route('/mal_index2.html')
def mal_index2():
    return render_template('mal_index2.html')

# Render Malayalam index3 page.
@app.route('/mal_index3.html')
def mal_index3():
    return render_template('mal_index3.html')

# Render Malayalam chatbot page.
@app.route('/chatbotmal.html')
def chatbot_mal_html():
    return render_template('chatbotmal.html')

# Render FAQ page.
@app.route('/faq.html')
def faq():
    return render_template('faq.html')

# Process the input structured text and return normalized text.
@app.route('/process', methods=['POST'])
def process_text():
    data = request.json
    if not data or 'text' not in data or 'lang' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    structured_text = data['text']
    lang = data['lang']
    if lang not in custom_corrections:
        return jsonify({'error': 'Unsupported language'}), 400

    try:
        normal_text = convert_structured_to_normal_text(structured_text, lang)
        return jsonify({'normal_text': normal_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Generate audio from provided text using gTTS and return the audio URL.
@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    data = request.json
    if not data or 'text' not in data or 'lang' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    text = data['text'].strip()
    lang = "ml" if data['lang'] == "mal" else "en"
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        tts = gTTS(text=text, lang=lang)
        audio_filename = f"{lang}_speech.mp3"
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        tts.save(audio_path)
        return jsonify({'audio_url': f"/static/audio/{audio_filename}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve the generated audio file.
@app.route('/static/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

# Render chatbot page.
@app.route("/chatbot.html")
def chatbot_page():
    return render_template("chatbot.html")

# Generate chatbot response for English speech therapy.
@app.route("/get", methods=["POST"])
def chatbot_response():
    try:
        data = request.get_json()
        user_message = data.get("msg", "").strip()
        if not user_message:
            return jsonify({"response": "⚠️ Please enter a message."}), 400

        therapist_prompt = (
            "You are Voice Sync, a speech therapist chatbot helping a patient with their speech. "
            "Correct their stuttered speech and appreciate them if they speak fluently. "
            "Get straight to the point in 2-3 sentences."
        )
        response = model.generate_content([therapist_prompt, user_message])
        bot_message = response.text if hasattr(response, "text") else "I couldn't generate a response."
        return jsonify({"response": bot_message})
    except Exception as e:
        return jsonify({"response": f"⚠️ Error processing request: {str(e)}"}), 500

# Generate chatbot response for Malayalam speech therapy.
@app.route("/getmal", methods=["POST"])
def chatbot_response2():
    try:
        data = request.get_json()
        user_message = data.get("msg", "").strip()
        if not user_message:
            return jsonify({"response": "⚠️ Please enter a message."}), 400

        therapist_prompt = (
            "Strictly speak in Malayalam. You are Voice Sync, a speech therapist chatbot helping a patient with their speech. "
            "Correct their stuttered speech and appreciate them if they speak fluently. "
            "Get straight to the point in 2-3 sentences. If the user speaks in Malayalam, respond in Malayalam. Otherwise respond in English."
        )
        response = model.generate_content([therapist_prompt, user_message])
        bot_message = response.text if hasattr(response, "text") else "I couldn't generate a response."
        return jsonify({"response": bot_message})
    except Exception as e:
        return jsonify({"response": f"⚠️ Error processing request: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
