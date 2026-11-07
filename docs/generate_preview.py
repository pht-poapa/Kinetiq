from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from demo import demo_analysis
from exercises import EXERCISES


figure, axes = plt.subplots(3, 1, figsize = (10, 7), sharex = True, constrained_layout = True)
figure.patch.set_facecolor('#0d1522')
figure.suptitle('Kinetiq · simulated counter demo', color = '#edf4fa', fontsize = 18)

for axis, exercise in zip(axes, EXERCISES):
    analysis = demo_analysis(exercise)
    settings = EXERCISES[exercise]
    times = [row['time'] for row in analysis['angles']]
    angles = [row['angle'] for row in analysis['angles']]
    axis.set_facecolor('#162235')
    axis.plot(times, angles, color = '#45d6af', linewidth = 2)
    axis.axhline(settings['bent_angle'], color = '#f0b66b', linestyle = '--', linewidth = 1)
    axis.axhline(settings['extended_angle'], color = '#9fb4ce', linestyle = '--', linewidth = 1)
    axis.set_title(f'{exercise} · 3 simulated repetitions', color = '#edf4fa', loc = 'left')
    axis.set_ylabel('Angle (degrees)', color = '#edf4fa')
    axis.tick_params(colors = '#b9c9db')
    axis.grid(alpha = 0.15)
    for spine in axis.spines.values():
        spine.set_color('#33445b')

axes[-1].set_xlabel('Time (seconds) · simulation, not a video accuracy benchmark', color = '#edf4fa')
figure.savefig(Path(__file__).parent / 'counter-demo.svg')
plt.close(figure)
