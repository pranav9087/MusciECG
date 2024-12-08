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

class ECGProcessor:
    # (Existing ECGProcessor code goes here)
api_key = "AIzaSyCXgaeWeZAER3C3bEaQVp-rZzbJ9SqDfuk"
def get_random_song(emotion, api_key):
    """Fetch a random song based on emotion using YouTube Data API."""
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
