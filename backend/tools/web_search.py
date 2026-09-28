"""
web_search.py — Deterministic multi-provider web search and browser navigation tools.
Features:
- Canonical WebSearchResult & SearchResult schemas (no raw HTML or webpage dumps).
- Explicit CAPTCHA / bot challenge detection (rejects 'Select squares containing a duck', etc.).
- Multi-tier search fallback pipeline (DDG Lite -> DDG HTML -> Bing -> Wikipedia).
- URL navigation and web page preview extraction.
"""
from __future__ import annotations

import base64
import logging
import re
import urllib.parse
import webbrowser
from typing import Any

import httpx
from bs4 import BeautifulSoup

from models.web_search import SearchResult, WebSearchResult, detect_bot_challenge

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def decode_target_url(href: str) -> str:
    """Extract and decode destination URL from search engine redirect links."""
    if not href:
        return ""
    clean = href.strip()

    # DuckDuckGo redirect: //duckduckgo.com/l/?uddg=https%3A%2F%2F...
    if "uddg=" in clean:
        match = re.search(r"uddg=([^&]+)", clean)
        if match:
            try:
                return urllib.parse.unquote(match.group(1))
            except Exception:
                pass

    # Bing redirect: https://www.bing.com/ck/a?!&&p=...&u=a1<base64>&...
    if "bing.com/ck/a" in clean and "u=a1" in clean:
        match = re.search(r"u=a1([a-zA-Z0-9_-]+)", clean)
        if match:
            b64_str = match.group(1).replace("-", "+").replace("_", "/")
            pad = len(b64_str) % 4
            if pad:
                b64_str += "=" * (4 - pad)
            try:
                decoded = base64.b64decode(b64_str).decode("utf-8", errors="ignore")
                if decoded.startswith(("http://", "https://")):
                    return decoded
            except Exception:
                pass

    if clean.startswith("//"):
        return f"https:{clean}"

    return clean


def extract_domain(url: str) -> str:
    """Extract simple domain name for source label."""
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.replace("www.", "")
    except Exception:
        return ""


async def _search_ddg_lite(client: httpx.AsyncClient, query: str) -> WebSearchResult:
    """Provider 1: DuckDuckGo Lite (structured HTML table, no JS overhead)."""
    provider_name = "DuckDuckGo Lite"
    url = "https://lite.duckduckgo.com/lite/"
    try:
        resp = await client.post(url, data={"q": query}, headers=HEADERS, timeout=8.0, follow_redirects=True)
        html = resp.text
        is_blocked, reason = detect_bot_challenge(html)
        if is_blocked:
            return WebSearchResult(
                query=query,
                status="blocked",
                provider=provider_name,
                blocked=True,
                reason=reason,
                error=reason,
            )

        if resp.status_code != 200:
            return WebSearchResult(
                query=query,
                status="failed",
                provider=provider_name,
                error=f"HTTP {resp.status_code}",
            )

        soup = BeautifulSoup(html, "html.parser")
        results: list[SearchResult] = []

        tables = soup.select("table")
        if len(tables) >= 3:
            rows = tables[2].select("tr")
            for i in range(0, len(rows), 4):
                title_row = rows[i] if i < len(rows) else None
                snip_row = rows[i + 1] if i + 1 < len(rows) else None
                if title_row:
                    link_el = title_row.select_one(".result-link")
                    snip_el = snip_row.select_one(".result-snippet") if snip_row else None
                    if link_el:
                        title = link_el.get_text(strip=True)
                        dest_url = decode_target_url(link_el.get("href", ""))
                        snippet = snip_el.get_text(strip=True) if snip_el else ""

                        if title and dest_url.startswith(("http://", "https://")):
                            res = SearchResult(
                                title=title,
                                url=dest_url,
                                snippet=snippet or title,
                                source=extract_domain(dest_url),
                            )
                            if res.is_valid():
                                results.append(res)
                if len(results) >= 8:
                    break

        if not results:
            return WebSearchResult(query=query, status="empty", provider=provider_name, error="No results parsed.")

        return WebSearchResult(query=query, status="success", provider=provider_name, results=results)

    except Exception as exc:
        logger.warning("%s search failed: %s", provider_name, exc)
        return WebSearchResult(query=query, status="failed", provider=provider_name, error=str(exc))


