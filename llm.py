"""
Wrapper tipis di atas Anthropic API.
Dipisah jadi modul sendiri supaya:
1. Semua panggilan ke LLM terpusat di satu tempat (memudahkan ganti model
   atau menambahkan logging/rate-limit di masa depan).
2. Modul lain (orchestrator, recommend) tidak perlu tahu detail SDK.
"""

from typing import Optional

from chatbot.config import ANTHROPIC_API_KEY, LLM_MODEL

_client = None


def _get_client():
    """Membuat instance Anthropic client sekali saja (lazy singleton)."""
    global _client
    if _client is None:
        import anthropic  # import lokal agar modul ini tetap bisa di-import
        # walau library anthropic belum terpasang, selama fungsi ini
        # tidak dipanggil (mis. saat mode fallback tanpa API key).
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def ask_llm(system_prompt: str, user_message: str, max_tokens: int = 500) -> str:
    """Mengirim satu permintaan ke Claude dan mengembalikan teks jawabannya.

    Args:
        system_prompt: instruksi sistem yang membatasi peran & lingkup LLM.
        user_message: pesan/pertanyaan yang ingin dijawab.
        max_tokens: batas maksimum panjang jawaban.

    Returns:
        Teks jawaban dari LLM.
    """
    client = _get_client()
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def classify_intent(user_message: str) -> Optional[str]:
    """Meminta LLM mengklasifikasikan intent pengguna.

    Returns salah satu dari: "search", "filter", "recommend", atau None
    jika LLM gagal memberi jawaban yang valid.
    """
    system_prompt = (
        "Kamu adalah pengklasifikasi intent untuk chatbot perpustakaan. "
        "Balas HANYA dengan satu kata tanpa penjelasan tambahan: "
        "'search' jika pengguna mencari judul/penulis buku spesifik, "
        "'filter' jika pengguna ingin menyaring buku berdasarkan "
        "kategori/genre/tahun, atau "
        "'recommend' jika pengguna menjelaskan tema/keinginan/perasaan "
        "dan ingin direkomendasikan buku yang cocok."
    )
    try:
        result = ask_llm(system_prompt, user_message, max_tokens=10)
        result = result.strip().lower()
        if result in {"search", "filter", "recommend"}:
            return result
        return None
    except Exception:
        return None
