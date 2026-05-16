from django.utils import translation


def current_language():
    return (translation.get_language() or "fr")[:2]


def is_english():
    return current_language() == "en"


def tr_text(fr_text, en_text):
    return en_text if is_english() else fr_text
