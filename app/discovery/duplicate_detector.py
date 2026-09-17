import re
from collections import Counter
from app.models import DiscoveredProblem
from app.config import Config
from app.logging_config import logger


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{2,}\b", text.lower())


def _jaccard_similarity(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def _ngram_similarity(text_a: str, text_b: str, n: int = 2) -> float:
    def get_ngrams(text: str) -> Counter:
        tokens = _tokenize(text)
        return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))

    ngrams_a = get_ngrams(text_a)
    ngrams_b = get_ngrams(text_b)
    if not ngrams_a or not ngrams_b:
        return 0.0
    intersection = sum((ngrams_a & ngrams_b).values())
    total = sum(ngrams_a.values()) + sum(ngrams_b.values())
    if total == 0:
        return 0.0
    return (2 * intersection) / total


def _keyword_overlap(text_a: str, text_b: str) -> float:
    stop_words = {
        "the", "is", "in", "for", "to", "of", "and", "a", "on", "with",
        "that", "this", "it", "from", "or", "an", "at", "by", "as",
        "how", "do", "does", "can", "why", "where", "when", "what",
        "which", "who", "whom", "there", "here", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "will", "would",
        "could", "should", "may", "might", "shall", "not", "no", "but",
    }
    keywords_a = set(_tokenize(text_a)) - stop_words
    keywords_b = set(_tokenize(text_b)) - stop_words
    return _jaccard_similarity(keywords_a, keywords_b)


def _phrase_overlap(text_a: str, text_b: str) -> float:
    stop_words = {
        "the", "is", "in", "for", "to", "of", "and", "a", "on", "with",
        "that", "this", "it", "from", "or", "an", "at", "by", "as",
        "how", "do", "does", "can", "why", "where", "when", "what",
        "which", "who", "there", "here", "are", "was", "were", "be",
        "not", "no", "but", "has", "have", "had",
    }

    def get_clean_tokens(text: str) -> list[str]:
        return [t for t in _tokenize(text) if t not in stop_words]

    tokens_a = get_clean_tokens(text_a)
    tokens_b = get_clean_tokens(text_b)

    shared_phrases = 0
    total_phrases = 0
    for n in [2, 3]:
        phrases_a = set(tuple(tokens_a[i : i + n]) for i in range(len(tokens_a) - n + 1))
        phrases_b = set(tuple(tokens_b[i : i + n]) for i in range(len(tokens_b) - n + 1))
        if phrases_a and phrases_b:
            shared_phrases += len(phrases_a & phrases_b)
            total_phrases += len(phrases_a | phrases_b)

    if total_phrases == 0:
        return 0.0
    return shared_phrases / total_phrases


def compute_similarity(text_a: str, text_b: str) -> float:
    jaccard = _jaccard_similarity(set(_tokenize(text_a)), set(_tokenize(text_b)))
    bigram = _ngram_similarity(text_a, text_b, n=2)
    keyword = _keyword_overlap(text_a, text_b)
    phrase = _phrase_overlap(text_a, text_b)
    return 0.2 * jaccard + 0.3 * bigram + 0.2 * keyword + 0.3 * phrase


class DuplicateDetector:
    def __init__(self, threshold: float | None = None):
        self.threshold = threshold or Config.DUPLICATE_THRESHOLD
        self.known_problems: list[DiscoveredProblem] = []

    def load_known(self, problems: list[DiscoveredProblem]):
        self.known_problems = list(problems)
        logger.info("Loaded %d known problems for dedup", len(self.known_problems))

    def deduplicate(
        self, candidates: list[DiscoveredProblem]
    ) -> list[DiscoveredProblem]:
        unique = []
        for candidate in candidates:
            is_duplicate = False

            for existing in unique:
                sim = compute_similarity(
                    candidate.problem_statement,
                    existing.problem_statement,
                )
                if sim >= self.threshold:
                    existing.evidence.extend(candidate.evidence)
                    existing.sources.extend(candidate.sources)
                    existing.raw_evidence.extend(candidate.raw_evidence)
                    is_duplicate = True
                    break

            if not is_duplicate:
                for known in self.known_problems:
                    sim = compute_similarity(
                        candidate.problem_statement,
                        known.problem_statement,
                    )
                    if sim >= self.threshold:
                        is_duplicate = True
                        break

            if not is_duplicate:
                unique.append(candidate)

        removed = len(candidates) - len(unique)
        logger.info(
            "Dedup: %d -> %d (-%d)",
            len(candidates),
            len(unique),
            removed,
        )
        return unique
