
import os
from pathlib import Path
import base64, requests
from PIL import Image
import base64
import re

#client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def find_screenshots(folder):
    folder = Path(folder)
    return list(folder.glob("**/Screenshot*.png")) + list(folder.glob("**/Screen Shot*.png"))

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_description(image_path):
    b64 = encode_image(image_path)
    prompt = ("Give a short, descriptive filename for this screenshot "
              "Keep it under 50 characters with no punctuation or emojis")
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llava", "prompt": prompt, "images": [b64], "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["response"].strip()

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
    