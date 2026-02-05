from pathlib import Path
from typing import Tuple
import subprocess

from PIL import Image
import img2pdf
from pypdf import PdfReader
from pdf2docx import Converter


def image_to_pdf(input_file: Path, output_file: Path) -> None:
    with open(output_file, "wb") as f_out:
        f_out.write(img2pdf.convert(str(input_file)))


def pdf_to_image_first_page(input_file: Path, output_file: Path, fmt: str) -> None:
    """
    MVP: Extracts first embedded image from PDF.
    For true PDF rendering, upgrade later with pdf2image + poppler.
    """
    reader = PdfReader(str(input_file))
    if len(reader.pages) == 0:
        raise ValueError("PDF has no pages")

    page = reader.pages[0]
    images = page.images
    if not images:
        raise ValueError("PDF→image not supported for this PDF (no embedded images).")

    img = images[0]
    img_bytes = img.data

    from io import BytesIO
    im = Image.open(BytesIO(img_bytes)).convert("RGB")

    if fmt.lower() == "png":
        im.save(output_file, "PNG")
    else:
        im.save(output_file, "JPEG", quality=90)


def docx_to_pdf_libreoffice(input_file: Path, output_file: Path) -> None:
    """
    Reliable DOCX -> PDF using LibreOffice headless.
    """
    out_dir = output_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # On macOS, sometimes soffice is not in PATH. If so, you may need full path:
    # /Applications/LibreOffice.app/Contents/MacOS/soffice
    cmd = [
        "soffice",
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to", "pdf",
        "--outdir", str(out_dir),
        str(input_file),
    ]
    subprocess.run(cmd, check=True)

    generated = out_dir / f"{input_file.stem}.pdf"
    if not generated.exists():
        raise ValueError("DOCX → PDF failed: output not created by LibreOffice")

    generated.replace(output_file)


def pdf_to_docx_pdf2docx(input_file: Path, output_file: Path) -> None:
    """
    PDF -> DOCX using pdf2docx.
    Works best on text-based PDFs (not scanned images).
    """
    cv = Converter(str(input_file))
    try:
        cv.convert(str(output_file), start=0, end=None)
    finally:
        cv.close()


def convert_file(input_file: Path, target_format: str, out_file: Path) -> Tuple[str, str]:
    tf = target_format.lower()
    suffix = input_file.suffix.lower().lstrip(".")

    # ---- DOCX -> PDF ----
    if tf == "pdf" and suffix == "docx":
        docx_to_pdf_libreoffice(input_file, out_file)
        return out_file.name, "application/pdf"

    # ---- PDF -> DOCX ----
    if tf == "docx" and suffix == "pdf":
        pdf_to_docx_pdf2docx(input_file, out_file)
        return out_file.name, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    # ---- Image -> PDF (existing) ----
    if tf == "pdf":
        if suffix in ["png", "jpg", "jpeg"]:
            image_to_pdf(input_file, out_file)
            return out_file.name, "application/pdf"
        raise ValueError("Only PNG/JPG/DOCX → PDF supported right now.")

    # ---- PDF -> Image (existing MVP) ----
    if tf in ["png", "jpg"]:
        if suffix == "pdf":
            pdf_to_image_first_page(input_file, out_file, tf)
            return out_file.name, f"image/{'png' if tf=='png' else 'jpeg'}"
        raise ValueError("Only PDF → PNG/JPG supported right now.")

    raise ValueError(f"Unsupported target format: {target_format}")
