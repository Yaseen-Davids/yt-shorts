import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

BOX_X = 2430
BOX_Y = 1390
BOX_WIDTH = 100
BOX_HEIGHT = 40

def read_value(roi):
    enlarged = cv2.resize(
        roi,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    threshold = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    text = pytesseract.image_to_string(
        threshold,
        config=(
            "--psm 7 "
            "-c tessedit_char_whitelist=0123456789."
        )
    )

    text = text.strip().replace(" ", "")

    match = re.search(r"\d+\.\d+", text)

    return match.group() if match else None

def binary_search_frame(video_path, target_value):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames <= 0:
        print("Invalid video or unable to read frame count.")
        return None

    low = 0
    high = total_frames - 1
    found_timestamp = None

    while low <= high:
        mid = (low + high) // 2
        
        # Seek to the middle frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
        ret, frame = cap.read()
        
        if not ret:
            print(f"Error reading frame at index {mid}.")
            break
            
        current_frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1

        roi = frame[
                    BOX_Y:BOX_Y + BOX_HEIGHT,
                    BOX_X:BOX_X + BOX_WIDTH
                ]
            
        detected_value = read_value(roi)

        if detected_value == None:
            low = current_frame_pos + 1
            continue
        
        if detected_value == target_value:
            timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            found_timestamp = timestamp_ms / 1000.0
            print(f"Target value found {target_value} at {current_frame_pos} frame, at {found_timestamp}s")
            break
        elif float(detected_value) < float(target_value):
            # Target is in the upper half
            low = current_frame_pos + 1
        else:
            # Target is in the lower half
            high = current_frame_pos - 1

    cap.release()

    if found_timestamp == None:
        return None

    return float(found_timestamp)

# Usage example
# frame = binary_search_frame('video.mp4', "0.002")
