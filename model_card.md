# Model Card: Mood Machine

This model card covers both versions of the classifier built in this project:

1. A **rule based model** implemented in `mood_analyzer.py`
2. A **machine learning model** implemented in `ml_experiments.py` using scikit-learn

Both models were built and evaluated, and this card compares them directly.

## 1. Model Overview

**Model type:**
I built and compared both models: the rule based `MoodAnalyzer` and the machine learning classifier trained with scikit-learn.

**Intended purpose:**
Classify short, casual, social-media-style posts into one of four moods: positive, negative, neutral, or mixed.

**How it works (brief):**

Rule based model: `preprocess()` lowercases the text and strips sentence punctuation (periods, commas, question marks) but keeps apostrophes so contractions like "wouldn't" survive as one token, and keeps emoji and text emoticons intact. `score_text()` walks the tokens and adds 1 point for each match in a positive word or emoji list, and subtracts 1 for each match in a negative word or emoji list. If the token right before a sentiment word is a negation word ("not," "no," "never," "cannot," or anything ending in "n't"), that word's point is flipped. `predict_label()` returns "mixed" if a post has at least one positive hit and one negative hit, and otherwise returns positive, negative, or neutral based on the sign of the total score.

ML model: `CountVectorizer` turns each post into a row of word counts (a "bag of words"). `LogisticRegression` is trained on those word counts and the labels in `TRUE_LABELS`, learning a weight for each word and each label. To predict a new post, the model counts its words and picks the label with the highest combined score.

## 2. Data

**Dataset description:**
The dataset started with 6 example posts. I added 10 more posts covering slang, emojis, sarcasm, and mixed emotions, then added 4 more posts later specifically to test how sensitive each model is to new data. The final dataset has 20 posts and 20 matching labels in `dataset.py`.

**Labeling process:**
I labeled every post myself, based on how I would naturally read it. Straightforward posts with one clear emotion word were easy to label ("Today was a terrible day" is clearly negative). Sarcastic and slang-heavy posts were hard, and several are genuine edge cases a different person might label differently:

- "oh great, another Monday 🙄" reads as negative in tone, even though it literally contains the positive word "great."
- "meh, it was okay I guess" sits right on the line between neutral and mildly negative.
- "3am and can't sleep, brain won't stop 💀" contains no positive or negative keywords at all, yet most people would read it as distress.

**Important characteristics of the dataset:**

- Contains slang: "lowkey," "highkey," "no cap," "mid," "ngl"
- Contains emoji and text emoticons: 🙄, 🔥, 💀, 😭, ":)"
- Contains 2 sarcastic posts
- Contains several posts with genuinely mixed feelings
- Contains short, low-signal posts like "This is fine" and "The bus arrives at 8am every weekday"

**Possible issues with the dataset:**

- It is very small (20 examples) for a 4-way classification task. The neutral and mixed classes only have 3 to 4 examples each, while negative has more examples than any other class.
- I wrote every post and label myself, so the dataset reflects one person's sense of tone and one dialect of English (casual, internet-fluent, US-centric slang). Someone from a different background could reasonably label several of these posts differently.
- Some slang overlaps with words that have unrelated literal meanings (like "sick" or "fire"). I chose not to add these to the word lists after testing showed it creates more problems than it solves (see Section 3), so that gap remains in the dataset.

## 3. How the Rule Based Model Works

**Scoring rules:**

- Positive and negative words each count as plus or minus 1 point. Words come from `POSITIVE_WORDS` and `NEGATIVE_WORDS` in `dataset.py`.
- Negation handling: if the token immediately before a sentiment word is "not," "no," "never," "cannot," or ends in "n't," that word's point is flipped. I tested a wider, 2-token lookback first and rejected it, because it wrongly flipped the meaning of "3am and can't sleep, brain won't stop 💀": the negation word "won't" ended up flipping the negative emoji two tokens later, even though "won't" was really only negating "stop." A 1-token lookback fixed that.
- Emoji handling: I added a small list of unambiguous positive emoji ("🔥," "😍," "🎉," ":)") and negative emoji ("💀," "🙄," "😡," ":(") and scored them exactly like word hits. I deliberately left out 😭 because it is genuinely ambiguous (it can mean sadness or being touched/laughing), and mapping it to either side would just trade one wrong answer for a different one.
- Label thresholds: a post is "mixed" if it has both a positive hit and a negative hit, no matter which one wins on raw score. Otherwise the sign of the score decides positive, negative, or neutral.

