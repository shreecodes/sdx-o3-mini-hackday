import os
import sys
import subprocess
import time
import webbrowser
import openai
from pathlib import Path
import re
from review_app import review_landing_page
import json

reasoning_effort = "low"

# This script is used to create a new Next.js app in the projects directory.

class NextApp:
    def __init__(self, app_name):
        self.app_name = app_name
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_dir = os.path.join(os.path.dirname(self.script_dir), "projects")
        self.app_dir = os.path.join(self.project_dir, self.app_name)
        self.dev_process = None
        self.openai_client = openai.OpenAI()  # Assumes OPENAI_API_KEY env var is set
        self.images_json_path = os.path.join(self.app_dir, 'public', 'images.json')

    def create_project_directory(self):
        os.makedirs(self.project_dir, exist_ok=True)

    def project_exists(self):
        return os.path.exists(os.path.join(self.app_dir, "package.json"))

    def create_app(self):
        if self.project_exists():
            print(f"Project {self.app_name} already exists. Skipping creation.")
            return

        print(f"Creating Next.js app in {self.project_dir}...")
        try:
            os.chdir(self.project_dir)
            create_cmd = [
                "bun", "create", "next-app", self.app_name,
                "--typescript", "--tailwind", "--eslint", "--app", "--yes"
            ]
            subprocess.run(create_cmd, check=True)
        except subprocess.CalledProcessError:
            print("Error: Failed to create Next.js app.")
            sys.exit(1)
        except OSError:
            print(f"Error: Failed to change to directory {self.project_dir}")
            sys.exit(1)

    def start_dev_server(self):
        dev_cmd = ["bun", "dev"]
        print(f"Starting development server with Bun in {self.app_dir}...")
        self.dev_process = subprocess.Popen(dev_cmd, cwd=self.app_dir)
        
        # Wait for server to boot
        time.sleep(3)

    def open_browser(self):
        print("Opening browser to http://localhost:3000...")
        webbrowser.open("http://localhost:3000")

    def read_file_content(self, file_path):
        """Read and return the contents of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    def should_include_file(self, file_path):
        """Determine if a file should be included in the prompt."""
        excluded_extensions = {'.ico', '.png', '.jpg', '.jpeg', '.gif', '.svg'}
        
        # Only include files from the app directory
        path = Path(file_path)
        if 'app' not in path.parts:
            return False
        
        return path.suffix not in excluded_extensions

    def get_app_files(self):
        """Get all relevant files from the app directory."""
        app_folder = os.path.join(self.app_dir, 'app')
        print(f"Scanning files in {app_folder}...")
        file_contents = []
        
        for root, _, files in os.walk(app_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if self.should_include_file(file_path):
                    relative_path = os.path.relpath(file_path, self.app_dir)
                    print(f"Reading file: {relative_path}")
                    content = self.read_file_content(file_path)
                    if content is not None:
                        file_contents.append(f"<file>{relative_path}\n```\n{content}\n```\n</file>")
                    else:
                        print(f"Skipping {relative_path} due to read error")
        
        print(f"Found {len(file_contents)} valid files")
        return "\n".join(file_contents)

    def extract_files_from_response(self, response_text):
        """Extract file contents from the LLM response."""
        print("Extracting files from LLM response...")
        # Look for ```language:path/to/file pattern
        file_blocks = re.finditer(r'```(?:[a-zA-Z]+:)?([^\n]+)\n(.*?)```', response_text, re.DOTALL)
        extracted_files = {}
        
        for match in file_blocks:
            file_path = match.group(1).strip()
            content = match.group(2).strip()
            print(f"Found file in response: {file_path}")
            extracted_files[file_path] = content
            
        print(f"Extracted {len(extracted_files)} files from response")
        return extracted_files

    def write_files(self, files_dict):
        """Write the generated files to disk."""
        for relative_path, content in files_dict.items():
            full_path = os.path.join(self.app_dir, relative_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {relative_path}")
            except Exception as e:
                print(f"Error writing {relative_path}: {e}")

    def load_image_descriptions(self):
        """Load existing image descriptions from JSON file."""
        if os.path.exists(self.images_json_path):
            try:
                with open(self.images_json_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_image_description(self, filename: str, description: str):
        """Save image description to JSON file."""
        os.makedirs(os.path.dirname(self.images_json_path), exist_ok=True)
        images = self.load_image_descriptions()
        images[filename] = description
        with open(self.images_json_path, 'w') as f:
            json.dump(images, f, indent=2)

    def modify_app(self, user_instruction):
        """Modify the app based on user instruction using OpenAI."""
        if not self.project_exists():
            print("Project doesn't exist. Create it first.")
            return

        # Load existing image descriptions
        existing_images = self.load_image_descriptions()
        if len(existing_images) > 0:
            existing_images_context = "<existing_images>\n"
            existing_images_context += json.dumps(existing_images, indent=2)
            existing_images_context += "\n</existing_images>\n"
        else:
            existing_images_context = ""

        # Prepare the prompt
        files_content = self.get_app_files()
        prompt = f"""You are a Next.js expert. Below are the current files in a Next.js application.
