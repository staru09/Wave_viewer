import matplotlib.pyplot as plt
import numpy as np
import wave
import sys

def generate_waveform(audio_path, output_image_path):
    # Read the wave file
    spf = wave.open('C:\Users\91745\OneDrive\Desktop\Wave_viewer\file_example_WAV_1MG.wav', 'r')

    # Extract Raw Audio from Wav File
    signal = spf.readframes(-1)
    signal = np.frombuffer(signal, dtype=np.int16)

    # Get the frame rate
    fs = spf.getframerate()

    # Create the time axis for the waveform
    Time = np.linspace(0, len(signal) / fs, num=len(signal))

    # Plot the waveform
    plt.figure(figsize=(12, 6))
    plt.plot(Time, signal)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid()

    # Save the waveform as an image
    plt.savefig(output_image_path)
    plt.close()

# Usage
generate_waveform('path_to_your_audio_file.wav', 'output_waveform.png')
