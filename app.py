import os
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from wave_generator import generate_waveform
from spectogram import generate_spectrogram
from pydub import AudioSegment

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/waveform')
def serve_waveform():
    return send_file('static/output_waveform.png', mimetype='image/png')

@app.route('/spectrogram')
def serve_spectrogram():
    return send_file('static/output_spectrogram.png', mimetype='image/png')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Convert to WAV format if necessary
        wav_path = convert_to_wav(filepath)
        generate_waveform(wav_path, 'static/output_waveform.png')
        generate_spectrogram(wav_path, 'static/output_spectrogram.png')
        
        audio_url = f'/uploads/{filename}'
        waveform_url = '/waveform'
        spectrogram_url = '/spectrogram'
        
        return jsonify({'audio_url': audio_url, 'waveform_url': waveform_url, 'spectrogram_url': spectrogram_url})

def convert_to_wav(audio_path):
    # Extract the file extension
    file_ext = os.path.splitext(audio_path)[1].lower()
    wav_path = audio_path

    if file_ext != '.wav':
        # Convert the file to WAV using pydub
        audio = AudioSegment.from_file(audio_path)
        wav_path = audio_path.replace(file_ext, '.wav')
        audio.export(wav_path, format='wav')

    return wav_path

if __name__ == '__main__':
    app.run(debug=True)
