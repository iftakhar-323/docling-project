"""
PDF/PPTX/DOCX -> Markdown converter (Docling based)
----------------------------------------------------
- Converts every pdf/pptx/docx file in input_docs/ into a markdown file in output_md/
- Combined grid images (e.g. "3 subplots merged into one image") are automatically
  split into separate images, if there is a clear whitespace gap between subplots
- The markdown file is updated so each split image is referenced on its own line
- NEW: Every image (split or not) is also run through full-page OCR (RapidOCR),
  and the extracted text is written into the markdown directly below the image,
  so handwritten / printed text inside images becomes real, searchable text —
  not just an embedded picture.
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
COMBINED_MD_NAME = "combined.md"           # single merged markdown output
COMBINED_IMAGES_DIR = "all_images"          # shared image folder for the merge

SUPPORTED_EXTENSIONS = (".pdf", ".pptx", ".docx")

# Grid-splitting tuning (adjust these if splitting doesn't work well)
WHITE_THRESHOLD = 235       # column/row mean brightness above this is considered a gap
MIN_GAP_WIDTH = 20          # a gap narrower than this is ignored (avoids noise from text spacing)
MIN_SEGMENT_SIZE = 120      # segments smaller than this are discarded as noise
# An aspect-ratio sanity check: if any candidate segment is unreasonably
# narrow vs the full image, we reject the whole split (it's almost certainly
# a page with text columns, not a grid of subplots).
MIN_SEGMENT_RATIO = 0.18    # smallest segment must be >= this fraction of full width/height

# Full-image OCR tuning
OCR_MIN_CONFIDENCE = 0.0    # RapidOCR score threshold below which a line is dropped
                             # (set to e.g. 0.3 if you see too much garbage text)


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


def _safe_stem(stem: str, max_len: int = 80) -> str:
    """Trim a file stem so it can safely become a folder/filename. Linux caps
    individual path components at 255 bytes; we cap at 80 to leave headroom
    for suffixes like `_artifacts` and `__image_000123_abcdef_part1.png`."""
    if len(stem) <= max_len:
        return stem
    # Keep the tail of the stem so the file's actual identifier is preserved
    # rather than truncated mid-name.
    return "x_" + stem[-max_len + 2:]


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

        # Use a length-safe stem to avoid Linux's 255-byte filename cap when
        # Docling later tries to make `<stem>_artifacts/`.
        safe = _safe_stem(file.stem)
        md_out = output_dir / f"{safe}.md"
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
    top by requiring a long run of dense rows (real image content), not just
    one or two dense rows that may be text descenders or punctuation."""
    h, w = gray.shape
    if h == 0:
        return 0, 0

    # For each row, count dark pixels and compute "density" = dark_count / width.
    # Real image content has high density (lots of dark pixels across the row),
    # while a row of small text strokes has low density.
    dark_mask = gray < (WHITE_THRESHOLD - 60)
    row_density = dark_mask.sum(axis=1) / max(1, w)

    # Find the first run of MIN_RUN consecutive dense rows. Image content has
    # long dense stretches; text rows are short isolated dense strokes.
    DENSITY_THRESHOLD = 0.30
    MIN_RUN = 15
    is_dense = row_density >= DENSITY_THRESHOLD

    start_y = 0
    run = 0
    found = False
    for y in range(h):
        if is_dense[y]:
            run += 1
            if run >= MIN_RUN:
                # First row of this long run is our content start.
                start_y = y - run + 1
                found = True
                break
        else:
            run = 0

    if not found:
        # No long dense run found: fall back to first dark row, or full image.
        any_dark = dark_mask.any(axis=1)
        if not any_dark.any():
            return 0, h
        ys = np.where(any_dark)[0]
        return int(ys[0]), int(ys[-1]) + 1

    # Now find the end: walk from start_y to find the last dense row that is
    # followed by enough dense rows to be content (avoid stopping at a text
    # descender above another text band).
    end_y = h
    run = 0
    last_dense = start_y
    for y in range(start_y, h):
        if is_dense[y]:
            run += 1
            last_dense = y
        else:
            if run >= MIN_RUN:
                # This was a real content run; keep last_dense as current end.
                end_y = last_dense + 1
            run = 0
    if run >= MIN_RUN:
        end_y = last_dense + 1

    # If everything after start_y is sparse text (no MIN_RUN block), keep
    # start_y to end of image rather than nothing.
    if end_y <= start_y:
        end_y = h

    return int(start_y), int(end_y)


