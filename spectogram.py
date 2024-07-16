import os
import matplotlib.pyplot as plt
import numpy as np
import wave
from pydub import AudioSegment
import librosa
import librosa.display

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

generate_spectrogram('file_example_WAV_1MG.wav','output_spectogram.png')