import base64
import requests
import pandas as pd
from time import sleep
import warnings
warnings.filterwarnings('ignore')
# OpenAI API Key
api_key = "put-key"


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


import os
img_root_dir = '/Users/abhinav.ravi/Downloads/diwali/'
file_names = os.listdir(img_root_dir)

save_file_name = './gpt4o_results_4k_onwards.csv'
if os.path.exists(save_file_name):
    os.remove(save_file_name)


# Getting the base64 string
def get_response(image_path, api_key):
    base64_image = encode_image(image_path)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    payload = {
      "model": "gpt-4o", # #gpt-4-vision-preview
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Pls suggest a few lines description for this image which would be fed into a vision language model for image generation task."
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response = response.json()
    response = response['choices'][0]['message']['content']
    return response

df = pd.DataFrame(columns=['image_name', 'description'])

for i, curr_file in enumerate(file_names[4000:]):
    try: 
        image_path = img_root_dir + curr_file
        response = get_response(image_path, api_key)
        print(i, response)
        df = df.append({'image_name': curr_file, 'description':response}, ignore_index=True)
        if(i % 4 ==0):
            df.to_csv(save_file_name, index=False)
        sleep(1)
    except Exception as ex:
        print(ex)
        sleep(10)




