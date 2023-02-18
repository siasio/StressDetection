import json
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

from utils import read_config, CONFIG_DIR

parser = argparse.ArgumentParser()

parser.add_argument('--config', default='default.yaml')
args = parser.parse_args()

config = read_config(CONFIG_DIR / args.config)
RESULTS_PATH = Path(config['results']['dir']) / 'trainer_state.json'


with open(RESULTS_PATH, 'r') as r:
    results = json.load(r)

log_history = results['log_history']

train_loss = []
train_steps = []

eval_loss = []
eval_wer = []
eval_cer = []
eval_steps = []

for l in log_history:
    if 'loss' in l.keys():
        train_loss.append(l['loss'] / 6168)
        train_steps.append(l['step'])
    elif 'eval_loss' in l.keys():
        eval_loss.append(l['eval_loss'] / 500)
        eval_wer.append(l['eval_wer'])
        eval_cer.append(l['eval_cer'])
        eval_steps.append(l['step'])

fig, ax = plt.subplots()
ax.plot(train_steps, train_loss, label='Train loss')
ax.plot(eval_steps, eval_loss, label='Eval loss')

ax.set(xlabel='Training step', ylabel='Loss',
       title='Loss for training and evaluation data')

ax.legend()

# fig.savefig("test.png")
plt.show()

fig, ax = plt.subplots()
ax.plot(eval_steps, eval_wer, label='WER')
ax.plot(eval_steps, eval_cer, label='CER')

ax.set(xlabel='Training step', ylabel='Error Rate',
       title='WER/CER metrics for evaluation data')

ax.legend()

# fig.savefig("test.png")
plt.show()
