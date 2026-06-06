#!/usr/bin/env python3
"""PDF to Markdown — masaüstü dönüştürücü arayüzü / desktop converter GUI."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

import converter as cv


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF to Markdown")
        self.geometry("660x640")
        self.minsize(560, 560)
        self.resizable(True, True)
        self.selected: list[str] = []

        # Varsayılan giriş/çıkış klasörlerini hazırla / ensure default folders
        os.makedirs(cv.INPUT_DIR, exist_ok=True)
        os.makedirs(cv.OUTPUT_DIR, exist_ok=True)

        self._build()

    def _build(self):
        outer = tk.Frame(self, padx=18, pady=14)
        outer.pack(fill=tk.BOTH, expand=True)

        tk.Label(outer, text="PDF to Markdown",
                 font=("Helvetica", 16, "bold")).pack(anchor="w")
        tk.Label(outer,
                 text="PDF dosyalarını metne dönüştürür / Convert PDF files to text.",
                 fg="gray").pack(anchor="w", pady=(2, 14))

        # Alt kontroller önce paketlenir, alta sabitlenir /
        # pack bottom controls first so they anchor to the bottom
        bottom = tk.Frame(outer)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Separator(bottom).pack(fill=tk.X, pady=(10, 10))

        # Motor seçimi / engine selector
        eng_frame = tk.LabelFrame(bottom, text="Dönüştürme Motoru / Engine",
                                  padx=10, pady=8)
        eng_frame.pack(fill=tk.X, pady=(0, 10))

        self.engine = tk.StringVar(value="fast")
        tk.Radiobutton(
            eng_frame,
            text="Hızlı / Fast  (pymupdf4llm)  —  anında, basit metin / instant, plain text",
            variable=self.engine, value="fast").pack(anchor="w")
        tk.Radiobutton(
            eng_frame,
            text="Kaliteli / Quality  (Marker)  —  matematik + tablo, yavaş / math + tables, slow",
            variable=self.engine, value="quality").pack(anchor="w")

        # Format ve seçenekler / format and options
        row = tk.Frame(bottom)
        row.pack(fill=tk.X, pady=(0, 10))

        fmt_frame = tk.LabelFrame(row, text="Çıktı Formatı / Format", padx=10, pady=6)
        fmt_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.fmt = tk.StringVar(value="md")
        tk.Radiobutton(fmt_frame, text="Markdown (.md)",
                       variable=self.fmt, value="md").pack(anchor="w")
        tk.Radiobutton(fmt_frame, text="Düz Metin / Plain text (.txt)",
                       variable=self.fmt, value="txt").pack(anchor="w")

        opt_frame = tk.LabelFrame(row, text="Seçenekler / Options", padx=10, pady=6)
        opt_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self.do_cleanup = tk.BooleanVar(value=True)
        tk.Checkbutton(opt_frame,
                       text="Slayt no ve fazla boşlukları temizle\n"
                            "Clean slide numbers and extra spaces",
                       variable=self.do_cleanup, justify="left").pack(anchor="w")

        # İlerleme çubuğu / progress bar
        self.pb_var = tk.DoubleVar()
        ttk.Progressbar(bottom, variable=self.pb_var,
                        maximum=100).pack(fill=tk.X, pady=(0, 6))

        # Durum etiketi / status label
        folder = os.path.basename(cv.OUTPUT_DIR)
        self.status_var = tk.StringVar(
            value=f"Çıktılar '{folder}' klasörüne kaydedilir / "
                  f"Outputs are saved to '{folder}'.")
        tk.Label(bottom, textvariable=self.status_var, fg="gray",
                 wraplength=620, justify="left").pack(anchor="w", pady=(0, 10))

        # Dönüştür butonu / convert button
        self.btn_convert = tk.Button(
            bottom, text="Dönüştür / Convert",
            command=self._start,
            state=tk.DISABLED,
            font=("Helvetica", 13, "bold"),
            padx=24, pady=8,
        )
        self.btn_convert.pack(pady=(0, 4))

        # Üst kısım: dosya listesi / top section: file list
        top = tk.Frame(outer)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tk.Label(top, text="Seçilen Dosyalar / Selected Files",
                 font=("Helvetica", 11, "bold")).pack(side=tk.TOP, anchor="w")

        # Dosya işlem butonları / file action buttons
        # Liste kutusundan önce alta sabitlenir, böylece her zaman görünür /
        # packed at the bottom before the listbox so it stays visible
        btn_row = tk.Frame(top)
        btn_row.pack(side=tk.BOTTOM, fill=tk.X, pady=(6, 0))

        tk.Button(btn_row, text="+ Dosya Seç / Add",
                  command=self._add).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_row, text="Kaldır / Remove",
                  command=self._remove).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_row, text="Temizle / Clear",
                  command=self._clear).pack(side=tk.LEFT)

        self.count_var = tk.StringVar()
        tk.Label(btn_row, textvariable=self.count_var,
                 fg="gray").pack(side=tk.RIGHT)

        # Liste kutusu kalan alanı doldurur / listbox fills the remaining space
        list_frame = tk.Frame(top, bd=1, relief=tk.SUNKEN)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(4, 0))

        sb = tk.Scrollbar(list_frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=sb.set,
            selectmode=tk.EXTENDED,
            activestyle="none",
            font=("Menlo", 11),
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.listbox.yview)

    # Dosya işlemleri / file operations
    def _add(self):
        files = filedialog.askopenfilenames(
            title="PDF Dosyaları Seç / Select PDF Files",
            initialdir=cv.INPUT_DIR if os.path.isdir(cv.INPUT_DIR) else None,
            filetypes=[("PDF", "*.pdf"), ("Tümü / All", "*.*")],
        )
        for f in files:
            if f not in self.selected:
                self.selected.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))
        self._refresh()

    def _remove(self):
        for i in sorted(self.listbox.curselection(), reverse=True):
            self.listbox.delete(i)
            del self.selected[i]
        self._refresh()

    def _clear(self):
        self.selected.clear()
        self.listbox.delete(0, tk.END)
        self._refresh()

    def _refresh(self):
        n = len(self.selected)
        self.count_var.set(f"{n} dosya / files" if n else "")
        self.btn_convert.config(state=tk.NORMAL if n else tk.DISABLED)
        self.pb_var.set(0)

    # Dönüştürme / conversion
    def _start(self):
        if not self.selected:
            return
        self.btn_convert.config(state=tk.DISABLED)
        self.pb_var.set(0)
        self.status_var.set("Hazırlanıyor / Preparing...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        engine = self.engine.get()
        try:
            convert_one = cv.make_engine(
                engine, status_cb=lambda m: self.after(0, self.status_var.set, m))
        except ImportError as exc:
            self.after(0, self._fail,
                       f"Motor kütüphanesi bulunamadı / engine library not found: {exc}")
            return
        except Exception as exc:
            self.after(0, self._fail, f"Motor yüklenemedi / engine load failed: {exc}")
            return

        fmt   = self.fmt.get()
        clean = self.do_cleanup.get()
        total = len(self.selected)
        done: list[str]             = []
        errs: list[tuple[str, str]] = []

        for i, path in enumerate(self.selected):
            name = os.path.basename(path)
            self.after(0, self.status_var.set,
                       f"Dönüştürülüyor / Converting ({i+1}/{total}): {name}")
            try:
                out = cv.convert_file(path, convert_one, cv.OUTPUT_DIR,
                                      fmt=fmt, do_cleanup=clean)
                done.append(out)
            except Exception as exc:
                errs.append((name, str(exc)))

            self.after(0, self.pb_var.set, (i + 1) / total * 100)

        self.after(0, self._done, done, errs)

    def _done(self, done: list[str], errs: list[tuple[str, str]]):
        self.btn_convert.config(
            state=tk.NORMAL if self.selected else tk.DISABLED)

        if done and not errs:
            self.status_var.set(
                f"{len(done)} dosya dönüştürüldü / files converted.")
        elif done:
            self.status_var.set(
                f"{len(done)} dönüştürüldü / done  |  {len(errs)} hata / errors")
        else:
            self.status_var.set("Dönüştürme başarısız / Conversion failed.")

        if done:
            folder = os.path.basename(cv.OUTPUT_DIR)
            msg = (f"{len(done)} dosya '{folder}' klasörüne kaydedildi.\n"
                   f"{len(done)} files saved to '{folder}'.")
            if errs:
                msg += "\n\nHatalar / Errors:\n"
                msg += "\n".join(f"- {n}: {e}" for n, e in errs)
            if messagebox.askyesno(
                    "Tamamlandı / Done",
                    msg + "\n\nKlasörü açmak ister misiniz? / Open the folder?"):
                cv.open_folder(cv.OUTPUT_DIR)
        else:
            messagebox.showerror(
                "Hata / Error", "\n".join(f"- {n}: {e}" for n, e in errs))

    def _fail(self, msg: str):
        self.btn_convert.config(
            state=tk.NORMAL if self.selected else tk.DISABLED)
        self.status_var.set(msg)
        messagebox.showerror("Hata / Error", msg)


if __name__ == "__main__":
    App().mainloop()
