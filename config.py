"""
Konfigurasi terpusat untuk chatbot perpustakaan.
Semua nilai sensitif (API key) diambil dari environment variable,
JANGAN pernah di-hardcode di kode sumber.
"""

import os

# API key Anthropic dibaca dari environment variable ANTHROPIC_API_KEY.
# Set di terminal sebelum menjalankan aplikasi, contoh:
#   export ANTHROPIC_API_KEY="sk-ant-..."   (Mac/Linux)
#   setx ANTHROPIC_API_KEY "sk-ant-..."     (Windows)
# atau taruh di file .env dan load dengan python-dotenv (lihat app.py).
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Model LLM yang dipakai untuk klasifikasi intent & menyusun jawaban akhir.
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")

# Path dataset buku.
BOOKS_JSON_PATH = os.environ.get("BOOKS_JSON_PATH", "data/books.json")

# Jumlah kandidat teratas yang diambil pada pencarian rekomendasi semantik.
TOP_K_RECOMMENDATIONS = int(os.environ.get("TOP_K_RECOMMENDATIONS", "5"))

# Jika True, orchestrator akan memakai klasifikasi intent berbasis LLM.
# Jika False (atau API key kosong), fallback ke aturan kata kunci sederhana
# supaya aplikasi tetap bisa didemokan tanpa API key (mode offline/demo).
USE_LLM_INTENT_ROUTING = bool(ANTHROPIC_API_KEY)
