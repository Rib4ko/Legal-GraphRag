"""
RTL utilities for Arabic text post-processing.

PaddleOCR returns Arabic characters in *visual* (LTR) order—i.e. each
word's characters are reversed compared to the standard *logical* (RTL)
Unicode order.  The functions here fix that so the resulting Markdown is
correct when opened in any modern editor.
"""
import re

_ARABIC_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF"
    r"\uFB50-\uFDFF\uFE70-\uFEFF]"
)


def is_arabic(text: str) -> bool:
    """Return True if *text* contains at least one Arabic character."""
    return bool(_ARABIC_RE.search(text))


def _reverse_word(word: str) -> str:
    """
    Reverse a single token.  If the token is purely numeric /
    punctuation it is returned as-is (e.g. "%5", ".3").
    """
    if not is_arabic(word):
        return word
    return word[::-1]


def fix_arabic_line(line: str) -> str:
    """
    Fix a single OCR line that is in visual (LTR) order.

    Strategy:
    1. Split the line into whitespace-delimited tokens.
    2. Reverse each Arabic token individually (character order fix).
    3. Reverse the overall token list (word order fix).
    4. Re-join.

    This converts PaddleOCR's visual output back to logical RTL order.
    """
    if not line or not is_arabic(line):
        return line

    tokens = line.split()
    # Step 1: reverse characters inside each Arabic word
    fixed_tokens = [_reverse_word(t) for t in tokens]
    # Step 2: reverse the order of words (RTL reading direction)
    fixed_tokens.reverse()
    return " ".join(fixed_tokens)
