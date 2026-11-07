import math
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

import imageio.v2 as imageio
import mediapipe as mp
import numpy as np

from exercises import EXERCISES
from pose_analysis import analyze_video


def pose_at_angle(angle, joints):
    landmarks = [SimpleNamespace(x = 0.5, y = 0.5, visibility = 0.1, presence = 1) for index in range(33)]
    radians = math.radians(angle)
    coordinates = [(0.5, 0.5 - 70 / 480), (0.5, 0.5), (0.5 + 70 * math.sin(radians) / 640, 0.5 - 70 * math.cos(radians) / 480)]

    for index, (x, y) in zip(joints, coordinates):
        landmarks[index] = SimpleNamespace(x = x, y = y, visibility = 1, presence = 1)

    return SimpleNamespace(pose_landmarks = [landmarks])


class VideoTests(unittest.TestCase):
    def test_video_report_progress_and_export(self):
        with TemporaryDirectory() as directory:
            input_path = Path(directory) / 'input.mp4'
            output_path = Path(directory) / 'output.mp4'

            with imageio.get_writer(str(input_path), fps = 15, codec = 'libx264') as writer:
                for frame in range(45):
                    writer.append_data(np.zeros((480, 640, 3), dtype = np.uint8))

            for exercise, settings in EXERCISES.items():
                for side in ['Left', 'Right']:
                    with self.subTest(exercise = exercise, side = side):
                        angles = [175] * 15 + [settings['bent_angle'] - 10] * 15 + [175] * 15
                        poses = [pose_at_angle(angle, settings[side.lower()]) for angle in angles]
                        progress = []

                        with patch.object(mp.tasks.vision.PoseLandmarker, 'create_from_options') as create:
                            create.return_value.__enter__.return_value.detect_for_video.side_effect = poses
                            result = analyze_video(input_path, output_path, exercise, side, progress = lambda fraction, seconds: progress.append(fraction))

                        self.assertEqual(result['repetitions'], 1)
                        self.assertEqual(result['measured_frames'], 45)
                        self.assertEqual(result['side'], side.lower())
                        self.assertEqual(len(result['report']), 1)
                        self.assertEqual(progress[-1], 1.0)

                        with imageio.get_reader(str(output_path)) as reader:
                            self.assertEqual(sum(1 for frame in reader), 45)

    def test_real_model_on_blank_video_and_resize(self):
        with TemporaryDirectory() as directory:
            input_path = Path(directory) / 'input.mp4'
            output_path = Path(directory) / 'output.mp4'

            with imageio.get_writer(str(input_path), fps = 10, codec = 'libx264') as writer:
                writer.append_data(np.zeros((1088, 1920, 3), dtype = np.uint8))

            result = analyze_video(input_path, output_path)
            self.assertEqual(result['repetitions'], 0)
            self.assertEqual(result['measured_frames'], 0)

            with imageio.get_reader(str(output_path)) as reader:
                self.assertLessEqual(max(reader.get_data(0).shape[:2]), 960)

    def test_invalid_video_and_duration_limit(self):
        with TemporaryDirectory() as directory:
            input_path = Path(directory) / 'invalid.mp4'
            output_path = Path(directory) / 'output.mp4'
            input_path.write_bytes(b'invalid')

            with self.assertRaises((OSError, ValueError, RuntimeError)):
                analyze_video(input_path, output_path)

            with patch('pose_analysis.imageio.get_reader') as reader:
                reader.return_value.__enter__.return_value.get_meta_data.return_value = {'fps': 30, 'duration': 121}
                with self.assertRaisesRegex(ValueError, '2 minutes'):
                    analyze_video(input_path, output_path)
