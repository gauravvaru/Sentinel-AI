import pytest
import os
from src.ingestion.csv_adapter import CSVSource

@pytest.mark.asyncio
async def test_csv_ingestion():
    sample_path = "data/samples/sentiment140_sample.csv"
    if not os.path.exists(sample_path):
        pytest.skip(f"Sample file {sample_path} not found")

    adapter = CSVSource(sample_path)
    
    events = []
    async for event in adapter.fetch():
        events.append(event)
    
    assert len(events) > 0
    first_event = events[0]
    
    assert first_event.platform == "twitter"
    assert first_event.event_type == "post"
    assert first_event.user_id is not None
    assert first_event.text is not None
    assert first_event.platform_event_id is not None
    
    # Check timestamp parsing
    assert first_event.event_time is not None
    assert first_event.event_time.tzinfo is not None
    assert first_event.ingested_at is not None
    assert first_event.processed_at is None
    
    # Check raw payload
    assert "target" in first_event.raw_payload
    assert "flag" in first_event.raw_payload

    # Check deduplication context (platform_event_id uniqueness)
    ids = [e.platform_event_id for e in events]
    assert len(ids) == len(set(ids))
