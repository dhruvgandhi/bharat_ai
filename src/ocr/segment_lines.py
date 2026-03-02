import cv2
import numpy as np
import os

INPUT_DIR = "data/processed_images"
OUTPUT_DIR = "data/segmented_lines"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def segment_lines(image_path):
    img = cv2.imread(image_path, 0)

    # Binary for line detection only
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    horizontal_projection = np.sum(thresh, axis=1)

    lines = []
    start = None

    for i, val in enumerate(horizontal_projection):
        if val > 1000 and start is None:
            start = i
        elif val <= 1000 and start is not None:
            end = i
            if end - start > 15:
                lines.append((start, end))
            start = None

    return img, lines


def segment_process_all():
    for file in os.listdir(INPUT_DIR):
        if file.endswith((".jpg", ".png")):
            path = os.path.join(INPUT_DIR, file)
            img, lines = segment_lines(path)

            base = os.path.splitext(file)[0]

            for idx, (start, end) in enumerate(lines):
                cropped = img[start:end, :]
                save_path = os.path.join(
                    OUTPUT_DIR, f"{base}_line_{idx}.png"
                )
                cv2.imwrite(save_path, cropped)

            print(f"Segmented: {file} → {len(lines)} lines")


if __name__ == "__main__":
    segment_process_all()