# --------------------------------------------------------------------------
# NEW: Full-image OCR (extracts ALL text in an image, not just a title band)
# --------------------------------------------------------------------------
_OCR_ENGINE = None  # lazy singleton so we only construct RapidOCR once


def _get_ocr_engine():
    """Returns a cached RapidOCR engine instance, or None if unavailable."""
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        try:
            from rapidocr import RapidOCR  # type: ignore
            _OCR_ENGINE = RapidOCR()
        except Exception as e:
            print(f"[ocr] RapidOCR unavailable ({e}); full-image OCR will be skipped.")
            _OCR_ENGINE = False  # sentinel: "tried and failed", don't retry
    return _OCR_ENGINE or None


def extract_full_text_from_image(image_path: Path) -> str:
    """Runs OCR over the ENTIRE image (not just a title band) and returns the
    recognized text as multi-line plain text, ordered top-to-bottom / left-to-
    right the way RapidOCR naturally returns boxes (reading order).

    Used so that handwritten/printed content inside an image (e.g. a scanned
    notebook page) is also captured as real, searchable text in the markdown,
    in addition to the embedded image itself.

    Returns "" if OCR is unavailable or finds no text.
    """
    engine = _get_ocr_engine()
    if engine is None:
        return ""

    try:
        img = Image.open(image_path).convert("RGB")
        result = engine(img)
    except Exception as e:
        print(f"[ocr] failed on {image_path.name}: {e}")
        return ""

    boxes = getattr(result, "boxes", None)
    txts = getattr(result, "txts", None) or []
    scores = getattr(result, "scores", None) or []

    if not txts:
        return ""

    # Pair up (text, score, box) so we can sort into natural reading order
    # (top-to-bottom by the box's mean y-coordinate) even if the engine
    # returns detections out of order.
    items = []
    for i, t in enumerate(txts):
        t = (t or "").strip()
        if not t:
            continue
        score = scores[i] if i < len(scores) else 1.0
        if score is not None and score < OCR_MIN_CONFIDENCE:
            continue
        y = 0.0
        if boxes is not None and i < len(boxes):
            try:
                pts = boxes[i]
                y = float(sum(p[1] for p in pts) / len(pts))
            except Exception:
                y = float(i)  # fall back to detection order
        else:
            y = float(i)
        items.append((y, t))

    items.sort(key=lambda x: x[0])
    lines = [t for _, t in items]
    return "\n".join(lines).strip()


