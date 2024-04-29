Data pipeline based on OBELICS

### Steps to run the OBELICS Pipeline

1. Download data
   - A dataset of metadata should be present at s3 location s3://llm-spark/multi_modal/commoncrawl/dataset/{batch_id}/
   - Execute following command with batch id and number of processes ```python 01_download_warc.py {batch_id} --path_metadata_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/dataset/" --path_save_dir_warc_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/warc_dataset/" --num_proc {number of processes}```
  
2. Extract html page and get image urls
   - Execute bash command with batch id and number of process. You also need to provide s3 location to store documents without images ```python 02_bis_extract_html_get_image_urls_new_rules.py {batch_id} --path_warc_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/warc_dataset/" --path_save_dir_web_document_dataset_without_images "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset_without_images/"  --num_proc {processes}```
   - Execute Another bash command as follows ```python 02_extract_html_get_image_urls.py {batch_id} --path_warc_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/warc_dataset/" --path_save_dir_html_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/html_dataset/" --num_proc {processes}```
  
3. Create images dataset
   - Execute following command ```python 03_dl_images_create_dataset.py {batch_id} --path_image_urls "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_urls/" --path_save_dir_dataset_images "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_dataset/" --path_save_file_map_url_idx "s3://llm-spark/multi_modal/commoncrawl/webdocs/map_url_idx/" --num_proc {processes}```
  
4. Merge Web Docs with Images
   - Execute following command with batch id and number of processes```python 04_merge_web_docs_with_images.py {batch_id} --path_web_document_dataset_without_images "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset_without_images/" --path_image_dataset_1 "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_dataset/" --path_image_dataset_2 "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_dataset_2/" --path_save_dir_web_document_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset/" --num_proc {processes}```

5. 