# Smart Price Monitor — Playwright Automation (Week 3)

A modular Python 3 + Microsoft Playwright project demonstrating browser launch, navigation, explicit waits, CSS selectors, data extraction, form interaction, validation, screenshots, logging, exception handling, CSV export, PDF reporting, optional email notifications, unit tests, Docker, and GitHub Actions.

> This is an educational demo, not a guarantee of production compatibility with every store. Only automate sites you are allowed to access, respect their terms/robots policies and rate limits, and do not bypass logins, CAPTCHAs, or access controls. The sample performs no purchases.

## Features mapped to the assignment

- Python 3.x and Microsoft Playwright (async API)
- `.env` configuration via `python-dotenv`; `.env` is git-ignored
- Logging to terminal and `logs/automation.log`
- Exception handling and browser/page cleanup with `try/finally` and async context managers
- Full-page screenshots on successful price checks; error screenshot on timeout
- README and modular reusable functions
- Browser launch, navigation, explicit waits, form interaction and execution validation
- Meaningful names, no credentials in source, clean repo structure
- Bonus: Async Playwright, headless/headed modes, CLI, CSV, PDF report, Docker, GitHub Actions, unit tests, optional SMTP email notification

## Project structure

```text
smart-price-monitor-complete/
├── .github/workflows/tests.yml
├── src/price_monitor/
│   ├── automation.py       # Async Playwright workflows
│   ├── cli.py              # CLI and orchestration
│   └── core.py             # Logging, parsing, CSV/PDF/email helpers
├── tests/                  # Unit tests + opt-in online smoke test
├── screenshots/            # Generated browser screenshots
├── output/                 # Generated CSV price history
├── reports/                # Generated PDF report
├── logs/                   # Generated log file
├── .env.example
├── Dockerfile
├── main.py
└── requirements.txt
```

## Setup (macOS / VS Code)

1. Install Python 3.11+ and Git if needed.
2. Extract this ZIP, then open the `smart-price-monitor-complete` folder in VS Code.
3. Open **Terminal → New Terminal** and run:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
```

Windows activation is `.venv\\Scripts\\activate`; copy `.env.example` to `.env` manually or use `copy .env.example .env` in Command Prompt.

## Run price monitoring

Headless (default):

```bash
python main.py price
```

Show browser window:

```bash
python main.py price --headed
```

Override URL/selectors without editing `.env`:

```bash
python main.py price --url "https://www.demoblaze.com/prod.html?idp_=1" --title-selector "h2.name" --price-selector ".price-container" --headed
```

Skip PDF generation:

```bash
python main.py price --no-pdf
```

The public demo website's HTML and availability may change. If selectors time out, open the page manually and inspect the title/price CSS selectors, then update `.env`. A price may be shown as text (for example `$360 *includes tax`); the parser extracts the first numeric amount when possible.

## Run form-filling automation

This workflow fills and submits a public demo form (no real account or personal data) and validates the confirmation message:

```bash
python main.py form-demo
python main.py form-demo --headed
```

It saves `screenshots/form_demo_success.png`.

## Generated artifacts

- `logs/automation.log` — execution status and tracebacks
- `screenshots/price_check_*.png` — full-page product screenshots
- `screenshots/price_check_error.png` — screenshot on selector/navigation timeout
- `screenshots/form_demo_success.png` — form workflow screenshot
- `output/price_history.csv` — timestamp, title, displayed price, parsed price and URL
- `reports/price_report.pdf` — formatted PDF report

Generated output files are git-ignored by design. Keep selected screenshots separately for your submission if required.

## Optional email notifications

Copy `.env.example` to `.env` and fill `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, and `EMAIL_TO` with credentials for an SMTP account you control. Use an app password where the provider requires one. Never commit `.env` or paste credentials into a public repository. If settings are blank, email is skipped. Email failures are logged and do not invalidate an otherwise successful automation run.

## Tests

```bash
pytest -q
```

The default suite tests parsing and CSV behavior offline. An online browser smoke test is opt-in:

```bash
RUN_BROWSER_TESTS=1 pytest -q tests/test_automation.py
```

It needs an internet connection and installed Chromium. Do not claim that tests or live browser runs passed unless you ran them successfully in your environment. GitHub Actions runs the offline unit tests on pushes and pull requests.

## Docker (bonus)

Build:

```bash
docker build -t smart-price-monitor .
```

Run (requires a configured `.env` file):

```bash
docker run --rm --env-file .env -v "$PWD/output:/app/output" -v "$PWD/logs:/app/logs" -v "$PWD/reports:/app/reports" -v "$PWD/screenshots:/app/screenshots" smart-price-monitor
```

## GitHub submission

Create a new GitHub repository (do not initialize it with another README), then run in this folder:

```bash
git init
git add .
git commit -m "Complete Playwright automation project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/smart-price-monitor.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Verify `.env` is not listed in `git status` or committed.

## 2–5 minute demo video plan

1. (0:00–0:20) Introduce project and objective.
2. (0:20–0:50) Show project structure and `.env` (hide any secret values).
3. (0:50–1:40) Run `python main.py price --headed` and explain navigation/waits/selectors.
4. (1:40–2:10) Run `python main.py form-demo --headed` and show confirmation.
5. (2:10–2:40) Show CSV, PDF, screenshot and log files.
6. (2:40–3:10) Run `pytest -q`; show the actual test output.
7. (3:10–3:30) Show GitHub repository and summarize learning.

## LinkedIn post template (mandatory per assignment)

> 🚀 Completed my Week 3 Playwright Automation Project — Smart Price Monitor!
>
> Built with Python and Microsoft Playwright, this project demonstrates async browser automation, price extraction, form filling, validation, screenshots, logging, CSV/PDF reports, optional email notifications, unit tests, Docker, and GitHub Actions.
>
> GitHub: [add your repository URL]
> Demo: [add your 2–5 minute video URL]
>
> #Python #Playwright #Automation #SoftwareTesting #LearningByBuilding

Publish after replacing the placeholders with your real links. The LinkedIn post and demo video must be completed by you; they cannot be created automatically by this repository.

## Troubleshooting

- `python3: command not found`: install Python 3 from python.org or Homebrew, then reopen terminal.
- `playwright install` browser issue: run `python -m playwright install chromium` again.
- `TimeoutError`: verify internet and CSS selectors in `.env`.
- PDF import error: activate `.venv`, then run `pip install -r requirements.txt`.
- Email error: clear optional SMTP settings or verify provider host/port/app password.
