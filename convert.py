"""
PDF/PPTX/DOCX -> Markdown converter (Docling based)
----------------------------------------------------
- Converts every pdf/pptx/docx file in input_docs/ into a markdown file in output_md/
- Combined grid images (e.g. "3 subplots merged into one image") are automatically
  split into separate images, if there is a clear whitespace gap between subplots
- The markdown file is updated so each split image is referenced on its own line,
  IMAGE FIRST, then its name/caption directly below it (never above, never inside).
- NEW: Every image (split or not) is also run through full-page OCR (RapidOCR),
  and the extracted text is written into the markdown directly below the image,
  so handwritten / printed text inside images becomes real, searchable text —
  not just an embedded picture.
- NEW (border-tight crop): every saved image — split part OR single/unsplit —
  is now cropped tightly to its own real content border (all 4 sides), so no
  surrounding whitespace or nearby page text ever bleeds into the picture.
  Text is only ever attached to an image if it was detected *inside* that
  image's own tight border; text sitting outside the border is page text and
  is left as plain markdown text (never pulled into / never used to justify
  keeping it glued to the picture).
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

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
MIN_GAP_WIDTH = 12          # a gap narrower than this is ignored (avoids noise from text spacing)
MIN_SEGMENT_SIZE = 120      # segments smaller than this are discarded as noise
# An aspect-ratio sanity check: if any candidate segment is unreasonably
# narrow vs the full image, we reject the whole split (it's almost certainly
# a page with text columns, not a grid of subplots).
MIN_SEGMENT_RATIO = 0.18    # smallest segment must be >= this fraction of full width/height

# Full-image OCR tuning
OCR_MIN_CONFIDENCE = 0.0    # RapidOCR score threshold below which a line is dropped
                             # (set to e.g. 0.3 if you see too much garbage text)

# If the OCR-detected text covers at least this fraction of the image's total
# area, the image is treated as a "text image" (e.g. a photographed notebook
# page) rather than a diagram/chart. Text images are DROPPED from the
# markdown entirely — only their extracted text is kept, so no text ever
# lives solely inside a picture. Diagrams/charts (low text coverage) keep
# the image AND get their text (e.g. a title) appended below as real text.
TEXT_IMAGE_COVERAGE_THRESHOLD = 0.12

# --- Tight border-crop tuning ---------------------------------------------
# A pixel counts as "content" (not blank background) if it's darker than
# this level. Used to find the image's true bounding box on all 4 sides.
BORDER_DARK_LEVEL = WHITE_THRESHOLD - 60
# Extra pixels of pure white padding kept around the tight content bbox, so
# the crop doesn't shave lines/strokes sitting exactly on the edge.
BORDER_CROP_PAD = 4


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
    """Converts every supported file in input_dir and saves the per-file markdowns
    directly into `output_dir/`. The companion `<stem>_artifacts/` directory
    that Docling creates next to each .md is later moved into a single shared
    `all_images/` folder by `consolidate_images_for_merge`.

    The per-file .md files are then moved into a `.staging/` subfolder so the
    final `output_dir/` only ever contains `README.md` + `all_images/`.

    Returns the list of generated .md file paths (they live in output_dir/ at
    this point; the caller is expected to move them into .staging/ later).
    """
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
MAX_GAP_DARK_FRACTION = 0.02   # a column/row counts as a "gap" only if this
                                # small a fraction of its pixels are dark —
                                # far more robust than averaging brightness,
                                # since a single stray dark pixel (anti-
                                # aliasing, noise) can't drag a real gap below
                                # threshold the way it can drag a mean down.
DARK_PIXEL_LEVEL = WHITE_THRESHOLD - 60


def _find_gap_columns(gray: np.ndarray) -> np.ndarray:
    """Returns a boolean mask marking which columns are a real whitespace
    'gap', based on the FRACTION of dark pixels in each column rather than
    mean brightness (fraction-based is far less sensitive to a few stray
    dark pixels bleeding a mean below WHITE_THRESHOLD)."""
    dark = gray < DARK_PIXEL_LEVEL
    dark_fraction = dark.mean(axis=0)
    return dark_fraction <= MAX_GAP_DARK_FRACTION


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

    # Find the first run of MIN_RUN consecutive dense rows. Real image/plot
    # content (e.g. a dark chart background) stays dense for a LONG,
    # unbroken stretch. A few lines of bold/monospace header text (e.g.
    # print() output above a chart) can also hit a moderate density for a
    # short run, but rarely holds it for this many consecutive rows without
    # a clean blank-line gap — so a high MIN_RUN reliably skips past header
    # text instead of mistaking it for the real content block.
    DENSITY_THRESHOLD = 0.45
    MIN_RUN = 40
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
# NEW: tight border-bbox crop (all 4 sides), applied to EVERY saved image —
# split part or single/unsplit — as the final step before the file is
# written to disk. This guarantees the saved picture never carries blank
# margin or neighbouring page content past its own true content edge.
# --------------------------------------------------------------------------
def _tight_content_bbox(gray: np.ndarray) -> tuple[int, int, int, int]:
    """Returns (x0, y0, x1, y1): the tight bounding box of non-background
    (dark) pixels in `gray`, padded by BORDER_CROP_PAD and clamped to the
    image bounds. If no dark pixel is found, returns the full image bbox
    unchanged (nothing to crop)."""
    h, w = gray.shape
    dark = gray < BORDER_DARK_LEVEL
    if not dark.any():
        return 0, 0, w, h

    ys = np.where(dark.any(axis=1))[0]
    xs = np.where(dark.any(axis=0))[0]
    y0, y1 = int(ys[0]), int(ys[-1]) + 1
    x0, x1 = int(xs[0]), int(xs[-1]) + 1

    y0 = max(0, y0 - BORDER_CROP_PAD)
    x0 = max(0, x0 - BORDER_CROP_PAD)
    y1 = min(h, y1 + BORDER_CROP_PAD)
    x1 = min(w, x1 + BORDER_CROP_PAD)
    return x0, y0, x1, y1


def tight_crop_to_border(img: Image.Image) -> Image.Image:
    """Crops `img` tightly to its own real content border on all 4 sides.
    This is the final pass applied to every saved image (after any row/
    column trimming already done for split parts) so nothing outside the
    picture's own edge — blank canvas, a neighbouring subplot's sliver,
    page text sitting just outside the figure — ever survives into the
    saved file."""
    gray = np.array(img.convert("L"))
    x0, y0, x1, y1 = _tight_content_bbox(gray)
    if x1 <= x0 or y1 <= y0:
        return img
    if (x0, y0, x1, y1) == (0, 0, img.width, img.height):
        return img
    return img.crop((x0, y0, x1, y1))


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


def _polygon_area(pts) -> float:
    """Shoelace formula: area of a (possibly non-axis-aligned) quadrilateral
    given as a list of (x, y) points, in pixel units."""
    try:
        n = len(pts)
        if n < 3:
            return 0.0
        area = 0.0
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0
    except Exception:
        return 0.0


def ocr_image_full(image_path: Path) -> tuple[str, float]:
    """Runs OCR over the ENTIRE image (not just a title band) and returns
    (extracted_text, text_coverage_ratio).

    IMPORTANT: this is only ever called on an image file that has ALREADY
    been tight-cropped to its own content border (see `tight_crop_to_border`
    / `_tight_content_bbox`). Because of that, any text this finds is, by
    construction, text that sits *inside* the image's own border — never
    surrounding page text — so it is always safe to treat as "part of the
    image".

    - extracted_text: recognized text as multi-line plain text, ordered
      top-to-bottom by each detection's vertical position (reading order).
    - text_coverage_ratio: fraction (0.0-1.0) of the image's total area that
      is covered by detected text boxes. A photographed notebook page (mostly
      handwriting) has a HIGH ratio; a chart/diagram with just a small title
      has a LOW ratio. Used to decide whether to keep the image or drop it
      and keep only the text (see TEXT_IMAGE_COVERAGE_THRESHOLD).

    Returns ("", 0.0) if OCR is unavailable or finds no text.
    """
    engine = _get_ocr_engine()
    if engine is None:
        return "", 0.0

    try:
        img = Image.open(image_path).convert("RGB")
        img_w, img_h = img.size
        result = engine(img)
    except Exception as e:
        print(f"[ocr] failed on {image_path.name}: {e}")
        return "", 0.0

    boxes = getattr(result, "boxes", None)
    txts = getattr(result, "txts", None) or []
    scores = getattr(result, "scores", None) or []

    if not txts:
        return "", 0.0

    # Pair up (text, score, box) so we can sort into natural reading order
    # (top-to-bottom by the box's mean y-coordinate) even if the engine
    # returns detections out of order. Also sum up each kept box's area to
    # compute the overall text coverage ratio.
    items = []
    total_text_area = 0.0
    for i, t in enumerate(txts):
        t = (t or "").strip()
        if not t:
            continue
        score = scores[i] if i < len(scores) else 1.0
        if score is not None and score < OCR_MIN_CONFIDENCE:
            continue
        y = float(i)
        if boxes is not None and i < len(boxes):
            try:
                pts = boxes[i]
                y = float(sum(p[1] for p in pts) / len(pts))
                total_text_area += _polygon_area(pts)
            except Exception:
                pass
        items.append((y, t))

    items.sort(key=lambda x: x[0])
    lines = [t for _, t in items]
    text = "\n".join(lines).strip()

    img_area = max(1.0, float(img_w) * float(img_h))
    coverage = min(1.0, total_text_area / img_area)

    return text, coverage


def extract_full_text_from_image(image_path: Path) -> str:
    """Backwards-compatible wrapper: returns just the extracted text."""
    text, _ = ocr_image_full(image_path)
    return text


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

    Every returned image file — split or not — is tight-cropped to its own
    real content border on all 4 sides (see `tight_crop_to_border`) as the
    LAST step before saving, so no whitespace margin or neighbouring content
    survives into the saved picture. A brand-new file is always written (even
    for the "nothing to split" case) so callers can tell a border-cropped
    version was produced and update the markdown to point at it.
    """
    img = Image.open(image_path).convert("RGB")
    gray = np.array(img.convert("L"))

    # A full-width header/title strip above the subplots (e.g. print() output
    # or a suptitle) has SOME dark pixels in every column, which would make
    # every column's mean brightness dip below WHITE_THRESHOLD and hide any
    # real gaps between subplots. To avoid that, restrict column-gap
    # detection to the vertical band that actually contains the dense image
    # content (found the same way we later trim each cropped part), so
    # header text above the subplots never suppresses split detection.
    content_y0, content_y1 = _trim_content_rows(gray)
    if content_y1 > content_y0:
        content_band = gray[content_y0:content_y1, :]
    else:
        content_band = gray

    # Try horizontal (column) splits first — using only the content band.
    col_gap_mask = _find_gap_columns(content_band)
    col_segments = _segments_from_gap_mask(col_gap_mask)

    # Try vertical (row) splits as well — same fraction-based test as columns.
    row_dark = gray < DARK_PIXEL_LEVEL
    row_dark_fraction = row_dark.mean(axis=1)
    row_gap_mask = row_dark_fraction <= MAX_GAP_DARK_FRACTION
    row_segments = _segments_from_gap_mask(row_gap_mask)

    # Pick whichever gives more segments (more useful for grid images).
    if len(col_segments) >= len(row_segments) and len(col_segments) > 1:
        segments = col_segments
        horizontal = True
    elif len(row_segments) > 1:
        segments = row_segments
        horizontal = False
    else:
        # Nothing worth splitting into multiple parts. Even so, the returned
        # image must NEVER carry leading/trailing text baked into it (e.g. a
        # print()/suptitle header sitting above a single chart that itself
        # has no internal columns to split), and it must never carry blank
        # margin past its own real border either. Trim rows first (drops any
        # text band sitting above the picture), then tight-crop all 4 sides
        # to the picture's own true content border.
        y0, y1 = content_y0, content_y1
        if y1 > y0 and (y1 - y0) < gray.shape[0] - 4:
            base = img.crop((0, y0, img.width, y1))
        else:
            base = img
        cropped = tight_crop_to_border(base)
        out_path = image_path.with_name(f"{image_path.stem}_trimmed{image_path.suffix}")
        cropped.save(out_path)
        return [(out_path, "")]

    # Sanity check: if any candidate segment is unreasonably narrow, this
    # isn't a real grid — it's a page with text columns / rows. Compare each
    # segment against the CONTENT span (from the start of the first segment
    # to the end of the last one), not the raw full image dimension — a real
    # grid image often has wide blank margins on the sides (common with
    # matplotlib exports), and comparing against the full image would wrongly
    # reject a perfectly good 3-column grid just because of that margin.
    content_extent = segments[-1][1] - segments[0][0]
    for s, e in segments:
        seg_extent = e - s
        if seg_extent < content_extent * MIN_SEGMENT_RATIO:
            print(
                f"[split] {image_path.name}: rejected split "
                f"(candidate segment {seg_extent}px is < "
                f"{int(MIN_SEGMENT_RATIO * 100)}% of content span {content_extent}px — "
                f"likely text spacing, not a real grid gap)"
            )
            # Still tight-crop the rejected image to its own border before
            # handing it back, same as the "no split candidates" branch.
            cropped = tight_crop_to_border(img)
            out_path = image_path.with_name(f"{image_path.stem}_trimmed{image_path.suffix}")
            cropped.save(out_path)
            return [(out_path, "")]

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
    # text up front and emit it as a markdown line below each image instead.
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
        # and will be emitted as a markdown line below each image, so the
        # saved image file itself stays free of text artefacts.
        cropped_gray = np.array(cropped.convert("L"))
        y0, y1 = _trim_content_rows(cropped_gray)

        # Always strip ANY text band above the real image content (per-
        # subplot titles, suptitles, OCR bleed) completely — no text should
        # ever remain baked into the image pixels. The title text itself is
        # preserved separately (OCR'd before cropping, see segment_titles
        # above) and placed as real markdown text below the image instead.
        if y1 - y0 > 20:
            cropped = cropped.crop((0, y0, cropped.width, y1))

        # Tight-crop this part to its OWN real content border on all 4
        # sides (left/right too, not just top/bottom) — removes any sliver
        # of a neighbouring subplot or blank canvas that the column/row gap
        # split left behind at the edges.
        cropped = tight_crop_to_border(cropped)

        # Add a small white margin (pure padding, no text) for visual breathing
        # room — the title itself is never kept in the image anymore.
        cw, ch = cropped.size
        top_pad = max(8, int(ch * 0.05)) if ch else 8
        bottom_pad = max(8, int(ch * 0.05)) if ch else 8
        if cw > 0 and ch > 0:
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
    (e.g. contains `_part1`, `_part2`, or `_trimmed`). Used to avoid
    re-splitting when the per-file processing loop runs against an
    already-shared folder."""
    name = img_file.stem
    import re as _re
    return bool(_re.search(r"_part\d+$", name)) or name.endswith("_trimmed")


def process_images_dir(images_dir: Path) -> dict[str, list[tuple[Path, str]]]:
    """Checks every image in images_dir, tight-crops/splits it, and returns
    a mapping: original_image_filename -> [(processed_image_path, title), ...]

    Every image is now included in the mapping — even when it wasn't split
    into multiple parts — because `split_grid_image` always writes a fresh,
    border-tight-cropped file. This makes sure a single (unsplit) image that
    had blank margin or bled-in page text trimmed off it actually gets its
    markdown reference updated to the cleaned-up file instead of silently
    keeping the old, untrimmed one.

    Skips images that look like they were already processed (contain
    `_partN` / `_trimmed`) so re-runs over a shared folder don't
    double-process."""
    if not images_dir.exists():
        return {}

    mapping: dict[str, list[tuple[Path, str]]] = {}
    for img_file in sorted(images_dir.glob("*")):
        if img_file.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        if _is_already_split(img_file):
            continue
        splits = split_grid_image(img_file)
        mapping[img_file.name] = splits

    return mapping


# --------------------------------------------------------------------------
# STEP 3: Update the markdown file so each split image appears on its own
#         line, IMAGE FIRST, followed directly by its name/caption BELOW it
#         (never above, never inside the image itself).
# --------------------------------------------------------------------------
def _text_as_markdown_lines(extracted: str) -> list[str]:
    """Formats OCR'd text as plain, readable markdown lines (hard line breaks
    via a trailing double-space) instead of a code fence, since this is meant
    to be read as normal document text, not code."""
    out = []
    for line in extracted.splitlines():
        line = line.rstrip()
        if line:
            out.append(line + "  ")  # markdown hard line break
        else:
            out.append("")
    return out


def _format_image_block(prefix: str, sp: Path, title: str, idx: int, is_single: bool = False) -> list[str]:
    """Returns the markdown lines for one processed image (a split part, or
    the single tight-cropped version of an unsplit image).

    `sp` has ALREADY been tight-cropped to its own content border (done in
    `split_grid_image`), so any OCR text found on it is — by construction —
    text that lives inside that border, never neighbouring page text. Two
    outcomes:

    1. TEXT IMAGE (OCR text covers a large fraction of the image area, e.g.
       a photographed notebook page): the image is DROPPED entirely and only
       its extracted text is emitted, so the same text never lives solely
       inside a picture.
    2. DIAGRAM/CHART (low text coverage, e.g. a plot with a small title): the
       image is KEPT — image first, then its caption directly BELOW it, then
       any further OCR'd text (title, axis labels, etc.) below that. Nothing
       is ever placed above or inside the image.
    """
    name = sp.name
    label = title or (f"Part {idx}" if not is_single else name)
    extracted, coverage = ocr_image_full(sp)

    lines: list[str] = []

    if extracted and coverage >= TEXT_IMAGE_COVERAGE_THRESHOLD:
        # Text image: no picture, text only.
        if title:
            lines.append(f"**{title}**")
        lines.extend(_text_as_markdown_lines(extracted))
        return lines

    # Diagram/chart: image FIRST, then its caption/name BELOW it, then any
    # extra title/text found INSIDE its own border — nothing ever goes above
    # or inside the image, and nothing from outside the image's border is
    # ever pulled in.
    lines.append(f"![{label}]({prefix}{name})")
    lines.append(f"**{name}**")
    if title:
        lines.append(title)
    if extracted:
        lines.append("")
        lines.extend(_text_as_markdown_lines(extracted))

    return lines


def update_markdown_with_splits(md_path: Path, split_mapping: dict[str, list[tuple[Path, str]]]) -> None:
    """For every image referenced in the markdown, replace the single line
    with the block(s) produced from its border-tight-cropped, processed
    version(s):
    - If it was split into multiple parts, one block per part.
    - If it wasn't split, still swap in its single tight-cropped version
      (never the original, possibly untrimmed file) with its caption below.
    Any image filename NOT present in split_mapping (e.g. one that failed to
    process) falls back to the original OCR-on-original-file behaviour so
    nothing is silently dropped.
    This ensures each saved image is cropped to its own true border, its
    filename is visible as text right below it, and only text detected
    inside that border is ever surfaced as the image's extracted text.
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
                parts = split_mapping[image_filename]
                prefix = ""
                if "/" in inside:
                    prefix = inside.rsplit("/", 1)[0] + "/"
                is_single = len(parts) == 1
                for i, (sp, title) in enumerate(parts, start=1):
                    new_lines.extend(_format_image_block(prefix, sp, title, i, is_single=is_single))
                replaced = True
            elif image_filename:
                # Fallback path (image wasn't found in split_mapping, e.g.
                # processing failed): OCR the original file as before. This
                # is the ONLY place where an un-cropped file may still be
                # OCR'd, kept purely as a safety net.
                img_on_disk = (md_path.parent / inside).resolve() if inside else None
                extracted, coverage = ("", 0.0)
                if img_on_disk and img_on_disk.exists():
                    extracted, coverage = ocr_image_full(img_on_disk)

                if extracted and coverage >= TEXT_IMAGE_COVERAGE_THRESHOLD:
                    # Text image (e.g. photographed notebook page): drop the
                    # picture, keep only the extracted text.
                    new_lines.extend(_text_as_markdown_lines(extracted))
                else:
                    # Diagram/chart (or no text at all): keep the image line
                    # as-is, then caption it directly BELOW, then still
                    # surface any OCR'd text below that.
                    new_lines.append(line)
                    new_lines.append(f"**{image_filename}**")
                    if extracted:
                        new_lines.append("")
                        new_lines.extend(_text_as_markdown_lines(extracted))
                replaced = True
        if not replaced:
            new_lines.append(line)

    md_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"[markdown] {md_path.name} updated with image captions + extracted text")


