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
        self.geometry("580x600")
        self.minsize(500, 520)
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
                 text="PDF dosyalarını Claude'a yükleyebilmek için metne dönüştürür.",
                 fg="gray").pack(anchor="w", pady=(2, 14))

        # Alt kontroller önce paketlenir, alta sabitlenir /
        # pack bottom controls first so they anchor to the bottom
        bottom = tk.Frame(outer)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Separator(bottom).pack(fill=tk.X, pady=(10, 10))

        # Motor seçimi / engine selector
        eng_frame = tk.LabelFrame(bottom, text="Dönüştürme Motoru", padx=10, pady=8)
        eng_frame.pack(fill=tk.X, pady=(0, 10))

        self.engine = tk.StringVar(value="fast")
        tk.Radiobutton(
            eng_frame,
            text="Hızlı  (pymupdf4llm)  —  anında, basit metin",
            variable=self.engine, value="fast").pack(anchor="w")
        tk.Radiobutton(
            eng_frame,
            text="Kaliteli  (Marker)  —  matematik/formül + tablo, yavaş",
            variable=self.engine, value="quality").pack(anchor="w")

        # Format ve seçenekler / format and options
        row = tk.Frame(bottom)
        row.pack(fill=tk.X, pady=(0, 10))

        fmt_frame = tk.LabelFrame(row, text="Çıktı Formatı", padx=10, pady=6)
        fmt_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.fmt = tk.StringVar(value="md")
        tk.Radiobutton(fmt_frame, text="Markdown (.md)",
                       variable=self.fmt, value="md").pack(anchor="w")
        tk.Radiobutton(fmt_frame, text="Düz Metin (.txt)",
                       variable=self.fmt, value="txt").pack(anchor="w")

        opt_frame = tk.LabelFrame(row, text="Seçenekler", padx=10, pady=6)
        opt_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self.do_cleanup = tk.BooleanVar(value=True)
        tk.Checkbutton(opt_frame,
                       text="Slayt numaralarını ve fazla\nboşlukları temizle",
                       variable=self.do_cleanup, justify="left").pack(anchor="w")

        # İlerleme çubuğu / progress bar
        self.pb_var = tk.DoubleVar()
        ttk.Progressbar(bottom, variable=self.pb_var,
                        maximum=100).pack(fill=tk.X, pady=(0, 6))

        # Durum etiketi / status label
        self.status_var = tk.StringVar(
            value=f"Çıktılar '{os.path.basename(cv.OUTPUT_DIR)}' klasörüne kaydedilir.")
        tk.Label(bottom, textvariable=self.status_var, fg="gray",
                 wraplength=540, justify="left").pack(anchor="w", pady=(0, 10))

        # Dönüştür butonu / convert button
        self.btn_convert = tk.Button(
            bottom, text="Dönüştür",
            command=self._start,
            state=tk.DISABLED,
            font=("Helvetica", 13, "bold"),
            padx=24, pady=8,
        )
        self.btn_convert.pack(pady=(0, 4))

        # Üst kısım: dosya listesi / top section: file list
        top = tk.Frame(outer)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tk.Label(top, text="Seçilen Dosyalar",
                 font=("Helvetica", 11, "bold")).pack(anchor="w")

        list_frame = tk.Frame(top, bd=1, relief=tk.SUNKEN)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

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

        # Dosya işlem butonları / file action buttons
        btn_row = tk.Frame(top)
        btn_row.pack(fill=tk.X, pady=(6, 0))

        tk.Button(btn_row, text="+ Dosya Seç",
                  command=self._add).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_row, text="Kaldır",
                  command=self._remove).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_row, text="Temizle",
                  command=self._clear).pack(side=tk.LEFT)

        self.count_var = tk.StringVar()
        tk.Label(btn_row, textvariable=self.count_var,
                 fg="gray").pack(side=tk.RIGHT)

    # Dosya işlemleri / file operations
    def _add(self):
        files = filedialog.askopenfilenames(
            title="PDF Dosyaları Seç",
            initialdir=cv.INPUT_DIR if os.path.isdir(cv.INPUT_DIR) else None,
            filetypes=[("PDF Dosyaları", "*.pdf"), ("Tüm Dosyalar", "*.*")],
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
        self.count_var.set(f"{n} dosya" if n else "")
        self.btn_convert.config(state=tk.NORMAL if n else tk.DISABLED)
        self.pb_var.set(0)

    # Dönüştürme / conversion
    def _start(self):
        if not self.selected:
            return
        self.btn_convert.config(state=tk.DISABLED)
        self.pb_var.set(0)
        self.status_var.set("Hazırlanıyor...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        engine = self.engine.get()
        try:
            convert_one = cv.make_engine(
                engine, status_cb=lambda m: self.after(0, self.status_var.set, m))
        except ImportError as exc:
            self.after(0, self._fail,
                       f"Motor kütüphanesi bulunamadı: {exc}")
            return
        except Exception as exc:
            self.after(0, self._fail, f"Motor yüklenemedi: {exc}")
            return

        fmt   = self.fmt.get()
        clean = self.do_cleanup.get()
        total = len(self.selected)
        done: list[str]             = []
        errs: list[tuple[str, str]] = []

        for i, path in enumerate(self.selected):
            name = os.path.basename(path)
            self.after(0, self.status_var.set,
                       f"Dönüştürülüyor ({i+1}/{total}): {name}")
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
            self.status_var.set(f"✓ {len(done)} dosya başarıyla dönüştürüldü.")
        elif done:
            self.status_var.set(
                f"✓ {len(done)} dönüştürüldü  |  ✗ {len(errs)} hata")
        else:
            self.status_var.set("Dönüştürme başarısız.")

        if done:
            folder = os.path.basename(cv.OUTPUT_DIR)
            msg = f"{len(done)} dosya '{folder}' klasörüne kaydedildi."
            if errs:
                msg += "\n\nHata oluşan dosyalar:\n"
                msg += "\n".join(f"• {n}: {e}" for n, e in errs)
            if messagebox.askyesno("Tamamlandı",
                                   msg + "\n\nKlasörü açmak ister misiniz?"):
                cv.open_folder(cv.OUTPUT_DIR)
        else:
            messagebox.showerror(
                "Hata", "\n".join(f"• {n}: {e}" for n, e in errs))

    def _fail(self, msg: str):
        self.btn_convert.config(
            state=tk.NORMAL if self.selected else tk.DISABLED)
        self.status_var.set(f"✗ {msg}")
        messagebox.showerror("Hata", msg)


if __name__ == "__main__":
    App().mainloop()
