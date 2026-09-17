# Tanzania Problem Finder

An autonomous AI agent that discovers real problems experienced by people in Tanzania and identifies opportunities to solve them using technology.

## Purpose

The agent searches for evidence-based problems, filters and analyzes them, and produces a daily report of the top 5 opportunities. The primary goal is helping people, not maximizing profit.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys and email settings
```

### 3. Run once

```bash
python run_agent.py
```

### 4. Start scheduler (every 3 hours)

```bash
python run_agent.py --scheduler
```

Custom interval (e.g. every 6 hours):

```bash
python run_agent.py --scheduler --interval 6
```

### 5. Validate configuration

```bash
python run_agent.py --validate
```

## Required API Keys

### Google Custom Search API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable "Custom Search API"
3. Create an API key
4. Create a Custom Search Engine at [cse.google.com](https://cse.google.com)
5. Set `GOOGLE_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID`

**Free tier:** 100 queries/day

### Gmail SMTP

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Set `SMTP_USER` and `SMTP_PASSWORD`

## Project Structure

```
tanzania-problem-finder/
├── app/
│   ├── collectors/     # Data collection from search APIs
│   ├── discovery/      # Problem discovery and deduplication
│   ├── analysis/       # Opportunity analysis
│   ├── scoring/        # Scoring and ranking
│   ├── database/       # SQLite database layer
│   ├── notifications/  # Email reporting
│   └── scheduler/      # Configurable scheduler (default: 3 hours)
├── tests/
├── data/               # Database and logs (auto-created)
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── run_agent.py        # Entry point
```

## Cloud Deployment

### Docker

```bash
docker compose up -d
```

### Linux (cron)

```bash
# Every 3 hours
0 */3 * * * cd /path/to/tanzania-problem-finder && python run_agent.py
```

### systemd timer

Create `/etc/systemd/system/tanzania-finder.service`:

```ini
[Unit]
Description=Tanzania Problem Finder
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/path/to/tanzania-problem-finder
ExecStart=/usr/bin/python3 run_agent.py
User=your-user
```

Create `/etc/systemd/system/tanzania-finder.timer`:

```ini
[Unit]
Description=Run Tanzania Problem Finder every 3 hours

[Timer]
OnCalendar=*-*-* 00/3:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl enable --now tanzania-finder.timer
```

## Evidence Rules

The agent NEVER fabricates:

- Search volume
- Statistics
- User complaints
- Market size
- Competitors
- Trends
- Quotations
- Sources

When reliable evidence is unavailable, it says "Insufficient evidence."

## License

MIT
