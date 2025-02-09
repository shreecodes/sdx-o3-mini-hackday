import base64
import subprocess
import os
from openai import OpenAI
from datetime import datetime
from typing import List, Optional, Tuple
from PIL import Image

# Constants
OVERLAP_PERCENT = 25
MODEL_NAME = "gpt-4o"

client = OpenAI()

def encode_image(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_filenames(app_name: str) -> Tuple[str, str]:
    """Generate timestamp-based filenames for screenshot and log."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return (f"{app_name}_{timestamp}.png", f"{app_name}_{timestamp}.log")

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

def split_image(image_path: str) -> List[str]:
    """
    Split a tall image into segments with overlap.
    Returns list of paths to segment images.
    """
    with Image.open(image_path) as img:
        width, height = img.size
        
        # Only split if height > width
        if height <= width:
            return [image_path]
        
        segment_height = width
        overlap_pixels = int(segment_height * OVERLAP_PERCENT / 100)
        effective_segment_height = segment_height - overlap_pixels
        num_segments = (height - overlap_pixels) // effective_segment_height + 1
        
        base_path = os.path.splitext(image_path)[0]
        segment_paths = []
        
        for i in range(num_segments):
            start_y = i * effective_segment_height
            end_y = start_y + segment_height
            
            # Adjust last segment to include remainder
            if i == num_segments - 1:
                end_y = height
                start_y = min(start_y, height - segment_height)
            
            segment = img.crop((0, start_y, width, end_y))
            segment_path = f"{base_path}_segment_{i}.png"
            segment.save(segment_path)
            segment_paths.append(segment_path)
        
        return segment_paths

def create_vision_messages(prompt: str, segment_paths: List[str]) -> List[dict]:
    """Create messages for the vision API based on number of segments."""
    if len(segment_paths) == 1:
        return [
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
                        "image_url": {"url": f"data:image/jpeg;base64,{encode_image(segment_paths[0])}"},
                    },
                ],
            }
        ]
    
    return [
        {
            "role": "system",
            "content": "You are an expert product manager for a software company. You are given multiple segments of a tall screenshot for analysis and review. The segments have 25% overlap for context.",
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                *[
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}"},
                    }
                    for path in segment_paths
                ],
            ]
        }
    ]

def get_screenshot_analysis(image_path: str, prompt: str) -> str:
    """Get AI analysis of screenshot."""
    segment_paths = split_image(image_path)
    messages = create_vision_messages(prompt, segment_paths)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )
        
        return response.choices[0].message.content
    finally:
        # Clean up segment files if they were created
        if len(segment_paths) > 1:
            for path in segment_paths:
                if path != image_path:
                    try:
                        os.remove(path)
                    except OSError:
                        pass

def analyze_screenshot(app_name: str, prompt: str) -> str:
    """Main function to analyze screenshot or error log."""
    screenshotter_dir = os.path.join(os.path.dirname(__file__), "screenshotter")
    screenshot_filename, log_filename = generate_filenames(app_name)
    
    take_screenshot(screenshotter_dir, screenshot_filename)
    
    log_path = os.path.join(screenshotter_dir, log_filename)
    error_content = read_error_log(log_path)
    
    if error_content:
        return error_content
    
    image_path = os.path.join(screenshotter_dir, screenshot_filename)
    result = get_screenshot_analysis(image_path, prompt)
    print(result)
    return result

if __name__ == "__main__":
    analyze_screenshot("dogwalking", "Is this a user friendly landing page?")