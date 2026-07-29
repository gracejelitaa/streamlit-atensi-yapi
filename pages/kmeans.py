import streamlit as st
import pandas as pd
from utils import plot_elbow, plot_distribution, plot_pca_scatter, get_id_series
from config import card_html, PALETTE

def show(artifacts):
    # =====================================================================
    # 1. HEADER HALAMAN
    # =====================================================================
    st.markdown('<div class="section-title"><h2>📊 Analitik Klasterisasi K-Means</h2></div>', unsafe_allow_html=True)

    if not st.session_state.clustering_done:
        st.info("Jalankan proses clustering terlebih dahulu pada menu **📂 Upload Dataset** untuk memunculkan visualisasi analitik.", icon="ℹ️")
        return

    # Ambil konfigurasi model
    cfg = artifacts["feature_config"]
    km_model = artifacts["kmeans_model"]
    labels = st.session_state.kmeans_labels

    # Hitung ringkasan cepat khusus K-Means
    counts_km = pd.Series(labels).value_counts().sort_index()
    total_n = len(labels)

    # =====================================================================
    # 2. RINGKASAN METRIK — headline (silhouette) diberi bobot visual lebih
    #    dibanding 3 kartu jumlah anggota, biar ada hierarki yang jelas
    # =====================================================================
    c1, c2, c3, c4 = st.columns([1.3, 1, 1, 1])
    with c1: st.markdown(card_html("Silhouette Score", f"{st.session_state.silhouette_kmeans:.4f}", "K-Means Model Quality", "🏆"), unsafe_allow_html=True)
    with c2: st.markdown(card_html("Cluster 0", f"{counts_km.get(0, 0)}", f"{counts_km.get(0, 0)/total_n*100:.1f}% dari total", "🔵"), unsafe_allow_html=True)
    with c3: st.markdown(card_html("Cluster 1", f"{counts_km.get(1, 0)}", f"{counts_km.get(1, 0)/total_n*100:.1f}% dari total", "🟠"), unsafe_allow_html=True)
    with c4: st.markdown(card_html("Cluster 2", f"{counts_km.get(2, 0)}", f"{counts_km.get(2, 0)/total_n*100:.1f}% dari total", "🟢"), unsafe_allow_html=True)

    st.write("")

    # =====================================================================
    # 3. ELBOW & DISTRIBUSI — rasio 6:4, elbow butuh ruang lebih buat
    #    baca titik k=1..10, distribusi cukup ringkas (cuma 3 bar)
    # =====================================================================
    col_g1, col_g2 = st.columns([6, 4])

    with col_g1:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>Penentuan Cluster Optimal</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Metode Elbow (Live Render) berdasarkan nilai WCSS (Within-Cluster Sum of Squares).</p>", unsafe_allow_html=True)
            st.plotly_chart(plot_elbow(artifacts["elbow_data"]["kmeans"], cfg["k"]), use_container_width=True, config={'displayModeBar': False})

    with col_g2:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>Komposisi Anggota</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Sebaran jumlah penerima manfaat hasil pembagian K-Means.</p>", unsafe_allow_html=True)
            st.plotly_chart(plot_distribution(labels, PALETTE["kmeans"]), use_container_width=True, config={'displayModeBar': False})

    st.write("")

    # =====================================================================
    # 4. VISUALISASI PCA 2D (FULL WIDTH)
    # =====================================================================
    with st.container(border=True):
        st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>Pemetaan Ruang Dimensi (PCA 2D Scatterplot)</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Reduksi dimensi data atribut X1 s/d X9 menggunakan Principal Component Analysis untuk melihat kedekatan antar objek data secara visual.</p>", unsafe_allow_html=True)
        st.plotly_chart(
            plot_pca_scatter(
                st.session_state.pca_coords,
                labels,
                st.session_state.pca_centroids_kmeans,
                "Centroid Akhir (*)",
                "K-Means PCA 2D Scatter Space"
            ),
            use_container_width=True
        )

    st.write("")

    # =====================================================================
    # 5. NILAI CENTROID AWAL & AKHIR (SKALA NORMALISASI)
    # =====================================================================
    with st.container(border=True):
        st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>Nilai Titik Pusat Klaster (Skala Normalisasi)</h4>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Koordinat centroid dalam skala ternormalisasi [0, 1] (X1–X9), persis seperti tabel "
            "\"Centroid Awal\" dan \"Centroid Akhir\" pada notebook Colab — bukan hasil transformasi balik ke nilai asli.</p>",
            unsafe_allow_html=True
        )

        centroids_akhir = km_model.cluster_centers_ if hasattr(km_model, "cluster_centers_") else km_model
        df_centroids_akhir = pd.DataFrame(centroids_akhir, columns=cfg["feature_order"]).round(4)
        df_centroids_akhir.index = [f"Final C{i}" for i in df_centroids_akhir.index]

        centroids_awal = artifacts.get("kmeans_centroids_awal")
        if centroids_awal is not None:
            df_centroids_awal = pd.DataFrame(centroids_awal, columns=cfg["feature_order"]).round(4)
            df_centroids_awal.index = [f"Initial C{i}" for i in df_centroids_awal.index]

            tab_awal, tab_akhir = st.tabs(["Centroid Awal", "Centroid Akhir"])
            with tab_awal:
                st.dataframe(df_centroids_awal, use_container_width=True)
                st.caption("Titik pusat awal hasil inisialisasi k-means++ (max_iter=1, n_init=1, random_state=42) sebelum iterasi konvergen.")
            with tab_akhir:
                st.dataframe(df_centroids_akhir, use_container_width=True)
                st.caption("Titik pusat akhir setelah model K-Means konvergen penuh.")
        else:
            st.dataframe(df_centroids_akhir, use_container_width=True)
            st.caption(
                "ℹ️ Centroid awal belum tersedia — re-export artifact dari Colab memakai versi terbaru "
                "`colab_joblib_export_cell.py` untuk menampilkan tabel Centroid Awal."
            )

    st.write("")

    # =====================================================================
    # 6. FILTERING DATA INTERAKTIF BERDASARKAN CLUSTER
    # =====================================================================
    with st.container(border=True):
        st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>🔍 Eksplorasi Data Penerima Manfaat per Cluster</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Gunakan filter di bawah untuk meninjau secara spesifik baris data penerima manfaat sosial yang dialokasikan ke klaster tertentu oleh model K-Means.</p>", unsafe_allow_html=True)

        f1, f2 = st.columns([1, 1])
        with f1:
            pilihan_cluster = st.selectbox(
                "Pilih Kelompok Cluster yang Ingin Ditinjau:",
                options=["Semua Cluster", "Cluster 0", "Cluster 1", "Cluster 2"]
            )
        with f2:
            kata_kunci = st.text_input("🔎 Cari berdasarkan Nama Penerima (opsional):", placeholder="Ketik nama untuk memfilter tabel...")

        df_eksplorasi = st.session_state.df_raw.copy()
        df_eksplorasi.insert(0, "Hasil_Cluster_KMeans", labels)
        df_eksplorasi["Hasil_Cluster_KMeans"] = df_eksplorasi["Hasil_Cluster_KMeans"].map({0: "Cluster 0", 1: "Cluster 1", 2: "Cluster 2"})

        if pilihan_cluster != "Semua Cluster":
            df_filtered = df_eksplorasi[df_eksplorasi["Hasil_Cluster_KMeans"] == pilihan_cluster]
        else:
            df_filtered = df_eksplorasi

        if kata_kunci:
            id_col = cfg.get("id_column")
            if id_col in df_filtered.columns:
                df_filtered = df_filtered[df_filtered[id_col].astype(str).str.contains(kata_kunci, case=False, na=False)]

        st.write(f"Menampilkan **{df_filtered.shape[0]} baris data** hasil filter:")

        cluster_colors = {"Cluster 0": "#DBEAFE", "Cluster 1": "#FFE4D6", "Cluster 2": "#DCFCE7"}
        def _highlight_cluster(row):
            color = cluster_colors.get(row["Hasil_Cluster_KMeans"], "")
            return [f"background-color: {color}" if color else "" for _ in row]

        st.dataframe(df_filtered.style.apply(_highlight_cluster, axis=1), use_container_width=True)

        st.download_button(
            "⬇️ Unduh Data Terfilter (.CSV)",
            data=df_filtered.to_csv(index=False).encode("utf-8"),
            file_name="hasil_kmeans_terfilter.csv",
            mime="text/csv",
        )