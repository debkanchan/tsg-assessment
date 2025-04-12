from datetime import datetime
import re
import time

from bs4 import BeautifulSoup
from playwright.async_api import Browser

from scraper.interface import MediaScraper
from scraper.models import Media

class FacebookScraper(MediaScraper):
	def __init__(self, url: str):
		self.url = url
	
	async def scrape(self, browser: Browser, start_date: datetime, end_date: datetime) -> list[Media]:
		# Create a new browser page
		page = await browser.new_page()

		# Navigate to the target page
		await page.goto(self.url)
		await page.wait_for_load_state()
		html = await page.content()
		soup = BeautifulSoup(html, 'html.parser')
		await page.locator("div[aria-label=Close]").click()

		# This follows the XPath '//*[@id="mount_0_0_po"]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div[2]/div/div/div/div[2]/div/div' to the video container
		# contianer = soup.find("div", id=re.compile("^mount_0_0")).find("div").find_all("div", recursive=False)[0].find("div").find_all("div", recursive=False)[2].find("div").find("div").find_all("div", recursive=False)[0].find_all("div", recursive=False)[0].find("div").find("div").find_all("div", recursive=False)[3].find("div").find_all("div", recursive=False)[1].find("div").find("div").find("div").find_all("div", recursive=False)[1].find("div").find("div")

		# This directly searches for the container using the text "Videos" inside a span though there are 3 of them
		contianer = soup.find_all("span", text="Videos")[2].find_parent("div").find_parent("div").find_all("div", recursive=False)[1].find("div").find("div")

		print(contianer.get_text(strip=True, separator=" | "))
		return []