"""
Regression tests for field value extraction:
- link text vs href depends on field type
- truncated link text falls back to the title attribute
- Scrapy-style ::attr()/::text pseudo-selectors from the LLM
- thousand separators vs decimal commas
"""

import pytest
from app.services.extraction_service import ExtractionService
from app.scrapers.html_parser import HTMLParser


HTML = """
<div class="list">
  <article class="item">
    <h3><a href="/books/1" title="A Light in the Attic">A Light in the ...</a></h3>
    <img src="/img/1.jpg" alt="Cover 1">
    <p class="price">$1,299.00</p>
  </article>
  <article class="item">
    <h3><a href="/books/2" title="Soumission">Soumission</a></h3>
    <img src="/img/2.jpg" alt="Cover 2">
    <p class="price">12,50 €</p>
  </article>
</div>
"""


@pytest.fixture
def service() -> ExtractionService:
    return ExtractionService(HTMLParser(HTML))


@pytest.mark.asyncio
async def test_string_field_on_link_returns_text_not_href(service):
    schema = {
        "fields": {"title": "string", "link": "url"},
        "container_selector": "article.item",
        "field_selectors": {"title": "h3 a", "link": "h3 a"},
    }
    records = await service.extract_data(schema=schema, max_records=10)
    assert records[0]["title"] == "A Light in the Attic"  # truncated text -> title attr
    assert records[1]["title"] == "Soumission"
    assert records[0]["link"].endswith("/books/1")


@pytest.mark.asyncio
async def test_url_field_on_wrapper_finds_inner_link(service):
    schema = {
        "fields": {"link": "url"},
        "container_selector": "article.item",
        "field_selectors": {"link": "h3"},
    }
    records = await service.extract_data(schema=schema, max_records=10)
    assert records[0]["link"].endswith("/books/1")


@pytest.mark.asyncio
async def test_scrapy_style_pseudo_selectors(service):
    schema = {
        "fields": {"link": "url", "cover": "url", "alt": "string", "title": "string"},
        "container_selector": "article.item",
        "field_selectors": {
            "link": "h3 a::attr(href)",
            "cover": "img::attr(src)",
            "alt": "img::attr(alt)",
            "title": "h3 a::text",
        },
    }
    records = await service.extract_data(schema=schema, max_records=10)
    assert records[0]["link"].endswith("/books/1")
    assert records[0]["cover"].endswith("/img/1.jpg")
    assert records[0]["alt"] == "Cover 1"
    assert records[1]["title"] == "Soumission"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1,299", 1299),
        ("$1,299.99", 1299.99),
        ("1.299,99 €", 1299.99),
        ("12,50", 12.5),
        ("1,000,000", 1000000),
        ("-3.5", -3.5),
    ],
)
def test_number_separators(service, raw, expected):
    assert service._extract_number(raw) == expected
