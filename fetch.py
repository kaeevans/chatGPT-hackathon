import requests

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
