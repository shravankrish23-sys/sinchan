import imageio_ffmpeg
import subprocess

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
for t in [1.8, 3.2, 5.0]:
    out_name = f"debug_frames/rigged_frame_{t}s.png"
    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss", str(t),
        "-i", "rhubarb_character_rigged_final.mp4",
        "-vframes", "1",
        out_name
    ]
    subprocess.run(cmd, check=True)
    print(f"Extracted {out_name}")
