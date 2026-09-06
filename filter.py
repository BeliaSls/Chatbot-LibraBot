"""
Modul untuk memfilter buku berdasarkan kategori, genre, dan rentang tahun terbit.
Dipakai baik oleh sidebar filter cepat di Streamlit maupun oleh orchestrator
saat pengguna menuliskan permintaan filter dalam bahasa natural.
"""

from typing import List, Dict, Any, Optional

from chatbot.data import load_books


def filter_books(
    category: Optional[str] = None,
    genre: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    only_available: bool = False,
) -> List[Dict[str, Any]]:
    """Memfilter daftar buku berdasarkan kombinasi kriteria yang diberikan.

    Semua argumen bersifat opsional; kriteria yang bernilai None diabaikan
    (tidak dipakai sebagai filter).

    Args:
        category: nama kategori, mis. "Fiksi" atau "Non-Fiksi".
        genre: nama genre, mis. "Sejarah".
        year_from: tahun terbit minimum (inklusif).
        year_to: tahun terbit maksimum (inklusif).
        only_available: jika True, hanya tampilkan buku berstatus "Tersedia".

    Returns:
        List buku yang memenuhi semua kriteria yang diberikan.
    """
    books = load_books()
    result = []

    for book in books:
        if category and category not in book.get("category", []):
            continue
        if genre and genre not in book.get("genre", []):
            continue
        if year_from and book.get("published_year", 0) < year_from:
            continue
        if year_to and book.get("published_year", 0) > year_to:
            continue
        if only_available and book.get("availability_status") != "Tersedia":
            continue
        result.append(book)

    return result
