"""
Starter code to create HF dataset
"""
import argparse
import json
import os
from pathlib import Path
from datasets import load_dataset, Image, DatasetDict, Dataset
from upload_to_hf import DataManager
from tqdm import tqdm


class HFDataset:
    """
    Create HF dataset 
    """
    def __init__(self, config):
        self.config = config

    def load_json(self, data_type: str = "test", suffix: str = "-doc", field="labels"):
        json_path = f"{self.config.base_data_dir}/{data_type}{suffix}.json"
        with open(json_path, "r",  encoding="utf-8") as file:
            json_object = json.load(file)
        return json_object[field]

    def convert_to_hf_data(self, **kwargs):    
        """
        Convert to huggingface dataset for image data
        https://huggingface.co/docs/datasets/upload_dataset
        https://huggingface.co/docs/datasets/en/image_load
        """
        img_paths = kwargs["img_paths"]
        labels = kwargs["labels"]

        ocr_annotations = kwargs["ocr_annotations"]
        filenames = kwargs["filenames"]

        dataset = Dataset.from_dict({"image": img_paths, "filenames": filenames, "labels": labels, "ocr_annotations": ocr_annotations 
                                    }).cast_column("image", Image())
        return dataset

    def load_ocr_annotations(self, folder_name: str, rel_path: str):
        """
        Load ocr annotations based on relateive path
        """
        file_path = f"{self.config.base_data_dir}/{folder_name}/{rel_path}"
        with open(file_path, "r",  encoding="utf-8") as file:
            content = file.readlines()
        return content


    def main(self):
        """
        Main wrapper which loads the json and image data and creates the dataset

        filenames can be something similar to "images/imagesc/"
        """
        relative_to = 'images'
        data_dic = {}
        for data_type in ["test", "val", "train"]:
            labels = []
            ocr_annotations = []
            tesseract_annotations = []
            filenames = []
            img_paths = []
            json_data = self.load_json(data_type=data_type)
            img_rel_paths = list(json_data.keys())
            for img_path in tqdm(img_rel_paths):
                img_paths.append(f"{self.config.base_data_dir}/{img_path}")
                labels.append(json_data[img_path])
                filename = os.path.splitext(os.path.basename(img_path))[0]
                filenames.append(filename)
                # rel_path = os.path.relpath(img_path, relative_to)  # relative path to the images folder
                # print(rel_path)
                ocr_filename = Path(img_path).with_suffix('.txt')
                ocr_annotation = self.load_ocr_annotations(folder_name="text", rel_path=ocr_filename)
                ocr_annotations.append(ocr_annotation)

            dic_obj = {"img_paths": img_paths, "labels": labels, "filenames": filenames, 
                       "ocr_annotations": ocr_annotations}
            hf_dataset = self.convert_to_hf_data(**dic_obj)   
            data_dic[data_type] = hf_dataset     
        dataset_dic = DatasetDict(data_dic)
        DataManager(self.config).push_wrapper(dataset_dic, repo_name=self.config.hf_repo_name, repo_prefix = self.config.hf_repo_prefix)


def parse_args() -> argparse.Namespace:
    """
    Parse cli arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--base_data_dir", type=str, default="/raid/datasets", help="Data path")
    parser.add_argument("-rp", "--hf_repo_prefix", type=str, default="Krutrim", help="Data type")
    parser.add_argument("-rn", "--hf_repo_name", type=str, default="xxxxx", help="Data type")        
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    config = parse_args()
    manager = HFDataset(config)
    manager.main()    
