from app.models import DiscoveredProblem
from app.logging_config import logger

WEIGHTS = {
    "frequency": 0.20,
    "pain": 0.20,
    "reach": 0.20,
    "solution_gap": 0.15,
    "feasibility": 0.10,
    "human_impact": 0.15,
}

LEVEL_SCORES = {
    "high": 1.0,
    "medium": 0.6,
    "low": 0.2,
}

SOLUTION_GAP_SCORES = {
    "large": 1.0,
    "medium": 0.6,
    "small": 0.2,
}


class Scorer:
    def score(self, problems: list[DiscoveredProblem]) -> list[DiscoveredProblem]:
        for problem in problems:
            problem.opportunity_score = self._compute_score(problem)

        problems.sort(key=lambda p: p.opportunity_score, reverse=True)

        if problems:
            logger.info(
                "Scored %d problems. Top: %.3f, Bottom: %.3f",
                len(problems),
                problems[0].opportunity_score,
                problems[-1].opportunity_score,
            )
        return problems

    def _compute_score(self, problem: DiscoveredProblem) -> float:
        components = {
            "frequency": LEVEL_SCORES.get(problem.frequency_signals, 0.2),
            "pain": LEVEL_SCORES.get(problem.pain_assessment, 0.2),
            "reach": LEVEL_SCORES.get(problem.reach_assessment, 0.2),
            "solution_gap": SOLUTION_GAP_SCORES.get(problem.solution_gap, 0.2),
            "feasibility": LEVEL_SCORES.get(problem.feasibility, 0.2),
            "human_impact": LEVEL_SCORES.get(problem.human_impact, 0.2),
        }

        total = sum(components[k] * WEIGHTS[k] for k in WEIGHTS)
        evidence_bonus = min(len(problem.evidence) * 0.02, 0.1)
        return round(total + evidence_bonus, 4)

    def rank(self, problems: list[DiscoveredProblem], top_n: int = 5) -> list[DiscoveredProblem]:
        scored = self.score(problems)
        return scored[:top_n]
