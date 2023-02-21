import rnc
from huggingsound import SpeechRecognitionModel
from pathlib import Path
import os
import random
import argparse
import nest_asyncio
from transcription_utils import remove_braces_content, get_vowel, get_latin, extract_stressed_syllables, get_phrase_no_stress, get_phrase_with_stress

from utils import read_config, CONFIG_DIR, get_basename

nest_asyncio.apply()

parser = argparse.ArgumentParser()

parser.add_argument('--config', default='default.yaml')
args = parser.parse_args()

config = read_config(CONFIG_DIR / args.config)


transcribe = 10000
evaluate = 10000

RNC_PATH = Path(config['data']['dir'])
MEDIA_PATH = RNC_PATH / config['data']['media']
model_path = Path(config['training']['output_model_folder'])
if config['training'].get('subdir', False):
    model_path = model_path / config['training']['subdir']
model = SpeechRecognitionModel(model_path)

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
audio_paths = [str(MEDIA_PATH / get_basename(example.filepath)) for example in examples]
phrases = [get_phrase_with_stress(example.txt) for example in examples]
        # gt = extract_stressed_syllables(example.txt)f
        # gt_transcriptions.append(gt)
        # phrases_vowels.append(''.join([get_vowel(vowel) for vowel in gt]))

if transcribe:
    transcriptions = model.transcribe(audio_paths, batch_size=12)
    ph_tr = list(zip(phrases, transcriptions))
    random.shuffle(ph_tr)
    # cyrillic_transcriptions = [''.join([get_vowel(vowel) for vowel in tr['transcription']]) for tr in transcriptions]
    print('\n'.join(['\n'.join([phr, f'Transcribed: {ct}'])
        for phr, ct in ph_tr[:32]]) )

if evaluate:
    transcriptions = [t.replace('\u0301', '') for t in transcriptions]
    phrases = [p.replace('\u0301', '') for p in phrases]
    train_data = [ {"path": str(audio_path), "transcription": gt} for audio_path, gt in zip(audio_paths, phrases) ]
    evaluation = model.evaluate(references=train_data, predictions=transcriptions) #, inference_batch_size=8, metrics_batch_size=8)
    print(evaluation)
