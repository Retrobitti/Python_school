import numpy as np
import sounddevice as sd
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def play_sound(frequency, duration):
    try:
        logging.debug(f"Playing sound with frequency: {frequency}, duration: {duration}")
        sample_rate = 44100  # 44.1kHz
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = 0.5 * np.sin(frequency * 2 * np.pi * t)
        audio = np.int16(wave * 32767)
        sd.play(audio, sample_rate)
        sd.wait()
        logging.debug("Sound playback finished")
    except Exception as e:
        logging.error(f"Error in play_sound: {e}")

# Test the play_sound function
play_sound(100, 0.2)
play_sound(800, 0.2)
