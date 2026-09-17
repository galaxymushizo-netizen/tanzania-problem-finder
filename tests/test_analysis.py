from app.models import DiscoveredProblem
from app.analysis.opportunity_analyzer import OpportunityAnalyzer


def test_analyze_populates_fields():
    analyzer = OpportunityAnalyzer()
    problems = [
        DiscoveredProblem(
            problem_statement="Students struggle with finding affordable study materials online in Tanzania",
            category="education",
            target_users="students",
            evidence=["Many students report this", "Widespread complaint"],
        ),
    ]
    result = analyzer.analyze(problems)
    assert len(result) == 1
    p = result[0]
    assert p.frequency_signals in ("high", "medium", "low")
    assert p.pain_assessment in ("high", "medium", "low")
    assert p.reach_assessment in ("high", "medium", "low")
    assert p.existing_solutions in ("none", "few", "several")
    assert p.solution_gap in ("large", "medium", "small")
    assert p.feasibility in ("high", "medium", "low")
    assert p.human_impact in ("high", "medium", "low")
    assert p.monetization_possibility in ("high", "medium", "low")
    assert p.ai_analysis != ""


def test_analyze_high_pain_problem():
    analyzer = OpportunityAnalyzer()
    problems = [
        DiscoveredProblem(
            problem_statement="Patients cannot access medicine at hospitals, dangerous and critical situation",
            category="healthcare",
            target_users="patients",
            evidence=["Many people report this"],
        ),
    ]
    result = analyzer.analyze(problems)
    p = result[0]
    assert p.pain_assessment == "high"
