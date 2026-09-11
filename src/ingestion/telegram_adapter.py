import os
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
import logging

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import FloodWaitError
import asyncio

from src.ingestion.base import IngestionSource
from src.models.event import SocialEvent

logger = logging.getLogger(__name__)

class TelegramSource(IngestionSource):
    def __init__(self, target_entity: str, limit: int = 100):
        self.target_entity = target_entity
        self.limit = limit
        
        load_dotenv()
        self.api_id = os.environ.get("TELEGRAM_API_ID")
        self.api_hash = os.environ.get("TELEGRAM_API_HASH")
        self.session_name = os.environ.get("TELEGRAM_SESSION_NAME", "sentinel_session")
        
        if not self.api_id or not self.api_hash:
            raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in the environment.")
            
        self.client = TelegramClient(self.session_name, int(self.api_id), self.api_hash)

    async def fetch(self) -> AsyncGenerator[SocialEvent, None]:
        # Connect to Telegram
        await self.client.start()
        
        count = 0
        try:
            # We iterate over messages. Telethon handles pagination internally.
            async for message in self.client.iter_messages(self.target_entity, limit=self.limit):
                if not message.text:
                    continue  # Skip messages without text (e.g., photos only)
                    
                event_time = message.date
                if event_time.tzinfo is None:
                    event_time = event_time.replace(tzinfo=timezone.utc)
                else:
                    event_time = event_time.astimezone(timezone.utc)
                    
                sender_id = str(message.sender_id) if message.sender_id else self.target_entity
                
                # Extract some useful metadata
                raw_payload = {
                    "views": message.views,
                    "forwards": message.forwards,
                    "post_author": message.post_author,
                    "target_entity": self.target_entity,
                    "reply_to_msg_id": message.reply_to_msg_id
                }
                
                event = SocialEvent(
                    id=str(uuid.uuid4()),
                    platform="telegram",
                    event_type="post",
                    platform_event_id=str(message.id),
                    user_id=sender_id,
                    text=message.text,
                    event_time=event_time,
                    ingested_at=datetime.now(timezone.utc),
                    raw_payload=raw_payload
                )
                yield event
                count += 1
                
        except FloodWaitError as e:
            logger.warning(f"Rate limited by Telegram. Waiting for {e.seconds} seconds.")
            # We wait and maybe let the caller handle it.
            # If we wanted to be perfectly resilient inside the generator, we could sleep and resume,
            # but telethon handles small floods automatically. For big ones, we yield what we have and stop.
            
        except Exception as e:
            logger.error(f"Error fetching from Telegram: {e}")
            # Do not crash the entire ingestion pipeline, just end the generator
            
        finally:
            await self.client.disconnect()
