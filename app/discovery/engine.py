import re
from app.models import RawSearchResult, DiscoveredProblem
from app.logging_config import logger

PROBLEM_INDICATORS = [
    r"how (?:do|can|to) (?:i|we|you|people)",
    r"where (?:can|do|is) (?:i|we|you|people)",
    r"why (?:is|are|do|does|can't|cannot) (?:it|there|we|people|the)",
    r"is there (?:an?|any) (?:app|way|method|solution|alternative)",
    r"best (?:way|app|method|tool|solution|approach) (?:to|for)",
    r"problems? (?:with|in|at|during|using)",
    r"difficult(?:y|ies) (?:with|in|at|during|finding|getting)",
    r"frustrat(?:ed|ing|ion)",
    r"complain(?:ts?|ed|ing)",
    r"challeng(?:es?|ing)",
    r"struggl(?:es?|ed|ing) (?:to|with|in)",
    r"cannot|can't|unable (?:to|to find|to get)",
    r"no (?:way|solution|option|app|alternative)",
    r"lack of",
    r"missing",
    r"need(?:s)? (?:a|an|to|better|more|improved)",
    r"improve(?:ment)? (?:needed|required)",
    r"waste(?:d|s)? (?:of|time|money)",
    r"confus(?:ed|ing|ion)",
    r"inefficien(?:t|cy)",
    r"pain(?:ful|s)? (?:point|of|with)",
    r"tedious",
    r"broken",
    r"doesn't work|does not work",
    r"not working|not available|not accessible",
    r"too (?:expensive|slow|difficult|complicated|hard)",
    r"long (?:wait|queue|time|process)",
]

EVIDENCE_PATTERNS = [
    r"many (?:people|users|citizens|Tanzanians)",
    r"common(?:ly)? (?:reported|complained|experienced)",
    r"recurring (?:issue|problem|complaint)",
    r"frequently (?:asked|reported|experienced)",
    r"majority of",
    r"widespread",
    r"pervasive",
    r"growing (?:problem|concern|issue)",
    r"increasing(?:ly)? (?:common|frequent|difficult)",
    r"daily (?:challenge|problem|struggle)",
    r"everyday (?:problem|challenge|issue)",
    r"major (?:challenge|problem|issue|obstacle)",
]

SWAHILI_INDICATORS = [
    r"je (?:kuna|watu|kuna mtu)",
    r"tatizo",
    r"matatizo",
    r"changamoto",
    r"ugomvi",
    r"shida",
    r"namna (?:gani|ya)",
    r"jinsi (?:ya|ya kupata)",
    r"suluhisho",
    r"mkakati",
    r"wanahitaji",
    r"wanapata",
    r"dhidi ya",
    r"kuhusu",
]

VAGUE_PATTERNS = [
    r"^what is .{0,20}$",
    r"^who is .{0,30}$",
    r"^when (?:is|was|did) .{0,30}$",
    r"^define ",
    r"^meaning of ",
    r"^history of ",
    r"^difference between .{0,20}$",
]

ONETIME_PATTERNS = [
    r"results (?:20\d{2})$",
    r"exam results",
    r"admission (?:list|results)",
    r"(?:school|university) (?:calendar| schedule)",
    r"holidays? (?:20\d{2})",
    r"(?:mpesa|m-pesa) (?:offers?|promotion)",
]

CATEGORY_KEYWORDS = {
    "transportation": [
        "traffic", "transport", "bus", "daladala", "bajaj",
        "commute", "travel", "road", "driving", "parking", "bodaboda",
    ],
    "finance": [
        "money", "mobile", "mpesa", "m-pesa", "bank",
        "loan", "savings", "payment", "financial", "insurance",
        "debt", "credit", "pesa",
    ],
    "agriculture": [
        "farm", "crop", "agriculture", "harvest", "market",
        "irrigation", "fertilizer", "livestock", "food", "kilimo",
    ],
    "education": [
        "school", "student", "university", "exam", "learn",
        "teacher", "education", "study", "necta", "fees", "elimu",
    ],
    "healthcare": [
        "health", "hospital", "medicine", "doctor", "patient",
        "clinic", "drug", "treatment", "maternal", "afya",
    ],
    "government_services": [
        "government", "nida", "passport", "license", "permit",
        "registration", "tax", "public service", "rta",
    ],
    "employment": [
        "job", "employ", "work", "career", "hire",
        "unemploy", "recruit", "salary", "wage", "ajira",
    ],
    "business": [
        "business", "startup", "entrepreneur", "customer",
        "supply", "market", "compete", "sell", "vendor", "biashara",
    ],
    "housing": [
        "house", "rent", "apartment", "building", "construct",
        "property", "land", "tenant", "nyumba",
    ],
    "communication": [
        "internet", "network", "phone", "connect",
        "wifi", "data", "signal", "communication",
    ],
    "shopping": [
        "shop", "buy", "deliver", "order", "consumer",
        "product", "price", "store", "online",
    ],
}

