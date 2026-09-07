import imageio_ffmpeg
import subprocess

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
for t in [1.5, 3.2]:
    out_name = f"debug_frames/v2_frame_{t}s.png"
    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss", str(t),
        "-i", "rhubarb_character_animated_v2.mp4",
        "-vframes", "1",
        out_name
    ]
    subprocess.run(cmd, check=True)
    print(f"Extracted {out_name}")
