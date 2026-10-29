import shutil
from pathlib import Path

from PIL import Image

CLASSES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]

SPLITS = ["training", "evaluation", "validation"]

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "food11_raw"
PROCESSED = ROOT / "data" / "food11_processed"
MINI = ROOT / "data" / "food11_processed_mini"


def category_from_filename(filename: str) -> str:
    class_id = int(filename.split("_")[0])
    return CLASSES[class_id]


def resize_image(img: Image.Image, size: int = 128) -> Image.Image:
    return img.convert("RGB").resize((size, size))


def process_dataset(output_dir, max_per_class=None):
    if output_dir.exists():
        shutil.rmtree(output_dir)

    for split in SPLITS:
        counts = {name: 0 for name in CLASSES}

        for img_path in (RAW / split).iterdir():
            if not img_path.is_file():
                continue

            class_name = category_from_filename(img_path.name)

            if max_per_class is not None and counts[class_name] >= max_per_class:
                continue

            dest = output_dir / split / class_name
            dest.mkdir(parents=True, exist_ok=True)

            with Image.open(img_path) as img:
                img = resize_image(img)
                img.save(dest / img_path.name)

            counts[class_name] += 1


if __name__ == "__main__":
    process_dataset(PROCESSED)
    process_dataset(MINI, max_per_class=100)
    print("Done")
