import cv2
import tempfile

def extract_frame_from_video(uploaded_file):
    """
    Extracts middle frame from uploaded video.
    """
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    cap = cv2.VideoCapture(tfile.name)

    if not cap.isOpened():
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle = total_frames // 2

    cap.set(cv2.CAP_PROP_POS_FRAMES, middle)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None

    return frame
