# -*- coding: utf-8 -*-
import re

syllable_tokens = ['q', 'w', 'e', 'r', 't', 'y', 'u']
cyrillic_tokens_stress = ["б", "в", "г", "д", "ж", "з", "й", "к", "л", "м", "н", "п", "p", "c", "т", "ф", "x", "ц", "ч", "ш", "щ",
          "ь", "ъ", "a", "y", "o", "ы", "э", "я", "ю", "ё", "и", "e",
          "а\u0301", "у\u0301", "о\u0301", "ы\u0301", "э\u0301", "я\u0301", "ю\u0301", "и\u0301", "е\u0301"]
cyrillic_tokens_stress_soft = ["б", "в", "г", "д", "ж", "з", "й", "к", "л", "м", "н", "п", "p", "c", "т", "ф", "x", "ц", "ч", "ш", "щ",
          "ь", "a", "y", "o", "ы", "э", "и",
          "a\u0301", "у\u0301", "о\u0301", "ы\u0301", "э\u0301", "и\u0301"]
cyrillic_tokens = ["б", "в", "г", "д", "ж", "з", "й", "к", "л", "м", "н", "п", "p", "c", "т", "ф", "x", "ц", "ч", "ш", "щ",
          "ь", "ъ", "a", "y", "o", "ы", "э", "я", "ю", "ё", "и", "e"]

def remove_braces_content(text):
  return re.sub('\[.*?\]', '', text)

vowels_to_latin = {
        'а': 'q',
        'я': 'q',
        'э': 'w',
        'е': 'w',
        'о': 'e',
        'ё': 'e',
        'у': 'r',
        'ю': 'r',
        'ы': 't',
        'и': 'y',
        '#': 'u'
        }
latin_to_vowels = {
        'q': 'а',
        'w': 'э',
        'e': 'о',
        'r': 'у',
        't': 'ы',
        'y': 'и',
        'u': '#',
        ' ': ' '
        }
fricative_nonpalatalized = {'ш', 'ж', 'ц'}

non_palatalized_vowels = {
    'а': 'а',
    'я': 'а',
    'у': 'у',
    'ю': 'у',
    'э': 'э',
    'е': 'э',
    'о': 'о',
    'ё': 'о\u0301',
    'и': 'и',
    'ы': 'ы',
}

def get_vowel(latin_letter):
  return latin_to_vowels[latin_letter]

def get_latin(cyrillic_vowel):
  return vowels_to_latin[cyrillic_vowel]

def extract_stressed_syllables(phrase, change_to_latin=True):
  bare_phrase = remove_braces_content(phrase)
  bare_phrase += ' '  # To handle correctly the last vowel in case it's the last character
  clean_phrase = ''
  last_vowel = None
  last_fricative_nonpalatalized = False
  for a in bare_phrase:
      a = a.lower()
      if last_vowel:
          if a.encode("unicode_escape") != b'\\u0301' and last_vowel != 'ё':
              last_vowel = '#'
          if last_fricative_nonpalatalized and last_vowel == "и":
              last_vowel = 'ы'
          clean_phrase += get_latin(last_vowel) if change_to_latin else get_vowel(get_latin(last_vowel))
          last_vowel = None
      last_fricative_nonpalatalized = a in fricative_nonpalatalized  # TODO: Check if this variable really has effect. It seems that it doesn't work.
      if a in vowels_to_latin.keys():
          last_vowel = a
  return clean_phrase

def get_phrase_with_stress(phrase):
    phrase = re.sub(r'\[.*?\]', '', phrase).lower()  # Remove braces content (it indicates a speaker)
    phrase = re.sub('[^\u0300\u0301\u0401\u0410-\u044f\u0451]', ' ', phrase)  # Change non-cyrillic characters into spaces
    phrase = phrase.replace('\u0300', '\u0301')
    return re.sub(r'\s+', ' ', phrase)  # Change multiple spaces into single spaces

def get_phrase_with_stress_soft(phrase):
    def replace_signs(text):
        for key in ['а', 'э', 'у', 'о', 'ы', 'я', 'е', 'ю', 'ё', 'и']:
            text = text.replace(rf'ь{key}', rf'ьй{non_palatalized_vowels[key]}')
            text = text.replace(rf'ъ{key}', rf'й{non_palatalized_vowels[key]}')
        return text

    def replace_palatalized(text):
        for key in ['я', 'е', 'ю', 'ё']:
            text = text.replace(f' {key}', f' й{non_palatalized_vowels[key]}')
            text = text.replace(key, f'ь{non_palatalized_vowels[key]}')

        return text.replace('йь', 'й')

    def clean_i(text):
        return re.sub(r'([жш])и', r'\1ы', text)

    phrase = re.sub(r'\[.*?\]', '', phrase).lower()  # Remove braces content (it indicates a speaker)
    phrase = re.sub('[^\u0300\u0301\u0401\u0410-\u044f\u0451]', ' ', phrase)  # Change non-cyrillic characters into spaces
    phrase = phrase.replace('\u0300', '\u0301')  # Should be '' or \u0301 but I realized it too late
    phrase = clean_i(phrase)
    phrase = replace_signs(phrase)
    phrase = replace_palatalized(phrase)

    return re.sub(r'\s+', ' ', phrase)  # Change multiple spaces into single spaces

def soft_to_original(phrase):
    def recreate_i(text):
        return re.sub(r'([жш])ы', r'\1и', text)

    phrase = recreate_i(phrase)

def get_phrase_no_stress(phrase):
    phrase = re.sub(r'\[.*?\]', '', phrase).lower()  # Remove braces content (it indicates a speaker)
    phrase = re.sub('[\u0300\u0301]', '', phrase)  # Remove stress marks
    phrase = re.sub('[^\u0401\u0410-\u044f\u0451]', ' ', phrase)  # Change non-cyrillic characters into spaces
    return re.sub(r'\s+', ' ', phrase)  # Change multiple spaces into single spaces


def add_stresses(phrase, pred):
  return
  # TODO: write a function which will add stresses to a phrase based on the model output
