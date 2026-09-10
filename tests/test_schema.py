import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, SocialEventModel
import uuid

import pytest_asyncio

@pytest_asyncio.fixture
async def async_session():
    # Use an in-memory SQLite DB for testing the schema initially, 
    # but wait, TimescaleDB / postgresql features might fail on SQLite.
    # We should use a test postgres DB or just stick to standard SQLAlchemy for unit tests.
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_schema_timestamps(async_session):
    # Ensure event_time, ingested_at, processed_at are separate
    now = datetime.now(timezone.utc)
    event_id = str(uuid.uuid4())
    
    event = SocialEventModel(
        id=event_id,
        platform="test",
        event_type="post",
        platform_event_id="12345",
        user_id="user1",
        text="Hello world",
        event_time=now,
        ingested_at=now
    )
    
    async_session.add(event)
    await async_session.commit()
    
    # Fetch back
    fetched = await async_session.get(SocialEventModel, event_id)
    assert fetched is not None
    assert fetched.event_time == now
    assert fetched.ingested_at == now
    assert fetched.processed_at is None
    
    # Process it
    processed_time = datetime.now(timezone.utc)
    fetched.processed_at = processed_time
    await async_session.commit()
    
    fetched2 = await async_session.get(SocialEventModel, event_id)
    assert fetched2.processed_at == processed_time
    assert fetched2.event_time != fetched2.processed_at
