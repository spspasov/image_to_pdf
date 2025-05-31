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

def save_images_to_pdf(images, output_path):
    if not images:
        print("No images found.")
        return

    image_list = []
    for img_path in tqdm(images, desc="Processing images"):
        image = Image.open(img_path).convert("RGB")
        image_list.append(image)

    first_image = image_list.pop(0)
    first_image.save(output_path, save_all=True, append_images=image_list)
    print(f"\n✅ PDF saved to: {output_path}")

if __name__ == "__main__":
    base_folder = "folders"
    output_pdf = "combined_learningaids.pdf"
    all_images = collect_images_from_learningaids(base_folder)
    save_images_to_pdf(all_images, output_pdf)
