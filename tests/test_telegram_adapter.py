import pytest
import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from src.ingestion.telegram_adapter import TelegramSource
from src.models.event import SocialEvent

@pytest.mark.asyncio
async def test_telegram_adapter():
    # Setup mock for the TelegramClient
    with patch("src.ingestion.telegram_adapter.TelegramClient") as MockClient:
        mock_client_instance = AsyncMock()
        MockClient.return_value = mock_client_instance
        
        # Mock connection and sign in
        mock_client_instance.connect = AsyncMock()
        mock_client_instance.is_user_authorized = AsyncMock(return_value=True)
        
        # Mock messages
        mock_message1 = MagicMock()
        mock_message1.id = 1
        mock_message1.sender_id = 12345
        mock_message1.text = "Hello Telegram"
        mock_message1.date = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
        
        mock_message2 = MagicMock()
        mock_message2.id = 2
        mock_message2.sender_id = 12345
        mock_message2.text = "Another message"
        mock_message2.date = datetime.datetime(2023, 1, 1, 12, 5, 0, tzinfo=datetime.timezone.utc)
        
        async def mock_iter_messages(*args, **kwargs):
            yield mock_message1
            yield mock_message2
            
        mock_client_instance.iter_messages = mock_iter_messages
        
        
        # Mock get_env to bypass actual env vars check if needed, but we can set env vars using monkeypatch
        # In this context, we will let TelegramSource handle it, we'll patch os.environ directly in actual tests if required
        
        with patch.dict("os.environ", {"TELEGRAM_API_ID": "123", "TELEGRAM_API_HASH": "hash", "TG_PHONE": "123456"}):
            adapter = TelegramSource("test_channel", limit=2)
            events = []
            async for event in adapter.fetch():
                events.append(event)
                
            assert len(events) == 2
            assert events[0].text == "Hello Telegram"
            assert events[0].platform == "telegram"
            assert events[0].platform_event_id == "1"
            assert events[1].text == "Another message"
            assert events[1].platform_event_id == "2"
