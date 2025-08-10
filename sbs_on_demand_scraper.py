import requests
import csv
from datetime import timedelta
import re

BASE_FEED = "https://www.sbs.com.au/api/video_feed/f/Bgtm9B/{}?form=json&range=1-1000"

# Filters
FILTER_GENRE = "Drama"         # Change this to your desired genre
FILTER_YEAR = 2022             # Change this to your desired year

def fetch_items(section_id):
    url = BASE_FEED.format(section_id)
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get('entries', [])

def convert_duration(raw_duration):
    """Convert ISO 8601 duration or seconds to hh:mm:ss format."""
    if not raw_duration:
        return None
    if isinstance(raw_duration, int):
        return str(timedelta(seconds=raw_duration))
    if isinstance(raw_duration, str) and raw_duration.startswith("PT"):
        # ISO 8601 format
        hours = minutes = seconds = 0
        h = re.search(r'(\d+)H', raw_duration)
        m = re.search(r'(\d+)M', raw_duration)
        s = re.search(r'(\d+)S', raw_duration)
        if h:
            hours = int(h.group(1))
        if m:
            minutes = int(m.group(1))
        if s:
            seconds = int(s.group(1))
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return raw_duration  # fallback

def parse_item(item):
    metadata = item.get('metadata', {})
    genre = metadata.get('genre')
    year = metadata.get('year')

    # Apply filters
    if FILTER_GENRE and genre and FILTER_GENRE.lower() not in genre.lower():
        return None
    if FILTER_YEAR and year:
        try:
            if int(year) != FILTER_YEAR:
                return None
        except ValueError:
            return None

    return {
        'title': item.get('title'),
        'year': year,
        'author': metadata.get('author'),
        'duration': convert_duration(metadata.get('duration')),
        'countries': metadata.get('country'),
        'directors': metadata.get('director'),
        'cast': metadata.get('actor'),
        'genre': genre
    }

def scrape_section(section_key):
    items = fetch_items(section_key)
    parsed = [parse_item(it) for it in items]
    return [p for p in parsed if p]

def save_to_csv(parsed_list, filename):
    keys = ['title', 'year', 'author', 'duration', 'countries', 'directors', 'cast', 'genre']
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in parsed_list:
            writer.writerow(row)

if __name__ == '__main__':
    print(f"Fetching filtered content: Genre = {FILTER_GENRE}, Year = {FILTER_YEAR}")
    movies = scrape_section('sbs-section-programs')

    save_to_csv(movies, f'sbs_{FILTER_GENRE}_{FILTER_YEAR}.csv')
    print("Done. Saved", len(movies), "items to file.")







