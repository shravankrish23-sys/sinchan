import os
import wave
import json
import numpy as np

def read_wav(filename):
    with wave.open(filename, 'rb') as w:
        params = w.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        data = w.readframes(nframes)
        samples = np.frombuffer(data, dtype=np.int16)
        return samples, framerate

def write_wav(filename, samples, framerate):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(samples.astype(np.int16).tobytes())

samples_boy, sr = read_wav("audio_boy.wav")
samples_gf, _ = read_wav("audio_grandfather.wav")
samples_cat, _ = read_wav("audio_cat.wav")

# Desired dialogue timeline:
# 0.00s - 0.40s: Initial pause (0.4s)
# 0.40s - (0.40 + boy_dur): Boy speaks ("What is JPEG?")
# Pause 0.60s (Grandfather thinks)
# GF speaks ("Is it alcohol peg?")
# Pause 0.55s (Cat reacts/glares)
# Cat speaks ("This idiot doesn't know anything! Wait, let me explain JPEG.")
# Trailing pause 0.80s (comedic timing)

pause_initial = np.zeros(int(0.40 * sr), dtype=np.int16)
pause_gf = np.zeros(int(0.60 * sr), dtype=np.int16)
pause_cat = np.zeros(int(0.55 * sr), dtype=np.int16)
pause_final = np.zeros(int(0.80 * sr), dtype=np.int16)

master_audio = np.concatenate([
    pause_initial,
    samples_boy,
    pause_gf,
    samples_gf,
    pause_cat,
    samples_cat,
    pause_final
])

write_wav("scene_master_dialogue.wav", master_audio, sr)

# Calculate exact time offsets for animation engine
t_boy_start = 0.40
t_boy_end = t_boy_start + len(samples_boy) / sr

t_gf_start = t_boy_end + 0.60
t_gf_end = t_gf_start + len(samples_gf) / sr

t_cat_start = t_gf_end + 0.55
t_cat_end = t_cat_start + len(samples_cat) / sr

total_duration = len(master_audio) / sr

timeline_info = {
    "total_duration": total_duration,
    "sample_rate": sr,
    "boy": {"start": t_boy_start, "end": t_boy_end, "json": "lip_sync_boy.json"},
    "grandfather": {"start": t_gf_start, "end": t_gf_end, "json": "lip_sync_grandfather.json"},
    "cat": {"start": t_cat_start, "end": t_cat_end, "json": "lip_sync_cat.json"}
}

with open("scene_timeline.json", "w") as f:
    json.dump(timeline_info, f, indent=2)

print(f"Master dialogue WAV generated: {total_duration:.2f}s total.")
print(f"Timeline: Boy ({t_boy_start:.2f}s - {t_boy_end:.2f}s) -> GF ({t_gf_start:.2f}s - {t_gf_end:.2f}s) -> Cat ({t_cat_start:.2f}s - {t_cat_end:.2f}s)")
