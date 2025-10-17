"""
SWOT-specific prompts and generation logic for GoodBlue Strategy App.

Usage:
    from generator import StrategyGenerator, OpenAIProvider
    from swot_prompts import generate_swot, SWOT_SYSTEM_PROMPT
    
    provider = OpenAIProvider(model="gpt-4o-mini")
    gen = StrategyGenerator(provider)
    
    swot = generate_swot(
        gen,
        company="ACME Corp",
        industry="Manufacturing",
        product="IoT Sensors",
        product_feature="Predictive maintenance"
    )
"""
from __future__ import annotations

from typing import Dict, List, Optional, Any
from generator import StrategyGenerator, coerce_list, topn, DEFAULT_SYSTEM_PROMPT

# ---------------------- SWOT Configuration ----------------------

SWOT_SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT

# Capability areas to ensure comprehensive SWOT coverage
CAPABILITY_AREAS = [
    "Brand strength",
    "Distribution/Channels",
    "Pricing/Packaging",
    "Integrations/Partner ecosystem",
    "Security/Compliance",
    "Analytics/AI",
    "Implementation complexity",
    "Support/Success"
]

# ---------------------- Prompts ----------------------

def _swot_prompt(
    company: str,
    industry: str,
    product: str,
    product_feature: str,
    notes: Optional[str] = None,
    geo: Optional[str] = None
) -> str:
    """Build the user prompt for SWOT generation."""
    return f"""
Company: {company}
Industry: {industry}
Product: {product}
Product Feature: {product_feature}
Geography: {geo or "unspecified"}
Additional Prompts: {notes or "None"}

TASK: Generate a detailed SWOT analysis with introduction, key takeaway, and priority matrix.

Constraints:
- Return **ONLY** valid JSON. No commentary, no code fences.
- Include these top-level keys: "introduction", "S", "W", "O", "T", "key_takeaway", "matrix_introduction", "matrix_takeaway"
- "introduction": Exactly 15-20 words that combines company, product, industry, geography, and product feature into a cohesive statement
- Each of S, W, O, T must have **5–8 items**.
- Each item must be an object with:
  - "text": 8–18 words, **specific** (no vague boilerplate)
  - "impact": score 1-10 (how much this affects business outcomes)
  - "control": score 1-10 (how much control the company has over this)
- Consider the Additional Prompts while deriving the SWOT
- Reflect the local context of **{geo or "the target market"}** and trends in **{industry}**.
- Cover these capabilities across items: {", ".join(CAPABILITY_AREAS)}.
- "key_takeaway": Exactly 25-30 words with actionable strategic insight based on the SWOT findings
- "matrix_introduction": Exactly 15-20 words introducing the priority matrix based on impact and control
- "matrix_takeaway": Exactly 25-30 words with insights from the priority matrix
- Avoid duplicates; no trailing commas.

Output schema (must match exactly):
{{
  "introduction": "...",
  "S": [
    {{"text": "...", "impact": 8, "control": 9}},
    {{"text": "...", "impact": 7, "control": 8}}
  ],
  "W": [
    {{"text": "...", "impact": 6, "control": 7}},
    {{"text": "...", "impact": 5, "control": 6}}
  ],
  "O": [
    {{"text": "...", "impact": 9, "control": 5}},
    {{"text": "...", "impact": 8, "control": 6}}
  ],
  "T": [
    {{"text": "...", "impact": 7, "control": 3}},
    {{"text": "...", "impact": 6, "control": 4}}
  ],
  "key_takeaway": "...",
  "matrix_introduction": "...",
  "matrix_takeaway": "..."
}}
""".strip()

def build_swot_prompt(
    company: str,
    industry: str,
    product: str,
    product_feature: str,
    notes: Optional[str] = None,
    geo: Optional[str] = None
) -> str:
    """Build the user prompt for SWOT generation with introduction and takeaway."""
    return _swot_prompt(company, industry, product, product_feature, notes, geo)

# ---------------------- Fallback Data ----------------------

def get_fallback_swot() -> Dict[str, Any]:
    """Return fallback SWOT data when LLM is unavailable."""
    return {
        "introduction": "Analysis of industrial IoT sensors for manufacturing operations with focus on predictive maintenance capabilities.",
        "S": [
            {"text": "Clear value proposition", "impact": 8, "control": 9},
            {"text": "Growing customer base", "impact": 7, "control": 8},
            {"text": "Experienced leadership", "impact": 6, "control": 9},
            {"text": "Strong partner interest", "impact": 7, "control": 7},
        ],
        "W": [
            {"text": "Limited brand awareness", "impact": 6, "control": 7},
            {"text": "Thin mid-market coverage", "impact": 5, "control": 8},
            {"text": "Inconsistent messaging", "impact": 4, "control": 9},
        ],
        "O": [
            {"text": "Upsell existing accounts", "impact": 8, "control": 7},
            {"text": "New geography pilots", "impact": 7, "control": 5},
            {"text": "Alliances with integrators", "impact": 8, "control": 6},
        ],
        "T": [
            {"text": "Price pressure from low-cost rivals", "impact": 7, "control": 3},
            {"text": "Long sales cycles", "impact": 6, "control": 4},
            {"text": "Security/compliance scrutiny", "impact": 8, "control": 5},
        ],
        "key_takeaway": "Focus on leveraging strong partnerships while addressing brand gaps. Prioritize customer retention and explore geographic expansion to offset competitive pressures.",
        "matrix_introduction": "Priority matrix shows control versus impact, identifying high-priority items requiring immediate strategic attention and resource allocation.",
        "matrix_takeaway": "High control items should be leveraged immediately while low control threats need mitigation strategies. Focus resources on high-impact, high-control opportunities first.",
    }

