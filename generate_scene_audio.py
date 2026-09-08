import os
import requests
import subprocess
import imageio_ffmpeg

ELEVENLABS_API_KEY = "sk_f3572e577269e2930404917d515e24472c23f06ca0986e1c"

# Voice selections:
# Sinchan: Josh (TxGEqnHWrfWFTfGW9XjX) or Antoni (ErXwobaYiN019PkySvjV)
# Grandfather: Arnold (VR6AewLTigWG4xSOukaG) or Daniel (onwK4e9ZLuTAKqWW03F9)
# Cat: Domi (AZnzlk1XvdvUeBnXmlld) or Callum (N2lVS1w4EtoT3dr4eOWO)

dialogues = [
    {
        "character": "sinchan",
        "voice_id": "ErXwobaYiN019PkySvjV",  # Antoni - youthful & clear
        "text": "What is JPEG?",
        "mp3": "audio_sinchan.mp3",
        "wav": "audio_sinchan.wav"
    },
    {
        "character": "grandfather",
        "voice_id": "VR6AewLTigWG4xSOukaG",  # Arnold - deep grandfather
        "text": "Is it alcohol peg?",
        "mp3": "audio_grandfather.mp3",
        "wav": "audio_grandfather.wav"
    },
    {
        "character": "cat",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella - sassy and expressive cat
        "text": "This idiot doesn't know anything! Wait, let me explain JPEG.",
        "mp3": "audio_cat.mp3",
        "wav": "audio_cat.wav"
    }
]

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

for d in dialogues:
    print(f"Generating voice for {d['character']}: '{d['text']}'...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{d['voice_id']}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": d["text"],
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.8
        }
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code != 200:
        print(f"Error for {d['character']}: {r.status_code} - {r.text}")
        continue
    
    with open(d["mp3"], "wb") as f:
        f.write(r.content)
    print(f"Saved {d['mp3']}")
    
    # Convert to 16-bit mono 16kHz WAV for Rhubarb
    subprocess.run([
        ffmpeg_exe, "-y", "-i", d["mp3"],
        "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000",
        d["wav"]
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Converted to {d['wav']}")

print("All audio generated successfully!")
