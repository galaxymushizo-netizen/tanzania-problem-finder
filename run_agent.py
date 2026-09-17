#!/usr/bin/env python3
"""
Tanzania Problem Finder - Mtazamo Mkuu

Matumizi:
    python run_agent.py                       # Endesha mara moja
    python run_agent.py --scheduler           # Anzisha ratiba (kila masaa 3)
    python run_agent.py --scheduler --interval 6   # Kila masaa 6
    python run_agent.py --validate            -# Kagua usanidi
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import Config
from app.logging_config import logger, setup_logging


def validate_config():
    errors = Config.validate()
    warnings = Config.validate_warn()
    if errors:
        logger.error("Hitilafu za usanidi:")
        for err in errors:
            logger.error("  - %s", err)
        return False
    for w in warnings:
        logger.warning(w)
    logger.info("Usanidi umeangaliwa")
    return True


def run_once():
    if not validate_config():
        sys.exit(1)
    from app.pipeline import AgentPipeline
    pipeline = AgentPipeline()
    summary = pipeline.run()
    print("\n" + "=" * 60)
    print("MUHTASARI WA UENDESHAJI")
    print("=" * 60)
    print(f"  Yaliyogunduliwa: matatizo {summary['total_discovered']}")
    print(f"  Baada ya uchunguzi: matatizo {summary['total_after_dedup']}")
    print(f"  Barua pepe imetumwa: {'Ndiyo' if summary['email_sent'] else 'Hapana'}")
    if summary["top_opportunities"]:
        print(f"\n  Fursa {len(summary['top_opportunities'])} Bora:")
        for opp in summary["top_opportunities"]:
            print(
                f"    #{opp['rank']}: [{opp['category']}] "
                f"{opp['problem'][:80]}... (alama: {opp['score']:.3f})"
            )
    if summary["errors"]:
        print(f"\n  Hitilafu: {summary['errors']}")
    print("=" * 60)
    return summary


def run_scheduler(interval_hours: int | None = None):
    if not validate_config():
        sys.exit(1)
    from app.scheduler.scheduler import Scheduler
    scheduler = Scheduler(interval_hours=interval_hours)
    scheduler.start()


def main():
    setup_logging()
    logger.info("Tanzania Problem Finder inaanza")

    args = sys.argv[1:]

    if "--scheduler" in args:
        idx = args.index("--scheduler")
        interval = None
        if "--interval" in args:
            int_idx = args.index("--interval")
            if int_idx + 1 < len(args):
                interval = int(args[int_idx + 1])
        run_scheduler(interval_hours=interval)
    elif "--validate" in args:
        validate_config()
    elif "--help" in args or "-h" in args:
        print(__doc__)
    elif not args:
        run_once()
    else:
        print(f"Amri haijulikani: {args[0]}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
