
import os
from pathlib import Path
from openai import OpenAI
from PIL import Image
import base64
import re

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def find_screenshots(folder):
    folder = Path(folder)
    return list(folder.glob("**/Screenshot*.png")) + list(folder.glob("**/Screen Shot*.png"))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_description(image_path):
   base64_image = encode_image(image_path)

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[
           {
               "role": "user",
               "content": [
                   {"type": "text", "text": "Give a short, descriptive filename for this screenshot (like 'recent US news' or 'zoom meeting with 3 people'). Keep it under 50 characters with no punctuation or emojis."},
                   {"type": "image_url","image_url": {"url": f"data:image/png;base64,{base64_image}"}},
               ],
           }
       ],
       max_tokens = 50,
   )
   return response.choices[0].message.content

def sanitize_filename(text):
    return re.sub (r'[\\/*?:"<>|]', "_", text)[:50]

def rename_file(file_path, description):
    sanitized = sanitize_filename(description)
    new_path = file_path.with_name(f"{sanitized}{file_path.suffix}")
    file_path.rename(new_path)
    return new_path

def auto_rename_screenshots(folder):
    screenshots = find_screenshots(folder)
    for shot in screenshots:
        try:
            print(f"Processing {shot.name}")
            description = generate_description(shot)
            new_file = rename_file(shot, description)
            print(f"Renamed to {new_file.name}")
        except Exception as e:
            print(f"Error processing {shot.name}: {e}")

if __name__ == "__main__":
    desktop_folder = Path.home() / "Desktop"
    auto_rename_screenshots(desktop_folder)