def _find_subplot_titles(img: Image.Image, segments: list[tuple[int, int]],
                          horizontal: bool) -> list[str]:
    """Best-effort: read the title text near the top of each subplot using
    RapidOCR (already available via Docling). Falls back to 'Part N' if OCR
    fails or returns no text."""
    titles: list[str] = []
    w, h = img.size
    engine = _get_ocr_engine()
    if engine is None:
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
    """Extracts real content segments (start, end) from the gap mask.

    Scans the mask for runs of consecutive SOLID (non-gap) pixels. Each gap
    in between is checked separately: only gaps >= MIN_GAP_WIDTH are
    treated as real separators. Gaps narrower than MIN_GAP_WIDTH are
    bridged so they don't fragment a real content block."""
    n = len(gap_mask)
    if n == 0:
        return []

    # Build a "narrow-gap-bridged" mask: True only where the gap run length
    # so far (and projected forward) is wide enough to count as a real gap.
    # Easier: find solid runs directly and split them on real gaps.
    segments = []
    seg_start = 0        # start of the current candidate segment
    in_segment = not gap_mask[0]   # are we currently inside a solid run?
    gap_len = 0          # length of the current gap (gap_mask=True) run

    for i in range(n):
        if not gap_mask[i]:
            # solid pixel
            if not in_segment:
                # transitioning from gap into a new solid run
                in_segment = True
                seg_start = i
            gap_len = 0
        else:
            # gap pixel
            gap_len += 1
            if in_segment and gap_len >= MIN_GAP_WIDTH:
                # close current segment at i - gap_len (end of last solid)
                segments.append((seg_start, i - gap_len + 1))
                in_segment = False
                gap_len = 0

    # Close a trailing segment that runs to the end.
    if in_segment:
        segments.append((seg_start, n))

    # Filter out tiny/noise segments.
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

    # Sanity check: if any candidate segment is unreasonably narrow vs the
    # full image, this isn't a real grid — it's a page with text columns /
    # rows. Don't split, keep the original image intact.
    full_extent = gray.shape[1] if horizontal else gray.shape[0]
    for s, e in segments:
        seg_extent = e - s
        if seg_extent < full_extent * MIN_SEGMENT_RATIO:
            print(
                f"[split] {image_path.name}: rejected split "
                f"(candidate segment {seg_extent}px is < "
                f"{int(MIN_SEGMENT_RATIO * 100)}% of full {full_extent}px — "
                f"likely text spacing, not a real grid gap)"
            )
            return [(image_path, "")]

    split_paths: list[tuple[Path, str]] = []
    stem = image_path.stem
    suffix = image_path.suffix

    # Lazy import — only when we actually need to OCR titles.
    engine = _get_ocr_engine()

    # Pre-OCR the per-subplot title for each segment by reading the title band
    # from the ORIGINAL (untrimmed) image at the segment's column range. We do
    # this here, before cropping, because the trim step below intentionally
    # removes any text band from the saved file — once trimmed, the title is
    # gone from the image and OCR can't recover it. So we capture the title
    # text up front and emit it as a markdown line above each image instead.
    segment_titles: list[str] = []
    if engine is not None:
        # Detect the title-band row range once on the full image: rows with
        # density 0.05..0.30 sitting between two quiet zones (typical pattern:
        # [code text] / gap / [subplot title] / gap / [dense content]).
        # We look at columns restricted to the segment being processed so we
        # only OCR text from that subplot.
        full_dark = gray < (WHITE_THRESHOLD - 60)
        full_row_density = full_dark.sum(axis=1) / max(1, gray.shape[1])

        for seg_idx, (a0, a1) in enumerate(segments, start=1):
            seg_dark = full_dark[:, a0:a1]
            seg_row_density = seg_dark.sum(axis=1) / max(1, seg_dark.shape[1])
            # Find the title band: the bottom-most run of 1..6 rows where
            # density is in (0.05, 0.30), sitting directly above a long dense
            # run (>= 30 rows of density >= 0.50).
            # Step 1: locate the topmost long dense run.
            dense_run_start = -1
            run = 0
            for y in range(seg_row_density.shape[0]):
                if seg_row_density[y] >= 0.50:
                    run += 1
                    if run >= 30:
                        dense_run_start = y - run + 1
                        break
                else:
                    run = 0
            title_text = ""
            if dense_run_start > 0:
                # Step 2: look at the rows just above the dense run. Find
                # the bottommost contiguous text band (rows 0.05..0.30) that
                # starts within 60 px of the dense run.
                scan_top = max(0, dense_run_start - 60)
                # Find a candidate title band: walk down from the top of this
                # scan window. Each band is text density surrounded by blanks.
                bands: list[tuple[int, int]] = []
                band_start = -1
                for y in range(scan_top, dense_run_start):
                    d = seg_row_density[y]
                    if 0.04 < d < 0.35:
                        if band_start < 0:
                            band_start = y
                    else:
                        if band_start >= 0:
                            bands.append((band_start, y - 1))
                            band_start = -1
                if band_start >= 0:
                    bands.append((band_start, dense_run_start - 1))
                # Pick the bottommost band (closest to dense content) — that's
                # most likely the per-subplot title, not the suptitle above.
                if bands:
                    title_band_top, title_band_bot = bands[-1]
                    # Pad a little top/bottom to give OCR room.
                    pad = 3
                    y0 = max(0, title_band_top - pad)
                    y1 = min(gray.shape[0], title_band_bot + pad + 1)
                    if horizontal:
                        title_crop = img.crop((a0, y0, a1, y1))
                    else:
                        title_crop = img.crop((0, y0, gray.shape[1], y1))
                    try:
                        out = engine(title_crop)
                        txts = getattr(out, "txts", None) or []
                        # Skip lines that look like Python code (heuristic:
                        # lines containing '=' or starting with 'plt.' are
                        # the print() output, not the rendered subplot title).
                        filtered = []
                        for t in txts:
                            s = (t or "").strip()
                            if not s:
                                continue
                            if s.startswith("plt.") or "import " in s or "=" in s and "(" in s:
                                continue
                            filtered.append(s)
                        if filtered:
                            title_text = " ".join(filtered).strip()
                            if len(title_text) > 80:
                                title_text = title_text[:80].rstrip() + "…"
                    except Exception:
                        pass
            segment_titles.append(title_text)
    else:
        segment_titles = [""] * len(segments)

    for idx, (a0, a1) in enumerate(segments, start=1):
        if horizontal:
            cropped = img.crop((a0, 0, a1, img.height))
        else:
            cropped = img.crop((0, a0, img.width, a1))

        # Trim out any stray title/OCR text that bleeds into the part. The
        # per-subplot title has already been captured above (segment_titles)
        # and will be emitted as a markdown line above each image, so the
        # saved image file itself stays free of text artefacts.
        cropped_gray = np.array(cropped.convert("L"))
        y0, y1 = _trim_content_rows(cropped_gray)

        # Look for any text band (sparse dark rows) sitting between (y0 - 30)
        # and y0. If found, trim everything above the start of that band.
        dark_mask = cropped_gray < (WHITE_THRESHOLD - 60)
        h_local, w_local = cropped_gray.shape
        row_density = dark_mask.sum(axis=1) / max(1, w_local)

        # Find the topmost dense row (y0) and check rows just above it for any
        # text-like content. If rows just above are sparse text, drop them.
        scan_top = max(0, y0 - 40)
        text_band_start = scan_top
        for y in range(scan_top, y0):
            if 0.03 < row_density[y] < 0.30:
                text_band_start = y
            elif row_density[y] == 0.0:
                continue
            else:
                # Either dense or blank — stop scanning up.
                break
        # Keep tiny top padding only if there's text immediately above content
        # (i.e. the per-subplot title).
        if text_band_start < y0 and row_density[text_band_start:y0].mean() > 0.05:
            # Per-subplot title present — keep a few px of it.
            keep_top = max(text_band_start, y0 - 6)
        else:
            keep_top = y0

        if y1 - keep_top > 20:
            cropped = cropped.crop((0, keep_top, cropped.width, y1))

        # Add a small top margin to keep the subplot title visible.
        cw, ch = cropped.size
        top_pad = max(8, int(ch * 0.05))
        bottom_pad = max(8, int(ch * 0.05))
        if cw > 0 and ch > 0:
            from PIL import ImageOps
            cropped = ImageOps.expand(cropped, border=(0, top_pad, 0, bottom_pad), fill="white")

        # Use the per-subplot title we OCR'd up front (before trim removed the
        # title text from the image). Fall back to "Part N" when nothing was
        # detected.
        title = segment_titles[idx - 1] if idx - 1 < len(segment_titles) else ""
        if not title:
            title = f"Part {idx}"

        out_path = image_path.with_name(f"{stem}_part{idx}{suffix}")
        cropped.save(out_path)
        split_paths.append((out_path, title))

    direction = "horizontally" if horizontal else "vertically"
    print(f"[split] {image_path.name} → split {direction} into {len(split_paths)} separate images")
    return split_paths


