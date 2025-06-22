import speech_recognition as sr
import pyaudio
import wave


def recoder(email,x):
    chunk = 1024  
    sample_format = pyaudio.paInt16 
    channels = 1
    fs = 44100  
    seconds = 5
    p = pyaudio.PyAudio()
    print('Recording...')
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    frames = []
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()  
    print('Finished recording.')
    wf = wave.open(f'voice/{email}_voice_{x}.wav', 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    return voice_to_text(email,x)

def voice_to_text(email,x):
    r = sr.Recognizer()
    audio_path = f"voice/{email}_voice_{x}.wav"
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return "error1"
    except sr.RequestError as e:
        print(f"Error: {e}")
        return "error1"


# import sqlite3

# # Connect to SQLite database (it will create the file if it doesn't exist)
# conn = sqlite3.connect("users.db")
# cursor = conn.cursor()

# # Create the table
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS users (
#     name TEXT,
#     email TEXT PRIMARY KEY,
#     phone TEXT,
#     pin TEXT,
#     pattern TEXT,
#     text1 TEXT,
#     text2 TEXT,
#     text3 TEXT
# )
# """)

# # Commit and close connection
# conn.commit()
# conn.close()



