#!/bin/bash

# Get list of running containers
echo "Available Docker containers:"
containers=$(docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}")
echo "$containers"

# Get just the container names for selection
container_names=$(docker ps --format "{{.Names}}")

if [ -z "$container_names" ]; then
    echo "No running containers found."
    exit 1
fi

echo ""
echo "Available containers:"
# Create numbered list of containers
container_array=()
counter=1
while IFS= read -r container; do
    echo "$counter) $container"
    container_array+=("$container")
    ((counter++))
done <<< "$container_names"

echo ""
read -p "Enter the container name or number from the list: " selection

# Check if selection is a number
if [[ "$selection" =~ ^[0-9]+$ ]]; then
    # Selection is a number
    if [ "$selection" -ge 1 ] && [ "$selection" -le "${#container_array[@]}" ]; then
        selected_container="${container_array[$((selection-1))]}"
    else
        echo "Error: Invalid number. Please select a number between 1 and ${#container_array[@]}."
        exit 1
    fi
else
    # Selection is a container name
    selected_container="$selection"
    # Validate that the selected container exists
    if ! echo "$container_names" | grep -q "^$selected_container$"; then
        echo "Error: Container '$selected_container' not found in running containers."
        exit 1
    fi
fi

# Show logs for the selected container
docker logs -f --tail 100 "$selected_container"