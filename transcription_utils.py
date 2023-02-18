# -*- coding: utf-8 -*-
import re

syllable_tokens = ['q', 'w', 'e', 'r', 't', 'y', 'u']
cyrillic_tokens = ["б", "в", "г", "д", "ж", "з", "й", "к", "л", "м", "н", "п", "p", "c", "т", "ф", "x", "ц", "ч", "ш", "щ",
          "ь", "ъ", "a", "y", "o", "ы", "э", "я", "ю", "ё", "и", "e",
          "\u0301a", "\u0301y", "\u0301o", "\u0301ы", "\u0301э", "\u0301я", "\u0301ю", "\u0301и", "\u0301e"]

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
    phrase = re.sub('[^\u0301\u0410-\u044f]', ' ', phrase)  # Change non-cyrillic characters into spaces
    return re.sub(r'\s+', ' ', phrase)  # Change multiple spaces into single spaces


def add_stresses(phrase, pred):
  return
  # TODO: write a function which will add stresses to a phrase based on the model output
