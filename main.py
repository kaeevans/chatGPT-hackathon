# What are the 5 best hotels in Lake Como, Lombardy, Italy that have at least 3 rooms available June 22-25 for under $2,000 per room per night.

import os
import json

import quart
import quart_cors
from quart import request
import requests
from bs4 import BeautifulSoup
import openai
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from util import parse_json, remove_useless_tags

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
#chrome_options.headless = True

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

openai.api_key = OPENAI_API_KEY

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")

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


def ask_chatgpt(system_prompt, user_prompt):
  raw_verdict = openai.ChatCompletion.create(  # type: ignore
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "system",
        "content": system_prompt,
      },
      {
        "role": "user",
        "content": user_prompt,
      },
    ],
    temperature=0.2,
  )
  verdict_result = raw_verdict["choices"][0]["message"]["content"]
  return verdict_result


#print(ask_chatgpt('do math', 'what is 1+1'))


def fetch_website_html_with_selenium(url):
  driver = webdriver.Chrome(options=chrome_options)
  driver.get(url)
  driver.implicitly_wait(2.0)

  # return the new HTML of the page
  source = driver.page_source
  driver.quit()
  return source


def fetch_website(url):
  try:
    # Make an HTTP GET request to the specified URL
    response = requests.get(url, timeout=5, allow_redirects=True)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
      # Return the content of the website
      return response.text
    else:
      # If the request was not successful, return an error message
      return f"An error occurred: {response.status_code}"
  except requests.exceptions.RequestException as e:
    # Handle any exceptions that occur during the request
    return f"An exception occurred: {e}"


# url = "https://www.example.com/"
# print(fetch_website(url))


def getHotelWebsite(hotel):
  hotelWebsite = ask_chatgpt(
    'You know every hotel\'s website.', 'What is the website for ' + hotel +
    '? Format your response as JSON in this format: { "hotel_name": "My Hotel", "url": "https://www.myhotel.com/" }'
  )
  return json.loads(hotelWebsite)["url"]


# print(getHotelWebsite("Hotel Belvedere"))


def get_actions(soup):
  anchor_tags = soup.find_all('a')
  output = []
  for anchor in anchor_tags:
    link = anchor.get('href')
    description = anchor.text.strip()
    output.append({'url': link, 'action_description': description})
  return output


def getBookingUrl(hotelUrl):
  print("getting booking url...")
  # print(f'hotelUrl: {hotelUrl}')
  website_html = fetch_website(hotelUrl)
  print(f'website_html: {website_html[:300]}')

  soup = BeautifulSoup(website_html, 'html.parser')
  # The 'get_text' method removes all HTML tags and returns the text content
  # website_text = soup.get_text()
  # print(f'website_text is {website_text[:300]}')

  available_actions = get_actions(soup)
  # print(available_actions)

  chat_gpt_response = ask_chatgpt(
    'You have a list of urls and a description of what each url does: ' +
    str(available_actions),
    'Give me the most likely url that I can use to book. Format your response as JSON in this format: { "booking_url": "https://www.myhotel.com/book" }'
  )
  # print(bookingUrl)
  response = parse_json(chat_gpt_response)
  if response:
    return response.get('booking_url')
  else:
    print(f'ChatGPT failed and said: {chat_gpt_response}')


# hotelUrl = "https://www.belvederebellagio.com/en"
# print(getBookingUrl(hotelUrl))

# def getBookingForm(form_tags):
#   forms_with_scores = []
#   # Loop through each <form> tag and extract its contents
#   for i, form_tag in enumerate(form_tags, start=1):
#     form_tag = remove_useless_tags(form_tag)
#     contents = str(form_tag)
#     print(f"Contents of form {i} are {len(contents)} chars long:")
#     print(f'form contents: {contents[:50]}')

#     isBookingForm = ask_chatgpt(
#       '',
#       'I have the html for a form element from a hotel website:' + contents +
#       'There could be multiple forms on the hotel website. Given the information you have, rate the probability from 0.0 to 1.0, where 1.0 is 100% certainty, that this form could be used to reserve or book a room at the hotel? Format your response as JSON in this format: { "isCorrectForm": 0.5 }.'
#     )
#     response_as_json = parse_json(isBookingForm)
#     print(response_as_json)
#     if response_as_json:
#       score = float(response_as_json.get('isCorrectForm', 0.0))
#       print(f'form score is: {score}')
#       forms_with_scores.append((score, contents))

#   # pick the best form
#   best_contents, best_score = sorted(forms_with_scores)[-1]
#   return best_contents


def getBookingForm2(form_tags):
  print("Calling getBookingForm2(form_tags)...")
  # Loop through each <form> tag and extract its contents
  formSummaries = []
  for i, form_tag in enumerate(form_tags, start=1):
    contents = str(remove_useless_tags(form_tag))
    # print(f"Contents of form {i} are {len(contents)} chars long:")
    # print(f'form contents: {contents[:50]}')

    formSummary = ask_chatgpt(
      '',
      'Without any additional context, do your best to describe what this form does. Here is the HTML for the form:'
      + contents)
    formSummaries.append(formSummary)
    # print("form " + str(i) + ": " + formSummary[:100])
    # print()
  bookingFormIndex = ask_chatgpt(
    '',
    'Given the descriptions of multiple forms on a hotel\'s website, which form  is most likely to be the one for booking/reserving a room at the hotel? Format your response as JSON in this format: { "bookingFormIndex": 27 } Here are the form descriptions: '
    + ",".join(formSummaries))
  # + "\n".join([f'Form #{i}: {s}' for i, s in enumerate(formSummaries)]))
  # print(bookingFormIndex)
  i = int(parse_json(bookingFormIndex).get('bookingFormIndex'))
  return form_tags[i]


