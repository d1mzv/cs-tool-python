# # Import libraries
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd

# # Create an URL object
# url = 'https://novi-nadebook.notion.site/61fe071adcfc42aba900d2bdb058926d?v=9ba9a8859d7247c7839f44eb8c392e01'
# # Create object page
# page = requests.get(url, timeout=10)

# # parser-lxml = Change html to Python friendly format
# # Obtain page's information
# soup = BeautifulSoup(page.text, 'lxml')
# print(soup)

# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as ec
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException
# from bs4 import BeautifulSoup

# options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# # executable_path param is not needed if you updated PATH
# browser = webdriver.Chrome(
#     options=options, executable_path='YOUR_PATH/chromedriver.exe')


# try:
#     browser.get(
#         "https://novi-nadebook.notion.site/61fe071adcfc42aba900d2bdb058926d?v=9ba9a8859d7247c7839f44eb8c392e01")
#     timeout_in_seconds = 10
#     WebDriverWait(browser, timeout_in_seconds).until(
#         ec.presence_of_element_located((By.CLASS_NAME, "notion-selectable notion-collection_view_page-block")))
#     html = browser.page_source
#     soup = BeautifulSoup(html, features="html.parser")
#     print(soup)
# except TimeoutException:
#     print("I give up...")
# finally:
#     browser.quit()

from requests_html import HTMLSession
from bs4 import BeautifulSoup
s = HTMLSession()
response = s.get(
    'https://novi-nadebook.notion.site/61fe071adcfc42aba900d2bdb058926d?v=9ba9a8859d7247c7839f44eb8c392e01/')
response.html.render(sleep=10, timeout=10)
# item = response.html.find(
#     'notion-selectable notion-collection_view_page-block', first=True)
soup = BeautifulSoup(response.html.html, 'lxml')

print(soup)

# import dryscrape
# from bs4 import BeautifulSoup
# session = dryscrape.Session()
# session.visit(
#     'https://novi-nadebook.notion.site/61fe071adcfc42aba900d2bdb058926d?v=9ba9a8859d7247c7839f44eb8c392e01')
# response = session.body()
# soup = BeautifulSoup(response)
# soup.find_all()
# print(soup)
