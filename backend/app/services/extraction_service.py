"""
Extraction Service - Apply LLM schemas to scraped data
Core logic for extracting structured data from HTML using LLM-generated schemas
"""

from typing import Dict, Any, List, Optional
from app.scrapers.html_parser import HTMLParser
from app.core.exceptions import ExtractionError
import logging
import re

logger = logging.getLogger(__name__)


class ExtractionService:
    """
    Service for extracting structured data from HTML using extraction schemas
    """
    
    def __init__(self, parser: HTMLParser):
        """
        Initialize extraction service
        
        Args:
            parser: HTMLParser instance with loaded HTML
        """
        self.parser = parser
    
    async def extract_data(
        self,
        schema: Dict[str, Any],
        max_records: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Extract structured data using schema
        
        Args:
            schema: Extraction schema from LLM
            {
                'fields': {'name': 'string', 'price': 'number', ...},
                'container_selector': '.product-card',
                'field_selectors': {'name': 'h3', 'price': '.price', ...},
                'filters': [optional filters]
            }
            max_records: Maximum number of records to extract
            
        Returns:
            List of extracted records
            
        Raises:
            ExtractionError: If extraction fails
        """
        logger.info("Starting data extraction with schema...")
        
        try:
            # Validate schema
            self._validate_schema(schema)
            
            # Get container selector
            container_selector = schema.get('container_selector', '')
            field_selectors = schema.get('field_selectors', {})
            field_types = schema.get('fields', {})
            
            # Extract containers
            containers = self.parser.extract_by_selector(container_selector)
            
            if not containers:
                logger.warning(f"No containers found with selector: {container_selector}")
                return []
            
            logger.info(f"Found {len(containers)} containers")
            
            # Extract data from each container
            records = []
            for idx, container in enumerate(containers[:max_records]):
                try:
                    record = self._extract_from_container(
                        container,
                        field_selectors,
                        field_types,
                    )
                    
                    # Apply filters if specified
                    if schema.get('filters'):
                        if not self._apply_filters(record, schema['filters']):
                            continue
                    
                    records.append(record)
                    
                except Exception as e:
                    logger.warning(f"Failed to extract from container {idx}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(records)} records")
            return records
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise ExtractionError(f"Data extraction failed: {str(e)}")
    
    def _validate_schema(self, schema: Dict[str, Any]):
        """
        Validate extraction schema
        
        Args:
            schema: Schema to validate
            
        Raises:
            ExtractionError: If schema is invalid
        """
        required_keys = ['fields', 'container_selector', 'field_selectors']
        
        for key in required_keys:
            if key not in schema:
                raise ExtractionError(f"Schema missing required key: {key}")
        
        if not schema['container_selector']:
            raise ExtractionError("Container selector cannot be empty")
        
        if not schema['fields']:
            raise ExtractionError("Fields cannot be empty")
    
    def _extract_from_container(
        self,
        container,
        field_selectors: Dict[str, str],
        field_types: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Extract data from a single container
        
        Args:
            container: BeautifulSoup element
            field_selectors: Field name to CSS selector mapping
            field_types: Field name to type mapping
            
        Returns:
            Extracted record
        """
        record = {}
        
        for field_name, field_type in field_types.items():
            selector = field_selectors.get(field_name, '')
            
            # Extract raw value
            raw_value = self._extract_field_value(container, selector)
            
            # Normalize value based on type
            normalized_value = self._normalize_value(raw_value, field_type)
            
            record[field_name] = normalized_value
        
        return record
    
    def _extract_field_value(self, container, selector: str) -> Optional[str]:
        """
        Extract field value from container using selector
        
        Args:
            container: BeautifulSoup element
            selector: CSS selector (relative to container)
            
        Returns:
            Extracted text or None
        """
        if not selector:
            # No selector, use container text
            return self.parser.get_text_from_element(container)
        
        try:
            # Find element within container
            element = container.select_one(selector)
            
            if not element:
                return None
            
            # Check for special attributes
            if element.name == 'a' and element.get('href'):
                return element['href']
            elif element.name == 'img' and element.get('src'):
                return element['src']
            elif element.get('content'):  # Meta tags
                return element['content']
            else:
                return self.parser.get_text_from_element(element)
                
        except Exception as e:
            logger.debug(f"Failed to extract field with selector '{selector}': {e}")
            return None
    
    def _normalize_value(self, value: Optional[str], field_type: str) -> Any:
        """
        Normalize extracted value based on field type
        
        Args:
            value: Raw extracted value
            field_type: Expected type (string, number, url, boolean, etc.)
            
        Returns:
            Normalized value
        """
        if value is None:
            return None
        
        field_type = field_type.lower()
        
        # String (default)
        if field_type == 'string' or field_type == 'text':
            return str(value).strip()
        
        # Number (int or float)
        elif field_type == 'number' or field_type == 'int' or field_type == 'float':
            return self._extract_number(value)
        
        # URL
        elif field_type == 'url' or field_type == 'link':
            return str(value).strip()
        
        # Boolean
        elif field_type == 'boolean' or field_type == 'bool':
            return self._extract_boolean(value)
        
        # Currency/Price
        elif field_type == 'price' or field_type == 'currency':
            return self._extract_number(value)
        
        # Default to string
        else:
            return str(value).strip()
    
    def _extract_number(self, value: str) -> Optional[float]:
        """
        Extract numeric value from string
        Handles currency symbols, commas, etc.
        
        Args:
            value: String potentially containing a number
            
        Returns:
            Extracted number or None
        """
        if not value:
            return None
        
        try:
            # Remove common non-numeric characters
            cleaned = re.sub(r'[^\d.,\-+]', '', str(value))
            
            # Handle comma as decimal separator (European format)
            if ',' in cleaned and '.' not in cleaned:
                cleaned = cleaned.replace(',', '.')
            else:
                # Remove thousand separators
                cleaned = cleaned.replace(',', '')
            
            # Convert to float
            number = float(cleaned)
            
            # Return int if it's a whole number
            if number.is_integer():
                return int(number)
            
            return number
            
        except (ValueError, AttributeError):
            logger.debug(f"Could not extract number from: {value}")
            return None
    
    def _extract_boolean(self, value: str) -> bool:
        """
        Extract boolean value from string
        
        Args:
            value: String to convert to boolean
            
        Returns:
            Boolean value
        """
        if not value:
            return False
        
        value_lower = str(value).lower().strip()
        
        # True values
        true_values = ['true', 'yes', '1', 'on', 'enabled', 'available']
        if value_lower in true_values:
            return True
        
        # False values
        false_values = ['false', 'no', '0', 'off', 'disabled', 'unavailable']
        if value_lower in false_values:
            return False
        
        # Default to True if value exists
        return bool(value_lower)
    
    def _apply_filters(
        self,
        record: Dict[str, Any],
        filters: List[Dict[str, Any]],
    ) -> bool:
        """
        Apply filters to determine if record should be included
        
        Args:
            record: Extracted record
            filters: List of filter conditions
            
        Returns:
            True if record passes all filters, False otherwise
        """
        for filter_condition in filters:
            field = filter_condition.get('field')
            operator = filter_condition.get('operator')
            value = filter_condition.get('value')
            
            if field not in record:
                continue
            
            record_value = record[field]
            
            # Skip if record value is None
            if record_value is None:
                return False
            
            # Apply operator
            if operator == '==' or operator == '=':
                if record_value != value:
                    return False
            elif operator == '!=' or operator == '<>':
                if record_value == value:
                    return False
            elif operator == '>':
                if not (record_value > value):
                    return False
            elif operator == '>=':
                if not (record_value >= value):
                    return False
            elif operator == '<':
                if not (record_value < value):
                    return False
            elif operator == '<=':
                if not (record_value <= value):
                    return False
            elif operator == 'contains':
                if str(value).lower() not in str(record_value).lower():
                    return False
        
        return True
