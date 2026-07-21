import math
import os
import shutil

from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class AudioAnalysisConfig:
    window_size: float = 0.1  # seconds
    min_speaking_duration: float = 0.2  # seconds
    volume_threshold: float = 0.001  # relative threshold
    merge_threshold: float = 0.3  # seconds, max gap to merge

def normalize_volume(volume: float, max_volume: float) -> float:
    return volume / max_volume if max_volume > 0 else 0

def find_speaking(
    audio_clip,
    config: AudioAnalysisConfig = AudioAnalysisConfig()
) -> List[Tuple[float, float]]:
    """
    Find speaking intervals in an audio clip by detecting transitions between silence and speech.
    
    Args:
        audio_clip: Audio clip object with properties: end, subclip(), max_volume()
        config: Configuration parameters for analysis
        
    Returns:
        List of tuples containing (start_time, end_time) for each speaking interval
    """
    # Calculate number of windows
    num_windows = math.floor(audio_clip.end / config.window_size)
    if num_windows == 0:
        return []

    # Find maximum volume in clip for normalization
    max_volume = max(
        audio_clip.subclip(i * config.window_size, (i + 1) * config.window_size).max_volume()
        for i in range(num_windows)
    )

    # Process windows and detect silence/speech
    window_is_silent = []
    for i in range(num_windows):
        start_time = i * config.window_size
        end_time = (i + 1) * config.window_size
        
        segment = audio_clip.subclip(start_time, end_time)
        volume = segment.max_volume()
        normalized_volume = normalize_volume(volume, max_volume)
        
        window_is_silent.append(normalized_volume < config.volume_threshold)

    # Find speaking intervals
    speaking_start = None
    speaking_intervals = []

    # Handle speaking at start of clip
    if not window_is_silent[0]:
        speaking_start = 0

    # Process transitions
    for i in range(len(window_is_silent)):
        is_silent = window_is_silent[i]
        current_time = i * config.window_size
        
        if speaking_start is None and not is_silent:
            # Start of new speaking interval
            speaking_start = current_time
        
        elif speaking_start is not None and is_silent:
            # End of speaking interval
            speaking_end = current_time
            
            # Only add if duration meets minimum threshold
            if speaking_end - speaking_start >= config.min_speaking_duration:
                new_interval = (speaking_start, speaking_end)
                
                # Merge with previous interval if gap is small enough
                if (speaking_intervals and 
                    new_interval[0] - speaking_intervals[-1][1] <= config.merge_threshold):
                    speaking_intervals[-1] = (speaking_intervals[-1][0], new_interval[1])
                else:
                    speaking_intervals.append(new_interval)
            
            speaking_start = None

    # Handle speaking at end of clip
    if speaking_start is not None:
        speaking_end = audio_clip.end
        if speaking_end - speaking_start >= config.min_speaking_duration:
            new_interval = (speaking_start, speaking_end)
            
            # Check for merging with previous interval
            if (speaking_intervals and 
                new_interval[0] - speaking_intervals[-1][1] <= config.merge_threshold):
                speaking_intervals[-1] = (speaking_intervals[-1][0], new_interval[1])
            else:
                speaking_intervals.append(new_interval)

    return speaking_intervals


def trim_silence(folder_path, processed_folder):
    # Loop through the files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if it is a file
        if os.path.isfile(file_path):
            vid = VideoFileClip(file_path)
            intervals_to_keep = find_speaking(vid.audio)
            vid.close()

            for indx, interval in enumerate(intervals_to_keep):
                [start_time, end_time] = interval

                file, ext = os.path.splitext(filename)
                cut_output = f"{file}.mp4"
                ffmpeg_extract_subclip(
                    file_path, start_time, end_time, targetname=cut_output
                )

                # Move the file to the processed folder
                shutil.move(
                    cut_output,
                    os.path.join(processed_folder, cut_output)
                )
                print("Moved", cut_output)
