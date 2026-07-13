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
WHITE_THRESHOLD = 235       # column/row mean brightness above this is considered a gap
MIN_GAP_WIDTH = 5           # a gap narrower than this is ignored (avoids noise)
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


def _trim_content_rows(gray: np.ndarray) -> tuple[int, int]:
    """Returns (y_start, y_end) of the main dark-content block inside a
    cropped image slice. Skips thin text rows (suptitles, OCR bleed) at the
    top by requiring rows to have a high density of dark pixels (image
    content), not just sparse text strokes."""
    h, w = gray.shape
    if h == 0:
        return 0, 0

    # For each row, count dark pixels and compute "density" = dark_count / width.
    # Real image content has high density (lots of dark pixels across the row),
    # while a row of small text strokes has low density.
    dark_mask = gray < (WHITE_THRESHOLD - 60)
    row_density = dark_mask.sum(axis=1) / max(1, w)

    # Density threshold: text rows have density < 0.15; image rows have >= 0.30.
    DENSITY_THRESHOLD = 0.30
    is_content = row_density >= DENSITY_THRESHOLD

    if not is_content.any():
        # Fall back to first/last dark row.
        any_dark = dark_mask.any(axis=1)
        if not any_dark.any():
            return 0, h
        ys = np.where(any_dark)[0]
        return int(ys[0]), int(ys[-1]) + 1

    ys = np.where(is_content)[0]
    return int(ys[0]), int(ys[-1]) + 1


