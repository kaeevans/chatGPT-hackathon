import json


def parse_json(json_string):
  try:
    # Attempt to parse the JSON string
    if len(json_string) > 0:
      if json_string[0] != '{' and '{' in json_string:
        json_string = json_string[json_string.index('{'):]
      if json_string[-1] != '}' and '}' in json_string:
        json_string = json_string[:json_string.rindex('}') + 1]
    #print(f'parsing {json_string}')
    data = json.loads(json_string)
    return data
  except json.JSONDecodeError as e:
    # Handle the exception if the JSON string is invalid
    print(f"An error occurred while decoding the JSON string: {e}")
    return None


def remove_useless_tags(bs4_tag):
  useless_tags = ['svg']
  for useless in useless_tags:
    matches = bs4_tag.find_all(useless)
    if matches:
      for m in matches:
        m.decompose()
  return bs4_tag



def get_actions(soup):
  anchor_tags = soup.find_all('a')
  output = []
  for anchor in anchor_tags:
    link = anchor.get('href')
    description = anchor.text.strip()
    output.append({'url': link, 'action_description': description})
  return output
