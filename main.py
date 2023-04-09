# What are the 5 best hotels in Lake Como, Lombardy, Italy that have at least 3 rooms available June 22-25 for under $2,000 per room per night.

import json
import quart
import quart_cors
from quart import request
from bs4 import BeautifulSoup

from util import parse_json, remove_useless_tags
from selenium_driver import fetch_website_html_with_selenium
from chatgpt import ask_chatgpt
from fetch import fetch_website

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")


def getHotelWebsite(hotel):
  hotelWebsite = ask_chatgpt(
    'You know every hotel\'s website.', 'What is the website for ' + hotel +
    '? Format your response as JSON in this format: { "hotel_name": "My Hotel", "url": "https://www.myhotel.com/" }'
  )
  return json.loads(hotelWebsite)["url"]


# print(getHotelWebsite("Hotel Belvedere"))


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


def getBookingForm(form_tags):
  print("Calling getBookingForm(form_tags)...")
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
def submitBookingForm(bookingUrl, bookingRequest):
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

  bookingFormTag = getBookingForm(form_tags)
  print("bookingFormTag: " + str(remove_useless_tags(bookingFormTag))[:200])

  javascriptCode = ask_chatgpt(
    'You are an expert at writing javascript code that performs actions on this html booking form: '
    + str(bookingFormTag),
    'Write javascript code that will fill out the booking form with the following information and submit it. Only use tags that exist in the HTML booking form: '
    + f'\n startDate: {bookingRequest["startDate"]}' +
    f'\n endDate: {bookingRequest["endDate"]}' +
    f'\n numRooms: {bookingRequest["numRooms"]}' +
    f'\n numAdults: {bookingRequest["numAdults"]}' +
    'Format your response as JSON in this format: { "javascriptCode": "console.log("my javascript")" }'
  )
  print(javascriptCode)
  code = json.loads(javascriptCode)["javascriptCode"]
  return code


bookingUrl = "https://reservations.belvederebellagio.com/107984?languageid=1"
bookingUrl = "https://reservations.verticalbooking.com/premium/index.html?id_albergo=295&dc=111&lingua_int=ita&id_stile=16908"
bookingUrl = 'https://reservations.laplayahotel.com/110243?adults=2&children=0&#/datesofstay'
bookingUrl = 'https://book.webrez.com/v31/#/property/2445/location/0/search'  # The George Hotel
bookingRequest = {
  "startDate": "06/22/2023",
  "endDate": "06/25/2023",
  "numRooms": '3',
  "numAdults": '6'
}
print(submitBookingForm(bookingUrl, bookingRequest))


def everythingAllTogether(hotelName, bookingRequest):
  print(f'hotel: {hotelName}')
  hotelUrl = getHotelWebsite(hotelName)
  print(f'hotelUrl: {hotelUrl}')
  bookingUrl = getBookingUrl(hotelUrl)
  print(f'bookingUrl: {bookingUrl}')
  code = submitBookingForm(bookingUrl, bookingRequest)
  print(f'code: {code}')


hotelName = "Hotel Belvedere"
hotelName = "Mandarin Oriental Lake Como"
hotelName = "Villa Flori Lago di como"
hotelName = "Stanford Inn in Mendocino"
hotelName = "La Playa Carmel"
# everythingAllTogether(hotelName, bookingRequest)


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
