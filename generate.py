"""
Strategy content generation engine for your Streamlit app (Step 1).

- Pluggable LLM provider (OpenAI) with JSON-only prompts
- Safe JSON extraction + robust fallbacks (no external calls required)
- Consistent schema aligned to session_state in your UX spec

Usage (in Streamlit button handler):

    #from generate import StrategyGenerator, OpenAIProvider

    provider = OpenAIProvider(model="gpt-4o-mini")  # or None for offline fallback
    gen = StrategyGenerator(provider)

    results = gen.generate_selected_frameworks(
        company=state["company"],
        scope=state["scope"],
        product=state["product"],
        frameworks=state["frameworks"],
        notes=state.get("notes"),
        geo=state.get("geo") or None,
        peers=["Rival A", "Rival B"]
    )
    state["results"].update(results)

    # Optional: auto-generate recommendations
    state["recs"] = gen.generate_recommendations(state["results"], constraints={})

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

# Clamp helper to top-N items per list to keep outputs tidy

def _topn(items: List[str], n: int = 6) -> List[str]:
    return items[:n] if len(items) > n else items

# ---------------------- Prompts ----------------------

_GEN_SYS = (
    "You are a concise strategy analyst. Return only strict JSON with the requested keys. "
    "No prose, no markdown, no backticks. Keep each list item short (<=18 words)."
)

def _scope_prompt(company: str) -> str:
    return f"""
Company: {company}
       Produce JSON with the key scope with an exact and concise 1-line description of the relevant business scope of the company.
        """.strip()



def _industry_analysis_prompt(
    company: str,
    scope: str,
    product: str,
    notes: Optional[str],
    geo: Optional[str],
    success_factors: Optional[dict] = None) -> str:
    try:
        with open("porter.json", "r") as f:
            success_factors = json.load(f)
    except Exception:
        success_factors = {}
    return f"""
Company: {company}
Scope: {scope}
Product: {product}
Geography: {geo or "unspecified"}
Notes: {notes or ""}

Return strict JSON only. No prose, no markdown.

You are given a JSON file of success factors:
{json.dumps(success_factors, indent=2)}

Task:
1) List the top 5 industry verticals applicable to the Company, Scope, and Product (exactly 5).
2) From the provided JSON, choose the 3 most important Critical_success_category for this context (exactly 3).
3) For each chosen category, select the top 3 success factors (exactly 3 per category), each ≤5 words and contextual to the scope/product.

Each industry item must include:
- "industry_vertical_name": string
- "TAM": number in billions (int or float)
- "Critical_success_category": object with exactly 3 categories; each category has exactly 3 factors (strings ≤5 words)

Example schema:
{{
  "industries": [
    {{
      "industry_vertical_name": "Financial Services",
      "TAM": 20,
      "Critical_success_category": {{
        "Brand": [
          "Trust with regulated clients",
          "Strong financial client references",
          "Reputation for compliance readiness"
        ],
        "Economies_of_Scale": [
          "Shared R&D costs across global clients",
          "Specialized financial services teams",
          "Extensive partner ecosystem"
        ],
        "Capital": [
          "Upfront compliance investment",
          "Infrastructure resilience",
          "Integration with legacy banking systems"
        ]
      }}
    }},
    {{
      "industry_vertical_name": "Manufacturing",
      "TAM": 10,
      "Critical_success_category": {{
        "Brand": [
          "Trusted vendor for factory automation",
          "Proven reliability in industrial workflows",
          "Reputation for minimizing downtime"
        ],
        "Economies_of_Scale": [
          "Global standardization lowers automation cost",
          "Shared R&D across manufacturing clients",
          "Bulk deployments reduce per-unit pricing"
        ],
        "Capital": [
          "Integration with robotics demands investment",
          "IoT infrastructure requires upfront funding",
          "Legacy system upgrades need capital"
        ]
      }}
    }}
  ]
}}
""".strip()
    
def _swot_prompt(company: str, scope: str, product: str, notes: Optional[str], geo: Optional[str]) -> str:
    return f"""
Company: {company}
scope: {scope}
Product: {product}
Geography: {geo or "unspecified"}
Notes: {notes or ""}

Produce JSON exactly with keys S, W, O, T. Each is an array of bullets.
Example schema:
{{"S":[],"W":[],"O":[],"T":[]}}
""".strip()

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

def _ansoff_prompt(company: str, product: str, notes: Optional[str], geo: Optional[str]) -> str:
    return f"""
Company: {company}
Product: {product}
Geography: {geo or "unspecified"}
Notes: {notes or ""}
Return strict JSON with keys: market_penetration, market_development, product_development, diversification. Each is an array of short initiatives.
""".strip()

def _benchmark_prompt(company: str, product: str, peers: List[str], caps: List[str]) -> str:
    peers_csv = ", ".join(peers)
    caps_csv = ", ".join(caps)
    return f"""
