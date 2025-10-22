#!/bin/bash
set -e

# This script is designed to automate the deployment of a Docker Compose application.
# It stops current containers, pulls the latest code, rebuilds the images,
# and starts the new containers.

# 1. Stop and remove the old containers
# We run this first to free up ports and resources.
echo "Shutting down existing containers..."
docker compose down

# 2. Pull the latest code from your repository
# Assumes you are on the 'main' branch. Change 'main' to 'master' or your default branch if different.
echo "Pulling latest code from git repository..."
git pull origin master

# 3. Build the new images
# This will rebuild any services that have changed since the last build.
echo "Building new Docker images..."
docker compose build

# 4. Start the new containers
# '-d' runs the containers in detached mode (in the background).
echo "Starting new containers..."
docker compose up -d

echo "Deployment finished successfully!"
