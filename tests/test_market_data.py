import pytest
import asyncio
from sahelper.services.market_data import MarketDataService

@pytest.mark.asyncio
async def test_market_data_service_initialization():
    service = MarketDataService()
    assert len(service.tickers) > 0
    for t in service.tickers:
        assert "history" in t
        assert len(t["history"]) == 50 # Pre-populated in __init__

@pytest.mark.asyncio
async def test_market_data_update_logic():
    service = MarketDataService()
    
    # Capture the emitted signal
    emitted_data = []
    def on_updated(data):
        emitted_data.append(data)
    
    service.data_updated.connect(on_updated)
    
    # Run one step of the feed (manually trigger what run_live_feed does)
    # Since run_live_feed is an infinite loop, we just call the core logic if possible
    # or just run it and cancel after one emission.
    
    task = asyncio.create_task(service.run_live_feed())
    
    # Wait for at least one emission (it emits every 2s)
    for _ in range(10): # 10*0.5s = 5s max wait
        if emitted_data:
            break
        await asyncio.sleep(0.5)
    
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
        assert len(t["history"]) > 50 # 50 + at least one update
        assert isinstance(t["history"], list)
