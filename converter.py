#!/usr/bin/env python3
"""PDF to Markdown — çekirdek dönüştürme mantığı / core conversion logic.

GUI'den bağımsızdır ve test edilebilir / GUI-independent and testable.

İki motor desteklenir / Two engines are supported:
  - "fast"    : pymupdf4llm  (anında, basit metin / instant, plain text)
  - "quality" : Marker       (matematik + tablo, yavaş / math + tables, slow)
"""
from __future__ import annotations

import os
import re
import sys
import subprocess

# Proje kök dizini ve varsayılan klasörler / project root and default folders
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR  = os.path.join(BASE_DIR, "input_pdfs")
OUTPUT_DIR = os.path.join(BASE_DIR, "md_files")


def strip_markdown(text: str) -> str:
    """Markdown işaretlerini kaldırır / strip markdown marks (for .txt output)."""
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",    r"\1", text)
    text = re.sub(r"`(.+?)`",       r"\1", text)
    return text


def cleanup(text: str) -> str:
    """Slayt no, ölü görüntü bağlantısı ve fazla boşlukları temizler /
    remove slide numbers, dead image links and extra blank lines."""
    # Marker'ın ürettiği görüntü referanslarını kaldır / remove Marker image refs
    # (ör. ![](_page_3_Picture.jpeg)); görüntüler kaydedilmez, amaç metindir /
    # images are not saved, output is text-only
    text = re.sub(r"(?m)^\s*!\[[^\]]*\]\([^)]*\)\s*$\n?", "", text)
    # Tek başına 1-3 haneli sayıları (slayt no) kaldır / drop standalone 1-3 digit numbers
    text = re.sub(r"(?m)^\s*\d{1,3}\s*$\n?", "", text)
    # Üçten fazla ardışık boş satırı ikiye indir / collapse 3+ blank lines to two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def output_path(pdf_path: str, output_dir: str, fmt: str = "md") -> str:
    """PDF yolundan çıktı yolu üretir / build output path (output_dir/<name>.<fmt>)."""
    name = os.path.splitext(os.path.basename(pdf_path))[0]
    return os.path.join(output_dir, f"{name}.{fmt}")


def make_fast_engine():
    """pymupdf4llm tabanlı hızlı motor / fast engine. path -> markdown text."""
    import pymupdf4llm
    return lambda path: pymupdf4llm.to_markdown(path, show_progress=False)


# Marker modelleri ağırdır, bir kez yüklenip önbelleğe alınır /
# Marker models are heavy; loaded once and cached at module level
_marker_models = None


def make_marker_engine(status_cb=None):
    """Marker tabanlı kaliteli motor / quality engine. path -> markdown text.

    status_cb verilirse model yüklenirken çağrılır / called while models load.
    """
    global _marker_models
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    if _marker_models is None:
        if status_cb:
            status_cb("Marker modelleri yükleniyor (ilk seferde indirilir)...")
        _marker_models = create_model_dict()

    pdf_converter = PdfConverter(artifact_dict=_marker_models)

    def convert(path):
        rendered = pdf_converter(path)
        text, _, _ = text_from_rendered(rendered)
        return text

    return convert


def make_engine(engine: str, status_cb=None):
    """'fast' veya 'quality' motorunu oluşturur / build the chosen engine."""
    if engine == "quality":
        return make_marker_engine(status_cb)
    return make_fast_engine()


def convert_file(pdf_path: str, convert_one, output_dir: str,
                 fmt: str = "md", do_cleanup: bool = True) -> str:
    """Tek PDF'i dönüştürüp yazar, çıktı yolunu döndürür /
    convert one PDF, write it, return the output path.

    convert_one: path -> markdown metni döndüren motor / engine callable.
    """
    text = convert_one(pdf_path)
    if do_cleanup:
        text = cleanup(text)
    if fmt == "txt":
        text = strip_markdown(text)

    os.makedirs(output_dir, exist_ok=True)
    out = output_path(pdf_path, output_dir, fmt)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    return out


def open_folder(path: str) -> None:
    """Klasörü işletim sisteminde açar / open the folder in the OS file manager."""
    folder = path if os.path.isdir(path) else os.path.dirname(path)
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", folder], check=False)
        elif os.name == "nt":
            os.startfile(folder)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", folder], check=False)
    except Exception:
        pass
