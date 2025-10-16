"""
SWOT generation engine for GoodBlue Strategy App.

- Pluggable LLM provider (OpenAI) with JSON-only prompts
- Safe JSON extraction + robust fallbacks

Usage:
    from generate import StrategyGenerator, OpenAIProvider

    provider = OpenAIProvider(model="gpt-4o-mini")
    gen = StrategyGenerator(provider)

    swot = gen.generate_swot(
        company=state["company"],
        industry=state["industry"],
        product=state["product"],
        product_feature=state["scope"],
        notes=state.get("notes"),
        geo=state.get("geo")
    )
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ---------------------- LLM Provider Abstraction ----------------------

class LLMProvider:
    def complete(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.2, max_tokens: int = 1200) -> str:
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    """OpenAI chat completions provider. Requires `openai` >= 1.0.0.
    Set OPENAI_API_KEY in env or pass api_key.
    """
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise RuntimeError("OpenAI Python SDK not installed. `pip install openai`.") from e
        self._OpenAI = OpenAI
        self.model = model
        self.client = self._OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def complete(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.2, max_tokens: int = 1200) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""

# ---------------------- Utilities ----------------------

def _coerce_list(x: Any) -> List[str]:
    if x is None:
        return []
    if isinstance(x, list):
        return [str(i).strip() for i in x if str(i).strip()]
    return [str(x).strip()] if str(x).strip() else []

_JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")

def _extract_json(text: str) -> Dict[str, Any]:
    """Try to parse JSON from the model output. Accepts raw JSON or fenced blocks.
    Falls back to empty dict on failure.
    """
    if not text:
        return {}
    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass
    # Look for the first JSON-looking block
    m = _JSON_BLOCK_RE.search(text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {}

def _topn(items: List[str], n: int = 8) -> List[str]:
    """Keep top N items per list"""
    return items[:n] if len(items) > n else items

# ---------------------- Prompts ----------------------

_GEN_SYS = (
    "You are a concise strategy analyst. Return only strict JSON with the requested keys. "
    "No prose, no markdown, no backticks. Keep each list item short (<=18 words)."
)

_DEF_BENCH_CAPS = [
    "Brand strength",
    "Distribution/Channels",
    "Pricing/Packaging",
    "Integrations/Partner ecosystem",
    "Security/Compliance",
    "Analytics/AI",
    "Implementation complexity",
    "Support/Success"
]

def _swot_prompt(
    company: str,
    industry: str,
    product: str,
    product_feature: str,
    notes: Optional[str],
    geo: Optional[str]
) -> str:
    return f"""
Company: {company}
Industry: {industry}
Product: {product}
Product Feature: {product_feature}
Geography: {geo or "unspecified"}
Notes: {notes or ""}

TASK: Generate a detailed SWOT for the inputs.

Constraints:
- Return **ONLY** valid JSON. No commentary, no code fences.
- Each of S, W, O, T must have **5–8 bullets**.
- Each bullet 8–18 words, **specific** (no vague boilerplate like "industry leading").
- Reflect the local context of **{geo or "the target market"}** and trends in **{industry}**.
- Cover these capabilities across the set of bullets (spread them; no need to label each):
  {", ".join(_DEF_BENCH_CAPS)}.
- Avoid duplicates; no trailing commas.

Output schema (must match exactly these keys):
{{
  "S": ["...", "..."],
  "W": ["...", "..."],
  "O": ["...", "..."],
  "T": ["...", "..."]
}}
""".strip()

# ---------------------- Fallback ----------------------

def _fallback_swot() -> Dict[str, Any]:
    return {
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
    }

# ---------------------- Core Generator ----------------------

@dataclass
class StrategyGenerator:
    provider: Optional[LLMProvider] = None

    def generate_swot(
        self, 
        company: str, 
        industry: str, 
        product: str,
        product_feature: str,
        *, 
        notes: Optional[str] = None, 
        geo: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Generate SWOT analysis using LLM provider or fallback."""
        if self.provider:
            out = _extract_json(
                self.provider.complete(
                    _GEN_SYS, 
                    _swot_prompt(company, industry, product, product_feature, notes, geo)
                )
            )
            S = _coerce_list(out.get("S"))
            W = _coerce_list(out.get("W"))
            O = _coerce_list(out.get("O"))
            T = _coerce_list(out.get("T"))
            if any([S, W, O, T]):
                return {"S": _topn(S), "W": _topn(W), "O": _topn(O), "T": _topn(T)}
        # fallback
        return _fallback_swot()

# ---------------------- Quick self-test ----------------------
if __name__ == "__main__":
    gen = StrategyGenerator(provider=None)  # offline fallback
    swot = gen.generate_swot(
        company="ACME Robotics",
        industry="Manufacturing",
        product="Industrial IoT Sensors",
        product_feature="Identifying bearing failure",
        notes="Mid-market focus",
        geo="US"
    )
    print(json.dumps(swot, indent=2))
