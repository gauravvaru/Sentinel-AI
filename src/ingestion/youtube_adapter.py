import os
import uuid
import logging
from datetime import datetime, timezone
from typing import AsyncGenerator, List
import asyncio

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser

from src.ingestion.base import IngestionSource
from src.models.event import SocialEvent

logger = logging.getLogger(__name__)

class YouTubeSource(IngestionSource):
    def __init__(self, video_ids: List[str], limit_per_video: int = 100):
        self.video_ids = video_ids
        self.limit_per_video = limit_per_video
        
        load_dotenv()
        self.api_key = os.environ.get("YOUTUBE_API_KEY")
        
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY must be set in the environment.")
            
        # Build the youtube client
        # Note: googleapiclient is synchronous, we will wrap it in asyncio.to_thread if needed,
        # but for simple generators, we can just yield. For production async, we'd use aiohttp directly 
        # or run inside an executor, but we'll use asyncio.to_thread here to keep it non-blocking.
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    async def fetch(self) -> AsyncGenerator[SocialEvent, None]:
        for video_id in self.video_ids:
            next_page_token = None
            fetched_count = 0
            
            while fetched_count < self.limit_per_video:
                try:
                    # Run the synchronous API call in a thread to avoid blocking the event loop
                    request = self.youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=min(100, self.limit_per_video - fetched_count),
                        pageToken=next_page_token,
                        textFormat="plainText"
                    )
                    
                    response = await asyncio.to_thread(request.execute)
                    
                    items = response.get("items", [])
                    if not items:
                        break
                        
                    for item in items:
                        comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
                        
                        # Parse timestamp
                        event_time = parser.parse(comment_snippet["publishedAt"])
                        if event_time.tzinfo is None:
                            event_time = event_time.replace(tzinfo=timezone.utc)
                        else:
                            event_time = event_time.astimezone(timezone.utc)
                            
                        raw_payload = {
                            "video_id": video_id,
                            "author_display_name": comment_snippet.get("authorDisplayName"),
                            "author_channel_url": comment_snippet.get("authorChannelUrl"),
                            "like_count": comment_snippet.get("likeCount", 0),
                            "reply_count": item["snippet"].get("totalReplyCount", 0)
                        }
                        
                        event = SocialEvent(
                            id=str(uuid.uuid4()),
                            platform="youtube",
                            event_type="comment",
                            platform_event_id=item["id"],
                            user_id=comment_snippet.get("authorChannelId", {}).get("value", "unknown"),
                            text=comment_snippet.get("textDisplay", ""),
                            event_time=event_time,
                            ingested_at=datetime.now(timezone.utc),
                            likes=raw_payload["like_count"],
                            replies=raw_payload["reply_count"],
                            raw_payload=raw_payload
                        )
                        yield event
                        fetched_count += 1
                        
                        if fetched_count >= self.limit_per_video:
                            break
                            
                    next_page_token = response.get("nextPageToken")
                    if not next_page_token:
                        break
                        
                except HttpError as e:
                    logger.error(f"YouTube API HttpError for video {video_id}: {e.status_code}")
                    if e.status_code in [403, 429]:
                        logger.warning("Quota exceeded or rate limited. Backing off.")
                        await asyncio.sleep(60) # Simple backoff
                    else:
                        break # Skip this video on other errors
                except Exception as e:
                    logger.error(f"Error fetching from YouTube for video {video_id}: {e}")
                    break # Skip video on unknown error
