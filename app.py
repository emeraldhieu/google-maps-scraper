from scraper.scraper import Scraper


def run():
    # 1) Pass headless=True if you want to run the browser in background
    scraper = Scraper(headless=False)

    # 2) Pass the text you want to search for
    search_text = "Surf shops in Florida"

    # 3) Pass the file path you want to export into
    file_path = "places.json"

    scraper.scrape(search_text, file_path)
    print("DONE")


if __name__ == '__main__':
    run()
