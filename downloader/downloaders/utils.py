from playwright.async_api import Cookie
import yt_dlp
import io

def gen_cookies_txt(cookies: list[Cookie]) -> list[str]:
		"""
		Format a single cookie dictionary into a line expected by certain tools.
		This is a simplified example. The actual format might require additional fields.
		"""
		formatted_lines = ["# Netscape HTTP Cookie File\n","\n"]

		# Assuming cookies is a list of cookie dictionaries
		for cookie in cookies:
			# Use defaults if certain fields are missing
			domain = cookie.get('domain', '')
			# Automatically set flag based on the domain string
			include_subdomains = "TRUE" if domain.startswith('.') else "FALSE"
			
			path = cookie.get('path', '/')
			secure = "TRUE" if cookie.get('secure', False) else "FALSE"
			expiration = str(cookie.get('expiration', 0))
			name = cookie.get('name', '')
			value = cookie.get('value', '')
			
			# Format in a tab-separated line (adapt as needed)
			formatted_lines.append(f"{domain}\t{include_subdomains}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")
		
		return formatted_lines

def try_download(url: str, headers: dict[str, str] | None = None, cookies: io.StringIO | None = None) -> bool:
	yt_dpl_options = {
		"simulate": True,
		"wait_for_video": True,
		"external_downloader": "aria2c",
		"http_headers": headers,
		"cookiefile": cookies,
	}

	with yt_dlp.YoutubeDL(yt_dpl_options) as ydl:
		try:
			code = ydl.download(url)
			if code == 0:
				return True
		except Exception as e:
			print(f"Error downloading {url}: {e}")
			return False

	return False

def is_valid_video_source_url(url: str) -> bool:
	return (url.startswith("https://") or url.startswith("http://") or url.startswith("[blob]")) and (".m3u8" in url or ".mp4" in url or ".ts" in url or ".flv" in url)