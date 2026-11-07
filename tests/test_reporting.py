import csv
import unittest
from io import StringIO

from demo import demo_analysis
from exercises import EXERCISES
from reporting import report_csv


class ReportingTests(unittest.TestCase):
    def test_demo_reports_three_cycles_for_each_exercise(self):
        for exercise in EXERCISES:
            with self.subTest(exercise = exercise):
                result = demo_analysis(exercise)
                self.assertEqual(result['repetitions'], 3)
                self.assertEqual(result['source'], 'simulation')
                self.assertEqual(result['measured_frames'], 0)
                self.assertEqual(result['detected_frames'], 0)
                self.assertEqual(len(result['angles']), 300)

    def test_csv_preserves_source_and_report_values(self):
        result = demo_analysis('Push-up')
        rows = list(csv.DictReader(StringIO(report_csv(result).decode('utf-8-sig'))))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]['source'], 'simulation')
        self.assertEqual(rows[0]['exercise'], 'Push-up')
        self.assertAlmostEqual(float(rows[0]['duration_seconds']), result['report'][0]['duration_seconds'])
        self.assertNotIn('', rows[0])