async def _search_ddg_html(client: httpx.AsyncClient, query: str) -> WebSearchResult:
    """Provider 2: DuckDuckGo HTML endpoint."""
    provider_name = "DuckDuckGo HTML"
    encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    try:
        resp = await client.get(url, headers=HEADERS, timeout=8.0, follow_redirects=True)
        html = resp.text
        is_blocked, reason = detect_bot_challenge(html)
        if is_blocked:
            return WebSearchResult(
                query=query,
                status="blocked",
                provider=provider_name,
                blocked=True,
                reason=reason,
                error=reason,
            )

        if resp.status_code != 200:
            return WebSearchResult(
                query=query,
                status="failed",
                provider=provider_name,
                error=f"HTTP {resp.status_code}",
            )

        soup = BeautifulSoup(html, "html.parser")
        results: list[SearchResult] = []

        for item in soup.select(".result"):
            title_el = item.select_one(".result__title a")
            snip_el = item.select_one(".result__snippet")
            if title_el:
                title = title_el.get_text(strip=True)
                dest_url = decode_target_url(title_el.get("href", ""))
                snippet = snip_el.get_text(strip=True) if snip_el else ""

                if title and dest_url.startswith(("http://", "https://")):
                    res = SearchResult(
                        title=title,
                        url=dest_url,
                        snippet=snippet or title,
                        source=extract_domain(dest_url),
                    )
                    if res.is_valid():
                        results.append(res)
            if len(results) >= 8:
                break

        if not results:
            return WebSearchResult(query=query, status="empty", provider=provider_name, error="No results parsed.")

        return WebSearchResult(query=query, status="success", provider=provider_name, results=results)

    except Exception as exc:
        logger.warning("%s search failed: %s", provider_name, exc)
        return WebSearchResult(query=query, status="failed", provider=provider_name, error=str(exc))


async def _search_bing(client: httpx.AsyncClient, query: str) -> WebSearchResult:
    """Provider 3: Bing Search."""
    provider_name = "Bing Search"
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded}"
    try:
        resp = await client.get(url, headers=HEADERS, timeout=8.0, follow_redirects=True)
        if resp.status_code != 200:
            return WebSearchResult(
                query=query,
                status="failed",
                provider=provider_name,
                error=f"HTTP {resp.status_code}",
            )

        html = resp.text
        is_blocked, reason = detect_bot_challenge(html)
        if is_blocked:
            return WebSearchResult(
                query=query,
                status="blocked",
                provider=provider_name,
                blocked=True,
                reason=reason,
                error=reason,
            )

        soup = BeautifulSoup(html, "html.parser")
        results: list[SearchResult] = []

        for li in soup.select("li.b_algo"):
            h2_a = li.select_one("h2 a")
            snip_p = li.select_one(".b_caption p")
            if h2_a:
                title = h2_a.get_text(strip=True)
                raw_url = h2_a.get("href", "")
                dest_url = decode_target_url(raw_url)
                snippet = snip_p.get_text(strip=True) if snip_p else ""

                if title and dest_url.startswith(("http://", "https://")):
                    res = SearchResult(
                        title=title,
                        url=dest_url,
                        snippet=snippet or title,
                        source=extract_domain(dest_url),
                    )
                    if res.is_valid():
                        results.append(res)
            if len(results) >= 8:
                break

        if not results:
            return WebSearchResult(query=query, status="empty", provider=provider_name, error="No results parsed.")

        return WebSearchResult(query=query, status="success", provider=provider_name, results=results)

    except Exception as exc:
        logger.warning("%s search failed: %s", provider_name, exc)
        return WebSearchResult(query=query, status="failed", provider=provider_name, error=str(exc))


async def _search_wikipedia(client: httpx.AsyncClient, query: str) -> WebSearchResult:
    """Provider 4: Wikipedia OpenSearch API (for informational / entity topics)."""
    provider_name = "Wikipedia"
    encoded = urllib.parse.quote_plus(query)
    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={encoded}&limit=5&format=json"
    headers = {"User-Agent": "GravityPilot/1.0 (https://github.com/gravity-pilot)"}
    try:
        resp = await client.get(url, headers=headers, timeout=6.0)
        if resp.status_code != 200:
            return WebSearchResult(query=query, status="failed", provider=provider_name, error=f"HTTP {resp.status_code}")

        data = resp.json()
        if not isinstance(data, list) or len(data) < 4:
            return WebSearchResult(query=query, status="empty", provider=provider_name, error="Invalid response format.")

        titles, snippets, urls = data[1], data[2], data[3]
        results: list[SearchResult] = []
        for t, s, u in zip(titles, snippets, urls):
            if t and u and u.startswith(("http://", "https://")):
                res = SearchResult(
                    title=t,
                    url=u,
                    snippet=s or t,
                    source="wikipedia.org",
                )
                if res.is_valid():
                    results.append(res)

        if not results:
            return WebSearchResult(query=query, status="empty", provider=provider_name, error="No Wikipedia matches.")

        return WebSearchResult(query=query, status="success", provider=provider_name, results=results)

    except Exception as exc:
        return WebSearchResult(query=query, status="failed", provider=provider_name, error=str(exc))


def sanitize_search_query(query: str) -> str:
    """Strip conversational prefixes like 'search the web for' to query exact topics."""
    q = (query or "").strip()
    pattern = r"^(search\s+the\s+web\s+for|search\s+the\s+web|search\s+for|search\s+about|search|lookup|find\s+online\s+for|find\s+online\s+about|find\s+online)\s+"
    cleaned = re.sub(pattern, "", q, flags=re.IGNORECASE).strip()
    return cleaned if len(cleaned) >= 2 else q


