# Data pipeline based on OBELICS
- Pipeline is originally borrowed from HuggingFace [OBELICS](https://github.com/huggingface/OBELICS/tree/main) pipeline
- Data is being stored in s3 after every step

Note - Data gets exploded after each step
### Metadata Preparation Steps
- In order to process the data parallely, we need to split the index data into multiple batches.
- Each batch need to be stored as huggingface dataset in s3 location `s3://llm-spark/multi_modal/commoncrawl/webdocs/dataset/{batch_id}/ (this is a example location)`
- Structure of the metadata should be as follows 
```json
{
 'url': 'https://www.herzindagi.com/hindi/advice/these-6-types-of-fashionable-footwear-will-damage-your-feet-ankles-and-knees-article-92503',
 'languages': 'hin,eng',
 'encoding': 'UTF-8',
 'warc_filename': 'crawl-data/CC-MAIN-2022-33/segments/1659882571538.36/warc/CC-MAIN-20220812014923-20220812044923-00734.warc.gz',
 'warc_record_offset': 691410160,
 'warc_record_length': 48078
 }
```
- Fields `url`, `warc_record_offset`, `warc_record_length` and `warc_filename` are mandatory.

### Data Extraction Steps

### Steps to run the OBELICS Pipeline

1. Download data
   - A dataset of metadata should be present at s3 location s3://llm-spark/multi_modal/commoncrawl/dataset/{batch_id}/
   - Execute following command for [01_download_warc.py](./01_download_warc.py) with batch id and number of processes 

   ```bash 
   python 01_download_warc.py {batch_id} --path_metadata_dataset
    "s3://llm-spark/multi_modal/commoncrawl/webdocs/dataset/" --path_save_dir_warc_dataset 
    "s3://llm-spark/multi_modal/commoncrawl/webdocs/warc_dataset/" --num_proc {number of processes}
   ```
  
2. Extract html page and get image urls
   - Execute bash command for [02_bis_extract_html_get_image_urls_new_rules.py](./02_bis_extract_html_get_image_urls_new_rules.py) with batch id and number of process. You also need to provide s3 location to store documents without images 
   
   ```bash
   python 02_bis_extract_html_get_image_urls_new_rules.py {batch_id} --path_warc_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/warc_dataset/" --path_save_dir_web_document_dataset_without_images "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset_without_images/"  --num_proc {processes}
   ```
   - Execute Another bash command as follows 
   
   ```bash
   python 02_extract_html_get_image_urls.py {batch_id} --path_warc_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/warc_dataset/" --path_save_dir_html_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/html_dataset/" --num_proc {processes}
   ```
  
3. Create images dataset
   - Execute following command 
   
   ```bash
   python 03_dl_images_create_dataset.py {batch_id} --path_image_urls "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_urls/" --path_save_dir_dataset_images "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_dataset/" --path_save_file_map_url_idx "s3://llm-spark/multi_modal/commoncrawl/webdocs/map_url_idx/" --num_proc {processes}
   ```
  
4. Merge Web Docs with Images
   - Execute following command with batch id and number of processes
   
   ```bash
   python 04_merge_web_docs_with_images.py {batch_id} --path_web_document_dataset_without_images "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset_without_images/" --path_image_dataset_1 "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_dataset/" --path_image_dataset_2 "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_dataset_2/" --path_save_dir_web_document_dataset "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset/" --num_proc {processes}
   ```

5. Command for web filtering
   
   ```bash
   python 05_filtering_web_docs.py {batch_id} 
   --path_web_document_dataset   "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset/" 
   --path_save_web_document_dataset_filtered  "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset_filtered/" 
   --path_config_filter_web_documents  "./obelics/configs/config_filter_web_documents.yaml"  
   --path_common_words "./models/common_words.json"  
   --path_lang_id_model "./models/lid.176.bin"   
   --path_sentencepiece_model "./models/en.sp.model" 
   --path_kenlm_model "./models/en.arpa.bin"  
   --num_proc 2
   ```
   - Download LID model from [FASTTEXT](https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin) and store in `pipeline/OBELICS/models`
   - Download sentencepiece model from [SENTENCEPIECE](https://huggingface.co/edugp/kenlm/resolve/main/wikipedia/en.sp.model?download=true) and store in `pipeline/OBELICS/models`
   - Download KenLM model from [KENLM](https://huggingface.co/edugp/kenlm/resolve/main/wikipedia/en.arpa.bin?download=true) and store in `pipeline/OBELICS/models`
   
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
         `NON_PRINTING_CHARACTERS_RE = re.compile(f"[{''.join(map(chr, list(range(0,32)) + list(range(127,160))))}]")`
      6. Standardize whitespaces
      7. Language filter: Filter the text data based on target_lang_ids parameter in the config file

6. Execute following command to get set of image urls
   ```bash 
   python 06_01_create_set_image_urls_in_webdocs.py 0 --path_web_document_dataset_filtered "s3://llm-spark/multi_modal/commoncrawl/webdocs/web_document_dataset_filtered/" --path_save_image_urls_in_web_document_dataset_filtered "s3://llm-spark/multi_modal/commoncrawl/webdocs/image_urls_in_web_document_dataset_filtered/" --num_proc 1
   ```
    To merge al the images
   ```bash 
   python 06_02_merge_sets_image_urls_in_webdocs.py
   ```
7. Classify NSFW images
   ```bash
   python 07_01_nsfw_image_filtering.py {batch_id}
   ```
   Visualization of NSFW images
   ```bash
   python 07_02_nsfw_image_visualization.py
   ```
   Remove the NSFW images from data
   ```bash
   python 07_03_nsfw_image_removal.py {batch_id}
   ```
8. Prepare urldedup data and remove duplicate image urls
   - identifying duplicate URLs, and retaining only the most recent document for each duplicate URL. Change `NUM_SHARDS = 7` in [08_01_prepare_urldedup.py](./08_01_prepare_urldedup.py) when running it with more data
   ```bash
   python 08_01_prepare_urldedup.py
   ```
   - This script is used to filter out duplicated URLs and documents without images. Change the `NUM_PROC = 1` when running it with more data
   ```bash
   python 08_02_urldedup.py {batch_id}
   ```

9. Get the text only data from documents 
   
      9.1 Get the texts only from web documents from [09_01_create_web_docs_texts_only.py](./09_01_create_web_docs_texts_only.py). Execute below command with `batch_id`

      ```bash
      python 09_01_create_web_docs_texts_only.py {batch_id}
      ```

      9.2 Get the domain to position details. User is required to change the `NUM_SHARDS = 200` value
      ```bash
      python 09_02_get_domain_to_positions.py
      ```

      9.3 Get line splited data to dedup at line level. User is required to change the `NUM_SHARDS = 200` value
      ```bash
      python 09_03_split_domain_to_positions.py
      ```

      9.4 Check line level duplication of data in all the documents.  User is required to change the `NUM_SHARDS = 200` value
      ```bash
      python 09_04_get_domain_to_duplicated_texts.py {batch_id}
      ```
      9.5 Merge all the duplicated texts into one file. User is required to change the `NUM_SHARDS = 200` value
      ```bash
      python 09_05_merge_domain_to_duplicated_texts_sharded.py
      ```
      9.6 Remove the duplicated texts from the data. 
      ```bash
         python 09_06_line_dedup.py {batch_id}
      ```
      9.7 merge the data back to one file
      ```bash
         python 09_07_merge_web_docs_texts_only_and_rest.py {batch_id}
      ```

10. Batchwise cleaning of data if there are case in the final data that are not expected  
   ```bash
   python 10_final_cleaning.py {batch_id}
   ```

11. Remove url and image set duplicates
      11.1 Create a set of urls and image 
      ```bash
      python 11_01_create_set_img_urls.py {batch_id}
      ```
      11.2 Get the documents to remove where image and url set duplicates are there. User need to change  `NUM_SHARDS = 200` value
      ```bash
      python 11_02_get_docs_to_remove_by_set_img_urls_dedup.py {batch_id}
      ```
      11.3 Remove unwanted documents 
      ```bash
      python 11_03_set_img_urls_dedup.py {batch_id}
      ```
12. Find out images that are not authorized to be used for training using spawning api
      12.1  User spawning API to get images that can not be used in training 
      ```bash
      python 12_01_find_opt_out_images.py
      ```
      12.2 Remove the images that are not authorized to be used for training
      ```bash
      python 12_02_remove_opt_out_images.py {batch_id}
      ```
13. Final processing 
   - Remove end of the document token 
   - Merge documents where end of document token is consecutively available
   ```bash
   python 13_final_processing.py
   ```

   
   

