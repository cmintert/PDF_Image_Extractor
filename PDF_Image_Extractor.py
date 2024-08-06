import os
import io
import tkinter as tk
from tkinter import ttk, filedialog
from typing import List, Tuple, Dict
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageTk
import imagehash

class PDFImageExtractorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("PDF Image Extractor")
        self.master.geometry("800x725")

        self.extractor = PDFImageExtractor()

        self.create_widgets()

    def create_widgets(self):
        """
        Creates and arranges all widgets for the PDF Image Extractor GUI.

        This method sets up the main layout of the application, including:
        - File selection frame for choosing a PDF file
        - Output folder selection frame for specifying where extracted images will be saved
        - Options frame with checkboxes for various extraction settings
        - Settings frame for adjusting threshold, hash size, and hash threshold
        - Action buttons for creating thumbnail previews and extracting images
        - Log area for displaying operation progress and results
        - Thumbnail frame for showing image previews

        The method uses tkinter and ttk widgets to create a user-friendly interface.
        It also sets up scrollbars, configures grid weights for responsive layout,
        and initializes variables for storing user input and preferences.

        Args:
            self: The instance of the class containing this method.

        Returns:
            None

        Attributes:
            main_frame (ttk.Frame): The main container for all widgets.
            file_frame (ttk.Frame): Frame for PDF file selection.
            output_frame (ttk.Frame): Frame for output folder selection.
            options_frame (ttk.LabelFrame): Frame for extraction options.
            settings_frame (ttk.LabelFrame): Frame for additional settings.
            button_frame (ttk.Frame): Frame for action buttons.
            log_frame (ttk.Frame): Frame for the log area.
            thumbnail_frame (ttk.Frame): Frame for displaying image thumbnails.

        Note:
            This method should be called during the initialization of the GUI application.
            It assumes that certain instance variables (e.g., self.master, self.extractor)
            have been properly initialized before calling this method.
        """

        # Main content frame
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # File selection
        self.file_frame = ttk.Frame(self.main_frame, padding="10")
        self.file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.file_label = ttk.Label(self.file_frame, text="Selected PDF:")
        self.file_label.grid(row=0, column=0, sticky=tk.W)

        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(
            self.file_frame, textvariable=self.file_path, width=50
        )
        self.file_entry.grid(row=0, column=1, padx=5)

        self.browse_button = ttk.Button(
            self.file_frame, text="Browse", command=self.browse_file
        )
        self.browse_button.grid(row=0, column=2)

        # Output folder selection
        self.output_frame = ttk.Frame(self.main_frame, padding="10")
        self.output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.output_label = ttk.Label(self.output_frame, text="Output Folder:")
        self.output_label.grid(row=0, column=0, sticky=tk.W)

        self.output_path = tk.StringVar()
        self.output_entry = ttk.Entry(
            self.output_frame, textvariable=self.output_path, width=50
        )
        self.output_entry.grid(row=0, column=1, padx=5)

        self.output_browse_button = ttk.Button(
            self.output_frame, text="Browse", command=self.browse_output_folder
        )
        self.output_browse_button.grid(row=0, column=2)

        # Options frame
        self.options_frame = ttk.LabelFrame(self.main_frame, text="Options", padding="10")
        self.options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        self.option_vars = {}
        for i, (option, default) in enumerate(self.extractor.options.items()):
            if option not in ["phash_size", "phash_threshold"]:
                var = tk.BooleanVar(value=default)
                self.option_vars[option] = var
                ttk.Checkbutton(
                    self.options_frame,
                    text=option.replace('_', ' ').title(),
                    variable=var,
                    command=self.update_options
                ).grid(row=i, column=0, sticky=tk.W)

        # Add the Option settings frame
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Option Settings", padding="10")
        self.settings_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        # Threshold setting
        ttk.Label(self.settings_frame, text="Threshold (KB):").grid(row=0, column=0, sticky=tk.W)
        self.threshold = tk.IntVar(value=0)
        self.threshold_entry = ttk.Entry(self.settings_frame, textvariable=self.threshold, width=10)
        self.threshold_entry.grid(row=0, column=1, padx=5)

        ttk.Label(self.settings_frame, text="Hash Size:").grid(row=1, column=0, sticky=tk.W)
        self.phash_size_var = tk.IntVar(value=self.extractor.options['phash_size'])
        self.phash_size_entry = ttk.Entry(self.settings_frame, textvariable=self.phash_size_var, width=5)
        self.phash_size_entry.grid(row=1, column=1, padx=5)

        ttk.Label(self.settings_frame, text="Hash Threshold:").grid(row=2, column=0, sticky=tk.W)
        self.phash_threshold_var = tk.IntVar(value=self.extractor.options['phash_threshold'])
        self.phash_threshold_entry = ttk.Entry(self.settings_frame, textvariable=self.phash_threshold_var, width=5)
        self.phash_threshold_entry.grid(row=2, column=1, padx=5)


        # Action buttons
        self.button_frame = ttk.Frame(self.main_frame, padding="10")
        self.button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))

        self.preview_button = ttk.Button(
            self.button_frame,
            text="Create Thumbnail Preview",
            command=self.create_preview,
        )
        self.preview_button.grid(row=0, column=0, padx=5)

        self.extract_button = ttk.Button(
            self.button_frame, text="Extract Images", command=self.extract_images
        )
        self.extract_button.grid(row=0, column=1, padx=5)

        # Log area
        self.log_frame = ttk.Frame(self.main_frame, padding="10")
        self.log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD, width=80, height=20)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.scrollbar = ttk.Scrollbar(
            self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=self.scrollbar.set)

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(4, weight=1)

        # Thumbnail frame (created last and lifted to top)
        self.thumbnail_frame = ttk.Frame(self.master, padding="10", width=200, height=250)
        self.thumbnail_frame.place(relx=1.0, rely=0, anchor="ne")
        self.thumbnail_frame.lift()  # Bring to front
        self.thumbnail_frame.pack_propagate(False)  # Prevent frame from shrinking

        self.thumbnail_label = ttk.Label(self.thumbnail_frame)
        self.thumbnail_label.pack()

        self.thumbnail_image = ttk.Label(self.thumbnail_frame)
        self.thumbnail_image.pack(expand=True, fill=tk.BOTH)

        # Adjust grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(5, weight=1)

    def update_options(self):
        """
        Updates the extractor options based on the current GUI settings.

        This method synchronizes the state of the GUI widgets with the extractor's
        options. It performs the following actions:

        1. Updates boolean options in the extractor based on checkbox states.
        2. Updates pHash-related settings (size and threshold) from their respective
           entry fields.
        3. Enables or disables the threshold entry field based on the 'use_threshold'
           option.
        4. Enables or disables pHash-related entry fields based on the
           'remove_duplicates' option.

        The method ensures that the extractor's configuration always reflects the
        current state of the GUI, allowing for dynamic updates of extraction parameters.

        Args:
            self: The instance of the class containing this method.

        Returns:
            None

        Attributes modified:
            self.extractor.options (dict): Updated with new values from GUI widgets.

        GUI elements affected:
            self.threshold_entry (ttk.Entry): Enabled/disabled based on 'use_threshold'.
            self.phash_size_entry (ttk.Entry): Enabled/disabled based on 'remove_duplicates'.
            self.phash_threshold_entry (ttk.Entry): Enabled/disabled based on 'remove_duplicates'.

        Note:
            This method should be called whenever there's a change in the GUI options,
            typically in response to user interactions with checkboxes or entry fields.
            It assumes that self.option_vars, self.extractor, and various ttk.Entry
            widgets have been properly initialized.
        """
        for option, var in self.option_vars.items():
            self.extractor.options[option] = var.get()

        # Update pHash settings
        self.extractor.options['phash_size'] = self.phash_size_var.get()
        self.extractor.options['phash_threshold'] = self.phash_threshold_var.get()

        # Enable/disable threshold entry based on use_threshold option
        if self.extractor.options["use_threshold"]:
            self.threshold_entry.config(state='normal')
        else:
            self.threshold_entry.config(state='disabled')

        # Enable/disable pHash settings based on remove_duplicates option
        if self.extractor.options["remove_duplicates"]:
            self.phash_size_entry.config(state='normal')
            self.phash_threshold_entry.config(state='normal')
        else:
            self.phash_size_entry.config(state='disabled')
            self.phash_threshold_entry.config(state='disabled')

    def browse_file(self):
        """
        Opens a file dialog for the user to select a PDF file.

        If a file is selected, updates the file path and sets a default output folder.
        Logs the selected file path and the default output folder.

        Logs an error message if an exception occurs during file selection.
        """

        try:
            file_path = self.extractor.select_pdf_file()
            if file_path:
                self.file_path.set(file_path)
                self.log("PDF file selected: " + file_path)
                # Set default output folder
                default_output = os.path.join(
                    os.path.dirname(file_path),
                    f"extracted_img_from_{os.path.basename(file_path)}",
                )
                self.output_path.set(default_output)
                self.log(f"Default output folder set to: {default_output}")
                self.log("----------------------------------------")
                # Load and display the cover thumbnail
                self.load_cover_thumbnail(file_path)

        except Exception as e:
            self.log(f"Error selecting PDF file: {str(e)}")

    def load_cover_thumbnail(self, pdf_path):
        try:
            # Open the PDF and get the first page
            doc = pymupdf.open(pdf_path)
            first_page = doc[0]

            # Render the page to a pixmap
            pix = first_page.get_pixmap(matrix=pymupdf.Matrix(0.2))

            # Convert pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Resize the image to fit in the GUI
            img.thumbnail((200, 200))

            # Convert PIL Image to PhotoImage
            photo = ImageTk.PhotoImage(img)

            # Update the thumbnail label
            self.thumbnail_image.config(image=photo)
            self.thumbnail_image.image = photo  # Keep a reference

            doc.close()
        except Exception as e:
            self.log(f"Error loading PDF cover: {str(e)}")


    def browse_output_folder(self):
        """
        Opens a directory dialog for the user to select an output folder.

        If a folder is selected, updates the output path and logs the selected folder.
        Logs an error message if an exception occurs during folder selection.
        """
        try:
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.output_path.set(folder_path)
                self.log(f"Output folder selected: {folder_path}")
        except Exception as e:
            self.log(f"Error selecting output folder: {str(e)}")

    def create_preview(self):
        """
        Creates a thumbnail preview of the selected PDF file.

        Logs an error message if no PDF file is selected or if an exception occurs during the preview creation.
        """
        if not self.file_path.get():
            self.log("Error: Please select a PDF file first.")
            return

        try:
            self.log("Creating thumbnail preview...")
            thumbnail_sheet = self.extractor.create_thumbnail_preview()
            self.log("Thumbnail sheet created at: " + thumbnail_sheet)
            os.startfile(thumbnail_sheet)
        except Exception as e:
            self.log(f"Error creating thumbnail preview: {str(e)}")

    def extract_images(self):
        if not self.file_path.get():
            self.log("Error: Please select a PDF file first.")
            return

        try:
            self.extractor.threshold = self.threshold.get() if self.extractor.options["use_threshold"] else 0
            self.extractor.output_folder = self.output_path.get()
            if not self.extractor.output_folder:
                raise ValueError("Please select an output folder.")

            self.update_options()  # Ensure pHash settings are updated

            self.log("Extracting images with options:")
            for option, value in self.extractor.options.items():
                self.log(f"- {option.replace('_', ' ').title()}: {value}")
            if self.extractor.options["use_threshold"]:
                self.log(f"- Threshold: {self.extractor.threshold} KB")
            self.log(f"Output folder: {self.extractor.output_folder}")

            self.log("----------------------------------------")
            self.log("Extracting images...")
            # Wait for logging to happen before starting the extraction
            self.master.update()
            self.extractor.extract_and_save_images()
            self.log("Image extraction completed.")
            self.log(f"Images have been extracted to: {self.extractor.output_folder}")
            self.log("----------------------------------------")

        except ValueError as ve:
            self.log(f"Error: {str(ve)}")
        except Exception as e:
            self.log(f"Error extracting images: {str(e)}")

    def log(self, message):
        """
        Logs a message to the text area and scrolls to the end.

        Args:
            message (str): The message to log.
        """
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)


