import asyncio
import argparse
import json
from datetime import datetime
from typing import Type

from playwright.async_api import async_playwright

from scraper import models
from scraper.interface import MediaScraper
from scraper.models import Media
from scraper.scrapers.civicclerk import CivicClerkScraper
from scraper.scrapers.facebook import FacebookScraper
from scraper.scrapers.lansdale import LansdaleScraper
from scraper.scrapers.youtube import YoutubeScraper

from tld import get_tld

# A mapping of domain names to scraper classes
scraper_for_domain: dict[str, Type[MediaScraper]] = {
	"youtube.com": YoutubeScraper,
	"facebook.com": FacebookScraper,
	"civicclerk.com": CivicClerkScraper,
	"lansdale.org": LansdaleScraper,
}

# Get the correct scraper implementation for a given URL
def get_scraper(url: str) -> MediaScraper:
	"""
	Get the correct scraper implementation for a given URL.

	:param url: The URL to scrape.
	:return: The scraper implementation for the given URL.
	:raises ValueError: If no scraper is found for the given URL.
	"""

	# Get the domain name from the URL. Example: https://www.youtube.com -> youtube.com
	tld = get_tld(url, as_object=True)
	domain = str(tld.fld)

	scrape = scraper_for_domain.get(domain)
	if scrape is None:
		raise ValueError(f"No scraper found for domain: {domain}")
	return scrape(url)

async def scrape_urls(base_urls: list[str], start_date: datetime, end_date: datetime):
	"""
	Scrape URLs and return a list of ScrapeResult objects.

	This function creates a new browser and manages mutliple scrapers for each domain concurrently.
	It returns a list of ScrapeResult objects, which contain the base URL and a list of media objects.
	In case of an error, the scraper returns a BaseException object only for the corresponding domain.
	
	:param base_urls: A list of URLs to scrape.
	:param start_date: The start date for the scrape.
	:param end_date: The end date for the scrape.
	:return: A list of ScrapeResult objects.
	"""

	mediaLists: list[Media | BaseException] = []

	# Create a new browser
	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=False)
		tasks = []

		# For each URL, create a scraper and add it to the task list
		for base_url in base_urls:
			tasks.append(get_scraper(base_url).scrape(browser, start_date, end_date))

		# Wait for all scrapers to complete
		mediaLists = await asyncio.gather(*tasks, return_exceptions=True)
		
		await browser.close()
	
	result: list[models.ScrapeResult] = []

	for i, mediaListOrError in enumerate(mediaLists):
		if isinstance(mediaListOrError, Exception):
			print(f"Error scraping {base_urls[i]}: {mediaListOrError}")
			result.append(models.ScrapeResult(base_url=base_urls[i], error=mediaListOrError))
		else: 
			result.append(models.ScrapeResult(base_url=base_urls[i], medias=mediaListOrError))
	
	return result