Compare {company} ({product}) against peers: {peers_csv}.
Capabilities to rate: {caps_csv}.
Return JSON: {{"peers": ["{peers_csv}"], "table": [{{"capability": str, "{company}": str, "{peers[0]}": str, "{peers[1] if len(peers)>1 else 'PeerB'}": str}} ...]}}. Ratings must be one of: Low, Medium, High, Best-in-class.
Keep table length = {len(caps)}.
""".strip()

def _recs_prompt(company: str, product: str, results: Dict[str, Any]) -> str:
    context = json.dumps(results, ensure_ascii=False)
    return f"""
Based on this analysis JSON: {context}
Return JSON array of 5 recommendation objects with keys: title, impact (1-5), effort (1-5), rationale.
Keep titles crisp; impact×effort should reflect SWOT threats/opportunities and Ansoff moves.
""".strip()

# ---------------------- Fallback (offline) heuristics ----------------------

def _fallback_scope() -> Dict[str, List[str]]:
    return ""

def _fallback_ind() -> Dict[str, List[str]]:
    return {
        "industries": [
            {
                "industry_vertical_name": "Financial Services",
                "TAM": 20,
                "Critical_success_category": {
                    "Brand": [
                        "Trust with regulated clients",
                        "Strong financial client references",
                        "Reputation for compliance readiness"
                        ],
                    "Economies_of_Scale": [
                        "Shared R&D costs across global clients",
                        "Specialized financial services teams",
                        "Extensive partner ecosystem"
                        ],
                    "Capital": [
                        "Upfront compliance investment",
                        "Infrastructure resilience",
                        "Integration with legacy banking systems"
                        ]
                }
            },
            {
                "industry_vertical_name": "Manufacturing",
                "TAM": 10,
                "Critical_success_category": {
                    "Brand": [
                        "Trusted vendor for factory automation",
                        "Proven reliability in industrial workflows",
                        "Reputation for minimizing downtime"
                        ],
                    "Economies_of_Scale": [
                        "Global standardization lowers automation cost",
                        "Shared R&D across manufacturing clients",
                        "Bulk deployments reduce per-unit pricing"
                        ],
                    "Capital": [
                        "Integration with robotics demands investment",
                        "IoT infrastructure requires upfront funding",
                        "Legacy system upgrades need capital"
                        ]
                    }
                }
            ]
        }

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

def _fallback_ansoff() -> Dict[str, List[str]]:
    return {
        "market_penetration": ["Bundle add-ons for existing customers", "Loyalty pricing to reduce churn"],
        "market_development": ["Enter 1–2 adjacent regions", "Activate reseller partners"],
        "product_development": ["Launch analytics-lite", "Managed service option"],
        "diversification": ["Test vertical solution pack", "Hardware+SaaS starter kit"],
    }

def _fallback_benchmark(company: str, peers: List[str], caps: List[str]) -> Dict[str, Any]:
    table = []
    scale = ["Low", "Medium", "High"]
    for i, cap in enumerate(caps):
        row = {"capability": cap, company: scale[min(2, (i+1) % 3)]}
        for p in peers:
            row[p] = scale[(i + len(p)) % 3]
        table.append(row)
    return {"peers": peers, "table": table}

# ---------------------- Core Generator ----------------------

@dataclass

class StrategyGenerator:
    provider: Optional[LLMProvider] = None

    # ---- Public API ----
    def generate_Industry_Analysis(self, company: str, scope: str, product: str, *, notes: Optional[str] = None, geo: Optional[str] = None) -> Dict[str, Any]:
        if self.provider:
            out = _extract_json(self.provider.complete(_GEN_SYS, _industry_analysis_prompt(company, scope, product, notes, geo)))
            #if isinstance(out, list):
            return out
        # fallback
        return _fallback_ind()
        
    def generate_swot(self, company: str, scope: str, product: str, *, notes: Optional[str] = None, geo: Optional[str] = None) -> Dict[str, List[str]]:
        if self.provider:
            out = _extract_json(
                self.provider.complete(_GEN_SYS, _swot_prompt(company, scope, product, notes, geo))
            )
            S = _coerce_list(out.get("S"))
            W = _coerce_list(out.get("W"))
            O = _coerce_list(out.get("O"))
            T = _coerce_list(out.get("T"))
            if any([S, W, O, T]):
                return {"S": _topn(S), "W": _topn(W), "O": _topn(O), "T": _topn(T)}
        # fallback
        return _fallback_swot()

    def generate_ansoff(self, company: str, scope: str, product: str, *, notes: Optional[str] = None, geo: Optional[str] = None) -> Dict[str, List[str]]:
        if self.provider:
            out = _extract_json(
                self.provider.complete(_GEN_SYS, _ansoff_prompt(company, product, notes, geo))
            )
            mp = _coerce_list(out.get("market_penetration"))
            md = _coerce_list(out.get("market_development"))
            pd = _coerce_list(out.get("product_development"))
            dv = _coerce_list(out.get("diversification"))
            if any([mp, md, pd, dv]):
                return {
                    "market_penetration": _topn(mp),
                    "market_development": _topn(md),
                    "product_development": _topn(pd),
                    "diversification": _topn(dv),
                }
        return _fallback_ansoff()

    def generate_benchmark(self, company: str, scope: str, product: str, *, peers: Optional[List[str]] = None, caps: Optional[List[str]] = None) -> Dict[str, Any]:
        peers = peers or ["PeerA", "PeerB"]
        caps = caps or _DEF_BENCH_CAPS
        if self.provider:
            out = _extract_json(
                self.provider.complete(_GEN_SYS, _benchmark_prompt(company, product, peers, caps))
            )
            table = out.get("table")
            if isinstance(table, list) and table:
                # keep only declared columns
                cleaned = []
                for row in table:
                    if not isinstance(row, dict):
                        continue
                    base = {"capability": str(row.get("capability", "")).strip()}
                    if not base["capability"]:
                        continue
                    base[company] = str(row.get(company, "")).strip() or "Medium"
                    for p in peers:
                        base[p] = str(row.get(p, "")).strip() or "Medium"
                    cleaned.append(base)
                return {"peers": peers, "table": cleaned[: len(caps)]}
        return _fallback_benchmark(company, peers, caps)

    def generate_recommendations(self, results: Dict[str, Any], *, top_k: int = 5, constraints: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Heuristic scaffold using SWOT + Ansoff if no LLM
        def _score(title: str) -> Dict[str, int]:
            # naive scoring based on keywords
            t = title.lower()
            impact = 5 if any(k in t for k in ["bundle", "platform", "ai", "oem", "security"]) else 4
            effort = 3 if any(k in t for k in ["managed", "new region"]) else 2
            return {"impact": impact, "effort": effort}

        if self.provider:
            try:
                out = _extract_json(self.provider.complete(_GEN_SYS, _recs_prompt("", "", results)))
                if isinstance(out, list) and out:
                    cleaned = []
                    for item in out[: top_k]:
                        if not isinstance(item, dict):
                            continue
                        title = str(item.get("title", "")).strip()
                        if not title:
                            continue
                        impact = int(item.get("impact", 3))
                        effort = int(item.get("effort", 2))
                        rationale = str(item.get("rationale", "")).strip()
                        cleaned.append({"title": title, "impact": max(1, min(5, impact)), "effort": max(1, min(5, effort)), "rationale": rationale})
                    if cleaned:
                        return cleaned
            except Exception:
                pass

        # Fallback: derive from inputs
        swot = results.get("SWOT", {})
        ansoff = results.get("Ansoff", {})
        seeds = []
        seeds += ansoff.get("market_penetration", [])
        seeds += ansoff.get("product_development", [])
        seeds += swot.get("O", [])
        seeds = [s for s in seeds if s]
        if not seeds:
            seeds = [
                "OEM bundle program",
                "Managed calibration add-on",
                "Security proof pack",
                "SKU simplification",
                "Launch design partner pilot",
            ]
        recs = []
        for s in seeds[: top_k]:
            sc = _score(s)
            recs.append({"title": s, "impact": sc["impact"], "effort": sc["effort"], "rationale": "Derived from analysis."})
        return recs

    def generate_selected_frameworks(
        self,
        *,
        company: str,
        scope: str,
        product: str,
        frameworks: List[str],
        notes: Optional[str] = None,
        geo: Optional[str] = None,
        peers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        fwset = set([f.strip() for f in frameworks])
        if "Industry Analysis" in fwset:
            out["ind"] = self.generate_Industry_Analysis(company, scope, product, notes=notes, geo=geo)
        if "SWOT" in fwset:
            out["SWOT"] = self.generate_swot(company, scope, product, notes=notes, geo=geo)
        if "Ansoff" in fwset:
            out["Ansoff"] = self.generate_ansoff(company, scope, product, notes=notes, geo=geo)
        if "Benchmark" in fwset:
            out["Benchmark"] = self.generate_benchmark(company, product, peers=peers)
        if "Fit Matrix" in fwset:
            # simple placeholder matrix
            out["Fit"] = {"matrix": [
                {"capability": "Core platform", "fit": "High"},
                {"capability": "Go-to-market", "fit": "Medium"},
                {"capability": "Operations", "fit": "Medium"},
            ]}
        return out

    def generate_scope(self, company: str) -> str:
        if self.provider:
            out = _extract_json(
                self.provider.complete(_GEN_SYS, _scope_prompt(company))
            )
        return out.get("scope", "")

# ---------------------- Quick self-test ----------------------
if __name__ == "__main__":
    gen = StrategyGenerator(provider=None)  # offline fallback
    res = gen.generate_selected_frameworks(
        company="ACME Robotics",
        scope="builds and sells robots",
        product="Industrial IoT Sensors",
        frameworks=["SWOT", "Ansoff", "Benchmark"],
        notes="Mid-market focus",
        geo="US",
        peers=["Rival A", "Rival B"],
    )
    print(json.dumps(res, indent=2))
    recs = gen.generate_recommendations(res)
    print(json.dumps(recs, indent=2))
