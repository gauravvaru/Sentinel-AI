from typing import AsyncGenerator, Protocol
from src.models.event import SocialEvent

class IngestionSource(Protocol):
    async def fetch(self, *args, **kwargs) -> AsyncGenerator[SocialEvent, None]:
        ...
