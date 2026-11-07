from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import urlopen


MODEL_PATH = Path(__file__).parent / 'models' / 'pose_landmarker_lite.task'
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task'
MODEL_SHA256 = '59929e1d1ee95287735ddd833b19cf4ac46d29bc7afddbbf6753c459690d574a'


def ensure_model():
    if MODEL_PATH.is_file():
        if sha256(MODEL_PATH.read_bytes()).hexdigest() == MODEL_SHA256:
            return MODEL_PATH
        raise ValueError('The pose model checksum is incorrect. Delete models/pose_landmarker_lite.task and retry.')

    with urlopen(MODEL_URL, timeout = 30) as response:
        data = response.read()

    if sha256(data).hexdigest() != MODEL_SHA256:
        raise ValueError('The downloaded model checksum is incorrect.')

    MODEL_PATH.parent.mkdir(parents = True, exist_ok = True)

    with NamedTemporaryFile(dir = MODEL_PATH.parent, suffix = '.tmp', delete = False) as temporary_file:
        temporary_file.write(data)
        temporary_path = Path(temporary_file.name)

    try:
        temporary_path.replace(MODEL_PATH)
    finally:
        temporary_path.unlink(missing_ok = True)

    return MODEL_PATH


if __name__ == '__main__':
    print(ensure_model())
