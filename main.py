from pathlib import Path
from PIL import Image
import re
from tqdm import tqdm


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]


def collect_images_from_learningaids(root_dir):
    root_path = Path(root_dir)
    image_files = []

    for subdir in sorted(root_path.iterdir()):
        learningaids_dir = subdir / "00_LEARNINGAIDS"
        if learningaids_dir.exists() and learningaids_dir.is_dir():
            images = sorted(learningaids_dir.glob("*.png"), key=natural_sort_key)
            image_files.extend(images)

    return image_files


def compress_image(image, max_width=1600, quality=75):
    # Resize if wider than max_width
    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    # Convert to RGB (required for JPEG)
    return image.convert("RGB")


def save_images_to_pdf(images, output_path, max_width=1600, quality=75):
    if not images:
        print("No images found.")
        return

    image_list = []

    for img_path in tqdm(images, desc="Compressing images"):
        image = Image.open(img_path)
        compressed = compress_image(image, max_width=max_width, quality=quality)
        image_list.append(compressed)

    first_image = image_list.pop(0)
    first_image.save(
        output_path,
        save_all=True,
        append_images=image_list,
        quality=quality
    )
    print(f"\n✅ Compressed PDF saved to: {output_path}")


if __name__ == "__main__":
    base_folder = "folders"
    output_pdf = "compressed_learningaids.pdf"
    all_images = collect_images_from_learningaids(base_folder)
    save_images_to_pdf(all_images, output_pdf)
