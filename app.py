import os
from flask import Flask, render_template, request, send_file, redirect, send_from_directory, url_for
from PyPDF2 import PdfReader
from googletrans import Translator
from pytube import YouTube
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
import tempfile

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ffmpeg_path = "D:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.converter = ffmpeg_path
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf_to_audio')
def pdf_to_audio():
    return render_template('pdf_to_audio.html')

@app.route('/video_conversion')
def video_conversion():
    return render_template('video_translation.html')

@app.route('/audio_to_text')
def audio_to_text():
    return render_template('audio_to_text.html')

@app.route('/convert', methods=['POST'])
def convert():
  if 'pdf_file' not in request.files:
    return redirect(url_for('index'))

  pdf_file = request.files['pdf_file']
  target_language = request.form.get('target_language')

  if pdf_file.filename == '' or not target_language:
    return redirect(url_for('index'))

  if pdf_file:
    # Create the "uploads" directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
      os.mkdir(app.config['UPLOAD_FOLDER'])

    # Explicitly specify a temporary directory for PDF processing
    temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    # Check if the file is a PDF
    if pdf_file.filename.endswith('.pdf'):
      # Create a temporary PDF path within the specified temp directory
      pdf_path = os.path.join(temp_dir, 'input.pdf')
      pdf_file.save(pdf_path)

      # Extract text from the PDF
      text = ''
      pdf = PdfReader(pdf_path)
      for page in pdf.pages:
        text += page.extract_text()

      # Translate the text to the target language
      translator = Translator()
      translated_text = translator.translate(text, dest=target_language).text

      # Convert translated text to audio
      tts = gTTS(translated_text)
      audio_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'audio')
      os.makedirs(audio_dir, exist_ok=True)
      audio_path = os.path.join(audio_dir, 'output.mp3')
      tts.save(audio_path)
      print(audio_path)
      # Define the audio URL relative to the "uploads/audio" folder
      audio_url = url_for('audio_file', filename='output.mp3')

      print(audio_url)

      return render_template('pdf_to_audio.html', translated_text=translated_text, audio_url=audio_url)

  return redirect(url_for('pdf_to_audio'))

@app.route('/video_translation', methods=['GET', 'POST'])
def video_translation():
    if request.method == 'POST':
        youtube_url= request.form['youtube_url']
        target_language = request.form['target_language']

        if not youtube_url or not target_language:
            return render_template('video_translation.html', error="Please provide a valid YouTube URL and target language.")

        try:
            # Download the YouTube video
            yt = YouTube(youtube_url)
            stream = yt.streams.filter(only_audio=True).first()
            audio_path = stream.download(output_path=app.config['UPLOAD_FOLDER'])

            # Translate the audio description
            translator = Translator()
            audio_text = translator.translate(yt.description, dest=target_language).text

            # Convert translated text to audio
            tts = gTTS(audio_text)
            audio_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'audio')
            os.makedirs(audio_dir, exist_ok=True)
            audio_output_path = os.path.join(audio_dir, 'video_output.mp3')
            tts.save(audio_output_path)
            audio_url = url_for('audio_file', filename='video_output.mp3')

            # Get the YouTube video ID for embedding
            video_id = yt.video_id

            return render_template('video_translation.html', translated_text=audio_text, video_id=video_id,audio_url=audio_url)
        except Exception as e:
            return render_template('video_translation.html', error="An error occurred during video translation. Please check the provided YouTube URL.")
    return render_template('video_translation.html')

@app.route('/audio_to_text_conversion', methods=['GET', 'POST'])
def audio_to_text_conversion():
    if request.method == 'POST':
        if 'audio_file' not in request.files:
            return redirect(request.url)

        audio_file = request.files['audio_file']

        if audio_file.filename == '':
            return redirect(request.url)

        if not allowed_file(audio_file.filename):
            return "Invalid file format. Please upload an MP3 or WAV file."

        # Create the "uploads" directory if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])

        # Save the uploaded audio file
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_audio.wav')

        # Convert MP3 to WAV using pydub
        audio = AudioSegment.from_file(audio_file, format="mp3")
        audio.export(audio_path, format="wav")

        # Convert the audio to text
        text = convert_audio_to_text(audio_path)
        print(audio_path)

        return render_template('audio_to_text.html', audio_path=audio_path, text=text)

    return render_template('audio_to_text.html')

def convert_audio_to_text(audio_path):
    try:
        # Initialize the recognizer
        recognizer = sr.Recognizer()
        # Convert audio to text
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

            try:
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                return "Speech Recognition could not understand audio"
            except sr.RequestError as e:
                return f"Could not request results from Google Speech Recognition service; {e}"

    except Exception as e:
        print(f"Error during audio-to-text conversion: {e}")
        raise e
    
@app.route('/uploads/audio/<filename>')
def audio_file(filename):
    return send_from_directory('uploads/audio', filename)

if __name__ == '__main__':
  app.run(debug=True)
