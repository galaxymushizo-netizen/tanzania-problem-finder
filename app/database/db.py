import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.models import DiscoveredProblem
from app.config import Config
from app.logging_config import logger


class Database:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or Config.DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS problems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_statement TEXT NOT NULL,
                    category TEXT,
                    target_users TEXT,
                    evidence TEXT,
                    sources TEXT,
                    date_discovered TEXT,
                    frequency_signals TEXT,
                    pain_assessment TEXT,
                    reach_assessment TEXT,
                    existing_solutions TEXT,
                    solution_gap TEXT,
                    feasibility TEXT,
                    human_impact TEXT,
                    monetization_possibility TEXT,
                    ai_analysis TEXT,
                    opportunity_score REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'discovered',
                    historical_occurrences TEXT,
                    raw_evidence TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_date TEXT NOT NULL,
                    problems_discovered INTEGER DEFAULT 0,
                    problems_filtered INTEGER DEFAULT 0,
                    top_opportunities TEXT,
                    report_sent INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_problems_score
                ON problems(opportunity_score DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_problems_date
                ON problems(date_discovered)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_problems_category
                ON problems(category)
            """)
        logger.info("Database initialized: %s", self.db_path)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_problem(self, problem: DiscoveredProblem) -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO problems (
                    problem_statement, category, target_users,
                    evidence, sources, date_discovered,
                    frequency_signals, pain_assessment, reach_assessment,
                    existing_solutions, solution_gap, feasibility,
                    human_impact, monetization_possibility, ai_analysis,
                    opportunity_score, status, historical_occurrences,
                    raw_evidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    problem.problem_statement,
                    problem.category,
                    problem.target_users,
                    json.dumps(problem.evidence),
                    json.dumps(problem.sources),
                    problem.date_discovered,
                    problem.frequency_signals,
                    problem.pain_assessment,
                    problem.reach_assessment,
                    problem.existing_solutions,
                    problem.solution_gap,
                    problem.feasibility,
                    problem.human_impact,
                    problem.monetization_possibility,
                    problem.ai_analysis,
                    problem.opportunity_score,
                    problem.status,
                    json.dumps(problem.historical_occurrences),
                    json.dumps(problem.raw_evidence),
                ),
            )
            return cursor.lastrowid

    def save_problems(self, problems: list[DiscoveredProblem]) -> int:
        count = 0
        for problem in problems:
            self.save_problem(problem)
            count += 1
        logger.info("Saved %d problems to database", count)
        return count

    def get_all_problems(self) -> list[DiscoveredProblem]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM problems ORDER BY opportunity_score DESC"
            ).fetchall()
        return [self._row_to_problem(row) for row in rows]

    def get_top_problems(self, n: int = 5) -> list[DiscoveredProblem]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM problems ORDER BY opportunity_score DESC LIMIT ?",
                (n,),
            ).fetchall()
        return [self._row_to_problem(row) for row in rows]

    def get_recent_problems(self, days: int = 7) -> list[DiscoveredProblem]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM problems
                WHERE date_discovered >= date('now', ?)
                ORDER BY opportunity_score DESC
                """,
                (f"-{days} days",),
            ).fetchall()
        return [self._row_to_problem(row) for row in rows]

    def problem_exists(self, statement: str) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM problems WHERE problem_statement = ?",
                (statement,),
            ).fetchone()
            return row["cnt"] > 0

    def log_run(
        self,
        discovered: int,
        filtered: int,
        top_opps: list[DiscoveredProblem],
        sent: bool = False,
    ):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO daily_runs
                    (run_date, problems_discovered, problems_filtered,
                     top_opportunities, report_sent)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    discovered,
                    filtered,
                    json.dumps([p.problem_statement for p in top_opps]),
                    1 if sent else 0,
                ),
            )

    def get_run_history(self, days: int = 30) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM daily_runs
                WHERE run_date >= date('now', ?)
                ORDER BY run_date DESC
                """,
                (f"-{days} days",),
            ).fetchall()
        return [dict(row) for row in rows]

    def _row_to_problem(self, row: sqlite3.Row) -> DiscoveredProblem:
        return DiscoveredProblem(
            problem_statement=row["problem_statement"],
            category=row["category"] or "",
            target_users=row["target_users"] or "",
            evidence=json.loads(row["evidence"]) if row["evidence"] else [],
            sources=json.loads(row["sources"]) if row["sources"] else [],
            date_discovered=row["date_discovered"] or "",
            frequency_signals=row["frequency_signals"] or "",
            pain_assessment=row["pain_assessment"] or "",
            reach_assessment=row["reach_assessment"] or "",
            existing_solutions=row["existing_solutions"] or "",
            solution_gap=row["solution_gap"] or "",
            feasibility=row["feasibility"] or "",
            human_impact=row["human_impact"] or "",
            monetization_possibility=row["monetization_possibility"] or "",
            ai_analysis=row["ai_analysis"] or "",
            opportunity_score=row["opportunity_score"] or 0.0,
            status=row["status"] or "discovered",
            historical_occurrences=(
                json.loads(row["historical_occurrences"])
                if row["historical_occurrences"]
                else []
            ),
            raw_evidence=(
                json.loads(row["raw_evidence"]) if row["raw_evidence"] else []
            ),
        )
