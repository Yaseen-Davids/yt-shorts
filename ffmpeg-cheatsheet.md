# FFmpeg Cheatsheet

Quick reference for this project's YouTube Shorts workflow: 4 camera angles, trim, crop to 9:16, stack, concat, and export.

---

## Basics

```bash
# Show file info
ffprobe input.mp4

# Video stream details only
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,duration \
  -of default=noprint_wrappers=1 input.mp4

# Remux without re-encoding (fast, no quality loss)
ffmpeg -i input.mp4 -c copy output.mp4

# Re-encode video, copy audio
ffmpeg -i input.mp4 -c:v libx264 -crf 20 -c:a copy output.mp4
```

---

## Trim / Cut

```bash
# Cut by start + end (put -ss/-to BEFORE -i for fast seek)
ffmpeg -ss 00:00:14 -to 00:00:33 -i input.mp4 -c copy output.mp4

# Cut by start + duration
ffmpeg -ss 00:00:14 -t 19 -i input.mp4 -c copy output.mp4

# Seconds also work
ffmpeg -ss 14 -to 33 -i input.mp4 -c copy output.mp4
```

| Flag | Meaning |
|------|---------|
| `-ss` | Start time |
| `-to` | End time |
| `-t` | Duration (length) |

**This project's trim settings** (`main.py`):

| Clip | Start | End | Duration |
|------|-------|-----|----------|
| cam1, cam2, cam3 (stack) | `00:00:14` | `00:00:33` | 19s |
| cam4 (intro) | `00:00:16` | `00:00:20` | 4s |

---

## Scale / Resize

```bash
# Exact size
ffmpeg -i input.mp4 -vf "scale=1080:1920" output.mp4

# Scale by percentage
ffmpeg -i input.mp4 -vf "scale=iw*0.68:ih*0.68" output.mp4

# Fit inside a box, keep aspect ratio
ffmpeg -i input.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease" output.mp4
```

Useful variables:

| Variable | Meaning |
|----------|---------|
| `iw`, `ih` | Input width / height |
| `ow`, `oh` | Output width / height |

---

## Crop

```bash
# crop=width:height:x:y
ffmpeg -i input.mp4 -vf "crop=1080:1920:0:0" output.mp4

# Center crop 16:9 -> 9:16 (used in this project)
crop=ih*9/16:ih:(iw-ow)/2:0

# Crop top/bottom by percentage (cam4 in Notes)
crop=iw:ih*(1-0.15-0.28):0:ih*0.15
```

**Project crop filter:**

```
crop=ih*9/16:ih:(iw-ow)/2:0,scale=1440:2560
```

This takes a landscape 16:9 clip, center-crops it to 9:16, then scales to 1440x2560.

---

## Color / Effects

```bash
# Brightness + contrast (maps from Adobe +19 brightness, +16 contrast)
eq=brightness=0.10:contrast=1.16

# Fade in / out
fade=t=in:st=0:d=1,fade=t=out:st=9:d=1
```

---

## Overlay / Positioning

Places a smaller clip on a 1080x1920 canvas. Used when stacking cameras at specific x/y positions from `Notes`.

```bash
overlay=x=(1080-w)/2:y=891-(h/2):shortest=1
```

| Part | Meaning |
|------|---------|
| `x=(1080-w)/2` | Center horizontally on a 1080px canvas |
| `y=891-(h/2)` | Place clip center at y=891 (FFmpeg uses top-left, Notes use center) |
| `shortest=1` | Stop when the shorter input ends (prevents infinite encode) |

**Camera positions from Notes:**

| Camera | x (center) | y (center) | Scale |
|--------|------------|------------|-------|
| 1 | 540 | 891 | 68% |
| 2 | 540 | 1629 | 47% |
| 3 | 540 | 360 | 72% |
| 4 | 540 | 960 | 134% |

FFmpeg overlay expressions:

```
cam1: overlay=x=(1080-w)/2:y=891-(h/2):shortest=1
cam2: overlay=x=(1080-w)/2:y=1629-(h/2):shortest=1
cam3: overlay=x=(1080-w)/2:y=360-(h/2):shortest=1
```

---

## Stack / Concat

```bash
# Vertical stack (cam1 + cam2 + cam3)
[cam1][cam2][cam3]vstack=inputs=3,scale=1080:1920,setsar=1[stack]

# Join cam4 intro + stack segment
[cam4_processed][stack_segmented]concat=n=2:v=1:a=0[video_out]

# Audio: cam4 then cam1
[3:a][0:a]concat=n=2:v=0:a=1[audio_out]
```

Always add `setsar=1` before `concat` — mismatched sample aspect ratios cause concat to fail.

---

## Encoding

### CPU — best quality, works everywhere