def _is_already_split(img_file: Path) -> bool:
    """True if this PNG is itself a part produced by a previous split pass
    (e.g. contains `_part1`, `_part2`). Used to avoid re-splitting when the
    per-file processing loop runs against an already-shared folder."""
    name = img_file.stem
    import re as _re
    return bool(_re.search(r"_part\d+$", name))


def process_images_dir(images_dir: Path) -> dict[str, list[tuple[Path, str]]]:
    """Checks every image in images_dir, splits it if applicable, and returns
    a mapping: original_image_filename -> [(split_image_path, title), ...]

    Skips images that look like they were already split (contain `_partN`)
    so re-runs over a shared folder don't double-process."""
    if not images_dir.exists():
        return {}

    mapping: dict[str, list[tuple[Path, str]]] = {}
    for img_file in sorted(images_dir.glob("*")):
        if img_file.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        if _is_already_split(img_file):
            continue
        splits = split_grid_image(img_file)
        if len(splits) > 1:
            mapping[img_file.name] = splits

    return mapping


# --------------------------------------------------------------------------
# STEP 3: Update the markdown file so each image line is preceded by the
#         image filename as a caption, and split images appear on their
#         own lines. Each image is now ALSO followed by its full OCR'd text.
# --------------------------------------------------------------------------
def _format_image_block(prefix: str, sp: Path, title: str, idx: int) -> list[str]:
    """Returns the markdown lines for one split part:
    - If a per-subplot title was OCR'd, emit it as a visible text line on its
      own so the reader sees the title above the image.
    - The filename line stays as a caption below the title (or above if no
      title was detected).
    - The image line keeps the title in the alt-text for accessibility.
    - NEW: below the image, the full OCR'd text content of that image part is
      inserted inside a fenced block, so all handwritten/printed text in the
      image is also present as real, copyable text.
    """
    name = sp.name
    label = title or f"Part {idx}"
    lines: list[str] = []
    if title:
        lines.append(f"**{title}**")
    lines.append(f"**{name}**")
    lines.append(f"![{label}]({prefix}{name})")

    extracted = extract_full_text_from_image(sp)
    if extracted:
        lines.append("")
        lines.append("_Extracted text:_")
        lines.append("```text")
        lines.append(extracted)
        lines.append("```")

    return lines


