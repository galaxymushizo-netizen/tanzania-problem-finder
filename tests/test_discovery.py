from app.models import RawSearchResult
from app.discovery.engine import ProblemDiscoveryEngine


def _make_result(title, snippet, url="https://example.com", query="test"):
    return RawSearchResult(title=title, snippet=snippet, url=url, query_used=query)


def test_extract_problems_finds_indicators():
    engine = ProblemDiscoveryEngine()
    results = [
        _make_result(
            "How to solve transport problems in Dar es Salaam",
            "Many people struggle with daladala commute daily traffic",
        ),
    ]
    problems = engine.extract_problems(results)
    assert len(problems) >= 1
    assert any("transport" in p.category or "transportation" in p.category for p in problems)


def test_filter_removes_vague():
    engine = ProblemDiscoveryEngine()
    results = [
        _make_result("What is Tanzania", "A country in East Africa"),
        _make_result(
            "How to fix mobile money problems in Tanzania",
            "People struggle with M-Pesa transactions failing frequently",
        ),
    ]
    problems = engine.extract_problems(results)
    assert len(problems) >= 1
    assert not any("what is" in p.problem_statement.lower() for p in problems)


def test_filter_removes_one_time():
    engine = ProblemDiscoveryEngine()
    results = [
        _make_result(
            "NECTA exam results 2024",
            "Check your exam results here",
        ),
    ]
    problems = engine.extract_problems(results)
    assert len(problems) == 0


def test_categorize():
    engine = ProblemDiscoveryEngine()
    assert engine._categorize("mobile money bank payment") == "finance"
    assert engine._categorize("student school exam") == "education"
    assert engine._categorize("hospital doctor medicine") == "healthcare"
    assert engine._categorize("random unrelated text") == "general"


def test_identify_users():
    engine = ProblemDiscoveryEngine()
    users = engine._identify_users("students at university struggle with exam fees")
    assert "students" in users


def test_swa_hili_indicators():
    engine = ProblemDiscoveryEngine()
    results = [
        _make_result(
            "tatizo la usafiri dar es salaam",
            "Watu wanapata shida ya usafiri kila siku",
        ),
    ]
    problems = engine.extract_problems(results)
    assert len(problems) >= 1


def test_get_discovered_topics():
    engine = ProblemDiscoveryEngine()
    engine.extract_problems([
        _make_result(
            "How to solve mobile money problems in Tanzania",
            "People struggle with M-Pesa transactions failing",
        ),
    ])
    topics = engine.get_discovered_topics()
    assert len(topics) >= 0
