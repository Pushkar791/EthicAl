import sys
import traceback
import json
import os
import importlib

def check_module(module_name):
    """Try to import a module and return error information if it fails."""
    try:
        module = importlib.import_module(module_name)
        return f"✅ Successfully imported {module_name}"
    except Exception as e:
        return f"❌ Failed to import {module_name}: {str(e)}\n{traceback.format_exc()}"

# Print Python environment information
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print("Environment variables:")
for key, value in os.environ.items():
    print(f"  {key}: {value}")

# Try to import key modules
modules_to_check = [
    'flask',
    'flask_sqlalchemy',
    'flask_login',
    'app',
    'app.models',
    'app.__init__'
]

print("\nChecking module imports:")
for module in modules_to_check:
    print(check_module(module))

# Try to create the app
print("\nTrying to create app:")
try:
    from app import create_app
    app = create_app()
    print("✅ Successfully created app")
except Exception as e:
    print(f"❌ Failed to create app: {str(e)}")
    print(traceback.format_exc())

# List directory contents to verify file structure
print("\nDirectory contents:")
for root, dirs, files in os.walk(".", topdown=True):
    if ".git" in root or "venv" in root or "__pycache__" in root:
        continue
    print(f"Directory: {root}")
    for file in files:
        print(f"  - {file}") 