# LibroBot — Chatbot Perpustakaan Berbasis AI

Chatbot berbasis AI untuk membantu pengguna mencari buku, memfilter koleksi
berdasarkan kategori/genre, dan mendapatkan rekomendasi buku berdasarkan
kecocokan sinopsis dengan deskripsi keinginan pengguna dalam bahasa natural.

## Fitur

- **Pencarian**: cari buku berdasarkan judul atau nama penulis (fuzzy match).
- **Filter**: saring koleksi berdasarkan kategori, genre, dan tahun terbit.
- **Rekomendasi semantik**: jelaskan tema/perasaan yang diinginkan, sistem
  mencari buku dengan sinopsis paling relevan menggunakan TF-IDF + cosine
  similarity, lalu LLM (Claude) merangkum alasan kecocokannya.
- **Memory sesi**: genre yang pernah dijelajahi pengguna disimpan selama
  sesi berjalan (`st.session_state`), tanpa perlu login.

## Arsitektur

```
Pesan pengguna
      |
      v
Orchestrator (intent routing: LLM atau rule-based fallback)
      |
      +--> search.py    (judul / penulis)
      +--> filter.py    (kategori / genre / tahun)
      +--> recommend.py (TF-IDF similarity + penjelasan LLM)
      |
      v
data/books.json (sumber data)
      |
      v
Streamlit UI (app.py)
```

Catatan desain: rekomendasi memakai pendekatan mirip RAG — LLM hanya
diminta menjelaskan alasan kecocokan dari kandidat yang sudah ditemukan
via pencarian kemiripan teks, bukan "mengarang" rekomendasi dari memori
sendiri. Ini mencegah LLM merekomendasikan buku yang tidak ada di koleksi.

Baseline kemiripan teks saat ini memakai **TF-IDF** (scikit-learn) supaya
aplikasi tetap bisa dijalankan sepenuhnya offline/tanpa API key untuk
keperluan demo. Untuk kualitas semantik yang lebih tinggi, ini bisa
diganti dengan embedding neural (mis. sentence-transformers atau
OpenAI text-embedding-3-small) yang disimpan di vector store seperti
ChromaDB — titik penggantiannya ada di `chatbot/recommend.py`.

## Instalasi

```bash
# 1. Buat virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependency
pip install -r requirements.txt

# 3. Salin file environment variable lalu isi API key Anthropic
cp .env.example .env
# edit .env dan isi ANTHROPIC_API_KEY

# 4. Jalankan aplikasi
streamlit run app.py
```

Jika `ANTHROPIC_API_KEY` tidak diisi, aplikasi tetap berjalan dalam mode
fallback: intent routing berbasis kata kunci, dan hasil rekomendasi
ditampilkan tanpa penjelasan naratif dari LLM.

## Struktur Proyek

```
library-chatbot/
├── app.py                  # Antarmuka Streamlit
├── chatbot/
│   ├── config.py            # Konfigurasi & environment variable
│   ├── data.py               # Loader dataset buku
│   ├── search.py             # Pencarian judul/penulis
│   ├── filter.py              # Filter kategori/genre/tahun
│   ├── recommend.py            # Rekomendasi semantik (TF-IDF + LLM)
│   ├── orchestrator.py          # Intent routing
│   └── llm.py                    # Wrapper Anthropic API
├── data/
│   └── books.json            # Dataset contoh (20 buku)
├── requirements.txt
├── .env.example
└── README.md
```
