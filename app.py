from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
import os, re, nltk
from flask_cors import CORS
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/*": {"origins": "*"}})
nltk.download('punkt')

# API Key config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Text correction map
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

# --- Text Processing ---
def remove_special_characters(text):
    return re.sub(r"[^a-zA-Z0-9\sഀ-ൿ]", "", text)

def remove_repeated_characters(word):
    return re.sub(r"(.)\1+", r"\1", word)

def normalize_word(word, lang="en"):
    word = word.lower()
    return custom_corrections.get(lang, {}).get(word, word)

def remove_duplicate_words(sentence):
    words = sentence.split()
    seen = set()
    return " ".join([word for word in words if not (word in seen or seen.add(word))])

def process_sentence(sentence, lang="en"):
    return remove_duplicate_words(" ".join([
        normalize_word(remove_repeated_characters(w), lang) for w in sentence.split()
    ]))

def remove_duplicate_sentences(sentences):
    seen = set()
    return [s for s in sentences if not (s.lower() in seen or seen.add(s.lower()))]

def convert_structured_to_normal_text(text, lang="en"):
    text = remove_special_characters(text.lower())
    cleaned_text = re.sub(r"[\-\*\•\d]+\s", "", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    sentences = nltk.sent_tokenize(cleaned_text)
    processed = [process_sentence(s, lang) for s in sentences]
    return " ".join(remove_duplicate_sentences(processed))

# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/config")
def get_config():
    return jsonify({"SUPABASE_URL": SUPABASE_URL, "SUPABASE_KEY": SUPABASE_KEY})

@app.route("/set_language", methods=["POST"])
def set_language():
    lang = request.form.get("language")
    return redirect(url_for('mal_index2' if lang == 'mal' else 'eng_index2'))

@app.route("/index2.html")
def eng_index2():
    return render_template("index2.html")

@app.route("/mal_index2.html")
def mal_index2():
    return render_template("mal_index2.html")

@app.route("/chatbot.html")
def chatbot_page():
    return render_template("chatbot.html")

@app.route("/chatbotmal.html")
def chatbot_mal_html():
    return render_template("chatbotmal.html")

@app.route("/process", methods=["POST"])
def process_text():
    data = request.json
    if not data or 'text' not in data or 'lang' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    lang = data['lang']
    if lang not in custom_corrections:
        return jsonify({'error': 'Unsupported language'}), 400

    try:
        result = convert_structured_to_normal_text(data['text'], lang)
        return jsonify({'normal_text': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/generate_audio", methods=["POST"])
def generate_audio():
    data = request.json
    text = data.get("text", "").strip()
    lang = "ml" if data.get("lang") == "mal" else "en"

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        tts = gTTS(text=text, lang=lang)
        audio_filename = f"{lang}_speech.mp3"
        tts.save(os.path.join(AUDIO_FOLDER, audio_filename))
        return jsonify({'audio_url': f"/static/audio/{audio_filename}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/static/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route("/get", methods=["POST"])
def chatbot_response():
    try:
        msg = request.get_json().get("msg", "").strip()
        if not msg:
            return jsonify({"response": "⚠️ Please enter a message."}), 400

        prompt = (
            "You are Voice Sync, a speech therapist chatbot helping a patient with their speech. "
            "Correct their stuttered speech and appreciate them if they speak fluently. "
            "Give them tips to improve. Reply in 1-3 sentences."
        )
        response = model.generate_content([prompt, msg])
        return jsonify({"response": response.text if hasattr(response, "text") else "⚠️ No response generated."})
    except Exception as e:
        return jsonify({"response": f"⚠️ Error: {str(e)}"}), 500

@app.route("/getmal", methods=["POST"])
def chatbot_response2():
    try:
        msg = request.get_json().get("msg", "").strip()
        if not msg:
            return jsonify({"response": "⚠️ Please enter a message."}), 400

        prompt = (
            "Strictly speak in Malayalam. You are Voice Sync, a speech therapist chatbot helping a patient. "
            "Introduce yourself as VoiceSync sometimes. Correct their stuttered speech, appreciate them if they speak fluently, "
            "and give them tips to improve. Reply in 1-3 sentences."
        )
        response = model.generate_content([prompt, msg])
        return jsonify({"response": response.text if hasattr(response, "text") else "⚠️ No response generated."})
    except Exception as e:
        return jsonify({"response": f"⚠️ Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
