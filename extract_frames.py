import os
import imageio_ffmpeg
import subprocess

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs("debug_frames", exist_ok=True)

# Extract frames at specific timestamps (0.5s, 1.5s, 3.2s, 4.5s)
timestamps = [0.5, 1.5, 3.2, 4.5]
for t in timestamps:
    out_name = f"debug_frames/frame_{t}s.png"
    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss", str(t),
        "-i", "rhubarb_character_animated.mp4",
        "-vframes", "1",
        out_name
    ]
    subprocess.run(cmd, check=True)
    print(f"Extracted {out_name}")

print("Frames extracted successfully!")
