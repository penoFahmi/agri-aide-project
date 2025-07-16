# 🌿 Agri-Aide: Asisten Penasihat Pertanian Interaktif 🌿

Agri-Aide adalah aplikasi chatbot berbasis AI yang dirancang untuk membantu petani dalam mengidentifikasi masalah tanaman, mendapatkan saran pemupukan dan perawatan, serta informasi pertanian lainnya secara cepat dan interaktif. Proyek ini dibangun sebagai tugas Ujian Akhir Semester (UAS).

---

## ✨ Fitur Utama

* **Konsultasi Interaktif:** Petani dapat mengajukan pertanyaan dalam bahasa sehari-hari.
* **Identifikasi Masalah:** Membantu mengidentifikasi potensi hama atau penyakit berdasarkan gejala yang dijelaskan.
* **Saran Praktis:** Memberikan rekomendasi penanganan, pemupukan, dan praktik budidaya yang relevan.
* **Antarmuka Pengguna Modern:** UI yang responsif dan intuitif, didukung oleh Next.js dan Shadcn UI.
* **Ditenagai AI Lokal:** Menggunakan model Deepseek Coder melalui Ollama untuk pemrosesan bahasa alami.

---

## 🚀 Teknologi yang Digunakan

* **Backend:**
    * **Python 3.x**
    * **Flask:** Kerangka kerja web untuk API.
    * **Ollama:** Untuk menjalankan model AI secara lokal (Deepseek Coder:latest).
    * **Sentence-Transformers:** Untuk menghasilkan *embedding* teks.
    * **FAISS:** Untuk pencarian kemiripan vektor (vector database).
* **Frontend:**
    * **Node.js**
    * **Next.js:** Kerangka kerja React untuk membangun UI.
    * **Shadcn UI:** Komponen UI yang dapat disesuaikan, dibangun di atas Radix UI dan Tailwind CSS.

---

## ⚙️ Persiapan dan Instalasi

Ikuti langkah-langkah di bawah untuk menyiapkan dan menjalankan proyek secara lokal.

### Prasyarat

* **Python 3.x**
* **Node.js & npm/yarn** (disarankan versi LTS)
* **Ollama:** Unduh dan instal dari [https://ollama.com/download](https://ollama.com/download)

### 1. Klon Repositori

```bash
git clone https://github.com/penoFahmi/agri-aide-project.git
cd agri-aide-project
