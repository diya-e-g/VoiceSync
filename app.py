from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
import os
import re
import nltk
from flask_cors import CORS  
from gtts import gTTS  
from dotenv import load_dotenv

load_dotenv()
# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

load_dotenv()

@app.route('/config')
def get_config():
    return jsonify({
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY")
    })

# Folder to store generated audio
AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Custom correction dictionaries
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

def remove_repeated_characters(word):
    return re.sub(r"(.)\1+", r"\1", word)

def normalize_word(word, lang):
    word = word.lower()
    return custom_corrections[lang].get(word, word)

def remove_duplicate_words(sentence):
    words = sentence.split()
    seen = set()
    unique_words = [word for word in words if not (word in seen or seen.add(word))]
    return " ".join(unique_words)

def process_sentence(sentence, lang):
    words = sentence.split()
    processed_words = [normalize_word(remove_repeated_characters(word), lang) for word in words]
    return remove_duplicate_words(" ".join(processed_words))

def remove_duplicate_sentences(sentences):
    seen = set()
    unique_sentences = [sentence for sentence in sentences if not (sentence.lower() in seen or seen.add(sentence.lower()))]
    return unique_sentences

def convert_structured_to_normal_text(text, lang):
    cleaned_text = re.sub(r"[\-\*\•\d]+\s", "", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    sentences = nltk.sent_tokenize(cleaned_text)
    processed_sentences = [process_sentence(sentence, lang) for sentence in sentences]
    unique_sentences = remove_duplicate_sentences(processed_sentences)
    return " ".join(unique_sentences)


@app.route('/')
def home():
    return render_template('index1.html')  
# Show index.html first

@app.route('/signup.html')
def signup_page():
    return render_template('signup.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')


@app.route('/dashboard.html')
def dash_page():
    return render_template('dashboard.html')


@app.route('/sel_page.html')
def select_language():
    return render_template('sel_page.html')  # Show selection page when needed




@app.route('/set_language', methods=['POST'])
def set_language():
    lang = request.form.get('language')
    if lang == 'mal':
        return redirect(url_for('mal_index2'))
    return redirect(url_for('eng_index2'))

@app.route('/eng_index2')
def eng_index2():
    return render_template('index2.html')

@app.route('/mal_index2')
def mal_index2():
    return render_template('mal_index2.html')

@app.route('/mal_index3')
def mal_index3():
    return render_template('mal_index3.html')

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
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=lang)
        audio_filename = f"{lang}_speech.mp3"
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        tts.save(audio_path)

        # Return the URL to the generated audio
        return jsonify({'audio_url': f"/static/audio/{audio_filename}"})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
