from datetime import datetime
import re

from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from dateutil.parser import parse as dateparse
from dateutil.parser import parse as dateparse
from playwright.async_api import Browser, Playwright

from scraper.interface import MediaScraper
from scraper.models import Media

class CivicClerkScraper(MediaScraper):
	def __init__(self, url: str):
		self.url = url
		self.base_url = "https://charlestonwv.portal.civicclerk.com"

	async def scrape(self, browser: Browser, start_date: datetime, end_date: datetime) -> list[Media]:
		# Create a new browser page
		page = await browser.new_page()
		
		try:
			# Navigate to the target page
			await page.goto(self.url)
			await page.wait_for_load_state('networkidle')
			html = await page.content()

			medias: set[Media] = set()

			# Fill the available date filters
			await page.fill("input[aria-label='From Date']", start_date.strftime("%m/%d/%Y"))
			await page.fill("input[aria-label='To Date']", end_date.strftime("%m/%d/%Y"))
			await page.wait_for_load_state('networkidle')
			
			# Click on the scrollable list of events to make keyboard navigation possible
			await page.click("div[aria-describedby='Event-list']")

			while True:
				# Check if the target text appears, indicating that there are no more events to load
				if await page.locator("p", has_text="There are no upcoming events").count() > 0:
					break

				for _ in range(10):
					await page.keyboard.press("ArrowDown")
				await page.wait_for_load_state('networkidle')
			
			# Get the updated page content
			html = await page.content()
			soup = BeautifulSoup(html, 'html.parser')

			# Find the event list container ul and extract the list items
			event_list = soup.find("ul", {"aria-labelledby": "Event-list-listSubheader-0"}).find_all("li")
			for event in event_list:
				title = event.find("h3").get_text(strip=True)

				date_text = event.find("div", {"data-testid": "dateDetails"}).getText(strip=False, separator=" ")
				date =  dateparse(date_text)

				# Actions contains the video link
				actions = event.find("div", {"id": re.compile(r"^listItemSecondaryAction")}).find_all("a")
				media_url: str = ""
				if actions == []:
					continue
				for action in actions:
					media_url = f"{self.base_url}{action['href']}"

				medias.add(Media(title=title, url=media_url, date=date, source_type="video"))
			
			await page.close()
			return list(medias)
		except Exception as e:
			await page.close()
			raise e

