import wave
import numpy as np
import os
import matplotlib.pyplot as plt

audio_path = os.path.join(os.path.dirname(__file__), "audios")
audios = [file for file in os.listdir(audio_path) if file.endswith(".wav")]

def get_audio_levels(wav_path, window_ms=100):
  with wave.open(wav_path, 'rb') as wf:
    sample_rate = wf.getframerate()
    n_frames = wf.getnframes()
    raw = wf.readframes(n_frames)

  samples = np.frombuffer(raw, dtype=np.int16)
  window_size = int(sample_rate * (window_ms / 1000))

  levels = []
  # loop through samples in chunks of window_size
  for i in range(0, len(samples), window_size):
      chunk = samples[i:i + window_size]
      rms = np.sqrt(np.mean(chunk.astype(np.float64) ** 2))
      db = 20 * np.log10(rms + 1e-6)
      timestamp = i / sample_rate

      levels.append([timestamp, db])
      pass

  return levels

audio_file = audios[0]
levels = get_audio_levels(os.path.join(audio_path, audio_file))

timestamps = [t for t, level in levels]
values = [level for t, level in levels]

def detect_acceleration(data):
   i = 0

   while i < len(data):
         
      i=i+1

# print(detect_acceleration(levels))

plt.plot(timestamps, values)
plt.xlabel("Time (seconds)")
plt.ylabel("Audio Level (dB)")
plt.title("Audio Level Over Time")
plt.minorticks_on()
plt.show()