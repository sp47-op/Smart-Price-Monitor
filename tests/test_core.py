from pathlib import Path
from src.price_monitor.core import parse_price, make_record, append_csv


def test_parse_price_dollar():
    assert parse_price("$1,299.00") == 1299.0


def test_parse_price_integer():
    assert parse_price("Price: 799") == 799.0


def test_parse_price_missing():
    assert parse_price("Price unavailable") is None


def test_make_record():
    record = make_record("Demo Phone", "$99.99", "https://example.com/product")
    assert record.title == "Demo Phone"
    assert record.price_value == 99.99
    assert record.url.startswith("https://")


def test_append_csv_writes_header_and_row(tmp_path: Path):
    target = tmp_path / "prices.csv"
    record = make_record("Demo", "$10.00", "https://example.com")
    append_csv(record, target)
    content = target.read_text(encoding="utf-8")
    assert "timestamp_utc,title,price_text,price_value,url" in content
    assert "Demo" in content
