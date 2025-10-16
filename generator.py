"""
Base LLM generator for GoodBlue Strategy App.

Provides common LLM provider interface and utilities that can be reused
across all framework modules (SWOT, Ansoff, Porter's 5 Forces, etc.)

Usage:
    from generator import StrategyGenerator, OpenAIProvider
    
    provider = OpenAIProvider(model="gpt-4o-mini", api_key="...")
    gen = StrategyGenerator(provider)
    
    result = gen.generate(system_prompt, user_prompt)
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ---------------------- LLM Provider Abstraction ----------------------

class LLMProvider:
    """Abstract base class for LLM providers."""
    def complete(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        *, 
        temperature: float = 0.2, 
        max_tokens: int = 1200
    ) -> str:
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    """OpenAI chat completions provider. 
    
    Requires `openai` >= 1.0.0.
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

    def complete(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        *, 
        temperature: float = 0.2, 
        max_tokens: int = 1200
    ) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""

# ---------------------- Utilities ----------------------

def _coerce_list(x: Any) -> List[str]:
    """Coerce value to list of strings."""
    if x is None:
        return []
    if isinstance(x, list):
        return [str(i).strip() for i in x if str(i).strip()]
    return [str(x).strip()] if str(x).strip() else []

_JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")

def _extract_json(text: str) -> Dict[str, Any]:
    """Try to parse JSON from the model output. 
    
    Accepts raw JSON or fenced blocks.
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

def topn(items: List[str], n: int = 8) -> List[str]:
    """Keep top N items from list."""
    return items[:n] if len(items) > n else items

def coerce_list(x: Any) -> List[str]:
    """Public wrapper for _coerce_list."""
    return _coerce_list(x)

def extract_json(text: str) -> Dict[str, Any]:
    """Public wrapper for _extract_json."""
    return _extract_json(text)

# ---------------------- Core Generator ----------------------

@dataclass
class StrategyGenerator:
    """Base strategy content generator.
    
    Provides common interface for generating strategy framework content
    using pluggable LLM providers.
    """
    provider: Optional[LLMProvider] = None

    def generate(
        self, 
        system_prompt: str, 
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1200
    ) -> str:
        """Generate raw text response from LLM."""
        if not self.provider:
            raise ValueError("No LLM provider configured")
        return self.provider.complete(
            system_prompt, 
            user_prompt, 
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1200
    ) -> Dict[str, Any]:
        """Generate and parse JSON response from LLM."""
        if not self.provider:
            return {}
        response = self.provider.complete(
            system_prompt,
            user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return _extract_json(response)
    
    def is_available(self) -> bool:
        """Check if generator has a valid provider."""
        return self.provider is not None

# ---------------------- Default System Prompt ----------------------

DEFAULT_SYSTEM_PROMPT = (
    "Return only strict JSON with the requested keys. "
    "No prose, no markdown, no backticks."
)

# ---------------------- Quick self-test ----------------------
if __name__ == "__main__":
    # Test without provider
    gen = StrategyGenerator(provider=None)
    print(f"Generator available: {gen.is_available()}")
    
    # Test with mock provider
    class MockProvider(LLMProvider):
        def complete(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
            return '{"test": "data"}'
    
    gen_with_provider = StrategyGenerator(provider=MockProvider())
    result = gen_with_provider.generate_json("system", "user")
    print(f"Mock result: {result}")
