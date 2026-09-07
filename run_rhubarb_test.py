import os
import subprocess
import requests
import miniaudio

ELEVENLABS_API_KEY = "sk_f3572e577269e2930404917d515e24472c23f06ca0986e1c"
VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"
DIALOG_TEXT = "Hey there! I am your animated character. With Rhubarb lip sync, my mouth moves perfectly with every word I say. Pretty awesome, right?"

# 1. Save dialog text
with open("dialog.txt", "w", encoding="utf-8") as f:
    f.write(DIALOG_TEXT)

mp3_path = "speech.mp3"
wav_path = "speech.wav"

if not os.path.exists(mp3_path):
    print("Generating speech from ElevenLabs...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": DIALOG_TEXT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    r = requests.post(url, json=data, headers=headers)
    if r.status_code == 200:
        with open(mp3_path, "wb") as f:
            f.write(r.content)
        print("Saved speech.mp3!")
    else:
        print("ElevenLabs error:", r.status_code, r.text)
        exit(1)

print("Decoding MP3 to WAV using miniaudio...")
decoded = miniaudio.decode_file(mp3_path)
miniaudio.wav_write_file(wav_path, decoded)
print(f"Created {wav_path} (Sample Rate: {decoded.sample_rate}Hz, Channels: {decoded.nchannels}, Duration: {decoded.duration:.2f}s)")

# 2. Run Rhubarb Lip Sync
rhubarb_exe = r"D:\Rim\rhubarb\Rhubarb-Lip-Sync-1.14.0-Windows\rhubarb.exe"
output_json = "lip_sync.json"

cmd = [
    rhubarb_exe,
    "-r", "phonetic",
    "-f", "json",
    "-d", "dialog.txt",
    "-o", output_json,
    wav_path
]

print("\nRunning Rhubarb Lip Sync on speech.wav...")
result = subprocess.run(cmd, capture_output=True, text=True)
print("Rhubarb exit code:", result.returncode)
if result.stdout:
    print("Stdout:", result.stdout)
if result.stderr:
    print("Stderr:", result.stderr)

if os.path.exists(output_json):
    with open(output_json, "r") as f:
        print("\n--- Generated Lip Sync JSON ---")
        print(f.read())
