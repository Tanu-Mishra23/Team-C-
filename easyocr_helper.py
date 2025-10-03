import easyocr

# Initialize reader once (English by default)
reader = easyocr.Reader(['en'])

def extract_text_from_image(image_path):
    """
    Extracts text from an image using EasyOCR.
    :param image_path: Path to the image file
    :return: Extracted text as string
    """
    results = reader.readtext(image_path)
    extracted_text = " ".join([res[1] for res in results])
    return extracted_text
