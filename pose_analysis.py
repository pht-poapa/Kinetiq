from pathlib import Path
import math

import cv2
import imageio.v2 as imageio
import mediapipe as mp


CONNECTIONS = [
    (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16),
    (11, 23), (12, 24),
    (23, 24),
    (23, 25), (25, 27),
    (24, 26), (26, 28),
    (27, 29), (29, 31), (27, 31),
    (28, 30), (30, 32), (28, 32)
]


def draw_pose(frame, landmarks):
    height, width = frame.shape[:2]
    points = {}

    for index in range(11, 33):
        landmark = landmarks[index]

        if landmark.visibility >= 0.5 and landmark.presence >= 0.5:
            if 0 <= landmark.x < 1 and 0 <= landmark.y < 1:
                points[index] = (int(landmark.x * width), int(landmark.y * height))

    for start, end in CONNECTIONS:
        if start in points and end in points:
            cv2.line(frame, points[start], points[end], (0, 255, 0), 3)

    for point in points.values():
        cv2.circle(frame, point, 5, (255, 255, 255), -1)

    return frame


def analyze_video(input_path, output_path):
    model_path = Path(__file__).parent / 'models' / 'pose_landmarker_lite.task'
    base_options = mp.tasks.BaseOptions(model_asset_path = str(model_path))
    options = mp.tasks.vision.PoseLandmarkerOptions(base_options = base_options, running_mode = mp.tasks.vision.RunningMode.VIDEO)

    total_frames = 0
    detected_frames = 0
    last_timestamp = -1

    with imageio.get_reader(str(input_path), format = 'FFMPEG') as reader:
        fps = reader.get_meta_data()['fps']

        if not math.isfinite(fps) or fps <= 0:
            raise ValueError('The video has an invalid frame rate.')

        with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:
            with imageio.get_writer(str(output_path), fps = fps, codec = 'libx264') as writer:
                for index, frame in enumerate(reader):
                    frame = frame.copy()
                    timestamp = max(round(index * 1000 / fps), last_timestamp + 1)
                    last_timestamp = timestamp

                    image = mp.Image(image_format = mp.ImageFormat.SRGB, data = frame)
                    result = landmarker.detect_for_video(image, timestamp)

                    if result.pose_landmarks:
                        frame = draw_pose(frame, result.pose_landmarks[0])
                        detected_frames += 1

                    writer.append_data(frame)
                    total_frames += 1

    if total_frames == 0:
        raise ValueError('The video contains no readable frames.')

    return total_frames, detected_frames