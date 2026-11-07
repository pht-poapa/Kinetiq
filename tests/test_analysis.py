import unittest
from types import SimpleNamespace

from exercises import EXERCISES
from pose_analysis import choose_side, joint_angle, update_position


def make_landmarks(joints, visibility = 1):
    landmarks = [SimpleNamespace(x = 0.5, y = 0.5, visibility = 0.1, presence = 1) for index in range(33)]
    coordinates = [(0.5, 0.2), (0.5, 0.5), (0.5, 0.8)]

    for index, (x, y) in zip(joints, coordinates):
        landmarks[index] = SimpleNamespace(x = x, y = y, visibility = visibility, presence = 1)

    return landmarks


def count_repetitions(angles, settings):
    position = 'waiting'
    repetitions = 0

    for angle in angles:
        position, completed = update_position(angle, position, settings)
        repetitions += completed

    return repetitions


class AnalysisTests(unittest.TestCase):
    def test_counting_for_each_exercise(self):
        for exercise, settings in EXERCISES.items():
            extended = settings['extended_angle'] + 5
            bent = settings['bent_angle'] - 5
            middle = (extended + bent) / 2
            cases = [
                ([extended, extended, extended], 0),
                ([extended, middle, bent, bent, middle, extended], 1),
                ([extended, bent, extended, bent, extended, bent, extended], 3),
                ([bent, bent, extended], 0),
                ([extended, middle, extended], 0),
                ([extended, bent, None, extended], 0),
                ([extended, bent, None, bent, extended], 0),
                ([extended, settings['bent_angle'], extended], 0)
            ]

            for angles, expected in cases:
                with self.subTest(exercise = exercise, angles = angles):
                    self.assertEqual(count_repetitions(angles, settings), expected)

    def test_exercises_use_their_own_thresholds(self):
        angles = [175, 80, 175]
        self.assertEqual(count_repetitions(angles, EXERCISES['Squat']), 1)
        self.assertEqual(count_repetitions(angles, EXERCISES['Push-up']), 1)
        self.assertEqual(count_repetitions(angles, EXERCISES['Biceps curl (single arm)']), 0)

    def test_both_sides_and_joints(self):
        for exercise, settings in EXERCISES.items():
            for side in ['left', 'right']:
                with self.subTest(exercise = exercise, side = side):
                    joints = settings[side]
                    landmarks = make_landmarks(joints)
                    self.assertAlmostEqual(joint_angle(landmarks, joints, 1280, 720), 180)

    def test_pixel_dimensions_are_used(self):
        joints = [11, 13, 15]
        landmarks = make_landmarks(joints)
        landmarks[11].x, landmarks[11].y = 0.3, 0.5
        landmarks[15].x, landmarks[15].y = 0.6, 0.7
        self.assertAlmostEqual(joint_angle(landmarks, joints, 1000, 500), 135)

    def test_unusable_points(self):
        joints = [23, 25, 27]

        for field, value in [('visibility', 0.1), ('presence', 0.1), ('x', 1.2)]:
            with self.subTest(field = field):
                landmarks = make_landmarks(joints)
                setattr(landmarks[27], field, value)
                self.assertIsNone(joint_angle(landmarks, joints, 1280, 720))

        landmarks = make_landmarks(joints)
        landmarks[27].y = landmarks[25].y
        self.assertIsNone(joint_angle(landmarks, joints, 1280, 720))

    def test_auto_selects_visible_usable_side(self):
        for settings in EXERCISES.values():
            landmarks = make_landmarks(settings['left'], visibility = 0.6)
            right_landmarks = make_landmarks(settings['right'], visibility = 0.9)

            for index in settings['right']:
                landmarks[index] = right_landmarks[index]

            self.assertEqual(choose_side(landmarks, settings, 1280, 720), 'right')
            landmarks[settings['right'][2]].x = 1.2
            self.assertEqual(choose_side(landmarks, settings, 1280, 720), 'left')

            landmarks[settings['left'][2]].visibility = 0.1
            self.assertIsNone(choose_side(landmarks, settings, 1280, 720))
