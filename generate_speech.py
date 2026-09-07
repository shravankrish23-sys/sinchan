import requests

ELEVENLABS_API_KEY = "sk_f3572e577269e2930404917d515e24472c23f06ca0986e1c"
VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"

text = "Hey there! I am your animated character. I can talk, blink, and move naturally. Pretty cool, right?"

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}
data = {
    "text": text,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

response = requests.post(url, json=data, headers=headers)
print("ElevenLabs status code:", response.status_code)
if response.status_code == 200:
    with open("speech.mp3", "wb") as f:
        f.write(response.content)
    print("Saved speech.mp3 successfully!")
else:
    print("ElevenLabs error:", response.text)
