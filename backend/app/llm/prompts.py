"""
LLM Prompt Templates
Centralized location for all prompt engineering
"""


EXTRACTION_SCHEMA_SYSTEM_PROMPT = """You are an expert web scraping assistant. Your job is to understand what data the user wants to extract from a webpage and generate a structured extraction schema.

Given:
1. User's natural language extraction request
2. Page structure summary (metadata, repeated patterns, content)

Generate a JSON extraction schema with:
- fields: Dictionary of field names and their data types (string, number, url, etc.)
- container_selector: CSS selector for repeated elements (e.g., product cards)
- field_selectors: CSS selectors for each field within the container
- filters: Optional conditions for filtering results

Be smart about:
- Identifying the right repeated pattern (product cards, articles, listings)
- Mapping user's request to actual page elements
- Inferring field types from context
- Using relative selectors within containers

Output ONLY valid JSON, no explanations."""


EXTRACTION_SCHEMA_USER_TEMPLATE = """Page Structure:
{page_context}

User Request: "{user_prompt}"

Generate an extraction schema that fulfills this request. Consider:
1. Which repeated pattern contains the data?
2. What CSS selectors extract each requested field?
3. What are the field data types?

Output JSON schema:
{{
  "fields": {{"field_name": "type", ...}},
  "container_selector": ".repeated-element",
  "field_selectors": {{"field_name": ".selector", ...}}
}}"""


PAGE_STRUCTURE_ANALYSIS_SYSTEM_PROMPT = """You are a web page structure analyzer. Analyze the provided page summary and identify:
1. Main content type (e-commerce, blog, directory, etc.)
2. Repeated data patterns (products, articles, listings)
3. Data extraction opportunities
4. Recommended extraction strategy

Be concise and focus on actionable insights."""


PAGE_STRUCTURE_ANALYSIS_USER_TEMPLATE = """Analyze this page structure:

{page_context}

Provide:
1. Page type
2. Identified data patterns
3. Extraction strategy

Output as JSON:
{{
  "page_type": "...",
  "data_patterns": [...],
  "strategy": "..."
}}"""


def create_extraction_schema_prompt(
    user_prompt: str,
    page_context: str,
) -> tuple[str, str]:
    """
    Create prompt for extraction schema generation
    
    Args:
        user_prompt: User's extraction instruction
        page_context: Page summary from DOM analyzer
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = EXTRACTION_SCHEMA_SYSTEM_PROMPT
    user = EXTRACTION_SCHEMA_USER_TEMPLATE.format(
        page_context=page_context,
        user_prompt=user_prompt,
    )
    return system, user


def create_structure_analysis_prompt(
    page_context: str,
) -> tuple[str, str]:
    """
    Create prompt for page structure analysis
    
    Args:
        page_context: Page summary from DOM analyzer
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = PAGE_STRUCTURE_ANALYSIS_SYSTEM_PROMPT
    user = PAGE_STRUCTURE_ANALYSIS_USER_TEMPLATE.format(
        page_context=page_context,
    )
    return system, user
