"""
Modul pencarian buku berdasarkan judul atau nama penulis.
Menggunakan fuzzy matching (difflib) supaya pencarian tetap toleran
terhadap salah ketik ringan atau pencarian sebagian kata.
"""

from difflib import SequenceMatcher
from typing import List, Dict, Any

from chatbot.data import load_books


def _similarity(a: str, b: str) -> float:
    """Menghitung skor kemiripan dua string, dalam rentang 0.0 - 1.0."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def search_books(query: str, limit: int = 10, min_score: float = 0.3) -> List[Dict[str, Any]]:
    """Mencari buku berdasarkan kemiripan judul atau nama penulis.

    Pencarian menggabungkan dua strategi:
    1. Substring match langsung (prioritas tertinggi, skor 1.0)
    2. Fuzzy match berbasis SequenceMatcher untuk menangani salah ketik
       atau kemiripan parsial.

    Args:
        query: kata kunci pencarian dari pengguna.
        limit: jumlah maksimum hasil yang dikembalikan.
        min_score: ambang batas skor kemiripan minimum agar dianggap relevan.

    Returns:
        List buku yang cocok, terurut dari yang paling relevan.
    """
    query = query.strip()
    if not query:
        return []

    books = load_books()
    scored = []

    for book in books:
        title = book.get("title", "")
        author = book.get("author", "")

        if query.lower() in title.lower() or query.lower() in author.lower():
            score = 1.0
        else:
            score = max(_similarity(query, title), _similarity(query, author))

        if score >= min_score:
            scored.append((score, book))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [book for _, book in scored[:limit]]
