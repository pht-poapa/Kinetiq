from hashlib import sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from model_setup import ensure_model


class ModelSetupTests(unittest.TestCase):
    def test_download_and_reuse_verified_model(self):
        data = b'test model'
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'models' / 'pose.task'
            with patch('model_setup.MODEL_PATH', path), patch('model_setup.MODEL_SHA256', sha256(data).hexdigest()), patch('model_setup.urlopen', return_value = BytesIO(data)) as download:
                self.assertEqual(ensure_model(), path)
                self.assertEqual(path.read_bytes(), data)
                self.assertEqual(ensure_model(), path)
                download.assert_called_once()
                self.assertEqual(list(path.parent.glob('*.tmp')), [])

    def test_corrupt_download_is_not_saved(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'pose.task'
            with patch('model_setup.MODEL_PATH', path), patch('model_setup.urlopen', return_value = BytesIO(b'corrupt')):
                with self.assertRaises(ValueError):
                    ensure_model()
            self.assertFalse(path.exists())

    def test_corrupt_existing_model_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'pose.task'
            path.write_bytes(b'corrupt')
            with patch('model_setup.MODEL_PATH', path):
                with self.assertRaises(ValueError):
                    ensure_model()
