import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"


def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    data = []

    for book in books:
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text
        rating = book.p["class"][1]  # e.g., "Three", "Four"

        data.append({
            "title": title,
            "price": price,
            "rating": rating
        })

    return data


def scrape_multiple_pages(pages=3):
    all_data = []

    for page in range(1, pages + 1):
        url = BASE_URL.format(page)
        print(f"Scraping page {page}...")
        data = scrape_page(url)
        all_data.extend(data)

    return all_data


if __name__ == "__main__":
    pages = int(input("Enter number of pages to scrape: "))

    results = scrape_multiple_pages(pages)

    if results:
        df = pd.DataFrame(results)
        df.to_csv("products.csv", index=False)
        print("Done! Data saved to products.csv")
    else:
        print("No data scraped.")
