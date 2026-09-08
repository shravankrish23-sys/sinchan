import os
import json
import subprocess

RHUBARB_EXE = os.path.abspath("rhubarb/Rhubarb-Lip-Sync-1.14.0-Windows/rhubarb.exe")

tracks = [
    {"wav": "audio_sinchan.wav", "json": "lip_sync_sinchan.json", "dialog": "What is JPEG?"},
    {"wav": "audio_grandfather.wav", "json": "lip_sync_grandfather.json", "dialog": "Is it alcohol peg?"},
    {"wav": "audio_cat.wav", "json": "lip_sync_cat.json", "dialog": "This idiot doesn't know anything! Wait, let me explain JPEG."}
]

for t in tracks:
    print(f"Running Rhubarb for {t['wav']}...")
    txt_file = t['wav'].replace('.wav', '.txt')
    with open(txt_file, 'w') as f:
        f.write(t['dialog'])
    
    cmd = [
        RHUBARB_EXE,
        "-r", "phonetic",
        "-f", "json",
        "-o", t['json'],
        "-d", txt_file,
        t['wav']
    ]
    subprocess.run(cmd, check=True)
    with open(t['json'], 'r') as f:
        data = json.load(f)
    print(f"Done {t['json']}: duration = {data['metadata']['duration']}s, cues = {len(data['mouthCues'])}")

print("All Rhubarb lip sync data generated successfully!")
