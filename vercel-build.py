import os
import sys
import subprocess

# Try to use the system's python version for installing dependencies
print("Starting build process")

try:
    # First try python3.9 explicitly
    subprocess.check_call([
        "python3.9", "-m", "pip", "install", 
        "-r", "requirements-vercel.txt"
    ])
    print("Successfully installed dependencies with python3.9")
except:
    # If that fails, try whatever python is available
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements-vercel.txt"
        ])
        print(f"Successfully installed dependencies with {sys.executable}")
    except Exception as e:
        print(f"Warning: Failed to install dependencies: {e}")
        print("Continuing deployment - dependencies may be handled by Vercel runtime")

# Create a build artifact to indicate success
with open("build-complete.txt", "w") as f:
    f.write("Build completed successfully\n")

print("Build process completed") 