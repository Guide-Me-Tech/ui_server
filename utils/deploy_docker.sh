#!/usr/bin/env bash

# Janis Rubins step 1: Enable strict mode for reliability
# -e: exit on error
# -u: treat unset variables as errors
# -o pipefail: pipelines fail on first error
set -euo pipefail

# Janis Rubins step 2: Define variables for flexibility
# These variables can be changed easily without modifying code logic
IMAGE_NAME="${IMAGE_NAME:-ui_server}"
CONTAINER_NAME="${CONTAINER_NAME:-ui_server}"
DOCKERFILE="${DOCKERFILE_PATH:-docker/Dockerfile}"
TZ_VALUE="${TZ_VALUE:-Asia/Tashkent}"
MEMORY_LIMIT="${MEMORY_LIMIT:-512m}"
CPU_LIMIT="${CPU_LIMIT:-0.5}"
CODE_PATH="${CODE_PATH:-$(pwd)/src/server.py}"
CONFIG_PATH="${CONFIG_PATH:-$(pwd)/configs}"

# Janis Rubins step 3: Add optional build arguments for flexibility
# If we need to integrate with external resources, we can do so by passing BUILD_ARGS
BUILD_ARGS=${BUILD_ARGS:-}

# Janis Rubins step 4: Build image with flexibility and no-cache option
# --pull ensures latest base image, improving security and patch level
docker build --pull --no-cache ${BUILD_ARGS} -f "$DOCKERFILE" -t "$IMAGE_NAME" .

# Janis Rubins step 5: Stop and remove existing container if present
# || true prevents error if container doesn't exist
docker container stop "$CONTAINER_NAME" || true
docker container rm "$CONTAINER_NAME" || true

# Janis Rubins step 6: Run container with resource constraints and security measures
# - Use memory and CPU limits to save RAM and CPU resources
# - Mounting code and configs as volumes for easy updates; code mounted ro to prevent attacks
# - Environment variables like TZ easily changed without code edits
docker run -d --name "$CONTAINER_NAME" \
  -e TZ="$TZ_VALUE" \
  -m "$MEMORY_LIMIT" \
  --cpus="$CPU_LIMIT" \
  -v "$CODE_PATH:/app/src/server.py:ro" \
  -v "$CONFIG_PATH:/app/src/configs:rw" \
  "$IMAGE_NAME"

# Janis Rubins step 7: Log container status for debugging
echo "[INFO] Container '$CONTAINER_NAME' started."
docker ps --filter "name=$CONTAINER_NAME"

# Optional: Uncomment to tail logs for debugging purposes
# docker logs -f "$CONTAINER_NAME"

# Summary of improvements:
# - environment variables (IMAGE_NAME, CONTAINER_NAME, DOCKERFILE, TZ_VALUE, MEMORY_LIMIT, CPU_LIMIT) can be changed
#   without editing code.
# - Keeps building and running container, but adds resource and security measures.
# - Uses strict mode and logging for better debugging and stability.
# - Code and config volumes are parameterized, allowing integration with external systems by just changing variables.
# - Memory and CPU limits ensure performance optimization and resource saving.
# - Mounting code as read-only for security against hacking attacks.
# - No breakage of old logic: still builds and runs the container, just enhanced with better security, performance,
#   and flexibility.
