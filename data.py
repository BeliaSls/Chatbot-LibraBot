"""
Modul untuk memuat dan menyediakan akses ke dataset buku.
Menggunakan cache sederhana di memori supaya file JSON tidak dibaca
berulang kali setiap ada request dari Streamlit.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from chatbot.config import BOOKS_JSON_PATH

_books_cache: Optional[List[Dict[str, Any]]] = None


def load_books(force_reload: bool = False) -> List[Dict[str, Any]]:
    """Memuat seluruh data buku dari file JSON.

    Args:
        force_reload: jika True, abaikan cache dan baca ulang dari disk.

    Returns:
        List of dict, tiap dict merepresentasikan satu buku.
    """
    global _books_cache
    if _books_cache is not None and not force_reload:
        return _books_cache

    path = Path(BOOKS_JSON_PATH)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset buku tidak ditemukan di '{path}'. "
            "Pastikan file data/books.json tersedia."
        )

    with open(path, "r", encoding="utf-8") as f:
        _books_cache = json.load(f)

    return _books_cache


def get_all_categories() -> List[str]:
    """Mengembalikan daftar unik semua kategori buku, terurut alfabetis."""
    books = load_books()
    categories = {c for book in books for c in book.get("category", [])}
    return sorted(categories)


def get_all_genres() -> List[str]:
    """Mengembalikan daftar unik semua genre buku, terurut alfabetis."""
    books = load_books()
    genres = {g for book in books for g in book.get("genre", [])}
    return sorted(genres)


def get_book_by_id(book_id: str) -> Optional[Dict[str, Any]]:
    """Mencari satu buku berdasarkan id-nya."""
    books = load_books()
    for book in books:
        if book["id"] == book_id:
            return book
    return None
