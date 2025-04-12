import asyncio
import argparse
import json
from datetime import datetime

from . import scrape_urls

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
		scape_results= asyncio.run(scrape_urls(args.urls, start_date, end_date))
		print("Scraping complete.")
		
		print("Exporting...")
		with open("results.jsonl", "w") as f:
				for result in scape_results:
						f.write(result.model_dump_json() + "\n")

		print("Export complete.")

if __name__ == "__main__":
		main()