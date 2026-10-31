"""Network-dependent smoke tests are deliberately opt-in."""
import os
import pytest
from src.price_monitor.automation import fill_demo_form


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("RUN_BROWSER_TESTS") != "1", reason="Set RUN_BROWSER_TESTS=1 to run online browser smoke test")
async def test_public_demo_form():
    result = await fill_demo_form(headless=True)
    assert result["status"] == "PASS"
    assert "Received!" in result["confirmation"]
