"""
HTML Parser and Content Extractor
Uses BeautifulSoup for parsing and extracting relevant content
"""

from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)


class HTMLParser:
    """
    Parse HTML and extract structured information
    """
    
    def __init__(self, html: str):
        """
        Initialize parser with HTML content
        
        Args:
            html: Raw HTML string
        """
        self.html = html
        self.soup = BeautifulSoup(html, 'lxml')
    
    def get_title(self) -> str:
        """Extract page title"""
        title_tag = self.soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""
    
    def get_meta_description(self) -> str:
        """Extract meta description"""
        meta = self.soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '') if meta else ""
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Extract various metadata from HTML
        
        Returns:
            Dictionary with metadata
        """
        metadata = {
            'title': self.get_title(),
            'description': self.get_meta_description(),
            'og_tags': {},
            'json_ld': [],
        }
        
        # Open Graph tags
        og_tags = self.soup.find_all('meta', property=re.compile(r'^og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if prop and content:
                metadata['og_tags'][prop] = content
        
        # JSON-LD structured data
        json_ld_scripts = self.soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            if script.string:
                metadata['json_ld'].append(script.string.strip())
        
        return metadata
    
    def get_visible_text(self) -> str:
        """
        Extract all visible text from page
        Filters out scripts, styles, and other non-content tags
        
        Returns:
            Clean visible text
        """
        # Remove unwanted tags
        for tag in self.soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()
        
        # Get text
        text = self.soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def get_links(self) -> List[Dict[str, str]]:
        """
        Extract all links from page
        
        Returns:
            List of dictionaries with href, text, and title
        """
        links = []
        for a_tag in self.soup.find_all('a', href=True):
            links.append({
                'href': a_tag['href'],
                'text': a_tag.get_text(strip=True),
                'title': a_tag.get('title', ''),
            })
        return links
    
    def get_images(self) -> List[Dict[str, str]]:
        """
        Extract all images from page
        
        Returns:
            List of dictionaries with src, alt, and title
        """
        images = []
        for img_tag in self.soup.find_all('img', src=True):
            images.append({
                'src': img_tag['src'],
                'alt': img_tag.get('alt', ''),
                'title': img_tag.get('title', ''),
            })
        return images
    
    def find_repeated_elements(self, min_count: int = 3) -> List[Dict[str, Any]]:
        """
        Find repeated HTML patterns (like product cards, article previews)
        
        Args:
            min_count: Minimum number of repetitions to consider
            
        Returns:
            List of repeated element patterns with CSS selectors
        """
        # Count elements by class combinations
        class_counter = Counter()
        
        for tag in self.soup.find_all(True):  # All tags
            if tag.get('class'):
                classes = ' '.join(sorted(tag['class']))
                if classes:
                    class_counter[f"{tag.name}.{classes.replace(' ', '.')}"] += 1
        
        # Find patterns that repeat at least min_count times
        repeated = []
        for selector, count in class_counter.items():
            if count >= min_count:
                repeated.append({
                    'selector': selector,
                    'count': count,
                })
        
        # Sort by count (most repeated first)
        repeated.sort(key=lambda x: x['count'], reverse=True)
        
        return repeated[:10]  # Top 10 patterns
    
    def get_structural_summary(self) -> Dict[str, Any]:
        """
        Get high-level structure of the page
        
        Returns:
            Dictionary with page structure information
        """
        return {
            'total_tags': len(self.soup.find_all(True)),
            'headings': {
                'h1': len(self.soup.find_all('h1')),
                'h2': len(self.soup.find_all('h2')),
                'h3': len(self.soup.find_all('h3')),
            },
            'lists': len(self.soup.find_all(['ul', 'ol'])),
            'tables': len(self.soup.find_all('table')),
            'forms': len(self.soup.find_all('form')),
            'divs': len(self.soup.find_all('div')),
            'links': len(self.soup.find_all('a')),
            'images': len(self.soup.find_all('img')),
        }
    
    def extract_by_selector(self, selector: str) -> List[Tag]:
        """
        Extract elements by CSS selector
        
        Args:
            selector: CSS selector string
            
        Returns:
            List of matching BeautifulSoup Tag objects
        """
        try:
            return self.soup.select(selector)
        except Exception as e:
            logger.error(f"Error selecting with '{selector}': {e}")
            return []
    
    def get_text_from_element(self, element: Tag) -> str:
        """
        Get clean text from an element
        
        Args:
            element: BeautifulSoup Tag
            
        Returns:
            Clean text content
        """
        if isinstance(element, Tag):
            return element.get_text(strip=True)
        return ""
    
    def element_to_dict(self, element: Tag, fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Convert an element to dictionary based on field mapping
        
        Args:
            element: BeautifulSoup Tag
            fields: Dictionary mapping field names to CSS selectors
            
        Returns:
            Dictionary with extracted data
        """
        if not fields:
            # Default: extract all text
            return {'text': self.get_text_from_element(element)}
        
        result = {}
        for field_name, field_selector in fields.items():
            try:
                # Find within this element
                if field_selector:
                    found = element.select_one(field_selector)
                    if found:
                        # Check for common attributes
                        if found.name == 'a' and found.get('href'):
                            result[field_name] = found['href']
                        elif found.name == 'img' and found.get('src'):
                            result[field_name] = found['src']
                        else:
                            result[field_name] = self.get_text_from_element(found)
                    else:
                        result[field_name] = None
                else:
                    # Use element itself
                    result[field_name] = self.get_text_from_element(element)
            except Exception as e:
                logger.warning(f"Error extracting field '{field_name}': {e}")
                result[field_name] = None
        
        return result
