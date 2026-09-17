from app.models import DiscoveredProblem
from app.scoring.scorer import Scorer


def test_score_returns_sorted():
    scorer = Scorer()
    problems = [
        DiscoveredProblem(
            problem_statement="Low impact problem",
            frequency_signals="low",
            pain_assessment="low",
            reach_assessment="low",
            solution_gap="small",
            feasibility="low",
            human_impact="low",
        ),
        DiscoveredProblem(
            problem_statement="High impact problem with many people affected daily",
            frequency_signals="high",
            pain_assessment="high",
            reach_assessment="high",
            solution_gap="large",
            feasibility="high",
            human_impact="high",
            evidence=["e1", "e2", "e3"],
        ),
    ]
    scored = scorer.score(problems)
    assert scored[0].opportunity_score > scored[1].opportunity_score
    assert scored[0].problem_statement == "High impact problem with many people affected daily"


def test_score_range():
    scorer = Scorer()
    p = DiscoveredProblem(
        problem_statement="Test problem",
        frequency_signals="medium",
        pain_assessment="medium",
        reach_assessment="medium",
        solution_gap="medium",
        feasibility="medium",
        human_impact="medium",
    )
    scored = scorer.score([p])
    score = scored[0].opportunity_score
    assert 0.0 <= score <= 1.0


def test_evidence_bonus():
    scorer = Scorer()
    p_no_evidence = DiscoveredProblem(
        problem_statement="Test problem A",
        frequency_signals="medium",
        pain_assessment="medium",
        reach_assessment="medium",
        solution_gap="medium",
        feasibility="medium",
        human_impact="medium",
        evidence=[],
    )
    p_many_evidence = DiscoveredProblem(
        problem_statement="Test problem B",
        frequency_signals="medium",
        pain_assessment="medium",
        reach_assessment="medium",
        solution_gap="medium",
        feasibility="medium",
        human_impact="medium",
        evidence=["e1", "e2", "e3", "e4", "e5"],
    )
    scored = scorer.score([p_no_evidence, p_many_evidence])
    assert scored[0].opportunity_score >= scored[1].opportunity_score


def test_rank():
    scorer = Scorer()
    problems = [
        DiscoveredProblem(problem_statement=f"Problem {i}", frequency_signals="low")
        for i in range(10)
    ]
    top = scorer.rank(problems, top_n=3)
    assert len(top) == 3
