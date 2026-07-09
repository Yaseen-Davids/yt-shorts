import os
import subprocess

# --- TRIM SETTINGS ---
# Clips 1, 2, 3 share the same start/end (measured from the aligned window)
stack_start = "00:00:17"   # start for cam1, cam2, cam3
stack_end   = "00:00:35"   # end for cam1, cam2, cam3

# Clip 4 has its own start/end
cam4_start  = "00:00:18"
cam4_end    = "00:00:22"
# ---

# Ensure your directory structure exists
os.makedirs("./files/converted", exist_ok=True)

# Map file names to their respective camera numbers based on sorting
files = sorted([f for f in os.listdir("./files") if f.endswith(".mp4")])

if len(files) < 4:
    raise ValueError(f"Found {len(files)} MP4 files. Need exactly 4 camera angle files.")

# Map clips to variables for easier filtergraph reading
cam1 = os.path.join("./files", files[0])
cam2 = os.path.join("./files", files[1])
cam3 = os.path.join("./files", files[2])
cam4 = os.path.join("./files", files[3])
output_file = "./files/converted/final_short.mp4"

def get_duration(path):
  command = [
    'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', path
  ]
  return float(subprocess.check_output(command).decode('utf-8'))

cam1_duration = get_duration(cam1)
cam2_duration = get_duration(cam2)
cam3_duration = get_duration(cam3)

def to_seconds(ts):
  h, m, s = ts.split(":")
  return int(h) * 3600 + int(m) * 60 + float(s)

stack_start_sec = to_seconds(stack_start)
stack_end_sec   = to_seconds(stack_end)
clip_len        = stack_end_sec - stack_start_sec

# The three clips end at the same real moment, so the extra length on the
# longer clips sits at their start. Align the tails by keeping only the last
# min_dur seconds of each clip, then apply stack_start/stack_end inside that
# common window.
min_dur = min(cam1_duration, cam2_duration, cam3_duration)

CONTRAST = 1.3
BRIGHTNESS = 0.1

def aligned_ss(clip_dur):
  return (clip_dur - min_dur) + stack_start_sec

# --- ADOBE TO FFMPEG FILTERGRAPH TRANSLATION ---
# Base canvas is assumed 1080x1920 (YouTube Shorts standard 9:16)
filter_complex = (
  # 1. Process Camera 4
  f"[3:v]crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920:flags=lanczos,eq=brightness={BRIGHTNESS}:contrast={CONTRAST}[cam4_processed];"

  # 2. Process Camera 1, 2, 3
  f"[0:v]scale=iw*0.68:ih*0.68:flags=lanczos,eq=brightness={BRIGHTNESS}:contrast={CONTRAST}[cam1_scaled];"
  f"[1:v]crop=iw:ih*(1-0.15-0.28):0:ih*0.15,scale=iw*0.72:ih*0.72:flags=lanczos,eq=brightness={BRIGHTNESS}:contrast={CONTRAST}[cam2_scaled];"
  f"[2:v]scale=iw*0.47:ih*0.47:flags=lanczos,eq=brightness={BRIGHTNESS}:contrast={CONTRAST}[cam3_scaled];"

  # 3. Create a black canvas
  "color=s=1080x1920:c=black:r=60[canvas_stack];"
  "[canvas_stack][cam3_scaled]overlay=x=(1080-w)/2:y=1629-(h/2):shortest=1[tmp1];"
  "[tmp1][cam1_scaled]overlay=x=(1080-w)/2:y=891-(h/2):shortest=1[tmp2];"
  "[tmp2][cam2_scaled]overlay=x=(1080-w)/2:y=290-(h/2):shortest=1[stack_segment];"

  # 4. Combine Camera 4 and the stacked segment
  "[cam4_processed][stack_segment]concat=n=2:v=1:a=0[video_out];"

  "[3:a][0:a]concat=n=2:v=0:a=1[audio_out];"
)

# Build the FFmpeg command
command = [
  'ffmpeg', '-y',
  '-ss', str(aligned_ss(cam1_duration)), '-t', str(clip_len), '-i', cam1,
  '-ss', str(aligned_ss(cam2_duration)), '-t', str(clip_len), '-i', cam2,
  '-ss', str(aligned_ss(cam3_duration)), '-t', str(clip_len), '-i', cam3,
  '-ss', cam4_start,  '-to', cam4_end,  '-i', cam4,
  '-filter_complex', filter_complex,
  '-map', '[video_out]',
  '-map', '[audio_out]',
  '-c:v', 'libx264',
  '-crf', '16',
  '-pix_fmt', 'yuv420p',
  '-preset', 'slow',
  output_file
]

print("Processing your YouTube Short via FFmpeg layout complex...")
try:
    subprocess.run(command, check=True)
    print(f"Success! Video exported to: {output_file}")
except subprocess.CalledProcessError as e:
    print(f"An error occurred during FFmpeg execution: {e}")