#!/bin/bash

# Ensure Python 3.9 is used
export PYTHON_VERSION=3.9

# Install dependencies from our custom requirements file
python3.9 -m pip install -r requirements-vercel.txt

# Create empty file to indicate build success
echo "Build completed" > build.txt 