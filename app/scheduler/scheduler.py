import time
import signal
from datetime import datetime, timedelta, timezone

from app.config import Config
from app.pipeline import AgentPipeline
from app.logging_config import logger


class Scheduler:
    def __init__(self, interval_hours: int | None = None):
        if interval_hours is None:
            interval_hours = Config.SCHEDULER_INTERVAL_HOURS
        self.interval_seconds = interval_hours * 3600
        self.running = True
        self.pipeline = AgentPipeline()

        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        logger.info("Shutdown signal %d received. Stopping...", signum)
        self.running = False

    def run_once(self):
        return self.pipeline.run()

    def start(self):
        hours = self.interval_seconds // 3600
        minutes = (self.interval_seconds % 3600) // 60
        if minutes:
            logger.info("Scheduler started. Interval: %dh %dm", hours, minutes)
        else:
            logger.info("Scheduler started. Interval: %d hours", hours)

        while self.running:
            try:
                self.run_once()
            except Exception as e:
                logger.error("Scheduler run failed: %s", e, exc_info=True)

            sleep_until = datetime.now(timezone.utc) + timedelta(seconds=self.interval_seconds)
            while self.running and datetime.now(timezone.utc) < sleep_until:
                time.sleep(10)

        logger.info("Scheduler stopped.")
