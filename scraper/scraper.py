from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


class Scraper:

    def __init__(self, headless=True):
        chrome_options = Options()
        if headless is True:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                       chrome_options=chrome_options)

    def scrape(self, search_text, file_path):
        url = "https://maps.google.com"
        self.driver.get(url)

        # Find the Search bar
        search_input = self.get_search_input()

        # Enter a search text
        search_input.send_keys(search_text)

        # Press Return
        search_input.send_keys(Keys.RETURN)

        # Scroll down until the bottom panel is found
        self.scroll_to_bottom()

        # Prepare JSON result
        places = [];

        # Find the top places displayed in the search result
        place_feeds = self.get_place_feeds()

        for place_feed in place_feeds:
            place_obj = {};

            # Get the place article wrapped inside the place feed.
            place_name = self.get_place_name(place_feed)
            place_obj["name"] = place_name

            stars = self.get_stars(place_feed)
            place_obj["stars"] = stars

            reviews = self.get_reviews(place_feed)
            place_obj["reviews"] = reviews

            address = self.get_address(place_feed)
            place_obj["address"] = address

            phone_number = self.get_phone_number(place_feed)
            place_obj["phoneNumber"] = phone_number

            # Store place
            places.append(place_obj);

        self.write_to_file(file_path, places)

    def get_search_input(self):
        return self.get_element_from_driver("#searchboxinput");

    def scroll_to_bottom(self):
        # Find the container of result elements
        scrollable_container = self.get_scrollable_container()

        # Find the bottom panel if exists
        bottom_panel = self.get_bottom_panel()

        ordinate = 0
        client_height = self.get_container_client_height(scrollable_container)
        previous_place_feed_count = 0
        while bottom_panel is None:
            print("======================")
            print("previous_place_feed_count: " + str(previous_place_feed_count))

            place_feed_count = self.get_place_feed_count()
            print("place_feed_count: " + str(place_feed_count))

            # If the loading is not responsive,
            # scroll up a half of the entire scroll height
            # then scroll down to send another request
            if place_feed_count == previous_place_feed_count:
                scroll_height = self.get_container_scroll_height(scrollable_container)
                self.scroll_top(scrollable_container, scroll_height / 2)
                time.sleep(1)

            ordinate += client_height
            print("ordinate: " + str(ordinate))

            self.scroll_top(scrollable_container, ordinate)
            time.sleep(2)

            bottom_panel = self.get_bottom_panel()
            previous_place_feed_count = place_feed_count

    def get_scrollable_container(self):
        return self.wait_for_element(".m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd[role='feed']")

    def get_bottom_panel(self):
        return self.get_element_from_driver(".m6QErb.tLjsW.eKbjU");

    def get_container_client_height(self, scrollable_container):
        return self.driver.execute_script("return arguments[0].clientHeight", scrollable_container)

    def get_container_scroll_height(self, scrollable_container):
        return self.driver.execute_script("return arguments[0].scrollHeight", scrollable_container)

    def get_place_feed_count(self):
        return len(self.get_place_feeds())

    def get_place_feeds(self):
        elements = self.get_elements_from_driver(".m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd[role='feed']"
                                                 " > div:has(> div[role='article'])")
        return elements if elements is not None else []

    def scroll_top(self, scrollable_container, ordinate):
        self.driver.execute_script("arguments[0].scrollTop = arguments[1]", scrollable_container, ordinate)

    def get_element_from_driver(self, selector):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element
        except NoSuchElementException:
            pass
        
    def wait_for_element(self, selector):
        element = WebDriverWait(self.driver, 10, .5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element

    def get_elements_from_driver(self, selector):
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return elements
        except NoSuchElementException:
            pass

    @staticmethod
    def get_element(parent, selector):
        try:
            element = parent.find_element(By.CSS_SELECTOR, selector)
            return element
        except NoSuchElementException:
            pass

    def get_place_name(self, place_feed):
        place_article = self.get_element(place_feed, "div[role='article']")
        return place_article.get_attribute("aria-label");

    def get_stars(self, place_feed):
        element = self.get_element(place_feed, ".UaQhfb :nth-child(3) .AJB7ye .ZkP5Je .MW4etd")
        if element is None:
            return ""
        return element.text

    def get_reviews(self, place_feed):
        element = self.get_element(place_feed, ".UaQhfb :nth-child(3) .AJB7ye .ZkP5Je .UY7F9")
        if element is None:
            return ""
        return element.text[1:-1]

    def get_address(self, place_feed):
        element = self.get_element(place_feed,
                                   ".UaQhfb > :nth-child(4) > :nth-child(2) > :nth-child(2) > jsl > :nth-child(2)")
        if element is None:
            return ""
        return element.text

    def get_phone_number(self, place_feed):
        element = self.get_element(place_feed,
                                   ".UaQhfb > .W4Efsd:last-of-type > :nth-child(3) > :nth-child(2) > jsl > :nth-child(2)")
        if element is None:
            return ""
        return element.text

    @staticmethod
    def write_to_file(file_path, places):
        with open(file_path, 'w') as output_file:
            json.dump(places, output_file)
