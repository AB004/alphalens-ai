"""Company-data service adapters.

Third-party market-data libraries are imported only when a company lookup is
requested, keeping unrelated API routes available if an optional adapter is
not installed or configured.
"""

from backend.services.company.provider import CompanyProvider


def get_default_provider() -> CompanyProvider:
    from backend.services.company.yahoo_provider import YahooFinanceProvider

    return YahooFinanceProvider()
