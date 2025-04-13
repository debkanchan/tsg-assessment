from typing import Type
from downloader.interface import Downloader
from downloader.downloaders.youtube import youtube_download
from downloader.downloaders.facebook import facebook_download
from downloader.downloaders.generic import generic_download
from downloader.downloaders.zoom import zoom_download
from downloader.downloaders.civicclerk import civic_clerk_download
from playwright.async_api import async_playwright
import asyncio
from tld import get_tld

downloader_for_domain: dict[str, Type[Downloader]] = {
	"youtube.com": youtube_download,
	"facebook.com": facebook_download,
	"zoomgov.com": zoom_download,
	"civicclerk.com": civic_clerk_download,
}

def get_downloader(url: str) -> Downloader:
	tld = get_tld(url, as_object=True)
	domain = str(tld.fld)
	downloader = downloader_for_domain.get(domain)
	if downloader is None:
		print(f"No downloader found for {domain}")
		print("Using generic downloader")
		downloader = generic_download

	return downloader

async def download_urls(urls: list[str]) -> list[str | None | BaseException]:
	async with async_playwright() as p:
		# TODO: Some websites have flash players for which we need to use chroms but then it breaks "networkidle" load event
		# browser = await p.chromium.launch(headless=False, channel="chrome")
		browser = await p.chromium.launch(headless=False)

		tasks = []

		for url in urls:
			download = get_downloader(url)
			tasks.append(download(browser, url))

		links: list[str | None | BaseException] = await asyncio.gather(*tasks, return_exceptions=True)
		
		await browser.close()
	
	return links