**Strengths of this approach:**
It is fully predictable and transparent. Every prediction comes with an `explain()` string that shows exactly which words or emoji were counted and why. It requires no training data and gets simple, direct statements right almost every time, for example "I love this class so much" (positive) and "Today was a terrible day" (negative).

**Weaknesses of this approach:**
It can only recognize words and emoji that are already in its lists, so any slang or emoji outside those lists produces no score and defaults to neutral. It has no concept of tone or context, so sarcasm defeats it completely, since sarcastic posts often contain literally positive words.

## 4. How the ML Model Works

**Features used:**
Bag of words counts, generated by `CountVectorizer`.

**Training data:**
The model is trained and evaluated on the same 20 posts and labels in `dataset.py` (`SAMPLE_POSTS` and `TRUE_LABELS`).

**Training behavior:**
When evaluated on the same data it was trained on, the model scored 100% accuracy, both at 16 posts and again at 20 posts. I do not trust this number, and confirmed it is memorization rather than real understanding:

- `CountVectorizer`'s default tokenizer drops emoji entirely and splits "wouldn't" into "wouldn" plus a discarded "t." This means the ML model cannot see two of the exact signals the rule based model was built to catch.
- At 16 posts, the words "traffic" and "stuck" had identical weights for every label, because they only ever appeared together, in one sarcastic negative post. When I tested the trained model on a brand new sentence, "Traffic was light today, made it home early and relaxed," which is clearly positive, the model called it negative, purely because it contained the word "traffic."
- I then added 2 new posts that used "traffic" and "stuck" in non-negative contexts and retrained. The weights for those words changed and were no longer identical, and the model correctly called the new traffic sentence positive. But when I tested it on yet another new sentence it had never seen, "There is a traffic light on Main Street," a plain, factual, neutral sentence, it predicted positive. It called "Sat in traffic but caught up on my favorite podcast" negative. The underlying problem did not go away. It just moved to different words.

**Strengths and weaknesses:**
The ML model can pick up patterns automatically without anyone hand-writing rules, and it can weigh many words at once instead of matching one keyword at a time. But with only 20 labeled examples, it does not have enough data to learn real meaning. It is overfitting to this specific tiny dataset. Its 100% training accuracy is not a real measure of how well it performs on new text, and it is extremely sensitive to which exact examples happen to be in the dataset, since adding 2 new posts completely rewrote what it had learned about two different words.

## 5. Evaluation

**How the models were evaluated:**
Both models were run on the same 20 labeled posts in `dataset.py`, using the built-in accuracy calculations in `main.py` and `ml_experiments.py`.

- Rule based accuracy: 15 out of 20 correct (75%).
- ML training accuracy: 20 out of 20 (100%), measured on the training set itself. This does not measure how the model performs on new text (see Section 4).

**Examples of correct predictions (rule based):**

- "I love this class so much" to positive, because "love" is a known positive word and nothing negates it.
- "Today was a terrible day" to negative, because "terrible" is a known negative word.
- "so tired of this but also kinda excited for tomorrow" to mixed, because it contains both a known negative word ("tired") and a known positive word ("excited").

**Examples of incorrect predictions (rule based):**

- "I absolutely love getting stuck in traffic for two hours" was predicted positive but is actually negative. The model only sees the word "love" and has no way to detect that the sentence is sarcastic.
- "this movie was mid, wouldn't watch again" was predicted neutral but is actually negative. "Mid" is slang for mediocre or bad, but it is not in the word lists, so it produces no score at all.
- "highkey obsessed with this new song 😭" was predicted neutral but is actually positive. The 😭 emoji is genuinely ambiguous, so it was left unmapped on purpose, which means this sentence produces no score either way.

