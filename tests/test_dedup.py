from app.models import DiscoveredProblem
from app.discovery.duplicate_detector import DuplicateDetector, compute_similarity


def test_compute_similarity_identical():
    sim = compute_similarity(
        "how to solve mobile money problems in Tanzania",
        "how to solve mobile money problems in Tanzania",
    )
    assert sim > 0.9


def test_compute_similarity_similar():
    sim = compute_similarity(
        "how to solve mobile money problems in Tanzania",
        "how to fix mobile money issues in Tanzania",
    )
    assert sim > 0.3


def test_compute_similarity_different():
    sim = compute_similarity(
        "how to solve mobile money problems in Tanzania",
        "students struggle with university exam fees",
    )
    assert sim < 0.5


def test_deduplicate_removes_duplicates():
    detector = DuplicateDetector(threshold=0.3)
    p1 = DiscoveredProblem(
        problem_statement="How to solve mobile money problems in Tanzania",
        evidence=["evidence1"],
    )
    p2 = DiscoveredProblem(
        problem_statement="How to fix mobile money issues in Tanzania",
        evidence=["evidence2"],
    )
    p3 = DiscoveredProblem(
        problem_statement="Students struggle with university exam fees in Dar",
        evidence=["evidence3"],
    )
    unique = detector.deduplicate([p1, p2, p3])
    assert len(unique) == 2
    assert len(unique[0].evidence) == 2


def test_deduplicate_against_known():
    detector = DuplicateDetector(threshold=0.3)
    known = [
        DiscoveredProblem(
            problem_statement="How to solve mobile money problems in Tanzania",
        ),
    ]
    detector.load_known(known)

    new = [
        DiscoveredProblem(
            problem_statement="How to fix mobile money issues in Tanzania",
            evidence=["new evidence"],
        ),
    ]
    unique = detector.deduplicate(new)
    assert len(unique) == 0
