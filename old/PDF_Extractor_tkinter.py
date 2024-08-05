import os
import io
import tkinter as tk
from tkinter import ttk, filedialog
from typing import List, Tuple
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageTk


class PDFImageExtractorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("PDF Image Extractor")
        self.master.geometry("800x600")

        self.extractor = PDFImageExtractor()

        self.create_widgets()

    def create_widgets(self):
        # File selection
        self.file_frame = ttk.Frame(self.master, padding="10")
        self.file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.file_label = ttk.Label(self.file_frame, text="Selected PDF:")
        self.file_label.grid(row=0, column=0, sticky=tk.W)

        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, width=50)
        self.file_entry.grid(row=0, column=1, padx=5)

        self.browse_button = ttk.Button(self.file_frame, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2)

        # Output folder selection
        self.output_frame = ttk.Frame(self.master, padding="10")
        self.output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.output_label = ttk.Label(self.output_frame, text="Output Folder:")
        self.output_label.grid(row=0, column=0, sticky=tk.W)

        self.output_path = tk.StringVar()
        self.output_entry = ttk.Entry(self.output_frame, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=0, column=1, padx=5)

        self.output_browse_button = ttk.Button(self.output_frame, text="Browse", command=self.browse_output_folder)
        self.output_browse_button.grid(row=0, column=2)

        # Threshold setting
        self.threshold_frame = ttk.Frame(self.master, padding="10")
        self.threshold_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        self.threshold_label = ttk.Label(self.threshold_frame, text="Threshold (KB):")
        self.threshold_label.grid(row=0, column=0, sticky=tk.W)

        self.threshold = tk.IntVar(value=0)
        self.threshold_entry = ttk.Entry(self.threshold_frame, textvariable=self.threshold, width=10)
        self.threshold_entry.grid(row=0, column=1, padx=5)

        # Action buttons
        self.button_frame = ttk.Frame(self.master, padding="10")
        self.button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))

        self.preview_button = ttk.Button(self.button_frame, text="Create Thumbnail Preview",
                                         command=self.create_preview)
        self.preview_button.grid(row=0, column=0, padx=5)

        self.extract_button = ttk.Button(self.button_frame, text="Extract Images", command=self.extract_images)
        self.extract_button.grid(row=0, column=1, padx=5)

        # Log area
        self.log_frame = ttk.Frame(self.master, padding="10")
        self.log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD, width=80, height=20)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=self.scrollbar.set)

        # Configure grid weights
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(4, weight=1)

    def browse_file(self):
        file_path = self.extractor.select_pdf_file()
        if file_path:
            self.file_path.set(file_path)
            self.log("PDF file selected: " + file_path)
            # Set default output folder
            default_output = os.path.join(os.path.dirname(file_path),
                                          f"extracted_img_from_{os.path.basename(file_path)}")
            self.output_path.set(default_output)
            self.log(f"Default output folder set to: {default_output}")

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_path.set(folder_path)
            self.log(f"Output folder selected: {folder_path}")

    def create_preview(self):
        if not self.file_path.get():
            self.log("Error: Please select a PDF file first.")
            return

        self.log("Creating thumbnail preview...")
        thumbnail_sheet = self.extractor.create_thumbnail_preview()
        self.log("Thumbnail sheet created at: " + thumbnail_sheet)
        os.startfile(thumbnail_sheet)

    def extract_images(self):
        if not self.file_path.get():
            self.log("Error: Please select a PDF file first.")
            return

        threshold = self.threshold.get()
        if threshold <= 0:
            self.log("Error: Please enter a valid threshold (positive integer).")
            return

        output_folder = self.output_path.get()
        if not output_folder:
            self.log("Error: Please select an output folder.")
            return

        self.extractor.threshold = threshold
        self.extractor.output_folder = output_folder
        self.log(f"Extracting images with threshold: {threshold} KB")
        self.log(f"Output folder: {output_folder}")
        self.extractor.extract_and_save_images()
        self.log("Image extraction completed.")
        self.log(f"Images have been extracted to: {self.extractor.output_folder}")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)


class PDFImageExtractor:
    def __init__(self):
        self.pdf_path = ""
        self.pdf_directory = ""
        self.pdf_name = ""
        self.output_folder = ""
        self.threshold = 0

    def select_pdf_file(self) -> str:
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.pdf_path:
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
                pass
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
        return thumbnail_sheet_path

    def create_thumbnail_preview(self):
        extracted_images = self.extract_images()
        sorted_images = self.sort_images_by_size(extracted_images)
        return self.create_thumb_sheet(sorted_images)

    def extract_and_save_images(self):
        os.makedirs(self.output_folder, exist_ok=True)
        with pymupdf.open(self.pdf_path) as doc:
            for page_index in range(len(doc)):
                self.process_page(doc, page_index)

    def process_page(self, doc: pymupdf.Document, page_index: int):
        page = doc[page_index]
        image_list = page.get_images()

        for image_index, img in enumerate(image_list, start=1):
            self.process_image(doc, page_index, image_index, img)

    def process_image(self, doc: pymupdf.Document, page_index: int, image_index: int, img: Tuple):

        xref, smask = img[0], img[1]
        image_bytes = doc.extract_image(xref)["image"]
        img_size = len(image_bytes) / 1024


        if img_size < self.threshold:

            return

        self.save_image(doc, xref, smask, page_index, image_index)

    def save_image(self, doc: pymupdf.Document, xref: int, smask: int, page_index: int, image_index: int):
        pix = self.create_pixmap(doc, xref, smask)
        output_path = os.path.join(self.output_folder, f"page_{page_index}-image_{image_index}.png")
        pix.save(output_path)

    def create_pixmap(self, doc: pymupdf.Document, xref: int, smask: int) -> pymupdf.Pixmap:
        pix1 = pymupdf.Pixmap(doc.extract_image(xref)["image"])
        if smask > 0:

            mask = pymupdf.Pixmap(doc.extract_image(smask)["image"])
            return pymupdf.Pixmap(pix1, mask)
        return pix1


def main():
    root = tk.Tk()
    app = PDFImageExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()