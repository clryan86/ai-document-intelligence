from __future__ import annotations

import re
from collections import Counter

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]{2,}")

def chunk_text(text: str, target_words: int = 180, overlap_words: int = 30) -> list[str]:
    words = text.split()
    if not words: return []
    chunks=[]; step=max(1,target_words-overlap_words)
    for start in range(0,len(words),step):
        piece=words[start:start+target_words]
        if not piece: break
        chunks.append(" ".join(piece))
        if start+target_words>=len(words): break
    return chunks

def summarize(text: str, max_sentences: int = 4) -> str:
    sentences=[s.strip() for s in _SENTENCE_RE.split(text) if len(s.strip())>25]
    if not sentences: return text[:900].strip()
    if len(sentences)<=max_sentences: return " ".join(sentences)
    try:
        matrix=TfidfVectorizer(stop_words="english").fit_transform(sentences); scores=matrix.sum(axis=1).A1
    except ValueError:
        return " ".join(sentences[:max_sentences])
    ranked=sorted(range(len(sentences)),key=lambda i:scores[i],reverse=True)[:max_sentences]; ranked.sort()
    return " ".join(sentences[i] for i in ranked)

def extract_keywords(text: str, limit: int = 10) -> list[str]:
    words=[w.lower() for w in _WORD_RE.findall(text)]; words=[w for w in words if w not in ENGLISH_STOP_WORDS]
    if not words: return []
    return [word for word,_ in Counter(words).most_common(limit)]

def semantic_search(query: str, chunks: list[str], limit: int = 8) -> list[tuple[int,float]]:
    if not query.strip() or not chunks: return []
    try:
        matrix=TfidfVectorizer(stop_words="english",ngram_range=(1,2)).fit_transform([query,*chunks])
    except ValueError:
        return []
    similarities=cosine_similarity(matrix[0:1],matrix[1:])[0]
    ranked=sorted(enumerate(similarities),key=lambda item:item[1],reverse=True)
    return [(index,float(score)) for index,score in ranked[:limit] if score>0]
