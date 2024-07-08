#!/bin/bash

# Check for the correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <batch_number> <starting_image_id>"
    exit 1
fi

batch_number=$1
starting_image_id=$2

# Ensure conda is initialized
eval "$(conda shell.bash hook)"
conda activate mm

# Create a main screen session
main_screen_name="image_download01"
screen -dmS "$main_screen_name"

# Function to run img_download.bash in a new screen window within the main screen session
run_in_screen_window() {
    local start_id=$1
    local end_id=$((start_id + 8))
    local window_name="batch_$start_id"
    sleep $((RANDOM % 5 + 5))
    echo "-S $main_screen_name -X screen -t $window_name bash -c ./img_parall.bash $start_id $end_id; exec bash"
    screen -S "$main_screen_name" -X screen -t "$window_name" bash -c "
        eval \"\$(conda shell.bash hook)\";
        conda activate /home/ubuntu/miniconda/envs/mm;
        time ./img_parall.bash $start_id $end_id;
        exec bash"
}

# Calculate the start ID for each batch and run the download command in a new window
for ((i=0; i<batch_number; i++)); do
    current_start_id=$((starting_image_id + i * 13))
    run_in_screen_window "$current_start_id"
done

echo "Started $batch_number batches starting from image ID $starting_image_id in screen session $main_screen_name"
