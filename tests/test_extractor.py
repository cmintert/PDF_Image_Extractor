import unittest
import os
import shutil
from unittest.mock import MagicMock, patch
import sys

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PDF_Image_Extractor import PDFImageExtractor

class TestPDFImageExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = PDFImageExtractor()
        # Mock file system interactions
        self.test_pdf_path = "test_doc.pdf"
        self.test_output_folder = "test_output"

    def test_set_pdf_file_success(self):
        with patch("os.path.isfile", return_value=True):
            self.extractor.set_pdf_file(self.test_pdf_path)
            self.assertEqual(self.extractor.pdf_path, self.test_pdf_path)
            self.assertEqual(self.extractor.pdf_name, "test_doc.pdf")

    def test_set_pdf_file_not_found(self):
        with patch("os.path.isfile", return_value=False):
            with self.assertRaises(FileNotFoundError):
                self.extractor.set_pdf_file("nonexistent.pdf")

    @patch("pymupdf.open")
    def test_extract_images_no_pdf_selected(self, mock_open):
        with self.assertRaises(ValueError) as cm:
            self.extractor.extract_images()
        self.assertEqual(str(cm.exception), "No PDF file selected.")

    @patch("pymupdf.open")
    def test_extract_and_save_images_calls_process_page(self, mock_open):
        # Setup mocks
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_open.return_value.__enter__.return_value = mock_doc

        # Setup extractor
        with patch("os.path.isfile", return_value=True):
            self.extractor.set_pdf_file(self.test_pdf_path)
        self.extractor.output_folder = self.test_output_folder

        # Mock process_page to avoid complex logic in this test
        self.extractor.process_page = MagicMock()

        # Run
        with patch("os.makedirs"):
            self.extractor.extract_and_save_images()

        # Verify
        self.extractor.process_page.assert_called_once()
        self.assertEqual(self.extractor.process_page.call_args[0][1], 0) # page_index 0

    def test_log_callback(self):
        # Create a mock callback
        log_callback = MagicMock()

        # Trigger a warning (by mocking process_page to fail if we wanted,
        # or testing filter_images with bad data)
        # Let's test filter_images directly since it is easier to isolate

        # Create a fake image tuple (bytes, size)
        # We need bytes that Image.open fails on to trigger the exception in filter_images
        bad_image_bytes = b"not an image"
        images = [(bad_image_bytes, 100)]

        self.extractor.options["remove_duplicates"] = True

        # Run filter_images
        self.extractor.filter_images(images, log_callback=log_callback)

        # Verify callback was called with warning
        log_callback.assert_called()
        self.assertTrue("Warning" in log_callback.call_args[0][0])

if __name__ == "__main__":
    unittest.main()
