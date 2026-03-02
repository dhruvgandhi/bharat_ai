import easyocr
import os
import json
from datetime import datetime


INPUT_DIR = "data/processed_images"
OUTPUT_DIR = "data/ocr_text"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize reader (GPU enabled)
print("Loading EasyOCR model...")
reader = easyocr.Reader(['hi'], gpu=True)
print("Model loaded.\n")


def extract_text(image_path):
    results = reader.readtext(image_path)

    full_text = ""
    total_conf = 0
    count = 0

    # Sort by vertical position (top to bottom)
    results = sorted(results, key=lambda x: x[0][0][1])

    for (bbox, text, confidence) in results:
        full_text += text + "\n"
        total_conf += confidence
        count += 1

    avg_conf = total_conf / count if count > 0 else 0

    return full_text.strip(), round(avg_conf, 3)


def process_all():
    metadata = []

    for file in sorted(os.listdir(INPUT_DIR)):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):

            image_path = os.path.join(INPUT_DIR, file)
            page_name = os.path.splitext(file)[0]
            output_text_path = os.path.join(OUTPUT_DIR, f"{page_name}.txt")

            print(f"Processing: {file}")

            text, confidence = extract_text(image_path)

            # Save extracted text
            with open(output_text_path, "w", encoding="utf-8") as f:
                f.write(text)

            metadata.append({
                "page": page_name,
                "file": file,
                "text_file": f"{page_name}.txt",
                "confidence": confidence,
                "processed_at": datetime.now().isoformat()
            })

            print(f"Saved: {page_name}.txt | Confidence: {confidence}\n")

    # Save metadata file
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print("All pages processed successfully.")


if __name__ == "__main__":
    process_all()

# # from datetime import datetime
# import easyocr
# import os
# import cv2
# from src.ocr.preprocess import preprocess_image

# # Initialize GPU reader
# reader = easyocr.Reader(['as','bn'], gpu=True) # 'hi' covers Devanagari


# def extract_text(image_path):
#     try:
#         processed = preprocess_image(image_path)

#         result = reader.readtext(processed, detail=0, paragraph=True)

#         text = "\n".join(result)
#         return text.strip()

#     except Exception as e:
#         print(f"OCR Error: {e}")
#         return None


# def process_folder(input_folder, output_folder):
#     os.makedirs(output_folder, exist_ok=True)

#     for file in os.listdir(input_folder):
#         if file.lower().endswith((".png", ".jpg", ".jpeg")):
#             image_path = os.path.join(input_folder, file)
#             text = extract_text(image_path)

#             if text:
#                 output_file = os.path.join(
#                     output_folder, file.rsplit(".", 1)[0] + ".txt"
#                 )
#                 with open(output_file, "w", encoding="utf-8") as f:
#                     f.write(text)

#                 print(f"Saved: {output_file}")

# import sys
# from src.ocr.preprocess import preprocess_image
# import pytesseract
# from PIL import Image
# import os

# # Set path to tesseract executable (IMPORTANT for Windows)
# pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


# # def extract_text(image_path, lang="san"):
# #     try:
# #         img = Image.open(image_path)
# #         text = pytesseract.image_to_string(img, lang=lang)
# #         return text
# #     except Exception as e:
# #         print(f"OCR Error: {e}")
# #         return None
    
# def extract_text(image_path, lang="san"):
#     try:
#         print(f"Preprocessing: {image_path} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#         processed = preprocess_image(image_path)
#         print(f"Preprocessed: {image_path} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

#         text = pytesseract.image_to_string(
#             processed,
#             lang=lang,
#             config="--oem 3 --psm 6"
#         )
#         return text.strip()
#     except Exception as e:
#         print(f"OCR Error: {e}")
#         return None


# def process_folder(input_folder, output_folder):
#     os.makedirs(output_folder, exist_ok=True)

#     for file in os.listdir(input_folder):
#         if file.lower().endswith((".png", ".jpg", ".jpeg")):
#             print(f"Processing: {file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#             image_path = os.path.join(input_folder, file)
#             text = extract_text(image_path)

#             if text:
#                 output_file = os.path.join(
#                     output_folder, file.rsplit(".", 1)[0] + ".txt"
#                 )
#                 with open(output_file, "w", encoding="utf-8") as f:
#                     f.write(text)

#                 print(f"Processed: {file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#             else:
#                 print(f"Failed to process: {file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")