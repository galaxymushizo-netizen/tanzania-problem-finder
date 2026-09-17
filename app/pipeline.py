from datetime import datetime, timezone

from app.collectors.google_collector import GoogleSearchCollector
from app.collectors.bing_collector import BingSearchCollector
from app.collectors.brave_collector import BraveSearchCollector
from app.collectors.tavily_collector import TavilySearchCollector
from app.collectors.duckduckgo_collector import DuckDuckGoCollector
from app.collectors.query_generator import QueryGenerator
from app.discovery.engine import ProblemDiscoveryEngine
from app.discovery.duplicate_detector import DuplicateDetector
from app.analysis.opportunity_analyzer import OpportunityAnalyzer
from app.scoring.scorer import Scorer
from app.database.db import Database
from app.notifications.email_reporter import EmailReporter
from app.config import Config
from app.logging_config import logger


class AgentPipeline:
    def __init__(self):
        self.query_gen = QueryGenerator(max_queries=Config.MAX_QUERIES_PER_RUN)
        self.google_collector = GoogleSearchCollector()
        self.bing_collector = BingSearchCollector()
        self.brave_collector = BraveSearchCollector()
        self.tavily_collector = TavilySearchCollector()
        self.ddg_collector = DuckDuckGoCollector()
        self.discovery = ProblemDiscoveryEngine(min_problems=Config.MIN_PROBLEMS_TO_DISCOVER)
        self.dedup = DuplicateDetector()
        self.analyzer = OpportunityAnalyzer()
        self.scorer = Scorer()
        self.db = Database()
        self.reporter = EmailReporter()

    def run(self) -> dict:
        run_start = datetime.now(timezone.utc)
        logger.info("=" * 60)
        logger.info("Pipeline started at %s", run_start.isoformat())
        logger.info("=" * 60)

        summary = {
            "run_date": run_start.isoformat(),
            "total_discovered": 0,
            "total_after_filter": 0,
            "total_after_dedup": 0,
            "top_opportunities": [],
            "email_sent": False,
            "errors": [],
        }

        try:
            logger.info("Step 1: Building query plan")
            queries = self.query_gen.build_query_plan()
            logger.info("Generated %d queries", len(queries))

            logger.info("Step 2: Collecting search results")
            all_results = []

            google_results = self.google_collector.search_multiple(
                queries, num_results=Config.SEARCH_RESULTS_PER_QUERY
            )
            all_results.extend(google_results)

            bing_results = self.bing_collector.search_multiple(
                queries[:15], num_results=5
            )
            all_results.extend(bing_results)

            brave_results = self.brave_collector.search_multiple(
                queries[:15], num_results=5
            )
            all_results.extend(brave_results)

            tavily_results = self.tavily_collector.search_multiple(
                queries[:15], num_results=5
            )
            all_results.extend(tavily_results)

            ddg_results = self.ddg_collector.search_multiple(
                queries[:15], num_results=5
            )
            all_results.extend(ddg_results)

            logger.info("Collected %d raw results", len(all_results))

            if not all_results:
                logger.warning("No search results collected")
                summary["errors"].append("No search results collected")
                return summary

            logger.info("Step 3: Discovering problems")
            problems = self.discovery.extract_problems(all_results)
            summary["total_discovered"] = len(problems)

            if not problems:
                logger.warning("No problems discovered")
                summary["errors"].append("No problems discovered")
                return summary

            logger.info("Step 4: Deduplication")
            known = self.db.get_all_problems()
            self.dedup.load_known(known)
            unique_problems = self.dedup.deduplicate(problems)
            summary["total_after_filter"] = len(unique_problems)

            logger.info("Step 5: Follow-up queries")
            topics = self.discovery.get_discovered_topics()
            if topics:
                self.query_gen.add_discovered_topics(topics)
                follow_up_queries = self.query_gen.generate_follow_up_queries(
                    topics[:8]
                )[:10]
                if follow_up_queries:
                    follow_up_results = self.ddg_collector.search_multiple(
                        follow_up_queries, num_results=5
                    )
                    follow_up_problems = self.discovery.extract_problems(follow_up_results)
                    unique_problems.extend(follow_up_problems)
                    unique_problems = self.dedup.deduplicate(unique_problems)
                    logger.info("After follow-up: %d unique", len(unique_problems))

            summary["total_after_dedup"] = len(unique_problems)

            logger.info("Step 6: Analyzing opportunities")
            analyzed = self.analyzer.analyze(unique_problems)

            logger.info("Step 7: Scoring and ranking")
            scored = self.scorer.score(analyzed)

            logger.info("Step 8: Saving to database")
            self.db.save_problems(scored)

            logger.info("Step 9: Getting top opportunities")
            top_n = Config.TOP_OPPORTUNITIES
            top_problems = scored[:top_n]
            summary["top_opportunities"] = [
                {
                    "rank": i + 1,
                    "problem": p.problem_statement,
                    "score": p.opportunity_score,
                    "category": p.category,
                }
                for i, p in enumerate(top_problems)
            ]

            logger.info("Step 10: Sending email report")
            email_sent = self.reporter.send_daily_report(
                top_problems=top_problems,
                total_discovered=summary["total_discovered"],
                total_after_filter=summary["total_after_dedup"],
                run_date=run_start,
            )
            summary["email_sent"] = email_sent

            self.db.log_run(
                discovered=summary["total_discovered"],
                filtered=summary["total_after_dedup"],
                top_opps=top_problems,
                sent=email_sent,
            )

        except Exception as e:
            logger.error("Pipeline error: %s", e, exc_info=True)
            summary["errors"].append(str(e))

        run_end = datetime.now(timezone.utc)
        duration = (run_end - run_start).total_seconds()
        logger.info("Pipeline completed in %.1f seconds", duration)
        logger.info("Summary: %s", summary)

        return summary
