"""
Official NSE / BSE IPO Data Provider.

Strictly connects only to official exchange endpoints (NSE India and BSE India).
Does NOT use any third-party websites or scrapers.

If official exchange endpoints are unreachable or unavailable, fails gracefully
and returns empty lists, allowing the service layer to keep existing data as-is.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

_NSE_BASE = "https://www.nseindia.com"
_NSE_UPCOMING_URL = "https://www.nseindia.com/api/upcoming-issues"
_NSE_CURRENT_URL = "https://www.nseindia.com/api/ipo-current-issue"


def _parse_price_range(price_str: Optional[str]) -> tuple[Optional[float], Optional[float]]:
    """Extract low and high prices from strings like 'Rs.290 to Rs.302' or 'Rs.150'."""
    if not price_str:
        return None, None
    clean = price_str.replace(",", "").replace("Rs.", "").replace("₹", "")
    nums = re.findall(r"(\d+(?:\.\d+)?)", clean)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    elif len(nums) == 1:
        val = float(nums[0])
        return val, val
    return None, None


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse dates in formats like '25-Sep-2026', '25-09-2026', '2026-09-25'."""
    if not date_str:
        return None
    for fmt in ("%d-%b-%Y", "%d-%m-%Y", "%Y-%m-%d", "%b %d, %Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


class NseBseIpoProvider:
    """Official exchange IPO provider querying NSE India."""

    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    def _get_nse_session(self) -> Optional[requests.Session]:
        """Establish a session with NSE India and obtain cookies."""
        try:
            session = requests.Session()
            session.headers.update(_HEADERS)
            resp = session.get(_NSE_BASE, timeout=self.timeout)
            if resp.status_code == 200:
                return session
            logger.warning("NSE homepage handshake returned status %d", resp.status_code)
            return None
        except Exception as exc:
            logger.warning("Could not establish session with NSE: %s", exc)
            return None

    def fetch_all_ipos(self) -> List[Dict[str, Any]]:
        """
        Fetch current and upcoming IPO issues directly from NSE India.
        Strictly queries only official exchange endpoints.
        Returns empty list if endpoints are unavailable or blocked.
        """
        session = self._get_nse_session()
        if not session:
            logger.warning("NSE session unavailable; keeping existing IPO data as-is.")
            return []

        results: List[Dict[str, Any]] = []
        seen_symbols = set()

        # 1. Fetch upcoming issues (contains both 'active' and 'forthcoming')
        try:
            resp = session.get(_NSE_UPCOMING_URL, timeout=self.timeout)
            if resp.status_code == 200:
                payload = resp.json()
                for bucket in ("forthcoming", "active"):
                    for item in payload.get(bucket, []):
                        d = item.get("data", {})
                        sym = (d.get("symbol") or item.get("symbol") or "").upper().strip()
                        if not sym or sym in seen_symbols:
                            continue
                        seen_symbols.add(sym)

                        company_name = d.get("companyName") or item.get("name") or sym
                        series = d.get("series", "EQ")
                        exchange = "sme" if str(series).upper() == "SME" else "mainboard"
                        p_low, p_high = _parse_price_range(d.get("issuePrice"))
                        issue_dt = _parse_date(d.get("issueStartDate") or item.get("startDate"))

                        shares = None
                        if d.get("issueSize"):
                            try:
                                shares = int(d.get("issueSize"))
                            except (ValueError, TypeError):
                                pass

                        results.append({
                            "company_name": company_name,
                            "symbol": sym,
                            "exchange": exchange,
                            "issue_date": issue_dt or datetime.now(timezone.utc),
                            "price_range_low": p_low,
                            "price_range_high": p_high,
                            "total_shares": shares,
                            "listing_price": None,
                            "underwriters": "NSE Registered Book Running Lead Managers",
                            "status": "upcoming",
                        })
        except Exception as exc:
            logger.warning("Failed querying NSE upcoming issues: %s", exc)

        # 2. Fetch current issues as well to complement
        try:
            resp = session.get(_NSE_CURRENT_URL, timeout=self.timeout)
            if resp.status_code == 200:
                items = resp.json()
                if isinstance(items, list):
                    for d in items:
                        sym = (d.get("symbol") or "").upper().strip()
                        if not sym or sym in seen_symbols:
                            continue
                        seen_symbols.add(sym)

                        company_name = d.get("companyName") or sym
                        series = d.get("series", "EQ")
                        exchange = "sme" if str(series).upper() == "SME" else "mainboard"
                        p_low, p_high = _parse_price_range(d.get("issuePrice"))
                        issue_dt = _parse_date(d.get("issueStartDate"))

                        shares = None
                        if d.get("issueSize"):
                            try:
                                shares = int(d.get("issueSize"))
                            except (ValueError, TypeError):
                                pass

                        results.append({
                            "company_name": company_name,
                            "symbol": sym,
                            "exchange": exchange,
                            "issue_date": issue_dt or datetime.now(timezone.utc),
                            "price_range_low": p_low,
                            "price_range_high": p_high,
                            "total_shares": shares,
                            "listing_price": None,
                            "underwriters": "NSE Registered Book Running Lead Managers",
                            "status": "upcoming",
                        })
        except Exception as exc:
            logger.warning("Failed querying NSE current issues: %s", exc)

        logger.info("Fetched %d IPO records directly from official NSE endpoints", len(results))
        return results


# Module singleton
nse_bse_ipo_provider = NseBseIpoProvider()