USER_PROFILES = {
    "students": ["student", "school", "university", "exam", "learn"],
    "farmers": ["farm", "crop", "agriculture", "harvest", "kilimo"],
    "small business owners": [
        "small business", "vendor", "entrepreneur", "shop owner",
    ],
    "workers": ["worker", "employee", "salary", "workplace", "commute"],
    "families": ["family", "household", "parent", "children"],
    "young people": ["youth", "young", "graduate", "teen"],
    "commuters": ["commute", "transport", "bus", "travel", "traffic"],
    "patients": ["patient", "hospital", "clinic", "health", "sick"],
    "entrepreneurs": ["entrepreneur", "startup", "business", "innovat"],
}


class ProblemDiscoveryEngine:
    def __init__(self, min_problems: int = 50):
        self.min_problems = min_problems
        self.discovered_topics: list[str] = []

    def extract_problems(
        self, results: list[RawSearchResult]
    ) -> list[DiscoveredProblem]:
        problems: list[DiscoveredProblem] = []

        for result in results:
            extracted = self._analyze_result(result)
            problems.extend(extracted)

        logger.info(
            "Extracted %d raw candidates from %d results",
            len(problems),
            len(results),
        )

        filtered = self._filter_problems(problems)
        logger.info("After filtering: %d problems remain", len(filtered))

        return filtered

    def _analyze_result(
        self, result: RawSearchResult
    ) -> list[DiscoveredProblem]:
        problems = []
        text = f"{result.title} {result.snippet}".lower()

        has_indicator = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in PROBLEM_INDICATORS + SWAHILI_INDICATORS
        )

        if has_indicator:
            problem_statement = self._extract_problem_statement(result)
            if problem_statement:
                category = self._categorize(text)
                target_users = self._identify_users(text)
                evidence_count = len(
                    [p for p in EVIDENCE_PATTERNS if re.search(p, text, re.IGNORECASE)]
                )
                problems.append(
                    DiscoveredProblem(
                        problem_statement=problem_statement,
                        category=category,
                        target_users=target_users,
                        evidence=[result.snippet],
                        sources=[result.url],
                        raw_evidence=[
                            {
                                "title": result.title,
                                "snippet": result.snippet,
                                "url": result.url,
                                "query": result.query_used,
                            }
                        ],
                        frequency_signals=self._estimate_frequency(evidence_count, text),
                    )
                )

                topic = self._extract_topic(text)
                if topic:
                    self.discovered_topics.append(topic)

        return problems

    def _extract_problem_statement(
        self, result: RawSearchResult
    ) -> str | None:
        text = f"{result.title}. {result.snippet}"
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

        if not sentences:
            combined = f"{result.title}: {result.snippet}"
            return combined[:300] if len(combined) > 30 else None

        scored = []
        all_indicators = PROBLEM_INDICATORS + SWAHILI_INDICATORS
        for sentence in sentences:
            score = sum(
                1 for p in all_indicators
                if re.search(p, sentence, re.IGNORECASE)
            )
            if score > 0:
                scored.append((score, sentence))

        if scored:
            scored.sort(key=lambda x: (-x[0], -len(x[1])))
            return scored[0][1]

        if len(result.title) > 20:
            return f"{result.title}: {result.snippet}"[:300]

        if sentences:
            return sentences[0]

        return None

    def _estimate_frequency(self, evidence_hits: int, text: str) -> str:
        high_words = [
            "common", "frequent", "always", "every day", "daily",
            "recurring", "widespread", "many people", "everyone",
            "constantly", "repeatedly",
        ]
        high = sum(1 for w in high_words if w in text)
        if evidence_hits >= 2 or high >= 2:
            return "high"
        elif evidence_hits >= 1 or high >= 1:
            return "medium"
        return "low"

    def _categorize(self, text: str) -> str:
        scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[category] = score
        if scores:
            return max(scores, key=scores.get)
        return "general"

    def _identify_users(self, text: str) -> str:
        found = []
        for profile, keywords in USER_PROFILES.items():
            if any(kw in text for kw in keywords):
                found.append(profile)
        return ", ".join(found) if found else "general population"

    def _extract_topic(self, text: str) -> str | None:
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after",
            "above", "below", "between", "out", "off", "over", "under",
            "again", "further", "then", "once", "here", "there", "when",
            "where", "why", "how", "all", "both", "each", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only",
            "own", "same", "so", "than", "too", "very", "just",
        }
        words = text.split()
        topic_words = []
        for word in words:
            clean = re.sub(r"[^a-zA-Z]", "", word).lower()
            if clean and clean not in stop_words and len(clean) > 3:
                topic_words.append(clean)
        if topic_words:
            return " ".join(topic_words[:3])
        return None

    def _filter_problems(
        self, problems: list[DiscoveredProblem]
    ) -> list[DiscoveredProblem]:
        filtered = []
        seen_statements = set()

        for problem in problems:
            statement = problem.problem_statement.lower().strip()

            if statement in seen_statements:
                continue
            seen_statements.add(statement)

            if any(
                re.search(p, statement, re.IGNORECASE) for p in VAGUE_PATTERNS
            ):
                continue

            if any(
                re.search(p, statement, re.IGNORECASE) for p in ONETIME_PATTERNS
            ):
                continue

            if len(statement) < 30:
                continue

            filtered.append(problem)

        return filtered

    def get_discovered_topics(self) -> list[str]:
        return list(set(self.discovered_topics))
