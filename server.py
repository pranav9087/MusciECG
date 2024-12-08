from flask import Flask, request, jsonify
from googleapiclient.discovery import build
import os
import pickle
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
import random

app = Flask(__name__)

# ECGProcessor class to handle ECG data processing
class ECGProcessor:
    def __init__(self, model_path, scaler_path, chunk_size=5000, overlap=0):
        self.chunk_size = chunk_size
        self.overlap = overlap

        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)

    def parse_ecg_data(self, raw_data):
        lines = raw_data.split('\n')
        data_values = []
        data_started = False

        for line in lines:
            if line.strip() == '':
                continue
            if not data_started:
                try:
                    num = float(line.strip(','))
                    if -1 <= num <= 1:
                        data_started = True
                except ValueError:
                    continue
            if data_started:
                try:
                    value = float(line.strip(','))
                    data_values.append(value)
                except ValueError:
                    continue

        return np.array(data_values)

    def extract_statistical_features(self, chunk):
        return np.array([
            np.mean(chunk),
            np.std(chunk),
            stats.skew(chunk),
            stats.kurtosis(chunk),
            np.ptp(chunk)
        ])

    def get_chunks(self, data):
        chunks = []
        step = self.chunk_size - self.overlap

        for i in range(0, len(data) - self.chunk_size + 1, step):
            chunk = data[i:i + self.chunk_size]
            chunks.append(chunk)

        return chunks

    def process_and_predict(self, ecg_data):
        data = self.parse_ecg_data(ecg_data)
        chunks = self.get_chunks(data)
        if not chunks:
            raise ValueError("Not enough data for analysis")

        predictions = []
        for chunk in chunks:
            features = self.extract_statistical_features(chunk).reshape(1, -1)
            features_scaled = self.scaler.transform(features)
            pred = self.model.predict(features_scaled)[0]
            predictions.append(pred)

        prediction_counts = pd.Series(predictions).value_counts()
        emotions = ['sad', 'fear', 'happy', 'anger', 'neutral', 'disgust', 'surprise']
        return [emotions[pred] for pred in prediction_counts.index]

# Function to fetch a random song based on emotion using the YouTube Data API
def get_random_song(emotion, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    query = f"songs about {emotion}"
    search_response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=10
    ).execute()

    videos = [item["id"]["videoId"] for item in search_response.get("items", [])]
    if not videos:
        return "No songs found for this emotion."
    return f"https://www.youtube.com/watch?v={random.choice(videos)}"

# Flask endpoint to process ECG data and return emotion and song link
@app.route('/process_ecg', methods=['POST'])
def process_ecg():
    try:
        ecg_data = request.json['ecgData']
        api_key = request.json['apiKey']
        
        # Paths to your model and scaler files
        model_path = 'assets/model_assets/random_forest_model.pkl'
        scaler_path = 'assets/model_assets/scaler.pkl'
        
        processor = ECGProcessor(model_path, scaler_path)
        emotions = processor.process_and_predict(ecg_data)

        if emotions:
            # Use the first predicted emotion for song recommendation
            emotion = emotions[0]
            song_link = get_random_song(emotion, api_key)
            return jsonify({
                'emotion': emotion,
                'song_link': song_link
            })
        else:
            return jsonify({'error': 'No emotions detected'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
