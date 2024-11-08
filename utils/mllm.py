import base64
import requests
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Messaging image
def image_qeury(query, image_path):
    base64_image = encode_image(image_path)
    # print("Base64 code >>>>", base64_image)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model":"gpt-4-vision-preview",
        "messages":[
            {
                "role":"user",
                "content":[
                    {    
                        "type":"text",
                        "text":query
                    },
                    {
                        "type":"image_url",
                        "image_url": {
                            "url":f"data:image/jpeg;base64, {base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 4096
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(response.json())
    return response.json()

print("Image Query >>>>>")
# image_qeury("What is this image?",  "1.png")