def _find_subplot_titles(img: Image.Image, segments: list[tuple[int, int]],
                          horizontal: bool) -> list[str]:
    """Best-effort: read the title text near the top of each subplot using
    RapidOCR (already available via Docling). Falls back to 'Part N' if OCR
    fails or returns no text."""
    titles: list[str] = []
    w, h = img.size
    try:
        from rapidocr import RapidOCR  # type: ignore
        engine = RapidOCR()
    except Exception:
        return [f"Part {i + 1}" for i in range(len(segments))]

    for i, (a0, a1) in enumerate(segments):
        if horizontal:
            crop = img.crop((a0, 0, a1, h))
        else:
            crop = img.crop((0, a0, w, a1))
        cw, ch = crop.size
        title_band = crop.crop((0, 0, cw, max(1, ch // 5)))
        text = ""
        try:
            output = engine(title_band)
            # RapidOCR returns a RapidOCROutput object with .txts (tuple).
            txts = getattr(output, "txts", None) or []
            text = " ".join(t.strip() for t in txts if t and t.strip())
        except Exception:
            text = ""
        # Trim noise / overly long OCR output.
        text = text.strip()
        if len(text) > 80:
            text = text[:80].rstrip() + "…"
        titles.append(text or f"Part {i + 1}")
    return titles


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


def split_grid_image(image_path: Path) -> list[tuple[Path, str]]:
    """
    Splits a combined grid image (e.g. 3 subplots side by side or stacked
    vertically) into separate image files, if there is a clear whitespace gap
    between the subplots.

    Returns a list of (split_image_path, title) tuples. The title is the OCR'd
    subplot title (e.g. "Thresholds: (0.03, 0.09)"), or "Part N" as fallback.
    If splitting isn't possible (only 1 segment found in either direction),
    returns the original image_path with an empty title wrapped in a tuple.
    """
    img = Image.open(image_path).convert("RGB")
    gray = np.array(img.convert("L"))

    # Try horizontal (column) splits first.
    col_gap_mask = _find_gap_columns(gray)
    col_segments = _segments_from_gap_mask(col_gap_mask)

    # Try vertical (row) splits as well.
    row_means = gray.mean(axis=1)
    row_gap_mask = row_means > WHITE_THRESHOLD
    row_segments = _segments_from_gap_mask(row_gap_mask)

    # Pick whichever gives more segments (more useful for grid images).
    if len(col_segments) >= len(row_segments) and len(col_segments) > 1:
        segments = col_segments
        horizontal = True
    elif len(row_segments) > 1:
        segments = row_segments
        horizontal = False
    else:
        # nothing worth splitting, keep the original image
        return [(image_path, "")]

    split_paths: list[tuple[Path, str]] = []
    stem = image_path.stem
    suffix = image_path.suffix

    # Lazy import — only when we actually need to OCR titles.
    try:
        from rapidocr import RapidOCR  # type: ignore
        engine = RapidOCR()
    except Exception:
        engine = None

    for idx, (a0, a1) in enumerate(segments, start=1):
        if horizontal:
            cropped = img.crop((a0, 0, a1, img.height))
        else:
            cropped = img.crop((0, a0, img.width, a1))

        # Trim out any stray title/OCR text that bleeds into the part. Use a
        # small padding so the per-subplot title stays visible, while the
        # suptitle (which sits well above the first row of dense content) is
        # removed.
        cropped_gray = np.array(cropped.convert("L"))
        y0, y1 = _trim_content_rows(cropped_gray)
        title_pad = max(8, int(cropped.height * 0.04))
        y0_padded = max(0, y0 - title_pad)
        if y1 - y0_padded > 20:
            cropped = cropped.crop((0, y0_padded, cropped.width, y1))

        # Add a small top margin to keep the subplot title visible.
        cw, ch = cropped.size
        top_pad = max(8, int(ch * 0.05))
        bottom_pad = max(8, int(ch * 0.05))
        if cw > 0 and ch > 0:
            from PIL import ImageOps
            cropped = ImageOps.expand(cropped, border=(0, top_pad, 0, bottom_pad), fill="white")

        # OCR the title band on the *trimmed* crop so we read the subplot title,
        # not the print-output/suptitle text that bled into the part.
        title = f"Part {idx}"
        if engine is not None:
            cw2, ch2 = cropped.size
            title_band = cropped.crop((0, 0, cw2, max(1, ch2 // 5)))
            try:
                output = engine(title_band)
                txts = getattr(output, "txts", None) or []
                text = " ".join(t.strip() for t in txts if t and t.strip())
                text = text.strip()
                if len(text) > 60:
                    text = text[:60].rstrip() + "…"
                if text:
                    title = text
            except Exception:
                pass

        out_path = image_path.with_name(f"{stem}_part{idx}{suffix}")
        cropped.save(out_path)
        split_paths.append((out_path, title))

    direction = "horizontally" if horizontal else "vertically"
    print(f"[split] {image_path.name} → split {direction} into {len(split_paths)} separate images")
    return split_paths


def process_images_dir(images_dir: Path) -> dict[str, list[tuple[Path, str]]]:
    """Checks every image in images_dir, splits it if applicable, and returns
    a mapping: original_image_filename -> [(split_image_path, title), ...]"""
    if not images_dir.exists():
        return {}

    mapping: dict[str, list[tuple[Path, str]]] = {}
    for img_file in sorted(images_dir.glob("*")):
        if img_file.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        splits = split_grid_image(img_file)
        if len(splits) > 1:
            mapping[img_file.name] = splits

    return mapping


# --------------------------------------------------------------------------
# STEP 3: Update the markdown file so each image line is preceded by the
#         image filename as a caption, and split images appear on their
#         own lines.
# --------------------------------------------------------------------------
def _format_image_block(prefix: str, sp: Path, title: str, idx: int) -> list[str]:
    """Returns 2 markdown lines: the caption (filename) and the image line."""
    name = sp.name
    label = title or f"Part {idx}"
    return [
        f"**{name}**",
        f"![{label}]({prefix}{name})",
    ]


def update_markdown_with_splits(md_path: Path, split_mapping: dict[str, list[tuple[Path, str]]]) -> None:
    """For every image referenced in the markdown:
    - If it was split into parts, replace the single line with one block per
      part (each block = caption line + image line).
    - Otherwise, prepend a caption line (the image filename) above the line.
    This ensures each image has its filename visible as text above it, while
    the image itself stays free of in-image text artefacts.
    """
    content = md_path.read_text(encoding="utf-8")
    new_lines: list[str] = []

    for line in content.splitlines():
        replaced = False
        if line.strip().startswith("!["):
            # Find the filename in this image line.
            inside = ""
            if "(" in line and ")" in line:
                inside = line.split("(", 1)[1].rsplit(")", 1)[0]
            image_filename = inside.rsplit("/", 1)[-1] if inside else ""

            if image_filename and image_filename in split_mapping:
                # Split image: emit one block per part.
                prefix = ""
                if "/" in inside:
                    prefix = inside.rsplit("/", 1)[0] + "/"
                for i, (sp, title) in enumerate(split_mapping[image_filename], start=1):
                    new_lines.extend(_format_image_block(prefix, sp, title, i))
                replaced = True
            elif image_filename:
                # Non-split image: prepend caption line with the filename.
                new_lines.append(f"**{image_filename}**")
        if not replaced:
            new_lines.append(line)

    md_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"[markdown] {md_path.name} updated with image captions")


def strip_code_blocks_near_images(md_path: Path) -> None:
    """Removes ```fenced code blocks``` that appear right next to an image
    (with only blank lines in between) so that each image is rendered on its
    own without surrounding OCR'd code text from the figure region."""
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Pre-compute which line indices are images.
    image_idx = {i for i, line in enumerate(lines) if line.strip().startswith("![")}

    out: list[str] = []
    i = 0
    n = len(lines)
    removed = 0

    while i < n:
        if i not in image_idx:
            out.append(lines[i])
            i += 1
            continue

        # We are at an image line. Walk backwards through `out` and drop any
        # ``` fenced blocks whose only content between block-end and this image
        # is blank lines.
        # First, find trailing blanks in `out` to know where to start scanning.
        scan_end = len(out)
        while scan_end > 0 and out[scan_end - 1].strip() == "":
            scan_end -= 1

        # From scan_end-1 backwards, walk back across blank lines + closing fence
        # lines; if we hit a closing fence (```) preceded by a matching opening
        # fence and only blanks/lines-with-code in between, drop them all.
        j = scan_end - 1
        # Only proceed if the immediately preceding non-blank line is a closing fence.
        if j >= 0 and out[j].strip() == "```":
            # Find the matching opening fence (also ```).
            depth = 0
            k = j
            found_open = -1
            while k >= 0:
                if out[k].strip() == "```":
                    if depth == 0:
                        found_open = k
                        break
                    depth -= 1
                k -= 1
            if found_open > 0 and out[found_open - 1].strip() != "```":
                # Confirm the block contains only blank lines or a single ```-style
                # code block (i.e. no prose). Anything that looks like a heading,
                # paragraph, or list is preserved.
                block_lines = out[found_open + 1 : j]
                only_blanks = all(bl.strip() == "" for bl in block_lines)
                if only_blanks:
                    # Drop everything from found_open up to (but not including) the
                    # blanks between the block and the image, then re-add one blank.
                    del out[found_open:]
                    removed += 1
                    # Make sure exactly one blank line separates previous content.
                    if out and out[-1].strip() != "":
                        out.append("")

        # Now emit the image line.
        out.append(lines[i])
        i += 1

    if removed:
        md_path.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"[cleanup] removed {removed} code block(s) sitting next to image(s) in {md_path.name}")


def find_images_dir_for(md_path: Path) -> Path:
    """Docling usually stores images in a '<stem>_artifacts' or similar folder.
    Searches both the markdown's parent directory and a nested OUTPUT_DIR sub-
    directory (some Docling versions nest artifacts under output_md/output_md/).
    """
    output_dir = Path(OUTPUT_DIR)
    candidates = [
        md_path.parent / f"{md_path.stem}_artifacts",
        md_path.parent / f"{md_path.stem}_images",
        output_dir / f"{md_path.stem}_artifacts",
        output_dir / f"{md_path.stem}_images",
        output_dir / "output_md" / f"{md_path.stem}_artifacts",
        output_dir / "output_md" / f"{md_path.stem}_images",
    ]
    seen = set()
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
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
        strip_code_blocks_near_images(md_path)

    print("\n✔ All done. Check the output_md/ folder.")


if __name__ == "__main__":
    main()