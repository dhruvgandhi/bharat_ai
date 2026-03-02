import os
import re
import cv2
import numpy as np
from pdf2image import convert_from_path
import easyocr

# ---------------- CONFIG ----------------
PDF_PATH = "data/trimmedpdfs/trimmed.pdf"
OUTPUT_DIR = "data/output"
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
PROC_DIR = os.path.join(OUTPUT_DIR, "processed")
SHLOK_DIR = os.path.join(OUTPUT_DIR, "shlokas")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)
os.makedirs(SHLOK_DIR, exist_ok=True)

# ---------------- GPU OCR INIT ----------------
reader = easyocr.Reader(['hi'], gpu=True)

# ---------------- PREPROCESS ----------------
def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur to remove tiny noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Otsu threshold (better for old books)
    _, thresh = cv2.threshold(
        blur, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Remove small noise blobs
    kernel = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    return cleaned

# ---------------- COLUMN SPLIT ----------------
def split_columns(img):
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi/180,
        threshold=100,
        minLineLength=500,
        maxLineGap=10
    )

    h, w = img.shape[:2]
    split_x = w // 2  # fallback

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x1 - x2) < 10:  # vertical line
                split_x = x1
                break

    left = img[:, :split_x]
    right = img[:, split_x:]

    return left, right

# ---------------- OCR PAGE ----------------
def ocr_page(img):
    result = reader.readtext(img, detail=0, paragraph=True)
    return "\n".join(result)

# ---------------- PROCESS PDF ----------------
pages = convert_from_path(PDF_PATH, dpi=300)

full_text = ""

for i, page in enumerate(pages):
    img = np.array(page)
    img_path = os.path.join(IMAGE_DIR, f"page_{i}.png")
    cv2.imwrite(img_path, img)

    processed = preprocess(img)
    proc_path = os.path.join(PROC_DIR, f"page_{i}_proc.png")
    cv2.imwrite(proc_path, processed)

    left, right = split_columns(processed)
    cv2.imwrite(os.path.join(PROC_DIR, f"page_{i}_left.png"), left)
    cv2.imwrite(os.path.join(PROC_DIR, f"page_{i}_right.png"), right)
    text_left = ocr_page(left)
    text_right = ocr_page(right)
    print(f"Page {i} Left OCR done. Length: {len(text_left)} chars | Page {i} Right OCR done. Length: {len(text_right)} chars")
    full_text += "\n" + text_left + "\n" + text_right
    with open(os.path.join(OUTPUT_DIR, f"page_{i}.txt"), "w", encoding="utf-8") as f:
        f.write(text_left + "\n" + text_right)

# ---------------- SHLOK EXTRACTION ----------------
pattern = r"(?:\|\|\s*(\d+)\s*\|\||॥\s*(\d+)\s*॥)"
matches = list(re.finditer(pattern, full_text))

for idx, match in enumerate(matches):
    shlok_num = match.group(1) if match.group(1) else match.group(2)

    start = match.start()
    end = matches[idx+1].start() if idx+1 < len(matches) else len(full_text)
    section = full_text[start:end].strip()

    lines = section.split("\n")
    shlok_text = lines[0]
    explanation = "\n".join(lines[1:]).strip()

    with open(os.path.join(SHLOK_DIR, f"Shloak{shlok_num}.txt"), "w", encoding="utf-8") as f:
        f.write(shlok_text)

    with open(os.path.join(SHLOK_DIR, f"ShloakExplain{shlok_num}.txt"), "w", encoding="utf-8") as f:
        f.write(explanation)

print("OCR Pipeline Completed.")