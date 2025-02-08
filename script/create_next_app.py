import os
import sys
import subprocess
import time
import webbrowser
import openai
from pathlib import Path
import re


# This script is used to create a new Next.js app in the projects directory.

class NextApp:
    def __init__(self, app_name):
        self.app_name = app_name
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_dir = os.path.join(os.path.dirname(self.script_dir), "projects")
        self.app_dir = os.path.join(self.project_dir, self.app_name)
        self.dev_process = None
        self.openai_client = openai.OpenAI()  # Assumes OPENAI_API_KEY env var is set

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
        excluded_directories = {'.git', 'node_modules', '.next'}
        
        path = Path(file_path)
        if any(part in excluded_directories for part in path.parts):
            return False
        return path.suffix not in excluded_extensions

    def get_app_files(self):
        """Get all relevant files from the app directory."""
        print(f"Scanning files in {self.app_dir}...")
        file_contents = []
        for root, _, files in os.walk(self.app_dir):
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

    def modify_app(self, user_instruction):
        """Modify the app based on user instruction using OpenAI."""
        if not self.project_exists():
            print("Project doesn't exist. Create it first.")
            return

        # Prepare the prompt
        files_content = self.get_app_files()
        prompt = f"""You are a Next.js expert. Below are the current files in a Next.js application.
Please modify or create files based on the following instruction:

{user_instruction}

Current files:
{files_content}

Respond with the complete content of any files that should be modified or created.
Use the format ```language:path/to/file for each file, where language is the appropriate
language identifier (tsx, css, etc) and path/to/file is the path relative to the app root.
"""

        try:
            response = self.openai_client.chat.completions.create(
                model="o3-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that modifies Next.js applications."},
                    {"role": "user", "content": prompt}
                ],
                reasoning_effort="low",
            )
            
            # Extract and write the files
            files_to_write = self.extract_files_from_response(response.choices[0].message.content)
            if files_to_write:
                self.write_files(files_to_write)
                print("Files updated successfully!")
            else:
                print("No file changes were found in the response.")
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")

    def run(self):
        self.create_project_directory()
        self.create_app()
        
        # Add optional modification step
        if len(sys.argv) > 2:
            user_instruction = " ".join(sys.argv[2:])
            self.modify_app(user_instruction)
        
        self.start_dev_server()
        self.open_browser()
        
        try:
            self.dev_process.wait()
        except KeyboardInterrupt:
            print("\nInterrupt received; stopping the development server.")
            self.dev_process.terminate()


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_next_app.py <app_name>")
        sys.exit(1)
    
    app = NextApp(sys.argv[1])
    app.run()


if __name__ == "__main__":
    main()