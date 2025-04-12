from bs4 import BeautifulSoup
from playwright.async_api import Browser

from downloader.downloaders import utils

async def civic_clerk_download(browser: Browser, url: str) -> str | None:
	# Create a new browser page
	page = await browser.new_page()

	# Navigate to the target page
	await page.goto(url)
	await page.wait_for_load_state('networkidle')

	html = await page.content()
	soup = BeautifulSoup(html, 'html.parser')

	# Try to find and click the play button
	play_button = page.locator(
			'div[aria-label="play" i]'
	)

	await play_button.nth(0).click()

	await page.wait_for_selector('video[src]', timeout=10000)

	html = await page.content()
	soup = BeautifulSoup(html, 'html.parser')

	tag = soup.find("video")
	url = tag.get("src")

	if utils.try_download(url):
		await page.close()
		return url

	await page.close()
	return None


def find_all_video_urls(soup: BeautifulSoup):
	urls = []
	for tag in soup.find_all("video"):
			src = tag.get("src")
			if src and utils.is_valid_video_source_url(str(src)):
					urls.append(src)
	
	return urls


# async def find_download_button_or_link(page: Page):
# 	# Locator for <button> elements with 'Download' in attributes or text
# 	button_locator = page.locator(
# 			'button[class*="download" i], button[id*="download" i], button[aria-label*="download" i], button[title*="download" i]'
# 	).or_(
# 			page.locator('button').filter(has_text=re.compile("Download", re.IGNORECASE))
# 	)

# 	# Locator for <a> elements with 'Download' in attributes or text
# 	link_locator = page.locator(
# 			'a[class*="download" i], a[id*="download" i], a[aria-label*="download" i], a[title*="download" i]'
# 	).or_(
# 			page.locator('a').filter(has_text=re.compile("Download", re.IGNORECASE))
# 	)