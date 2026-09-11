import pytest
import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from src.ingestion.youtube_adapter import YouTubeSource

@pytest.mark.asyncio
async def test_youtube_adapter():
    with patch("src.ingestion.youtube_adapter.build") as mock_build, \
         patch.dict("os.environ", {"YOUTUBE_API_KEY": "fake_key"}):
        
        # Setup mock YouTube client
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        
        # Mock the commentThreads().list().execute() response
        mock_list = MagicMock()
        mock_youtube.commentThreads().list.return_value = mock_list
        
        # We need execute to return our dict, but wait, the execute is wrapped in asyncio.to_thread
        # So it's executed as a normal sync function that returns a dictionary.
        mock_list.execute.return_value = {
            "items": [
                {
                    "id": "comment_1",
                    "snippet": {
                        "topLevelComment": {
                            "snippet": {
                                "authorDisplayName": "User 1",
                                "authorChannelUrl": "http://channel1",
                                "likeCount": 10,
                                "publishedAt": "2023-01-01T12:00:00Z",
                                "authorChannelId": {"value": "ch1"},
                                "textDisplay": "Hello YouTube",
                            }
                        },
                        "totalReplyCount": 2
                    }
                },
                {
                    "id": "comment_2",
                    "snippet": {
                        "topLevelComment": {
                            "snippet": {
                                "authorDisplayName": "User 2",
                                "authorChannelUrl": "http://channel2",
                                "likeCount": 5,
                                "publishedAt": "2023-01-01T12:05:00Z",
                                "authorChannelId": {"value": "ch2"},
                                "textDisplay": "Another comment",
                            }
                        },
                        "totalReplyCount": 0
                    }
                }
            ],
            "nextPageToken": None
        }
        
        adapter = YouTubeSource(video_ids=["video_id_1"], limit_per_video=2)
        
        events = []
        async for event in adapter.fetch():
            events.append(event)
            
        assert len(events) == 2
        assert events[0].platform == "youtube"
        assert events[0].platform_event_id == "comment_1"
        assert events[0].text == "Hello YouTube"
        assert events[0].likes == 10
        assert events[0].replies == 2
        
        assert events[1].platform_event_id == "comment_2"
        assert events[1].text == "Another comment"
        
