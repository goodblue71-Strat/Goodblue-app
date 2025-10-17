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

TASK: Generate a detailed SWOT analysis with introduction, key takeaway, priority matrix, and strategic roadmap.

Constraints:
- Return **ONLY** valid JSON. No commentary, no code fences.
- Include these top-level keys: "introduction", "S", "W", "O", "T", "key_takeaway", "matrix_introduction", "matrix_takeaway", "roadmap_introduction", "roadmap_takeaway", "roadmap"
- "introduction": Exactly 15-20 words that combines company, product, industry, geography, and product feature into a cohesive statement
- Each of S, W, O, T must have **5–8 items**.
- Each item must be an object with:
  - "text": 8–18 words, **specific** (no vague boilerplate)
  - "impact": score 1-10 (impact on business success)
  - "control": score 1-10 (company's ability to influence this factor)
  - "priority": "high" or "medium" or "low" (based on impact and control: high=both>5, medium=impact>5 and control<=5, low=otherwise)
  - "solution": 10-15 words describing a brief, actionable solution (only for high and medium priority items)
- IMPORTANT: Vary the impact and control scores to spread items across the matrix (avoid clustering around same values)
- Consider the Additional Prompts while deriving the SWOT
- Reflect the local context of **{geo or "the target market"}** and trends in **{industry}**.
- Cover these capabilities across items: {", ".join(CAPABILITY_AREAS)}.
- "key_takeaway": Exactly 25-30 words with actionable strategic insight based on the SWOT findings
- "matrix_introduction": Exactly 15-20 words introducing the priority matrix using "Impact on Success" vs "Ability to Influence"
- "matrix_takeaway": Exactly 35-45 words with SPECIFIC, CONTEXTUAL insights about {company}'s {product} strategy. Reference actual high-priority items and suggest concrete actions based on their position in the matrix.
- "priority_table_introduction": Exactly 20-25 words introducing the priority table and how items are ranked
- "priority_table_takeaway": Exactly 25-35 words summarizing the key actions from the priority table
- "roadmap_introduction": Exactly 20-25 words introducing the strategic roadmap and how it sequences actions over time
- "roadmap_takeaway": Exactly 30-40 words summarizing the roadmap's focus, sequencing logic, and expected outcomes for {company}
- "roadmap": object with three keys:
  - "short_term": array of 2-3 items with {{"item_ref": "S1", "solution": "detailed 20-25 word solution"}}
  - "near_term": array of 2-3 items with {{"item_ref": "O1", "solution": "detailed 20-25 word solution"}}
  - "long_term": array of 2-3 items with {{"item_ref": "O2", "solution": "detailed 20-25 word solution"}}
- Avoid duplicates; no trailing commas.

Output schema (must match exactly):
{{
  "introduction": "...",
  "S": [
    {{"text": "...", "impact": 8, "control": 9, "priority": "high", "solution": "..."}},
    {{"text": "...", "impact": 7, "control": 8, "priority": "high", "solution": "..."}}
  ],
  "W": [
    {{"text": "...", "impact": 6, "control": 7, "priority": "medium", "solution": "..."}},
    {{"text": "...", "impact": 5, "control": 6, "priority": "medium", "solution": "..."}}
  ],
  "O": [
    {{"text": "...", "impact": 9, "control": 5, "priority": "medium", "solution": "..."}},
    {{"text": "...", "impact": 8, "control": 6, "priority": "medium", "solution": "..."}}
  ],
  "T": [
    {{"text": "...", "impact": 7, "control": 3, "priority": "medium", "solution": "..."}},
    {{"text": "...", "impact": 6, "control": 4, "priority": "low"}}
  ],
  "key_takeaway": "...",
  "matrix_introduction": "...",
  "matrix_takeaway": "...",
  "roadmap_introduction": "...",
  "roadmap_takeaway": "...",
  "roadmap": {{
    "short_term": [
      {{"item_ref": "S1", "action": "Launch targeted campaign leveraging this strength"}},
      {{"item_ref": "W1", "action": "Implement immediate fix for this weakness"}}
    ],
    "near_term": [
      {{"item_ref": "O1", "action": "Pilot program to capture this opportunity"}},
      {{"item_ref": "S2", "action": "Scale this strength across regions"}}
    ],
    "long_term": [
      {{"item_ref": "O2", "action": "Strategic partnership to realize this opportunity"}},
      {{"item_ref": "T1", "action": "Build capabilities to mitigate this threat"}}
    ]
  }}
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
            {"text": "Clear value proposition", "impact": 8, "control": 9, "priority": "high", "solution": "Launch case studies showcasing ROI to amplify market position"},
            {"text": "Growing customer base", "impact": 7, "control": 8, "priority": "high", "solution": "Implement customer success program to maximize retention and expansion"},
            {"text": "Experienced leadership", "impact": 6, "control": 9, "priority": "high", "solution": "Leverage leadership expertise for strategic partnerships and thought leadership"},
            {"text": "Strong partner interest", "impact": 7, "control": 7, "priority": "high", "solution": "Formalize partner program with clear incentives and co-marketing"},
        ],
        "W": [
            {"text": "Limited brand awareness", "impact": 6, "control": 7, "priority": "medium", "solution": "Execute targeted digital marketing campaign in key manufacturing verticals"},
            {"text": "Thin mid-market coverage", "impact": 5, "control": 8, "priority": "medium", "solution": "Develop mid-market specific packaging and partner channel strategy"},
            {"text": "Inconsistent messaging", "impact": 4, "control": 9, "priority": "low"},
        ],
        "O": [
            {"text": "Upsell existing accounts", "impact": 8, "control": 7, "priority": "high", "solution": "Create tiered product bundles for cross-sell into installed base"},
            {"text": "New geography pilots", "impact": 7, "control": 5, "priority": "medium", "solution": "Partner with local distributors for APAC market entry pilot"},
            {"text": "Alliances with integrators", "impact": 8, "control": 6, "priority": "medium", "solution": "Establish co-sell agreements with top three system integrators"},
        ],
        "T": [
            {"text": "Price pressure from low-cost rivals", "impact": 7, "control": 3, "priority": "medium", "solution": "Differentiate on total cost of ownership and premium support"},
            {"text": "Long sales cycles", "impact": 6, "control": 4, "priority": "low"},
            {"text": "Security/compliance scrutiny", "impact": 8, "control": 5, "priority": "medium", "solution": "Obtain SOC 2 certification and publish security whitepaper"},
        ],
        "key_takeaway": "Focus on leveraging strong partnerships while addressing brand gaps. Prioritize customer retention and explore geographic expansion to offset competitive pressures.",
        "matrix_introduction": "Priority matrix maps impact on success versus ability to influence, revealing strategic action priorities.",
        "matrix_takeaway": "Leverage high-control strengths like experienced leadership immediately. Address brand awareness gaps within your control. Partner strategically for low-control opportunities like new geographies. Monitor and prepare contingency plans for low-control threats.",
        "roadmap_introduction": "Strategic roadmap prioritizes actions across three time horizons to maximize impact and build sustainable competitive advantage.",
        "roadmap_takeaway": "Focus next quarter on high-ROI customer initiatives. This year, expand market presence and strengthen partnerships. Long-term, build infrastructure for scale and compliance readiness.",
        "roadmap": {
            "short_term": [
                {"item_ref": "S1", "action": "Launch case studies and ROI calculators to strengthen value proposition messaging"},
                {"item_ref": "S2", "action": "Roll out customer success program to drive retention and expansion"}
            ],
            "near_term": [
                {"item_ref": "O1", "action": "Develop and pilot upsell bundles with existing enterprise accounts"},
                {"item_ref": "W1", "action": "Execute digital marketing campaign targeting manufacturing decision makers"}
            ],
            "long_term": [
                {"item_ref": "O2", "action": "Establish APAC presence through distributor partnerships and local support"},
                {"item_ref": "T3", "action": "Complete SOC 2 certification and build compliance framework"}
            ]
        }
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
                        "control": item.get("control", 5),
                        "priority": item.get("priority", "low"),
                        "solution": item.get("solution", "")
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
        roadmap_introduction = result.get("roadmap_introduction", "")
        roadmap_takeaway = result.get("roadmap_takeaway", "")
        roadmap = result.get("roadmap", {
            "short_term": [],
            "near_term": [],
            "long_term": []
        })
        
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
                "roadmap_introduction": roadmap_introduction if roadmap_introduction else "Strategic roadmap outlines phased approach to address priorities across time horizons.",
                "roadmap_takeaway": roadmap_takeaway if roadmap_takeaway else "Execute quick wins now, build capabilities this year, and establish strategic positioning for long-term success.",
                "roadmap": roadmap if roadmap else {
                    "short_term": [],
                    "near_term": [],
                    "long_term": []
                }
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
    required_keys = {"introduction", "S", "W", "O", "T", "key_takeaway", "matrix_introduction", "matrix_takeaway", "roadmap_introduction", "roadmap_takeaway", "roadmap"}
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
