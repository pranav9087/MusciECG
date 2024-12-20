# MusicECG

MusicECG is a React Native app built using Expo that automatically detects your emotions from ECG data collected by a Samsung smartwatch and recommends music based on these emotions. This project combines the power of mobile development and AI to create a personalized music experience.

## Features
- **Emotion Detection**: Analyze ECG data to determine your current emotional state.
- **Music Recommendations**: Receive music suggestions tailored to your mood.
- **Seamless Integration**: Designed for Samsung smartwatches, with plans to support more devices in the future.

---

## Getting Started

Follow these steps to set up the project and run the app locally.

### Prerequisites
Ensure you have the following installed on your system:
- Node.js and npm
- Python 3
- Expo CLI (`npm install -g expo-cli`)
- An Android phone or emulator

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/pranav9087/MusicECG.git
   cd MusicECG
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Set Up the Server**:
   - Navigate to the server directory and run the Python server:
     ```bash
     python server.py
     ```
   - Make a note of your local IP address (e.g., `192.168.x.x`). This will be needed for configuring the app.

4. **Update the Server URL**:
   - Open `app/(tabs)/index.jsx`.
   - Find the line:
     ```javascript
     const SERVER_URL = 'http://192.168.xx.xxx:8000/process_ecg';
     ```
   - Replace `192.168.xx.xxx` with your local IP address.

5. **Run the App**:
   - Start the Expo development server:
     ```bash
     npx expo start
     ```
   - Connect your Android device or emulator:
     - For a physical device, scan the QR code using the Expo Go app.
     - For an emulator, select your emulator from the Expo interface.

6. **Experience MusicECG**:
   - Collect ECG data using your Samsung smartwatch.
   - Allow the app to process the data and recommend music based on your emotional state.

---

## Project Structure
- **app/**: Contains the main application code.
- **server.py**: Handles requests and processes ECG data.
- **assets/**: Stores images and other static resources.

---

## Contributing
We welcome contributions! Feel free to fork this repository and submit pull requests. Here are some ways you can contribute:
- Add support for more devices.
- Improve emotion detection algorithms.
- Enhance the user interface.

---

## Troubleshooting

### Common Issues:
1. **Error: Unable to connect to server**
   - Ensure the server is running (`server.py`).
   - Check that the `SERVER_URL` in `index.jsx` matches your local IP address.

2. **Expo app not loading on device**
   - Ensure your phone and computer are on the same network.
   - Restart the Expo development server.

### Support
If you encounter any issues or have questions, feel free to open an issue in this repository.

---

## Acknowledgements
- React Native and Expo for providing a robust development framework.
