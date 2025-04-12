# TSG-Scraper With Bonus Task

**TSG-Scraper** is a Python CLI tool to scrape and download videos with metadata from a list of URLs within a specified date range.

---

## What works:
- scrapes every test site except Facebook
- Downloads videos from YouTube, ZoomGov, CivicClerk, Facebook
- Can download videos from generic sites

---

## 🧩 Architecture

The project is divided into two parts, each runnable as a separate module:

### 1. Scraper
- Scrapes video links and metadata from the provided URLs.
- Saves the output to a file named `results.jsonl`.
- Accepts the following arguments:
  - `-u` / `--urls` (required): List of URLs to scrape
  - `-s` / `--start-date` (required): Start date in `MM-DD-YYYY` format
  - `-e` / `--end-date` (optional): End date in `MM-DD-YYYY` format (defaults to today)

```bash
python -m scraper -u "https://www.youtube.com/@SLCLiveMeetings/streams" -s 01-01-2025 -e 02-01-2025
```

Outputs a structure like this:

```json
[
  {
    "base_url": "http://detroit-vod.cablecast.tv/CablecastPublicSite",
    "medias": [
      {
        "url": "http://detroit-vod.cablecast.tv/CablecastPublicSite/show/14093?site=1",
        "title": "Detroit City Council Formal Session pt2 11-26-2024",
        "date": "2024-11-26",
        "source_type": "video"
      }
    ]
  }
]
```

#### CLI Usage
```bash
python -m scraper -u "https://www.youtube.com/@SLCLiveMeetings/streams" -s 01-01-2025 -e 02-01-2025
```

#### As a Package
```python
from scraper import scrape_urls
await scrape_urls(urls, start_date, end_date)
```

### 2. Downloader
- Accepts a list of video URLs.
- Prints to the console whether each video is being downloaded or skipped.
- Accepts the following argument:
  - `-u` / `--urls` (required): List of video URLs to download

#### CLI Usage
```bash
python -m downloader -u "http://example.com/video1" "http://example.com/video2"
```

#### As a Package
```python
from downloader import download_urls
await download_urls(urls)
```

---

## 🔧 Usage

You can also run the tool using the unified interface:

```bash
python main.py -u "https://www.youtube.com/@SLCLiveMeetings/streams" -s 01-01-2025 -e 02-01-2025
```

### Arguments

| Flag            | Description                                            | Required | Format/Example                     |
|-----------------|--------------------------------------------------------|----------|------------------------------------|
| `-u`, `--urls`  | List of URLs to scrape                                 | ✅       | `"https://site.com/page1"`         |
| `-s`, `--start-date` | Start date for scraping                         | ✅       | `MM-DD-YYYY` (e.g., `01-01-2025`)  |
| `-e`, `--end-date`   | End date (defaults to today if omitted)         | ❌       | `MM-DD-YYYY`                       |

---

## 📁 Output

- Scraped metadata is saved to `results.jsonl`. (Only when ran as a independent module)
- Videos are fetched using `yt-dlp` and `aria2c`.

---

## 📦 Dependencies

Install dependencies via `pip`:

```bash
pip install -r requirements.txt
```

or via `uv`

```bash
uv install
uv sync
```

---

## Example

```bash
$ python main.py -u "https://charlestonwv.portal.civicclerk.com/" -s 12-01-2024 -e 01-01-2025
Scraping...
Downloading...
Downloading 3 videos for: https://charlestonwv.portal.civicclerk.com/
[generic] Extracting URL: https://cpmedia.azureedge.net/charlestonwv/fd915de025.mp4
[generic] fd915de025: Downloading webpage
[info] fd915de025: Downloading 1 format(s): mp4
[generic] Extracting URL: https://cpmedia.azureedge.net/charlestonwv/478203d9ae.mp4
[generic] 478203d9ae: Downloading webpage
[info] 478203d9ae: Downloading 1 format(s): mp4
[generic] Extracting URL: https://cpmedia.azureedge.net/charlestonwv/0c2caab591.mp4
[generic] 0c2caab591: Downloading webpage
[info] 0c2caab591: Downloading 1 format(s): mp4
Successful: 3
Failed: 0
```
