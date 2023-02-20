import rnc
from huggingsound import SpeechRecognitionModel
from pathlib import Path
import os
import argparse
import nest_asyncio
from transcription_utils import remove_braces_content, get_vowel, get_latin, extract_stressed_syllables, get_phrase_no_stress

from utils import read_config, CONFIG_DIR

nest_asyncio.apply()

parser = argparse.ArgumentParser()

parser.add_argument('--config', default='default.yaml')
args = parser.parse_args()

config = read_config(CONFIG_DIR / args.config)

# parser = argparse.ArgumentParser()
#
# parser.add_argument('--transcribe_sents', type=int, dest='transcribe', default=1,
#         help='How many sentences to transcribe. 0 means: don\'t produce transcrtiptions. -1 means: run on all examples from the csv file.')
# parser.add_argument('--evaluate_sents', type=int, dest='evaluate', default=10,
#         help='On how many sentences to run the evaluation. 0 means: don\'t run the evaluation. -1 means: run on all examples from the csv file.')
# parser.add_argument('--data_path', default='',
#         help='''Path to the folder containing the csv file and the model folder.
#         Defaults to empty string '' which might work if data sits in the current working directory.
#         If it doesn't work, then you need to specify the path.''')
# parser.add_argument('--no_csv', action='store_true',
#         help='With this flag, --examples_folder should be used instead of --examples_basename')
# parser.add_argument('--examples_basename', default='all_data20.csv',
#         help='Name of the csv file, needs to be located in the data path.')
# parser.add_argument('--examples_folder', default='other_media',
#         help='Name of the csv file, needs to be located in the data path.')
# parser.add_argument('--model_folder', default='best_model',
#         help='Name of the folder containing the model, needs to be located inside the data path folder.')
# args = parser.parse_args()

transcribe = 10
evaluate = 10

RNC_PATH = Path(config['data']['dir'])
model = SpeechRecognitionModel(Path(config['training']['output_model_folder']))

audio_paths = []
phrases = []
gt_transcriptions = []
# phrases_vowels = []

# if args.no_csv:
#     examples_directory = RNC_PATH / args.examples_folder
#     all_files = os.listdir(str(examples_directory))
#     txt_files = [af for af in all_files if af.endswith('.txt')]
#     if transcribe >= 0 and evaluate >= 0:
#         txt_files = txt_files[:max(transcribe,evaluate)]
#     for tf in txt_files:
#         audio_paths.append(examples_directory / f'{tf[:-4]}.mp3')
#         with open(str(examples_directory / tf), 'r') as tf_file:
#             tf_text = tf_file.read()
#         phrases.append(remove_braces_content(tf_text))
#         gt = extract_stressed_syllables(tf_text)
#         gt_transcriptions.append(gt)
#         phrases_vowels.append(''.join([get_vowel(vowel) for vowel in gt]))
# else:
examples_file = RNC_PATH / config['data']['eval']  # Slash is a syntax of the pathlib library
mult = rnc.MultimodalCorpus(file=examples_file)
examples = mult.data
if transcribe >= 0 and evaluate >= 0:
    examples = examples[:max(transcribe,evaluate)]
for example in examples:
    audio_paths.append(Path(example.filepath))
    phrases.append(get_phrase_no_stress(example.txt))
        # gt = extract_stressed_syllables(example.txt)f
        # gt_transcriptions.append(gt)
        # phrases_vowels.append(''.join([get_vowel(vowel) for vowel in gt]))

if transcribe:
    transcriptions = model.transcribe(audio_paths)
    # cyrillic_transcriptions = [''.join([get_vowel(vowel) for vowel in tr['transcription']]) for tr in transcriptions]
    print('\n'.join(['\n'.join([phr, f'Transcribed: {ct}'])
        for phr, ct in zip(phrases, transcriptions)]) )

if evaluate:
    train_data = [ {"path": str(audio_path), "transcription": gt} for audio_path, gt in zip(audio_paths, gt_transcriptions) ]
    evaluation = model.evaluate(train_data)
    print(evaluation)
