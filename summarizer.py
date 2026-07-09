"""
summarizer.py
Generates a short extractive summary of the resume — no API key required.

Approach: word-frequency scoring (a lightweight, classic NLP technique).
Each sentence is scored by how many "important" (non-stopword) words it
contains, and the top-N highest scoring sentences are returned in their
original order.
"""

import re
from collections import Counter

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "in", "on", "at", "to", "for", "of", "with", "by",
    "from", "as", "this", "that", "these", "those", "i", "we", "you", "he",
    "she", "it", "they", "my", "our", "your", "his", "her", "its", "their",
}


def _split_sentences(text: str) -> list:
    # Simple sentence splitter — good enough for resume-style short sentences/bullets.
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 15]


def extractive_summary(text: str, num_sentences: int = 3) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return "Not enough text to summarize."
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    # Build word frequency table (ignoring stopwords)
    words = re.findall(r"[a-zA-Z]+", text.lower())
    freq = Counter(w for w in words if w not in STOPWORDS)

    # Score each sentence by sum of its word frequencies
    scored = []
    for sentence in sentences:
        sent_words = re.findall(r"[a-zA-Z]+", sentence.lower())
        score = sum(freq.get(w, 0) for w in sent_words)
        scored.append((score, sentence))

    # Take top-N sentences, then restore original order for readability
    top_sentences = sorted(scored, key=lambda x: x[0], reverse=True)[:num_sentences]
    top_set = {s for _, s in top_sentences}
    ordered = [s for s in sentences if s in top_set]

    return " ".join(ordered)
