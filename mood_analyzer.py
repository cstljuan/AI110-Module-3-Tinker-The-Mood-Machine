# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class starts with very simple logic:
  - Preprocess the text
  - Look for positive and negative words
  - Compute a numeric score
  - Convert that score into a mood label
"""

import re
from typing import List, Dict, Tuple, Optional

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS


class MoodAnalyzer:
    """
    A very simple, rule based mood classifier.
    """

    # Words that flip the polarity of the sentiment word right after them
    # (e.g. "not happy" should count as negative, not positive).
    # Contractions like "wouldn't" / "can't" are also treated as negators
    # because preprocess() keeps apostrophes, so they survive as one token.
    NEGATION_WORDS = {"not", "no", "never", "cannot"}

    # Simple emoji/emoticon signals, treated as strong standalone sentiment
    # words. Ambiguous emoji (like the "crying" face, which can mean
    # heartbroken OR touched/laughing depending on context) are deliberately
    # left out rather than guessed at.
    POSITIVE_EMOJI = {":)", ":-)", ":d", "🔥", "😍", "🎉"}
    NEGATIVE_EMOJI = {":(", ":-(", "💀", "🙄", "😡"}

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        # Use the default lists from dataset.py if none are provided.
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        # Store as sets for faster lookup.
        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens the model can work with.

        Steps:
          - Strip leading/trailing whitespace and lowercase everything,
            so "Great" and "great" are treated the same word.
          - Strip sentence punctuation (periods, commas, "!", "?", quotes)
            so "great," and "great" match the same keyword.
          - Keep apostrophes, so contractions like "wouldn't" / "can't"
            survive as a single token (useful for negation handling).
          - Keep colons/parentheses and non-ASCII characters untouched,
            so text emoticons (":)") and emoji ("🔥") survive as their own
            tokens instead of being stripped away.
          - Split on whitespace.
        """
        cleaned = text.strip().lower()
        cleaned = re.sub(r"[.,!?;\"]+", " ", cleaned)
        tokens = cleaned.split()

        return tokens

    # ---------------------------------------------------------------------
    # Scoring logic
    # ---------------------------------------------------------------------

    def _is_negation(self, token: str) -> bool:
        """True for words that flip the meaning of the next sentiment word."""
        return token in self.NEGATION_WORDS or token.endswith("n't")

    def _analyze(self, text: str) -> Tuple[int, List[str], List[str]]:
        """
        Shared scoring logic used by score_text(), predict_label(), and
        explain(), so all three always agree on what the model "saw".

        Returns (score, positive_hits, negative_hits).
        """
        tokens = self.preprocess(text)

        score = 0
        positive_hits: List[str] = []
        negative_hits: List[str] = []

        for i, token in enumerate(tokens):
            if token in self.positive_words or token in self.POSITIVE_EMOJI:
                polarity = 1
            elif token in self.negative_words or token in self.NEGATIVE_EMOJI:
                polarity = -1
            else:
                continue

            # Only the immediately preceding token counts as a negator.
            # (A wider lookback window sounds better in theory, but testing
            # against SAMPLE_POSTS showed it misfires on sentences like
            # "brain won't stop 💀", where "won't" ends up negating the
            # unrelated emoji two tokens later instead of "stop".)
            if i > 0 and self._is_negation(tokens[i - 1]):
                polarity *= -1

            score += polarity
            if polarity > 0:
                positive_hits.append(token)
            else:
                negative_hits.append(token)

        return score, positive_hits, negative_hits

    def score_text(self, text: str) -> int:
        """
        Compute a numeric "mood score" for the given text.

        Positive words/emoji increase the score, negative words/emoji
        decrease it, and a negator immediately before a sentiment word
        (e.g. "not happy") flips its polarity.
        """
        score, _positive_hits, _negative_hits = self._analyze(text)
        return score

    # ---------------------------------------------------------------------
    # Label prediction
    # ---------------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        """
        Turn the numeric score for a piece of text into a mood label.

        Mapping:
          - Both positive AND negative hits present -> "mixed"
            (the text contains conflicting signals, regardless of which
            side "wins" on raw score, e.g. "tired but excited")
          - score > 0  -> "positive"
          - score < 0  -> "negative"
          - score == 0 -> "neutral"
        """
        score, positive_hits, negative_hits = self._analyze(text)

        if positive_hits and negative_hits:
            return "mixed"
        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        return "neutral"

    # ---------------------------------------------------------------------
    # Explanations (optional but recommended)
    # ---------------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining WHY the model chose its label.

        Reuses the same _analyze() logic as score_text() and predict_label(),
        so the explanation always matches the actual prediction (including
        negation flips and emoji hits).
        """
        score, positive_hits, negative_hits = self._analyze(text)

        return (
            f"Score = {score} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'})"
        )
