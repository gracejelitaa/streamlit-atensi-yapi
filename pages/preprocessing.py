import pandas as pd
import streamlit as st
from config import card_html

def show(artifacts):
    st.markdown('<div class="section-title"><h2>⚙️ Preprocessing Data</h2></div>', unsafe_allow_html=True)
    if st.session_state.df_raw is None:
        st.error(
            "⚠️ Dataset asli belum berhasil dimuat. Pastikan file "
            "`artifacts/reference_dataset.pkl` ada dan valid, lalu muat ulang halaman ini.",
            icon="🚫",
        )
        return

    # =====================================================================
    # 0. RINGKASAN CEPAT
    # =====================================================================
    df_raw = st.session_state.df_raw
    r1, r2, r3 = st.columns(3)
    with r1: st.markdown(card_html("Jumlah Baris", f"{df_raw.shape[0]:,}", "Data Penerima Manfaat", "📄"), unsafe_allow_html=True)
    with r2: st.markdown(card_html("Jumlah Kolom", f"{df_raw.shape[1]}", "Kolom pada Dataset Asli", "📊"), unsafe_allow_html=True)
    with r3:
        n_null = int(df_raw.isnull().sum().sum())
        st.markdown(card_html("Nilai Kosong", f"{n_null}", "Sel Kosong Terdeteksi" if n_null else "Tidak Ada Nilai Kosong", "⚠️" if n_null else "✅"), unsafe_allow_html=True)
    st.write("")

    # =====================================================================
    # 1. TIMELINE TAHAPAN PREPROCESSING
    # =====================================================================
    step2_done = st.session_state.df_encoded is not None
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:1.5rem; flex-wrap:wrap; background-color:#FFFFFF; border:1px solid #E2E8F0; padding: 1.2rem; border-radius: 18px; box-shadow: 0 4px 15px rgba(148, 163, 184, 0.02);">
            <span class="badge-success">1. Dataset Awal</span>
            <span style="color:#94A3B8; font-weight:bold; padding: 0 0.2rem;">➔</span>
            <span class="{'badge-success' if step2_done else 'badge-pending'}">
                2. Encoding Manual
            </span>
            <span style="color:#94A3B8; font-weight:bold; padding: 0 0.2rem;">➔</span>
            <span class="{'badge-success' if step2_done else 'badge-pending'}">
                3. Normalisasi (MinMaxScaler)
            </span>
        </div>
        """, unsafe_allow_html=True,
    )

    with st.expander("1️⃣ Dataset Awal", expanded=not step2_done):
        st.dataframe(st.session_state.df_raw.head(15), use_container_width=True)
        st.caption(f"Menampilkan 15 dari {st.session_state.df_raw.shape[0]} baris total.")

    if not step2_done:
        st.warning("⏳ Preprocessing belum selesai diproses otomatis. Coba muat ulang halaman ini.", icon="⚠️")
        return

    cfg = artifacts["feature_config"]

    # =====================================================================
    # 2. HASIL ENCODING MANUAL +  MAPPING
    # =====================================================================
    with st.expander("2️⃣ Hasil Encoding Manual", expanded=False):
        st.dataframe(st.session_state.df_encoded.head(15), use_container_width=True)
        st.markdown("**📖 Pemetaan (encoding maps) yang digunakan:**")
        enc_maps = artifacts["encoding_maps"]
        map_cols = st.columns(2)
        for i, (kolom, mapping) in enumerate(enc_maps.items()):
            with map_cols[i % 2]:
                df_map = pd.DataFrame(list(mapping.items()), columns=["Kategori Asli", "Kode"])
                st.markdown(f"**{kolom}**")
                st.dataframe(df_map, use_container_width=True, hide_index=True)

    # =====================================================================
    # 3. HASIL NORMALISASI + RINGKASAN STATISTIK
    # =====================================================================
    with st.expander("3️⃣ Hasil Normalisasi (MinMaxScaler)", expanded=True):
        st.dataframe(st.session_state.df_scaled.head(15).round(4), use_container_width=True)

        st.markdown("**📊 Ringkasan Rentang Nilai Sebelum vs Sesudah Normalisasi**")
        raw_stats = st.session_state.df_renamed[cfg["feature_order"]].agg(["min", "max"]).T
        scaled_stats = st.session_state.df_scaled[cfg["feature_order"]].agg(["min", "max"]).T
        df_compare = pd.DataFrame({
            "Fitur": cfg["feature_order"],
            "Min Asli": raw_stats["min"].values,
            "Max Asli": raw_stats["max"].values,
            "Min Ternormalisasi": scaled_stats["min"].values.round(4),
            "Max Ternormalisasi": scaled_stats["max"].values.round(4),
        })
        st.dataframe(df_compare, use_container_width=True, hide_index=True)
        st.caption("Setelah normalisasi, seluruh fitur berada pada rentang [0, 1] agar tidak ada atribut yang mendominasi perhitungan jarak Euclidean.")