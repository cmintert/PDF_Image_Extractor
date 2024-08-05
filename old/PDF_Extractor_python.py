import os
import io
from typing import List, Tuple

import pymupdf
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont

class PDFImageExtractor:
    def __init__(self):
        self.pdf_path = ""
        self.pdf_directory = ""
        self.pdf_name = ""
        self.output_folder = ""
        self.threshold = 0

    def select_pdf_file(self) -> str:
        root = tk.Tk()
        root.withdraw()
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf_directory = os.path.dirname(self.pdf_path)
        self.pdf_name = os.path.basename(self.pdf_path)
        return self.pdf_path

    def extract_images(self) -> List[Tuple[bytes, float]]:
        extracted_images = []
        with pymupdf.open(self.pdf_path) as doc:
            for page in doc:
                image_list = page.get_images(full=True)
                for img in image_list:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_size = len(image_bytes) / 1024  # size in KB
                    extracted_images.append((image_bytes, image_size))
        return extracted_images

    def sort_images_by_size(self, images: List[Tuple[bytes, float]]) -> List[Tuple[Image.Image, float]]:
        images.sort(key=lambda x: x[1], reverse=True)  # Sort by size in KB
        thumbnails = []
        for image_bytes, size in images:
            try:
                img = Image.open(io.BytesIO(image_bytes))
                img = img.convert("RGB")  # Ensure image mode is RGB
                img.thumbnail((100, 100))  # Creating a thumbnail
                thumbnails.append((img, size))
            except OSError as e:
                print(f"Error processing image: {e}")
        return thumbnails

    def create_thumb_sheet(self, images: List[Tuple[Image.Image, float]]) -> str:
        thumb_width, thumb_height = 100, 100
        max_thumbs_per_row = 10

        # Calculate the number of rows needed
        num_rows = (len(images) - 1) // max_thumbs_per_row + 1

        sheet_width = thumb_width * min(len(images), max_thumbs_per_row)
        sheet_height = (thumb_height + 20) * num_rows  # Extra height for labels

        sheet = Image.new("RGB", (sheet_width, sheet_height))
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.load_default()

        for index, (img, size) in enumerate(images):
            row = index // max_thumbs_per_row
            col = index % max_thumbs_per_row
            x_offset = col * thumb_width
            y_offset = row * (thumb_height + 20)

            sheet.paste(img, (x_offset, y_offset))
            draw.text((x_offset, y_offset + thumb_height + 5), f"{size:.2f} KB", fill="white", font=font)

        thumbnail_sheet_path = os.path.join(self.pdf_directory, "thumbnail_sheet.png")
        sheet.save(thumbnail_sheet_path)
        print(f"Thumbnail sheet created at: {thumbnail_sheet_path}")
        return thumbnail_sheet_path

    def create_thumbnail_preview(self):
        extracted_images = self.extract_images()
        sorted_images = self.sort_images_by_size(extracted_images)
        thumbnail_sheet = self.create_thumb_sheet(sorted_images)
        os.startfile(thumbnail_sheet)

    def set_threshold_size(self):
        while True:
            try:
                self.threshold = int(input("Enter the threshold for image size in KB: "))
                if self.threshold > 0:
                    break
                print("Threshold must be a positive integer")
            except ValueError:
                print("Please enter a valid integer")
        print(f"Images below {self.threshold} KB will be skipped")

    def create_output_folder(self):
        self.output_folder = os.path.join(self.pdf_directory, f"extracted_img_from_{self.pdf_name}")
        os.makedirs(self.output_folder, exist_ok=True)

    def extract_and_save_images(self):
        self.create_output_folder()
        with pymupdf.open(self.pdf_path) as doc:
            for page_index in range(len(doc)):
                self.process_page(doc, page_index)

    def process_page(self, doc: pymupdf.Document, page_index: int):
        page = doc[page_index]
        image_list = page.get_images()
        self.print_image_count(page_index, len(image_list))

        for image_index, img in enumerate(image_list, start=1):
            self.process_image(doc, page_index, image_index, img)

    def print_image_count(self, page_index: int, count: int):
        if count:
            print(f"Found {count} images on page {page_index}")
        else:
            print(f"No images found on page {page_index}")

    def process_image(self, doc: pymupdf.Document, page_index: int, image_index: int, img: Tuple):
        print(f"Extracting image {image_index} on page {page_index}")
        xref, smask = img[0], img[1]
        image_bytes = doc.extract_image(xref)["image"]
        img_size = len(image_bytes) / 1024
        print(f"Size of processed image is {img_size:.2f} KB")

        if img_size < self.threshold:
            print(f"Skipping image {image_index} on page {page_index}. Too small")
            return

        self.save_image(doc, xref, smask, page_index, image_index)

    def save_image(self, doc: pymupdf.Document, xref: int, smask: int, page_index: int, image_index: int):
        pix = self.create_pixmap(doc, xref, smask)
        output_path = os.path.join(self.output_folder, f"page_{page_index}-image_{image_index}.png")
        pix.save(output_path)

    def create_pixmap(self, doc: pymupdf.Document, xref: int, smask: int) -> pymupdf.Pixmap:
        pix1 = pymupdf.Pixmap(doc.extract_image(xref)["image"])
        if smask > 0:
            print("Mask found for image")
            mask = pymupdf.Pixmap(doc.extract_image(smask)["image"])
            return pymupdf.Pixmap(pix1, mask)
        return pix1

def main():
    extractor = PDFImageExtractor()
    extractor.select_pdf_file()
    extractor.create_thumbnail_preview()
    extractor.set_threshold_size()
    extractor.extract_and_save_images()

if __name__ == "__main__":
    main()