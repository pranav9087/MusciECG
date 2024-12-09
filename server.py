from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
import pickle
import os

class ECGProcessor:
    def __init__(self, model_path, scaler_path, chunk_size=5000, overlap=0):
        """
        Initialize ECG processor
        
        Args:
            model_path: Path to saved Random Forest model
            scaler_path: Path to saved StandardScaler
            chunk_size: Size of ECG chunks to process (default 5000)
            overlap: Number of samples to overlap between chunks (default 0)
        """
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
            # Skip header until we find numeric data
            if not data_started:
                try:
                    num = float(line.strip(','))
                    # Assuming data in range [-1, 1] as an indicator for start of ECG data
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
        features = []
        
        # Time domain statistical features
        features.extend([
            np.mean(chunk),
            np.std(chunk),
            stats.skew(chunk),
            stats.kurtosis(chunk),
            np.ptp(chunk)  # Peak-to-peak range
        ])
        
        return np.array(features)
    
    def get_chunks(self, data):
        chunks = []
        step = self.chunk_size - self.overlap
        
        for i in range(0, len(data) - self.chunk_size + 1, step):
            chunk = data[i:i + self.chunk_size]
            chunks.append(chunk)
            
        return chunks
    
    def process_and_predict(self, ecg_data):
        try:
            data = self.parse_ecg_data(ecg_data)
            chunks = self.get_chunks(data)
            
            if not chunks:
                raise ValueError("Not enough data for analysis")
            
            # Process each chunk
            predictions = []
            for chunk in chunks:
                features = self.extract_statistical_features(chunk)
                features = features.reshape(1, -1)
                features_scaled = self.scaler.transform(features)
                pred = self.model.predict(features_scaled)[0]
                predictions.append(pred)
            
            # Get mode of predictions
            prediction_counts = pd.Series(predictions).value_counts()
            final_predictions = prediction_counts.index.tolist()
            
            # Emotions are indexed as [0: sad, 1: fear, 2: happy, 3: anger, 4: neutral, 5: disgust, 6: surprise]
            emotions = ['sad', 'fear', 'happy', 'anger', 'neutral', 'disgust', 'surprise']
            
            return {
                'predictions': [emotions[pred] for pred in final_predictions],
                'counts': prediction_counts.tolist(),
                'chunks_processed': len(chunks)
            }
            
        except Exception as e:
            raise RuntimeError(f"Error processing ECG data: {str(e)}")

app = Flask(__name__)
CORS(app)

CSV_DIR = 'csv_files'

if not os.path.exists(CSV_DIR):
    os.makedirs(CSV_DIR)

# Define a mapping from emotions to recommended songs (with YouTube links)
emotion_songs = {
    'happy': [
        {'title': 'Pharrell Williams - Happy', 'youtube_link': 'https://www.youtube.com/watch?v=y6Sxv-sUYtM'},
        {'title': 'Justin Timberlake - Can\'t Stop the Feeling!', 'youtube_link': 'https://www.youtube.com/watch?v=ru0K8uYEZWw'},
        {'title': 'Katrina & The Waves - Walking on Sunshine', 'youtube_link': 'https://www.youtube.com/watch?v=iPUmE-tne5U'}
    ],
    'sad': [
        {'title': 'Adele - Someone Like You', 'youtube_link': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0'},
        {'title': 'Sam Smith - Stay With Me', 'youtube_link': 'https://www.youtube.com/watch?v=pB-5XG-DbAA'},
        {'title': 'Billie Eilish - When the Party\'s Over', 'youtube_link': 'https://www.youtube.com/watch?v=pbMwTqkKSps'}
    ],
    'fear': [
        {'title': 'Radiohead - Creep', 'youtube_link': 'https://www.youtube.com/watch?v=XFkzRNyygfk'},
        {'title': 'Evanescence - Bring Me To Life', 'youtube_link': 'https://www.youtube.com/watch?v=3YxaaGgTQYM'}
    ],
    'anger': [
        {'title': 'Rage Against the Machine - Killing In the Name', 'youtube_link': 'https://www.youtube.com/watch?v=bWXazVhlyxQ'},
        {'title': 'System Of A Down - Chop Suey!', 'youtube_link': 'https://www.youtube.com/watch?v=CSvFpBOe8eY'}
    ],
    'neutral': [
        {'title': 'Lo-fi Beats - Chill Study Mix', 'youtube_link': 'https://www.youtube.com/watch?v=5qap5aO4i9A'},
        {'title': 'Chillhop Essentials', 'youtube_link': 'https://www.youtube.com/watch?v=7NOSDKb0HlU'}
    ],
    'disgust': [
        {'title': 'Nine Inch Nails - Closer', 'youtube_link': 'https://www.youtube.com/watch?v=PTFwQP86BRs'},
        {'title': 'Marilyn Manson - The Beautiful People', 'youtube_link': 'https://www.youtube.com/watch?v=Ypkv0HeUvTc'}
    ],
    'surprise': [
        {'title': 'MGMT - Time to Pretend', 'youtube_link': 'https://www.youtube.com/watch?v=B9dSYgd5Elk'},
        {'title': 'Coldplay - Paradise', 'youtube_link': 'https://www.youtube.com/watch?v=1G4isv_Fylg'}
    ]
}

@app.route('/process_ecg', methods=['POST'])
def process_ecg():
    try:
        ecg_data = request.json['ecgData']
        model_path = os.path.join('assets', 'model_assets', 'random_forest_model.pkl')
        scaler_path = os.path.join('assets', 'model_assets', 'scaler.pkl')
        
        processor = ECGProcessor(
            model_path=model_path,
            scaler_path=scaler_path
        )
        results = processor.process_and_predict(ecg_data)
        
        # Select the top predicted emotion based on the first emotion in results['predictions']
        # since `final_predictions` was used to sort them by mode frequency.
        final_emotion = results['predictions'][0] if results['predictions'] else 'neutral'
        
        # Retrieve songs for the final emotion
        songs_for_emotion = emotion_songs.get(final_emotion, [])
        
        # Return emotions, counts, selected songs, and the final emotion
        return jsonify({
            'emotions': results['predictions'],
            'counts': results['counts'],
            'final_emotion': final_emotion,
            'songs': songs_for_emotion
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
