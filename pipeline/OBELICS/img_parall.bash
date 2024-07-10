# !/bin/bash




# Check if correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <start_batch> <end_batch>"
    exit 1
fi


# Ensure conda is initialized
source /home/ubuntu/miniconda/etc/profile.d/conda.sh
conda activate mm

echo "check its running or not "

BUCKET_PATH="s3://llm-spark/multi_modal/commoncrawl/webdocs/image_dataset"
# Loop over batches from start to end
for BATCH in $(seq $1 $2); do
    # Initialize logging   

    BATCH_PATH="$BUCKET_PATH/$BATCH/"
    if aws s3 ls "$BATCH_PATH" > /dev/null 2>&1; then
        echo "Batch exists: $BATCH"
        continue  # Skip to the next batch
    fi
    mkdir -p ./logs
    LOG_FILE="./logs/log_batch_img_${BATCH}.log"
    touch $LOG_FILE
    echo "Processing batch $BATCH ..." | tee -a $LOG_FILE
    start_time=$(date +%s)
    
    # Run the Python script with necessary arguments
    python 03_dl_images_create_dataset.py $BATCH \
    --path_image_urls "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_urls_new_rules/" \
    --path_save_dir_dataset_images "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_dataset/" \
    --path_save_file_map_url_idx "s3://llm-spark/multi_modal/commoncrawl/webdocs/map_url_idx/" \
    --num_proc 5 \
    --path_save_dir_tmp_datasets_images "./scratch/storage_hugo_${BATCH}/tmp_datasets_images" \
    --path_save_dir_downloaded_images "./scratch/storage_hugo_${BATCH}/downloaded_images"
    
    # Calculate elapsed time and log it
    end_time=$(date +%s)
    elapsed_time=$((end_time - start_time))
    echo "Batch $BATCH completed in $elapsed_time seconds" | tee -a $LOG_FILE

    # Append individual batch log to final log file
    cat $LOG_FILE >> './logs/final_batch.log'
    done
