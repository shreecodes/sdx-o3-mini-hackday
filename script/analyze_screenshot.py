import base64
import subprocess
import os
from openai import OpenAI
from datetime import datetime

client = OpenAI()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_screenshot(prompt):
    # Generate timestamp filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_filename = f"screenshot_{timestamp}.png"
    
    # Take screenshot first
    screenshotter_dir = os.path.join(os.path.dirname(__file__), "screenshotter")
    subprocess.run(["bun", "run", "index.ts", screenshot_filename], cwd=screenshotter_dir, check=True)

    # Path to your image
    image_path = os.path.join(screenshotter_dir, screenshot_filename)

    # Getting the Base64 string
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a product manager for a software company. You are given a screenshot of a project for analysis and review.",
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

    print(response.choices[0].message.content)
    return response.choices[0].message.content

analyze_screenshot("Is this a user friendly landing page?")