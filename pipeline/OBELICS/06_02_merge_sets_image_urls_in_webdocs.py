# srun --pty --ntasks=1 --cpus-per-task=96 bash -i
# conda activate /fsx/m4/conda/shared-m4-2023-03-10


import os
import pickle
from collections import Counter

from tqdm import tqdm


PATH_S3_IMAGE_URLS_IN_WEBDOCS = "s3://llm-spark/shahrukh/commoncrawl/image_urls_in_web_document_dataset_filtered/"
NUM_SHARDS = 4
THRESHOLD_TOO_DUPLICATED = 10
root_path = os.getcwd()

if __name__ == "__main__":
    path_save_disk_image_urls_in_webdocs = f"{root_path}/scratch/image_urls_in_webdocs"
    command_sync_s3 = f"aws s3 sync {PATH_S3_IMAGE_URLS_IN_WEBDOCS} {path_save_disk_image_urls_in_webdocs}"
    os.system(command_sync_s3)
    os.system(command_sync_s3)
    os.system(command_sync_s3)

    all_counters = []
    for idx_shard in tqdm(range(NUM_SHARDS)):
        with open(
            os.path.join(
                path_save_disk_image_urls_in_webdocs,
                str(idx_shard),
                "image_urls_in_web_document_dataset_filtered.pickle",
            ),
            "rb",
        ) as f:
            all_counters.append(pickle.load(f))

    tot_counter = Counter()
    for counter in tqdm(all_counters):
        tot_counter.update(counter)

    with open(f"{root_path}/scratch/tot_image_urls_in_web_document_dataset_filtered.pickle", "wb") as f:
        pickle.dump(tot_counter, f, pickle.HIGHEST_PROTOCOL)

    command_sync_s3 = (
        f"aws s3 cp {root_path}/scratch/tot_image_urls_in_web_document_dataset_filtered.pickle"
        " s3://llm-spark/shahrukh/commoncrawl/tot_image_urls_in_web_document_dataset_filtered.pickle"
     
    os.system(command_sync_s3)
    os.system(command_sync_s3)
    os.system(command_sync_s3)

    tot_image_urls_in_web_document_dataset_filtered_too_duplicated = [
        k for k, v in tot_counter.items() if v > THRESHOLD_TOO_DUPLICATED
    ]

    with open(f"{root_path}/scratch/tot_image_urls_in_web_document_dataset_filtered_too_duplicated.pickle", "wb") as f:
        pickle.dump(tot_counter, f, pickle.HIGHEST_PROTOCOL)

    command_sync_s3 = (
        f"aws s3 cp {root_path}/scratch/tot_image_urls_in_web_document_dataset_filtered_too_duplicated.pickle"
        " s3://llm-spark/shahrukh/commoncrawl/tot_image_urls_in_web_document_dataset_filtered_too_duplicated.pickle"
    )
    os.system(command_sync_s3)
    os.system(command_sync_s3)
    os.system(command_sync_s3)
