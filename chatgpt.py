import os
import openai

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

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
