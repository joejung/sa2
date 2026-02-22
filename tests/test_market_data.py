import pytest
import asyncio
from sahelper.services.market_data import MarketDataService

@pytest.mark.asyncio
async def test_market_data_service_initialization():
    service = MarketDataService()
    assert len(service.tickers) > 0
    for t in service.tickers:
        assert "history" in t
        assert len(t["history"]) > 0 # At least some data exists

@pytest.mark.asyncio
async def test_market_data_update_logic():
    service = MarketDataService()
    
    # Capture the emitted signal
    emitted_data = []
    def on_updated(data):
        emitted_data.append(data)
    
    service.data_updated.connect(on_updated)
    
    # Run one step of the feed
    task = asyncio.create_task(service.run_live_feed())
    
    # Wait for at least one emission
    for _ in range(30): # Allow more time for real network calls
        if emitted_data:
            break
        await asyncio.sleep(1.0)
    
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    assert len(emitted_data) >= 1
    update = emitted_data[0]
    assert len(update) == len(service.tickers)
    for t in update:
        assert "history" in t
        assert len(t["history"]) >= 1 # Should have history from fetch_history
        assert isinstance(t["history"], list)
