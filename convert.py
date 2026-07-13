from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc import ImageRefMode

def convert_folder(input_dir, output_dir):
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pipeline_opts = PdfPipelineOptions()
    pipeline_opts.images_scale = 2.0
    pipeline_opts.generate_picture_images = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)
        }
    )

    for file in input_dir.glob("*"):
        if file.suffix.lower() in (".pdf", ".pptx", ".docx"):
            print(f"Processing {file.name}...")
            result = converter.convert(str(file))
            md_out = output_dir / f"{file.stem}.md"
            result.document.save_as_markdown(
                md_out,
                image_mode=ImageRefMode.REFERENCED
            )
            print(f"✔ {file.name} → {md_out.name}")

if __name__ == "__main__":
    convert_folder("input_docs", "output_md")