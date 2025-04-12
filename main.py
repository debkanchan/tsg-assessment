import argparse
import asyncio
from datetime import datetime

from downloader import download_urls
from scraper import scrape_urls

def validate_date(date_str):
		try:
				return datetime.strptime(date_str, "%m-%d-%Y")
		except ValueError:
				raise argparse.ArgumentTypeError(f"Invalid date: {date_str}. Expected format: MM-DD-YYYY")

def main():
		parser = argparse.ArgumentParser(description="CLI script to process URLs.")
		
		parser.add_argument(
				"--urls", "-u",
				nargs='+',
				required=True,
				help="List of URLs (space-separated)"
		)

		parser.add_argument(
				"--start-date", "-s",
				type=str,
				required=True,
				help="Start date in MM-DD-YYYY-MM- format"
		)

		parser.add_argument(
				"--end-date", "-e",
				type=str,
				required=False,
				default=datetime.now().strftime("%m-%d-%Y"),
				help="End date in MM-DD-YYYY format. Defaults to today."
		)
		
		args = parser.parse_args()

		start_date = validate_date(args.start_date)
		end_date = validate_date(args.end_date)

		if start_date > end_date or start_date == end_date:
				raise ValueError("Start date must be before the end date.")
		
		print("Scraping...")
		scaped_medias = asyncio.run(scrape_urls(args.urls, start_date, end_date))

		print("Downloading...")
		successful, failed = 0, 0
		for media_result in scaped_medias:
			if media_result.error is not None:
				continue

			print(f"Downloading {len(media_result.medias)} videos for: {media_result.base_url}")
			results = asyncio.run(download_urls([media.url for media in media_result.medias]))

			for result in results:
				if isinstance(result, str):
					successful += 1
				else:
					failed += 1
		
		print(f"Successful: {successful}")
		print(f"Failed: {failed}")

if __name__ == "__main__":
		main()