async def execute_multi_provider_search(query: str) -> tuple[WebSearchResult, list[dict[str, Any]]]:
    """
    Execute search with resilient fallback hierarchy:
    DDG Lite -> DDG HTML -> Bing -> Wikipedia.
    Detects CAPTCHA/bot challenges and switches to fallback immediately without halting.
    Emits granular execution traces matching Requirement 8.
    """
    clean_query = (query or "").strip()
    effective_query = sanitize_search_query(clean_query)
    traces: list[dict[str, Any]] = []

    if not effective_query:
        result = WebSearchResult(
            query=clean_query,
            status="failed",
            error="Search query cannot be empty.",
        )
        return result, traces

    providers = [
        ("DuckDuckGo Lite", _search_ddg_lite),
        ("DuckDuckGo HTML", _search_ddg_html),
        ("Bing Search", _search_bing),
        ("Wikipedia", _search_wikipedia),
    ]

    had_blocked_provider = False
    blocked_provider_name = ""

    async with httpx.AsyncClient(timeout=12.0) as client:
        for idx, (provider_name, search_fn) in enumerate(providers):
            traces.append({
                "agent": "browser_agent",
                "status": "info",
                "message": f"Web Search → Querying search provider: {provider_name}",
            })

            search_outcome: WebSearchResult = await search_fn(client, effective_query)
            search_outcome.query = clean_query

            if search_outcome.blocked:
                had_blocked_provider = True
                blocked_provider_name = provider_name
                traces.append({
                    "agent": "browser_agent",
                    "status": "warning",
                    "message": f"{provider_name} → CAPTCHA / Bot verification challenge detected. Switching to fallback search provider...",
                })
                continue

            if search_outcome.status == "success" and search_outcome.results:
                traces.append({
                    "agent": "browser_agent",
                    "status": "info",
                    "message": f"{provider_name} → Result Extraction: Retrieved {len(search_outcome.results)} structured search results.",
                })
                return search_outcome, traces

            # Provider failed or empty, proceed to next
            traces.append({
                "agent": "browser_agent",
                "status": "info",
                "message": f"{provider_name} returned no usable results ({search_outcome.error or 'empty'}). Trying next provider...",
            })

    # If all providers failed
    if had_blocked_provider:
        final_err = "I couldn't retrieve live search results because the search provider blocked the request."
        traces.append({
            "agent": "browser_agent",
            "status": "error",
            "message": f"Search failed: All providers blocked or unavailable. Primary {blocked_provider_name} was blocked.",
        })
        return WebSearchResult(
            query=clean_query,
            status="blocked",
            provider=blocked_provider_name,
            blocked=True,
            error=final_err,
            reason="Search provider returned a bot verification challenge",
        ), traces

    no_res_err = f"No search results could be retrieved for '{clean_query}' across all search providers."
    traces.append({
        "agent": "browser_agent",
        "status": "error",
        "message": no_res_err,
    })
    return WebSearchResult(
        query=clean_query,
        status="empty",
        provider="All providers",
        error=no_res_err,
    ), traces


async def open_url(url: str) -> dict[str, Any]:
    """Open a URL in the browser and return page details."""
    target = (url or "").strip()
    if not target:
        return {
            "success": False,
            "error": "URL cannot be empty",
            "operation": "open_url",
            "agent_type": "browser_agent",
        }

    target_lower = target.lower()
    if target_lower in ("google", "google.com", "open google"):
        target = "https://www.google.com"
    elif not target.startswith(("http://", "https://")):
        target = f"https://{target}"

    try:
        webbrowser.open(target)
    except Exception as wb_err:
        logger.warning("webbrowser.open warning: %s", wb_err)

    title = target
    preview = f"Opened website in browser: {target}"

    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(target, headers=HEADERS)
            if resp.status_code == 200:
                is_blocked, _ = detect_bot_challenge(resp.text)
                if not is_blocked:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    if soup.title and soup.title.string:
                        title = soup.title.string.strip()
                    for tag in soup(["script", "style", "nav", "footer"]):
                        tag.extract()
                    body_text = soup.get_text(separator=" ", strip=True)[:350]
                    if body_text:
                        preview = f"Opened {target} ({title}).\n\nPreview: {body_text}..."
    except Exception as exc:
        logger.debug("Page preview skipped for %s: %s", target, exc)

    return {
        "success": True,
        "url": target,
        "title": title,
        "operation": "open_url",
        "extracted_data": preview,
        "agent_type": "browser_agent",
    }


async def web_search(query: str, extract: str = "summary") -> dict[str, Any]:
    """Execute real web search using multi-provider fallback hierarchy."""
    clean_query = (query or "").strip()
    if not clean_query:
        return {
            "success": False,
            "error": "Search query cannot be empty",
            "operation": "web_search",
            "agent_type": "browser_agent",
        }

    search_result, _ = await execute_multi_provider_search(clean_query)
    return search_result.to_execution_result()
