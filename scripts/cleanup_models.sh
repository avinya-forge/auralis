#!/bin/bash

# neu-cleanup-models: Prunes unused model checkpoints from cloud storage (simulated locally)
# Keeps the top 3 most recent versions in the specified directory.

if [ -z "$1" ]; then
    echo "Usage: $0 <models_directory>"
    exit 1
fi

MODELS_DIR="$1"

if [ ! -d "$MODELS_DIR" ]; then
    echo "Error: Directory '$MODELS_DIR' does not exist."
    exit 1
fi

echo "Pruning models in '$MODELS_DIR'..."

# Find all files, sort by modification time (newest first)
# Skip the first 3 (keep them)
# Delete the rest

cd "$MODELS_DIR" || exit 1

# List files sorted by time (newest first), output only filenames
FILES_TO_DELETE=$(ls -t | tail -n +4)

if [ -z "$FILES_TO_DELETE" ]; then
    echo "No models to prune. Total models <= 3."
    exit 0
fi

for FILE in $FILES_TO_DELETE; do
    if [ -f "$FILE" ]; then
        echo "Deleting old model checkpoint: $FILE"
        rm -f "$FILE"
    fi
done

echo "Cleanup complete."
