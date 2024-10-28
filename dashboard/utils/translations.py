import json
import os

def load_translations(lang):
    try:
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(parent_dir, 'assets', 'locale', f'{lang}.json')
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Translation file for language '{lang}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from translation file for language '{lang}'.")
        return {}

def get_translation(key, lang='fr'):
    try:
        translations = load_translations(lang)
        return translations.get(key, key)
    except Exception as e:
        print(f"Error getting translation for key '{key}' in language '{lang}': {e}")
        return key