```bash
-c:v libx264 -crf 20 -pix_fmt yuv420p
```

### Apple Silicon (M1)

```bash
-c:v h264_videotoolbox -b:v 8M -pix_fmt yuv420p
```

### NVIDIA RTX 4060

```bash
-c:v h264_nvenc -preset p5 -cq 20 -pix_fmt yuv420p
```

| Setting | Quality | Notes |
|---------|---------|-------|
| CRF/CQ `18` | Very high | Near visually lossless |
| CRF/CQ `20` | Great default | Current project setting |
| CRF/CQ `23` | Good | Smaller files |
| CRF/CQ `28` | Low | Noticeable compression |

---

## Full Project Workflow

Target output: **1080x1920, 9:16, yuv420p**

Layout:
1. **cam4** plays first (full-screen 9:16)
2. **cam1, cam2, cam3** stacked vertically (each cropped to 9:16)

```bash
ffmpeg -y \
  -ss 00:00:16 -to 00:00:20 -i cam4.mp4 \
  -ss 00:00:14 -to 00:00:33 -i cam1.mp4 \
  -ss 00:00:14 -to 00:00:33 -i cam2.mp4 \
  -ss 00:00:14 -to 00:00:33 -i cam3.mp4 \
  -filter_complex "
    [3:v]crop=ih*9/16:ih:(iw-ow)/2:0,scale=1440:2560,eq=brightness=0.10:contrast=1.16,scale=1080:1920,setsar=1[cam4];
    [0:v]crop=ih*9/16:ih:(iw-ow)/2:0,scale=1440:2560,eq=brightness=0.10:contrast=1.16[cam1];
    [1:v]crop=ih*9/16:ih:(iw-ow)/2:0,scale=1440:2560,eq=brightness=0.10:contrast=1.16[cam2];
    [2:v]crop=ih*9/16:ih:(iw-ow)/2:0,scale=1440:2560,eq=brightness=0.10:contrast=1.16[cam3];
    [cam1][cam2][cam3]vstack=inputs=3,scale=1080:1920,setsar=1[stack];
    [cam4][stack]concat=n=2:v=1:a=0[v];
    [3:a][0:a]concat=n=2:v=0:a=1[a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 20 -pix_fmt yuv420p \
  final_short.mp4
```

Run via Python:

```bash
python3 main.py
```

Output: `./files/converted/final_short.mp4`

---

## Debug / Inspect

```bash
# Check output dimensions and aspect ratio
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,sample_aspect_ratio,display_aspect_ratio \
  -of default=noprint_wrappers=1 ./files/converted/final_short.mp4

# Extract a single frame as image
ffmpeg -ss 00:00:05 -i input.mp4 -frames:v 1 frame.jpg

# Dry-run filtergraph (no output file written)
ffmpeg -v verbose -i input.mp4 -vf "scale=1080:1920" -f null -
```

---

## Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| Encode runs forever | `color=black` canvas has no end | Add `shortest=1` to overlays |
| `concat` fails to configure | Mismatched SAR between segments | Add `setsar=1` before concat |
| Two `-filter_complex` flags | FFmpeg only uses the last one | Combine into one filter string |
| Trim seems ignored | `-ss` placed after `-i` | Put `-ss`/`-to` before `-i` |
| Quality loss | Re-encoding H.264 -> H.264 | Unavoidable; use low CRF/CQ |
| `UDTA parsing failed` | Harmless metadata warning | Safe to ignore |

---

## Quick Reference

| Task | Command |
|------|---------|
| Trim | `-ss START -to END -i file` |
| Resize | `scale=1080:1920` |
| Crop to 9:16 | `crop=ih*9/16:ih:(iw-ow)/2:0` |
| Brightness/contrast | `eq=brightness=0.10:contrast=1.16` |
| Overlay (centered) | `overlay=x=(1080-w)/2:y=891-(h/2):shortest=1` |
| Stack 3 clips | `vstack=inputs=3` |
| Join segments | `concat=n=2:v=1:a=0` |
| CPU encode | `-c:v libx264 -crf 20` |
| RTX encode | `-c:v h264_nvenc -cq 20` |
| M1 encode | `-c:v h264_videotoolbox` |

---

## Camera Reference

| # | Description | Position (Notes) | Crop |
|---|-------------|------------------|------|
| 1 | Exterior, behind car | y: 891, scale: 68% | 9:16 center |
| 2 | Exterior, opponent car | y: 1629, scale: 47% | 9:16 center |
| 3 | Interior, speedometer | y: 360, scale: 72% | 9:16 center |
| 4 | Pass-by both cars | y: 960, scale: 134% | top 15%, bottom 28% |

Final short layout: **cam4 first (4s) → cam1+2+3 stacked (19s) = ~23s total**
