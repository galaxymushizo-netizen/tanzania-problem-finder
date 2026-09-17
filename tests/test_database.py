import os
import gc
import tempfile
from app.database.db import Database
from app.models import DiscoveredProblem


def _make_db():
    db_path = os.path.join(tempfile.gettempdir(), f"test_tpf_{id(tempfile)}.db")
    if os.path.exists(db_path):
        os.unlink(db_path)
    return db_path


def test_database_init():
    db_path = _make_db()
    try:
        db = Database(db_path=db_path)
        problems = db.get_all_problems()
        assert problems == []
    finally:
        try:
            del db
            gc.collect()
            os.unlink(db_path)
        except Exception:
            pass


def test_save_and_retrieve():
    db_path = _make_db()
    try:
        db = Database(db_path=db_path)
        p = DiscoveredProblem(
            problem_statement="Test problem for database",
            category="education",
            target_users="students",
            evidence=["evidence1", "evidence2"],
            sources=["https://example.com"],
            frequency_signals="high",
            pain_assessment="medium",
            reach_assessment="high",
            existing_solutions="few",
            solution_gap="large",
            feasibility="high",
            human_impact="high",
            monetization_possibility="medium",
            opportunity_score=0.85,
        )
        db.save_problem(p)

        all_problems = db.get_all_problems()
        assert len(all_problems) == 1
        assert all_problems[0].problem_statement == "Test problem for database"
        assert all_problems[0].evidence == ["evidence1", "evidence2"]
        assert all_problems[0].opportunity_score == 0.85
    finally:
        try:
            del db
            gc.collect()
            os.unlink(db_path)
        except Exception:
            pass


def test_get_top_problems():
    db_path = _make_db()
    try:
        db = Database(db_path=db_path)
        for i in range(5):
            db.save_problem(
                DiscoveredProblem(
                    problem_statement=f"Problem {i}",
                    opportunity_score=i * 0.1,
                )
            )
        top = db.get_top_problems(3)
        assert len(top) == 3
        assert top[0].opportunity_score >= top[1].opportunity_score
    finally:
        try:
            del db
            gc.collect()
            os.unlink(db_path)
        except Exception:
            pass


def test_problem_exists():
    db_path = _make_db()
    try:
        db = Database(db_path=db_path)
        db.save_problem(
            DiscoveredProblem(problem_statement="Unique problem statement")
        )
        assert db.problem_exists("Unique problem statement")
        assert not db.problem_exists("Nonexistent problem")
    finally:
        try:
            del db
            gc.collect()
            os.unlink(db_path)
        except Exception:
            pass


def test_log_run():
    db_path = _make_db()
    try:
        db = Database(db_path=db_path)
        db.log_run(
            discovered=10,
            filtered=8,
            top_opps=[DiscoveredProblem(problem_statement="Top opp")],
            sent=True,
        )
        history = db.get_run_history()
        assert len(history) == 1
    finally:
        try:
            del db
            gc.collect()
            os.unlink(db_path)
        except Exception:
            pass
