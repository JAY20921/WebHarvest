"""
DOM Analyzer - Token-Efficient HTML Summarization
Creates compressed representations of HTML for LLM consumption
"""

from typing import Dict, Any, List
from app.scrapers.html_parser import HTMLParser
import logging

logger = logging.getLogger(__name__)


class DOMAnalyzer:
    """
    Analyze HTML DOM and create token-efficient summaries for LLM
    """
    
    def __init__(self, html: str):
        """
        Initialize DOM analyzer
        
        Args:
            html: Raw HTML string
        """
        self.parser = HTMLParser(html)
    
    def create_summary(self, max_text_chars: int = 2000) -> Dict[str, Any]:
        """
        Create comprehensive but token-efficient page summary
        
        Args:
            max_text_chars: Maximum characters of visible text to include
            
        Returns:
            Dictionary with page summary suitable for LLM analysis
        """
        logger.info("Creating DOM summary for LLM analysis")
        
        # Get metadata
        metadata = self.parser.get_metadata()
        
        # Get structure
        structure = self.parser.get_structural_summary()
        
        # Get repeated patterns
        repeated_patterns = self.parser.find_repeated_elements(min_count=3)
        
        # Get visible text (truncated)
        visible_text = self.parser.get_visible_text()
        if len(visible_text) > max_text_chars:
            visible_text = visible_text[:max_text_chars] + "... [truncated]"
        
        # Get sample links (first 10)
        all_links = self.parser.get_links()
        sample_links = all_links[:10]
        
        # Create summary
        summary = {
            'metadata': {
                'title': metadata['title'],
                'description': metadata['description'],
                'og_type': metadata['og_tags'].get('type', ''),
            },
            'structure': structure,
            'repeated_patterns': repeated_patterns,
            'visible_text_preview': visible_text,
            'sample_links': sample_links,
            'stats': {
                'total_links': len(all_links),
                'has_json_ld': len(metadata['json_ld']) > 0,
                'estimated_tokens': self._estimate_tokens(visible_text),
            }
        }
        
        logger.info(
            f"Created summary: {structure['total_tags']} tags, "
            f"{len(repeated_patterns)} repeated patterns, "
            f"{summary['stats']['estimated_tokens']} estimated tokens"
        )
        
        return summary
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (1 token ≈ 4 characters)
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
    
    def create_llm_prompt_context(self) -> str:
        """
        Create human-readable context string for LLM prompts
        
        Returns:
            Formatted string describing the page structure
        """
        summary = self.create_summary()
        
        context_parts = []
        
        # Page info
        if summary['metadata']['title']:
            context_parts.append(f"Page Title: {summary['metadata']['title']}")
        
        if summary['metadata']['description']:
            context_parts.append(f"Description: {summary['metadata']['description']}")
        
        # Structure
        structure = summary['structure']
        context_parts.append(
            f"\nPage Structure: {structure['total_tags']} total elements"
        )
        
        headings = structure['headings']
        if sum(headings.values()) > 0:
            heading_str = ", ".join([f"{k}: {v}" for k, v in headings.items() if v > 0])
            context_parts.append(f"Headings: {heading_str}")
        
        if structure['lists'] > 0:
            context_parts.append(f"Lists: {structure['lists']}")
        
        if structure['tables'] > 0:
            context_parts.append(f"Tables: {structure['tables']}")
        
        # Repeated patterns
        if summary['repeated_patterns']:
            context_parts.append("\nRepeated Patterns (likely data containers):")
            for pattern in summary['repeated_patterns'][:5]:
                context_parts.append(f"  - {pattern['selector']}: {pattern['count']} occurrences")
        
        # Sample content
        context_parts.append(f"\nVisible Text Preview:\n{summary['visible_text_preview']}")
        
        return "\n".join(context_parts)
    
    def identify_data_containers(self) -> List[Dict[str, Any]]:
        """
        Identify likely containers for structured data
        
        Returns:
            List of container information with selectors and sample data
        """
        repeated = self.parser.find_repeated_elements(min_count=3)
        containers = []
        
        for pattern in repeated[:5]:  # Top 5 patterns
            selector = pattern['selector']
            elements = self.parser.extract_by_selector(selector)
            
            # Get sample data from first element
            if elements:
                first_elem = elements[0]
                sample_data = {
                    'text': self.parser.get_text_from_element(first_elem)[:200],
                    'has_links': len(first_elem.find_all('a')) > 0,
                    'has_images': len(first_elem.find_all('img')) > 0,
                    'class_names': ' '.join(first_elem.get('class', [])),
                }
                
                containers.append({
                    'selector': selector,
                    'count': pattern['count'],
                    'sample': sample_data,
                })
        
        return containers
