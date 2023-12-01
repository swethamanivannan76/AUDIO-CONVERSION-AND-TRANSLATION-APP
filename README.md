# AUDIO-CONVERSION-AND-TRANSLATION-APP


This Flask application provides functionalities for multimedia processing, including PDF to audio conversion, video translation, and audio to text conversion.

## Features

- **PDF to Audio Conversion:** Upload a PDF file, translate its text to the desired language, and convert it to an audio file.
- **Video Translation:** Enter a YouTube video URL, translate its description, and generate an audio file with the translated text.
- **Audio to Text Conversion:** Upload an audio file (MP3 or WAV), and convert its speech content to text.

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/flask-multimedia-processing.git
   ```

   Install the required Python packages:

 ```bash
pip install -r requirements.txt
   ```
Run the application:

 ```bash
python app.py
   ```
The application will be accessible at http://localhost:5000/.

## Dependencies
Flask
PyPDF2
googletrans
pytube
gtts
pydub
speech_recognition
Feel free to explore and use these multimedia processing features in your projects.
