# Shorts

Turn multi-angle drag race footage into a vertical YouTube Short using FFmpeg.

The script takes 4 camera angles of the same drag race, shows the pass-by angle first, then stacks the three remaining angles into a single 9:16 (1080×1920) frame.

## Layout

The final video is a sequence of two segments:

1. **Camera 4** — exterior pass-by of both cars, cropped/scaled to fill the full 1080×1920 frame.
2. **Stacked segment** — cameras 1, 2, and 3 stacked vertically on a black canvas:
   - **Top** — camera 2 (exterior facing opponent car)
   - **Middle** — camera 1 (exterior behind the car)
   - **Bottom** — camera 3 (interior speedometer)

## Requirements

- [FFmpeg](https://ffmpeg.org/) and `ffprobe` available on your `PATH`
- Python 3.8+

Check your install:

```bash
ffmpeg -version
ffprobe -version
```

## Usage

1. Drop exactly **4** `.mp4` camera angle files into `./files/`.

   Files are picked up in **sorted filename order**, so name them so they sort into the intended camera order (`cam1`, `cam2`, `cam3`, `cam4`).

2. Adjust the trim settings in `main.py` if needed:

   ```python
   stack_start = "00:00:14"   # start for the stacked clips (cam1/2/3)
   stack_end   = "00:00:33"   # end for the stacked clips
   cam4_start  = "00:00:17"   # start for the pass-by clip
   cam4_end    = "00:00:20"   # end for the pass-by clip
   ```

3. Run it:

   ```bash
   python main.py
   ```

4. The result is written to `./files/converted/final_short.mp4`.

## How alignment works

The three stacked recordings were started at different moments but **end** at the same real-world instant. The script probes each clip's duration with `ffprobe`, then keeps only the last `min_dur` seconds of each so their tails line up, and applies `stack_start`/`stack_end` inside that common window. This is the FFmpeg equivalent of dragging the clip tails together on a timeline.

## Notes

- The canvas is fixed at 1080×1920 @ 60fps (YouTube Shorts standard).
- All clips get a `brightness=0.10` / `contrast=1.16` color adjustment; camera 2 is additionally cropped (top 15%, bottom 28%).
- Contents of `./files/` are git-ignored.
- See `ffmpeg-cheatsheet.md` for a filter reference and `Notes` for the original layout values from the Adobe project.
