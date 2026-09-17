from app.models import RawSearchResult, DiscoveredProblem, Opportunity


def test_raw_search_result():
    r = RawSearchResult(
        title="Test Title",
        snippet="Test snippet about problems",
        url="https://example.com",
        query_used="test query",
        source="google_search",
    )
    assert r.title == "Test Title"
    assert r.source == "google_search"


def test_discovered_problem_defaults():
    p = DiscoveredProblem(problem_statement="People struggle with transport in Dar")
    assert p.category == ""
    assert p.opportunity_score == 0.0
    assert p.status == "discovered"
    assert p.evidence == []
    assert p.sources == []


def test_discovered_problem_to_dict():
    p = DiscoveredProblem(
        problem_statement="Test problem",
        category="finance",
        evidence=["evidence1"],
    )
    d = p.to_dict()
    assert isinstance(d, dict)
    assert d["problem_statement"] == "Test problem"
    assert d["category"] == "finance"
    assert d["evidence"] == ["evidence1"]


def test_opportunity_from_problem():
    p = DiscoveredProblem(
        problem_statement="Students cannot access study materials online",
        category="education",
        target_users="students",
        evidence=["Many students complain about lack of online resources"],
        existing_solutions="few",
        solution_gap="large",
        frequency_signals="high",
        pain_assessment="high",
        reach_assessment="medium",
        feasibility="high",
        human_impact="high",
        monetization_possibility="medium",
        opportunity_score=0.85,
    )
    opp = Opportunity.from_problem(1, p)
    assert opp.rank == 1
    assert opp.problem == "Students cannot access study materials online"
    assert opp.who_has_problem == "students"
    assert opp.score == 0.85
    assert "students" in opp.validation_step.lower()
