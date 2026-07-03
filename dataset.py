"""
Shared data for the Mood Machine lab.

This file defines:
  - POSITIVE_WORDS: starter list of positive words
  - NEGATIVE_WORDS: starter list of negative words
  - SAMPLE_POSTS: short example posts for evaluation and training
  - TRUE_LABELS: human labels for each post in SAMPLE_POSTS
"""

# ---------------------------------------------------------------------
# Starter word lists
# ---------------------------------------------------------------------

POSITIVE_WORDS = [
    "happy",
    "great",
    "good",
    "love",
    "excited",
    "awesome",
    "fun",
    "chill",
    "relaxed",
    "amazing",
]

NEGATIVE_WORDS = [
    "sad",
    "bad",
    "terrible",
    "awful",
    "angry",
    "upset",
    "tired",
    "stressed",
    "hate",
    "boring",
]

# ---------------------------------------------------------------------
# Starter labeled dataset
# ---------------------------------------------------------------------

# Short example posts written as if they were social media updates or messages.
SAMPLE_POSTS = [
    "I love this class so much",
    "Today was a terrible day",
    "Feeling tired but kind of hopeful",
    "This is fine",
    "So excited for the weekend",
    "I am not happy about this",
    # --- Added: slang, emojis, sarcasm, and mixed/ambiguous tone ---
    "lowkey stressed but kinda proud of myself ngl",
    "this movie was mid, wouldn't watch again",
    "just got home from the gym, feeling amazing :)",
    "oh great, another Monday 🙄",
    "I absolutely love getting stuck in traffic for two hours",
    "no cap this is the best day ever 🔥",
    "meh, it was okay I guess",
    "so tired of this but also kinda excited for tomorrow",
    "3am and can't sleep, brain won't stop 💀",
    "highkey obsessed with this new song 😭",
]

# Human labels for each post above.
# Allowed labels in the starter:
#   - "positive"
#   - "negative"
#   - "neutral"
#   - "mixed"
TRUE_LABELS = [
    "positive",  # "I love this class so much"
    "negative",  # "Today was a terrible day"
    "mixed",     # "Feeling tired but kind of hopeful"
    "neutral",   # "This is fine"
    "positive",  # "So excited for the weekend"
    "negative",  # "I am not happy about this"
    # --- Added labels (must stay aligned with SAMPLE_POSTS above) ---
    "mixed",     # "lowkey stressed but kinda proud of myself ngl"
    "negative",  # "this movie was mid, wouldn't watch again" (slang: "mid" = mediocre/bad)
    "positive",  # "just got home from the gym, feeling amazing"
    "negative",  # "oh great, another Monday" (sarcasm: "great" is not meant literally)
    "negative",  # "I absolutely love getting stuck in traffic for two hours" (sarcasm)
    "positive",  # "no cap this is the best day ever" (slang: "no cap" = "no lie")
    "neutral",   # "meh, it was okay I guess" (lukewarm, non-committal)
    "mixed",     # "so tired of this but also kinda excited for tomorrow"
    "negative",  # "3am and can't sleep, brain won't stop" (distress, not literally negative words)
    "positive",  # "highkey obsessed with this new song" (slang: "highkey" = openly/very)
]

# Notes on edge cases (things a friend might label differently):
#   - "oh great, another Monday" and "I absolutely love getting stuck in
#     traffic for two hours" are sarcastic. The literal words are positive
#     ("great", "love") but the intended meaning is negative. A keyword
#     based system has no way to detect sarcasm, so these are good stress
#     tests for the rule based model.
#   - "meh, it was okay I guess" vs. "so tired of this but also kinda
#     excited for tomorrow" both sit near the boundary between "neutral"
#     and "mixed" -- reasonable people could disagree on which is which.
#   - "3am and can't sleep, brain won't stop" contains no obvious
#     positive/negative keywords at all, yet most people would read it as
#     a negative/distressed post.
#
# Remember to keep them aligned:
#   len(SAMPLE_POSTS) == len(TRUE_LABELS)
