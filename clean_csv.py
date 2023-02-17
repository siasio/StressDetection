import pandas as pd
import argparse
import os
from pathlib import Path

from utils import read_config, CONFIG_DIR

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default='default.yaml',
        help='''Path to the config file (should be located in the config folder).''')
args = parser.parse_args()
config = read_config(CONFIG_DIR / args.config)

RNC_PATH = Path(config['data']['dir'])
CSV_FILE = RNC_PATH / config['data']['examples']
EVAL_CSV = RNC_PATH / config['data']['eval']


def delete_nonexistent(dataframe):
    df_len = len(dataframe.index)
    print(f'The file contains {df_len} examples.')
    new_dataframe = dataframe[dataframe.apply(lambda x: Path(x['filename']).is_file(), axis=1)]
    new_df_len = len(new_dataframe.index)
    diff = df_len - new_df_len
    print(f'{diff} of the media files seem to be non-existent. If you proceed, these examples will be deleted. {new_df_len} examples will be left. Proceed? [y/n]')
    decision = input()
    if decision == 'y':
        return new_dataframe
    elif decision == 'n':
        return dataframe
    print(f'Input {decision} not recognised. Type y or n. If y, the examples will be removed. If n, they will be kept.')
    return delete_nonexistent(dataframe)


def drop_duplicates_and_overwrite(dataframe, file, change_to_mp3=False):
    df_len = len(dataframe.index)
    dataframe.drop_duplicates(subset='filename', inplace=True)
    if change_to_mp3:
        dataframe['filename'] = dataframe.filename.apply(lambda x: x.replace('.mp3', '.mp4'))
    nondup_len = len(dataframe.index)
    duplicates_count = df_len - nondup_len
    print(f'Dropped {duplicates_count} duplicated examples. Left {nondup_len} examples. Proceed to overwrite the csv file? [y/n]')
    decision = input()
    if decision == 'y':
        dataframe.to_csv(file, sep='\t', index=False)
        return
    elif decision == 'n':
        return
    print(f'Input {decision} not recognised. Type y or n. If y, the csv file will be overwritten. If n, nothing will happen.')
    return drop_duplicates_and_overwrite(dataframe)


for file in [EVAL_CSV, CSV_FILE]:
    df = pd.read_csv(file, delimiter='\t')
    df = delete_nonexistent(df)
    drop_duplicates_and_overwrite(df, file, change_to_mp3=config['data']['use_mp3'])

