import rnc
from huggingsound import SpeechRecognitionModel, TrainingArguments, ModelArguments, TokenSet
from pathlib import Path
import os
import argparse
from transcription_utils import remove_braces_content, get_vowel, get_latin, \
    extract_stressed_syllables, syllable_tokens, \
    latin_tokens, latin_tokens_stress, latin_tokens_stress_soft, \
    cyrillic_tokens, cyrillic_tokens_stress, cyrillic_tokens_stress_soft, \
    get_phrase_with_stress, get_phrase_with_stress_soft, get_phrase_no_stress
import nest_asyncio
from tqdm import tqdm

# os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

from utils import read_config, CONFIG_DIR, get_basename

nest_asyncio.apply()

parser = argparse.ArgumentParser()

parser.add_argument('--config', default='default.yaml')
parser.add_argument('--num_train_epochs', type=int, default=1,
        help='Training will start from the next epoch compared to the one on which it finished previously. Therefore, we need to increase this number each time.')
args = parser.parse_args()

config = read_config(CONFIG_DIR / args.config)

RNC_PATH = Path(config['data']['dir'])
MEDIA_PATH = RNC_PATH / Path(config['data']['media'])
train_path = RNC_PATH / config['data']['examples']  # Slash is a syntax of the pathlib library
eval_path = RNC_PATH / config['data']['eval']
model_folder = Path(config['training']['pretrained_model_folder'])
model_name = config['training']['web_model'] if config['training']['use_model_from_web'] or not model_folder.is_dir()\
    else model_folder
model = SpeechRecognitionModel(model_name, device='cuda')
output_dir = Path(config['training']['output_model_folder'])
overwrite_output_dir = True  # not args.not_overwrite_output_dir
num_train_epochs = args.num_train_epochs



train_corpus = rnc.MultimodalCorpus(file=train_path)
eval_corpus = rnc.MultimodalCorpus(file=eval_path) if eval_path else None
train_data = [
    {"path": str(MEDIA_PATH / get_basename(example.filepath)),
     "transcription": get_phrase_with_stress_soft(example.txt)} for example in train_corpus.data
]
eval_data = [
    {"path": str(MEDIA_PATH / get_basename(example.filepath)),
     "transcription": get_phrase_with_stress_soft(example.txt)} for example in eval_corpus.data
] if eval_corpus else None

accum_steps = config['training']['accumulation_steps']
batch_size = config['training']['batch_size']
steps_per_epoch = len(train_data) // (accum_steps * batch_size)

training_args = TrainingArguments(fp16=config['training']['fp16'],
                                  gradient_accumulation_steps=accum_steps,
                                  per_device_train_batch_size=batch_size,
                                  use_8bit_optimizer=config['training']['adam_8bit'],
                                  eval_steps=config['training']['eval_steps'],
                                  logging_steps=config['training']['logging_steps'],
                                  lr_warmup_steps=steps_per_epoch,
                                  lr_decay_steps=steps_per_epoch,
                                  learning_rate=1e-4,
                                  gradient_checkpointing=True)
training_args.num_train_epochs = args.num_train_epochs
training_args.overwrite_output_dir = overwrite_output_dir  # If we don't want to keep the less trained model, it's good to just overwrite the current model directory
#training_args.save_strategy = 'epoch'  # Default save strategy is 'steps'. If we use 'epoch' instead, a model checkpoint will be saved in the end of every epoch.
#training_args.save_steps = 100  # Works only if save strategy is 'steps'. Default value is 500.
#training_args.ignore_skip_dat = True

token_set = TokenSet(latin_tokens_stress_soft)

data_cache_dir = config['data']['cache']
data_cache_dir = str(RNC_PATH / data_cache_dir) if data_cache_dir else None

# model_args = ModelArguments(apply_spec_augment=False, mask_time_length=4, mask_feature_length=4)

model.finetune(
    output_dir,
    train_data=train_data,
    eval_data=eval_data, #eval_data, # the eval_data is optional
    token_set=token_set,  # token_set won't be used if the model is already fine-tuned and therefore has the token set already defined
    training_args=training_args,
    # model_args=model_args,
    data_cache_dir=data_cache_dir
)

