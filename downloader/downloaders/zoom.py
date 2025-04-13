from playwright.async_api import Browser
from bs4 import BeautifulSoup
import io
from . import utils

async def zoom_download(browser: Browser, url: str) -> str | None:
	# Create a new browser page
	context = await browser.new_context()
	page = await context.new_page()

	# Navigate to the target page
	await page.goto(url)
	# Wait for all requests to finish
	await page.wait_for_load_state('networkidle')
	print("resolved")

	# Get the updated page content
	html = await page.content()
	soup = BeautifulSoup(html, 'html.parser')

	# Find the video element
	video_url = soup.find("video").get("src")

	print(video_url)

	if video_url is None:
		return None

	video_url = str(video_url)

	# Get the cookies from the page
	cookies = await context.cookies()
	
	# Convert the cookies to Netscape HTTP Cookie File format
	cookies_txt = "".join(utils.gen_cookies_txt(cookies))

	if utils.try_download(video_url, headers={
			"referer": "https://www.zoomgov.com/",
		}, cookies=io.StringIO(cookies_txt)):
		return video_url

	await page.close()
	return video_url
