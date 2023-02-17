from scraper.scraper import Scraper
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from customLogging import ColoredLog
import logging
import sys
import traceback
import json

def d(path)->Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


logFormatter = logging.Formatter("%(asctime)s  %(name)-12.12s L%(lineno)-4.4d  %(levelname)-5.5s: %(message)s")
fileHandler = TimedRotatingFileHandler(filename=d('logs')/'scraper.log', encoding='utf-8', when='midnight', interval=1, backupCount=7)
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(ColoredLog())
consoleHandler.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG, handlers=[consoleHandler,fileHandler])

def log_exceptions(type, value, tb):
    for line in traceback.TracebackException(type, value, tb).format(chain=True):
        logging.exception(line)
    logging.exception(value)

    sys.__excepthook__(type, value, tb) # calls default excepthook

sys.excepthook = log_exceptions

def run():
    # 1) Pass headless=False if you want to see Chrome's automation
    scraper = Scraper(headless=False)
    keywords = json.load(open("keywords.json"))

    for k in keywords:
        result = scraper.scrape(k)
        json.dump(result,open("%s.json"%k,"w"))


if __name__ == '__main__':
    run()
