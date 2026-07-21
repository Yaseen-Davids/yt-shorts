import os
import subprocess

video_path = os.path.join(os.path.dirname(__file__), "audios")

videos = [file for file in os.listdir(video_path) if file.endswith(".mp4")]
if not videos:
    raise ValueError(f"No .mp4 files found in {video_path}")

video_file = videos[0]

command = [
    "ffmpeg",
    "-i", os.path.join(video_path, video_file),
    "-ac", "1",
    "-ar", "44100",
    "-vn",
    os.path.join(video_path, "output.wav")
]

try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    print(f"An error occurred during FFmpeg execution: {e}")