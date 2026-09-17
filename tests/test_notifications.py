from datetime import datetime, timezone
from app.models import DiscoveredProblem, Opportunity
from app.notifications.email_reporter import EmailReporter


def test_email_reporter_escapes_html():
    reporter = EmailReporter()
    result = reporter._esc("<script>alert('xss')</script>")
    assert "&lt;" in result
    assert "&gt;" in result


def test_build_plain_format():
    reporter = EmailReporter()
    opp = Opportunity(
        rank=1,
        problem="Students struggle with transport",
        who_has_problem="students",
        evidence="Multiple sources confirm",
        how_widespread="high frequency, medium reach",
        possible_solution="Route planning app",
        existing_solutions="few",
        whats_missing="centralized transport info",
        simple_mvp="Web app with bus routes",
        human_impact="high",
        monetization_later="low",
        validation_step="Survey 20 students",
        score=0.85,
    )
    run_date = datetime.now(timezone.utc)
    plain = reporter._build_plain([opp], 10, 8, run_date)
    assert "FURSA #1" in plain
    assert "Students struggle with transport" in plain
    assert "0.850" in plain


def test_build_html_contains_cards():
    reporter = EmailReporter()
    opp = Opportunity(
        rank=1,
        problem="Test problem",
        who_has_problem="test users",
        evidence="test evidence",
        how_widespread="high",
        possible_solution="test solution",
        existing_solutions="few",
        whats_missing="gap",
        simple_mvp="mvp",
        human_impact="high",
        monetization_later="low",
        validation_step="validate",
        score=0.9,
    )
    run_date = datetime.now(timezone.utc)
    html = reporter._build_html([opp], 10, 8, run_date)
    assert "Fursa #1" in html
    assert "Test problem" in html
    assert "<!DOCTYPE html>" in html
