import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models import DiscoveredProblem, RawSearchResult
from app.discovery.engine import ProblemDiscoveryEngine
from app.discovery.duplicate_detector import compute_similarity, DuplicateDetector
from app.analysis.opportunity_analyzer import OpportunityAnalyzer
from app.scoring.scorer import Scorer
from app.database.db import Database
from app.collectors.query_generator import QueryGenerator


def test_models():
    p = DiscoveredProblem(
        problem_statement="Tanzania farmers struggle to find fair market prices",
        category="agriculture",
        target_users="farmers",
        evidence=["Farmers report losing income due to middlemen"],
        sources=["https://example.com"],
    )
    d = p.to_dict()
    assert d["problem_statement"] == p.problem_statement
    assert d["category"] == "agriculture"
    print("PASS: test_models")


def test_query_generator():
    gen = QueryGenerator(max_queries=20)
    queries = gen.build_query_plan()
    assert len(queries) > 0
    assert len(queries) <= 20
    assert len(queries) == len(set(queries))
    print(f"PASS: test_query_generator ({len(queries)} queries)")


def test_problem_discovery():
    engine = ProblemDiscoveryEngine()
    results = [
        RawSearchResult(
            title="How to solve traffic in Dar es Salaam",
            snippet="Many people struggle with daily traffic jams. How can I find alternative routes?",
            url="https://example.com/traffic",
            query_used="dar es salaam traffic",
        ),
        RawSearchResult(
            title="What is the capital of Tanzania",
            snippet="The capital is Dodoma",
            url="https://example.com/dodoma",
            query_used="tanzania capital",
        ),
    ]
    problems = engine.extract_problems(results)
    assert len(problems) >= 1
    print(f"PASS: test_problem_discovery ({len(problems)} problems found)")


def test_similarity():
    sim1 = compute_similarity(
        "How to solve traffic in Dar es Salaam",
        "Dar es Salaam traffic jam problems",
    )
    sim2 = compute_similarity(
        "How to solve traffic in Dar es Salaam",
        "Agriculture challenges for farmers",
    )
    assert sim1 > sim2, f"Expected traffic similarity ({sim1}) > agriculture similarity ({sim2})"
    print(f"PASS: test_similarity (traffic={sim1:.3f}, diff={sim2:.3f})")


def test_duplicate_detector():
    detector = DuplicateDetector(threshold=0.25)
    candidates = [
        DiscoveredProblem(
            problem_statement="Dar es Salaam traffic is terrible and causes long delays",
            evidence=["Traffic jams reported daily"],
        ),
        DiscoveredProblem(
            problem_statement="Dar es Salaam traffic jams waste hours of commuters time",
            evidence=["Commuters complain about traffic"],
        ),
        DiscoveredProblem(
            problem_statement="Farmers cannot find fair prices for their crops",
            evidence=["Agriculture market issues"],
        ),
    ]
    unique = detector.deduplicate(candidates)
    assert len(unique) <= 2, f"Expected <= 2 unique problems, got {len(unique)}"
    print(f"PASS: test_duplicate_detector ({len(unique)} unique from 3 candidates)")


def test_analyzer():
    analyzer = OpportunityAnalyzer()
    problems = [
        DiscoveredProblem(
            problem_statement="Many people struggle with traffic in Dar es Salaam daily. "
            "It is a common frustration that wastes time.",
            category="transportation",
            target_users="commuters, workers",
            evidence=["Source 1", "Source 2", "Source 3"],
        ),
    ]
    analyzed = analyzer.analyze(problems)
    p = analyzed[0]
    assert p.frequency_signals in ("low", "medium", "high")
    assert p.pain_assessment in ("low", "medium", "high")
    assert p.reach_assessment in ("low", "medium", "high")
    print(f"PASS: test_analyzer (freq={p.frequency_signals}, pain={p.pain_assessment}, reach={p.reach_assessment})")


def test_scorer():
    scorer = Scorer()
    problems = [
        DiscoveredProblem(
            problem_statement="Test problem A",
            frequency_signals="high",
            pain_assessment="high",
            reach_assessment="high",
            solution_gap="large",
            feasibility="high",
            human_impact="high",
            evidence=["a", "b", "c"],
        ),
        DiscoveredProblem(
            problem_statement="Test problem B",
            frequency_signals="low",
            pain_assessment="low",
            reach_assessment="low",
            solution_gap="small",
            feasibility="low",
            human_impact="low",
        ),
    ]
    scored = scorer.score(problems)
    assert scored[0].opportunity_score > scored[1].opportunity_score
    print(f"PASS: test_scorer (top={scored[0].opportunity_score:.3f}, bottom={scored[1].opportunity_score:.3f})")


def test_database():
    import tempfile
    import os

    db_path = os.path.join(tempfile.mkdtemp(), "test.db")
    db = Database(db_path)

    problem = DiscoveredProblem(
        problem_statement="Test database problem",
        category="test",
        target_users="testers",
        evidence=["Evidence 1"],
        sources=["https://test.com"],
        opportunity_score=0.75,
    )
    db.save_problem(problem)

    loaded = db.get_all_problems()
    assert len(loaded) == 1
    assert loaded[0].problem_statement == "Test database problem"
    assert loaded[0].opportunity_score == 0.75

    top = db.get_top_problems(1)
    assert len(top) == 1

    try:
        os.remove(db_path)
    except OSError:
        pass
    print("PASS: test_database")


if __name__ == "__main__":
    tests = [
        test_models,
        test_query_generator,
        test_problem_discovery,
        test_similarity,
        test_duplicate_detector,
        test_analyzer,
        test_scorer,
        test_database,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)} tests")
    sys.exit(1 if failed else 0)
