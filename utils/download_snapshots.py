from huggingface_hub import snapshot_download
folder = snapshot_download(
                "google/imageinwords", 
                repo_type="dataset",
                local_dir="/mnt/disk2/shubham/hf_home")