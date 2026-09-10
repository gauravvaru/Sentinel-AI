import csv
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from dateutil import parser
import pytz

from src.ingestion.base import IngestionSource
from src.models.event import SocialEvent

class CSVSource(IngestionSource):
    def __init__(self, file_path: str):
        self.file_path = file_path

    async def fetch(self) -> AsyncGenerator[SocialEvent, None]:
        # tzinfos for dateutil parser to handle PDT/PST etc.
        tzinfos = {"PDT": pytz.timezone("US/Pacific"), "PST": pytz.timezone("US/Pacific")}
        
        with open(self.file_path, 'r', encoding='latin-1') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 6:
                    continue
                
                # Sentiment140 format: target, id, date, flag, user, text
                platform_id = row[1]
                raw_date = row[2]
                user = row[4]
                text = row[5]

                try:
                    event_time = parser.parse(raw_date, tzinfos=tzinfos)
                    if event_time.tzinfo is None:
                        event_time = event_time.replace(tzinfo=timezone.utc)
                    else:
                        event_time = event_time.astimezone(timezone.utc)
                except Exception:
                    event_time = datetime.now(timezone.utc)
                
                event = SocialEvent(
                    id=str(uuid.uuid4()),
                    platform="twitter",
                    event_type="post",
                    platform_event_id=platform_id,
                    user_id=user,
                    text=text,
                    event_time=event_time,
                    ingested_at=datetime.now(timezone.utc),
                    raw_payload={
                        "target": row[0],
                        "flag": row[3]
                    }
                )
                yield event
