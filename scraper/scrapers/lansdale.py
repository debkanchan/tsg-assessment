from datetime import datetime

from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from dateutil.parser import parse as dateparse
from dateutil.parser import parse as dateparse
from playwright.async_api import Browser

from scraper.interface import MediaScraper
from scraper.models import Media

class LansdaleScraper(MediaScraper):
	def __init__(self, url: str):
		self.url = url
		self.base_url = "https://www.lansdale.org"

	async def scrape(self, browser: Browser, start_date: datetime, end_date: datetime) -> list[Media]:
		"""
		Scrape videos from a https://www.lansdale.org.

		:param browser: The Playwright browser instance.
		:param start_date: The start date for the scrape.
		:param end_date: The end date for the scrape.
		:return: A list of media objects.
		:raises ValueError: If the URL is not a valid URL.
		:raises Exception: If an error occurs during the scrape.
		"""
		# Create a new browser page
		page = await browser.new_page()

		try:
			# Navigate to the target page
			await page.goto(self.url)

			# Wait for the page content to load. VERY IMPORTANT!
			await page.wait_for_load_state('domcontentloaded')

			medias: set[Media] = set()

			html = await page.content()
			soup = BeautifulSoup(html, "html.parser")

			# Find the number of pages
			pages = soup.find("p", {"class": "pagination"}).get_text(strip=True, separator="|")
			total_pages = pages.split("|")[-1].strip()

			# We will visit this url once all the other pages except the landning page have been scraped
			sibling_url: str = ""

			# Loop through all the pages. Start at Page 1 and go up to the total number of pages.
			for page_num in range(1, int(total_pages)+1):
				# Get the updated page content
				html = await page.content()
				soup = BeautifulSoup(html, "html.parser")

				# Find all the video links on the page
				video_urls = soup.find("div", {"id": "ctl00_ctl00_MainContent_ModuleContent_ctl00_videoListingControl_UpdatePanelListing"}).find_all("a")

				reached_start_date = False

				for video_url in video_urls:
					# Ensure the link is a valid video link
					if video_url.get("href") is not None and video_url["href"].startswith("/CivicMedia"):
						# If we haven't set the sibling url yet, set it
						if sibling_url == "":
							sibling_url = f"{self.base_url}{video_url['href']}"

						page_url = f"{self.base_url}{video_url['href']}"
						media = await self._scrape(browser, page_url)

						if media.date < start_date:
							reached_start_date = True
							break
						
						if media.date > end_date:
							continue

						medias.add(media)
					else:
						continue
				
				if reached_start_date:
					break

				if page_num == int(total_pages):
					break
				
				# Find and click the next page link
				await page.locator('p.pagination span a', has_text=f"{page_num+1}").click()
				# Wait for the page to load
				await page.wait_for_load_state('networkidle')
				await page.wait_for_load_state('domcontentloaded')

				# Wait for the loader to disappear
				loader_div = page.locator("#divAjaxProgress")
				await loader_div.wait_for(state="visible")
				await loader_div.wait_for(state="hidden")


			# Now that we have scraped all the pages except the current page, visit the sibling page
			await page.goto(sibling_url)
			await page.wait_for_load_state('domcontentloaded')

			# Get the updated page content
			html = await page.content()
			soup = BeautifulSoup(html, "html.parser")

			# Find all the video links on the page
			video_urls = soup.find("div", {"id": "ctl00_ctl00_MainContent_ModuleContent_ctl00_videoListingControl_UpdatePanelListing"}).find_all("a")

			# If there are video links on the page, find the first one and scrape it
			if video_urls is not None and len(video_urls) > 0:
				video_url = video_urls[0]
				if video_url.get("href") is not None and video_url["href"].startswith("/CivicMedia"):
					page_url = f"{self.base_url}{video_url['href']}"
					media = await self._scrape(browser, page_url)
							
					if start_date >= media.date >= end_date:
						medias.add(media)
			
			await page.close()
			return list(medias)
		except Exception as e:
			await page.close()
			raise e

	async def _scrape(self, browser: Browser, page_url: str) -> Media:
		"""
		Scrape a single video on a https://www.lansdale.org page.

		:param browser: The Playwright browser instance.
		:param page_url: The URL of the page to scrape.
		:return: A media object.
		:raises ValueError: If the URL is not a valid URL.
		:raises Exception: If an error occurs during the scrape.
		"""
		page = await browser.new_page()
		await page.goto(page_url)
		await page.wait_for_load_state('domcontentloaded')

		html = await page.content()
		soup = BeautifulSoup(html, 'html.parser')

		title = soup.find("h2", {"id": "videoName"}).get_text(strip=True)

		# Find the div with the video metadata
		video_meta_container = soup.find("div", {"class": "videoMeta"})

		# A <dd> element holds the date
		date_text = video_meta_container.find("dd", {"class": "first"}).get_text(strip=True)
		date = dateparse(date_text)

		await page.close()
		return Media(title=title, url=page_url, date=date, source_type="video")



