"""
Orchestrator: menerima pesan bebas dari pengguna, menentukan intent-nya,
lalu meneruskan ke modul yang sesuai (search / filter / recommend).

Ada dua mode klasifikasi intent:
1. Berbasis LLM (jika ANTHROPIC_API_KEY tersedia) — lebih fleksibel
   memahami bahasa natural.
2. Fallback berbasis kata kunci sederhana — supaya aplikasi tetap bisa
   didemokan tanpa API key.
"""

import re
from typing import Dict, Any

from chatbot.config import USE_LLM_INTENT_ROUTING
from chatbot import llm
from chatbot.search import search_books
from chatbot.filter import filter_books
from chatbot.recommend import recommend_with_explanation
from chatbot.data import get_all_categories, get_all_genres

FILTER_KEYWORDS = ["kategori", "genre", "filter", "tahun", "terbitan"]
SEARCH_KEYWORDS = ["judul", "penulis", "karya", "buku berjudul"]


def _rule_based_intent(message: str) -> str:
    """Klasifikasi intent sederhana berbasis kata kunci, dipakai sebagai
    fallback saat LLM tidak tersedia."""
    lower = message.lower()

    if any(k in lower for k in FILTER_KEYWORDS):
        return "filter"
    if any(k in lower for k in SEARCH_KEYWORDS):
        return "search"

    # Default: kalau pesan cukup panjang dan deskriptif, anggap user
    # sedang menjelaskan preferensi -> arahkan ke rekomendasi semantik.
    if len(message.split()) >= 6:
        return "recommend"

    return "search"


def _extract_filter_params(message: str) -> Dict[str, Any]:
    """Mencocokkan kategori/genre yang disebut user dengan daftar yang ada
    di dataset, secara case-insensitive dan sederhana (substring match)."""
    lower = message.lower()
    params: Dict[str, Any] = {}

    for category in get_all_categories():
        if category.lower() in lower:
            params["category"] = category
            break

    for genre in get_all_genres():
        if genre.lower() in lower:
            params["genre"] = genre
            break

    year_match = re.search(r"\b(19|20)\d{2}\b", message)
    if year_match:
        params["year_from"] = int(year_match.group())

    return params


def handle_message(message: str) -> Dict[str, Any]:
    """Titik masuk utama: proses satu pesan pengguna end-to-end.

    Returns:
        dict dengan minimal key "intent" dan "books" (list hasil),
        serta "explanation" (str) untuk ditampilkan di UI.
    """
    message = message.strip()
    if not message:
        return {"intent": "none", "books": [], "explanation": "Pesan kosong."}

    if USE_LLM_INTENT_ROUTING:
        intent = llm.classify_intent(message) or _rule_based_intent(message)
    else:
        intent = _rule_based_intent(message)

    if intent == "search":
        books = search_books(message)
        explanation = (
            f"Ditemukan {len(books)} buku yang cocok dengan pencarianmu."
            if books
            else "Tidak ditemukan buku yang cocok. Coba kata kunci lain."
        )
        return {"intent": intent, "books": books, "explanation": explanation}

    if intent == "filter":
        params = _extract_filter_params(message)
        books = filter_books(**params)
        explanation = (
            f"Ditemukan {len(books)} buku sesuai filter yang kamu maksud."
            if books
            else "Tidak ada buku yang cocok dengan filter tersebut."
        )
        return {"intent": intent, "books": books, "explanation": explanation}

    # intent == "recommend"
    result = recommend_with_explanation(message)
    return {
        "intent": "recommend",
        "books": result["books"],
        "explanation": result["explanation"],
    }
