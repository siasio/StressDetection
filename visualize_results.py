import json
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

from utils import read_config, CONFIG_DIR

parser = argparse.ArgumentParser()

parser.add_argument('--config', default='default.yaml')
args = parser.parse_args()

config = read_config(CONFIG_DIR / args.config)
RESULTS_PATH_N1 = Path('model') / 'real_no_stress' / 'trainer_state.json'
RESULTS_PATH_N2 = Path('model') / 'real_no_stress_lr' / 'trainer_state.json'
RESULTS_PATH_A1 = Path('model') / 'real_soft' / 'trainer_state.json'
RESULTS_PATH_A2 = Path('model') / 'real_soft_lr' / 'trainer_state.json'

def get_stats(path, offset=0):
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
            train_loss.append(l['loss'] / 24) # / 6168)
            step = l['step'] + offset
            train_steps.append(step)
        elif 'eval_loss' in l.keys():
            eval_loss.append(l['eval_loss'] / 8) # / 500)
            eval_wer.append(l['eval_wer'])
            eval_cer.append(l['eval_cer'])
            step = l['step'] + offset
            eval_steps.append(step)
    return train_loss, train_steps, eval_loss, eval_wer, eval_cer, eval_steps

results_n1 = get_stats(RESULTS_PATH_N1)
results_n2 = get_stats(RESULTS_PATH_N2, offset=1000)
for a, b in zip(results_n1, results_n2):
    a.extend(b)
train_loss_n, train_steps_n, eval_loss_n, eval_wer_n, eval_cer_n, eval_steps_n = results_n1

results_a1 = get_stats(RESULTS_PATH_A1)
results_a2 = get_stats(RESULTS_PATH_A2, offset=1000)
for a, b in zip(results_a1, results_a2):
    a.extend(b)
train_loss_a, train_steps_a, eval_loss_a, eval_wer_a, eval_cer_a, eval_steps_a = results_a1

fig, ax = plt.subplots()
ax.plot(train_steps_n, train_loss_n, label='Train loss (Raw text model)')
ax.plot(eval_steps_n, eval_loss_n, label='Eval loss (Raw text model)')
ax.plot(train_steps_a, train_loss_a, label='Train loss (Enriched text model)')
ax.plot(eval_steps_a, eval_loss_a, label='Eval loss (Enriched text model)')

ax.set(xlabel='Training step', ylabel='Loss',
       title='Loss for training and evaluation data')

ax.legend()

# fig.savefig("test.png")
plt.show()

fig, ax = plt.subplots()
ax.plot(eval_steps_n, eval_wer_n, label='WER (Raw text model)')
ax.plot(eval_steps_n, eval_cer_n, label='CER (Raw text model)')
ax.plot(eval_steps_a, eval_wer_a, label='WER (Enriched text model)')
ax.plot(eval_steps_a, eval_cer_a, label='CER (Enriched text model)')

ax.set(xlabel='Training step', ylabel='Error Rate',
       title='WER/CER metrics for evaluation data')

ax.legend()

# fig.savefig("test.png")
plt.show()
