"""Reusable helpers for price monitoring, CSV/PDF reports, and notifications."""
from __future__ import annotations

import csv
import logging
import os
import re
import smtplib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
SCREENSHOT_DIR = ROOT / "screenshots"
REPORT_DIR = ROOT / "reports"


def configure_logging(level: str = "INFO") -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("price_monitor")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        file_handler = logging.FileHandler(LOG_DIR / "automation.log", encoding="utf-8")
        console_handler = logging.StreamHandler()
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger


def parse_price(raw: str) -> Optional[float]:
    """Return the first decimal number from text such as '$1,299.00' or None."""
    if not raw:
        return None
    match = re.search(r"\d[\d,]*(?:\.\d{1,2})?", raw.replace("\u00a0", " "))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None


@dataclass
class PriceRecord:
    timestamp_utc: str
    title: str
    price_text: str
    price_value: Optional[float]
    url: str


def make_record(title: str, price_text: str, url: str) -> PriceRecord:
    return PriceRecord(
        timestamp_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        title=title.strip(), price_text=price_text.strip(),
        price_value=parse_price(price_text), url=url,
    )


def append_csv(record: PriceRecord, path: Path | None = None) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = path or OUTPUT_DIR / "price_history.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    fields = list(asdict(record).keys())
    write_header = not target.exists() or target.stat().st_size == 0
    with target.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow(asdict(record))
    return target


def create_pdf_report(record: PriceRecord, path: Path | None = None) -> Path:
    """Create a concise PDF report. Requires reportlab (listed in requirements)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    target = path or REPORT_DIR / "price_report.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(target), pagesize=A4, title="Smart Price Monitor Report")
    data = [["Field", "Value"], ["Product", record.title], ["Displayed price", record.price_text],
            ["Parsed numeric price", str(record.price_value) if record.price_value is not None else "Not detected"],
            ["Page URL", record.url], ["Timestamp (UTC)", record.timestamp_utc]]
    table = Table(data, colWidths=[135, 360], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    doc.build([Paragraph("Smart Price Monitor — Run Report", styles["Title"]), Spacer(1, 16), table])
    return target


def send_email_notification(subject: str, body: str) -> bool:
    """Send optional SMTP email; returns False if not configured, raises on SMTP errors."""
    host = os.getenv("SMTP_HOST", "").strip()
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("EMAIL_FROM", "").strip()
    recipient = os.getenv("EMAIL_TO", "").strip()
    if not all([host, username, password, sender, recipient]):
        return False
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)
    port = int(os.getenv("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=20) as server:
        server.ehlo()
        if os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}:
            server.starttls()
            server.ehlo()
        server.login(username, password)
        server.send_message(message)
    return True
