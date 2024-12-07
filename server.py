from flask import Flask, request, jsonify
import os
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

CSV_DIR = 'csv_files'

if not os.path.exists(CSV_DIR):
    os.makedirs(CSV_DIR)

@app.route('/process_ecg', methods=['POST'])
def process_ecg():
    try:
        ecg_data = request.json['ecgData']
        filename = "ecg_data.csv"
        file_path = os.path.join(CSV_DIR, filename)
        with open(file_path, 'w') as file:
            file.write(ecg_data)
            
        return jsonify({'emotions': ['happy']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)