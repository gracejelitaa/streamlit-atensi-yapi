import streamlit as st


def show(artifacts):
    st.markdown(
        """
        <div class="hero-box">
            <h1>📖 Panduan</h1>
            <p>Panduan singkat menyiapkan data dan menjalankan proses clustering
            pada aplikasi ClusterInsight.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------
    # LANGKAH-LANGKAH
    # -----------------------------------------------------------------
    st.markdown('<div class="section-title"><h2>Langkah-Langkah</h2></div>', unsafe_allow_html=True)
    steps = [
        ("1️⃣ Download Template", "Buka menu **Upload Data**, klik tombol **Download Template CSV**."),
        ("2️⃣ Isi Data", "Isi template dengan data penerima sesuai ketentuan kolom "
                         "(lihat bagian *Ketentuan Kolom* pada menu Upload Data)."),
        ("3️⃣ Upload File", "Kembali ke menu **Upload Data**, unggah file CSV yang sudah diisi."),
        ("4️⃣ Jalankan Clustering", "Klik tombol **Jalankan Clustering**. Sistem otomatis menjalankan "
                                     "preprocessing, K-Means, dan K-Medoids."),
        ("5️⃣ Lihat Hasil", "Buka menu **Dashboard**, **K-Means**, **K-Medoids**, **Perbandingan**, "
                            "atau **Hasil Akhir** untuk melihat hasil clustering."),
    ]
    for title, desc in steps:
        st.markdown(f"**{title}** — {desc}")

    # -----------------------------------------------------------------
    # CATATAN PENTING
    # -----------------------------------------------------------------
    st.markdown('<div class="section-title"><h2>Catatan Penting</h2></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="conclusion-card">
        <ul style="margin-bottom:0;">
            <li>Pastikan nilai kolom kategorikal <b>persis sama</b> (termasuk huruf besar/kecil)
            dengan pilihan yang tersedia — nilai yang tidak dikenal akan menyebabkan proses gagal.</li>
            <li>Jika kolom nama/ID tidak diisi, sistem akan memberi label otomatis (Data 1, Data 2, dst).</li>
            <li>Jumlah cluster (k) serta model K-Means/K-Medoids sudah ditentukan sebelumnya oleh admin;
            Anda hanya perlu menyiapkan data yang ingin dikelompokkan.</li>
            <li>Jika belum mengunggah data sendiri, aplikasi ini otomatis menampilkan hasil dari
            dataset referensi yang sudah tersedia.</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
