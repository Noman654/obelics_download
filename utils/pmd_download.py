# https://huggingface.co/datasets/facebook/pmd
import argparse
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import io
import urllib
import os
import PIL.Image

from datasets import load_dataset
from datasets.utils.file_utils import get_datasets_user_agent


USER_AGENT = get_datasets_user_agent()


def fetch_single_image(image_data, timeout=None, retries=0):
    image_url, image = image_data
    if image is not None:
        return image

    for _ in range(retries + 1):
        try:
            request = urllib.request.Request(
                image_url,
                data=None,
                headers={"user-agent": USER_AGENT},
            )
            with urllib.request.urlopen(request, timeout=timeout) as req:
                image = PIL.Image.open(io.BytesIO(req.read()))
            break
        except Exception:
            image = None
    return image


def fetch_images(batch, num_threads, timeout=None, retries=0):
    fetch_single_image_with_args = partial(fetch_single_image, timeout=timeout, retries=retries)
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        batch["image"] = list(executor.map(fetch_single_image_with_args, zip(batch["image_url"], batch["image"])))
    return batch


def main(config, download_data=False):
    dir_name = f"pmd-coco"
    local_save_path = f"{config.local_hf_path}/{dir_name}"
    if download_data:
        num_threads = 20
        dset = load_dataset("facebook/pmd", "coco", use_auth_token=True)
        dset = dset.map(fetch_images, batched=True, batch_size=100, fn_kwargs={"num_threads": num_threads})                
        dset.save_to_disk(local_save_path)

    s3_cp_path = f"{config.base_s3_path}/{dir_name}"

    aws_command = f"aws s3 cp {local_save_path} {s3_cp_path} --recursive"
    os.system(aws_command)
    print(f"Uploaded from {local_save_path} to {s3_cp_path}")


def parse_args() -> argparse.Namespace:
    """
    Parse cli arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--local_hf_path", type=str, default="/mnt/disk2/shubham/hf_home/", help="Local HF path")
    parser.add_argument("-s", "--base_s3_path", type=str, default="s3://llm-spark/frontier_data/visual_data/", help="Save data path")


    args = parser.parse_args()
    return args


if __name__ == "__main__":
    config = parse_args()
    main(config)