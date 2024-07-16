import numpy as np
import wave
import matplotlib.pyplot as plt

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
