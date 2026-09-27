"""
Unit and Integration tests for Module 11.5: Home Page & Market Overview Backend APIs.
Tests all endpoints:
- Consolidated Master Dashboard
- Market Overview & Indices
- Advance / Decline Market Breadth
- Top Gainers / Losers (Multi-cap: Large, Mid, Small, All)
- Sector Performance & Sector Movers
- Quarterly Results (Upcoming & Recent)
- Watchlists (Default & Custom CRUD)
- 52-Week High / Low Breakouts
- Volume Shockers
- Market Sentiment Pulse
- Fallback & Seed Data Resilience (Never empty responses)
"""

from fastapi.testclient import TestClient
from backend.main import app


def test_home_dashboard_consolidated():
    """Verify consolidated home page payload returns 200 with all sections populated."""
    with TestClient(app) as client:
        response = client.get("/api/home")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "market_overview" in data
        assert "advance_decline" in data
        assert "market_movers" in data
        assert "sector_performance" in data
        assert "quarterly_results" in data
        assert "watchlist" in data
        assert "breakouts_52w" in data
        assert "volume_shockers" in data
        assert "market_sentiment" in data

        # Ensure no empty lists
        assert len(data["market_overview"]["indices"]) >= 4
        assert data["advance_decline"]["total_tracked"] > 0
        assert len(data["sector_performance"]) > 0
        assert len(data["watchlist"]["items"]) > 0


def test_market_overview():
    """Verify /api/home/overview returns indices and market trading status."""
    with TestClient(app) as client:
        response = client.get("/api/home/overview")
        assert response.status_code == 200
        data = response.json()

        assert "market_status" in data
        assert "status" in data["market_status"]
        assert "market_regime" in data
        assert "mood_score" in data
        assert isinstance(data["indices"], list)
        assert len(data["indices"]) >= 4

        symbols = [idx["symbol"] for idx in data["indices"]]
        assert "^NSEI" in symbols
        assert "^BSESN" in symbols


def test_advance_decline():
    """Verify /api/home/advance-decline returns breadth statistics and ratio."""
    with TestClient(app) as client:
        response = client.get("/api/home/advance-decline")
        assert response.status_code == 200
        data = response.json()

        assert data["advances"] >= 0
        assert data["declines"] >= 0
        assert data["total_tracked"] == data["advances"] + data["declines"] + data["unchanged"]
        assert data["advance_decline_ratio"] >= 0
        assert "breadth_sentiment" in data


def test_market_movers_multi_cap():
    """Verify /api/home/movers returns large, mid, small cap gainers/losers."""
    with TestClient(app) as client:
        # All caps view
        response = client.get("/api/home/movers?cap=all")
        assert response.status_code == 200
        data = response.json()

        assert "large_cap" in data
        assert "mid_cap" in data
        assert "small_cap" in data
        assert len(data["large_cap"]["gainers"]) > 0
        assert len(data["large_cap"]["losers"]) > 0
        assert len(data["mid_cap"]["gainers"]) > 0
        assert len(data["small_cap"]["gainers"]) > 0
        assert len(data["most_active"]) > 0

        # Specific cap filter: large cap
        resp_large = client.get("/api/home/movers?cap=large")
        assert resp_large.status_code == 200
        large_data = resp_large.json()
        assert large_data["cap_filter"] == "large"
        assert len(large_data["gainers"]) > 0
        for item in large_data["gainers"]:
            assert item["market_cap_category"] == "large"

        # Specific cap filter: mid cap
        resp_mid = client.get("/api/home/movers?cap=mid")
        assert resp_mid.status_code == 200
        mid_data = resp_mid.json()
        assert mid_data["cap_filter"] == "mid"
        for item in mid_data["gainers"]:
            assert item["market_cap_category"] == "mid"

        # Specific cap filter: small cap
        resp_small = client.get("/api/home/movers?cap=small")
        assert resp_small.status_code == 200
        small_data = resp_small.json()
        assert small_data["cap_filter"] == "small"
        for item in small_data["gainers"]:
            assert item["market_cap_category"] == "small"


