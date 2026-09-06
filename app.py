"""
Antarmuka Streamlit untuk chatbot perpustakaan.

Jalankan dengan:
    streamlit run app.py
"""

import streamlit as st

from chatbot.orchestrator import handle_message
from chatbot.filter import filter_books
from chatbot.data import get_all_categories, get_all_genres

st.set_page_config(page_title="LibroBot - Asisten Perpustakaan", page_icon="📚", layout="wide")


def render_book_card(book: dict):
    """Menampilkan satu buku sebagai kartu ringkas."""
    with st.container(border=True):
        cols = st.columns([3, 1])
        with cols[0]:
            st.markdown(f"**{book['title']}**")
            st.caption(f"{book['author']} · {book.get('published_year', '-')}")
            st.write(book.get("synopsis", ""))
            tags = ", ".join(book.get("category", []) + book.get("genre", []))
            st.caption(f"Kategori/Genre: {tags}")
        with cols[1]:
            status = book.get("availability_status", "-")
            if status == "Tersedia":
                st.success(status)
            else:
                st.warning(status)
            if "similarity_score" in book:
                st.caption(f"Kecocokan: {book['similarity_score']:.0%}")


# ---------- Sidebar: filter cepat + memory preferensi sesi ----------
st.sidebar.title("📚 LibroBot")
st.sidebar.write("Filter cepat koleksi buku")

if "preferred_genres" not in st.session_state:
    st.session_state.preferred_genres = []

selected_category = st.sidebar.selectbox(
    "Kategori", options=["(semua)"] + get_all_categories()
)
selected_genre = st.sidebar.selectbox(
    "Genre", options=["(semua)"] + get_all_genres()
)

if st.sidebar.button("Terapkan filter"):
    params = {}
    if selected_category != "(semua)":
        params["category"] = selected_category
    if selected_genre != "(semua)":
        params["genre"] = selected_genre
        if selected_genre not in st.session_state.preferred_genres:
            st.session_state.preferred_genres.append(selected_genre)

    results = filter_books(**params)
    st.session_state["sidebar_filter_results"] = results

if st.session_state.preferred_genres:
    st.sidebar.divider()
    st.sidebar.caption("Genre yang pernah kamu jelajahi sesi ini:")
    st.sidebar.write(", ".join(st.session_state.preferred_genres))

# ---------- Area utama ----------
st.title("Chatbot Perpustakaan")
st.caption(
    "Cari judul buku, filter berdasarkan kategori/genre, atau ceritakan "
    "tema yang kamu inginkan untuk mendapat rekomendasi."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Tampilkan hasil filter sidebar (jika ada) di atas riwayat chat
if st.session_state.get("sidebar_filter_results") is not None:
    st.subheader("Hasil filter")
    results = st.session_state["sidebar_filter_results"]
    if results:
        for book in results:
            render_book_card(book)
    else:
        st.info("Tidak ada buku yang cocok dengan filter ini.")
    st.divider()

# Riwayat percakapan
for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.write(entry["content"])
        for book in entry.get("books", []):
            render_book_card(book)

# Input pengguna
user_input = st.chat_input("Tulis pesanmu di sini...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Mencari di koleksi..."):
            result = handle_message(user_input)
        st.write(result["explanation"])
        for book in result["books"]:
            render_book_card(book)

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": result["explanation"],
            "books": result["books"],
        }
    )