**How the ML model's failures differed:**
On the same 20 posts, the ML model got all 20 "correct," but only because it had already seen every one of them during training. When tested on sentences that were not in the training set at all, it produced wrong or inconsistent answers, for example calling the plain, factual sentence "There is a traffic light on Main Street" positive. The two models fail in very different ways: the rule based model fails by staying silent (a score of 0, which defaults to neutral) when it does not recognize a word, while the ML model fails by confidently picking a label based on word associations that only happen to hold true in a 20-row dataset.

## 6. Limitations

- The dataset is very small (20 posts) for a 4-way classification task, and the neutral and mixed classes only have 3 to 4 examples each.
- Neither model reliably detects sarcasm. The rule based model has no way to represent tone at all. The ML model appeared to handle one sarcastic example correctly at first, but that turned out to be an accident of a tiny dataset, not real sarcasm detection (see the "Traffic was light today" example in Section 4).
- The rule based model only recognizes words and emoji that were manually added to its lists. Any slang, synonym, or emoji outside those lists is invisible to it and defaults to neutral.
- The rule based model does not attempt to solve polysemy, meaning words with two unrelated meanings, like "sick" (ill) versus "sick" (awesome). Adding "sick" to the word list was tested and rejected, since it would fix one meaning while breaking the other.
- The ML model's 100% training accuracy is not evidence that it generalizes. With such a small dataset, testing a model on the same data it trained on will always look better than the model actually performs on new text.
- The ML model is highly sensitive to small changes in the dataset. Adding just 2 new posts completely changed how it weighed the words "traffic" and "stuck."
- Neither model was tested on longer posts, multiple sentences, or paragraph-length text. All testing here used single, short sentences.

## 7. Ethical Considerations

- Both models risk badly misreading a message from someone expressing real distress if the wording does not match the model's known vocabulary. For example, "3am and can't sleep, brain won't stop" is only flagged as negative here because of one emoji that happened to be mapped. If that emoji were missing, the sentence would be called neutral, even though it describes something closer to distress. In any application involving mental health or wellbeing, treating "no keyword match" as "neutral" could be actively harmful.
- The dataset reflects one person's sense of tone, slang, and labeling choices, all written in casual, internet-fluent, US-centric English. Posts written in a different dialect, a different language, by a non-native English speaker, or using slang from a different community or generation are likely to be misread by both models, since the entire system is built around the words and examples chosen by one person.
- The rule based model's "mixed" rule (a positive hit and a negative hit both present means "mixed") means any post that happens to combine one known positive word and one known negative word gets labeled mixed automatically, whether or not the person's actual feelings are genuinely mixed. This could mislabel someone describing two separate topics as having mixed feelings about a single thing.
- Real deployment of either model on personal messages raises privacy concerns. A mood classifier is, by definition, inferring something private about a person's emotional state, and both models here are simple enough that they can be systematically wrong for entire groups of people, not just occasionally wrong on individual edge cases.

## 8. Ideas for Improvement

- Add much more labeled data, spread more evenly across all four labels, and written by more than one person, so the dataset does not only reflect one person's sense of tone.
- For the rule based model, keep a short list of words that are known to be unsafe to guess (like "sick," "fire," "wicked") because their meaning depends entirely on context, instead of leaving them out completely or guessing at one meaning.
- Replace `CountVectorizer` with a tokenizer that keeps emoji and contractions intact, or add custom preprocessing before vectorizing, so the ML model can see the same signals the rule based model was built to catch.
- Use TF-IDF instead of raw word counts, so common, low-signal words do not carry the same weight as rarer, more meaningful ones.
- Evaluate the ML model on a genuinely separate holdout set of posts it never trained on, instead of only reporting training accuracy, since training accuracy on a 20-row dataset told us almost nothing true about real performance.
- Consider a small pretrained model or transformer embedding for the ML side, since it would already have some real-world sense of words like "mid" or "fire" instead of learning meaning from scratch off 20 examples.
