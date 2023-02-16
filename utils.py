import yaml
from pathlib import Path

CONFIG_DIR = Path('config')

def read_config(file_name):
    with open(file_name, encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config