def update_markdown_with_splits(md_path: Path, split_mapping: dict[str, list[tuple[Path, str]]]) -> None:
    """For every image referenced in the markdown:
    - If it was split into parts, replace the single line with one block per
      part (each block = caption line + image line + extracted OCR text).
    - Otherwise, prepend a caption line (the image filename) above the line,
      and append the image's full OCR'd text below it.
    This ensures each image has its filename visible as text above it, the
    image itself stays free of in-image text artefacts, and the actual
    handwritten/printed content is captured as real markdown text.
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
                # Non-split image: prepend caption line with the filename,
                # keep the original image line, then append its full OCR text.
                new_lines.append(f"**{image_filename}**")
                new_lines.append(line)

                # Resolve the actual file on disk so we can OCR it. `inside`
                # is the path as written in the markdown (relative to the
                # markdown file's own directory).
                img_on_disk = (md_path.parent / inside).resolve() if inside else None
                extracted = ""
                if img_on_disk and img_on_disk.exists():
                    extracted = extract_full_text_from_image(img_on_disk)
                if extracted:
                    new_lines.append("")
                    new_lines.append("_Extracted text:_")
                    new_lines.append("```text")
                    new_lines.append(extracted)
                    new_lines.append("```")
                replaced = True
        if not replaced:
            new_lines.append(line)

    md_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"[markdown] {md_path.name} updated with image captions + extracted text")


def strip_code_blocks_near_images(md_path: Path) -> None:
    """Removes OCR'd ```code blocks``` that sit just before a caption line
    (e.g. ````...```` immediately followed by blank line and our inserted
    `**filename.png**` caption). Leaves real prose intact — only fenced code
    blocks are removed, never paragraph text. Does NOT touch the
    `_Extracted text:_` ```text``` blocks we add ourselves (those are always
    preceded by an image line, not a caption line, so they're never matched
    by the backward-scan below)."""
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find caption line indices: `**...png**` lines we just inserted.
    def is_caption(s: str) -> bool:
        st = s.strip()
        return st.startswith("**") and st.endswith("**") and ".png" in st

    # Find indices of image lines.
    def is_image(s: str) -> bool:
        return s.strip().startswith("![")

    removed = 0
    new_lines: list[str] = []
    n = len(lines)
    skip_until = -1  # set to index k after we delete a block, to skip pre-recorded lines

    i = 0
    while i < n:
        if i <= skip_until:
            i += 1
            continue

        new_lines.append(lines[i])

        # If this line is a caption, look at the lines just before it. If they
        # form a ``` fenced block ```, drop the whole block (opening fence
        # through closing fence).
        if is_caption(lines[i]):
            # Walk backward through blanks to find the line right before.
            j = len(new_lines) - 2  # new_lines already includes caption at -1
            while j >= 0 and new_lines[j].strip() == "":
                j -= 1
            if j >= 0 and new_lines[j].strip().startswith("```"):
                # That's a closing fence. Walk back to find the matching opening fence.
                closing = j
                k = j - 1
                while k >= 0:
                    if new_lines[k].strip().startswith("```"):
                        opening = k
                        break
                    k -= 1
                else:
                    opening = -1
                if opening >= 0:
                    # Drop everything from opening through closing inclusive
                    # (and any blanks between closing and caption).
                    del new_lines[opening:]
                    # Re-append the caption (which we already added).
                    new_lines.append(lines[i])
                    removed += 1

        i += 1

    if removed:
        md_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
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
        output_dir / COMBINED_IMAGES_DIR,
    ]
    seen = set()
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        if c.exists():
            return c
    return candidates[0]  # default guess, treated as empty if it doesn't exist


def consolidate_images_for_merge(md_files: list[Path]) -> tuple[Path, dict[Path, str]]:
    """Move every per-file `_artifacts/` folder into a single shared
    `output_md/all_images/` folder and rewrite the image paths inside each
    markdown file so the references still resolve.

    Docling gives every input file its own `<stem>_artifacts/` folder, and
    the image filenames inside each folder start at `image_000000` — so two
    input files would collide on the same image number. We rename images to
    `<source_stem>__<original_image_name>` when moving them, and rewrite the
    `!(...)(...)` paths inside each .md accordingly.

    Returns (shared_images_dir, source_md_to_combined_md_path_map).
    """
    import shutil

    output_dir = Path(OUTPUT_DIR)
    shared_dir = output_dir / COMBINED_IMAGES_DIR
    shared_dir.mkdir(parents=True, exist_ok=True)

    # Track which files we copied so split-image outputs (which are written
    # later into the same per-file _artifacts/ folder) end up here too.
    file_rewrite_map: dict[str, str] = {}  # original_md_text -> rewritten_md_text

    for md_path in md_files:
        stem = md_path.stem
        # Find this file's artifacts directory (whatever shape Docling made).
        images_dir = find_images_dir_for(md_path)
        if not images_dir.exists():
            continue

        md_text = md_path.read_text(encoding="utf-8")
        original_text = md_text

        # Both the per-file .md and the combined.md live inside OUTPUT_DIR,
        # so image references in them must be RELATIVE to OUTPUT_DIR (i.e.
        # `all_images/...`, not `output_md/all_images/...`). If the text
        # still contains `output_md/` prefixes from Docling's earlier
        # save_as_markdown call, strip them so paths resolve correctly.
        md_text = _strip_output_md_prefix(md_text)

        # Move every file in images_dir to shared_dir, prefixing with the
        # source file stem so two sources can't collide on the same name.
        for img in sorted(images_dir.iterdir()):
            if not img.is_file():
                continue
            if img.suffix.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                continue
            new_name = f"{stem}__{img.name}"
            dest = shared_dir / new_name
            if dest.exists():
                dest.unlink()
            shutil.move(str(img), str(dest))
            old_basename = img.name
            new_basename = new_name
            # Rewrite any remaining references (with whatever leftover
            # folder prefix Docling may have used) so they resolve to the
            # shared `all_images/` folder next to the .md files.
            md_text = md_text.replace(
                f"(output_md/{images_dir.name}/{old_basename})",
                f"({COMBINED_IMAGES_DIR}/{new_basename})",
            )
            md_text = md_text.replace(
                f"({images_dir.name}/{old_basename})",
                f"({COMBINED_IMAGES_DIR}/{new_basename})",
            )
            md_text = md_text.replace(
                f"(output_md/{COMBINED_IMAGES_DIR}/{old_basename})",
                f"({COMBINED_IMAGES_DIR}/{new_basename})",
            )
            # Also handle plain `(image_xxx.png)` references (no folder).
            md_text = md_text.replace(
                f"({old_basename})",
                f"({COMBINED_IMAGES_DIR}/{new_basename})",
            )

        # Clean up now-empty per-file _artifacts directory and the nested
        # output_md/ wrapper if everything got moved out.
        try:
            images_dir.rmdir()
        except OSError:
            pass
        parent = images_dir.parent
        # If we just emptied output_md/output_md/<stem>_artifacts and the
        # parent is now empty, drop the nested wrapper too.
        try:
            parent.rmdir()
        except OSError:
            pass

        if md_text != original_text:
            md_path.write_text(md_text, encoding="utf-8")

    return shared_dir, {}


def _strip_output_md_prefix(md_text: str) -> str:
    """Strip any leading `output_md/` from image-link paths so the rewritten
    markdown's image references resolve relative to OUTPUT_DIR (where the .md
    files actually sit). Only touches the path inside `![..](..)`."""
    import re as _re
    return _re.sub(
        r"(!\[[^\]]*\]\()output_md/([^)]+)(\))",
        lambda m: m.group(1) + m.group(2) + m.group(3),
        md_text,
    )


def merge_markdown_files(md_files: list[Path], output_path: Path) -> Path:
    """Concatenate all per-file markdown outputs into a single combined
    markdown file. Each source file is introduced with a clear `## Source`
    heading so the reader can see where one document ends and the next
    begins.

    Image paths in each per-file .md already point at `./all_images/...` by
    the time this runs (set by `consolidate_images_for_merge`), and the
    combined file sits in the same directory, so no path rewriting is needed.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    parts: list[str] = []
    parts.append(f"# Combined Document\n")
    parts.append(
        f"_Generated from {len(md_files)} source file(s) in `{INPUT_DIR}`._\n"
    )

    for idx, md_path in enumerate(md_files):
        if not md_path.exists():
            continue
        text = md_path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        parts.append("")
        parts.append(f"---\n")
        parts.append(f"## Source {idx + 1}: `{md_path.name}`\n")
        parts.append("")
        parts.append(text)
        parts.append("")

    output_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"[merge] {output_path.name} written ({len(md_files)} source(s))")
    return output_path


