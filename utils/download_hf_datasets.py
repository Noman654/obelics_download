import argparse
import os
from pathlib import Path
from datasets import get_dataset_config_names, get_dataset_split_names, load_dataset, Dataset


class OBELICSDataset:
    """
    Create RVL-CDIP dataset with ocr annotations
    """
    def __init__(self, config):
        self.config = config
        try:
            self.hf_home = os.environ['HF_HOME']
        except:
            print(f"HF home not set! Will use /tmp to save")
            self.hf_home = "/tmp/"

    def get_hf_configs(self):
        """
        Dataset of datasets
        https://huggingface.co/docs/datasets/en/load_hub#configurations
        """
        configs = get_dataset_config_names(self.config.hf_dataset)
        return configs

    def get_hf_splits(self, data_config):
        splits = get_dataset_split_names(self.config.hf_dataset, data_config, trust_remote_code=True)
        return splits

    def load_hf_dataset(self, dataset_name, data_config, data_split, redownload: bool = True):
        if redownload:
            dataset = load_dataset(dataset_name, data_config, split=data_split, trust_remote_code=True, 
                                   download_mode='force_redownload')
        else:
            dataset = load_dataset(dataset_name, data_config, split=data_split, trust_remote_code=True)

        return dataset


    def save_disk_wrapper(self, dataset, hf_data_save_dir):
        if not os.path.exists(hf_data_save_dir):
            os.makedirs(hf_data_save_dir)
        dataset.save_to_disk(hf_data_save_dir)

    def main(self):
        print(f"Default save location for dataset: {self.hf_home}")
        # Dataset of datasets have a config for each dataset
        data_configs = self.get_hf_configs()
        for data_name in data_configs:
            splits = self.get_hf_splits(self, data_name)
            for split in splits:
                dataset = self.load_hf_dataset(self.config.hf_dataset, data_name, split)
                if self.config.save_data_path:
                    hf_data_save_dir = f"{self.config.save_data_path}/{data_name}/{split}"
                    self.save_disk_wrapper(dataset, hf_data_save_dir)


def parse_args() -> argparse.Namespace:
    """
    Parse cli arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--hf_dataset", type=str, default="HuggingFaceM4/the_cauldron", help="HF dataset")
    parser.add_argument("-s", "--save_data_path", type=str, default="", help="Save data path")


    args = parser.parse_args()
    return args


if __name__ == "__main__":
    config = parse_args()
    manager = OBELICSDataset(config)
    manager.main()    
