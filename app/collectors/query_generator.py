import random
from app.logging_config import logger


SEED_QUERIES = [
    "how to solve problems in Tanzania",
    "Tanzania common challenges daily life",
    "Tanzania frustrations complaints",
    "Tanzania people need help with",
    "dar es salaam traffic problems",
    "Tanzania public transport challenges",
    "bajaj dar es salaam problems",
    "how to travel between cities Tanzania",
    "daladala problems",
    "Tanzania mobile money problems",
    "M-Pesa challenges Tanzania",
    "Tigo Pesa issues",
    "how to send money Tanzania",
    "Tanzania banking problems",
    "unbanked population Tanzania",
    "Tanzania loan difficulties",
    "Tanzania farmers challenges",
    "Tanzania agriculture problems",
    "how to sell crops Tanzania",
    "Tanzania farming technology",
    "Tanzania food prices problems",
    "Tanzania education challenges",
    "Tanzania students problems",
    "how to study Tanzania",
    "Tanzania university challenges",
    "Tanzania exam preparation problems",
    "NECTA results problems",
    "Tanzania healthcare challenges",
    "Tanzania hospital problems",
    "medicine availability Tanzania",
    "Tanzania health services complaints",
    "Tanzania government services online",
    "NIDA problems Tanzania",
    "Tanzania passport application problems",
    "Tanzania driving license problems",
    "TANZANIA land registration problems",
    "Tanzania business registration difficulties",
    "Tanzania job search problems",
    "Tanzania youth unemployment",
    "Tanzania career opportunities",
    "Tanzania freelance work",
    "Tanzania job hunting frustrations",
    "online shopping Tanzania problems",
    "Tanzania delivery services issues",
    "Tanzania market prices",
    "Tanzania consumer problems",
    "Tanzania internet problems",
    "Tanzania phone network issues",
    "Tanzania social media challenges",
    "Tanzania housing challenges",
    "Dar es salaam rent problems",
    "Tanzania construction difficulties",
    "Tanzania small business challenges",
    "Tanzania entrepreneurship problems",
    "Tanzania business licensing difficulties",
    "Tanzania supplier problems",
    "best app for Tanzania",
    "Tanzania technology solutions",
    "how to make life easier Tanzania",
    "Tanzania digital services",
    "Tanzania innovation problems solved",
    "tatizo la usafiri Tanzania",
    "matatizo ya kila siku Tanzania",
    "watu wanahitaji msaada gani Tanzania",
    "ugomvi wa kibiashara Tanzania",
    "tatizo la kilimo Tanzania",
    "matatizo ya elimu Tanzania",
    "tatizo la afya Tanzania",
    "matatizo ya biashara ndogo Tanzania",
    "tatizo la nyumba Tanzania",
    "matatizo ya ajira Tanzania",
]

CATEGORY_QUERIES = {
    "transportation": [
        "dar es salaam traffic jam solution",
        "Tanzania bus system problems",
        "Tanzania motorcycle taxi problems",
        "Tanzania road safety issues",
        "how to commute dar es salaam",
    ],
    "finance": [
        "Tanzania financial inclusion problems",
        "Tanzania savings challenges",
        "Tanzania insurance problems",
        "Tanzania payment difficulties",
        "Tanzania debt problems",
    ],
    "agriculture": [
        "Tanzania post-harvest losses",
        "Tanzania market access farmers",
        "Tanzania farming inputs problems",
        "Tanzania irrigation challenges",
        "Tanzania agricultural information",
    ],
    "education": [
        "Tanzania dropout rates problems",
        "Tanzania teacher challenges",
        "Tanzania school fees problems",
        "Tanzania digital learning challenges",
        "Tanzania vocational training problems",
    ],
    "healthcare": [
        "Tanzania medicine stockouts",
        "Tanzania patient referral problems",
        "Tanzania medical records challenges",
        "Tanzania maternal health problems",
        "Tanzania mental health challenges",
    ],
    "government_services": [
        "Tanzania ID card problems",
        "Tanzania tax filing difficulties",
        "Tanzania permit applications problems",
        "Tanzania public service complaints",
        "Tanzania corruption frustrations",
    ],
    "employment": [
        "Tanzania fresh graduates employment",
        "Tanzania informal sector problems",
        "Tanzania workplace challenges",
        "Tanzania skills mismatch employment",
        "Tanzania remote work challenges",
    ],
    "business": [
        "Tanzania startup challenges",
        "Tanzania market competition problems",
        "Tanzania customer acquisition difficulties",
        "Tanzania supply chain problems",
        "Tanzania business scaling challenges",
    ],
}

FOLLOW_UP_TEMPLATES = [
    "how to solve {topic} in Tanzania",
    "{topic} challenges Tanzania",
    "problems with {topic} Tanzania",
    "Tanzania {topic} complaints",
    "best way to handle {topic} Tanzania",
    "{topic} difficulties dar es salaam",
    "Tanzania people frustrated with {topic}",
    "{topic} alternatives Tanzania",
]

PATTERN_TEMPLATES = [
    "how do I {pattern} Tanzania",
    "where can I {pattern} in Tanzania",
    "why is it difficult to {pattern} Tanzania",
    "is there an app for {pattern} Tanzania",
]


class QueryGenerator:
    def __init__(self, max_queries: int = 30):
        self.max_queries = max_queries
        self._discovered_topics: list[str] = []

    def build_query_plan(self) -> list[str]:
        queries = []

        seed_sample = random.sample(SEED_QUERIES, min(15, len(SEED_QUERIES)))
        queries.extend(seed_sample)

        all_categories = list(CATEGORY_QUERIES.keys())
        selected_categories = random.sample(
            all_categories, min(5, len(all_categories))
        )
        for cat in selected_categories:
            cat_sample = random.sample(
                CATEGORY_QUERIES[cat],
                min(3, len(CATEGORY_QUERIES[cat])),
            )
            queries.extend(cat_sample)

        if self._discovered_topics:
            follow_ups = self.generate_follow_up_queries(self._discovered_topics[:10])
            if follow_ups:
                queries.extend(random.sample(follow_ups, min(10, len(follow_ups))))

        seen = set()
        unique = []
        for q in queries:
            q_lower = q.lower().strip()
            if q_lower not in seen:
                seen.add(q_lower)
                unique.append(q)

        return unique[: self.max_queries]

    def generate_follow_up_queries(self, topics: list[str]) -> list[str]:
        follow_ups = []
        for topic in topics[:15]:
            for template in FOLLOW_UP_TEMPLATES:
                follow_ups.append(template.format(topic=topic))
        return follow_ups

    def generate_pattern_queries(self, patterns: list[str]) -> list[str]:
        queries = []
        for pattern in patterns[:10]:
            for template in PATTERN_TEMPLATES:
                queries.append(template.format(pattern=pattern))
        return queries

    def add_discovered_topics(self, topics: list[str]):
        self._discovered_topics.extend(topics)
        seen = set()
        unique = []
        for t in self._discovered_topics:
            t_lower = t.lower().strip()
            if t_lower not in seen:
                seen.add(t_lower)
                unique.append(t)
        self._discovered_topics = unique
