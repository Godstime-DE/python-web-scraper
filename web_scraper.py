import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"

# Convert rating text to numeric
rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

def scrape_page(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching page:", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all("article", class_="product_pod")

    data = []

    for book in books:
        try:
            # Title
            title = book.h3.a.get("title", "").strip()

            # Price (convert to float)
            price_text = book.find("p", class_="price_color").text
            price_match = re.search(r"\d+\.\d+", price_text)
            price = float(price_match.group()) if price_match else 0

            # Rating (convert to number)
            rating_text = book.p.get("class", ["", ""])[1]
            rating = rating_map.get(rating_text, 0)

            data.append({
                "title": title,
                "price": price,
                "rating": rating
            })

        except Exception as e:
            print(f"Skipping item due to error: {e}")
            continue

    return data


def scrape_multiple_pages(pages=3):
    all_data = []

    for page in range(1, pages + 1):
        url = BASE_URL.format(page)
        print(f"Scraping page {page}...")
        data = scrape_page(url)
        all_data.extend(data)

        time.sleep(2)  # Be respectful to the server

    return all_data


if __name__ == "__main__":
    # Input validation
    while True:
        try:
            pages = int(input("Enter number of pages to scrape: "))
            if pages > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    results = scrape_multiple_pages(pages)

    if results:
        df = pd.DataFrame(results)
        df.to_csv("products.csv", index=False, encoding="utf-8")
        print("Done! Data saved to products.csv")
    else:
        print("No data scraped.")
