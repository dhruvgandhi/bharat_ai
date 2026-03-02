import sys
from src.ocr.segment_lines import segment_process_all
from src.ocr.ocr_engine import process_all
from src.ocr.preprocess import preprocess_all

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.main ocr")
        sys.exit(1)

    command = sys.argv[1]

    if command == "ocr":
        preprocess_all()
        segment_process_all()
        process_all()
    else:
        print("Unknown command")