Please modify or create files based on the following instruction:

<user_instruction>
{user_instruction}
</user_instruction>

Important notes:

1. You may add images, but you must use the generate_image function to create or re-create any needed images. The image will be saved in the public directory referenced as /[image_name].png

2. When modifying or creating files, you MUST use this exact format:
   ```language:path/to/file
   // Complete content of the file goes here
   ```

3. For new files, provide the complete file contents.
   For existing files, provide the complete new contents of the file.

{existing_images_context}
<project_files>
{files_content}
</project_files>
"""

        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that modifies Next.js applications."},
                {"role": "user", "content": prompt}
            ]

            while True:
                response = self.openai_client.chat.completions.create(
                    model="o3-mini",
                    messages=messages,
                    tools=[{
                        "type": "function",
                        "function": {
                            "name": "generate_image",
                            "description": "Generate an image with the specified filename and description",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "filename": {
                                        "type": "string",
                                        "description": "The filename to save the image as (e.g. hero.png)"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Detailed description of the image to generate"
                                    }
                                },
                                "required": ["filename", "description"]
                            }
                        }
                    }],
                    tool_choice="auto",
                    reasoning_effort=reasoning_effort,
                )
                
                response_message = response.choices[0].message
                messages.append({"role": "assistant", "content": response_message.content, "tool_calls": response_message.tool_calls})

                # print(response_message.content)
                # print(response_message.tool_calls)

                # If there are no tool calls, we're done
                if not response_message.tool_calls:
                    break

                # Handle tool calls
                tool_call_responses = []
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "generate_image":
                        args = json.loads(tool_call.function.arguments)
                        print(f"\nImage Generation Request:")
                        print(f"Filename: {args['filename']}")
                        print(f"Description: {args['description']}")
                        
                        # Save the image description
                        self.save_image_description(args['filename'], args['description'])
                        
                        # Here you would actually call your image generation code
                        # self.generate_image(args['filename'], args['description'])
                        
                        tool_call_responses.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": f"Image {args['filename']} has been generated and saved to the public directory."
                        })

                # Add tool responses to messages
                messages.extend(tool_call_responses)

            # Extract and write the files from the final response
            if response_message.content:
                files_to_write = self.extract_files_from_response(response_message.content)
                if files_to_write:
                    self.write_files(files_to_write)
                    print("Files updated successfully!")
                else:
                    print("No file changes were found in the response.")
                    
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")

    def generate_image(self, filename: str, description: str):
        """Generate an image using DALL-E or another image generation service."""
        # TODO: Implement actual image generation
        print(f"Would generate image {filename} with description: {description}")
        pass

    def run(self):
        self.create_project_directory()
        self.create_app()
        print("App created successfully - run the following command to start the development server:")
        print(f"cd {self.app_dir} && bun dev")
        
        print("\nEnter modifications for your Next.js app (or 'exit' to quit):")
        
        try:
            while True:
                user_instruction = input("\nModification instruction: ").strip()
                if user_instruction.lower() in ['exit', 'quit', 'q']:
                    break
                if user_instruction:
                    self.modify_app(user_instruction)
                else:
                    print("Please enter a modification instruction or 'exit' to quit")
        
        except KeyboardInterrupt:
            print("\nInterrupt received.")
        finally:
            if self.dev_process is not None:
                self.dev_process.terminate()


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_next_app.py <app_name> [initial_instruction]")
        sys.exit(1)
    
    app = NextApp(sys.argv[1])
    app.run()


if __name__ == "__main__":
    main()