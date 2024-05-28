# Installation

```
conda create -n data_pipe python=3.8 -y
pip install -r requirements.txt
pip install datasets==
```

## Sample run

1. Download the epub file in `input_data` folder. (Add `input_data` to `.gitignore`). Please provide a sample url and `wget ` step too like
```
mkdir -p input_data
wget .... -o ... input_data/sample.epub
```

2. Run from current directory as 

```
python epub_book_extract.py --path_save_dataset "~/tmp" --path_epub_file "data/sample.epub"
```