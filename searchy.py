#!/usr/bin/env python3
"""
Reads searchy.txt (or given path) and searches Serper API for the event text
across multiple ticketing/event sites. Only prints URLs when the result's
title/snippet contains a date matching the event date from the file.
"""

import json
import os
import platform
import re
import subprocess
import sys
import urllib.request
import webbrowser
from typing import List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv

load_dotenv()

API_URL = "https://google.serper.dev/search"


def _load_sites() -> List[str]:
    """Load site list from sites.txt (next to this script). Lines starting with - are skipped (disabled)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sites.txt")
    with open(path) as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("-")]


SITES = _load_sites()

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
}

DATE_PATTERNS = [
    r"\b(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday)\s+,?\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{4})\b",
    r"\b(Sat|Sun|Mon|Tue|Wed|Thu|Fri)\s*,?\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{4})\b",
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{4})\b",
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{4})\b",
    r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b",
    r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b",
    r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b",
    r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b",
    r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b",
]


def _parse_capture(m: re.Match, pattern_id: int) -> Optional[Tuple[int, int, int]]:
    """Convert regex match to (year, month, day) by pattern type."""
    try:
        if pattern_id in (0, 2):  # Weekday? Month Day Year  or  Month Day Year
            month_name, day, year = m.group(2).strip(), m.group(3), m.group(4)
            month = MONTHS.get(month_name.lower()[:3]) or MONTHS.get(month_name.lower())
            if month:
                return (int(year), month, int(day))
        elif pattern_id == 1:  # Sat, Apr 11, 2026
            month_abbr, day, year = m.group(2).strip(), m.group(3), m.group(4)
            month = MONTHS.get(month_abbr.lower())
            if month:
                return (int(year), month, int(day))
        elif pattern_id == 3:  # Apr 11, 2026
            month_abbr, day, year = m.group(1).strip(), m.group(2), m.group(3)
            month = MONTHS.get(month_abbr.lower())
            if month:
                return (int(year), month, int(day))
        elif pattern_id == 4:  # 11 April 2026
            day, month_name, year = m.group(1), m.group(2).strip(), m.group(3)
            month = MONTHS.get(month_name.lower()[:3]) or MONTHS.get(month_name.lower())
            if month:
                return (int(year), month, int(day))
        elif pattern_id == 5:  # 11 Apr 2026
            day, month_abbr, year = m.group(1), m.group(2).strip(), m.group(3)
            month = MONTHS.get(month_abbr.lower())
            if month:
                return (int(year), month, int(day))
        elif pattern_id == 6:  # 2026-04-11
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        elif pattern_id == 7:  # 11.04.2026
            a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if a <= 12 and b <= 12:
                return (y, b, a)  # day.month.year
            return (y, b, a)
        elif pattern_id == 8:  # 4/11/2026 (US month/day)
            a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if a <= 12 and b <= 12:
                return (y, a, b)
            return (y, b, a)
    except (ValueError, IndexError, KeyError):
        pass
    return None


def extract_date(filepath: str) -> Tuple[int, int, int]:
    """Parse event date from file. Returns (year, month, day)."""
    with open(filepath, "r") as f:
        s = f.read().strip()
    text = s.replace("|", " ").replace(",", " ").replace("\n", " ")

    for i, pat in enumerate(DATE_PATTERNS):
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            t = _parse_capture(m, i)
            if t:
                y, mo, d = t
                if 2000 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 31:
                    return (y, mo, d)

    sys.exit("ERROR: No date found in " + filepath)


def build_search_content(filepath: str) -> str:
    """Build the search query string from file (first line or first 3 if short)."""
    with open(filepath, "r") as f:
        lines = [ln.strip() for ln in f.readlines()]
    content = (lines[0] if lines else "").strip()
    if len(content) < 40 and len(lines) >= 3:
        content = " ".join(lines[:3]).strip()
    return content or None


def date_matches_text(year: int, month: int, day: int, text: str) -> bool:
    """Return True if text contains a date matching (year, month, day)."""
    months_re = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    ordinal = r"(?:st|nd|rd|th)?"
    patterns = [
        re.compile(rf"{months_re}\s+{day}{ordinal}\s*,?\s*{year}", re.I),
        re.compile(rf"{months_re}\s+{day}{ordinal}\s+,?\s*{year}", re.I),
        re.compile(rf"\b{day}{ordinal}\s+{months_re}\s+{year}", re.I),
        re.compile(rf"\b{year}\s*[-/]\s*{month:02d}\s*[-/]\s*{day:02d}", re.I),
        re.compile(rf"\b{day:02d}\s*[./]\s*{month:02d}\s*[./]\s*{year}", re.I),
        re.compile(rf"\b{month:02d}\s*[./]\s*{day:02d}\s*[./]\s*{year}", re.I),
        re.compile(rf"\b{day}\s*[./]\s*{month}\s*[./]\s*{year}", re.I),
        re.compile(rf"\b{month}\s*/\s*{day}\s*/\s*{year}", re.I),
        re.compile(rf"\b{month:02d}\s*/\s*{day:02d}\s*/\s*{year}", re.I),
    ]
    for pat in patterns:
        if pat.search(text):
            return True
    return False


def normalize_and_dedupe_urls(site: str, links: List[str]) -> List[str]:
    """Normalize URLs per site and return unique list. dice.fm: only event URL (slug after /event/); ra.co: base URL without query."""
    seen = set()
    out = []
    for link in links:
        if not link:
            continue
        parsed = urlparse(link)
        if site == "dice.fm":
            # Only https://dice.fm/event/{slug} — slug is path after /event/ (hyphen-delimited), no query
            if "/event/" not in parsed.path:
                continue
            path = parsed.path.rstrip("/")
            if path.startswith("/event/"):
                slug = path[len("/event/"):].split("/")[0]
                if slug:
                    canonical = urlunparse((parsed.scheme or "https", parsed.netloc or "dice.fm", f"/event/{slug}", "", "", ""))
                    if canonical not in seen:
                        seen.add(canonical)
                        out.append(canonical)
        elif site == "ra.co":
            # Only https://ra.co/events/#### — strip query and any path after event id
            if "/events/" not in parsed.path:
                continue
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "events" and parts[1].isdigit():
                path = f"/events/{parts[1]}"
                canonical = urlunparse((parsed.scheme or "https", parsed.netloc or "ra.co", path, "", "", ""))
                if canonical not in seen:
                    seen.add(canonical)
                    out.append(canonical)
        else:
            if link not in seen:
                seen.add(link)
                out.append(link)
    return out


def open_url_in_chrome(url: str) -> None:
    """Open URL in Google Chrome. Handles macOS and Windows."""
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["/usr/bin/open", "-a", "Google Chrome", url], check=False)
    elif system == "Windows":
        localappdata = os.environ.get("LOCALAPPDATA", "")
        chrome = os.path.join(
            localappdata,
            "Google", "Chrome", "Application", "chrome.exe",
        )
        if localappdata and os.path.isfile(chrome):
            subprocess.run([chrome, url], check=False)
        else:
            # Fallback: default browser (often Chrome if set)
            webbrowser.open(url)
    # else: no-op on other platforms


def search_serper(api_key: str, query: str) -> dict:
    """POST to Serper search API; return JSON response."""
    data = json.dumps({"q": query}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--open"]
    open_in_chrome = "--open" in sys.argv
    short_file = args[0] if args else "searchy.txt"

    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        sys.exit("Error: SERPER_API_KEY not set. Add it to .env or set the environment variable.")

    try:
        with open(short_file):
            pass
    except FileNotFoundError:
        sys.exit(f"Error: File '{short_file}' not found.")

    content = build_search_content(short_file)
    if not content:
        sys.exit(f"Error: '{short_file}' is empty or has no content.")

    year, month, day = extract_date(short_file)

    for site in SITES:
        query = f"site:{site} {content}"
        try:
            resp = search_serper(api_key, query)
        except Exception as e:
            print(f"--- site:{site} (request failed: {e}) ---", file=sys.stderr)
            continue
        organic = resp.get("organic") or []
        matched_links = []
        for item in organic:
            title = item.get("title") or ""
            snippet = item.get("snippet") or ""
            link = item.get("link") or ""
            text = (title + " " + snippet).replace("\n", " ")
            if date_matches_text(year, month, day, text):
                matched_links.append(link)
        unique_urls = normalize_and_dedupe_urls(site, matched_links)
        if unique_urls:
            print(f"--- site:{site} (date {year}-{month}-{day} matches) ---")
            for url in unique_urls:
                print(url)
                if open_in_chrome:
                    open_url_in_chrome(url)


if __name__ == "__main__":
    main()
