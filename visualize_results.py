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
RESULTS_FIRST_PATH = Path(config['results']['dir']) / 'trainer_state_first.json'

def get_stats(path, mult=False):
    with open(path, 'r') as r:
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
            step = l['step']
            if mult:
                step *= 2
            train_steps.append(step)
        elif 'eval_loss' in l.keys():
            eval_loss.append(l['eval_loss'] / 500)
            eval_wer.append(l['eval_wer'])
            eval_cer.append(l['eval_cer'])
            step = l['step']
            if mult:
                step *= 2
            eval_steps.append(step)
    return train_loss, train_steps, eval_loss, eval_wer, eval_cer, eval_steps

train_loss1, train_steps1, eval_loss1, eval_wer1, eval_cer1, eval_steps1 = get_stats(RESULTS_FIRST_PATH, mult=True)
train_loss2, train_steps2, eval_loss2, eval_wer2, eval_cer2, eval_steps2 = get_stats(RESULTS_PATH)

fig, ax = plt.subplots()
ax.plot(train_steps1, train_loss1, label='Train loss 1')
ax.plot(eval_steps1, eval_loss1, label='Eval loss 1')
ax.plot(train_steps2, train_loss2, label='Train loss 2')
ax.plot(eval_steps2, eval_loss2, label='Eval loss 2')

ax.set(xlabel='Training step', ylabel='Loss',
       title='Loss for training and evaluation data')

ax.legend()

# fig.savefig("test.png")
plt.show()

fig, ax = plt.subplots()
ax.plot(eval_steps1, eval_wer1, label='WER 1')
ax.plot(eval_steps1, eval_cer1, label='CER 1')
ax.plot(eval_steps2, eval_wer2, label='WER 2')
ax.plot(eval_steps2, eval_cer2, label='CER 2')

ax.set(xlabel='Training step', ylabel='Error Rate',
       title='WER/CER metrics for evaluation data')

ax.legend()

# fig.savefig("test.png")
plt.show()
