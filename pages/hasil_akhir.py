import io
import pandas as pd
import streamlit as st
from utils import get_id_series
from config import card_html, PALETTE

def show(artifacts):
    # =====================================================================
    # 1. HEADER HALAMAN
    # =====================================================================
    st.markdown('<div class="section-title"><h2>Tabulasi Ekspor Hasil Akhir</h2></div>', unsafe_allow_html=True)

    if not st.session_state.clustering_done:
        st.error("⚠️ Dataset asli belum berhasil dimuat otomatis. Pastikan file `artifacts/reference_dataset.pkl` tersedia.", icon="🚫")
        return

    # Ambil konfigurasi model & data state asli
    cfg = artifacts["feature_config"]
    df_raw = st.session_state.df_raw
    id_series = get_id_series(df_raw, cfg)

    # Membangun dataframe komparasi final untuk pelaporan
    df_final = pd.DataFrame({
        "Identitas / Nama Penerima": id_series.values,
        "Alokasi Cluster K-Means": st.session_state.kmeans_labels,
        "Alokasi Cluster K-Medoids": st.session_state.kmedoids_labels,
    })

    # Mengubah format angka klaster menjadi label string agar informatif di laporan
    df_report = df_final.copy()
    df_report["Alokasi Cluster K-Means"] = df_report["Alokasi Cluster K-Means"].map({0: "Cluster 0", 1: "Cluster 1", 2: "Cluster 2"})
    df_report["Alokasi Cluster K-Medoids"] = df_report["Alokasi Cluster K-Medoids"].map({0: "Cluster 0", 1: "Cluster 1", 2: "Cluster 2"})

    # =====================================================================
    # 2. METRIC SUMMARY LAYER
    # =====================================================================
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(card_html("Total Baris Terekspor", f"{df_final.shape[0]} Baris", "Siap Unduh (.CSV)", icon="📊"), unsafe_allow_html=True)
    with c2:
        st.markdown(card_html("Metode Evaluasi", "Silhouette Coefficient", "K-Means vs K-Medoids", icon="📐"), unsafe_allow_html=True)
    st.write("")

    # =====================================================================
    # 3. TABEL DATA HASIL KLASTERISASI KEDUA METODE
    # =====================================================================
    st.markdown(
        f"""
        <div class="ci-card" style="margin-bottom: 0.5rem;">
            <h4 style="margin-top:0; color:{PALETTE['primary_dark']};">Tabel Matriks Perbandingan Hasil Alokasi Data</h4>
            <p style="font-size:0.85rem; color:{PALETTE['muted']};">
                Berikut adalah rekapitulasi data penerima bantuan sosial ATENSI YAPI beserta label klaster yang diberikan oleh masing-masing algoritma.
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    # Filter interaktif berdasarkan kesepakatan/ketidaksepakatan label
    filter_opsi = st.selectbox(
        "Tampilkan baris data:",
        options=["Semua Data", "Hanya yang Sepakat (K-Means = K-Medoids)", "Hanya yang Berbeda (K-Means ≠ K-Medoids)"],
    )
    if filter_opsi == "Hanya yang Sepakat (K-Means = K-Medoids)":
        df_report_view = df_report[df_final["Alokasi Cluster K-Means"] == df_final["Alokasi Cluster K-Medoids"]]
    elif filter_opsi == "Hanya yang Berbeda (K-Means ≠ K-Medoids)":
        df_report_view = df_report[df_final["Alokasi Cluster K-Means"] != df_final["Alokasi Cluster K-Medoids"]]
    else:
        df_report_view = df_report

    st.caption(f"Menampilkan {df_report_view.shape[0]} dari {df_report.shape[0]} baris total.")

    # Menampilkan tabel interaktif penuh di web Streamlit
    st.dataframe(df_report_view, use_container_width=True)

    st.write("")

    # =====================================================================
    # 4. DOWNLOAD DATASET BUTTON LAYER
    # =====================================================================
    st.markdown(
        f"""
        <div class="ci-card" style="margin-bottom: 0;">
            <h4 style="margin-top:0; color:{PALETTE['primary_dark']};">Unduh Berkas Hasil Penelitian</h4>
            <p style="font-size:0.85rem; color:{PALETTE['muted']}; margin-bottom: 1.2rem;">
                Ekspor tabel komparasi di atas ke dalam format berkas Comma-Separated Values (.CSV) untuk kebutuhan lampiran draf laporan skripsi atau analisis lanjutan.
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    # Menyiapkan bytes data eksport
    csv_bytes = df_report_view.to_csv(index=False).encode("utf-8")

    # Tombol download bawaan Streamlit yang secara otomatis mewarisi style CSS tombol utama kita
    st.download_button(
        label="Unduh Lembar Hasil Analisis (.CSV)",
        data=csv_bytes,
        file_name="hasil_komparasi_clustering_atensi_yapi.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.write("")
    st.write("")

    # =====================================================================
    # 5. MINI SYSTEM FOOTER
    # =====================================================================
    st.markdown(
        """
        <div style="text-align: center; padding-top: 1rem; border-top: 1px solid #E2E8F0;">
            <p style="margin: 0; font-size: 0.78rem; color: #94A3B8;">
                Modul Ekspor Data. Hasil pembagian bersifat mutlak berdasarkan parameter final model.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )