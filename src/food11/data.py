from pathlib import Path
from PIL import Image
import shutil

CLASSES = {
    0: "Bread",
    1: "Dairy product",
    2: "Dessert",
    3: "Egg",
    4: "Fried food",
    5: "Meat",
    6: "Noodles-Pasta",
    7: "Rice",
    8: "Seafood",
    9: "Soup",
    10: "Vegetable-Fruit",
}

SPLITS = ["training", "evaluation", "validation"]

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "food11_raw"
PROCESSED = ROOT / "data" / "food11_processed"
MINI = ROOT / "data" / "food11_processed_mini"


def process_dataset(output_dir, max_per_class=None):
    if output_dir.exists():
        shutil.rmtree(output_dir)

    for split in SPLITS:
        counts = {name: 0 for name in CLASSES.values()}

        for img_path in (RAW / split).iterdir():
            if not img_path.is_file():
                continue

            class_id = int(img_path.name.split("_")[0])
            class_name = CLASSES[class_id]

            if max_per_class is not None and counts[class_name] >= max_per_class:
                continue

            dest = output_dir / split / class_name
            dest.mkdir(parents=True, exist_ok=True)

            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img = img.resize((128, 128))
                img.save(dest / img_path.name)

            counts[class_name] += 1


process_dataset(PROCESSED)
process_dataset(MINI, max_per_class=100)

print("Done")