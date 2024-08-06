# PDF Image Extractor User Manual

## 1. Introduction

The PDF Image Extractor is an application for extracting images from PDF files. This manual provides guidance on using the application's features.

## 2. Getting Started

### 2.1 Launching the Application

Upon launching the PDF Image Extractor, you will see a graphical user interface (GUI) with various options and controls.

### 2.2 Selecting a PDF File

1. Click the "Browse" button next to the "Selected PDF" field.
2. Select the desired PDF file in the file dialog.
3. The selected file path will be displayed in the interface.

### 2.3 Choosing an Output Folder

1. Click the "Browse" button next to the "Output Folder" field.
2. Select or create a directory for storing extracted images.
3. The chosen output path will be shown in the interface.

## 3. Core Functionalities

### 3.1 Creating Thumbnail Previews

1. After selecting a PDF, click the "Create Thumbnail Preview" button.
2. The application will generate a thumbnail sheet of images from the PDF.
3. The preview will open upon completion.
4. Note: The thumbnail generation process applies the current threshold and duplicate removal settings.

### 3.2 Extracting Images

1. Ensure a PDF file and output folder are selected.
2. Configure extraction options as needed (see Section 4).
3. Click the "Extract Images" button to start the extraction process.
4. Progress and results will be displayed in the log area.

## 4. Configurable Options

### 4.1 Use Threshold

- When enabled, filters images based on a specified size threshold.
- Enter the desired threshold value in kilobytes (KB) in the "Threshold (KB)" field.

### 4.2 Remove Duplicates

- Eliminates duplicate images using perceptual hashing (pHash) technology.
- Adjustable parameters:
  - Hash Size: Affects the precision of the pHash. Larger values may increase processing time.
  - Hash Threshold: Sets the similarity threshold for identifying duplicates.

## 5. Features

- PDF Processing: Uses pymupdf for PDF parsing and image extraction.
- Duplicate Detection: Uses perceptual hashing to identify similar images.
- Size-based Filtering: Allows filtering of images based on file size.
- Preview Functionality: Generates thumbnail previews of PDF contents.
- Graphical User Interface: Provides a GUI for operation.
- Customizable Options: Offers adjustable parameters for the extraction process.

## 6. Troubleshooting

- Ensure all required libraries (pymupdf, PIL, imagehash) are installed.
- Verify that the selected PDF file is not corrupted or password-protected.
- Check write permissions for the chosen output folder.
- Refer to the log area for error messages and warnings.

## 7. Conclusion

The PDF Image Extractor allows users to extract images from PDF documents. By using its features and options, users can process PDFs and extract images according to their specifications.