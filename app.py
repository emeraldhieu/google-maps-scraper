from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import json


def scroll_to_bottom(driver):
    # Find the container of result elements
    scrollable_container = get_scrollable_container(driver)

    # Find the bottom panel if exists
    bottom_panel = get_bottom_panel(driver)

    ordinate = 0
    scroll_height = get_scroll_height(scrollable_container)
    previous_place_feed_count = 0
    while bottom_panel is None:
        place_feed_count = get_place_feed_count(driver)
        print("previous_place_feed_count: " + str(previous_place_feed_count))
        print("place_feed_count: " + str(place_feed_count))
        print("ordinate: " + str(ordinate))

        # If the loading is not responsive, scroll up then scroll down to send another request
        if place_feed_count == previous_place_feed_count:
            ordinate -= scroll_height
            scroll_top(scrollable_container, ordinate)
            time.sleep(2)

        ordinate += scroll_height
        scroll_top(scrollable_container, ordinate)
        time.sleep(2)
        bottom_panel = get_bottom_panel(driver)
        previous_place_feed_count = place_feed_count


def get_scroll_height(scrollable_container):
    return driver.execute_script("return arguments[0].scrollHeight", scrollable_container)


def get_search_input(driver):
    return get_element_from_driver(driver, "#searchboxinput");


def get_scrollable_container(driver):
    return get_element_from_driver(driver, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd[role='feed']")


def get_bottom_panel(driver):
    return get_element_from_driver(driver, ".m6QErb.tLjsW.eKbjU");


def get_place_feed_count(driver):
    return len(get_place_feeds(driver))


def get_place_feeds(driver):
    elements = get_elements_from_driver(driver,
                                        ".m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd[role='feed']"
                                        " > div:has(> div[role='article'])")
    return elements if elements is not None else []


def scroll_top(scrollable_container, ordinate):
    driver.execute_script("arguments[0].scrollTop = arguments[1]", scrollable_container, ordinate)


def get_element_from_driver(driver, selector):
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        return element
    except NoSuchElementException:
        pass


def get_elements_from_driver(driver, selector):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        return elements
    except NoSuchElementException:
        pass


def get_element(parent, selector):
    try:
        element = parent.find_element(By.CSS_SELECTOR, selector)
        return element
    except NoSuchElementException:
        pass


def get_place_name(placeFeed):
    place_article = get_element(placeFeed, "div[role='article']")
    return place_article.get_attribute("aria-label");


def get_stars(place_feed):
    element = get_element(place_feed, ".UaQhfb :nth-child(3) .AJB7ye .ZkP5Je .MW4etd")
    if element is None:
        return ""
    return element.text


def get_reviews(place_feed):
    element = get_element(place_feed, ".UaQhfb :nth-child(3) .AJB7ye .ZkP5Je .UY7F9")
    if element is None:
        return ""
    return element.text[1:-1]


def get_address(place_feed):
    element = get_element(place_feed, ".UaQhfb > :nth-child(4) > :nth-child(2) > :nth-child(2) > jsl > :nth-child(2)")
    if element is None:
        return ""
    return element.text


def get_phone_number(place_feed):
    element = get_element(place_feed, ".UaQhfb > :nth-child(4) > :nth-child(4) > :nth-child(2) > jsl > :nth-child(2)")
    if element is None:
        return ""
    return element.text


def write_to_file(file_path, places):
    with open(file_path, 'w') as output_file:
        json.dump(places, output_file)


driver = webdriver.Chrome(ChromeDriverManager().install())

url = "https://maps.google.com"
driver.get(url)

# Find the Search bar
search_input = get_search_input(driver)

# Enter a search text
search_text = "Surf shops in Florida"
search_input.send_keys(search_text)

# Press Return
search_input.send_keys(Keys.RETURN)

# Wait for the search results to appear
time.sleep(5)

# Scroll down until the bottom panel is found
scroll_to_bottom(driver)

# Prepare JSON result
places = [];

# Find the top places displayed in the search result
place_feeds = get_place_feeds(driver)

for place_feed in place_feeds:
    place_obj = {};

    # Get the place article wrapped inside the place feed.
    place_name = get_place_name(place_feed)
    place_obj["name"] = place_name

    stars = get_stars(place_feed)
    place_obj["stars"] = stars

    reviews = get_reviews(place_feed)
    place_obj["reviews"] = reviews

    address = get_address(place_feed)
    place_obj["address"] = address

    # TODO Investigate why this element is None though I can get the element in Chrome's developer's console
    phone_number = get_phone_number(place_feed)
    place_obj["phoneNumber"] = phone_number

    # Store place
    places.append(place_obj);

file_path = "places.json"
write_to_file(file_path, places)

print("DONE")