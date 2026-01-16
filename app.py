from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
import os
import re
import nltk
from flask_cors import CORS  
from gtts import gTTS  
from google import genai 
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app with CORS enabled
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/*": {"origins": "*"}})

# Download required NLTK tokenizer data
nltk.download('punkt')
nltk.download('punkt_tab')

# Retrieve API keys and configuration values from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY,http_options=types.HttpOptions(api_version='v1'))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing in the .env file")



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

# Process a word: remove repeated characters and count changes (blocks).
def process_word_with_stats(word):
    new_word, count = re.subn(r"(.)\1+", r"\1", word)
    return new_word, count

# Process a sentence: normalize, remove repeated characters, eliminate duplicate words, and return stats.
def process_sentence_with_stats(sentence, lang="en"):
    words = sentence.split()
    
    # 1. Blocks (repeated characters)
    processed_words_step1 = []
    blocks_count = 0
    for word in words:
        nw, c = process_word_with_stats(word)
        blocks_count += c
        processed_words_step1.append(normalize_word(nw, lang))
        
    # 2. Repetitions (duplicate words)
    seen = set()
    unique_words = []
    repetitions_count = 0
    for w in processed_words_step1:
        if w in seen:
            repetitions_count += 1
        else:
            seen.add(w)
            unique_words.append(w)
            
    final_sentence = " ".join(unique_words)
    return final_sentence, blocks_count, repetitions_count

# Convert structured text into normal text with analytics.
def convert_structured_to_normal_text_with_stats(text, lang="en"):
    text = text.lower()
    text = remove_special_characters(text)
    cleaned_text = re.sub(r"[\-\*\•\d]+\s", "", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    sentences = nltk.sent_tokenize(cleaned_text)
    
    total_blocks = 0
    total_repetitions = 0
    processed_sentences_list = []
    
    for sentence in sentences:
        s_text, b_count, r_count = process_sentence_with_stats(sentence, lang)
        total_blocks += b_count
        total_repetitions += r_count
        processed_sentences_list.append(s_text)
        
    unique_sentences = remove_duplicate_sentences(processed_sentences_list)
    return " ".join(unique_sentences), {"blocks": total_blocks, "repetitions": total_repetitions}

def normalize_word(word, lang="en"):
    """Corrects common typos based on the custom_corrections dictionary."""
    return custom_corrections.get(lang, {}).get(word, word)

def remove_duplicate_sentences(sentences):
    """Removes identical consecutive sentences."""
    if not sentences:
        return []
    result = [sentences[0]]
    for i in range(1, len(sentences)):
        if sentences[i] != sentences[i-1]:
            result.append(sentences[i])
    return result

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

#Render MyProgress page
@app.route('/dashboard.html')
def dashboard_page():
    return render_template('dashboard.html')

#Render PracticeMode page
@app.route('/practice_mode.html')
def practice_mode():
    return render_template('practice_mode.html')


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
        normal_text, stats = convert_structured_to_normal_text_with_stats(structured_text, lang)
        return jsonify({'normal_text': normal_text, 'stats': stats})
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
        scenario = data.get("scenario", "general").lower()
        resume_text = data.get("resume_text", "")
        
        print(f"DEBUG: Received message: {user_message}")
        print(f"DEBUG: Scenario: {scenario}")

        # Process stats
        _, stats = convert_structured_to_normal_text_with_stats(user_message, "en")
        print(f"DEBUG: Stats calculated: {stats}")

        base_prompt = (
            "You are Voice Sync, a speech therapist chatbot. "
            "Correct their stuttered speech and appreciate them if they speak fluently. "
            "Keep response to 2 sentences."
        )

        # Customize prompt based on scenario
        if scenario == "job_interview":
            base_prompt = (
                "You are an experienced and professional hiring manager conducting a job interview. "
                "Your goal is to assess the candidate's fit for the role while maintaining a professional yet encouraging tone. "
                "Ask one clear, relevant question at a time. "
                "If the user provides a short or incomplete answer, ask a follow-up question to dig deeper. "
                "If they answer well, acknowledge it briefly and move to the next topic. "
                "Keep your responses natural and spoken-style, not robotic. Limit to 2-3 sentences."
            )
            if resume_text:
                base_prompt += f"\n\nContext from Candidate's Resume:\n{resume_text}\n"
                base_prompt += "Tailor your questions specifically to the experience, skills, and projects listed in the resume."
            
        elif scenario == "ordering_coffee":
            base_prompt = (
                "You are a friendly and energetic barista at a popular coffee shop. "
                "Your goal is to take the customer's order efficiently while being warm and welcoming. "
                "Ask clarifying questions if the order is vague (e.g., 'What size would you like?', 'Hot or iced?', 'Any milk preference?'). "
                "React naturally to what they say. Use casual language appropriate for a cafe setting. "
                "Keep your responses short and conversational (1-2 sentences)."
            )
            
        elif scenario == "public_speaking":
            base_prompt = (
                "You are a supportive Public Speaking Coach and an active audience member. "
                "Your goal is to help the user practice their speech delivery and content. "
                "After the user speaks, provide a specific piece of positive feedback and one gentle suggestion for improvement if needed. "
                "Then, ask a relevant follow-up question to help them expand on their topic or practice impromptu speaking. "
                "Keep your tone encouraging and motivating. Limit response to 2-3 sentences."
            )

        print("DEBUG: Calling New Gemini API...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{base_prompt} \n\nUser: {user_message}\nAI:"
        )
        
        bot_message = response.text
        print("DEBUG: Response Successful")

        return jsonify({
            "response": bot_message, 
            "stats": stats
        })
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"response": f"⚠️ Connection Error: {str(e)}"}), 500

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        text = ""
        if file.filename.endswith('.pdf'):
            try:
                from pypdf import PdfReader
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            except ImportError:
                return jsonify({'error': 'pypdf not installed'}), 500
            except Exception as e:
                return jsonify({'error': f'Error reading PDF: {str(e)}'}), 500
        else:
            # Assume text file
            text = file.read().decode('utf-8', errors='ignore')

        return jsonify({'text': text})
    except Exception as e:
        print(f"Upload Error: {e}")
        return jsonify({'error': str(e)}), 500

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
            "Be more supportive and always encourage the person speaking."
            "Get straight to the point in 2-3 sentences. If the user speaks in Malayalam, respond in Malayalam. Otherwise respond in English."
        )
        # Using the client object correctly for Malayalam as well if needed, but keeping original structure if it works or updating it.
        # Original code used `model.generate_content` but `model` isn't defined in the snippet I saw unless I missed it.
        # I'll update it to use `client` to be safe, assuming `client` is the global genai client.
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{therapist_prompt} User message: {user_message}"
        )
        bot_message = response.text
        return jsonify({"response": bot_message})
    except Exception as e:
        return jsonify({"response": f"⚠️ Error processing request: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
