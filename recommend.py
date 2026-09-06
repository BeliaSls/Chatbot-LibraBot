"""
Modul rekomendasi buku berbasis kecocokan sinopsis (pendekatan RAG ringan).

Catatan desain:
- Untuk representasi vektor sinopsis, modul ini memakai TF-IDF
  (scikit-learn) sebagai baseline yang bisa jalan sepenuhnya offline
  tanpa API key eksternal, sehingga aplikasi tetap bisa didemokan kapan
  saja. Ini juga memberi baseline yang adil untuk dibandingkan pada
  laporan evaluasi (mis. dibandingkan dengan embedding neural).
- Untuk kualitas semantik yang lebih tinggi (menangkap makna, bukan
  cuma kemiripan kata), baseline ini bisa diganti dengan embedding
  neural (mis. OpenAI text-embedding-3-small, atau model lokal
  sentence-transformers) yang disimpan di vector store seperti ChromaDB.
  Titik penggantian ada di fungsi `_build_vectorizer()` di bawah ini.
- Setelah kandidat buku ditemukan, LLM (Claude) dipakai HANYA untuk
  merangkum alasan kecocokan dalam bahasa natural — bukan untuk
  "mengarang" rekomendasi dari memori sendiri. Ini penting untuk
  mencegah halusinasi (LLM merekomendasikan buku yang tidak ada
  di koleksi).
"""

from typing import List, Dict, Any, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from chatbot.data import load_books
from chatbot.config import TOP_K_RECOMMENDATIONS, USE_LLM_INTENT_ROUTING
from chatbot import llm

_vectorizer: Optional[TfidfVectorizer] = None
_book_vectors = None
_indexed_books: Optional[List[Dict[str, Any]]] = None


def _build_vectorizer():
    """Membangun ulang TF-IDF index dari seluruh sinopsis buku.

    Dipanggil sekali (lazy) dan di-cache di memori. Jika data buku
    berubah saat runtime, panggil dengan force=True dari luar modul ini.
    """
    global _vectorizer, _book_vectors, _indexed_books

    _indexed_books = load_books()
    corpus = [book.get("synopsis", "") for book in _indexed_books]

    _vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words=None,  # dataset berbahasa Indonesia, stopword list bawaan sklearn untuk bahasa Inggris tidak relevan
        ngram_range=(1, 2),
    )
    _book_vectors = _vectorizer.fit_transform(corpus)


def find_similar_books(user_request: str, top_k: int = None) -> List[Dict[str, Any]]:
    """Mencari buku dengan sinopsis paling mirip dengan deskripsi keinginan user.

    Args:
        user_request: deskripsi bebas dari pengguna, mis. "buku yang bikin
            mikir soal identitas dan keluarga tapi nggak terlalu berat".
        top_k: jumlah hasil teratas yang dikembalikan.

    Returns:
        List buku, masing-masing ditambah field 'similarity_score' (0-1).
    """
    if _vectorizer is None:
        _build_vectorizer()

    top_k = top_k or TOP_K_RECOMMENDATIONS

    query_vector = _vectorizer.transform([user_request])
    scores = cosine_similarity(query_vector, _book_vectors)[0]

    ranked_indices = scores.argsort()[::-1][:top_k]

    results = []
    for idx in ranked_indices:
        if scores[idx] <= 0:
            continue
        book = dict(_indexed_books[idx])
        book["similarity_score"] = round(float(scores[idx]), 3)
        results.append(book)

    return results


def recommend_with_explanation(user_request: str, top_k: int = None) -> Dict[str, Any]:
    """Mencari buku mirip lalu (opsional) meminta LLM merangkum alasannya.

    Jika LLM tidak tersedia (API key kosong), fungsi tetap mengembalikan
    daftar buku hasil pencarian TF-IDF tanpa penjelasan naratif tambahan
    (mode fallback/offline).

    Returns:
        dict dengan key "books" (list hasil) dan "explanation" (str).
    """
    candidates = find_similar_books(user_request, top_k=top_k)

    if not candidates:
        return {
            "books": [],
            "explanation": (
                "Maaf, belum ada buku di koleksi yang cukup mirip dengan "
                "permintaanmu. Coba jelaskan dengan kata kunci lain."
            ),
        }

    if not USE_LLM_INTENT_ROUTING:
        return {
            "books": candidates,
            "explanation": (
                "Berikut buku dengan sinopsis paling relevan dengan "
                "permintaanmu (mode tanpa LLM, hanya berdasarkan kemiripan teks)."
            ),
        }

    candidate_text = "\n".join(
        f"- {b['title']} oleh {b['author']}: {b['synopsis']}" for b in candidates
    )
    system_prompt = (
        "Kamu adalah pustakawan AI yang ramah dan santai. Kamu HANYA boleh "
        "merekomendasikan buku dari daftar kandidat yang diberikan, jangan "
        "menyebut buku lain di luar daftar itu. Jelaskan singkat (2-3 kalimat "
        "per buku) mengapa tiap buku cocok dengan permintaan pengguna."
    )
    user_message = (
        f"Permintaan pengguna: \"{user_request}\"\n\n"
        f"Daftar kandidat buku:\n{candidate_text}\n\n"
        "Tuliskan rekomendasimu."
    )

    try:
        explanation = llm.ask_llm(system_prompt, user_message, max_tokens=600)
    except Exception:
        explanation = (
            "Berikut buku dengan sinopsis paling relevan dengan permintaanmu "
            "(penjelasan LLM gagal dimuat, menampilkan hasil kemiripan teks)."
        )

    return {"books": candidates, "explanation": explanation}
