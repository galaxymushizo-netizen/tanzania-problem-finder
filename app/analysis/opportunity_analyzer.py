from app.models import DiscoveredProblem
from app.logging_config import logger


class OpportunityAnalyzer:
    def analyze(self, problems: list[DiscoveredProblem]) -> list[DiscoveredProblem]:
        for problem in problems:
            problem.frequency_signals = problem.frequency_signals or self._assess_frequency(problem)
            problem.pain_assessment = self._assess_pain(problem)
            problem.reach_assessment = self._assess_reach(problem)
            problem.existing_solutions = self._assess_existing_solutions(problem)
            problem.solution_gap = self._assess_solution_gap(problem)
            problem.feasibility = self._assess_feasibility(problem)
            problem.human_impact = self._assess_human_impact(problem)
            problem.monetization_possibility = self._assess_monetization(problem)
            problem.ai_analysis = self._generate_analysis(problem)

        logger.info("Analyzed %d problems", len(problems))
        return problems

    def _assess_frequency(self, problem: DiscoveredProblem) -> str:
        evidence_count = len(problem.evidence)
        text = problem.problem_statement.lower()
        high_words = [
            "common", "frequent", "always", "every day", "daily",
            "recurring", "widespread", "many people", "everyone",
        ]
        med_words = [
            "often", "sometimes", "regular", "usually", "many", "several",
        ]
        high = sum(1 for w in high_words if w in text)
        med = sum(1 for w in med_words if w in text)
        if evidence_count >= 5 or high >= 2:
            return "high"
        elif evidence_count >= 2 or high >= 1 or med >= 2:
            return "medium"
        return "low"

    def _assess_pain(self, problem: DiscoveredProblem) -> str:
        text = problem.problem_statement.lower()
        high_pain = [
            "difficult", "impossible", "frustrat", "struggle", "pain",
            "waste", "lost", "broken", "fail", "danger", "risk",
            "suffer", "crisis", "urgent", "critical", "severe",
            "exploit", "corrupt", "scam", "fraud",
        ]
        med_pain = [
            "problem", "challenge", "issue", "concern", "trouble",
            "confus", "inefficien", "slow", "expensive", "tedious",
        ]
        high = sum(1 for w in high_pain if w in text)
        med = sum(1 for w in med_pain if w in text)
        if high >= 2:
            return "high"
        elif high >= 1 or med >= 2:
            return "medium"
        return "low"

    def _assess_reach(self, problem: DiscoveredProblem) -> str:
        text = problem.problem_statement.lower()
        users = problem.target_users.lower()
        large = [
            "everyone", "all tanzanians", "general population",
            "ordinary people", "citizens", "millions",
        ]
        med = [
            "students", "workers", "families", "commuters",
            "patients", "entrepreneurs", "farmers",
        ]
        large_hits = sum(1 for g in large if g in text or g in users)
        med_hits = sum(1 for g in med if g in text or g in users)
        if large_hits >= 1:
            return "high"
        elif med_hits >= 1:
            return "medium"
        return "low"

    def _assess_existing_solutions(self, problem: DiscoveredProblem) -> str:
        text = problem.problem_statement.lower()
        evidence_text = " ".join(problem.evidence).lower()
        combined = f"{text} {evidence_text}"
        solution_words = [
            "app", "website", "service", "solution", "platform",
            "tool", "system", "alternative",
        ]
        no_solution_words = [
            "no solution", "no app", "no alternative", "nothing",
            "lack of", "missing", "not available", "no way",
        ]
        sol = sum(1 for w in solution_words if w in combined)
        no_sol = sum(1 for w in no_solution_words if w in combined)
        if no_sol >= 2 or sol == 0:
            return "none"
        elif sol >= 3:
            return "several"
        return "few"

    def _assess_solution_gap(self, problem: DiscoveredProblem) -> str:
        existing = self._assess_existing_solutions(problem)
        text = problem.problem_statement.lower()
        gap_words = [
            "but", "however", "although", "unfortunately",
            "still", "yet", "doesn't", "not good", "poor", "limited",
        ]
        gap_hits = sum(1 for w in gap_words if w in text)
        if existing == "none":
            return "large"
        elif existing == "few" or gap_hits >= 2:
            return "medium"
        return "small"

    def _assess_feasibility(self, problem: DiscoveredProblem) -> str:
        category = problem.category.lower()
        text = problem.problem_statement.lower()
        easy_categories = [
            "finance", "communication", "education", "government_services",
            "shopping", "employment",
        ]
        medium_categories = ["transportation", "healthcare", "business"]
        digital_words = [
            "app", "online", "digital", "website", "platform", "system",
        ]
        manual_words = [
            "infrastructure", "road", "building", "physical", "construction",
        ]
        digital = sum(1 for w in digital_words if w in text)
        manual = sum(1 for w in manual_words if w in text)
        if category in easy_categories and digital >= 1:
            return "high"
        elif category in medium_categories or manual == 0:
            return "medium"
        return "low"

    def _assess_human_impact(self, problem: DiscoveredProblem) -> str:
        text = problem.problem_statement.lower()
        pain = self._assess_pain(problem)
        reach = self._assess_reach(problem)
        impact_words = [
            "life", "livelihood", "health", "safety", "education",
            "income", "poverty", "survival", "wellbeing", "dignity",
        ]
        impact_hits = sum(1 for w in impact_words if w in text)
        if (pain == "high" and reach in ("high", "medium")) or impact_hits >= 2:
            return "high"
        elif pain in ("high", "medium") and reach != "low":
            return "medium"
        return "low"

    def _assess_monetization(self, problem: DiscoveredProblem) -> str:
        category = problem.category.lower()
        text = problem.problem_statement.lower()
        monetizable = {
            "finance": "high",
            "business": "high",
            "shopping": "medium",
            "transportation": "medium",
            "education": "medium",
            "healthcare": "medium",
            "employment": "medium",
        }
        if category in monetizable:
            return monetizable[category]
        transaction_words = [
            "pay", "buy", "sell", "price", "cost", "money", "market",
        ]
        if sum(1 for w in transaction_words if w in text) >= 2:
            return "medium"
        return "low"

    def _generate_analysis(self, problem: DiscoveredProblem) -> str:
        return (
            f"Frequency: {problem.frequency_signals}. "
            f"Pain: {problem.pain_assessment}. "
            f"Reach: {problem.reach_assessment}. "
            f"Existing solutions: {problem.existing_solutions}. "
            f"Solution gap: {problem.solution_gap}. "
            f"Feasibility: {problem.feasibility}. "
            f"Human impact: {problem.human_impact}. "
            f"Monetization: {problem.monetization_possibility}. "
            f"Evidence sources: {len(problem.evidence)}."
        )
