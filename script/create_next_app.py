import os
import sys
import subprocess
import time
import webbrowser


# This script is used to create a new Next.js app in the projects directory.

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_next_app.py <app_name>")
        sys.exit(1)
    
    app_name = sys.argv[1]
    # Get the script's directory and construct the project path relative to it
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(os.path.dirname(script_dir), "projects")
    
    # create a new directory for the project
    os.makedirs(project_dir, exist_ok=True)

    # Check if the 

    # Use Bun to create a Next.js app in the project directory.
    # This command will generate the app using the template.
    print(f"Creating Next.js app in {project_dir}...")
    try:
        # Change to the project directory
        os.chdir(project_dir)
        # Run bun init
        create_cmd = ["bun", "create", "next-app", app_name, "--typescript", "--tailwind", "--eslint", "--app", "--yes"]
        subprocess.run(create_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to create Next.js app.")
        sys.exit(1)
    except OSError as e:
        print(f"Error: Failed to change to directory {project_dir}")
        sys.exit(1)
    
    # Start the development server.
    # We assume that "bun run dev" starts the Next.js dev server.
    dev_cmd = ["bun", "dev"]
    app_dir = os.path.join(project_dir, app_name)
    print(f"Starting development server with Bun in {app_dir}...")
    # Start the server as a subprocess, using the newly created app's folder as the working directory.
    dev_proc = subprocess.Popen(dev_cmd, cwd=app_dir)
    
    # Wait a short period to give the server time to boot up.
    time.sleep(5)
    
    # Open the default web browser to the Next.js app URL (usually localhost:3000).
    print("Opening browser to http://localhost:3000...")
    webbrowser.open("http://localhost:3000")
    
    # Wait for the dev server process to exit.
    try:
        dev_proc.wait()
    except KeyboardInterrupt:
        print("\nInterrupt received; stopping the development server.")
        dev_proc.terminate()

if __name__ == "__main__":
    main()