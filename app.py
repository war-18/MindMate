from flask import Flask, render_template, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import keras
import json
import numpy as np
import warnings
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder
import pickle
import joblib
from models import LVQ
import tensorflow as tf
warnings.filterwarnings("ignore")

app = Flask(__name__, template_folder='templates', static_folder='static')

# Dummy therapist data with photo URLs
therapists = [
    {"name": "Dr. Smith", "location": "New York", "specialty": "Psychologist", "photo": "/static/images/dr_smith.jpg"},
    {"name": "Dr. Johnson", "location": "Los Angeles", "specialty": "Therapist", "photo": "/static/images/dr_johnson.jpg"},
    {"name": "Dr. Williams", "location": "Chicago", "specialty": "Counselor", "photo": "/static/images/dr_williams.jpg"},
    {"name": "Dr. Williams", "location": "Chicago", "specialty": "Counselor", "photo": "/static/images/dr_williams.jpg"},
    {"name": "Dr. Williams", "location": "Chicago", "specialty": "Counselor", "photo": "/static/images/dr_williams.jpg"},
    {"name": "Dr. Williams", "location": "Chicago", "specialty": "Counselor", "photo": "/static/images/dr_williams.jpg"},
    {"name": "Dr. Williams", "location": "Chicago", "specialty": "Counselor", "photo": "/static/images/dr_williams.jpg"},
]

# YouTube Data API key
API_KEY = 'AIzaSyDP_qbDoNP8IHf1fE3CTL-zdd_NFDqx-o0'


# Function to fetch YouTube videos based on mood and language
def fetch_youtube_videos(mood, language='en'):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    query = ''
    if mood in ['happy', 'excited', 'funny']:
        query = 'happy videos'
    elif mood in ['sad', 'depressed']:
        query = 'sad motivation videos'
    elif mood == 'angry':
        query = 'angry motivation videos'
    else:
        query = mood + ' videos'

    try:
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=5, # Fetching maximum 5 videos per mood
            videoDuration='medium'
        )
        response = request.execute()
        videos = []
        for item in response['items']:
            try:
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                video_description = item['snippet']['description']
                # Check if the video is marked as "Video unavailable" in title or description
                if "Video unavailable" not in video_title and "Video unavailable" not in video_description:
                    videos.append({'title': video_title, 'id': video_id})
            except KeyError:
                # Skip video if it doesn't have a videoId, title, or description
                pass
        return videos
    except HttpError as e:
        print(f"An error occurred: {e}")
        return []


# Load intents data for the chatbot
with open('intents.json') as file:
    data = json.load(file)

# Load trained model for the chatbot
model = keras.models.load_model('chat-model.h5')

# Load tokenizer object for the chatbot
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Load label encoder object for the chatbot
with open('label_encoder.pickle', 'rb') as enc:
    lbl_encoder = pickle.load(enc)

# Load depression prediction model
file_name = "finalized_model.sav"
loaded_model = joblib.load(file_name)

# Parameters for the chatbot
max_len = 20

# About route
@app.route('/about')
def about():
    return render_template('about.html')

# About route
@app.route('/team')
def team():
    return render_template('team.html')

# Contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Index page with navigation for chatbot and depression calculator
@app.route('/therapists')
def therapist():
    return render_template('therapist.html', therapists=therapists)

# Chatbot route
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# Depression calculator route
@app.route('/depression_calculator')
def depression_calculator():
    return render_template('depression_calculator.html')

# Music route
@app.route('/music')
def music():
    return render_template('music.html')

# Suicide analysis route
@app.route('/indexofsucide')
def suicide_analysis():
    return render_template('indexofsucide.html')

# Chatbot response API
@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form["user_input"]
    result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([user_input]), truncating='post', maxlen=max_len))
    tag = lbl_encoder.inverse_transform([np.argmax(result)])

    for intent in data['intents']:
        if intent['tag'] == tag:
            response = np.random.choice(intent['responses'])
            return jsonify({"response": response})

# Depression calculator result route
@app.route('/result_depressionCalci', methods=['POST'])
def result():
    if request.method=='POST':
        umur = request.form['umur']
        jk = request.form['jk']
        ap = request.form['ap']
        af = request.form['af']
        mp = request.form['mp']
        dtest = [umur, jk, ap, af, mp, 0]
        lvq = LVQ(dtest, maxepoch=3, learnRate=0.1, lr_reducer=0.1)
        lvq.normalize()
        lvq.train()
        lvq.test()
        return render_template('result_depressionCalci.html', lvq=lvq)
    return render_template('depression_calculator.html')

# Suicide prediction route
@app.route('/predict', methods=['POST'])
def predict():
    text = request.form['user_text']
    result = loaded_model.predict([text])
    return render_template('resultofsucide.html', result=result[0])

# Route for searching mood and displaying video groups
@app.route('/videos')
def show_videos():
    mood = request.args.get('q', '')
    if mood:
        videos = fetch_youtube_videos(mood)
        return render_template('motivate.html', mood=mood.capitalize(), videos=videos)
    else:
        default_videos = fetch_youtube_videos('motivation')
        return render_template('motivate.html', mood='Motivation', videos=default_videos)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