class PDFImageExtractor:
    def __init__(self):
        self.pdf_path = ""
        self.pdf_directory = ""
        self.pdf_name = ""
        self.output_folder = ""
        self.threshold = 0
        self.current_p_hashes: List = []
        self.options: Dict[str, bool] = {
            "use_threshold": True,
            "remove_duplicates": True,
            "phash_size": 8,  # New option for pHash size
            "phash_threshold": 5  # New option for pHash comparison threshold
        }

    def phash_image(self, image: Image) -> imagehash.ImageHash:
        """
        Calculates the pHash value

        Args:
            image (Image.Image): The image to calculate the pHash for.

        Returns:
            str: The pHash value of the image.
        """
        p_hash = imagehash.phash(image, hash_size=self.options["phash_size"])
        return p_hash

    def is_duplicate(self, new_hash: imagehash.ImageHash) -> bool:
        """
        Checks if the new hash is a duplicate based on the current threshold

        Args:
            new_hash (imagehash.ImageHash): The hash to check for duplicates

        Returns:
            bool: True if it's a duplicate, False otherwise
        """
        for existing_hash in self.current_p_hashes:
            if (new_hash - existing_hash) <= self.options['phash_threshold']:
                return True
        return False

    def select_pdf_file(self) -> str:
        """
        Opens a file dialog for the user to select a PDF file.

        If a valid file is selected, updates the PDF path, directory, and name.
        Raises a FileNotFoundError if the selected file does not exist.

        Returns:
            str: The path of the selected PDF file.
        """
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.pdf_path:
            if not os.path.isfile(self.pdf_path):
                raise FileNotFoundError(
                    f"The selected file does not exist: {self.pdf_path}"
                )
            self.pdf_directory = os.path.dirname(self.pdf_path)
            self.pdf_name = os.path.basename(self.pdf_path)
        return self.pdf_path

    def extract_images(self) -> List[Tuple[bytes, float]]:
        """
        Extracts images from the selected PDF file.

        Raises a ValueError if no PDF file is selected or if an error occurs while reading the PDF file.
        Raises a RuntimeError for unexpected errors during image extraction.

        Returns:
            List[Tuple[bytes, float]]: A list of tuples containing image bytes and their sizes in KB.
        """
        if not self.pdf_path:
            raise ValueError("No PDF file selected.")

        extracted_images = []
        try:
            with pymupdf.open(self.pdf_path) as doc:
                for page in doc:
                    image_list = page.get_images(full=True)
                    for img in image_list:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_size = len(image_bytes) / 1024  # size in KB
                        extracted_images.append((image_bytes, image_size))
        except pymupdf.fitz.FileDataError as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error extracting images: {str(e)}")

        return extracted_images

    def filter_images(self, images: List[Tuple[bytes, float]]) -> List[Tuple[bytes, float]]:
        """
        Filters images based on threshold and duplicate settings.

        Args:
            images (List[Tuple[bytes, float]]): A list of tuples containing image bytes and their sizes in KB.

        Returns:
            List[Tuple[bytes, float]]: A filtered list of image tuples.
        """
        filtered_images = []
        self.current_p_hashes = []  # Reset pHashes for thumbnail preview

        for image_bytes, size in images:
            if self.options["use_threshold"] and size < self.threshold:
                continue

            if self.options["remove_duplicates"]:
                try:
                    img = Image.open(io.BytesIO(image_bytes))
                    img = img.convert("RGB")
                    hash_to_check = self.phash_image(img)
                    if self.is_duplicate(hash_to_check):
                        continue
                    self.current_p_hashes.append(hash_to_check)
                except Exception as e:
                    print(f"Warning: Failed to process image for duplicate check: {str(e)}")
                    continue

            filtered_images.append((image_bytes, size))

        return filtered_images

    def sort_images_by_size(
        self, images: List[Tuple[bytes, float]]
    ) -> List[Tuple[Image.Image, float]]:
        """
        Sorts images by size in descending order and creates thumbnails.

        Args:
            images (List[Tuple[bytes, float]]): A list of tuples containing image bytes and their sizes in KB.

        Returns:
            List[Tuple[Image.Image, float]]: A list of tuples containing thumbnail images and their sizes in KB.
        """
        images.sort(key=lambda x: x[1], reverse=True)  # Sort by size in KB
        thumbnails = []
        for image_bytes, size in images:
            try:
                img = Image.open(io.BytesIO(image_bytes))
                img = img.convert("RGB")  # Ensure image mode is RGB
                img.thumbnail((100, 100))  # Creating a thumbnail
                thumbnails.append((img, size))
            except OSError as e:
                print(f"Warning: Failed to process an image: {str(e)}")
            except Exception as e:
                print(f"Unexpected error processing an image: {str(e)}")
        return thumbnails

    def create_thumb_sheet(self, images: List[Tuple[Image.Image, float]]) -> str:
        """
        Creates a thumbnail sheet from a list of images and saves it as an image.

        Args:
            images (List[Tuple[Image.Image, float]]): A list of tuples containing images and their sizes in KB.

        Raises:
            ValueError: If the images list is empty.
            IOError: If saving the thumbnail sheet fails.

        Returns:
            str: The path to the saved thumbnail sheet.
        """
        if not images:
            raise ValueError("No images to create thumbnail sheet.")

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
            draw.text(
                (x_offset, y_offset + thumb_height + 5),
                f"{size:.2f} KB",
                fill="white",
                font=font,
            )

        thumbnail_sheet_path = os.path.join(self.pdf_directory, "thumbnail_sheet.png")
        try:
            sheet.save(thumbnail_sheet_path)
        except Exception as e:
            raise IOError(f"Failed to save thumbnail sheet: {str(e)}")
        return thumbnail_sheet_path

    def create_thumbnail_preview(self):
        """
        Creates a thumbnail preview of the selected PDF file, respecting threshold and duplicate settings.

        Raises:
            ValueError: If no PDF file is selected.

        Returns:
            str: The path to the created thumbnail sheet.
        """
        if not self.pdf_path:
            raise ValueError("No PDF file selected.")

        extracted_images = self.extract_images()
        filtered_images = self.filter_images(extracted_images)
        sorted_images = self.sort_images_by_size(filtered_images)
        return self.create_thumb_sheet(sorted_images)

    def extract_and_save_images(self):
        """
        Extracts and saves images from the selected PDF file.

        Raises:
            ValueError: If no PDF file is selected or no output folder is specified.
            IOError: If creating the output folder fails.
            ValueError: If an error occurs while reading the PDF file.
            RuntimeError: For unexpected errors during PDF processing.
        """
        if not self.pdf_path:
            raise ValueError("No PDF file selected.")
        if not self.output_folder:
            raise ValueError("No output folder specified.")

        self.current_p_hashes = [] # Reset the current pHashes

        try:
            os.makedirs(self.output_folder, exist_ok=True)
        except OSError as e:
            raise IOError(f"Failed to create output folder: {str(e)}")

        try:
            with pymupdf.open(self.pdf_path) as doc:
                for page_index in range(len(doc)):
                    self.process_page(doc, page_index)
        except pymupdf.fitz.FileDataError as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error processing PDF: {str(e)}")

    def process_page(self, doc: pymupdf.Document, page_index: int):
        """
        Processes a page of the PDF to extract and handle images.

        Args:
            doc (pymupdf.Document): The PDF document object.
            page_index (int): The index of the page to process.

        Raises:
            RuntimeError: If an error occurs while processing an image.
        """
        page = doc[page_index]
        image_list = page.get_images()

        for image_index, img in enumerate(image_list, start=1):
            try:
                self.process_image(doc, page_index, image_index, img)
            except Exception as e:
                print(
                    f"Warning: Failed to process image {image_index} on page {page_index}: {str(e)}"
                )

    def process_image(
        self, doc: pymupdf.Document, page_index: int, image_index: int, img: Tuple
    ):
        """
        Processes an image from a PDF page if it is larger than a threshold. It also checks if the image is a duplicate.

        Args:
            doc (pymupdf.Document): The PDF document object.
            page_index (int): The index of the page containing the image.
            image_index (int): The index of the image on the page.
            img (Tuple): A tuple containing image reference and smask.

        Raises:
            RuntimeError: If an error occurs while processing the image.
        """
        xref, smask = img[0], img[1]
        try:
            image_bytes = doc.extract_image(xref)["image"]
            img_size = len(image_bytes) / 1024
            pil_image = Image.open(io.BytesIO(image_bytes))

            if self.check_conditions(img_size, pil_image):
                return

            self.save_image(doc, xref, smask, page_index, image_index)
        except Exception as e:
            raise RuntimeError(f"Failed to process image: {str(e)}")

    def check_conditions(self, img_size: int, image:Image.Image) -> bool:
        """
        Checks if the image size is less than the threshold or if the image is a duplicate.
        Respects the options set by the user.

        Args:
            img_size (int): The size of the image in KB.
            image (Image.Image): The image to check for duplicates.

        Returns:
            bool: True if the image should be skipped, False otherwise.
        """
        if self.options["use_threshold"] and img_size < self.threshold:
            return True

        if self.options["remove_duplicates"]:
            try:
                hash_to_check = self.phash_image(image)
                if self.is_duplicate(hash_to_check):
                    print(f"Duplicate image found: {hash_to_check}")
                    return True
                self.current_p_hashes.append(hash_to_check)
            except Exception as e:
                raise RuntimeError(f"Failed to hash image: {str(e)}")

        return False

    def save_image(
        self,
        doc: pymupdf.Document,
        xref: int,
        smask: int,
        page_index: int,
        image_index: int,
    ):
        """
        Saves an image from a PDF page to the output folder.

        Args:
            doc (pymupdf.Document): The PDF document object.
            xref (int): The reference number of the image.
            smask (int): The soft mask reference number.
            page_index (int): The index of the page containing the image.
            image_index (int): The index of the image on the page.

        Raises:
            IOError: If saving the image fails.
        """
        try:
            pix = self.create_pixmap(doc, xref, smask)
            output_path = os.path.join(
                self.output_folder, f"page_{page_index}-image_{image_index}.png"
            )
            pix.save(output_path)
        except Exception as e:
            raise IOError(f"Failed to save image: {str(e)}")

    def create_pixmap(
        self, doc: pymupdf.Document, xref: int, smask: int
    ) -> pymupdf.Pixmap:
        """
        Creates a pixmap from a PDF image reference and optional soft mask.

        Args:
            doc (pymupdf.Document): The PDF document object.
            xref (int): The reference number of the image.
            smask (int): The soft mask reference number.

        Raises:
            RuntimeError: If creating the pixmap fails.

        Returns:
            pymupdf.Pixmap: The created pixmap.
        """
        try:
            pix1 = pymupdf.Pixmap(doc.extract_image(xref)["image"])
            if smask > 0:
                mask = pymupdf.Pixmap(doc.extract_image(smask)["image"])
                return pymupdf.Pixmap(pix1, mask)
            return pix1
        except Exception as e:
            raise RuntimeError(f"Failed to create pixmap: {str(e)}")


def main():
    """
    Initializes the main application window and starts the Tkinter event loop.

    This function creates an instance of the PDFImageExtractorGUI class and
    starts the Tkinter main loop to run the GUI application.
    """
    root = tk.Tk()
    _ = PDFImageExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
