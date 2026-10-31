"""Command-line interface."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

from .automation import (
    monitor_price,
    fill_demo_form,
    monitor_multiple_products,
)
from .core import configure_logging, send_email_notification


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smart Price Monitor — Playwright automation project"
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Single product command
    price = sub.add_parser(
        "price",
        help="Monitor one product",
    )
    price.add_argument("--url", default=None)
    price.add_argument("--title-selector", default=None)
    price.add_argument("--price-selector", default=None)
    price.add_argument(
        "--headed",
        action="store_true",
        help="Show the browser window",
    )
    price.add_argument(
        "--keep-open",
        action="store_true",
        help="Keep browser open until Enter is pressed",
    )
    price.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF report generation",
    )

    # Multiple products command
    batch = sub.add_parser(
        "batch",
        help="Monitor multiple products from a CSV file",
    )
    batch.add_argument(
        "--products-file",
        default="products.csv",
        help="Path to the products CSV file",
    )
    batch.add_argument("--headed", action="store_true")
    batch.add_argument("--keep-open", action="store_true")
    batch.add_argument("--no-pdf", action="store_true")

    # Demo form command
    form = sub.add_parser(
        "form-demo",
        help="Fill and validate a public demo form",
    )
    form.add_argument("--headed", action="store_true")

    return parser


async def run(args: argparse.Namespace) -> int:
    load_dotenv()

    logger = configure_logging(
        os.getenv("LOG_LEVEL", "INFO")
    )
    timeout = int(
        os.getenv("TIMEOUT_MS", "15000")
    )

    try:
        if args.command == "price":
            url = args.url or os.getenv("PRODUCT_URL", "")
            title_selector = (
                args.title_selector
                or os.getenv("TITLE_SELECTOR", "")
            )
            price_selector = (
                args.price_selector
                or os.getenv("PRICE_SELECTOR", "")
            )

            if not all([url, title_selector, price_selector]):
                raise ValueError(
                    "PRODUCT_URL, TITLE_SELECTOR, and PRICE_SELECTOR "
                    "must be set in .env or provided as CLI options."
                )

            record = await monitor_price(
                url=url,
                title_selector=title_selector,
                price_selector=price_selector,
                timeout_ms=timeout,
                headless=not args.headed,
                make_pdf=not args.no_pdf,
                keep_open=args.keep_open,
            )

            logger.info(
                "Price run passed: title=%r price=%r parsed=%r",
                record.title,
                record.price_text,
                record.price_value,
            )

            body = (
                f"Product: {record.title}\n"
                f"Price: {record.price_text}\n"
                f"URL: {record.url}\n"
                f"UTC: {record.timestamp_utc}"
            )

            try:
                if send_email_notification(
                    "Smart Price Monitor report",
                    body,
                ):
                    logger.info("Email notification sent")
                else:
                    logger.info(
                        "Email notification skipped "
                        "(SMTP not configured)"
                    )
            except Exception:
                logger.exception(
                    "Email notification failed; "
                    "main automation succeeded"
                )

            print(
                f"\nSUCCESS: {record.title}\n"
                f"Price: {record.price_text}\n"
                "CSV: output/price_history.csv\n"
                "PDF: reports/price_report.pdf\n"
                "Screenshot: screenshots/\n"
            )

            return 0

        elif args.command == "batch":
            results = await monitor_multiple_products(
                products_file=args.products_file,
                timeout_ms=timeout,
                headless=not args.headed,
                make_pdf=not args.no_pdf,
                keep_open=args.keep_open,
            )

            print(
                f"\nBatch complete: "
                f"{len(results)} product(s) collected."
            )

            return 0 if results else 1

        elif args.command == "form-demo":
            result = await fill_demo_form(
                headless=not args.headed,
                timeout_ms=timeout,
            )

            logger.info(
                "Form demo %s: %s",
                result["status"],
                result["confirmation"],
            )

            print(
                f"\nFORM DEMO {result['status']}: "
                f"{result['confirmation']}\n"
                "Screenshot: screenshots/form_demo_success.png\n"
            )

            return 0

        return 1

    except Exception as exc:
        logger.exception("Automation failed: %s", exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
