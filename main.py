import os
import io

import fitz
import pymupdf
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageDraw, ImageFont, ImageTk

# Create a Tkinter root window (it will not be shown)
root = tk.Tk()
root.withdraw()

# Open a file dialog to select the PDF file
file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

# Create thumbnail sheet of contained images that are not masks, sorted by size in KB, labeled by size in KB
if file_path:
    doc = fitz.open(file_path)  # open the selected PDF document

    pdf_directory = os.path.dirname(file_path)

    extracted_images = []

    for page_index in range(len(doc)):  # iterate over pdf pages
        page = doc[page_index]  # get the page
        image_list = page.get_images(full=True)

        for img in image_list:  # enumerate the image list
            xref = img[0]  # get the XREF of the image
            base_image = doc.extract_image(xref)  # extract the base image
            image_bytes = base_image["image"]
            image_size = len(image_bytes) / 1024  # size in KB

            extracted_images.append((image_bytes, image_size))

    doc.close()  # close the document

    if extracted_images:
        extracted_images.sort(key=lambda x: x[1], reverse=True)  # Sort by size in KB

        thumbnails = []
        for image_bytes, size in extracted_images:
            try:
                img = Image.open(io.BytesIO(image_bytes))
                img = img.convert("RGB")  # Ensure image mode is RGB
                img.thumbnail((100, 100))  # Creating a thumbnail
                thumbnails.append((img, size))
            except OSError as e:
                print(f"Error processing image: {e}")
                continue

        # Calculate the dimensions of the thumbnail sheet
        thumb_width, thumb_height = 100, 100
        sheet_width = thumb_width * len(thumbnails)
        sheet_height = thumb_height + 20  # Extra height for labels

        # Create a new blank image for the thumbnail sheet
        sheet = Image.new("RGB", (sheet_width, sheet_height))

        # Draw the thumbnails onto the sheet
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.load_default()  # Load a default font
        x_offset = 0
        for img, size in thumbnails:
            sheet.paste(img, (x_offset, 0))
            # Draw the label with the size
            draw.text((x_offset, thumb_height + 5), f"{size:.2f} KB", fill="white", font=font)
            x_offset += thumb_width

        # Save the thumbnail sheet
        thumbnail_sheet_path = os.path.join(pdf_directory, "thumbnail_sheet.png")
        sheet.save(thumbnail_sheet_path)

        print(f"Thumbnail sheet created at: {thumbnail_sheet_path}")

        #Open File in os explorer

        os.startfile(thumbnail_sheet_path)


    else:
        print("No images found in the document.")
else:
    print("No file selected")


# Ask for the threshold for image size in dialog using tkinter. Units are KB
treshold = 0
while treshold <= 0:
    treshold = int(input("Enter the treshold for image size in KB: "))
    if treshold <= 0:
        print("Treshold must be a positive integer")
print (f"Images below {treshold} KB will be skipped")

if file_path:
    # Get the directory of the selected PDF file
    pdf_directory = os.path.dirname(file_path)
    pdf_name = os.path.basename(file_path)


    # Create the subfolder in the same directory as the PDF file
    output_folder = os.path.join(pdf_directory, f"extracted_img_from_{pdf_name}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = pymupdf.open(file_path)  # open the selected PDF document

    for page_index in range(len(doc)):  # iterate over pdf pages
        page = doc[page_index]  # get the page
        image_list = page.get_images()

        # print the number of images found on the page
        if image_list:
            print(f"Found {len(image_list)} images on page {page_index}")
        else:
            print("No images found on page", page_index)

        for image_index, img in enumerate(image_list, start=1):  # enumerate the image list

            print(f"Extracting image {image_index} on page {page_index}")

            xref = img[0]  # get the XREF of the image
            smask = img[1]  # get the XREF of the mask, if any

            # Extract the image data
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Calculate the image size in KB
            img_size = len(image_bytes) / 1024

            # Print the image size
            print(f"Size of processed image is {img_size:.2f} KB")

            # Skip images below the threshold
            if img_size < treshold:
                print(f"Skipping image {image_index} on page {page_index}. Too small")
                continue

            pix1 = pymupdf.Pixmap(doc.extract_image(xref)["image"])  # create a Pixmap for the image

            if smask > 0:  # if there is a mask
                print("Mask found for image", image_index)
                mask = pymupdf.Pixmap(doc.extract_image(smask)["image"])  # create a Pixmap for the mask
                pix = pymupdf.Pixmap(pix1, mask)  # combine image and mask
            else:
                pix = pix1  # no mask, use the original image

            # Save the image in the subfolder
            pix.save(os.path.join(output_folder, "page_%s-image_%s.png" % (page_index, image_index)))
            pix = None

    doc.close()  # close the document
else:
    print("No file selected")