# ---------------------- Generation Function ----------------------

def generate_swot(
    generator: StrategyGenerator,
    company: str,
    industry: str,
    product: str,
    product_feature: str,
    *,
    notes: Optional[str] = None,
    geo: Optional[str] = None,
    max_items: int = 8
) -> Dict[str, Any]:
    """Generate SWOT analysis with introduction, key takeaway, and priority matrix using the provided generator.
    
    Args:
        generator: StrategyGenerator instance with LLM provider
        company: Company name
        industry: Industry name
        product: Product name
        product_feature: Specific product feature
        notes: Optional additional prompts
        geo: Optional geography
        max_items: Maximum items per SWOT category (default 8)
    
    Returns:
        Dictionary with keys: introduction, S, W, O, T, key_takeaway, matrix_introduction, matrix_takeaway
    """
    if not generator.is_available():
        return get_fallback_swot()
    
    try:
        user_prompt = build_swot_prompt(
            company, industry, product, product_feature, notes, geo
        )
        
        result = generator.generate_json(
            SWOT_SYSTEM_PROMPT,
            user_prompt,
            temperature=0.2,
            max_tokens=2000
        )
        
        # Extract and validate SWOT data
        introduction = result.get("introduction", "")
        
        # Process S, W, O, T - handle both old format (strings) and new format (objects)
        def process_items(items):
            processed = []
            if not items:
                return []
            for item in items:
                if isinstance(item, dict):
                    processed.append({
                        "text": item.get("text", ""),
                        "impact": item.get("impact", 5),
                        "control": item.get("control", 5)
                    })
                elif isinstance(item, str):
                    # Fallback for old format
                    processed.append({
                        "text": item,
                        "impact": 5,
                        "control": 5
                    })
            return processed[:max_items]
        
        S = process_items(result.get("S"))
        W = process_items(result.get("W"))
        O = process_items(result.get("O"))
        T = process_items(result.get("T"))
        
        key_takeaway = result.get("key_takeaway", "")
        matrix_introduction = result.get("matrix_introduction", "")
        matrix_takeaway = result.get("matrix_takeaway", "")
        
        # Return if we got valid data
        if any([S, W, O, T]):
            return {
                "introduction": introduction if introduction else f"Strategic analysis for {company}'s {product} in {industry}.",
                "S": S,
                "W": W,
                "O": O,
                "T": T,
                "key_takeaway": key_takeaway if key_takeaway else "Focus on building strengths while addressing weaknesses to capitalize on opportunities.",
                "matrix_introduction": matrix_introduction if matrix_introduction else "Priority matrix based on impact and control to guide strategic resource allocation.",
                "matrix_takeaway": matrix_takeaway if matrix_takeaway else "Prioritize high-impact, high-control items for immediate action while developing strategies for lower-control factors.",
            }
    except Exception as e:
        print(f"SWOT generation error: {e}")
    
    # Fallback if generation fails
    return get_fallback_swot()

# ---------------------- Validation ----------------------

def validate_swot(swot: Dict[str, Any]) -> bool:
    """Validate SWOT structure and content.
    
    Returns True if SWOT has all required keys and non-empty lists.
    """
    required_keys = {"introduction", "S", "W", "O", "T", "key_takeaway", "matrix_introduction", "matrix_takeaway"}
    if not all(key in swot for key in required_keys):
        return False
    list_keys = {"S", "W", "O", "T"}
    return all(isinstance(swot[key], list) and len(swot[key]) > 0 for key in list_keys)

# ---------------------- Quick self-test ----------------------
if __name__ == "__main__":
    import json
    
    # Test without provider (should return fallback)
    gen = StrategyGenerator(provider=None)
    swot = generate_swot(
        gen,
        company="ACME Robotics",
        industry="Manufacturing",
        product="Industrial IoT Sensors",
        product_feature="Identifying bearing failure",
        notes="Mid-market focus",
        geo="US"
    )
    print("Fallback SWOT:")
    print(json.dumps(swot, indent=2))
    print(f"\nValid: {validate_swot(swot)}")
