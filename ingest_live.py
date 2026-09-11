import asyncio
import argparse
import sys
import os
from sqlalchemy.dialects.postgresql import insert

from src.ingestion.telegram_adapter import TelegramSource
from src.ingestion.youtube_adapter import YouTubeSource
from src.db.session import async_session
from src.db.models import SocialEventModel

async def save_events(adapter, source_name):
    print(f"Starting ingestion from {source_name}...")
    inserted_count = 0
    duplicate_count = 0
    
    async with async_session() as session:
        async for event in adapter.fetch():
            stmt = insert(SocialEventModel).values(
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
            
            # Deduplicate by skipping if platform_event_id already exists
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['platform_event_id']
            )
            
            result = await session.execute(stmt)
            if result.rowcount > 0:
                inserted_count += 1
            else:
                duplicate_count += 1
                
        await session.commit()
    
    print(f"Finished ingestion from {source_name}. Inserted: {inserted_count}, Duplicates skipped: {duplicate_count}")


async def main():
    parser = argparse.ArgumentParser(description="Live Data Ingestion for SentinelAI")
    parser.add_argument("--telegram", type=str, help="Telegram channel username (e.g. 'telegram')")
    parser.add_argument("--youtube", type=str, help="YouTube Video ID")
    parser.add_argument("--limit", type=int, default=10, help="Limit number of items to fetch per source")
    
    args = parser.parse_args()
    
    if not args.telegram and not args.youtube:
        print("Please specify --telegram <channel> and/or --youtube <video_id>")
        sys.exit(1)
        
    tasks = []
    if args.telegram:
        tg_source = TelegramSource(target_entity=args.telegram, limit=args.limit)
        tasks.append(save_events(tg_source, f"Telegram ({args.telegram})"))
        
    if args.youtube:
        yt_source = YouTubeSource(video_ids=[args.youtube], limit_per_video=args.limit)
        tasks.append(save_events(yt_source, f"YouTube ({args.youtube})"))
        
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
