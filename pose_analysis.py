import math

import cv2
import imageio.v2 as imageio
import mediapipe as mp

from exercises import EXERCISES
from repetition_counter import new_counter, track_repetition
from model_setup import ensure_model


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


def joint_angle(landmarks, joints, width, height):
    start, middle, end = [landmarks[index] for index in joints]

    for point in [start, middle, end]:
        if not all(math.isfinite(value) for value in [point.x, point.y, point.visibility, point.presence]):
            return None
        if point.visibility < 0.5 or point.presence < 0.5:
            return None
        if not (0 <= point.x < 1 and 0 <= point.y < 1):
            return None

    first = ((start.x - middle.x) * width, (start.y - middle.y) * height)
    second = ((end.x - middle.x) * width, (end.y - middle.y) * height)
    length = math.hypot(*first) * math.hypot(*second)

    if length == 0:
        return None

    dot_product = first[0] * second[0] + first[1] * second[1]
    cosine = max(-1, min(1, dot_product / length))
    return math.degrees(math.acos(cosine))


def choose_side(landmarks, settings, width, height):
    best_side = None
    best_score = -1

    for side in ['left', 'right']:
        joints = settings[side]

        if joint_angle(landmarks, joints, width, height) is not None:
            score = min(min(landmarks[i].visibility, landmarks[i].presence) for i in joints)

            if score > best_score:
                best_side = side
                best_score = score

    return best_side


def analyze_video(input_path, output_path, exercise = 'Squat', side = 'Auto', progress = None):
    if exercise not in EXERCISES:
        raise ValueError('Choose one of the supported exercises.')

    settings = EXERCISES[exercise]

    if side not in ['Auto', 'Left', 'Right']:
        raise ValueError('Choose Auto, Left or Right for the tracked side.')
    if exercise == 'Biceps curl (single arm)' and side == 'Auto':
        raise ValueError('Choose the working arm for single-arm curls.')

    model_path = ensure_model()

    base_options = mp.tasks.BaseOptions(model_asset_path = str(model_path))
    options = mp.tasks.vision.PoseLandmarkerOptions(base_options = base_options, running_mode = mp.tasks.vision.RunningMode.VIDEO)

    total_frames = 0
    detected_frames = 0
    last_timestamp = -1
    counter = new_counter()
    measured_frames = 0
    tracked_side = None if side == 'Auto' else side.lower()
    angles = []

    with imageio.get_reader(str(input_path), format = 'FFMPEG') as reader:
        metadata = reader.get_meta_data()
        fps = metadata['fps']
        duration = metadata.get('duration', 0)

        if not math.isfinite(fps) or fps <= 0:
            raise ValueError('The video has an invalid frame rate.')
        if duration > 120:
            raise ValueError('Please upload a video of at most 2 minutes.')

        with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:
            with imageio.get_writer(str(output_path), fps = fps, codec = 'libx264') as writer:
                for index, frame in enumerate(reader):
                    if index / fps >= 120:
                        raise ValueError('Please upload a video of at most 2 minutes.')

                    height, width = frame.shape[:2]
                    scale = min(1, 960 / max(height, width))
                    size = (max(16, round(width * scale / 16) * 16), max(16, round(height * scale / 16) * 16))
                    frame = cv2.resize(frame, size)
                    height, width = frame.shape[:2]
                    timestamp = max(round(index * 1000 / fps), last_timestamp + 1)
                    last_timestamp = timestamp

                    image = mp.Image(image_format = mp.ImageFormat.SRGB, data = frame)
                    result = landmarker.detect_for_video(image, timestamp)
                    angle = None

                    if result.pose_landmarks:
                        landmarks = result.pose_landmarks[0]
                        detected_frames += 1

                        if tracked_side is None:
                            tracked_side = choose_side(landmarks, settings, width, height)

                        if tracked_side is not None:
                            angle = joint_angle(landmarks, settings[tracked_side], width, height)

                        frame = draw_pose(frame, landmarks)

                    if angle is not None:
                        measured_frames += 1

                    angle = track_repetition(angle, index / fps, counter, settings)
                    repetitions = len(counter['report'])
                    angles.append({'time': index / fps, 'angle': angle})

                    joint = settings['joint']
                    angle_text = f'{joint} angle: unavailable' if angle is None else f'{joint} angle: {angle:.0f} deg'
                    cv2.putText(frame, f'Reps: {repetitions}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, angle_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    writer.append_data(frame)
                    total_frames += 1

                    if progress is not None and (index % max(1, round(fps / 2)) == 0):
                        fraction = min(0.99, total_frames / fps / duration) if duration > 0 and math.isfinite(duration) else 0
                        progress(fraction, total_frames / fps)

    if total_frames == 0:
        raise ValueError('The video contains no readable frames.')

    if progress is not None:
        progress(1.0, total_frames / fps)

    return {'exercise': exercise, 'side': tracked_side, 'source': 'video', 'total_frames': total_frames, 'detected_frames': detected_frames, 'measured_frames': measured_frames, 'duration': total_frames / fps, 'repetitions': len(counter['report']), 'report': counter['report'], 'angles': angles}
