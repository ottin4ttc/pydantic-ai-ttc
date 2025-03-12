#!/bin/bash
# build.sh

# Build the React app
npm run build

# Create a static directory in the FastAPI app if it doesn't exist
mkdir -p ../static

# Copy the build files to the static directory
cp -r dist/* ../static/

echo "React app built and copied to FastAPI static directory"
