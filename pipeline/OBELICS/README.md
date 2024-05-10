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

5. Command for web filtering
   ```python 05_filtering_web_docs.py {batch_id} --path_web_document_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset/" --path_save_web_document_dataset_filtered "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset_filtered/" --path_config_filter_web_documents "./obelics/configs/config_filter_web_documents.yaml" --path_common_words "/mnt/weka/shahrukh/workspace/OBELICS/models/common_words.json" --path_lang_id_model "/mnt/weka/shahrukh/workspace/OBELICS/models/lid.176.bin"  --path_sentencepiece_model "/mnt/weka/shahrukh/workspace/OBELICS/models/en.sp.model" --path_kenlm_model "/mnt/weka/shahrukh/workspace/OBELICS/models/en.arpa.bin" --num_proc 2```
   Different kind of filters applied are as follows
### Filtering
1. Format check
   If format of the image is in (jpg, jpeg, png, webp)
2. Check image size
   Check of minimum and maximum values of width, height, and aspect ratio of original and rendered image
3. Check number of images
   Filter the document if number of images in the document is more and less than max and min threshold values
4. Remove enmpty words from the text data
5. Remove non printing characters generated with following
   ```NON_PRINTING_CHARACTERS_RE = re.compile(f"[{''.join(map(chr, list(range(0,32)) + list(range(127,160))))}]")```
6. Standardize whitespaces
7. Language filter: Filter the text data based on target_lang_ids parameter in the config file

6. Execute following command to get set of image urls
   ```python 06_01_create_set_image_urls_in_webdocs.py 0 --path_web_document_dataset_filtered "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset_filtered/" --path_save_image_urls_in_web_document_dataset_filtered "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_urls_in_web_document_dataset_filtered/" --num_proc 1```
    To merge al the images
   ```python 06_02_merge_sets_image_urls_in_webdocs.py```
7. Classify NSFW images
   ```python 07_01_nsfw_image_filtering.py```