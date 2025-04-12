from abc import ABC, abstractmethod
from datetime import datetime

from playwright.async_api import Browser, Playwright
from .models import Media

class MediaScraper(ABC):
  def __init__(self, url: str):
        self.url = url

  @abstractmethod
  async def scrape(self, browser: Browser, start_date: datetime, end_date: datetime) -> list[Media]:
    pass