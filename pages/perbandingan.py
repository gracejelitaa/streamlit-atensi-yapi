import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from config import card_html, PALETTE
from utils import plot_pca_scatter

def show(artifacts):
    # =====================================================================
    # 1. HEADER HALAMAN
    # =====================================================================
    st.markdown('<div class="section-title"><h2>⚖️ Komparasi Evaluasi K-Means vs K-Medoids</h2></div>', unsafe_allow_html=True)

    if not st.session_state.clustering_done:
        st.info("Jalankan proses clustering terlebih dahulu pada menu **📂 Upload Dataset** untuk mengaktifkan komparasi model.", icon="ℹ️")
        return

    cfg = artifacts["feature_config"]
    sil_km = st.session_state.silhouette_kmeans
    sil_kmed = st.session_state.silhouette_kmedoids
    diff = abs(sil_km - sil_kmed)
    best_method = "K-Means" if sil_km >= sil_kmed else "K-Medoids"

    km_counts = pd.Series(st.session_state.kmeans_labels).value_counts().sort_index()
    kmed_counts = pd.Series(st.session_state.kmedoids_labels).value_counts().sort_index()

    # =====================================================================
    # 2. KPI ROW — kartu rekomendasi diberi bobot sedikit lebih besar
    #    karena itu kesimpulan utama halaman ini
    # =====================================================================
    col1, col2, col3 = st.columns([1, 1, 1.15])
    with col1:
        st.markdown(card_html("K-Means Quality", f"{sil_km:.4f}", "Silhouette Coefficient", "📊"), unsafe_allow_html=True)
    with col2:
        st.markdown(card_html("K-Medoids Quality", f"{sil_kmed:.4f}", "Silhouette Coefficient", "📊"), unsafe_allow_html=True)
    with col3:
        st.markdown(card_html("Algoritma Rekomendasi", best_method, f"Selisih Skor: {diff:.4f}", "🏆"), unsafe_allow_html=True)

    st.write("")

    # =====================================================================
    # 3. GRAFIK KOMPARASI METRIK — dua chart sejenis (bar), rasio seimbang
    # =====================================================================
    ch1, ch2 = st.columns([5, 5])

    with ch1:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>🏆 Komparasi Kedekatan Struktur (Silhouette Score)</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Nilai koefisien kedekatan objek data dalam klaster. Semakin mendekati 1.000, struktur klaster semakin ideal.</p>", unsafe_allow_html=True)
            fig_sil = go.Figure(data=[go.Bar(
                x=["K-Means", "K-Medoids"],
                y=[sil_km, sil_kmed],
                marker_color=[PALETTE["kmeans"], PALETTE["kmedoids"]],
                text=[f"{sil_km:.4f}", f"{sil_kmed:.4f}"],
                textposition="outside",
                textfont=dict(family="JetBrains Mono, monospace", size=11, color="#0F172A"),
                width=0.4
            )])
            fig_sil.update_layout(
                font=dict(family="Plus Jakarta Sans, sans-serif"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickfont=dict(color=PALETTE["text"])),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(sil_km, sil_kmed) * 1.25], tickfont=dict(family="JetBrains Mono, monospace", color=PALETTE["muted"])),
                margin=dict(t=15, b=10, l=10, r=10),
                height=250
            )
            st.plotly_chart(fig_sil, use_container_width=True, config={'displayModeBar': False})

    with ch2:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>📦 Komposisi Keseimbangan Partisi Anggota</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Perbandingan jumlah data aktual penerima bantuan sosial Atensi Yapi pada setiap nomor indeks klaster.</p>", unsafe_allow_html=True)
            all_clusters = sorted(set(km_counts.index) | set(kmed_counts.index))
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Bar(x=[f"Cluster {c}" for c in all_clusters], y=[km_counts.get(c, 0) for c in all_clusters], name="K-Means", marker_color=PALETTE["kmeans"], width=0.22))
            fig_dist.add_trace(go.Bar(x=[f"Cluster {c}" for c in all_clusters], y=[kmed_counts.get(c, 0) for c in all_clusters], name="K-Medoids", marker_color=PALETTE["kmedoids"], width=0.22))
            fig_dist.update_layout(
                barmode="group",
                font=dict(family="Plus Jakarta Sans, sans-serif"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickfont=dict(color=PALETTE["text"])),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(family="JetBrains Mono, monospace", color=PALETTE["muted"])),
                margin=dict(t=15, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(size=10)),
                height=250
            )
            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})

    st.write("")

    # =====================================================================
    # 4. GRAFIK SEBARAN GEOMETRIS SIDE-BY-SIDE (PCA) — dua scatter kembar,
    #    rasio 1:1 memang paling wajar di sini
    # =====================================================================
    col_pca1, col_pca2 = st.columns([1, 1])
    with col_pca1:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>🌐 K-Means — Ruang PCA</h4>", unsafe_allow_html=True)
            st.plotly_chart(
                plot_pca_scatter(
                    st.session_state.pca_coords,
                    st.session_state.kmeans_labels,
                    st.session_state.pca_centroids_kmeans,
                    "Centroid (*)",
                    "K-Means PCA Space Diagram"
                ),
                use_container_width=True
            )
    with col_pca2:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>🌐 K-Medoids — Ruang PCA</h4>", unsafe_allow_html=True)
            st.plotly_chart(
                plot_pca_scatter(
                    st.session_state.pca_coords,
                    st.session_state.kmedoids_labels,
                    st.session_state.pca_medoids_kmedoids,
                    "Medoid (*)",
                    "K-Medoids PCA Space Diagram"
                ),
                use_container_width=True
            )

    st.write("")

    # =====================================================================
    # 4b. HEATMAP SILANG KESELARASAN LABEL — dipusatkan (bukan full-bleed)
    #     karena isinya cuma matriks 3x3, biar nggak kelihatan kosong melar
    # =====================================================================
    hm_left, hm_center, hm_right = st.columns([1, 3, 1])
    with hm_center:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top:0; color:{PALETTE['primary_dark']};'>🔥 Peta Silang Keselarasan Label (Cross-Tabulation)</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.85rem; color:{PALETTE['muted']};'>Jumlah objek data yang dialokasikan ke kombinasi cluster K-Means vs K-Medoids yang sama.</p>", unsafe_allow_html=True)
            crosstab = pd.crosstab(
                pd.Series(st.session_state.kmeans_labels, name="K-Means").map(lambda x: f"Cluster {x}"),
                pd.Series(st.session_state.kmedoids_labels, name="K-Medoids").map(lambda x: f"Cluster {x}"),
            )
            fig_heat = go.Figure(data=go.Heatmap(
                z=crosstab.values,
                x=[f"K-Medoids {c}" for c in crosstab.columns],
                y=[f"K-Means {r}" for r in crosstab.index],
                colorscale=[[0, "#F8FAFC"], [1, PALETTE["primary_dark"]]],
                text=crosstab.values,
                texttemplate="%{text}",
                textfont=dict(family="JetBrains Mono, monospace", size=13),
                showscale=False,
            ))
            fig_heat.update_layout(
                font=dict(family="Plus Jakarta Sans, sans-serif"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickfont=dict(color=PALETTE["text"])),
                yaxis=dict(tickfont=dict(color=PALETTE["text"])),
                margin=dict(t=10, b=10, l=10, r=10),
                height=280
            )
            st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})

    st.write("")

    # =====================================================================
    # 5. KOTAK KESIMPULAN AKADEMIS (INSIGHT CARD)
    # =====================================================================
    st.markdown(
        f"""
        <div class="ci-card" style="margin-bottom: 0;">
            <h4 style="margin-top:0; color:{PALETTE['primary_dark']};">📝 Analisis Komparatif Komprehensif</h4>
            <p style="font-size:0.85rem; color:{PALETTE['muted']}; margin-bottom:1rem;">
                Kesimpulan akhir pembuktian hipotesis pengujian komparasi model berdasarkan dataset aktual yang diunggah pengguna.
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    agreement = np.mean(st.session_state.kmeans_labels == st.session_state.kmedoids_labels) * 100

    st.markdown(
        f"""
        <div class="conclusion-card">
            <ul style="margin: 0; padding-left: 1.2rem; line-height: 1.6; color: {PALETTE['text']}; font-size:0.9rem;">
                <li>Selisih absolut kedekatan struktur antar-kedua model (Silhouette Score Deviation) tercatat sebesar <b>{diff:.4f}</b>.</li>
                <li>Tingkat keselarasan alokasi baris data (Label Assignment Agreement) mencapai <b>{agreement:.1f}%</b>. Hal ini menunjukkan tingkat konsistensi klasifikasi yang tinggi antar-kedua algoritma pada dataset Atensi Yapi.</li>
                <li>Metode <b>K-Means</b> menghasilkan partisi pembagian jumlah sampel yang cenderung 
                    <b>{"lebih seimbang dan merata" if km_counts.std() < kmed_counts.std() else "memiliki tingkat variansi pengelompokan yang lebih tajam"}</b> 
                    dengan simpangan baku (Std. Dev) sebaran anggota sebesar <b>{km_counts.std():.2f}</b>, dibandingkan K-Medoids dengan nilai simpangan sebesar <b>{kmed_counts.std():.2f}</b>.</li>
                <li><b>Rekomendasi Akademis Bab 5:</b> Algoritma <b>{best_method}</b> terpilih sebagai model terbaik untuk melakukan analisis segmentasi pengelompokan tingkat kerentanan sosial ekonomi penerima bantuan karena memiliki performa kohesi objek internal tertinggi.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )