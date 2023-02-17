from moviepy.editor import *
from tqdm import tqdm
from pathlib import Path
import argparse

from utils import read_config, CONFIG_DIR

parser = argparse.ArgumentParser()

parser.add_argument('--config', type=str, default='default.yaml',
        help='''Path to the config file (should be located in the config folder).''')
args = parser.parse_args()
config = read_config(CONFIG_DIR / args.config)

RNC_PATH = Path(config['data']['dir'])
CSV_FILE = RNC_PATH / config['data']['examples']
MEDIA_PATH = RNC_PATH / config['data']['media']

def MP4ToMP3(mp4, mp3):
    try:
        FILETOCONVERT = AudioFileClip(mp4)
        FILETOCONVERT.write_audiofile(mp3)
        FILETOCONVERT.close()
    except UnicodeDecodeError:
        os.remove(mp4)

videos = list(MEDIA_PATH.glob('*.mp4'))

for video in videos:
    audio = video.with_suffix('.mp3')
    if not Path(audio).is_file():
        MP4ToMP3(str(video), str(audio))

