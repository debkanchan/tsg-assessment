from downloader.downloaders.utils import try_download
from downloader.interface import Downloader
import yt_dlp
from playwright.async_api import Browser
	
async def youtube_download(browser: Browser, url: str) -> str | None:
	if try_download(url):
		return url
	else:
		return None
	