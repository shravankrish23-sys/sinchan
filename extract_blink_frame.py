import imageio_ffmpeg
import subprocess

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
out_name = "debug_frames/final_blink_frame.png"
cmd = [
    ffmpeg_exe,
    "-y",
    "-ss", "1.26",
    "-i", "rhubarb_character_rigged_final.mp4",
    "-vframes", "1",
    out_name
]
subprocess.run(cmd, check=True)
print("Extracted final blink frame!")
