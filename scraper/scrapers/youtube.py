from datetime import datetime
import re
import time

from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from dateutil.parser import parse as dateparse
from playwright.async_api import Browser

from scraper.interface import MediaScraper
from scraper.models import Media

class YoutubeScraper(MediaScraper):
	def __init__(self, url: str):
		self.url = url

	async def scrape(self, browser: Browser, start_date: datetime, end_date: datetime):
		"""
		Scrape videos from a YouTube URL.

		:param browser: The Playwright browser instance.
		:param start_date: The start date for the scrape.
		:param end_date: The end date for the scrape.
		:return: A list of media objects.
		:raises ValueError: If the URL is not a valid YouTube URL.
		:raises Exception: If an error occurs during the scrape.
		"""
		stream_match = re.match(r"https://www\.youtube\.com/([^/]+)/streams", self.url)
		# video_match = re.match(r"https://www\.youtube\.com/([^/]+)", url)

		if stream_match:
			results = await self.scrape_streams(browser, start_date, end_date)
			return results
		# elif video_match:
		# 	return scrape_video(url, start_date, end_date)
		else:
			raise ValueError("Invalid URL")

	async def scrape_streams(self, browser: Browser, start_date: datetime, end_date: datetime) -> list[Media]:
		"""
		Scrape streams from a YouTube URL.

		:param browser: The Playwright browser instance.
		:param start_date: The start date for the scrape.
		:param end_date: The end date for the scrape.
		:return: A list of media objects.
		:raises ValueError: If the URL is not a valid YouTube URL.
		:raises Exception: If an error occurs during the scrape.
		"""
		# Create a new browser page
		page = await browser.new_page()

		# Navigate to the target page
		await page.goto(self.url)

		# await page.wait_for_load_state('domcontentloaded')

		video_data: set[Media] = set()
		scraped_videos: set[str] = set()

		reached_start_date = False

		# Keep scrolling until we reach the start date
		while reached_start_date == False:
			# Get the latest HTML content
			html = await page.content()
			soup = BeautifulSoup(html, 'html.parser')

			# Find all videos on the page
			videos = soup.find("div", {"id": "contents"}).find_all("ytd-rich-item-renderer", recursive=True)

			for video in videos:
				try:
						# Find the link to the video
						link_tag = video.find("a", {"id": "video-title-link"})
						video_url = f"https://www.youtube.com{link_tag['href']}"

						# Skip if the video has already been scraped
						if video_url in scraped_videos:
								continue
						
						# Add the video to the set of scraped videos
						scraped_videos.add(video_url)

						full_title = video.find("yt-formatted-string", {"id": "video-title"}).get_text(strip=True)
						
						video_date = await self.get_date_from_video_player(browser, video_url)
						
						if video_date > end_date:
							continue

						if video_date < start_date:
								reached_start_date = True
								break
						
						video_data.add(Media(title=full_title, url=video_url, date=video_date, source_type="video"))

				except Exception as e:
						print(f"Error parsing video data: {e}")
			
			# Scroll down the page and wait for more videos to load
			for _ in range(50):
				await page.keyboard.press("ArrowDown")
			time.sleep(3)
		
		await page.close()
		return list(video_data)

	async def get_date_from_video_player(self, browser: Browser, url: str) -> datetime:
		"""
		Opens the video page and extracts the date from a tooltip in the description.

		:param browser: The Playwright browser instance.
		:param url: The URL of the video page.
		:return: The date of the video.
		:raises Exception: If an error occurs during the scrape. Closes the page if an error occurs.
		"""
		page = await browser.new_page()
		try: 

			# Navigate to the target page
			await page.goto(url)
			await page.wait_for_load_state('networkidle')

			html = await page.content()
			soup = BeautifulSoup(html, 'html.parser')

			description = soup.find("ytd-watch-info-text", {"id": "ytd-watch-info-text"})
			tooltip_text = description.find("div", {"id": "tooltip"}).get_text(strip=True)
			tooltip_text = tooltip_text.split("live on ")[1].strip()
			await page.close()
			return dateparse(tooltip_text)
		except Exception as e:
			await page.close()
			raise Exception(f"Error parsing date from video player: {e}")


