import base64
import subprocess
import os
from openai import OpenAI
from datetime import datetime
from typing import Optional

client = OpenAI()

def encode_image(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_filenames(app_name: str) -> tuple[str, str]:
    """Generate timestamp-based filenames for screenshot and log."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return (
        f"{app_name}_{timestamp}.png",
        f"{app_name}_{timestamp}.log"
    )

def take_screenshot(screenshotter_dir: str, screenshot_filename: str) -> None:
    """Capture screenshot using the screenshotter tool."""
    subprocess.run(
        ["bun", "run", "index.ts", screenshot_filename], 
        cwd=screenshotter_dir, 
        check=True
    )

def read_error_log(log_path: str) -> Optional[str]:
    """Read error log if it exists and has content."""
    if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
        with open(log_path, 'r') as log_file:
            return log_file.read()
    return None


def get_screenshot_analysis(image_path: str, prompt: str) -> str:
    """Get AI analysis of screenshot."""
    base64_image = encode_image(image_path)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert product manager for a software company. You are given a screenshot of a project for analysis and review.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content

def analyze_screenshot(app_name: str, prompt: str) -> str:
    """Main function to analyze screenshot or error log."""
    # Setup paths and filenames
    screenshotter_dir = os.path.join(os.path.dirname(__file__), "screenshotter")
    screenshot_filename, log_filename = generate_filenames(app_name)
    
    # Take screenshot
    take_screenshot(screenshotter_dir, screenshot_filename)
    
    # Check for errors
    log_path = os.path.join(screenshotter_dir, log_filename)
    error_content = read_error_log(log_path)
    
    if error_content:
        result = error_content
    else:
        image_path = os.path.join(screenshotter_dir, screenshot_filename)
        result = get_screenshot_analysis(image_path, prompt)
    
    print(result)
    return result

if __name__ == "__main__":
    analyze_screenshot("dogwalking", "Is this a user friendly landing page?")