# --------------------------------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------------------------------
def main():
    input_dir = Path(INPUT_DIR)
    output_dir = Path(OUTPUT_DIR)

    # Fresh start: remove any prior markdown outputs and image folders so each
    # run begins clean.
    if output_dir.exists():
        for old_md in output_dir.glob("*.md"):
            old_md.unlink()
        for nested in (output_dir / "output_md",):
            if nested.exists():
                for child in nested.glob("*"):
                    if child.is_dir():
                        import shutil
                        shutil.rmtree(child)
                    else:
                        child.unlink()
        shared = output_dir / COMBINED_IMAGES_DIR
        if shared.exists():
            import shutil
            shutil.rmtree(shared)

    converter = build_converter()
    md_files = convert_documents(input_dir, output_dir, converter)

    # Move every per-file _artifacts/ into one shared folder and rewrite
    # image references in each .md to point at it. Doing this BEFORE splitting
    # means each source file contributes its own copy of the original image
    # to the shared pool, so all subsequent operations see the right files.
    consolidate_images_for_merge(md_files)

    for md_path in md_files:
        images_dir = find_images_dir_for(md_path)
        split_mapping = process_images_dir(images_dir)
        update_markdown_with_splits(md_path, split_mapping)
        strip_code_blocks_near_images(md_path)

    # Stitch every per-file .md into one combined.md.
    if md_files:
        combined_path = output_dir / COMBINED_MD_NAME
        merge_markdown_files(md_files, combined_path)

    print("\n✔ All done. Check the output_md/ folder.")


if __name__ == "__main__":
    main()