from typing import Awaitable, Callable, List
from playwright.async_api import Browser

# class Downloader(ABC):
#   def __init__(self, url: str):
#     self.url = url

#   @abstractmethod
#   async def download(self, browser: Browser, urls: list[str]) -> list[str]:
#     pass

Downloader = Callable[[Browser, str], Awaitable[str | None]]
