import sounddevice as sd

# Define the audio callback function


def audio_callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata


# Start the audio stream
with sd.Stream(channels=2, blocksize=1024, callback=audio_callback):
    print("Playing your voice to your mic. Press Ctrl+C to stop.")
    while True:
        pass
