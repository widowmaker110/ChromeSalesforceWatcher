"""
MIT License

Copyright (c) 2021 Alexander Miller

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

###### SETUP ######

1. Run command: pip install -r requirements.txt
2. Download a MATCHING version to your computer's Chrome browser from (https://chromedriver.chromium.org/downloads)
2A. Find your current Chrome version by visiting this (https://www.whatismybrowser.com/detect/what-version-of-chrome-do-i-have)
3. Change global variable path to the path you've set for Chromium download from step 2
4. Download the zip from https://bmp.lightbody.net/
5. Copy path to the browsermob-proxy file in the bin folder. set the browsermobLocation to this path
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from browsermobproxy import Server
import os
import json
from dotenv import load_dotenv
import time

load_dotenv()

chromiumDriverLocation = "/Users/alexm/Documents/chromedriver"
browsermobLocation = "/Users/alexm/Documents/browsermob-proxy-2.1.4/bin/browsermob-proxy"

def load_credentials():

    credential = {
        "sf_username" : os.getenv('SF_USERNAME'),
        "sf_password": os.getenv('SF_PASSWORD'),
        "sf_login_url": os.getenv('SF_LOGIN_URL')
    }

    return credential

def create_server():
    server = Server(browsermobLocation, options={'port': 8090})
    server.start()
    return server

def create_proxy(server):
    return server.create_proxy()

def build_webdriver(proxy):
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    opts = Options()
    opts.add_argument('--ignore-certificate-errors')
    opts.add_argument('--proxy-server={0}'.format(proxy.proxy))
    opts.add_argument('--disable-gpu')

    return webdriver.Chrome(executable_path=chromiumDriverLocation, chrome_options=opts, desired_capabilities=caps)

def salesforce_login(credential, driver, proxy):
    # reminder, the proxy har needs to be called BEFORE driver is called
    proxy.new_har(credential["sf_login_url"])
    driver.get(credential["sf_login_url"])
    driver.implicitly_wait(1)

    ts = time.time()
    har_name = 'har_' + str(ts) + '.har'
    performance_name = 'performance_' + str(ts) + '.json'
    with open('./har_files/' + har_name, 'w') as har_file:
        json.dump(proxy.har, har_file)

    with open('./performance_files/' + performance_name, 'w') as performance_file:
        json.dump(driver.get_log('performance'), performance_file)

    username = driver.find_element_by_id("username")
    password = driver.find_element_by_id("password")
    login_button = driver.find_element_by_id("Login")

    username.send_keys(credential["sf_username"])
    password.send_keys(credential["sf_password"])

    login_button.click()


if __name__ == '__main__':

    # 1. Load credentials from environment variables
    credentials = load_credentials()

    # 2. Build driver with downloaded Chromium
    server = create_server()
    proxy = create_proxy(server)
    driver = build_webdriver(proxy)

    # 3. Log into Salesforce
    salesforce_login(credentials, driver, proxy)

    # 4. End both programs
    server.stop()
    driver.quit()


