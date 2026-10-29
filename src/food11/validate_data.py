import argparse
import hashlib
import sys
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

SPLITS = ["training", "validation", "evaluation"]


def report(name: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    print(f"{status}: {name}" + (f" - {detail}" if detail else ""))
    return passed


def validate(root: Path, min_per_class: int, tau: float) -> bool:
    results = []

    # 1. Exact class folders in every split
    folders_ok = True
    for split in SPLITS:
        split_dir = root / split
        if not split_dir.exists():
            folders_ok = False
            continue

        actual = sorted(p.name for p in split_dir.iterdir() if p.is_dir())
        if actual != sorted(CLASSES):
            folders_ok = False

    results.append(report("11 class folders in every split", folders_ok))

    # 2. Every image opens, is RGB and 128x128
    images_ok = True
    for split in SPLITS:
        for class_name in CLASSES:
            class_dir = root / split / class_name
            if not class_dir.exists():
                continue

            for path in class_dir.iterdir():
                if not path.is_file():
                    continue

                try:
                    with Image.open(path) as img:
                        if img.mode != "RGB" or img.size != (128, 128):
                            images_ok = False
                except Exception:
                    images_ok = False

    results.append(report("all images valid RGB 128x128", images_ok))

    # 3. Minimum number of images per class
    counts = {}
    minimum_ok = True

    for split in SPLITS:
        counts[split] = {}

        for class_name in CLASSES:
            class_dir = root / split / class_name
            count = (
                sum(1 for p in class_dir.iterdir() if p.is_file())
                if class_dir.exists()
                else 0
            )
            counts[split][class_name] = count

            if count < min_per_class:
                minimum_ok = False

    results.append(
        report(
            f"at least {min_per_class} images per class",
            minimum_ok,
        )
    )

    # 4. No image content appears in more than one split
    seen = {}
    duplicates = []

    for split in SPLITS:
        for class_name in CLASSES:
            class_dir = root / split / class_name
            if not class_dir.exists():
                continue

            for path in class_dir.iterdir():
                if not path.is_file():
                    continue

                digest = hashlib.md5(path.read_bytes()).hexdigest()

                if digest in seen and seen[digest][0] != split:
                    duplicates.append((seen[digest][1], path))
                else:
                    seen[digest] = (split, path)

    duplicate_ok = len(duplicates) == 0
    results.append(
        report(
            "no duplicate images across splits",
            duplicate_ok,
            f"{len(duplicates)} duplicates found",
        )
    )

    # 5. Training/validation class-share difference <= tau
    distribution_ok = True

    train_total = sum(counts["training"].values())
    val_total = sum(counts["validation"].values())

    if train_total == 0 or val_total == 0:
        distribution_ok = False
    else:
        for class_name in CLASSES:
            train_share = counts["training"][class_name] / train_total
            val_share = counts["validation"][class_name] / val_total

            if abs(train_share - val_share) > tau:
                distribution_ok = False

    results.append(
        report(
            f"training/validation class-share difference <= {tau}",
            distribution_ok,
        )
    )

    return all(results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--min-per-class", type=int, default=50)
    parser.add_argument("--tau", type=float, default=0.05)
    args = parser.parse_args()

    ok = validate(args.dataset, args.min_per_class, args.tau)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
