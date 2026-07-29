import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import card_html, PALETTE

def show(artifacts):
    # =====================================================================
    # HERO SECTION
    # =====================================================================
    status_badge = (
        "<span class='badge-success'>Clustering Selesai</span>"
        if st.session_state.clustering_done
        else "<span class='badge-pending'>Menunggu Dataset</span>"
    )

    if not st.session_state.clustering_done:
        st.info(
            "Dataset asli belum berhasil dimuat otomatis. Pastikan file "
            "`artifacts/reference_dataset.pkl` tersedia, lalu muat ulang halaman ini.",
            icon="ℹ️",
        )
        return
    st.markdown(
        f"""
        <div class="hero-box">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
                <div>
                    <h1 style="margin:0; color:white;">🔷 ClusterInsight</h1>
                    <p style="margin-top:0.4rem;">
                        Analisis pengelompokan data penerima bantuan sosial Atensi Yapi
                        menggunakan algoritma K-Means dan K-Medoids.
                    </p>
                </div>
                <div>{status_badge}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.clustering_done:
        st.info(
            "Dataset asli belum berhasil dimuat otomatis. Pastikan file "
            "`artifacts/reference_dataset.pkl` tersedia, lalu muat ulang halaman ini.",
            icon="ℹ️",
        )
        return
    # =====================================================================
    # DATA DARI SESSION STATE & ARTIFACTS
    # =====================================================================
    df = st.session_state.df_raw
    cfg = artifacts["feature_config"]
    sil_km = st.session_state.silhouette_kmeans
    sil_kmed = st.session_state.silhouette_kmedoids
    
    # Beri warna khusus pada teks metode terbaik sesuai filosofi warnamu
    if sil_km >= sil_kmed:
        best_method_html = f"<span style='color:{PALETTE['kmeans']}; font-weight:700;'>K-Means</span>"
        best_method_str = "K-Means"
    else:
        best_method_html = f"<span style='color:{PALETTE['kmedoids']}; font-weight:700;'>K-Medoids</span>"
        best_method_str = "K-Medoids"

    # =====================================================================
    # VISUAL METRIC CARDS (Menggunakan card_html kustom agar seragam & cantik)
    # =====================================================================
    st.markdown('<div class="section-title"><h2>Ringkasan Data & Model</h2></div>', unsafe_allow_html=True)
    
    # Baris 1: Informasi Dataset
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(card_html("Jumlah Data", f"{df.shape[0]:,}", "Penerima Manfaat", "📊"), unsafe_allow_html=True)
    with c2:
        st.markdown(card_html("Jumlah Fitur", f"{len(cfg['feature_order'])}", "Indikator Kerentanan", "⚙️"), unsafe_allow_html=True)
    with c3:
        st.markdown(card_html("Jumlah Cluster (K)", f"{cfg['k']}", "Pengelompokan Terpilih", "🔷"), unsafe_allow_html=True)

    st.write("") # Spasi antar baris kartu

    # Baris 2: Hasil Evaluasi
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(card_html("Silhouette Score K-Means", f"{sil_km:.4f}", "Kedekatan berbasis hitungan rata-rata", "🧬"), unsafe_allow_html=True)
    with c5:
        st.markdown(card_html("Silhouette Score K-Medoids", f"{sil_kmed:.4f}", "Kedekatan berbasis data objek nyata", "🎯"), unsafe_allow_html=True)
    with c6:
        # Menggunakan struktur ci-card kustom agar bisa menyisipkan HTML berwana untuk Metode Terbaik
        st.markdown(
            f"""
            <div class="ci-card" style="border-left: 4px solid {PALETTE['gold']};">
                <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1.2rem;">
                    <div style="display:flex; align-items:center; justify-content:center; width:2.75rem; height:2.75rem; border-radius:12px; background-color:rgba(245, 158, 11, 0.08); font-size:1.4rem; color:#F59E0B;">
                        👑
                    </div>
                    <span style="font-family:'Plus Jakarta Sans', sans-serif; font-weight:600; color:{PALETTE['muted']}; font-size:0.85rem; letter-spacing:0.02em; text-transform:uppercase;">Metode Terbaik</span>
                </div>
                <div style="font-size:2.2rem; font-weight:700; font-family:'JetBrains Mono', monospace; margin-bottom:0.4rem; line-height:1.1;">{best_method_html}</div>
                <div style="color:{PALETTE['muted']}; font-size:0.8rem; font-weight:400;">Berdasarkan nilai Silhouette tertinggi</div>
            </div>
            """, unsafe_allow_html=True
        )

    # =====================================================================
    # DYNAMIC INSIGHT CARD
    # =====================================================================
    best_method = "K-Means" if sil_km >= sil_kmed else "K-Medoids"
    best_score = max(sil_km, sil_kmed)
    alternative_method = "K-Medoids" if sil_km >= sil_kmed else "K-Means"
    alternative_score = min(sil_km, sil_kmed)
    

    st.write("")
    st.write("")

    # =====================================================================
    # CHART SECTION (FIXED: Grafik Terbungkus Sempurna di Dalam Kartu)
    # =====================================================================
    st.markdown('<div class="section-title"><h2>Analisis Perbandingan</h2></div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns([4, 6])

    with ch1:
        # Gunakan st.container dengan border agar otomatis membentuk kartu yang rapi
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="margin-bottom: 1.2rem;">
                    <h4 style="margin:0; font-size:1.1rem; color:{PALETTE['primary']}; font-family:'Fraunces', serif;">📐 Perbandingan Silhouette Score</h4>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            fig_score = go.Figure(data=[go.Bar(
                y=["K-Means", "K-Medoids"],
                x=[sil_km, sil_kmed],
                orientation="h",
                marker_color=[PALETTE["kmeans"], PALETTE["kmedoids"]],
                text=[f" {sil_km:.4f}", f" {sil_kmed:.4f}"],
                textposition="outside",
                width=0.4,
            )])
            fig_score.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 1.15], tickfont=dict(color=PALETTE["muted"], family="JetBrains Mono")),
                yaxis=dict(showgrid=False, tickfont=dict(color=PALETTE["text"], size=12)),
                margin=dict(t=10, b=10, l=10, r=50),
                height=180, # Disesuaikan agar pas di dalam kontainer
            )
            st.plotly_chart(fig_score, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        # Gunakan st.container dengan border agar otomatis membentuk kartu yang rapi
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="margin-bottom: 1.2rem;">
                    <h4 style="margin:0; font-size:1.1rem; color:{PALETTE['primary']}; font-family:'Fraunces', serif;">👥 Distribusi Anggota Tiap Cluster</h4>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            km_counts = pd.Series(st.session_state.kmeans_labels).value_counts().sort_index()
            kmed_counts = pd.Series(st.session_state.kmedoids_labels).value_counts().sort_index()
            all_clusters = sorted(set(km_counts.index) | set(kmed_counts.index))

            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(
                x=[f"Cluster {c}" for c in all_clusters],
                y=[km_counts.get(c, 0) for c in all_clusters],
                name="K-Means (Abstrak)", marker_color=PALETTE["kmeans"], width=0.25,
            ))
            fig_comp.add_trace(go.Bar(
                x=[f"Cluster {c}" for c in all_clusters],
                y=[kmed_counts.get(c, 0) for c in all_clusters],
                name="K-Medoids (Nyata)", marker_color=PALETTE["kmedoids"], width=0.25,
            ))
            fig_comp.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickfont=dict(color=PALETTE["text"])),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(color=PALETTE["muted"], family="JetBrains Mono")),
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(size=11, color=PALETTE["text"])),
                height=180, # Disesuaikan agar tingginya sejajar dengan kartu sebelah kiri
            )
            st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})