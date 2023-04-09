import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')


def fetch_website_html_with_selenium(url):
  driver = webdriver.Chrome(options=chrome_options)
  driver.get(url)
  driver.implicitly_wait(2.0)

  # return the new HTML of the page
  source = driver.page_source
  driver.quit()
  return source


# def try_selenium(url, keyboard_form_values, click_actions):
#   driver = webdriver.Chrome(options=chrome_options)

#   driver.get(url)
#   driver.implicitly_wait(0.5)

#   for (form_name, form_value) in keyboard_form_values:
#     try:
#       element = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=form_name)
#       if element:
#         element.send_keys(form_value)
#     except selenium.common.exceptions.NoSuchElementException:
#       pass

#   for action in click_actions:
#     element = driver.find_element(by=By.PARTIAL_LINK_TEXT,
#                                   value=action['action_description'])
#     if element:
#       element.click()

#   # return the new HTML of the page
#   source = driver.page_source
#   driver.quit()
#   return source

#try_selenium("https://google.com", [("search", "this is my google search")], "search")
# try_selenium("https://reservations.belvederebellagio.com/107984?languageid=1", [("search", "this is my google search")], "search")
