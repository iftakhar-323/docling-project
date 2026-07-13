# Docling Project

Convert every `.pdf` / `.pptx` / `.docx` file in `input_docs/` into a single
merged `output_md/combined.md` using [Docling](https://github.com/DS4SD/docling).

What it does:

- **Merges** every input file into one `output_md/combined.md` with `## Source N` headings so each document is clearly separated.
- **Combines all images** into a single shared `output_md/all_images/` folder, with filenames prefixed by the source stem to avoid collisions.
- **Splits grid-style images** (multiple subplots combined into one picture) into separate images with their subplot titles OCR'd and rendered as captions.
- **Runs OCR on every image** and inserts the recognized text into the markdown directly below the image, so handwritten / printed content inside screenshots and scanned pages is still searchable and copy-pasteable.

---

## How to run

You only need **one command** to (re)generate the entire output:

```bash
source venv/bin/activate && python convert.py
```

That's it. The script will:

1. Read every supported file from `input_docs/`
2. Convert each to its own per-file `.md` inside `output_md/`
3. Move every extracted image into `output_md/all_images/` (one shared folder)
4. Split any composite grid images into separate parts and OCR subplot titles
5. Run full-image OCR on every extracted image and insert the recognized text
   into the markdown directly below each image (in `_Extracted text:` blocks)
6. Stitch all per-file `.md` into `output_md/combined.md` with `## Source N`
   headings so each input file is clearly separated

### Watch progress live

The script prints a lot of Docling/OCR logs. To see only the pipeline
milestones, pipe through a filter:

```bash
source venv/bin/activate && python convert.py 2>&1 | grep -vE '^\[(INFO|WARNING)\]'
```

### Run in background and tail the log

For long runs you can fire it in the background and check on it later:

```bash
source venv/bin/activate
rm -rf output_md                  # optional: clean previous output
nohup python convert.py > /tmp/convert.log 2>&1 &
echo "PID: $!"

# check progress
tail -30 /tmp/convert.log
# or wait until it finishes
while pgrep -f 'python convert.py' > /dev/null; do sleep 10; done
echo "Done"
```

---

## Adding or changing inputs

**No code changes are required.** Just drop new files (or replace existing
ones) into the `input_docs/` folder, then re-run the single command above.

Supported file extensions (case-insensitive):

- `.pdf` — PDF documents
- `.pptx` — PowerPoint slides
- `.docx` — Word documents

Anything else in `input_docs/` is silently ignored.

### Filename notes

- Files are processed in **alphabetical order**, so the order in
  `combined.md` follows that.
- Very long filenames (>80 chars in the stem) are automatically truncated
  to keep them within Linux's 255-byte filename limit. Truncated names get
  an `x_` prefix so you can still spot them.

### Quick verification after a run

```bash
# 1. check the file exists and has all sources
ls output_md/combined.md
grep -E '^## Source' output_md/combined.md

# 2. confirm every image reference resolves to a real file
python3 - <<'PY'
import re
from pathlib import Path
text = Path('output_md/combined.md').read_text()
links = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text)
ok = sum(1 for p in links if Path('output_md', p).exists())
print(f"{ok}/{len(links)} images resolve")
PY
```

---

## Project layout

```
.
├── convert.py            # the whole pipeline (one file)
├── input_docs/           # PUT YOUR FILES HERE — gitignored
├── output_md/            # generated each run
│   ├── all_images/       # every extracted / split image (shared)
│   ├── <name>.md         # per-file markdown
│   └── combined.md       # ⭐ the merged output
├── venv/                 # Python virtual env (gitignored)
└── README.md             # this file
```

---

## Prerequisites

- **Python 3.10+** (tested on 3.12)
- **Linux / macOS / WSL** (uses POSIX paths; works on Windows too but
  filenames are mangled differently)

### One-time setup

```bash
# create venv
python3 -m venv venv
source venv/bin/activate

# install dependencies (Docling + image/OCR libs)
pip install docling pillow numpy rapidocr-onnxruntime
```

The first run downloads a few OCR model files (~30 MB total) into
`venv/lib/.../rapidocr/models/`. After that they're cached and re-used.

---

## What the script does (technical overview)

`convert.py` runs these stages in order, defined as separate functions:

| Stage | Function | What it does |
|-------|----------|--------------|
| 1 | `build_converter()` | Build a `DocumentConverter` with PDF image scale 2.0 and picture image generation enabled |
| 2 | `convert_documents()` | Run Docling on every supported file in `input_docs/`, save each as `<stem>.md` in `output_md/` |
| 3 | `_safe_stem()` | Trim long filenames so the per-file `_artifacts/` folder fits in Linux's 255-byte limit |
| 4 | `consolidate_images_for_merge()` | Move every per-file `_artifacts/` into `output_md/all_images/`, prefix names with `<source_stem>__` to avoid collisions, strip the `output_md/` prefix from image links |
| 5 | `process_images_dir()` | For every image in `all_images/`, call `split_grid_image()` if it looks like a multi-subplot composite. Skip files already containing `_partN` to avoid double-processing |
| 6 | `split_grid_image()` | Detect whitespace columns/rows, OCR subplot titles before cropping, then crop into segments with smart top-band trimming |
| 7 | `update_markdown_with_splits()` | Replace each image's single markdown line with the formatted block: `**title**`, `**filename**`, `![label](path)` — and for *every* image, append the full-image OCR text in a `_Extracted text:_` `\`\`\`text` block |
| 8 | `extract_full_text_from_image()` | Run RapidOCR over the entire image (not just a title band), sort boxes top-to-bottom, return all recognized text. Used for both split parts and whole images |
| 9 | `strip_code_blocks_near_images()` | Remove stray code blocks that sit immediately above image captions (common when source documents embed code+figure pairs) |
| 10 | `merge_markdown_files()` | Concatenate every per-file `.md` into `output_md/combined.md` with `## Source N: <name>` headings and `---` separators |

### Why every image gets its OCR text in the markdown

Docling emits an image as an `<img>` tag whenever it can't reliably read the
content as text — handwritten notes, scanned pages, screenshots, equations,
etc. To make those figures still useful inside `combined.md`, the pipeline
runs **RapidOCR over the whole image** and writes the recognized text into a
`_Extracted text:_` fenced block directly below the image. The image stays
embedded so the reader can see it, and the text version becomes searchable,
copy-pasteable, and indexable. For printed-text images this is essentially
perfect; for handwritten content you'll get a noisy but recognizable
transcription.

---

## Tuning knobs

These constants near the top of `convert.py` control the pipeline:

| Constant | Default | Effect |
|----------|---------|--------|
| `IMAGES_SCALE` (via pipeline) | 2.0 | Higher = sharper OCR but slower |
| `WHITE_THRESHOLD` | 235 | Pixel brightness above this counts as "whitespace gap" |
| `MIN_GAP_WIDTH` | 20 | Minimum gap width in pixels to count as a separator |
| `MIN_SEGMENT_SIZE` | 120 | Minimum segment size in pixels — smaller pieces are dropped |
| `MIN_SEGMENT_RATIO` | 0.18 | Sanity check: if any candidate segment is < 18 % of full width/height, the split is rejected (avoids splitting text columns inside a single diagram) |
| `OCR_MIN_CONFIDENCE` | 0.0 | RapidOCR confidence floor; raise to ~0.3 if the extracted text blocks contain too much garbage |

If splits aren't happening where you expect, lower `WHITE_THRESHOLD` to ~225
or lower `MIN_GAP_WIDTH` to ~10. If a single image gets wrongly cut into
thin strips, raise `MIN_SEGMENT_RATIO` to ~0.25.

---

## Troubleshooting

**`CUDA out of memory`**

Multiple parallel `python convert.py` processes will fight over GPU memory.
Kill stale ones first:

```bash
pkill -9 -f 'python convert.py'
```

**`OSError: [Errno 36] File name too long`**

The PDF filename exceeds Linux's 255-byte path limit. The script handles this
via `_safe_stem()` automatically — the truncated stem gets an `x_` prefix.

**Images still don't render in GitHub markdown preview**

Make sure `output_md/all_images/` is **not** in `.gitignore` and the images
are committed (`git ls-files output_md/all_images/ | wc -l` should be > 0).

**The script runs but `combined.md` is missing a source file**

Check that the file extension is `.pdf`, `.pptx`, or `.docx` (lowercase or
uppercase both work). Files with other extensions are silently skipped.

**The `_Extracted text:` block under an image is full of garbage**

Raise `OCR_MIN_CONFIDENCE` to `0.3` (or higher) at the top of `convert.py` so
low-confidence detections are dropped.

**A handwritten page still looks like gibberish even after OCR**

RapidOCR (PP-OCRv6) is trained on **printed** text. For handwritten content
you'll get a noisy but partially readable transcription — not a perfect one.
A dedicated handwriting model (e.g. `microsoft/trocr-base-handwritten`) would
do better but isn't bundled with Docling.

---

## License

Internal project — no license declared.