# https://reservations.belvederebellagio.com/107984?languageid=1#/guestsandrooms
def submitBookingForm(bookingUrl):
  print("bookingUrl: " + bookingUrl)
  #website_html = fetch_website(bookingUrl)
  website_html = fetch_website_html_with_selenium(bookingUrl)

  # print(website_html[:1000])
  soup = BeautifulSoup(website_html, 'html.parser')

  print("looking for form tags...")
  # Find all <form> tags
  form_tags = soup.find_all('form')
  if len(form_tags) == 0:
    print("no form tags found")
    return
  print(f'found {len(form_tags)} form tags')

  bookingFormTag = getBookingForm2(form_tags)
  print("bookingFormTag: " + str(bookingFormTag))

  startDate = "06/22/2023"
  endDate = "06/25/2023"
  numRooms = '3'
  numAdults = '6'
  javascriptCode = ask_chatgpt(
    'You are an expert at writing javascript code that performs actions on this html booking form: '
    + str(bookingFormTag),
    'Write javascript code that will fill out the booking form with the following information and submit it. Only use tags that exist in the HTML booking form: '
    + f'\n startDate: {startDate}' + f'\n endDate: {endDate}' +
    f'\n numRooms: {numRooms}' + f'\n numAdults: {numAdults}' +
    'Format your response as JSON in this format: { "javascriptCode": "console.log("my javascript")" }'
  )
  print(javascriptCode)
  code = json.loads(javascriptCode)["javascriptCode"]
  return code


bookingUrl = "https://reservations.belvederebellagio.com/107984?languageid=1"
bookingUrl = "https://reservations.verticalbooking.com/premium/index.html?id_albergo=295&dc=111&lingua_int=ita&id_stile=16908"
bookingUrl = 'https://reservations.laplayahotel.com/110243?adults=2&children=0&#/datesofstay'
bookingUrl = 'https://book.webrez.com/v31/#/property/2445/location/0/search'  # The George Hotel
print(submitBookingForm(bookingUrl))


def everythingAllTogether(hotelName):
  print(f'hotel: {hotelName}')
  hotelUrl = getHotelWebsite(hotelName)
  print(f'hotelUrl: {hotelUrl}')
  bookingUrl = getBookingUrl(hotelUrl)
  print(f'bookingUrl: {bookingUrl}')
  code = submitBookingForm(bookingUrl)
  print(f'code: {code}')


hotelName = "Hotel Belvedere"
hotelName = "Mandarin Oriental Lake Como"
hotelName = "Villa Flori Lago di como"
hotelName = "Stanford Inn in Mendocino"
hotelName = "La Playa Carmel"
# everythingAllTogether(hotelName)


@app.post("/website/<string:username>")
async def get_website(username):
  request = await quart.request.get_json(force=True)
  url = request['url']
  print(f'url is {url}')
  website_html = fetch_website(url)
  # print(f'website_text is {website_html[:300]}')

  soup = BeautifulSoup(website_html, 'html.parser')
  # The 'get_text' method removes all HTML tags and returns the text content
  website_text = soup.get_text()
  # print(f'website_text is {website_text[:300]}')

  available_actions = get_actions(soup)

  return quart.Response(
    response=json.dumps({
      'summarized_html': website_text,
      'actions': available_actions
    }),
    # status=200,
    content_type='application/json')


@app.post("/hotel/<string:username>")
async def get_hotel_availability(username):
  print(username)
  request = await quart.request.get_json(force=True)
  url = request['url']

  bookingUrl = getBookingUrl(url)

  return quart.Response(response=json.dumps({
    'availability': bookingUrl,
  }),
                        status=200,
                        content_type='application/json')


#@app.post("/todos/<string:username>")
#async def add_todo(username):
#  request = await quart.request.get_json(force=True)
#  if username not in _TODOS:
#    _TODOS[username] = []
#  _TODOS[username].append(request["todo"])
#  return quart.Response(response='OK', status=200)

#@app.get("/todos/<string:username>")
#async def get_todos(username):
#  return quart.Response(response=json.dumps(_TODOS.get(username, [])),
#                        status=200)

#@app.delete("/todos/<string:username>")
#async def delete_todo(username):
#  request = await quart.request.get_json(force=True)
#  todo_idx = request["todo_idx"]
#  if 0 <= todo_idx < len(_TODOS[username]):
#    _TODOS[username].pop(todo_idx)
#  return quart.Response(response='OK', status=200)


@app.get("/logo.png")
async def plugin_logo():
  filename = 'logo.png'
  return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
  host = request.headers['Host']
  with open("ai-plugin.json") as f:
    text = f.read()
    # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the manifest
    text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
    return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
  host = request.headers['Host']
  print("hiiii")
  with open("openapi.yaml") as f:
    text = f.read()
    # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
    text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
    return quart.Response(text, mimetype="text/yaml")


def main():
  app.run(debug=True, host="0.0.0.0", port=5002)


if __name__ == "__main__":
  main()
