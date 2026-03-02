import cv2
import os

INPUT_DIR = "data/raw_images"
OUTPUT_DIR = "data/processed_images"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def preprocess_image(image_path, save_path):
    img = cv2.imread(image_path)

    # Resize if too large (keep detail)
    height, width = img.shape[:2]
    if width > 2500:
        scale_percent = 70
        img = cv2.resize(img, (int(width * scale_percent / 100),
                               int(height * scale_percent / 100)))

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Light denoising (preserve strokes)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # Mild contrast boost
    alpha = 1.4   # contrast
    beta = 10     # brightness
    enhanced = cv2.convertScaleAbs(denoised, alpha=alpha, beta=beta)

    # DO NOT threshold
    # DO NOT morphology
    # Keep grayscale for OCR

    cv2.imwrite(save_path, enhanced)


def preprocess_all():
    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            input_path = os.path.join(INPUT_DIR, file)
            output_path = os.path.join(OUTPUT_DIR, file)

            preprocess_image(input_path, output_path)
            print(f"Processed: {file}")


if __name__ == "__main__":
    preprocess_all()