def strip_code_blocks_near_images(md_path: Path) -> None:
    """Removes OCR'd ```code blocks``` that sit just before an IMAGE line
    (e.g. ````...```` immediately followed by blank line and our ![...]
    image reference). Leaves real prose intact — only fenced code blocks are
    removed, never paragraph text. Does NOT touch the `_Extracted text:_`
    ```text``` blocks we add ourselves (those always sit after an image +
    caption, never directly before an image line, so they're never matched
    by the backward-scan below).

    NOTE: captions now live BELOW each image, so the code-block cleanup has
    to anchor on the image line itself, not the caption line."""
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find image line indices: our own `![...](...)` references.
    def is_image(s: str) -> bool:
        return s.strip().startswith("![")

    removed = 0
    new_lines: list[str] = []
    n = len(lines)

    i = 0
    while i < n:
        new_lines.append(lines[i])

        # If this line is an image reference, look at the lines just before
        # it. If they form a ``` fenced block ```, drop the whole block
        # (opening fence through closing fence) so leftover code/print()
        # output never sits directly above the picture.
        if is_image(lines[i]):
            # Walk backward through blanks to find the line right before.
            j = len(new_lines) - 2  # new_lines already includes image at -1
            while j >= 0 and new_lines[j].strip() == "":
                j -= 1
            if j >= 0 and new_lines[j].strip().startswith("```"):
                # That's a closing fence. Walk back to find the matching opening fence.
                closing = j
                k = j - 1
                opening = -1
                while k >= 0:
                    if new_lines[k].strip().startswith("```"):
                        opening = k
                        break
                    k -= 1
                if opening >= 0:
                    # Drop everything from opening through closing inclusive
                    # (and any blanks between closing and the image line).
                    del new_lines[opening:]
                    # Re-append the image line (which we already added).
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

    As a last resort, walks under md_path.parent looking for any directory
    whose name matches the per-file artifact pattern — this catches the
    deeply-nested `output_md/.staging/output_md/.staging/<stem>_artifacts/`
    shape Docling produces when the markdown is saved inside a `.staging/`
    subdirectory.
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

    # Deep fallback: search recursively under md_path.parent for any directory
    # whose name begins with the stem and ends with `_artifacts` or `_images`.
    suffixes = ("_artifacts", "_images")
    if md_path.parent.exists():
        for child in md_path.parent.rglob("*"):
            if not child.is_dir():
                continue
            if child.name in seen:
                continue
            seen.add(child.name)
            if child.name.startswith(md_path.stem) and child.name.endswith(suffixes):
                return child

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
    print(f"[images] Shared image folder ready at {shared_dir}")

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
        staging = output_dir / ".staging"
        if staging.exists():
            import shutil
            shutil.rmtree(staging)

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

    # Once everything is processed, move the per-file .md files into a
    # hidden .staging/ subfolder so we can stitch them together without
    # cluttering the final output_md/.
    import shutil
    staging = output_dir / ".staging"
    staging.mkdir(parents=True, exist_ok=True)
    for md_path in md_files:
        shutil.move(str(md_path), str(staging / md_path.name))
    # Re-point md_files at their new locations.
    md_files = [staging / md_path.name for md_path in md_files]

    # Stitch every per-file .md into one combined.md, then expose that
    # combined document inside output_md/ as a single README.md so the
    # output folder only ever contains README.md + the shared image folder.
    if md_files:
        combined_path = output_dir / COMBINED_MD_NAME
        merge_markdown_files(md_files, combined_path)

        readme_path = output_dir / "README.md"
        readme_body = combined_path.read_text(encoding="utf-8")
        readme_path.write_text(readme_body, encoding="utf-8")
        print(f"[merge] {readme_path.name} written (embeds {combined_path.name})")

        # Now that the merge is done, the per-file .md files are no longer
        # needed in the final output. Delete the staging dir.
        shutil.rmtree(staging)

        # The combined.md file is also redundant once README.md holds its
        # contents — remove it so the output folder only has README.md
        # plus all_images/.
        if combined_path.exists():
            combined_path.unlink()

    print("\n✔ All done. Check the output_md/ folder.")


if __name__ == "__main__":
    main()