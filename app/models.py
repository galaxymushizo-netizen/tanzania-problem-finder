from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class RawSearchResult:
    title: str
    snippet: str
    url: str
    query_used: str
    source: str = "google_search"


@dataclass
class DiscoveredProblem:
    problem_statement: str
    category: str = ""
    target_users: str = ""
    evidence: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    date_discovered: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    frequency_signals: str = ""
    pain_assessment: str = ""
    reach_assessment: str = ""
    existing_solutions: str = ""
    solution_gap: str = ""
    feasibility: str = ""
    human_impact: str = ""
    monetization_possibility: str = ""
    ai_analysis: str = ""
    opportunity_score: float = 0.0
    status: str = "discovered"
    historical_occurrences: list[dict[str, Any]] = field(default_factory=list)
    raw_evidence: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Opportunity:
    rank: int
    problem: str
    who_has_problem: str
    evidence: str
    how_widespread: str
    possible_solution: str
    existing_solutions: str
    whats_missing: str
    simple_mvp: str
    human_impact: str
    monetization_later: str
    validation_step: str
    score: float

    @classmethod
    def from_problem(cls, rank: int, p: DiscoveredProblem) -> "Opportunity":
        evidence_text = (
            "; ".join(p.evidence[:3]) if p.evidence else "Insufficient evidence."
        )
        return cls(
            rank=rank,
            problem=p.problem_statement,
            who_has_problem=p.target_users or "General population",
            evidence=evidence_text,
            how_widespread=f"{p.frequency_signals} frequency, {p.reach_assessment} reach",
            possible_solution=_suggest_solution(p),
            existing_solutions=p.existing_solutions or "Insufficient evidence",
            whats_missing=p.solution_gap or "Insufficient evidence",
            simple_mvp=_suggest_mvp(p),
            human_impact=p.human_impact or "Insufficient evidence",
            monetization_later=p.monetization_possibility or "Low",
            validation_step=_suggest_validation(p),
            score=p.opportunity_score,
        )


def _suggest_solution(p: DiscoveredProblem) -> str:
    category_solutions = {
        "finance": "Mobile app or USSD service for financial access",
        "education": "Web or mobile learning platform",
        "healthcare": "Appointment booking or health info service",
        "transportation": "Route planning or booking app",
        "government_services": "Digital service portal or chatbot",
        "employment": "Job matching platform or skill-building app",
        "agriculture": "Market price or farming advice service",
        "business": "Business management or marketplace tool",
        "shopping": "E-commerce or delivery coordination platform",
        "housing": "Property listing or rental matching service",
        "communication": "Community or messaging service",
    }
    return category_solutions.get(
        p.category, "AI agent or digital service addressing the gap"
    )


def _suggest_mvp(p: DiscoveredProblem) -> str:
    if p.category in ("finance", "government_services"):
        return "WhatsApp or Telegram bot providing key information"
    if p.category in ("education", "employment"):
        return "Simple web app with curated resources"
    if p.category == "healthcare":
        return "SMS or USSD service for basic health guidance"
    if p.category == "transportation":
        return "Web app showing routes and schedules"
    return "Simple web page or chatbot addressing the core need"


def _suggest_validation(p: DiscoveredProblem) -> str:
    users = p.target_users.lower()
    if "student" in users:
        return "Survey 20 students at a local university about this problem"
    if "farmer" in users:
        return "Visit a local market and ask 10 farmers about this challenge"
    if "business" in users or "entrepreneur" in users:
        return "Interview 5 small business owners in your area"
    return "Post in 3 Tanzanian Facebook/WhatsApp groups and collect responses"
