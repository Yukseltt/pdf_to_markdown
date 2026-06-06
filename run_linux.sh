#!/bin/bash
# Linux başlatıcı, ./run_linux.sh ile çalıştırın / Linux launcher, run with ./run_linux.sh
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$DIR/.venv"

# Marker Python 3.10+ ister, uygun sürümü bul / Marker needs 3.10+, find a suitable one
find_python() {
    for py in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$py" >/dev/null 2>&1; then
            echo "$py"; return 0
        fi
    done
    echo "python3"   # son çare / last resort
}

# Venv yoksa oluştur ve bağımlılıkları kur / create venv and install deps if missing
if [ ! -d "$VENV" ]; then
    PY="$(find_python)"
    echo "Ortam oluşturuluyor ($PY)..."
    "$PY" -m venv "$VENV"
    "$VENV/bin/pip" install --quiet --upgrade pip
    echo "Kütüphaneler kuruluyor (Marker büyük bir indirme, ilk kurulum birkaç dakika sürebilir)..."
    "$VENV/bin/pip" install --quiet -r "$DIR/requirements.txt"
fi

# Uygulamayı başlat / launch the app
exec "$VENV/bin/python3" "$DIR/app.py"
