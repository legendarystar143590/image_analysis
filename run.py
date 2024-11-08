import base64
import pathlib
from pathlib import Path
import time
from dotenv import load_dotenv
import os
from openai import OpenAI
import json

client = OpenAI()

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def read__text_file(filepath):
    """Reads the entire content of a file into a string."""
    try:
        with open(filepath, 'r') as file:  # 'r' mode for reading (default)
            content = file.read()
        return content
    except FileNotFoundError:
        return None  # Or handle the error as needed

def read_json_file(filepath):
    """Reads JSON data from a file and returns a Python object."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return None
    
def get_file_paths(directory):
    """Gets file paths recursively using pathlib."""
    file_paths = [str(path) for path in pathlib.Path(directory).rglob('*') if path.is_file()]
    return file_paths
    
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def get_filename_without_extension_pathlib(filepath):
    """Extracts the filename (without extension) using pathlib."""
    path = Path(filepath)
    return path.stem

def get_filename_pathlib(filepath):
    """Extracts the filename (with extension) using pathlib."""
    path = Path(filepath)
    return path.name

def create_and_save_json(data, filepath):
    """Creates a JSON file if it doesn't exist and saves data to it."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        # If data is a string, replace single quotes with double quotes
        if isinstance(data, str):
            # Replace single quotes with double quotes, but only for JSON structure
            data = data.replace("'", '"')
        
        # Convert string to JSON if it's a string
        json_data = json.loads(data) if isinstance(data, str) else data
        print(json_data)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"JSON file '{filepath}' created and data saved.")
    except Exception as e:
        print(f"Error creating or saving to JSON file: {e}")

#  Single analyze image
def analyze_image(image_path):
    base64_image = encode_image(image_path)
    file_full_name = get_filename_pathlib(image_path)
    file_name = get_filename_without_extension_pathlib(image_path)
    query = f"""###Analyze the image and describe the scene in detail with follow categories: Background, Hair, Top, Kethcup, Weapon, Accessories, Mood, Rating.
        ###{items}
        ###This is output json format: {formats}
        ###The filename is: {file_full_name}
        ###Important: Return ONLY the raw JSON object without any markdown formatting, code block symbols, or additional text.
        ###Do not include ```json or ``` in your response.
        ###You must be serious with colors because most of items describes the color. Be more sensitive with colors.
    """
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": query,
            },
            {
            "type": "image_url",
            "image_url": {
                "url":  f"data:image/png;base64,{base64_image}"
            },
            },
        ],
        }
    ],
    )
    result = response.choices[0].message.content
    create_and_save_json(result, f"results/{file_name}.json")

#  Batch analyze images
def analyze_images_batch(image_paths, batch_size=10):
    """Analyzes multiple images in a single API call"""
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""###Analyze these images and describe each scene in detail with follow categories: Background, Hair, Top, Kethcup, Weapon, Accessories, Mood, Rating.
                        ###{items}
                        ###This is output json format: {formats}
                        ###Important: Return ONLY an array of JSON objects, one for each image, without any markdown formatting.
                        ###Do not include ```json or ``` in your response.
                        ###Each object should include the filename."""
                }
            ]
        }
    ]
    
    # Add each image to the message content
    for image_path in image_paths:
        base64_image = encode_image(image_path)
        file_name = get_filename_pathlib(image_path)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",  # Make sure to use the correct model name
        messages=messages,
        max_tokens=3000,  # Adjust based on your needs
    )

    result = response.choices[0].message.content
    # Clean the result and parse JSON
    result = result.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    
    # Parse and save individual results
    results = json.loads(result.replace("'", '"'))
    for item in results:
        file_name = item.get('fileName', '').split('.')[0]
        if file_name:
            create_and_save_json(item, f"results/{file_name}.json")
            

# Start processing         
items = read__text_file("1.txt")
formats = read_json_file("1.json")
file_paths = get_file_paths("images")

for file_path in file_paths:
    analyze_image(file_path)
    time.sleep(17)
