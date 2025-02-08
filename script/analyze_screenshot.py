import base64
import subprocess
import os
from openai import OpenAI

client = OpenAI()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_screenshot(prompt):
  # Take screenshot first
  screenshotter_dir = os.path.join(os.path.dirname(__file__), "screenshotter")
  subprocess.run(["bun", "run", "index.ts"], cwd=screenshotter_dir, check=True)

  # Path to your image
  image_path = "screenshotter/screenshot.png"

  # Getting the Base64 string
  base64_image = encode_image(image_path)

  response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
          {
              "role": "system",
              "content": "You are a product manager for a software company. You are given a screenshot of a project for analysis.",
          },
          {
              "role": "user",
              "content": [
                  {
                      "type": "text",
                      "text": prompt,
                  },
                  {
                      "type": "image_url",
                      "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                  },
              ],
          }
      ],
  )

  print(response.choices[0])

analyze_screenshot("What is in this image?")