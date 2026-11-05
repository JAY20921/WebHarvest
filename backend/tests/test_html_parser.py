"""
Tests for HTML Parser
"""

import pytest
from app.scrapers.html_parser import HTMLParser


@pytest.fixture
def sample_html():
    """Sample HTML for testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="This is a test page">
        <meta property="og:title" content="OG Test Title">
        <meta property="og:type" content="website">
    </head>
    <body>
        <h1>Main Heading</h1>
        <div class="product-card">
            <h3>Product 1</h3>
            <span class="price">$99.99</span>
            <a href="/product1">View</a>
        </div>
        <div class="product-card">
            <h3>Product 2</h3>
            <span class="price">$149.99</span>
            <a href="/product2">View</a>
        </div>
        <div class="product-card">
            <h3>Product 3</h3>
            <span class="price">$199.99</span>
            <a href="/product3">View</a>
        </div>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <script>console.log('test');</script>
        <style>.test { color: red; }</style>
    </body>
    </html>
    """


class TestHTMLParser:
    """Test HTML parser functionality"""
    
    def test_get_title(self, sample_html):
        """Test title extraction"""
        parser = HTMLParser(sample_html)
        assert parser.get_title() == "Test Page"
    
    def test_get_meta_description(self, sample_html):
        """Test meta description extraction"""
        parser = HTMLParser(sample_html)
        assert parser.get_meta_description() == "This is a test page"
    
    def test_get_metadata(self, sample_html):
        """Test metadata extraction"""
        parser = HTMLParser(sample_html)
        metadata = parser.get_metadata()
        
        assert metadata['title'] == "Test Page"
        assert metadata['description'] == "This is a test page"
        assert metadata['og_tags']['title'] == "OG Test Title"
        assert metadata['og_tags']['type'] == "website"
    
    def test_get_visible_text(self, sample_html):
        """Test visible text extraction (no scripts/styles)"""
        parser = HTMLParser(sample_html)
        text = parser.get_visible_text()
        
        assert "Main Heading" in text
        assert "Product 1" in text
        assert "console.log" not in text  # Script removed
        assert ".test {" not in text  # Style removed
    
    def test_get_links(self, sample_html):
        """Test link extraction"""
        parser = HTMLParser(sample_html)
        links = parser.get_links()
        
        assert len(links) == 3
        assert links[0]['href'] == "/product1"
        assert links[0]['text'] == "View"
    
    def test_find_repeated_elements(self, sample_html):
        """Test repeated element detection"""
        parser = HTMLParser(sample_html)
        repeated = parser.find_repeated_elements(min_count=3)
        
        assert len(repeated) > 0
        # Should find div.product-card repeated 3 times
        product_cards = [r for r in repeated if 'product-card' in r['selector']]
        assert len(product_cards) > 0
        assert product_cards[0]['count'] == 3
    
    def test_get_structural_summary(self, sample_html):
        """Test structural summary"""
        parser = HTMLParser(sample_html)
        summary = parser.get_structural_summary()
        
        assert summary['headings']['h1'] == 1
        assert summary['headings']['h3'] == 3
        assert summary['lists'] == 1
        assert summary['links'] == 3
    
    def test_extract_by_selector(self, sample_html):
        """Test CSS selector extraction"""
        parser = HTMLParser(sample_html)
        products = parser.extract_by_selector('.product-card')
        
        assert len(products) == 3
        assert products[0].find('h3').get_text() == "Product 1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
