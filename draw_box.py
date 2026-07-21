import cv2

VIDEO_PATH = "video.mp4"
OUTPUT_PATH = "box_preview.jpg"

BOX_X = 2430
BOX_Y = 1390
BOX_WIDTH = 100
BOX_HEIGHT = 40

TIME_SECONDS = 10

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS)
frame_number = int(TIME_SECONDS * fps)

cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

success, frame = cap.read()
cap.release()

if not success:
    raise RuntimeError(f"Could not read the frame at {TIME_SECONDS} seconds")

cv2.rectangle(
    frame,
    (BOX_X, BOX_Y),
    (BOX_X + BOX_WIDTH, BOX_Y + BOX_HEIGHT),
    (0, 255, 0),
    3
)

cv2.imwrite(OUTPUT_PATH, frame)

print(f"Saved frame {frame_number} at {TIME_SECONDS} seconds")