from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from customLogging import ColoredLog, CallCounted
import time
import logging
logger = logging.getLogger('scraper')

PLACE_LIST_CLASS = ['m6QErb','DxyBCb','kA9KIf','dS8AEf','ecceSd']
ONE_PLACE_CLASS = ['m6QErb','WNBkOb']

class Scraper:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )

    def scrape(self, search_text, retry=True):
        while True:
            logger.debug('browsing gmaps')
            url = "https://maps.google.com"
            self.driver.get(url)
            logger.debug('getting search input')
            search_input = self.get_search_input()
            logger.info('searching for: "%s"'%search_text)
            search_input.send_keys(search_text)
            search_input.send_keys(Keys.RETURN)
            timeout = 20
            try:
                logger.debug('waiting for search results...')
                places_container = self.wait_for_search_result(timeout)
                break
            except TimeoutException:
                if timeout==20:
                    logger.warning('Waiting for results but it is taking too long')
                    #scroll_height = self.get_container_scroll_height(scrollable_container)
                    logger.debug('refreshing')
                    timeout=40
                else:
                    logger.critical('Google is not responding.')
        
        if self.check_for_single_place(places_container):
            # single result
            logger.info('1 place feed found. extracting data')
            return [
                {
                    "name": self.get_single_name(places_container),
                    "stars": self.get_single_stars(places_container),
                    "reviews":self.get_single_reviews(places_container),
                    "address":self.get_single_address(places_container),
                    "phoneNumber":self.get_single_phone_number(places_container)
                }
            ]
        
        state = self.scroll_to_bottom(places_container)
        places = []
        place_feeds = self.get_place_feeds()
        if len(place_feeds)==1:
            logger.debug("got %d places"%len(place_feeds))
            logger.warning("didn't found proper data")
            return []

        logger.info('%d place feeds found. extracting data, this may take some time.'%len(place_feeds))
        
        for place_feed in place_feeds:
            place_obj = {
                "name":self.get_place_name(place_feed),
                "stars":self.get_stars(place_feed),
                "reviews":self.get_reviews(place_feed),
                "address":self.get_address(place_feed),
                "phoneNumber":self.get_phone_number(place_feed)
            }
            places.append(place_obj)
        
        if retry and state == 1 or state == 2:
            logger.warning('last try was unsuccessful, retying...')
            retry_result = self.scrape(search_text, False)
            if len(retry_result)>len(places):
                return retry_result
        
        return places

    def get_search_input(self):
        return self.wait_for_element("#searchboxinput")

    def scroll_to_bottom(self, scrollable_container):
        logger.debug('scrolling container')
        logger.debug(f'scrollable container is null? => {scrollable_container is None}')

        # Find the bottom panel if exists
        bottom_panel = self.get_bottom_panel()
        logger.debug(f'bottom panel is null? => {bottom_panel is None}')
        
        while bottom_panel is None:
            timeout = 20
            while True:
                try:
                    logger.debug("waiting for new places")
                    self.wait_for_get_new_places(timeout)
                    break
                except TimeoutException:
                    if timeout==20:
                        logger.warning('Waiting for more places but it is taking too long')
                        #scroll_height = self.get_container_scroll_height(scrollable_container)
                        self.scroll_top(scrollable_container, 0)
                        time.sleep(1)
                        self.scroll_down()
                        timeout=40
                    else:
                        logger.error('Google is not responding. Can not get more places.')
                        return 2
                        
            place_feed_count = self.get_place_feed_count()
            logger.info("got %d place feeds..."%place_feed_count)
            if place_feed_count == 0:
                logger.warning('found nothing. skipping...')
                return 3
            self.scroll_down()

            bottom_panel = self.get_bottom_panel()

    def get_scrollable_container(self):
        return self.wait_for_element(".m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd[role='feed']")
    
    def wait_for_search_result(self, timeout=10)->WebElement:
        return WebDriverWait(self.driver, timeout, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".m6QErb.WNBkOb[role='main']"))
        )

    def get_bottom_panel(self):
        return self.get_element_from_driver(".m6QErb.tLjsW.eKbjU")

    def get_container_client_height(self, scrollable_container):
        return self.driver.execute_script(
            "return arguments[0].clientHeight", scrollable_container
        )

    def get_container_scroll_height(self, scrollable_container):
        return self.driver.execute_script(
            "return arguments[0].scrollHeight", scrollable_container
        )

    def get_place_feed_count(self):
        return len(self.get_place_feeds())

    def get_place_feeds(self):
        elements = self.get_elements_from_driver(
            ".m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd[role='feed']"
            " > div:has(> div[role='article'])"
        )
        return elements if elements is not None else []

    def scroll_top(self, scrollable_container, ordinate):
        self.driver.execute_script(
            "arguments[0].scrollTop = arguments[1]", scrollable_container, ordinate
        )
        
    def scroll_down(self):
        element = self.get_element_from_driver(".lXJj5c.Hk4XGb")
        if element:
            self.driver.execute_script("arguments[0].scrollIntoView();",element)
        else:
            return False

    def get_element_from_driver(self, selector):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element
        except NoSuchElementException:
            logger.debug('element "%s" not found, returning None'%selector)
            pass

    def wait_for_element(self, selector):
        element = WebDriverWait(self.driver, 10, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element

    def check_object_is_in_viewport(self, selector):
        element = self.get_element_from_driver(selector)
        if element is None:
            return False
        return self.driver.execute_script(
            """
                var elem = arguments[0],
                    box = elem.getBoundingClientRect(),
                    cx = box.left + box.width / 2,
                    cy = box.top + box.height / 2,
                    e = document.elementFromPoint(cx, cy);
                for (; e; e = e.parentElement) {
                    if (e === elem)
                    return true;
                }
                return false;
            """,
            element,
        )

    def wait_for_get_new_places(self, timeout=10):
        WebDriverWait(self.driver, timeout, 0.5).until_not(lambda _:self.check_object_is_in_viewport(".lXJj5c.Hk4XGb"))

    def get_elements_from_driver(self, selector, desc=''):
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return elements
        except NoSuchElementException:
            logger.debug('element "%s" not found (description: "%s")'%(selector, desc))
            pass

    @staticmethod
    def get_element(parent, selector, desc=''):
        try:
            element = parent.find_element(By.CSS_SELECTOR, selector)
            return element
        except NoSuchElementException:
            logger.debug('element "%s" not found (description: "%s")'%(selector, desc))
            pass
        
    def check_for_single_place(self, container):
        element = self.get_element(
            container, ".TIHn2 .tAiQdd .lMbq3e h2.bwoZTb span", 'check for single place feed'
        )
        return element is not None

    def get_single_name(self, place_feed):
        element = self.get_element(
            place_feed, ".TIHn2 .tAiQdd .lMbq3e h2.bwoZTb span", 'single name'
        )
        if element is None:
            return ""
        return element.text
        
    def get_single_stars(self, place_feed):
        element = self.get_element(
            place_feed, "div.TIHn2 div.tAiQdd div.lMbq3e div.LBgpqf div.skqShb div.fontBodyMedium.dmRWX div.F7nice.mmu3tf span span span",
            'single stars'
        )
        if element is None:
            return ""
        return element.text
        
    def get_single_reviews(self, place_feed):
        
        element = self.get_element(
            place_feed, "div.TIHn2 div.tAiQdd div.lMbq3e div.LBgpqf div.skqShb div.fontBodyMedium.dmRWX div.F7nice.mmu3tf :nth-child(2) span span",
            "single reviews"
        )
        if element is None:
            return ""
        return element.text.split()[0]
        
    def get_single_address(self, place_feed):
        informations = self.get_elements_from_driver("div.m6QErb.WNBkOb div.m6QErb div.RcCsl.fVHpi.w4vB1d.NOE9ve.M0S7ae.AG25L", "single info")
        for info_elem in informations:
            address_elem = self.get_element(
                info_elem, "button.CsEnBe"
            )
            if address_elem:
                label = address_elem.get_attribute('aria-label')
                if label and label.startswith('Address:'):
                    break
        else:
            return ""
        address = self.get_element(address_elem,"div.AeaXub div.rogA2c div.Io6YTe.fontBodyMedium", "single address")
        if address:
            return address.text
        return ""
    
    def get_single_phone_number(self, place_feed):
        informations = self.get_elements_from_driver("div.m6QErb.WNBkOb div.m6QErb div.RcCsl.fVHpi.w4vB1d.NOE9ve.M0S7ae.AG25L", "single info")
        for info_elem in informations:
            phone_elem = self.get_element(
                info_elem, "button.CsEnBe"
            )
            if phone_elem:
                label = phone_elem.get_attribute('aria-label')
                if label and label.startswith('Phone:'):
                    break
        else:
            return ""
        phone = self.get_element(phone_elem,"div.AeaXub div.rogA2c div.Io6YTe.fontBodyMedium", "single phone")
        if phone:
            return phone.text
        return ""

    def get_place_name(self, place_feed):
        place_article = self.get_element(place_feed, "div[role='article']", "name")
        return place_article.get_attribute("aria-label")

    def get_stars(self, place_feed):
        element = self.get_element(
            place_feed, ".UaQhfb :nth-child(3) .AJB7ye .ZkP5Je .MW4etd", "stars"
        )
        if element is None:
            return ""
        return element.text

    def get_reviews(self, place_feed):
        element = self.get_element(
            place_feed, ".UaQhfb :nth-child(3) .AJB7ye .ZkP5Je .UY7F9", "reviews"
        )
        if element is None:
            return ""
        return element.text[1:-1]

    def get_address(self, place_feed):
        element = self.get_element(
            place_feed,
            ".UaQhfb > :nth-child(4) > :nth-child(2) > :nth-child(2) > jsl > :nth-child(2)","address"
        )
        if element is None:
            return ""
        return element.text

    def get_phone_number(self, place_feed):
        element = self.get_element(
            place_feed,
            ".UaQhfb > .W4Efsd:last-of-type > :nth-child(3) > :nth-child(2) > jsl > :nth-child(2)","phone"
        )
        if element is None:
            return ""
        return element.text
