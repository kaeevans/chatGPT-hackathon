import os
import json

import quart
import quart_cors
from quart import request
import requests
from bs4 import BeautifulSoup
import openai

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

openai.api_key = OPENAI_API_KEY
#openai.organization = OPENAI_ORG_ID

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")

#_TODOS = {}


def try_selenium(url, keyboard_form_values, click_actions):
  import selenium
  from selenium import webdriver
  from selenium.webdriver.common.by import By
  from selenium.webdriver.chrome.options import Options
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')
  #chrome_options.headless = True

  driver = webdriver.Chrome(options=chrome_options)

  driver.get(url)
  driver.implicitly_wait(0.5)

  for (form_name, form_value) in keyboard_form_values:
    try:
      element = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=form_name)
      if element:
        element.send_keys(form_value)
    except selenium.common.exceptions.NoSuchElementException:
      pass

  for action in click_actions:
    element = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=action)
    if element:
      element.click()

  # return the new HTML of the page
  source = driver.page_source
  driver.quit()
  return source


try_selenium("https://google.com", [("search", "this is my google search")], "search")


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


def fetch_website(url):
  try:
    # Make an HTTP GET request to the specified URL
    response = requests.get(url)

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


# Example usage
#url = "https://www.example.com/"
#website_content = fetch_website(url)
#print(website_content)

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


def get_actions(soup):
  anchor_tags = soup.find_all('a')
  output = []
  for anchor in anchor_tags:
    link = anchor.get('href')
    description = anchor.text.strip()
    output.append({'url': link, 'action_description': description})
  return output


@app.post("/website/<string:username>")
async def get_website(username):
  request = await quart.request.get_json(force=True)
  url = request['url']
  print(f'url is {url}')
  website_html = fetch_website(url)
  print(f'website_text is {website_html[:300]}')

  soup = BeautifulSoup(website_html, 'html.parser')
  # The 'get_text' method removes all HTML tags and returns the text content
  website_text = soup.get_text()
  print(f'website_text is {website_text[:300]}')

  available_actions = get_actions(soup)

  return quart.Response(response=json.dumps({
    'summarized_html': website_text,
    'actions': available_actions
  }),
                        status=200,
                        content_type='application/json')


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
