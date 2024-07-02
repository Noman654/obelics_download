import base64
import requests
import os
import argparse
import glob
from pathlib import Path
# OpenAI API Key
API_KEY = os.getenv("OPENAI_API_KEY")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def wrapper(image_path, prompt, max_tokens:int = 1000):
    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
    "model": "gpt-4-vision-preview", #gpt-4o
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt
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
    "max_tokens": max_tokens
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # print(response.json()["choices"][0]["message"]["content"])
    return response.json()["choices"][0]["message"]["content"]


def parse_args() -> argparse.Namespace:
    """
    Parse cli arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image_dir", type=str, default="/mnt/disk2/shubham/hf_home/sample_images/", help="Local dir")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    # Path to your image
    config = parse_args()
    image_dir = config.image_dir

    prompt = f"""You are a helpful assistant. You are helping create a red teaming dataset for alignment training
                 Multimodal vision language model. You will be provided an image. Your task is to first provide a 
                 detailed description of the image. You should also create a synthetic dialog with user and model
                 turns where the user asks irrelevant questions and the system provides a correct answer or politely
                 corrects the user. For example, with a cat in the image, the user may ask what is the dog doing here. 
                 The system in this case must say that there is no cat in the image but a brown dog sitting. 
                 Provide the output in a json with keys as `caption` and `dialog`. Dialog must be a list with user and 
                 assistant turns. Do not provide anything else only the json result. \n\n JSON: \n\n """

    # files = glob.glob(f'{image_path}/.jpeg',  
    #                 recursive = True) 
    # for file in files[0]: 
    print(image_dir)
    images = Path(image_dir).glob('*.png')
    for image_path in images:
        print(image_path)
        wrapper(image_path, prompt)

    