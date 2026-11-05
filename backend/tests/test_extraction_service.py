"""
Tests for Extraction Service
"""

import pytest
from app.services.extraction_service import ExtractionService
from app.scrapers.html_parser import HTMLParser


@pytest.fixture
def sample_html():
    """Sample HTML with product data"""
    return """
    <div class="products">
        <div class="product-card">
            <h3 class="name">Wireless Headphones</h3>
            <span class="price">$99.99</span>
            <div class="rating">4.5</div>
            <a href="/product1" class="link">View</a>
        </div>
        <div class="product-card">
            <h3 class="name">Bluetooth Speaker</h3>
            <span class="price">$149.99</span>
            <div class="rating">4.8</div>
            <a href="/product2" class="link">View</a>
        </div>
        <div class="product-card">
            <h3 class="name">USB Cable</h3>
            <span class="price">$9.99</span>
            <div class="rating">4.2</div>
            <a href="/product3" class="link">View</a>
        </div>
    </div>
    """


@pytest.fixture
def extraction_schema():
    """Sample extraction schema"""
    return {
        'fields': {
            'name': 'string',
            'price': 'number',
            'rating': 'number',
            'url': 'url',
        },
        'container_selector': '.product-card',
        'field_selectors': {
            'name': '.name',
            'price': '.price',
            'rating': '.rating',
            'url': '.link',
        },
    }


@pytest.mark.asyncio
class TestExtractionService:
    """Test extraction service functionality"""
    
    async def test_extract_data_success(self, sample_html, extraction_schema):
        """Test successful data extraction"""
        parser = HTMLParser(sample_html)
        service = ExtractionService(parser)
        
        records = await service.extract_data(extraction_schema)
        
        assert len(records) == 3
        assert records[0]['name'] == "Wireless Headphones"
        assert records[0]['price'] == 99.99
        assert records[0]['rating'] == 4.5
        assert records[0]['url'] == "/product1"
    
    async def test_extract_data_with_filters(self, sample_html):
        """Test extraction with filters"""
        schema_with_filters = {
            'fields': {
                'name': 'string',
                'price': 'number',
            },
            'container_selector': '.product-card',
            'field_selectors': {
                'name': '.name',
                'price': '.price',
            },
            'filters': [
                {
                    'field': 'price',
                    'operator': '<',
                    'value': 100,
                }
            ],
        }
        
        parser = HTMLParser(sample_html)
        service = ExtractionService(parser)
        
        records = await service.extract_data(schema_with_filters)
        
        # Should only get products under $100
        assert len(records) == 2  # Headphones ($99.99) and Cable ($9.99)
        assert all(r['price'] < 100 for r in records)
    
    async def test_number_extraction(self, sample_html):
        """Test number extraction from strings"""
        parser = HTMLParser(sample_html)
        service = ExtractionService(parser)
        
        # Test various number formats
        assert service._extract_number("$99.99") == 99.99
        assert service._extract_number("1,299") == 1299
        assert service._extract_number("Price: ₹1,499.50") == 1499.50
        assert service._extract_number("42") == 42
        assert service._extract_number("Not a number") is None
    
    async def test_missing_fields(self, sample_html):
        """Test handling of missing fields"""
        schema = {
            'fields': {
                'name': 'string',
                'nonexistent': 'string',
            },
            'container_selector': '.product-card',
            'field_selectors': {
                'name': '.name',
                'nonexistent': '.does-not-exist',
            },
        }
        
        parser = HTMLParser(sample_html)
        service = ExtractionService(parser)
        
        records = await service.extract_data(schema)
        
        assert len(records) == 3
        assert records[0]['name'] == "Wireless Headphones"
        assert records[0]['nonexistent'] is None  # Missing field


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
