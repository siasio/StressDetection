import rnc
from huggingsound import SpeechRecognitionModel
from huggingsound.normalizer import DefaultTextNormalizer
from pathlib import Path
import os
import random
import argparse
import nest_asyncio
import json
from transcription_utils import remove_braces_content, get_vowel, get_latin, extract_stressed_syllables,\
    get_phrase_no_stress, get_phrase_with_stress, get_phrase_with_stress_soft, soft_to_original, back_to_cyrillic

from utils import read_config, CONFIG_DIR, get_basename

nest_asyncio.apply()

parser = argparse.ArgumentParser()

parser.add_argument('--config', default='default.yaml')
args = parser.parse_args()

config = read_config(CONFIG_DIR / args.config)


transcribe = 32000
evaluate = 32000

RNC_PATH = Path(config['data']['dir'])
MEDIA_PATH = RNC_PATH / config['data']['media']
model_path = Path(config['training']['output_model_folder'])
if config['training'].get('subdir', False):
    model_path = model_path / config['training']['subdir']
model = SpeechRecognitionModel(model_path)

examples_file = RNC_PATH / config['data']['eval']  # Slash is a syntax of the pathlib library
mult = rnc.MultimodalCorpus(file=examples_file)
examples = mult.data
if transcribe >= 0 and evaluate >= 0:
    examples = examples[:max(transcribe,evaluate)]
audio_paths = [str(MEDIA_PATH / get_basename(example.filepath)) for example in examples]
phrases = [get_phrase_no_stress(example.txt) for example in examples]
train_data = [{"path": str(audio_path), "transcription": gt} for audio_path, gt in zip(audio_paths, phrases)]


preds = Path(config['results']['dir']) / 'transcriptions_real_not_stressed.json'
gt = Path(config['results']['dir']) / 'data_real_not_stressed.json'

if not preds.is_file():
    transcriptions = model.transcribe(audio_paths, batch_size=8)
    transcriptions = [{'transcription': t['transcription']} for t in transcriptions]

    with open(preds, 'w') as f:
        json.dump(transcriptions, f)
    with open(gt, 'w') as f:
        json.dump(train_data, f)

with open(preds, 'r') as f:
    transcriptions = json.load(f)

with open(gt, 'r') as f:
    train_data = json.load(f)

# transcriptions = [{'transcription': get_phrase_no_stress(t['transcription'])} for t in transcriptions]

print(model.token_set)
text_normalizer = DefaultTextNormalizer(model.token_set)
evaluation = model.evaluate(references=train_data, predictions=transcriptions, text_normalizer=DefaultTextNormalizer(model.token_set)) #, inference_batch_size=8, metrics_batch_size=8)
print(evaluation)

transcriptions = [back_to_cyrillic(t['transcription']) for t in transcriptions]
phrases = [back_to_cyrillic(ph) for ph in phrases]

ph_tr = list(zip(phrases, transcriptions))
random.shuffle(ph_tr)
# cyrillic_transcriptions = [''.join([get_vowel(vowel) for vowel in tr['transcription']]) for tr in transcriptions]
print('\n'.join(['\n'.join([phr, f'Transcribed: {ct}'])
    for phr, ct in ph_tr[:32]]) )
