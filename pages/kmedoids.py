import streamlit as st
import pandas as pd
from utils import plot_distribution, plot_pca_scatter, get_id_series
from config import card_html, PALETTE

def show(artifacts):
    # =====================================================================
    # 1. HEADER HALAMAN
    # =====================================================================
    st.markdown('<div class="section-title"><h2>📊 Analitik Klasterisasi K-Medoids</h2></div>', unsafe_allow_html=True)

    if not st.session_state.clustering_done:
        st.info("Jalankan proses clustering terlebih dahulu pada menu **📂 Upload Dataset** untuk memunculkan visualisasi analitik.", icon="ℹ️")
        return

    cfg = artifacts["feature_config"]
    medoid_coords = artifacts["kmedoids_medoids"]
    labels = st.session_state.kmedoids_labels

    counts_kmed = pd.Series(labels).value_counts().sort_index()
    total_n = len(labels)

    # =====================================================================
    # 2. RINGKASAN METRIK — headline (silhouette) diberi bobot visual lebih,
    #    sejajar dengan halaman K-Means biar mudah dibandingkan
    # =====================================================================
    c1, c2, c3, c4 = st.columns([1.3, 1, 1, 1])
    with c1: st.markdown(card_html("Silhouette Score", f"{st.session_state.silhouette_kmedoids:.4f}", "K-Medoids Model Quality", "🏆"), unsafe_allow_html=True)
    with c2: st.markdown(card_html("Cluster 0", f"{counts_kmed.get(0, 0)}", f"{counts_kmed.get(0, 0)/total_n*100:.1f}% dari total", "🔵"), unsafe_allow_html=True)
    with c3: st.markdown(card_html("Cluster 1", f"{counts_kmed.get(1, 0)}", f"{counts_kmed.get(1, 0)/total_n*100:.1f}% dari total", "🟠"), unsafe_allow_html=True)
    with c4: st.markdown(card_html("Cluster 2", f"{counts_kmed.get(2, 0)}", f"{counts_kmed.get(2, 0)/total_n*100:.1f}% dari total", "🟢"), unsafe_allow_html=True)

    st.write("")

    # =====================================================================
    # 3. MEDOID & DISTRIBUSI — rasio 6:4, tabel medoid (9 kolom X1-X9)
    #    butuh ruang lebih lebar dibanding chart distribusi 3 bar
    # =====================================================================
    col_g1, col_g2 = st.columns([6, 4])

    with col_g1:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>Objek Representatif Medoid</h4>", unsafe_allow_html=True)
            st.markdown(
                f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Koordinat medoid dalam skala ternormalisasi [0, 1] (X1–X9) — objek data ASLI, "
                "bukan rata-rata hitung seperti centroid K-Means.</p>",
                unsafe_allow_html=True
            )

            df_medoids_akhir = pd.DataFrame(medoid_coords, columns=cfg["feature_order"]).round(4)
            df_medoids_akhir.index = [f"Final M{i}" for i in df_medoids_akhir.index]

            medoids_awal = artifacts.get("kmedoids_medoids_awal")
            if medoids_awal is not None:
                df_medoids_awal = pd.DataFrame(medoids_awal, columns=cfg["feature_order"]).round(4)
                df_medoids_awal.index = [f"Initial M{i}" for i in df_medoids_awal.index]

                tab_awal, tab_akhir = st.tabs(["Medoid Awal", "Medoid Akhir"])
                with tab_awal:
                    st.dataframe(df_medoids_awal, use_container_width=True)
                    st.caption("Medoid awal hasil pemilihan acak (random_state=42) sebelum iterasi PAM konvergen.")
                with tab_akhir:
                    st.dataframe(df_medoids_akhir, use_container_width=True)
                    st.caption("Medoid akhir — objek data aktual setelah iterasi PAM konvergen.")
            else:
                st.dataframe(df_medoids_akhir, use_container_width=True)
                st.caption(
                    "ℹ️ Medoid awal belum tersedia — re-export artifact dari Colab memakai versi terbaru "
                    "`colab_joblib_export_cell.py` untuk menampilkan tabel Medoid Awal."
                )

    with col_g2:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>Komposisi Anggota</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Sebaran jumlah penerima manfaat hasil partisi algoritma K-Medoids (PAM).</p>", unsafe_allow_html=True)
            st.plotly_chart(plot_distribution(labels, PALETTE["kmedoids"]), use_container_width=True, config={'displayModeBar': False})

    st.write("")

    # =====================================================================
    # 4. VISUALISASI PCA 2D (FULL WIDTH)
    # =====================================================================
    with st.container(border=True):
        st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>Pemetaan Ruang Dimensi (K-Medoids PCA 2D Scatterplot)</h4>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Reduksi dimensi data atribut X1 s/d X9 untuk memetakan jarak kedekatan antar objek "
            "data penerima manfaat terhadap titik perwakilan Medoids.</p>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            plot_pca_scatter(
                st.session_state.pca_coords,
                labels,
                st.session_state.pca_medoids_kmedoids,
                "Medoid Akhir (*)",
                "K-Medoids PCA 2D Scatter Space"
            ),
            use_container_width=True
        )

    st.write("")

    # =====================================================================
    # 5. FILTERING DATA INTERAKTIF BERDASARKAN CLUSTER
    # =====================================================================
    with st.container(border=True):
        st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>🔍 Eksplorasi Data Penerima Manfaat per Cluster</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Gunakan filter di bawah untuk meninjau secara spesifik baris data penerima manfaat sosial yang dialokasikan ke klaster tertentu oleh model K-Medoids.</p>", unsafe_allow_html=True)

        f1, f2 = st.columns([1, 1])
        with f1:
            pilihan_cluster = st.selectbox(
                "Pilih Kelompok Cluster yang Ingin Ditinjau:",
                options=["Semua Cluster", "Cluster 0", "Cluster 1", "Cluster 2"]
            )
        with f2:
            kata_kunci = st.text_input("🔎 Cari berdasarkan Nama Penerima (opsional):", placeholder="Ketik nama untuk memfilter tabel...")

        id_series = get_id_series(st.session_state.df_raw, cfg)

        df_eksplorasi = st.session_state.df_raw.copy()
        df_eksplorasi.insert(0, "Hasil_Cluster_KMedoids", labels)
        df_eksplorasi["Hasil_Cluster_KMedoids"] = df_eksplorasi["Hasil_Cluster_KMedoids"].map({0: "Cluster 0", 1: "Cluster 1", 2: "Cluster 2"})

        if pilihan_cluster != "Semua Cluster":
            df_filtered = df_eksplorasi[df_eksplorasi["Hasil_Cluster_KMedoids"] == pilihan_cluster]
        else:
            df_filtered = df_eksplorasi

        if kata_kunci:
            id_col = cfg.get("id_column")
            if id_col in df_filtered.columns:
                df_filtered = df_filtered[df_filtered[id_col].astype(str).str.contains(kata_kunci, case=False, na=False)]

        st.write(f"Menampilkan **{df_filtered.shape[0]} baris data** hasil filter:")

        cluster_colors = {"Cluster 0": "#DBEAFE", "Cluster 1": "#FFE4D6", "Cluster 2": "#DCFCE7"}
        def _highlight_cluster(row):
            color = cluster_colors.get(row["Hasil_Cluster_KMedoids"], "")
            return [f"background-color: {color}" if color else "" for _ in row]

        st.dataframe(df_filtered.style.apply(_highlight_cluster, axis=1), use_container_width=True)

        st.download_button(
            "⬇️ Unduh Data Terfilter (.CSV)",
            data=df_filtered.to_csv(index=False).encode("utf-8"),
            file_name="hasil_kmedoids_terfilter.csv",
            mime="text/csv",
        )