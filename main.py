import json

import quart
import quart_cors
from quart import request
import requests
from bs4 import BeautifulSoup

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")

_TODOS = {}


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


@app.post("/todos/<string:username>")
async def add_todo(username):
  request = await quart.request.get_json(force=True)
  if username not in _TODOS:
    _TODOS[username] = []
  _TODOS[username].append(request["todo"])
  return quart.Response(response='OK', status=200)


@app.get("/todos/<string:username>")
async def get_todos(username):
  return quart.Response(response=json.dumps(_TODOS.get(username, [])),
                        status=200)


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

  return quart.Response(response=json.dumps({'summarized_html': website_text}),
                        status=200)


@app.delete("/todos/<string:username>")
async def delete_todo(username):
  request = await quart.request.get_json(force=True)
  todo_idx = request["todo_idx"]
  if 0 <= todo_idx < len(_TODOS[username]):
    _TODOS[username].pop(todo_idx)
  return quart.Response(response='OK', status=200)


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
