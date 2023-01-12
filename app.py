from scraper.scraper import Scraper


def run():
    scraper = Scraper()
    search_text = "Surf shops in Florida"
    file_path = "places.json"
    scraper.scrape(search_text, file_path)
    print("DONE")


if __name__ == '__main__':
    run()
