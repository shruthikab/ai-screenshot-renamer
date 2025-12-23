import os
from pathlib import Path
import base64
import requests
import re

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llava")

def find_screenshots(folder: Path):
    folder = Path(folder)
    return list(folder.glob("**/Screenshot*.png")) + list(folder.glob("**/Screen Shot*.png"))

def encode_image(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def ollama_json(method: str, path: str, **kwargs):
    url = f"{OLLAMA_HOST}{path}"
    r = requests.request(method, url, timeout=kwargs.pop("timeout", 30), **kwargs)
    if not r.ok:
        # Show the real server error payload (often {"error": "..."} in Ollama)
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"{method} {url} -> {r.status_code}: {detail}")
    return r.json()

def ensure_model_available(model: str):
    tags = ollama_json("GET", "/api/tags")
    names = {m["name"] for m in tags.get("models", []) if "name" in m}
    if model not in names:
        print(f"Model '{model}' not found locally. Pulling...")
        ollama_json("POST", "/api/pull", json={"model": model, "stream": False}, timeout=600)

def generate_description(image_path: Path) -> str:
    b64 = encode_image(image_path)
    prompt = (
        "Give a short, descriptive filename for this screenshot. "
        "Keep it under 50 characters with no punctuation or emojis."
    )
    data = ollama_json(
        "POST",
        "/api/generate",
        json={"model": MODEL, "prompt": prompt, "images": [b64], "stream": False},
        timeout=120,
    )
    return (data.get("response") or "").strip()

def sanitize_filename(text: str) -> str:
    # allow letters/numbers/spaces/underscores; replace everything else with underscore
    text = re.sub(r"[^\w\s-]", "_", text).strip()
    text = re.sub(r"\s+", " ", text)
    return text[:50] if text else "screenshot"

def rename_file(file_path: Path, description: str) -> Path:
    base = sanitize_filename(description)
    new_path = file_path.with_name(f"{base}{file_path.suffix}")

    i = 1
    while new_path.exists() and new_path != file_path:
        new_path = file_path.with_name(f"{base}_{i}{file_path.suffix}")
        i += 1

    if new_path != file_path:
        file_path.rename(new_path)
    return new_path

def auto_rename_screenshots(folder: Path):
    ensure_model_available(MODEL)
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
