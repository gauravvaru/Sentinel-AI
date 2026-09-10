import asyncio
import os
from src.ingestion.csv_adapter import CSVSource
from src.db.session import async_session
from src.db.models import SocialEventModel

async def ingest_sample():
    sample_path = "data/samples/sentiment140_sample.csv"
    if not os.path.exists(sample_path):
        print(f"Sample file {sample_path} not found")
        return

    adapter = CSVSource(sample_path)
    
    async with async_session() as session:
        async for event in adapter.fetch():
            # Check if exists
            db_event = SocialEventModel(
                id=event.id,
                platform=event.platform,
                event_type=event.event_type,
                platform_event_id=event.platform_event_id,
                user_id=event.user_id,
                text=event.text,
                event_time=event.event_time,
                ingested_at=event.ingested_at,
                raw_payload=event.raw_payload
            )
            session.add(db_event)
        
        await session.commit()
        print("Sample records ingested successfully.")

if __name__ == "__main__":
    asyncio.run(ingest_sample())
