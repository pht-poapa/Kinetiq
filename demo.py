import math

from exercises import EXERCISES
from repetition_counter import new_counter, track_repetition


def demo_analysis(exercise):
    settings = EXERCISES[exercise]
    counter = new_counter()
    angles = []
    high = 175
    low = settings['bent_angle'] - 20

    for frame in range(300):
        time = frame / 30
        phase = (time - 1) % 3
        raw_angle = high

        if time >= 1 and phase < 2.4:
            raw_angle = high - (high - low) * (1 - math.cos(2 * math.pi * phase / 2.4)) / 2

        angle = track_repetition(raw_angle, time, counter, settings)
        angles.append({'time': time, 'angle': angle})

    return {'exercise': exercise, 'side': None, 'source': 'simulation', 'total_frames': 300, 'detected_frames': 0, 'measured_frames': 0, 'duration': 10.0, 'repetitions': len(counter['report']), 'report': counter['report'], 'angles': angles}
