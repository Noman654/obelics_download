# Installation

```
conda create -n data_pipe python=3.10 -y
pip install -r requirements.txt
```

## Sample run

1. Download the epub file in `input_data` folder. (Add `input_data` to `.gitignore`). Please provide a sample url and `wget ` step too like
```
mkdir -p input_data
wget -o my_book.epub https://filesamples.com/samples/ebook/epub/famouspaintings.epub
```

2. Run from current directory as 

```
python epub_book_extract.py --path_save_dataset "~/tmp/" --path_epub_file "my_book.epub"
```