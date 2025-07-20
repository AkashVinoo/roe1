from playwright.sync_api import sync_playwright
import re

URLS = [
    f"https://sanand0.github.io/tdsdata/js_table/?seed={seed}" for seed in range(67, 77)
]

def extract_numbers_from_table(table_html):
    # Find all numbers (including decimals, negatives, and commas)
    numbers = re.findall(r"[-+]?[0-9,]*\.?[0-9]+", table_html)
    total = 0.0
    for num in numbers:
        try:
            total += float(num.replace(",", ""))
        except Exception:
            pass
    return total

def main():
    grand_total = 0.0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for url in URLS:
            page.goto(url)
            page.wait_for_selector('table')
            tables = page.query_selector_all('table')
            for table in tables:
                html = table.inner_html()
                grand_total += extract_numbers_from_table(html)
        browser.close()
    print(f"GRAND TOTAL: {grand_total}")

if __name__ == "__main__":
    main() 