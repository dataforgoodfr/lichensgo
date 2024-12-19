import os
import json

def load_translations(lang):
    with open(os.path.join(os.path.dirname(__file__), f'locale/{lang}.json'), 'r', encoding='utf-8') as file:
        return json.load(file)

translations = {
    'en': load_translations('en'),
    'fr': load_translations('fr'),
    # Add more languages as needed
}

def get_language():
    # Get the language from the user's session
    return 'fr'

def get_lazy_translation(key):
    lang = 'fr'
    key = str(key)
    return translations.get(lang, {}).get(key, key)
