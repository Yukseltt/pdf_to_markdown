# PDF to Markdown

PDF dosyalarını Markdown (`.md`) veya düz metin (`.txt`) biçimine dönüştüren basit
bir masaüstü uygulaması.
/ A simple desktop app that converts PDF files into Markdown (`.md`) or plain
text (`.txt`).

## Neden? / Why?

Claude'a (ve diğer LLM'lere) doğrudan PDF yüklediğinizde her sayfa bir görüntü
olarak işlenir; çok sayfalı belgelerde bu hızla "maksimum görüntü sayısı" hatasına
yol açar. Bu araç PDF'i metne dönüştürerek bu sınırı ortadan kaldırır: çıktı yalnızca
metin olduğu için görüntü limiti devreye girmez ve metin token'ları daha verimlidir.
/ When you upload a PDF directly to Claude (or other LLMs), each page is processed
as an image, which quickly hits the "maximum images" error on long documents. This
tool converts the PDF to text, removing that limit: the output is text only, so the
image cap never applies and text tokens are more efficient.

## Özellikler / Features

- Grafik arayüz, dosya gezgininden PDF seçimi / GUI with file picker.
- İki dönüştürme motoru / two conversion engines:
  - Hızlı (pymupdf4llm): anında çalışır, model indirmez / fast, no model download.
  - Kaliteli (Marker): matematik/formülleri LaTeX'e çevirir, tabloları korur; ilk
    kullanımda ~1.3 GB model indirir / converts math to LaTeX, keeps tables,
    downloads ~1.3 GB of models on first use.
- Çıktı biçimi: Markdown veya düz metin / output as Markdown or plain text.
- Otomatik temizleme (slayt no, ölü görüntü bağlantısı, fazla boşluk) / optional
  cleanup of slide numbers, dead image links and extra blank lines.
- Düzenli klasörler: `input_pdfs/` ve `md_files/` / tidy input and output folders.
- Çapraz platform: macOS, Windows, Linux / cross-platform launchers.

## Klasör Yapısı / Project Structure

```
pdf_for_claude/
├── app.py                 # GUI uygulaması / GUI app
├── converter.py           # Çekirdek mantık / core logic (testable)
├── requirements.txt       # Bağımlılıklar / dependencies
├── input_pdfs/            # Giriş PDF'leri / input PDFs
├── md_files/              # Çıktılar / outputs
├── tests/                 # Testler / tests
│   ├── test_converter.py
│   └── test_integration.py
├── run_apple.command      # macOS başlatıcı / macOS launcher
├── run_windows.bat        # Windows başlatıcı / Windows launcher
└── run_linux.sh           # Linux başlatıcı / Linux launcher
```

## Gereksinimler / Requirements

- Python 3.10 veya üzeri (Kaliteli/Marker motoru için zorunlu). Hızlı motor 3.9 ile de
  çalışır. / Python 3.10+ (required for the Marker engine; fast engine works on 3.9).
- İlk çalıştırmada bağımlılıklar otomatik kurulur; internet bağlantısı gerekir.
  / Dependencies install automatically on first run; internet is required.

## Kurulum ve Çalıştırma / Setup and Run

Başlatıcılar ilk açılışta bir `.venv` sanal ortamı oluşturur ve `requirements.txt`
içindeki paketleri kurar. Sonraki açılışlar hızlıdır.
/ Launchers create a `.venv` and install packages on first launch; later runs are fast.

### macOS
`run_apple.command` dosyasına çift tıklayın. Gatekeeper uyarısı çıkarsa sağ tık → Aç.
/ Double-click `run_apple.command`. If Gatekeeper warns, right-click → Open.

### Windows
`run_windows.bat` dosyasına çift tıklayın. / Double-click `run_windows.bat`.

### Linux
```bash
./run_linux.sh
```

### Manuel kurulum / Manual setup
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Kullanım / Usage

1. PDF'leri `input_pdfs/` klasörüne koyun (zorunlu değil) / put PDFs in `input_pdfs/`
   (optional).
2. Uygulamayı başlatın / start the app.
3. "+ Dosya Seç" ile PDF ekleyin / add PDFs with "+ Dosya Seç".
4. Motoru seçin: günlük işler için Hızlı, matematik/tablo için Kaliteli / pick an
   engine: Fast for everyday docs, Quality for math/tables.
5. Çıktı biçimini ve temizleme seçeneğini ayarlayın / set output format and cleanup.
6. "Dönüştür"e tıklayın; çıktılar `md_files/` klasörüne kaydedilir / click convert;
   outputs go to `md_files/`.

## Motor Karşılaştırması / Engine Comparison

| Özellik / Feature        | Hızlı / Fast (pymupdf4llm) | Kaliteli / Quality (Marker) |
|--------------------------|----------------------------|-----------------------------|
| Hız / Speed              | Anında / Instant           | Dakikalar / Minutes per file |
| Kurulum / Install size   | Küçük / Small (~50 MB)     | Büyük / Large (~2 GB)       |
| Matematik / Math         | Sınırlı / Limited          | LaTeX                       |
| Tablolar / Tables        | Değişken / Variable        | Markdown tablo / tables     |
| Hızlandırma / Accel.     | —                          | Apple Silicon (MPS)         |
| Python                   | 3.9+                       | 3.10+                       |

Marker modelleri bir kez indirilir ve önbelleğe alınır; sonraki dönüştürmeler tekrar
indirmez. / Marker models are downloaded once and cached; later runs reuse them.

## Testler / Tests

Testler standart kütüphane `unittest` ile yazılmıştır, ek bağımlılık gerekmez.
/ Tests use the standard library `unittest`, no extra dependencies.

```bash
# Hızlı testler / fast tests (unit + fast-engine integration)
.venv/bin/python3 -m unittest discover -s tests -v

# Ağır Marker testi dahil / including the heavy Marker test
RUN_MARKER_TEST=1 .venv/bin/python3 -m unittest discover -s tests -v
```

- Birim testleri / unit tests (`test_converter.py`): temizleme, sadeleştirme, çıktı
  yolu mantığı / cleanup, stripping and output-path logic.
- Entegrasyon testleri / integration tests (`test_integration.py`): gerçek PDF üretip
  uçtan uca dönüştürür / generate a real PDF and convert end to end.

## Sorun Giderme / Troubleshooting

- "pymupdf4llm/marker bulunamadı" / not found → başlatıcıyı yeniden çalıştırın veya
  `pip install -r requirements.txt`.
- Marker ilk açılışta yavaş / slow on first run → ~1.3 GB model bir kez indirilir,
  ilerleme terminalde görünür / models download once, progress shows in terminal.
- "Python 3.10+ gerekir" / required → Python 3.10+ kurun; başlatıcılar uygun sürümü
  bulmaya çalışır / install Python 3.10+, launchers try to locate it.
- Matematikte nadir OCR kusurları / rare OCR glitches in math → Marker yapay zekâ
  tabanlıdır, kritik belgeleri gözden geçirin / Marker is AI-based, review critical docs.

## Lisans / License

Kişisel ve eğitim amaçlı kullanım. Bağımlılıkların (PyMuPDF, Marker, PyTorch vb.) kendi
lisansları geçerlidir. / For personal and educational use. Dependencies keep their own
licenses.
