"""
web_search.py — Canonical models and helpers for web search results and validation.
Enforces structured search results and blocks CAPTCHA / bot challenge pollution.
"""
from __future__ import annotations

import re
from typing import List, Optional
from pydantic import BaseModel, Field


# Comprehensive detection for CAPTCHA, bot challenges, and security blocks
BOT_CHALLENGE_PATTERNS = [
    r"unfortunately,\s*bots\s*use\s*duckduckgo\s*too",
    r"please\s*complete\s*the\s*following\s*challenge",
    r"select\s*all\s*squares\s*containing\s*a\s*duck",
    r"verify\s*(that\s*)?you\s*are\s*a?\s*human",
    r"confirm\s*this\s*search\s*was\s*made\s*by\s*a\s*human",
    r"unusual\s*traffic\s*from\s*your\s*computer\s*network",
    r"are\s*you\s*a\s*human",
    r"human\s*verification\s*challenge",
    r"cf-challenge",
    r"cloudflare\s*ray\s*id",
    r"access\s*denied",
    r"recaptcha",
    r"hcaptcha",
    r"cloudflare-turnstile",
    r"select\s*all\s*squares",
    r"solve\s*the\s*challenge",
    r"confirm\s*you('re| are)\s*not\s*a\s*robot",
    r"i'm\s*not\s*a\s*robot",
]

COMPILED_BOT_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BOT_CHALLENGE_PATTERNS]


def detect_bot_challenge(content: str, secondary: str = "") -> tuple[bool, str]:
    """
    Detect whether the content is a bot challenge / CAPTCHA block page.
    Automatically strips scripts, styles, and tags if HTML is present.
    Returns (is_blocked, reason).
    """
    from bs4 import BeautifulSoup

    combined = f"{content or ''} {secondary or ''}".strip()
    if not combined:
        return False, ""

    if "<" in combined and ">" in combined:
        try:
            soup = BeautifulSoup(combined, "html.parser")
            for tag in soup(["script", "style", "svg", "noscript"]):
                tag.extract()
            text = soup.get_text(separator=" ", strip=True)
        except Exception:
            text = combined
    else:
        text = combined

    for pattern in COMPILED_BOT_PATTERNS:
        match = pattern.search(text)
        if match:
            matched_phrase = match.group(0).strip()
            return True, f"Search provider returned a bot verification challenge ('{matched_phrase}')"

    return False, ""


class SearchResult(BaseModel):
    """Canonical model for an individual web search result."""
    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="Destination URL of the search result")
    snippet: str = Field(..., description="Informative snippet or excerpt")
    source: str = Field(default="", description="Source domain or name")

    def is_valid(self) -> bool:
        """Check if result is structurally valid and not CAPTCHA/navigation text."""
        if not self.title or not self.title.strip():
            return False
        if not self.url or not (self.url.startswith("http://") or self.url.startswith("https://")):
            return False
        if not self.snippet or not self.snippet.strip():
            return False
        
        # Ensure title/snippet are not bot challenges
        blocked, _ = detect_bot_challenge(f"{self.title} {self.snippet}")
        if blocked:
            return False

        # Ensure not purely navigation
        nav_terms = {"images", "videos", "news", "maps", "open menu", "duck.ai", "sign in", "all images videos"}
        if self.title.lower().strip() in nav_terms and len(self.snippet) < 30:
            return False

        return True


class WebSearchResult(BaseModel):
    """Canonical model for aggregated web search outcome across agents."""
    query: str
    status: str = "success"  # "success" | "blocked" | "failed" | "empty"
    provider: str = "Unknown"
    results: List[SearchResult] = Field(default_factory=list)
    error: Optional[str] = None
    blocked: bool = False
    reason: Optional[str] = None

    def to_execution_result(self) -> dict:
        """
        Convert to structured execution result dictionary expected by LangGraph and ValidationAgent.
        NEVER passes raw HTML or raw unparsed page content.
        """
        lines = []
        for i, res in enumerate(self.results, 1):
            source_lbl = f"Source: {res.source or res.url}"
            lines.append(f"{i}. **{res.title}**\n   *{source_lbl}*\n   {res.snippet}")
        
        formatted_summary = "\n\n".join(lines) if lines else ""

        is_success = (
            self.status == "success"
            and not self.blocked
            and len(self.results) > 0
            and all(r.is_valid() for r in self.results)
        )

        return {
            "success": is_success,
            "operation": "web_search",
            "agent_type": "browser_agent",
            "query": self.query,
            "status": self.status,
            "provider": self.provider,
            "blocked": self.blocked,
            "reason": self.reason,
            "error": self.error,
            "results": [r.model_dump() for r in self.results],
            "extracted_data": formatted_summary,
            "url": self.results[0].url if self.results else "",
            "title": f'Search results for "{self.query}"',
        }
