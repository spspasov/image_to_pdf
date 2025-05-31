from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re
from tqdm import tqdm
import fitz  # PyMuPDF


def natural_sort_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', str(s))]

def collect_folders_with_images(root_dir):
    root_path = Path(root_dir)
    folders = []

    for subdir in sorted(root_path.iterdir()):
        learningaids_dir = subdir / "00_LEARNINGAIDS"
        if learningaids_dir.exists() and learningaids_dir.is_dir():
            images = sorted(learningaids_dir.glob("*.png"), key=natural_sort_key)
            if images:
                folders.append((subdir.name, images))
    return folders

def compress_image(image_path, max_width=1600):
    image = Image.open(image_path)
    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image.convert("RGB")

def create_chapter_page(title, width=1600, height=900):
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", size=64)
    except IOError:
        font = ImageFont.load_default()

    text = f"Chapter: {title}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill="black", font=font)
    return image

def pil_image_to_pdf_bytes(img):
    """Convert a PIL image to in-memory PDF bytes"""
    from io import BytesIO
    pdf_bytes = BytesIO()
    img.save(pdf_bytes, format="PDF")
    return pdf_bytes.getvalue()

def save_pdf_with_bookmarks(folders, output_path):
    doc = fitz.open()
    current_page = 0

    for folder_name, images in tqdm(folders, desc="Generating PDF with bookmarks"):
        # 1. Create chapter page
        chapter_img = create_chapter_page(folder_name)
        chapter_pdf = fitz.open("pdf", pil_image_to_pdf_bytes(chapter_img))
        doc.insert_pdf(chapter_pdf)
        doc.set_toc([*doc.get_toc(), [1, folder_name, current_page + 1]])
        current_page += len(chapter_pdf)

        # 2. Add images from that chapter
        for img_path in images:
            compressed_img = compress_image(img_path)
            img_pdf = fitz.open("pdf", pil_image_to_pdf_bytes(compressed_img))
            doc.insert_pdf(img_pdf)
            current_page += len(img_pdf)

    doc.save(output_path)
    print(f"\n✅ PDF with bookmarks saved to: {output_path}")

if __name__ == "__main__":
    base_folder = "folders"
    output_pdf = "learningaids_with_toc.pdf"
    folders_with_images = collect_folders_with_images(base_folder)
    save_pdf_with_bookmarks(folders_with_images, output_pdf)
