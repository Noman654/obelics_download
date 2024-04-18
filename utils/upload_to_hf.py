import os
from huggingface_hub import login as hf_login
from datasets import Dataset, load_dataset, set_caching_enabled, DatasetDict
import pandas as pd
import argparse

class DataManager:
    """
    Data manager
    """

    def __init__(self, config):
        self.config = config

    def push_df_to_hub(self, dataset, repo_path: str, do_hf_login: bool = True):
        """
        https://huggingface.co/docs/datasets/upload_dataset
        """
        HF_TOKEN = os.environ['HF_TOKEN']
        if do_hf_login:
            hf_login(token=HF_TOKEN)    
        dataset.push_to_hub(repo_path)

    def convert_to_dict(self, df, data_type):
        """
        https://discuss.huggingface.co/t/save-datasetdict-to-huggingface-hub/12075/4
        https://stackoverflow.com/questions/72499850/how-to-load-two-pandas-dataframe-into-hugginfaces-dataset-object
        https://discuss.huggingface.co/t/from-pandas-dataframe-to-huggingface-dataset/9322
        
        """
        dataset_dic = DatasetDict({data_type: Dataset.from_pandas(df)})
        return dataset_dic

    def convert_df_to_hf_upload(self, df_pandas_or_dataset, hf_data_save_dir, data_type = "test"):
        if type(df_pandas_or_dataset) == pd.DataFrame:
            dataset = Dataset.from_pandas(df_pandas_or_dataset)
        else:
            dataset = df_pandas_or_dataset    
        dataset_dic = DatasetDict({data_type: dataset})
        return dataset_dic

    def push_wrapper(self, dataset_or_dic, repo_name, repo_prefix):
        repo_path = f"{repo_prefix}/{repo_name}"
        self.push_df_to_hub(dataset_or_dic, repo_path)


    def save_disk_wrapper(self, dataset_dic, repo_name, hf_data_save_dir):
        hf_data_save_dir = f"{hf_data_save_dir}/{repo_name}"
        if not os.path.exists(hf_data_save_dir):
            os.makedirs(hf_data_save_dir)
        dataset_dic.save_to_disk(hf_data_save_dir)

    def load_hf_dataset(self, dataset_name, redownload: bool = True):
        if redownload:
            dataset = load_dataset(dataset_name, trust_remote_code=True, download_mode='force_redownload')
        else:
            dataset = load_dataset(dataset_name, trust_remote_code=True)

        return dataset

    def main(self):
        dataset = self.load_hf_dataset(dataset_name=self.config.hf_dataset)
        self.push_wrapper(dataset, repo_name=self.config.hf_repo_name, repo_prefix = self.config.hf_repo_prefix)

def parse_args() -> argparse.Namespace:
    """
    Parse cli arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_path", type=str, default="data", help="Data path")
    parser.add_argument("-dt", "--data_type", type=str, default="train", help="Data type")
    parser.add_argument("-hd", "--hf_dataset", type=str, default="aharley/rvl_cdip", help="HF repo")
    parser.add_argument("-rp", "--hf_repo_prefix", type=str, default="Krutrim", help="Data type")
    parser.add_argument("-rn", "--hf_repo_name", type=str, default="rvl_cdip", help="Data type")        
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    config = parse_args()
    manager = DataManager(config)
    manager.main()    
