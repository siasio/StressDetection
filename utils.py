import yaml
from pathlib import Path

CONFIG_DIR = Path('./config')

def read_config(file_name):
    with open(file_name, encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

def get_basename(path: Path):
    # When using RNC on different platforms, the paths which were saved in a csv with platform-specific separators
    # are incorrectly loaded by an RNC corpus.
    return str(path).rsplit('/')[-1].rsplit('\\')[-1]
