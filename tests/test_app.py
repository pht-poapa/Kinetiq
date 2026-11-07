from io import BytesIO
from pathlib import Path
from unittest.mock import patch
import unittest

from streamlit.testing.v1 import AppTest

from demo import demo_analysis
from exercises import EXERCISES


APP_PATH = Path(__file__).resolve().parents[1] / 'app.py'


def fake_analysis(input_path, output_path, exercise, side, progress = None):
    Path(output_path).write_bytes(b'test output')
    result = demo_analysis(exercise)
    result.update({'source': 'video', 'side': side.lower(), 'measured_frames': 300, 'detected_frames': 300})
    progress(1.0, 10.0)
    return result


class AppTests(unittest.TestCase):
    def test_demo_and_exercise_reset(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        self.assertEqual(len(app.exception), 0)

        for exercise in EXERCISES:
            app.selectbox[0].select(exercise).run()
            self.assertEqual(len(app.metric), 0)
            app.button[0].click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.metric[0].value, '3')
            self.assertEqual(app.metric[1].value, 'Simulated')
            self.assertTrue(any('Simulated joint angles' in message.value for message in app.info))
            app.run()
            self.assertEqual(app.metric[0].value, '3')

    def test_uploaded_video_and_errors(self):
        with patch('streamlit.file_uploader', return_value = BytesIO(b'input')):
            with patch('pose_analysis.analyze_video', side_effect = fake_analysis) as analyze:
                app = AppTest.from_file(str(APP_PATH)).run()

                for exercise in EXERCISES:
                    app.selectbox[0].select(exercise).run()
                    app.selectbox[1].select('Left').run()
                    app.button[1].click().run()
                    self.assertEqual(len(app.exception), 0)
                    self.assertEqual(app.metric[0].value, '3')
                    self.assertEqual(app.metric[1].value, '100%')
                    self.assertEqual(analyze.call_args.args[2:], (exercise, 'Left'))
                    app.selectbox[1].select('Right').run()
                    self.assertEqual(len(app.metric), 0)

                analyze.side_effect = OSError('Invalid MP4')
                app.button[1].click().run()
                self.assertEqual(len(app.exception), 0)
                self.assertEqual(len(app.error), 1)
                self.assertEqual(len(app.metric), 0)
