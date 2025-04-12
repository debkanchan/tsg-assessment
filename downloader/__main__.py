import argparse
import asyncio

from . import download_urls

def main():
		parser = argparse.ArgumentParser(description="CLI script to process URLs.")
		
		parser.add_argument(
				"--urls", "-u",
				nargs='+',
				required=True,
				help="List of URLs (space-separated)"
		)
		
		args = parser.parse_args()
		
		print("Finding Download links...")
		scape_results = asyncio.run(download_urls(args.urls))
		print("Done.")

		succcessful, failed = 0, 0

		for url in scape_results:
				if isinstance(url, str):
						succcessful += 1
				else:
						failed += 1

		print(f"Successful: {succcessful}")
		print(f"Failed: {failed}")


if __name__ == "__main__":
		main()