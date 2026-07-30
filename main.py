import os
from trimsilence import trim_silence
from process import process_vid

# Step 1. First trim the clips by removing non sound video
# Step 2. Process the trimmed videos
# Step 3. Remove all trimmed videos

files = os.listdir("files")
files_path = os.path.join(os.path.dirname(__file__), "files")

for folder in files:
  if os.path.isdir(os.path.join(files_path, folder)):
    # check if folder has already been trimmed
    if os.path.exists(os.path.join(files_path, f"trimmed_{folder}")):
      continue

    # check if folder is a trimmed folder
    if "trimmed" in folder:
      continue

    input_path = os.path.join(files_path, folder)

    folder_name = os.path.basename(input_path)
    output_folder = f"trimmed_{folder_name}"
    output_path = os.path.join(files_path, output_folder)

    os.mkdir(output_path)

    trim_silence(input_path, output_path)

for folder in os.listdir("files"):
  filename = folder.split("_", 1)[-1]

  if not os.path.isfile(folder):
    # check if folder is a trimmed folder
    if "trimmed" in folder:
      if os.path.exists(os.path.join(files_path, f"{filename}.mp4")):
        continue

      input_path = os.path.join(files_path, folder)
      output_path = os.path.join(files_path)

      process_vid(input_path, output_path, filename)