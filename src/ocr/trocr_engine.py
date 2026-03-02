import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import os

INPUT_DIR = "data/processed_images"
OUTPUT_DIR = "data/ocr_text_trocr"

os.makedirs(OUTPUT_DIR, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading TrOCR model...")

processor = TrOCRProcessor.from_pretrained(
    "microsoft/trocr-base-handwritten"
)
model = VisionEncoderDecoderModel.from_pretrained(
    "microsoft/trocr-base-handwritten"
).to(device)

print("Model loaded.\n")


def extract_text(image_path):
    image = Image.open(image_path).convert("RGB")

    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)

    with torch.no_grad():
        generated_ids = model.generate(pixel_values)

    generated_text = processor.batch_decode(
        generated_ids, skip_special_tokens=True
    )[0]

    return generated_text


def process_all():
    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(INPUT_DIR, file)
            print(f"Processing: {file}")

            text = extract_text(path)

            output_file = os.path.join(
                OUTPUT_DIR,
                os.path.splitext(file)[0] + ".txt"
            )

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)

            print("Saved:", output_file, "\n")


if __name__ == "__main__":
    process_all()