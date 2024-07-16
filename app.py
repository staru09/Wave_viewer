import os
from flask import Flask, request, send_file, render_template_string
import matplotlib.pyplot as plt
import numpy as np
import wave
from pydub import AudioSegment
from werkzeug.utils import secure_filename
import librosa
import librosa.display

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.tailwindcss.com?plugins=forms,typography"></script>
            <title>Audio Waveform and Spectrogram Viewer</title>
            <style type="text/tailwindcss">
                @layer base {
                    :root {
                        --background: 0 0% 100%;
                        --foreground: 240 10% 3.9%;
                        --card: 0 0% 100%;
                        --card-foreground: 240 10% 3.9%;
                        --popover: 0 0% 100%;
                        --popover-foreground: 240 10% 3.9%;
                        --primary: 240 5.9% 10%;
                        --primary-foreground: 0 0% 98%;
                        --secondary: 240 4.8% 95.9%;
                        --secondary-foreground: 240 5.9% 10%;
                        --muted: 240 4.8% 95.9%;
                        --muted-foreground: 240 3.8% 46.1%;
                        --accent: 240 4.8% 95.9%;
                        --accent-foreground: 240 5.9% 10%;
                        --destructive: 0 84.2% 60.2%;
                        --destructive-foreground: 0 0% 98%;
                        --border: 240 5.9% 90%;
                        --input: 240 5.9% 90%;
                        --ring: 240 5.9% 10%;
                        --radius: 0.5rem;
                    }
                    .dark {
                        --background: 240 10% 3.9%;
                        --foreground: 0 0% 98%;
                        --card: 240 10% 3.9%;
                        --card-foreground: 0 0% 98%;
                        --popover: 240 10% 3.9%;
                        --popover-foreground: 0 0% 98%;
                        --primary: 0 0% 98%;
                        --primary-foreground: 240 5.9% 10%;
                        --secondary: 240 3.7% 15.9%;
                        --secondary-foreground: 0 0% 98%;
                        --muted: 240 3.7% 15.9%;
                        --muted-foreground: 240 5% 64.9%;
                        --accent: 240 3.7% 15.9%;
                        --accent-foreground: 0 0% 98%;
                        --destructive: 0 62.8% 30.6%;
                        --destructive-foreground: 0 0% 98%;
                        --border: 240 3.7% 15.9%;
                        --input: 240 3.7% 15.9%;
                        --ring: 240 4.9% 83.9%;
                    }
                }
            </style>
        </head>
        <body>
            <div class="flex flex-col items-center justify-center min-h-screen bg-background text-primary-foreground">
                <h1 class="text-3xl font-bold my-8">Audio Waveform and Spectrogram Viewer</h1>
                <div class="w-full max-w-screen-lg bg-card shadow-lg rounded-lg overflow-hidden">
                    <div class="bg-primary p-4">
                        <img id="waveform" src="/waveform" class="w-full h-48 bg-gray-200"/>
                    </div>
                    <div class="bg-primary p-4">
                        <img id="spectrogram" src="/spectrogram" class="w-full h-48 bg-gray-200"/>
                    </div>
                    <div class="p-4">
                        <audio id="audio-player" controls class="w-full bg-primary-foreground text-primary">
                            <source id="audio-source" src="" type="audio/wav">
                            Your browser does not support the audio element.
                        </audio>
                    </div>
                    <div class="flex justify-center p-4">
                        <div class="bg-muted p-4 rounded-lg">
                            <button id="zoom-in" class="bg-secondary text-secondary-foreground px-4 py-2 rounded-lg m-2">Zoom In</button>
                            <button id="zoom-out" class="bg-secondary text-secondary-foreground px-4 py-2 rounded-lg m-2">Zoom Out</button>
                            <button id="zoom-vertical" class="bg-secondary text-secondary-foreground px-4 py-2 rounded-lg m-2">Vertical Zoom In</button>
                            <button id="zoom-vertical-out" class="bg-secondary text-secondary-foreground px-4 py-2 rounded-lg m-2">Vertical Zoom Out</button>
                        </div>
                    </div>
                    <div class="flex justify-center p-4">
                        <label for="file-upload" class="hidden">Upload Audio File:</label>
                        <input id="file-upload" type="file" accept="audio/*" class="hidden" />
                        <button id="upload-btn" class="bg-accent text-accent-foreground px-4 py-2 rounded-lg">Upload</button>
                    </div>
                </div>
            </div>
            <script>
                document.getElementById('upload-btn').addEventListener('click', () => {
                    document.getElementById('file-upload').click();
                });

                document.getElementById('file-upload').addEventListener('change', (event) => {
                    const file = event.target.files[0];
                    const formData = new FormData();
                    formData.append('file', file);

                    fetch('/upload', {
                        method: 'POST',
                        body: formData
                    }).then(response => response.json()).then(data => {
                        document.getElementById('audio-source').src = data.audio_url;
                        document.getElementById('waveform').src = data.waveform_url;
                        document.getElementById('spectrogram').src = data.spectrogram_url;
                        document.getElementById('audio-player').load();
                    });
                });

                let zoomLevel = 1;
                document.getElementById('zoom-in').addEventListener('click', () => {
                    zoomLevel *= 1.2;
                    document.getElementById('waveform').style.transform = `scale(${zoomLevel}, 1)`;
                });

                document.getElementById('zoom-out').addEventListener('click', () => {
                    zoomLevel /= 1.2;
                    document.getElementById('waveform').style.transform = `scale(${zoomLevel}, 1)`;
                });

                let verticalZoomLevel = 1;
                document.getElementById('zoom-vertical').addEventListener('click', () => {
                    verticalZoomLevel *= 1.2;
                    document.getElementById('waveform').style.transform = `scale(1, ${verticalZoomLevel})`;
                });

                document.getElementById('zoom-vertical-out').addEventListener('click', () => {
                    verticalZoomLevel /= 1.2;
                    document.getElementById('waveform').style.transform = `scale(1, ${verticalZoomLevel})`;
                });
            </script>
        </body>
        </html>
    ''')

@app.route('/waveform')
def serve_waveform():
    return send_file('output_waveform.png', mimetype='image/png')

@app.route('/spectrogram')
def serve_spectrogram():
    return send_file('output_spectrogram.png', mimetype='image/png')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Convert to WAV format if necessary
        wav_path = convert_to_wav(filepath)
        generate_waveform(wav_path, 'output_waveform.png')
        generate_spectrogram(wav_path, 'output_spectrogram.png')
        
        audio_url = f'/uploads/{filename}'
        waveform_url = '/waveform'
        spectrogram_url = '/spectrogram'
        
        return {'audio_url': audio_url, 'waveform_url': waveform_url, 'spectrogram_url': spectrogram_url}

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

def generate_waveform(audio_path, output_image_path):
    spf = wave.open(audio_path, 'r')
    signal = spf.readframes(-1)
    signal = np.frombuffer(signal, dtype=np.int16)

    plt.figure(figsize=(12, 6))
    plt.plot(signal)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.savefig(output_image_path, dpi=100)
    plt.close()

def generate_spectrogram(audio_path, output_image_path):
    y, sr = librosa.load(audio_path)
    plt.figure(figsize=(12, 6))
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', fmax=8000)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel-frequency spectrogram')
    plt.savefig(output_image_path, dpi=100)
    plt.close()

if __name__ == '__main__':
    app.run(debug=True)
