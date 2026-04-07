"""
Shared preprocessing utilities for both datasets.
"""

import re
import unicodedata


ARABIZI_NUMBER_LETTERS = {
    "2": "ء", "3": "ع", "5": "خ",
    "6": "ط", "7": "ح", "8": "غ", "9": "ق"
}

ARABIZI_PATTERN = re.compile(
    r"\b[a-zA-Z]*[23567893][a-zA-Z0-9]*\b|"
    r"\b(?:ana|inta|msh|mesh|bas|yalla|habibi|habibti|inshallah|wallah|"
    r"tayeb|kwayes|mabsoot|ahlan|marhaba|sho|kif|leish|wein)\b",
    re.IGNORECASE
)


def is_arabic_script(token):
    """Return True if token contains Arabic Unicode characters."""
    return any(
        "\u0600" <= ch <= "\u06FF" or "\u0750" <= ch <= "\u077F"
        for ch in token
    )


def is_arabizi(token):
    """Heuristic: return True if token looks like Arabizi (Latin-script Arabic)."""
    if is_arabic_script(token):
        return False
    return bool(ARABIZI_PATTERN.match(token))


def normalize_arabic(text):
    """Normalize Arabic text: remove diacritics, normalize alef variants."""
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)  # remove diacritics
    text = re.sub(r"[أإآ]", "ا", text)                 # normalize alef
    text = re.sub(r"ة", "ه", text)                     # normalize ta marbuta
    text = re.sub(r"ى", "ي", text)                     # normalize alef maqsura
    return text


def tokenize(text):
    """Simple whitespace tokenizer that preserves Arabic and Latin tokens."""
    return text.strip().split()


def remove_pii(text):
    """
    Remove obvious PII: @mentions, URLs.
    Note: does not guarantee complete PII removal.
    """
    text = re.sub(r"@\w+", "@USER", text)
    text = re.sub(r"http\S+|www\.\S+", "URL", text)
    return text


def load_conll(filepath, encoding="utf-8"):
    """
    Load a CoNLL-format file (one token per line, blank lines = sentence boundary).
    Returns list of sentences, each a list of (token, label) tuples.
    """
    sentences = []
    current = []
    with open(filepath, encoding=encoding) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.strip() == "":
                if current:
                    sentences.append(current)
                    current = []
            else:
                parts = line.split()
                if len(parts) >= 2:
                    current.append((parts[0], parts[-1]))
                elif len(parts) == 1:
                    current.append((parts[0], "O"))
    if current:
        sentences.append(current)
    return sentences
