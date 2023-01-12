# Google Maps Scraper

A script that scrapes places from Google Maps and export the result into a JSON file.

## Requirements

+ Python 3.11
+ Selenium 3.141.0
+ Webdriver Manager

## Quickstart

+ Run the `app.py`
  + The script will open Google Chrome and do some automation steps
  + Leave it running until the console says "Done"
  + Do not focus on another Google Chrome
+ Check the `places.json` in the project based directory
+ Change the `search_text` if needed

`places.json` output:

```json
[
  {
    "name": "Ron Jon Surf Shop",
    "stars": "4.6",
    "reviews": "8,938",
    "address": "4151 N Atlantic Ave",
    "phoneNumber": "+1 321-799-8820"
  },
  {
    "name": "CaliFlorida Surf & Skate Shop",
    "stars": "4.7",
    "reviews": "69",
    "address": "5221 Ocean Blvd",
    "phoneNumber": ""
  }
]
```

## Installation

This is an installation guide if you're new to Python.

### 1) Install [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)

Virtualenv is basically a tool that creates an isolated Python environment to avoid conflicting with global Python. You can use a different version of Python other than the one installed on your local machine.

### 2) Set up environment

Set it up by either of these ways

#### 2.1) Command lines

At base project directory, run
```
virtualenv venv
```

Install necessary modules
```
pip3 install -r requirements.txt
```

Activate the virtual environment
```
source venv/bin/activate
```

To deactivate it, run this during being "activated"
```
deactivate
```

#### 2.2) IntelliJ

+ `New` / `Project from Existing Sources...`
+ Select the repo
+ In `Project Structure` / `SDKs`, `Add Python SDK`
  + Point `Location` to directory `venv`
  + Point `Base intepreter` to the Python version you want to use
  + Click `OK`
+ IntelliJ will pop up and ask you to install the modules in `requirements.txt`
  + or you can manually do it vi `Tool` / `Sync Python Requirements...`

## Notes

+ This script works in 2023-01-12
  + If Google updates their HTML, I will update the script
  + Feel free to create issues
+ Do not focus on another Google Chrome during non-headless mode (`headless=False`)
  + because Selenium will be confused with the instance you're in
