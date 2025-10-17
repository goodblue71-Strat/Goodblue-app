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
Notes: {notes or ""}

TASK: Generate a detailed SWOT analysis with introduction and key takeaway.

Constraints:
- Return **ONLY** valid JSON. No commentary, no code fences.
- Include these top-level keys: "introduction", "S", "W", "O", "T", "key_takeaway"
- "introduction": Exactly 15-20 words providing context for this specific analysis
- Each of S, W, O, T must have **5–8 bullets**.
- Each bullet 8–18 words, **specific** (no vague boilerplate like "industry leading").
- Reflect the local context of **{geo or "the target market"}** and trends in **{industry}**.
- Cover these capabilities across the set of bullets (spread them; no need to label each):
  {", ".join(CAPABILITY_AREAS)}.
- "key_takeaway": Exactly 25-30 words with actionable strategic insight based on the SWOT findings
- Avoid duplicates; no trailing commas.

Output schema (must match exactly):
{{
  "introduction": "...",
  "S": ["...", "..."],
  "W": ["...", "..."],
  "O": ["...", "..."],
  "T": ["...", "..."],
  "key_takeaway": "..."
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
        "introduction": "Strategic analysis of competitive position and market opportunities for sustainable growth.",
        "S": [
            "Clear value proposition",
            "Growing customer base",
            "Experienced leadership",
            "Strong partner interest",
        ],
        "W": [
            "Limited brand awareness",
            "Thin mid-market coverage",
            "Inconsistent messaging",
        ],
        "O": [
            "Upsell existing accounts",
            "New geography pilots",
            "Alliances with integrators",
        ],
        "T": [
            "Price pressure from low-cost rivals",
            "Long sales cycles",
            "Security/compliance scrutiny",
        ],
        "key_takeaway": "Focus on leveraging strong partnerships while addressing brand gaps. Prioritize customer retention and explore geographic expansion to offset competitive pressures.",
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
    """Generate SWOT analysis with introduction and key takeaway using the provided generator.
    
    Args:
        generator: StrategyGenerator instance with LLM provider
        company: Company name
        industry: Industry name
        product: Product name
        product_feature: Specific product feature
        notes: Optional additional context
        geo: Optional geography
        max_items: Maximum items per SWOT category (default 8)
    
    Returns:
        Dictionary with keys: introduction, S, W, O, T, key_takeaway
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
            max_tokens=1500
        )
        
        # Extract and validate SWOT data
        introduction = result.get("introduction", "")
        S = coerce_list(result.get("S"))
        W = coerce_list(result.get("W"))
        O = coerce_list(result.get("O"))
        T = coerce_list(result.get("T"))
        key_takeaway = result.get("key_takeaway", "")
        
        # Return if we got valid data
        if any([S, W, O, T]):
            return {
                "introduction": introduction if introduction else "Strategic analysis of current position and future opportunities.",
                "S": topn(S, max_items),
                "W": topn(W, max_items),
                "O": topn(O, max_items),
                "T": topn(T, max_items),
                "key_takeaway": key_takeaway if key_takeaway else "Focus on building strengths while addressing weaknesses to capitalize on opportunities.",
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
    required_keys = {"introduction", "S", "W", "O", "T", "key_takeaway"}
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
