
"""Asynchronous Playwright workflows."""

from __future__ import annotations

import asyncio
import csv
from pathlib import Path

from playwright.async_api import (
    async_playwright,
)

from .core import (
    SCREENSHOT_DIR,
    make_record,
    append_csv,
    create_pdf_report,
)


async def monitor_price(
    url: str,
    title_selector: str,
    price_selector: str,
    timeout_ms: int = 15000,
    headless: bool = True,
    make_pdf: bool = True,
    keep_open: bool = False,
):
    """Open one product page and save its price."""

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=headless
        )

        page = await browser.new_page(
            viewport={"width": 1440, "height": 1000}
        )

        try:
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )

            title_element = page.locator(title_selector).first
            price_element = page.locator(price_selector).first

            await title_element.wait_for(
                state="visible",
                timeout=timeout_ms,
            )
            await price_element.wait_for(
                state="visible",
                timeout=timeout_ms,
            )

            title = (await title_element.inner_text()).strip()
            price_text = (
                await price_element.inner_text()
            ).strip()

            if not title or not price_text:
                raise ValueError(
                    "Product title or price is empty. "
                    "Check your CSS selectors."
                )

            record = make_record(
                title,
                price_text,
                page.url,
            )

            stamp = record.timestamp_utc.replace(":", "-")

            await page.screenshot(
                path=str(
                    SCREENSHOT_DIR
                    / f"price_check_{stamp}.png"
                ),
                full_page=True,
            )

            append_csv(record)

            if make_pdf:
                create_pdf_report(record)

            print(f"Product: {record.title}")
            print(f"Price: {record.price_text}")

            if keep_open and not headless:
                await asyncio.to_thread(
                    input,
                    "\nPrice check complete. Press Enter to close the browser...",
                )

            return record

        except Exception as exc:
            try:
                await page.screenshot(
                    path=str(
                        SCREENSHOT_DIR
                        / "price_check_error.png"
                    ),
                    full_page=True,
                )
            except Exception:
                pass

            print(f"\nAutomation error: {exc}")

            if keep_open and not headless:
                await asyncio.to_thread(
                    input,
                    "\nBrowser is open for inspection. Press Enter to close it...",
                )

            raise

        finally:
            await page.close()
            await browser.close()


async def monitor_multiple_products(
    products_file: str = "products.csv",
    timeout_ms: int = 15000,
    headless: bool = True,
    make_pdf: bool = False,
    keep_open: bool = False,
):
    """Monitor multiple products listed in a CSV file."""

    csv_path = Path(products_file)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Products file not found: {csv_path.resolve()}"
        )

    with csv_path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        products = list(csv.DictReader(file))

    if not products:
        raise ValueError(
            "products.csv has no product rows."
        )

    results = []

    for index, product in enumerate(products, start=1):
        url = (product.get("url") or "").strip()
        title_selector = (
            product.get("title_selector") or ""
        ).strip()
        price_selector = (
            product.get("price_selector") or ""
        ).strip()

        if not all([url, title_selector, price_selector]):
            print(
                f"Skipping row {index}: "
                "URL or selector is missing."
            )
            continue

        print(f"\nChecking product {index}: {url}")

        try:
            record = await monitor_price(
                url=url,
                title_selector=title_selector,
                price_selector=price_selector,
                timeout_ms=timeout_ms,
                headless=headless,
                make_pdf=make_pdf,
                keep_open=keep_open,
            )

            results.append(record)

            print(
                f"SUCCESS: {record.title} — "
                f"{record.price_text}"
            )

        except Exception as exc:
            print(f"FAILED: {url}\nReason: {exc}")

    print(
        f"\nFinished: {len(results)} product(s) collected."
    )

    return results


async def fill_demo_form(
    headless: bool = True,
    timeout_ms: int = 15000,
    keep_open: bool = False,
) -> dict[str, str]:
    """Fill and validate a public demonstration form."""

    url = "https://www.selenium.dev/selenium/web/web-form.html"

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=headless
        )

        page = await browser.new_page()

        try:
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )

            await page.locator(
                "input[name='my-text']"
            ).fill("Playwright Demo")

            await page.locator(
                "input[name='my-password']"
            ).fill("demo-only-password")

            await page.locator(
                "textarea[name='my-textarea']"
            ).fill("Automated form submission test")

            await page.locator(
                "button[type='submit']"
            ).click()

            confirmation = page.locator("#message")

            await confirmation.wait_for(
                state="visible",
                timeout=timeout_ms,
            )

            result = (
                await confirmation.inner_text()
            ).strip()

            if "Received!" not in result:
                raise AssertionError(
                    f"Unexpected form confirmation: {result}"
                )

            await page.screenshot(
                path=str(
                    SCREENSHOT_DIR / "form_demo_success.png"
                ),
                full_page=True,
            )

            if keep_open and not headless:
                await asyncio.to_thread(
                    input,
                    "\nForm demo complete. Press Enter to close the browser...",
                )

            return {
                "url": page.url,
                "confirmation": result,
                "status": "PASS",
            }

        finally:
            await page.close()
            await browser.close()

