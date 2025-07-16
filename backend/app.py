from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

app = Flask(__name__)
CORS(app) # Mengaktifkan CORS agar frontend bisa berkomunikasi

# --- Konfigurasi ---
FAISS_INDEX_PATH = 'agri_faiss_index.bin'
TEXT_CHUNKS_PATH = 'agri_text_chunks.npy'
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
OLLAMA_MODEL = 'deepseek-coder:latest' # Model Ollama yang akan digunakan
# Jumlah chunks teratas yang akan diambil sebagai konteks
TOP_K_CHUNKS = 3 

# --- Inisialisasi Model dan Data ---
# Ini akan dijalankan sekali saat aplikasi Flask dimulai
embedding_model = None
faiss_index = None
text_chunks = None

def load_resources():
    global embedding_model, faiss_index, text_chunks
    try:
        print("Memuat model embedding untuk pencarian...")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Model embedding dimuat.")

        print(f"Memuat FAISS index dari {FAISS_INDEX_PATH}...")
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        print("FAISS index dimuat.")

        print(f"Memuat teks chunks dari {TEXT_CHUNKS_PATH}...")
        text_chunks = np.load(TEXT_CHUNKS_PATH, allow_pickle=True).tolist()
        print("Teks chunks dimuat.")

        print("\nSumber daya backend siap!")
    except Exception as e:
        print(f"Error saat memuat sumber daya: {e}")
        print("Pastikan Anda sudah menjalankan 'python process_data.py' terlebih dahulu.")
        # Hentikan aplikasi jika sumber daya penting tidak bisa dimuat
        # Atau atur variabel global agar service tidak tersedia
        embedding_model = None
        faiss_index = None
        text_chunks = None

# Panggil fungsi ini saat aplikasi Flask pertama kali dijalankan
with app.app_context():
    load_resources()

@app.route('/')
def home():
    return "Backend Agri-Aide Berjalan! Siap menerima pertanyaan."

@app.route('/chat', methods=['POST'])
def chat():
    if not embedding_model or not faiss_index or not text_chunks:
        return jsonify({"error": "Sistem pengetahuan belum siap. Mohon tunggu atau hubungi admin."}), 503

    data = request.get_json()
    user_question = data.get('question')

    if not user_question:
        return jsonify({"error": "Mohon sediakan pertanyaan."}), 400

    print(f"\nPertanyaan diterima: {user_question}")

    try:
        # 1. Ubah pertanyaan pengguna menjadi embedding
        query_embedding = embedding_model.encode([user_question])

        # 2. Cari chunks yang paling relevan di FAISS
        # D = jarak, I = indeks dari top_k chunks
        D, I = faiss_index.search(query_embedding, TOP_K_CHUNKS)

        # 3. Ambil teks asli dari chunks yang relevan
        relevant_docs = [text_chunks[idx] for idx in I[0]]
        # Gabungkan menjadi satu string konteks
        context = "\n\n".join(relevant_docs)

        print(f"Konteks yang ditemukan (top {TOP_K_CHUNKS}):\n---\n{context}\n---")

        # 4. Kirim ke Ollama (Deepseek Coder)
        # Pesan sistem untuk menginstruksikan perilaku AI
        system_prompt = (
            "Anda adalah seorang asisten penasihat pertanian yang ramah dan membantu. "
            "Tugas Anda adalah menjawab pertanyaan petani. "
            "**Jawablah hanya berdasarkan informasi yang SANGAT JELAS dan RELEVAN dari 'Dokumentasi Pertanian' yang disediakan.** "
            "Jangan menambahkan informasi dari luar konteks yang diberikan. "
            "Jika informasi yang diminta TIDAK ADA di dalam 'Dokumentasi Pertanian' yang Anda miliki, cukup katakan 'Maaf, saya belum memiliki informasi spesifik tentang hal itu.' atau 'Informasi ini tidak tersedia dalam basis pengetahuan saya.' "
            "Berikan jawaban yang jelas, ringkas, dan praktis untuk petani, hindari jargon yang tidak perlu."
        )

        # Gabungkan konteks dan pertanyaan untuk model
        full_prompt = f"Dokumentasi Pertanian:\n{context}\n\nPertanyaan: {user_question}\n\nJawaban:"

        # Panggil model Ollama
        response = ollama.chat(
            model=OLLAMA_MODEL, 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': full_prompt}
            ]
        )
        ai_response = response['message']['content']
        print(f"Jawaban AI:\n{ai_response}")

        return jsonify({"answer": ai_response})

    except Exception as e:
        print(f"Error saat memproses permintaan: {e}")
        return jsonify({"error": f"Terjadi kesalahan internal: {str(e)}"}), 500

if __name__ == '__main__':
    # Jalankan aplikasi Flask
    # host='0.0.0.0' agar bisa diakses dari frontend (jika berjalan di localhost)
    # port=5000 adalah port default Flask
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True untuk pengembangan