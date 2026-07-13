"""
PDF/PPTX/DOCX -> Markdown converter (Docling based)
----------------------------------------------------
- Converts every pdf/pptx/docx file in input_docs/ into a markdown file in output_md/
- Combined grid images (e.g. "3 subplots merged into one image") are automatically
  split into separate images, if there is a clear whitespace gap between subplots
- The markdown file is updated so each split image is referenced on its own line
"""

from pathlib import Path

import numpy as np
from PIL import Image

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc import ImageRefMode


# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------
INPUT_DIR = "input_docs"
OUTPUT_DIR = "output_md"

SUPPORTED_EXTENSIONS = (".pdf", ".pptx", ".docx")

# Grid-splitting tuning (adjust these if splitting doesn't work well)
WHITE_THRESHOLD = 245       # column mean brightness above this is considered "white"
MIN_GAP_WIDTH = 6           # a white gap narrower than this is ignored (avoids noise)
MIN_SEGMENT_SIZE = 40       # segments smaller than this are discarded as noise


# --------------------------------------------------------------------------
# STEP 1: Convert documents to Markdown using Docling
# --------------------------------------------------------------------------
def build_converter() -> DocumentConverter:
    """Builds a DocumentConverter with PDF pipeline options configured."""
    pipeline_opts = PdfPipelineOptions()
    pipeline_opts.images_scale = 2.0
    pipeline_opts.generate_picture_images = True

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)
        }
    )


def convert_documents(input_dir: Path, output_dir: Path, converter: DocumentConverter) -> list[Path]:
    """Converts every supported file in input_dir and saves it as markdown in output_dir.
    Returns the list of generated .md file paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_md_files = []

    for file in sorted(input_dir.glob("*")):
        if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        print(f"[convert] Processing {file.name} ...")
        result = converter.convert(str(file))

        md_out = output_dir / f"{file.stem}.md"
        result.document.save_as_markdown(md_out, image_mode=ImageRefMode.REFERENCED)

        print(f"[convert] ✔ {file.name} → {md_out.name}")
        generated_md_files.append(md_out)

    return generated_md_files


# --------------------------------------------------------------------------
# STEP 2: Split combined grid images into separate images
# --------------------------------------------------------------------------
def _find_gap_columns(gray: np.ndarray) -> np.ndarray:
    """Computes column-wise mean brightness and returns a boolean mask
    marking which columns are a 'white gap'."""
    col_means = gray.mean(axis=0)
    return col_means > WHITE_THRESHOLD


def _segments_from_gap_mask(gap_mask: np.ndarray) -> list[tuple[int, int]]:
    """Extracts real content segments (start, end) from the gap mask,
    ignoring gaps narrower than MIN_GAP_WIDTH."""
    n = len(gap_mask)
    segments = []
    start = None
    gap_run = 0

    for i in range(n):
        if not gap_mask[i]:
            if start is None:
                start = i
            gap_run = 0
        else:
            gap_run += 1
            if start is not None and gap_run >= MIN_GAP_WIDTH:
                segments.append((start, i - gap_run + 1))
                start = None

    if start is not None:
        segments.append((start, n))

    # filter out tiny/noise segments
    return [(s, e) for s, e in segments if (e - s) >= MIN_SEGMENT_SIZE]


def split_grid_image(image_path: Path) -> list[Path]:
    """
    Splits a combined grid image (e.g. 3 subplots side by side) into separate
    image files, if there is a clear whitespace gap between the subplots.

    Returns the list of split image paths (ordered left-to-right).
    If splitting isn't possible (only 1 segment found), returns the original
    image_path wrapped in a list.
    """
    img = Image.open(image_path).convert("RGB")
    gray = np.array(img.convert("L"))

    col_gap_mask = _find_gap_columns(gray)
    col_segments = _segments_from_gap_mask(col_gap_mask)

    if len(col_segments) <= 1:
        # nothing worth splitting, keep the original image
        return [image_path]

    split_paths = []
    stem = image_path.stem
    suffix = image_path.suffix

    for idx, (x0, x1) in enumerate(col_segments, start=1):
        cropped = img.crop((x0, 0, x1, img.height))
        out_path = image_path.with_name(f"{stem}_part{idx}{suffix}")
        cropped.save(out_path)
        split_paths.append(out_path)

    print(f"[split] {image_path.name} → split into {len(split_paths)} separate images")
    return split_paths


def process_images_dir(images_dir: Path) -> dict[str, list[Path]]:
    """Checks every image in images_dir, splits it if applicable, and returns
    a mapping: original_image_filename -> [new split image paths]"""
    if not images_dir.exists():
        return {}

    mapping = {}
    for img_file in sorted(images_dir.glob("*")):
        if img_file.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        splits = split_grid_image(img_file)
        if len(splits) > 1:
            mapping[img_file.name] = splits

    return mapping


# --------------------------------------------------------------------------
# STEP 3: Update the markdown file so split images are referenced on
#         separate lines
# --------------------------------------------------------------------------
def update_markdown_with_splits(md_path: Path, split_mapping: dict[str, list[Path]]) -> None:
    """Reads the markdown file, and wherever the original combined image is
    referenced, replaces that line with one markdown image line per split image."""
    if not split_mapping:
        return

    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines = []

    for line in lines:
        replaced = False
        for original_name, split_paths in split_mapping.items():
            if original_name in line and line.strip().startswith("!["):
                # replace the original image line with one line per split image
                for i, sp in enumerate(split_paths, start=1):
                    rel_path = f"{sp.parent.name}/{sp.name}"
                    new_lines.append(f"![Part {i}]({rel_path})")
                replaced = True
                break
        if not replaced:
            new_lines.append(line)

    md_path.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"[markdown] {md_path.name} updated with split image references")


def find_images_dir_for(md_path: Path) -> Path:
    """Docling usually stores images in a '<stem>_artifacts' or similar folder."""
    candidates = [
        md_path.parent / f"{md_path.stem}_artifacts",
        md_path.parent / f"{md_path.stem}_images",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]  # default guess, treated as empty if it doesn't exist


# --------------------------------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------------------------------
def main():
    input_dir = Path(INPUT_DIR)
    output_dir = Path(OUTPUT_DIR)

    converter = build_converter()
    md_files = convert_documents(input_dir, output_dir, converter)

    for md_path in md_files:
        images_dir = find_images_dir_for(md_path)
        split_mapping = process_images_dir(images_dir)
        update_markdown_with_splits(md_path, split_mapping)

    print("\n✔ All done. Check the output_md/ folder.")


if __name__ == "__main__":
    main()