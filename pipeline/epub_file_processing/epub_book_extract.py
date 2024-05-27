import os
from ebooklib import epub
from bs4 import BeautifulSoup
import ebooklib
from PIL import Image
import io
from datasets import Dataset
import argparse
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def extract_text_and_images_from_html(soup):
    text_data = []
    img_data = []
    for element in soup.recursiveChildGenerator():
        if element.name:
            if element.name == 'img':
                img_data.append({"Image": {element['src']}, "Alt": {element.get('alt', 'No alt text')}})
                text_data.append(None)
            elif element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span']:
                text = element.get_text(strip=True)
                if text:  
                    text_data.append(text)
                    img_data.append(None)
    return text_data, img_data

def extract_save_images(book, output_folder):
    text_content = []
    image_files = []
    text_data = []
    data_dicts = []
    
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Extract text from the document
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')
            text_data, img_data = extract_text_and_images_from_html(soup)
            data_dicts.append({"texts":text_data, "images":img_data})
        elif item.get_type() == ebooklib.ITEM_IMAGE:
            # Save image files
            image_folder = os.path.join(output_folder, "/".join(item.file_name.split("/")[:-1]))
            if ~os.path.exists(image_folder):
                os.system(f"mkdir -p {image_folder}")
            image_path = os.path.join(output_folder, item.file_name)
            with open(image_path, 'wb') as img_file:
                img_file.write(item.content)
            image_files.append(image_path)
    return data_dicts, image_files

def extract_text_and_images(soup):
    text_data = []
    img_data = []
    for element in soup.recursiveChildGenerator():
        if element.name:
            if element.name == 'img':
               # print(f"Image: {element['src']}, Alt: {element.get('alt', 'No alt text')}")
                img_data.append({"Image": element['src'], "Alt": element.get('alt', 'No alt text')})
                text_data.append(None)
            elif element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span']:
                text = element.get_text(strip=True)
                if text:  # Only print non-empty text
                    #print(f"Text: {text}")
                    text_data.append(text)
                    img_data.append(None)
    return text_data, img_data

def get_args():
    parser = argparse.ArgumentParser(description="Process epub file to extract image and interleaved text")
    parser.add_argument(
        "--path_epub_file",
        type=str,
        default=None,
        help="Path of the epub file.",
    )
    parser.add_argument(
        "--path_save_dataset",
        type=str,
        default="./",
        help="The directory to save the final dataset.",
    )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    working_dir = os.getcwd()
    path_save_tmp_files = f"{working_dir}/book_data/"
    if os.path.exists(f"{path_save_tmp_files}"):
        os.system(f"rm -r {path_save_tmp_files}")
    os.system(f"mkdir -p {path_save_tmp_files}")

    logger.info("Starting loading the epub file")
    book = epub.read_epub(args.path_epub_file)
    data_dicts, images = extract_save_images(book, path_save_tmp_files)
    html_pages = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            html_pages.append(BeautifulSoup(item.get_body_content(), 'html.parser'))
            
    final_data = []
    for html_page in html_pages:
        text_data, img_data = extract_text_and_images(html_page)
        if text_data:
            for img_path in img_data:
                if img_path:
                    print(img_path["Image"])
                    partial_path = "/".join(img_path["Image"].split("/")[1:])
                    img = Image.open(f'{path_save_tmp_files}{img_path["Image"]}')
                    buffered = io.BytesIO()
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    img.save(buffered, format="JPEG")
                    img_str = buffered.getvalue()
                    img_path["Image"]=img_str
            final_data.append({"text":text_data, "image":img_data})
    book_path = args.path_epub_file
    book_name = book_path.split("/")[-1].split(".")[0]
    ds = Dataset.from_list(final_data)
    ds.save_to_disk(f"{args.path_save_dataset}{book_name}")
