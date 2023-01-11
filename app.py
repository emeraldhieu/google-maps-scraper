from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import json

def scrollToBottom(driver):
   # Find the container of result elements
   scrollableContainer = getScrollableContainer(driver)

   # Find the bottom panel if exists
   bottomPanel = getBottomPanel(driver)

   ordinate = 0
   scrollHeight = getScrollHeight(scrollableContainer)
   previousPlaceFeedCount = 0
   while bottomPanel is None:
      placeFeedCount = getPlaceFeedCount(driver)
      print("previousPlaceFeedCount: " + str(previousPlaceFeedCount))
      print("placeFeedCount: " + str(placeFeedCount))
      print("ordinate: " + str(ordinate))

      # If the loading is not responsive, scroll up then scroll down to send another request
      if placeFeedCount == previousPlaceFeedCount:
         ordinate -= scrollHeight
         scrollTop(scrollableContainer, ordinate)
         time.sleep(2)
      
      ordinate += scrollHeight
      scrollTop(scrollableContainer, ordinate)
      time.sleep(2)
      bottomPanel = getBottomPanel(driver)
      previousPlaceFeedCount = placeFeedCount

def getScrollHeight(scrollableContainer):
   return driver.execute_script("return arguments[0].scrollHeight", scrollableContainer)

def getSearchInput(driver):
   return getElementFromDriver(driver, "#searchboxinput");

def getScrollableContainer(driver):
   return getElementFromDriver(driver, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd[role='feed']")

def getBottomPanel(driver):
   return getElementFromDriver(driver, ".m6QErb.tLjsW.eKbjU");

def getPlaceFeedCount(driver):
   return len(getPlaceFeeds(driver))

def getPlaceFeeds(driver):   
   elements = getElementsFromDriver(driver, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd[role='feed'] > div:has(> div[role='article'])")
   return elements if elements is not None else []

def scrollTop(scrollableContainer, ordinate):
   driver.execute_script("arguments[0].scrollTop = arguments[1]", scrollableContainer, ordinate)

def getElementFromDriver(driver, selector):
   try:
      element = driver.find_element(By.CSS_SELECTOR, selector)
      return element
   except NoSuchElementException:
      pass

def getElementsFromDriver(driver, selector):
   try:
      elements = driver.find_elements(By.CSS_SELECTOR, selector)
      return elements
   except NoSuchElementException:
      pass

def getElement(parent, selector):
   try:
      element = parent.find_element(By.CSS_SELECTOR, selector)
      return element
   except NoSuchElementException:
      pass

def getPlaceName(placeFeed):
   placeArticle = getElement(placeFeed, "div[role='article']")
   return placeArticle.get_attribute("aria-label");

def getStars(placeFeed):
   element = getElement(placeFeed, ".UaQhfb :nth-child(3) .AJB7ye .ZkP5Je .MW4etd")
   if element is None:
      return ""
   return element.text

def getReviews(placeFeed):
   element = getElement(placeFeed, ".UaQhfb :nth-child(3) .AJB7ye .ZkP5Je .UY7F9")
   if element is None:
      return ""
   return element.text[1:-1]
   
def getAddress(placeFeed):
   element = getElement(placeFeed, ".UaQhfb > :nth-child(4) > :nth-child(2) > :nth-child(2) > jsl > :nth-child(2)")
   if element is None:
      return ""
   return element.text

def getPhoneNumber(placeFeed):
   element = getElement(placeFeed, ".UaQhfb > :nth-child(4) > :nth-child(4) > :nth-child(2) > jsl > :nth-child(2)")
   if element is None:
      return ""
   return element.text

def writeToFile(filePath, places):
   with open(filePath, 'w') as outputFile:
      json.dump(places, outputFile)   

driver = webdriver.Chrome(ChromeDriverManager().install())

url = "https://maps.google.com"
driver.get(url)

# Find the Search bar
searchInput = getSearchInput(driver)

# Enter a search text
searchText = "Surf shops in Florida"
searchInput.send_keys(searchText)

# Press Return
searchInput.send_keys(Keys.RETURN)

# Wait for the search results to appear
time.sleep(5)

# Scroll down until the bottom panel is found
scrollToBottom(driver)
 
# Prepare JSON result
places = []; 

# Find the top places displayed in the search result
placeFeeds = getPlaceFeeds(driver)

for placeFeed in placeFeeds:
   placeObj = {};

   # Get the place article wrapped inside the place feed.
   placeName = getPlaceName(placeFeed)
   placeObj["name"] = placeName

   stars = getStars(placeFeed)
   placeObj["stars"] = stars

   reviews = getReviews(placeFeed)
   placeObj["reviews"] = reviews
      
   address = getAddress(placeFeed)
   placeObj["address"] = address

   # TODO Investigate why this element is None though I can get the element in Chrome's developer's console
   #phoneNumber = getPhoneNumber(placeFeed)
   #placeObj["phoneNumber"] = phoneNumber

   # Store place
   places.append(placeObj);

filePath = "places.json"
writeToFile(filePath, places)















