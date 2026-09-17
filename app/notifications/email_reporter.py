import smtplib
import time
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import Config
from app.models import DiscoveredProblem, Opportunity
from app.logging_config import logger


class EmailReporter:
    def __init__(self):
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_user = Config.SMTP_USER
        self.smtp_password = Config.SMTP_PASSWORD
        self.recipient = Config.REPORT_RECIPIENT
        self.max_retries = 3
        self.retry_delay = 5

    def send_daily_report(
        self,
        top_problems: list[DiscoveredProblem],
        total_discovered: int,
        total_after_filter: int,
        run_date: datetime | None = None,
    ) -> bool:
        if not run_date:
            run_date = datetime.now(timezone.utc)

        opportunities = [
            Opportunity.from_problem(i + 1, p)
            for i, p in enumerate(top_problems)
        ]

        subject = f"Tanzania Problem Finder - Ripoti ya Siku {run_date.strftime('%Y-%m-%d')}"
        html_body = self._build_html(opportunities, total_discovered, total_after_filter, run_date)
        plain_body = self._build_plain(opportunities, total_discovered, total_after_filter, run_date)

        for attempt in range(1, self.max_retries + 1):
            try:
                self._send_email(subject, html_body, plain_body)
                logger.info("Email imetumwa kwa %s", self.recipient)
                return True
            except Exception as e:
                logger.error(
                    "Jaribio la barua pepe %d/%d limefungwa: %s",
                    attempt, self.max_retries, e,
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)

        logger.error("Barua pepe imefungwa baada ya majaribio %d", self.max_retries)
        return False

    def _send_email(self, subject: str, html_body: str, plain_body: str):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.smtp_user
        msg["To"] = self.recipient

        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, [self.recipient], msg.as_string())

    def _build_html(
        self,
        opportunities: list[Opportunity],
        total_discovered: int,
        total_after_filter: int,
        run_date: datetime,
    ) -> str:
        date_str = run_date.strftime("%d/%m/%Y")
        cards = []

        for opp in opportunities:
            cards.append(f"""
            <div style="background:#f8f9fa;border-left:4px solid #007bff;padding:18px;margin:18px 0;border-radius:6px;">
                <h3 style="color:#007bff;margin:0 0 12px 0;">Fursa #{opp.rank}</h3>
                <table style="width:100%;border-collapse:collapse;font-size:14px;">
                    <tr><td style="padding:8px;font-weight:bold;width:180px;vertical-align:top;">Tatizo</td><td style="padding:8px;">{self._esc(opp.problem)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Nani ana tatizo hili</td><td style="padding:8px;">{self._esc(opp.who_has_problem)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Ushahidi</td><td style="padding:8px;font-style:italic;color:#555;">{self._esc(opp.evidence)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Imeenea kiasi gani</td><td style="padding:8px;">{self._esc(opp.how_widespread)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Suluhisho linalowezekana</td><td style="padding:8px;">{self._esc(opp.possible_solution)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Suluhisho zilizopo</td><td style="padding:8px;">{self._esc(opp.existing_solutions)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Kinachokosekana</td><td style="padding:8px;">{self._esc(opp.whats_missing)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">MVP rahisi</td><td style="padding:8px;">{self._esc(opp.simple_mvp)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Athari kwa binadamu</td><td style="padding:8px;">{self._esc(opp.human_impact)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Mapato baadaye</td><td style="padding:8px;">{self._esc(opp.monetization_later)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Hatua ya uthibitisho</td><td style="padding:8px;">{self._esc(opp.validation_step)}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Alama</td><td style="padding:8px;">{opp.score:.3f}</td></tr>
                </table>
            </div>
            """)

        cards_html = "\n".join(cards)

        return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;color:#333;">
    <h1 style="border-bottom:2px solid #007bff;padding-bottom:10px;">
        Tanzania Problem Finder - Ripoti ya Siku
    </h1>
    <p style="color:#666;font-size:14px;">Tarehe: {date_str}</p>
    <div style="background:#e9ecef;padding:15px;border-radius:6px;margin:20px 0;">
        <h3 style="margin:0 0 8px 0;">Muhtasari wa Uendeshaji</h3>
        <p style="margin:4px 0;">Matatizo yaliyogunduliwa: <strong>{total_discovered}</strong></p>
        <p style="margin:4px 0;">Baada ya uchunguzi: <strong>{total_after_filter}</strong></p>
        <p style="margin:4px 0;">Fursa bora: <strong>{len(opportunities)}</strong></p>
    </div>
    <h2>Fursa {len(opportunities)} Bora</h2>
    {cards_html}
    <hr style="margin:30px 0;">
    <p style="color:#999;font-size:12px;">
        Imetengenezwa na Tanzania Problem Finder | Uchunguzi unaotegemea ushahidi
    </p>
</body>
</html>
        """

    def _build_plain(
        self,
        opportunities: list[Opportunity],
        total_discovered: int,
        total_after_filter: int,
        run_date: datetime,
    ) -> str:
        date_str = run_date.strftime("%d/%m/%Y")
        lines = [
            "=" * 60,
            "TANZANIA PROBLEM FINDER - RIPOTI YA SIKU",
            f"Tarehe: {date_str}",
            "=" * 60,
            "",
            f"Matatizo yaliyogunduliwa: {total_discovered}",
            f"Baada ya uchunguzi: {total_after_filter}",
            f"Fursa bora: {len(opportunities)}",
            "",
            "-" * 60,
        ]

        for opp in opportunities:
            lines.extend([
                "",
                f"FURSA #{opp.rank}",
                f"  Tatizo: {opp.problem}",
                f"  Nani ana tatizo hili: {opp.who_has_problem}",
                f"  Ushahidi: {opp.evidence}",
                f"  Imeenea kiasi gani: {opp.how_widespread}",
                f"  Suluhisho linalowezekana: {opp.possible_solution}",
                f"  Suluhisho zilizopo: {opp.existing_solutions}",
                f"  Kinachokosekana: {opp.whats_missing}",
                f"  MVP rahisi: {opp.simple_mvp}",
                f"  Athari kwa binadamu: {opp.human_impact}",
                f"  Mapato baadaye: {opp.monetization_later}",
                f"  Hatua ya uthibitisho: {opp.validation_step}",
                f"  Alama: {opp.score:.3f}",
                "-" * 60,
            ])

        lines.extend([
            "",
            "Imetengenezwa na Tanzania Problem Finder",
            "Uchunguzi unaotegemea ushahidi",
        ])
        return "\n".join(lines)

    def _esc(self, text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
