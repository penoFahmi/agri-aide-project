import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# --- Konfigurasi ---
# Direktori tempat kamu menyimpan file teks data pertanian
DATA_DIR = 'data_pertanian'
# Path untuk menyimpan index FAISS dan teks aslinya
FAISS_INDEX_PATH = 'agri_faiss_index.bin'
TEXT_CHUNKS_PATH = 'agri_text_chunks.npy'

# Model SentenceTransformer untuk membuat embeddings.
# 'all-MiniLM-L6-v2' adalah pilihan yang bagus untuk performa dan ukuran.
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# Ukuran chunk (jumlah karakter) dan overlap
# Ini untuk memecah teks panjang menjadi potongan-potongan yang bisa diproses AI.
CHUNK_SIZE = 700  # Misalnya, 700 karakter per chunk
CHUNK_OVERLAP = 150 # Misalnya, 150 karakter overlap antar chunk

def load_text_from_directory(directory):
    """Membaca semua file teks dari direktori tertentu."""
    all_text = []
    # Menggunakan os.walk untuk mencari file di subdirektori juga (jika ada)
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith((".txt", ".md")):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    all_text.append(f.read())
    return "\n".join(all_text)

def chunk_text(text, chunk_size, chunk_overlap):
    """Membagi teks menjadi potongan-potongan dengan overlap."""
    chunks = []
    if not text:
        return chunks

    # Menggunakan NLTK (jika diinstal) untuk pemecahan kalimat lebih cerdas
    # from nltk.tokenize import sent_tokenize
    # sentences = sent_tokenize(text)
    # current_chunk = ""
    # for sentence in sentences:
    #     if len(current_chunk) + len(sentence) <= chunk_size:
    #         current_chunk += (" " if current_chunk else "") + sentence
    #     else:
    #         chunks.append(current_chunk)
    #         current_chunk = sentence # Mulai chunk baru dengan kalimat ini
    # if current_chunk: # Tambahkan chunk terakhir
    #     chunks.append(current_chunk)

    # Untuk kesederhanaan awal, kita gunakan pemotongan karakter dasar
    # Ini kurang "pintar" tapi lebih mudah diimplementasikan tanpa dependensi tambahan
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text): # Jika sudah di akhir teks
            break
        start += chunk_size - chunk_overlap
        # Pastikan start tidak melewati akhir teks setelah overlap
        if start >= len(text):
            break
    return [chunk.strip() for chunk in chunks if chunk.strip()] # Hapus chunk kosong

def main():
    print(f"Memuat model embedding: {EMBEDDING_MODEL_NAME}...")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Model embedding dimuat.")
    except Exception as e:
        print(f"Error memuat model embedding: {e}")
        print("Pastikan Anda memiliki koneksi internet untuk mengunduh model pertama kali.")
        print("Atau modelnya sudah ada secara lokal.")
        return

    # Pastikan direktori data ada
    if not os.path.exists(DATA_DIR):
        print(f"Error: Direktori '{DATA_DIR}' tidak ditemukan.")
        print("Mohon buat folder ini dan letakkan file .txt atau .md data pertanian Anda di dalamnya.")
        return

    print(f"Memuat teks dari direktori: {DATA_DIR}...")
    full_text = load_text_from_directory(DATA_DIR)
    if not full_text:
        print("Tidak ada teks yang ditemukan. Pastikan ada file .txt atau .md di direktori data.")
        return

    print(f"Jumlah karakter teks yang dimuat: {len(full_text)}")

    print(f"Memecah teks menjadi chunks (ukuran: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP})...")
    chunks = chunk_text(full_text, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"Total {len(chunks)} chunks dibuat.")

    if not chunks:
        print("Tidak ada chunks yang valid untuk diproses. Periksa data input Anda.")
        return

    print("Membuat embeddings untuk setiap chunk...")
    # Mengkodekan chunks menjadi embedding
    embeddings = model.encode(chunks, show_progress_bar=True)
    print("Embeddings selesai dibuat.")

    print("Membuat FAISS index...")
    # Membuat index FAISS. `embeddings.shape[1]` adalah dimensi embedding.
    index = faiss.IndexFlatL2(embeddings.shape[1]) # IndexFlatL2 untuk L2 (Euclidean) distance
    index.add(embeddings) # Menambahkan embeddings ke index
    print("FAISS index selesai dibuat.")

    print(f"Menyimpan FAISS index ke '{FAISS_INDEX_PATH}'...")
    faiss.write_index(index, FAISS_INDEX_PATH)
    print("FAISS index berhasil disimpan.")

    print(f"Menyimpan teks chunks asli ke '{TEXT_CHUNKS_PATH}'...")
    np.save(TEXT_CHUNKS_PATH, np.array(chunks))
    print("Teks chunks berhasil disimpan.")

    print("\nProses pemrosesan data selesai! Data siap digunakan oleh aplikasi Flask Anda.")

if __name__ == "__main__":
    main()