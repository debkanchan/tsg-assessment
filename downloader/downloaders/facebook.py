from playwright.async_api import Browser

from downloader.downloaders.utils import try_download
	
async def facebook_download(browser: Browser, url: str ) -> str | None:
	if try_download(url):
		return url
	else:
		return None