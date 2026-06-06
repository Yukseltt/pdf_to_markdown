"""Entegrasyon testleri / integration tests: gerçek PDF üretip uçtan uca dönüştürür.

Hızlı motor (pymupdf4llm) kullanılır, model indirmez / fast engine, no downloads.
Marker testi ağır olduğu için atlanır / Marker test is skipped by default;
RUN_MARKER_TEST=1 ile etkinleştirin / enable with RUN_MARKER_TEST=1.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import converter as cv


def _ornek_pdf_olustur(yol: str, metin: str = "Merhaba Dunya PDF testi") -> None:
    """Tek sayfalık örnek PDF üretir / create a one-page sample PDF with fitz."""
    import fitz  # pymupdf
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), metin, fontsize=14)
    doc.save(yol)
    doc.close()


class TestHizliMotorEntegrasyon(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.pdf = os.path.join(self.tmp, "ornek.pdf")
        self.out_dir = os.path.join(self.tmp, "cikti")
        _ornek_pdf_olustur(self.pdf, "Entegrasyon testi metni")

    def test_md_uretilir_ve_metin_icerir(self):
        engine = cv.make_fast_engine()
        out = cv.convert_file(self.pdf, engine, self.out_dir,
                              fmt="md", do_cleanup=True)
        self.assertTrue(os.path.exists(out))
        self.assertTrue(out.endswith("ornek.md"))
        with open(out, encoding="utf-8") as f:
            icerik = f.read()
        self.assertIn("Entegrasyon", icerik)

    def test_txt_formati_markdown_isareti_icermez(self):
        # Markdown içeren sahte motor / fake engine returning markdown
        def sahte_engine(_path):
            return "# Baslik\n**kalin** metin"
        out = cv.convert_file(self.pdf, sahte_engine, self.out_dir,
                              fmt="txt", do_cleanup=False)
        self.assertTrue(out.endswith("ornek.txt"))
        with open(out, encoding="utf-8") as f:
            icerik = f.read()
        self.assertNotIn("#", icerik)
        self.assertNotIn("**", icerik)
        self.assertIn("Baslik", icerik)
        self.assertIn("kalin", icerik)

    def test_cikti_klasoru_otomatik_olusturulur(self):
        self.assertFalse(os.path.exists(self.out_dir))
        engine = cv.make_fast_engine()
        cv.convert_file(self.pdf, engine, self.out_dir, fmt="md")
        self.assertTrue(os.path.isdir(self.out_dir))


@unittest.skipUnless(os.environ.get("RUN_MARKER_TEST") == "1",
                     "Marker testi ağır; RUN_MARKER_TEST=1 ile etkinleştirin")
class TestKaliteliMotorEntegrasyon(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.pdf = os.path.join(self.tmp, "ornek.pdf")
        self.out_dir = os.path.join(self.tmp, "cikti")
        _ornek_pdf_olustur(self.pdf, "Marker motoru testi")

    def test_marker_md_uretir(self):
        engine = cv.make_marker_engine()
        out = cv.convert_file(self.pdf, engine, self.out_dir, fmt="md")
        self.assertTrue(os.path.exists(out))
        with open(out, encoding="utf-8") as f:
            self.assertTrue(len(f.read()) > 0)


if __name__ == "__main__":
    unittest.main()
