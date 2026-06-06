"""converter.py birim testleri / unit tests (saf fonksiyonlar / pure functions)."""
import os
import sys
import unittest

# Proje kökünü içe aktarma yoluna ekle / add project root to import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import converter as cv


class TestStripMarkdown(unittest.TestCase):
    def test_basliklar_kaldirilir(self):
        self.assertEqual(cv.strip_markdown("# Başlık"), "Başlık")
        self.assertEqual(cv.strip_markdown("### Alt başlık"), "Alt başlık")

    def test_kalin_ve_italik_kaldirilir(self):
        self.assertEqual(cv.strip_markdown("**kalın**"), "kalın")
        self.assertEqual(cv.strip_markdown("*italik*"), "italik")

    def test_kod_isaretleri_kaldirilir(self):
        self.assertEqual(cv.strip_markdown("`kod`"), "kod")

    def test_duz_metin_degismez(self):
        self.assertEqual(cv.strip_markdown("sade metin"), "sade metin")


class TestCleanup(unittest.TestCase):
    def test_slayt_numaralari_kaldirilir(self):
        metin = "İçerik\n3\nDevam"
        self.assertNotIn("\n3\n", cv.cleanup(metin))
        self.assertIn("İçerik", cv.cleanup(metin))
        self.assertIn("Devam", cv.cleanup(metin))

    def test_olu_goruntu_baglantilari_kaldirilir(self):
        metin = "Önce\n![](_page_3_Picture_2.jpeg)\nSonra"
        sonuc = cv.cleanup(metin)
        self.assertNotIn("![]", sonuc)
        self.assertNotIn(".jpeg", sonuc)
        self.assertIn("Önce", sonuc)
        self.assertIn("Sonra", sonuc)

    def test_fazla_bos_satirlar_indirgenir(self):
        metin = "A\n\n\n\n\nB"
        sonuc = cv.cleanup(metin)
        self.assertNotIn("\n\n\n", sonuc)

    def test_sonda_tek_yeni_satir(self):
        self.assertTrue(cv.cleanup("metin").endswith("\n"))
        self.assertFalse(cv.cleanup("metin").endswith("\n\n"))

    def test_metin_icindeki_uzun_sayi_korunur(self):
        # 4 haneli sayı slayt no sayılmaz, korunmalı / 4-digit number is kept
        metin = "Cevap\n2024\nbitti"
        self.assertIn("2024", cv.cleanup(metin))


class TestOutputPath(unittest.TestCase):
    def test_uzanti_md_olur(self):
        yol = cv.output_path("/x/y/rapor.pdf", "/cikti", "md")
        self.assertEqual(yol, os.path.join("/cikti", "rapor.md"))

    def test_uzanti_txt_olur(self):
        yol = cv.output_path("/x/y/rapor.pdf", "/cikti", "txt")
        self.assertEqual(yol, os.path.join("/cikti", "rapor.txt"))

    def test_sadece_dosya_adi_kullanilir(self):
        # Girdi değil çıktı klasörü kullanılmalı / output dir, not input dir
        yol = cv.output_path("/baska/yer/UHCY1.pdf", "/cikti", "md")
        self.assertTrue(yol.startswith(os.path.join("/cikti", "")))
        self.assertTrue(yol.endswith("UHCY1.md"))


class TestVarsayilanKlasorler(unittest.TestCase):
    def test_klasor_yollari_tanimli(self):
        self.assertTrue(cv.INPUT_DIR.endswith("input_pdfs"))
        self.assertTrue(cv.OUTPUT_DIR.endswith("md_files"))


if __name__ == "__main__":
    unittest.main()
