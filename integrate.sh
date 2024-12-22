#!/bin/bash

# Define the folder path and Python scripts
FOLDER_PATH="/home/nerdnhk/Byte-Bandits/audio"
SCRIPT1="youtube.py"
SCRIPT2="extract_pod.py"
SCRIPT3="audio_concatenator.py"

# Check if the correct number of arguments is provided for the first script
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <link_argument>"
  exit 1
fi

LINK_ARG="$1"

# Run the first script with the link argument
echo "Running $SCRIPT1 with argument: $LINK_ARG..."
python3 "$SCRIPT1" "$LINK_ARG"

# Check if the first script exited with an error
if [ $? -ne 0 ]; then
  echo "Error: $SCRIPT1 failed. Exiting."
  exit 1
fi

echo "$SCRIPT1 executed successfully."

# Check if the specified folder is empty
if [ -z "$(ls -A "$FOLDER_PATH")" ]; then
  echo "Error: Folder $FOLDER_PATH is empty. Exiting."
  exit 1
fi

# Run the second script
echo "Running $SCRIPT2..."
python3 "$SCRIPT2"

# Check if the second script exited with an error
if [ $? -ne 0 ]; then
  echo "Error: $SCRIPT2 failed. Exiting."
  exit 1
fi

echo "$SCRIPT2 executed successfully."

# Run the third script
echo "Running $SCRIPT3..."
python3 "$SCRIPT3"

# Check if the third script exited with an error
if [ $? -ne 0 ]; then
  echo "Error: $SCRIPT3 failed. Exiting."
  exit 1
fi

echo "$SCRIPT3 executed successfully."

# Empty the specified folder
echo "Emptying folder $FOLDER_PATH..."
rm -rf "$FOLDER_PATH"/*

# Check if folder was emptied successfully
if [ $? -ne 0 ]; then
  echo "Error: Failed to empty folder $FOLDER_PATH."
  exit 1
fi

echo "Folder $FOLDER_PATH emptied successfully."
echo "All scripts executed successfully. Exiting."
exit 0
