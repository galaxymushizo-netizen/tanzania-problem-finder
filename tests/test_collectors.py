from app.collectors.query_generator import QueryGenerator


def test_build_query_plan_returns_queries():
    gen = QueryGenerator(max_queries=20)
    queries = gen.build_query_plan()
    assert len(queries) > 0
    assert len(queries) <= 20


def test_query_plan_deduplicates():
    gen = QueryGenerator(max_queries=50)
    queries = gen.build_query_plan()
    assert len(queries) == len(set(q.lower() for q in queries))


def test_follow_up_queries():
    gen = QueryGenerator()
    follow_ups = gen.generate_follow_up_queries(["mobile money", "traffic"])
    assert len(follow_ups) > 0
    assert any("mobile money" in q for q in follow_ups)
    assert any("traffic" in q for q in follow_ups)


def test_add_discovered_topics():
    gen = QueryGenerator(max_queries=10)
    gen.add_discovered_topics(["healthcare", "education"])
    assert "healthcare" in gen._discovered_topics
    assert "education" in gen._discovered_topics


def test_add_discovered_topics_dedup():
    gen = QueryGenerator()
    gen.add_discovered_topics(["test", "test", "other"])
    assert len(gen._discovered_topics) == 2
