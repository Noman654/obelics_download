

Batch=$1
python 03_dl_images_create_dataset.py $Batch --path_image_urls "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_urls_new_rules/" --path_save_dir_dataset_images "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_dataset/" \
--path_save_file_map_url_idx "s3://llm-spark/multi_modal/commoncrawl/webdocs/map_url_idx/" --num_proc 10 \
--path_save_dir_tmp_datasets_images "./scratch/storage_hugo_${Batch}/tmp_datasets_images" --path_save_dir_downloaded_images "./scratch/storage_hugo_${Batch}/downloaded_images"
