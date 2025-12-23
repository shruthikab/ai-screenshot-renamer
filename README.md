A Python script that automatically renames screenshot image files using AI-generated descriptions of their contents.
Instead of generic names like Screenshot 2024-01-01.png, files are renamed to something meaningful based on what the image shows.

What This Script Does
-Scans a folder for screenshot images
-Sends each image to an AI vision model
-Generates a short, descriptive filename
-Renames the image accordingly

This makes screenshots easier to search, organize, and understand later.

Requirements
-Python 3.8+
-Ollama installed and running locally
-A vision-capable Ollama model (for example: llava)

Ollama setup
-Install Ollama: https://ollama.com
-Pull a vision model: ollama pull llava
-Make sure Ollama is running: ollama serve

Usage: python screenshot_renamer.py
