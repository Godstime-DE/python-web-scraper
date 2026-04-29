import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# CONFIGURATION
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
}

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

# CORE SCRAPER
def fetch_page(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None


def parse_books(html):
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    books = soup.find_all("article", class_="product_pod")

    results = []

    for book in books:
        try:
            title = book.h3.a.get("title", "").strip()

            price_text = book.find("p", class_="price_color").text
            price_match = re.search(r"\d+\.\d+", price_text)
            price = float(price_match.group()) if price_match else 0

            rating_tag = book.find("p", class_=re.compile("star-rating"))
            rating_class = rating_tag.get("class") if rating_tag else []
            rating_word = next((c for c in rating_class if c in rating_map), None)
            rating = rating_map.get(rating_word, 0)

            results.append({
                "title": title,
                "price": price,
                "rating": rating
            })

        except Exception as e:
            print(f"[WARNING] Skipped item: {e}")

    return results


# ORCHESTRATION
def scrape_pages(base_url, total_pages, delay=1.5):
    all_data = []

    for page in range(1, total_pages + 1):
        url = base_url.format(page)
        print(f"[INFO] Scraping page {page}...")

        html = fetch_page(url)
        data = parse_books(html)
        all_data.extend(data)

        time.sleep(delay)

    return all_data


def validate_data(data):
    cleaned = []

    for item in data:
        if (
            item.get("title")
            and isinstance(item.get("price"), (int, float))
            and isinstance(item.get("rating"), int)
        ):
            cleaned.append(item)

    return cleaned


# EXPORTATION
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"[SUCCESS] Data saved to {filename}")


# MAIN
if __name__ == "__main__":

    base_url = input("Enter base URL (use {} for page number): ")

    try:
        pages = int(input("Enter number of pages to scrape: "))
        if pages <= 0:
            raise ValueError
    except ValueError:
        print("Invalid input. Using 1 page.")
        pages = 1

    output_file = input("Enter output filename (e.g. data.csv): ")

    data = scrape_pages(base_url, pages)
    data = validate_data(data)

    if data:
        save_to_csv(data, output_file)
    else:
        print("[INFO] No valid data scraped.")
