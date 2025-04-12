import io
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.async_api import Browser, Page, Request, Response

from downloader.downloaders import utils

async def generic_download(browser: Browser, url: str) -> str | None:
	base_url = urlparse(url).netloc
	# Create a new browser page
	context = await browser.new_context()
	page = await context.new_page()
	
	requests: list[Request] = []
	responses: list[Response] = []

	page.on("request", lambda request: requests.append(request))
	page.on("response", lambda response: responses.append(response))

	# Navigate to the target page
	await page.goto(url)
	# await page.wait_for_load_state('networkidle')

	# Extract the cookies from the page
	cookies = await context.cookies()

	html = await page.content()
	soup = BeautifulSoup(html, 'html.parser')

	urls = [*find_all_video_urls(soup), *find_all_source_urls(soup), *find_all_iframe_urls(soup), *find_a_hrefs(soup, base_url), *find_all_response_urls(responses)]

	successful_url: str | None = None

	for url in urls:
		if url.startswith("https://") or url.startswith("http://"):
			if utils.try_download(url, cookies=io.StringIO("".join(utils.gen_cookies_txt(cookies)))):
				successful_url = url
				break

	if successful_url is not None:
		await page.close()
		return successful_url

	request_urls = find_all_request_urls(requests)

	for url, headers in request_urls.items():
		if utils.try_download(url, headers, cookies=io.StringIO("".join(utils.gen_cookies_txt(cookies)))):
			successful_url = url
			break
	
	if successful_url is not None:
		await page.close()
		return successful_url

	# Try to find and click the play button
	try:
		await find_and_click_play_button(page)
	except Exception as e:
		print(f"Error finding and clicking play button: {e}")

	# await page.wait_for_timeout(15*1000)

	html = await page.content()
	soup = BeautifulSoup(html, 'html.parser')

	# Try again after clicking the play button
	urls = [*find_all_video_urls(soup), *find_all_source_urls(soup), *find_all_iframe_urls(soup), *find_a_hrefs(soup, base_url), *find_all_response_urls(responses)]

	successful_url: str | None = None

	for url in urls:
		if url.startswith("https://") or url.startswith("http://"):
			if utils.try_download(url, cookies=io.StringIO("".join(utils.gen_cookies_txt(cookies)))):
				successful_url = url
				break

	if successful_url is not None:
		await page.close()
		return successful_url
	
	request_urls = find_all_request_urls(requests)

	for url, headers in request_urls.items():
		if utils.try_download(url, headers, cookies=io.StringIO("".join(utils.gen_cookies_txt(cookies)))):
			successful_url = url
			break

	await page.close()
	return successful_url

def find_all_video_urls(soup: BeautifulSoup):
	urls = []
	for tag in soup.find_all("video"):
			src = tag.get("src")
			if src and utils.is_valid_video_source_url(str(src)):
					urls.append(src)
	
	return urls

def find_a_hrefs(soup: BeautifulSoup, base_url: str):
	urls = []
	
	for tag in soup.find_all("a"):
			href = tag.get("href")
			if href and utils.is_valid_video_source_url(str(href)):
					urls.append(href)
			
			if href and href.startswith("/"):
					urls.append(f"{base_url}{href}")
	
	return urls

def find_all_iframe_urls(soup: BeautifulSoup):
	urls = []
	for tag in soup.find_all("iframe"):
			src = str(tag.get("src"))
			if src and utils.is_valid_video_source_url(src):
					urls.append(src)
	
	return urls

def find_all_source_urls(soup: BeautifulSoup):
	urls = []
	for tag in soup.find_all("source"):
			src = str(tag.get("src"))
			if src:
					urls.append(src)
	
	return urls

def find_all_request_urls(requests: list[Request]):
	urls: dict[str, dict[str, str]] = {}
	for request in requests:
		if utils.is_valid_video_source_url(request.url):
			urls[request.url] = request.headers
	
	return urls

def find_all_response_urls(responses: list[Response]):
	urls = []
	for response in responses:
		if utils.is_valid_video_source_url(response.url):
			urls.append(response.url)
	
	return urls

async def find_and_click_play_button(page: Page):
	# Locator for <button> elements with 'play' in attributes or text
	button_locator = page.locator(
			'button[class*="play" i], button[id*="play" i], button[aria-label*="play" i], button[title*="play" i]'
	).or_(
			page.locator('button').filter(has_text=re.compile("play", re.IGNORECASE))
	)

	# Locator for <div> elements with role="button" or onclick attribute and 'play' in attributes or text
	div_locator = page.locator(
			'div[role="button"][class*="play" i], div[role="button"][id*="play" i], div[role="button"][aria-label*="play" i], div[role="button"][title*="play" i], div[onclick][class*="play" i], div[onclick][id*="play" i], div[onclick][aria-label*="play" i], div[onclick][title*="play" i]'
	).or_(
			page.locator('div[role="button"], div[onclick]').filter(has_text=re.compile("play", re.IGNORECASE))
	)

	locator = button_locator.or_(div_locator)

	num_locators = await locator.count()

	if num_locators == 0:
		raise Exception("No play button found")

	if num_locators > 1:
		for i in range(num_locators):
			await locator.nth(i).click()

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