def test_sector_performance_and_movers():
    """Verify /api/home/sectors and /api/home/sectors/{sector_name}/movers."""
    with TestClient(app) as client:
        # Heatmap
        response = client.get("/api/home/sectors")
        assert response.status_code == 200
        sectors = response.json()
        assert len(sectors) >= 5

        first_sector = sectors[0]
        assert "sector" in first_sector
        assert "average_change_percent" in first_sector
        assert "momentum" in first_sector
        assert "stock_count" in first_sector

        # Sector movers for Technology
        sec_name = "Technology"
        movers_resp = client.get(f"/api/home/sectors/{sec_name}/movers")
        assert movers_resp.status_code == 200
        sec_movers = movers_resp.json()
        assert sec_movers["sector"] == sec_name
        assert len(sec_movers["constituents"]) > 0


def test_quarterly_results_filtering():
    """Verify /api/home/quarterly-results for upcoming, recent, and all."""
    with TestClient(app) as client:
        # All
        resp_all = client.get("/api/home/quarterly-results?status=all")
        assert resp_all.status_code == 200
        data_all = resp_all.json()
        assert len(data_all["upcoming"]) > 0
        assert len(data_all["recent"]) > 0

        # Upcoming only
        resp_up = client.get("/api/home/quarterly-results?status=upcoming")
        assert resp_up.status_code == 200
        data_up = resp_up.json()
        assert len(data_up["upcoming"]) > 0
        assert len(data_up["recent"]) == 0
        for item in data_up["upcoming"]:
            assert item["is_upcoming"] is True

        # Recent only
        resp_rec = client.get("/api/home/quarterly-results?status=recent")
        assert resp_rec.status_code == 200
        data_rec = resp_rec.json()
        assert len(data_rec["recent"]) > 0
        assert len(data_rec["upcoming"]) == 0
        for item in data_rec["recent"]:
            assert item["is_upcoming"] is False
            assert item["verdict"] in ["Beat", "Met", "Miss"]


def test_watchlist_crud_lifecycle():
    """Verify watchlist retrieval, addition, and removal."""
    test_user = "test_user_42"
    with TestClient(app) as client:
        # Default home watchlist
        resp_default = client.get("/api/home/watchlist")
        assert resp_default.status_code == 200
        default_data = resp_default.json()
        assert default_data["total_items"] >= 5
        assert len(default_data["items"]) >= 5

        # Add to custom user watchlist
        add_payload = {
            "symbol": "TCS",
            "user_id": test_user,
            "category": "custom",
            "notes": "Testing watchlist entry",
        }
        add_resp = client.post("/api/home/watchlist", json=add_payload)
        assert add_resp.status_code == 201
        add_data = add_resp.json()
        assert add_data["item"]["symbol"] == "TCS"
        assert add_data["item"]["user_id"] == test_user

        # Fetch custom user watchlist
        user_wl_resp = client.get(f"/api/home/watchlist?user_id={test_user}")
        assert user_wl_resp.status_code == 200
        user_wl = user_wl_resp.json()
        assert user_wl["total_items"] == 1
        assert user_wl["items"][0]["symbol"] == "TCS"

        # Remove from watchlist
        del_resp = client.delete(f"/api/home/watchlist/TCS?user_id={test_user}")
        assert del_resp.status_code == 200
        assert del_resp.json()["removed"] is True

        # Confirm empty
        user_wl_after = client.get(f"/api/home/watchlist?user_id={test_user}").json()
        assert user_wl_after["total_items"] == 0


def test_52_week_high_low_and_volume_shockers():
    """Verify 52-week high/low breakouts and volume shockers endpoints."""
    with TestClient(app) as client:
        # 52-week
        hl_resp = client.get("/api/home/52-week-high-low?threshold_percent=5.0")
        assert hl_resp.status_code == 200
        hl_data = hl_resp.json()
        assert "near_52w_high" in hl_data
        assert "near_52w_low" in hl_data

        # Volume shockers
        vol_resp = client.get("/api/home/volume-shockers?min_ratio=1.2")
        assert vol_resp.status_code == 200
        vol_data = vol_resp.json()
        assert isinstance(vol_data, list)
        for item in vol_data:
            assert item["volume_surge_ratio"] >= 1.2


def test_market_sentiment_endpoint():
    """Verify /api/home/sentiment returns sentiment score and breakdown."""
    with TestClient(app) as client:
        resp = client.get("/api/home/sentiment")
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_sentiment" in data
        assert "sentiment_score" in data
        assert "positive_percentage" in data
        assert "negative_percentage" in data
