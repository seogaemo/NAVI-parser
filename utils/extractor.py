import io
import cv2


class FrameExtractor:
    def __init__(self, videoPath):
        self.videoPath = videoPath
        self.cap = cv2.VideoCapture(videoPath)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {videoPath}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    def __del__(self):
        self.release()

    def extractFrame(self, duration):
        frameNumber = int(self.fps * duration)

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frameNumber)

        ret, frame = self.cap.read()
        if not ret:
            raise ValueError(
                f"Failed to capture at {duration}@{self.videoPath}"
            )

        success, buffer = cv2.imencode(
            ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40]
        )

        if not success:
            raise ValueError("Failed to encode frame.")

        return io.BytesIO(buffer)

    def release(self):
        self.cap.release()
