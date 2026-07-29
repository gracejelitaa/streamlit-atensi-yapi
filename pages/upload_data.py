import streamlit as st
import pandas as pd
from utils import validate_columns, preprocess_data, run_clustering

# =====================================================================
# TEMPLATE CSV — kolom & contoh data sesuai feature_config di artifacts
# =====================================================================
TEMPLATE_COLUMNS = [
    "Nama Penerima",
    "Status Orang Tua",
    "Kondisi Tempat Tinggal",
    "Kondisi Bangunan",
    "Atap Tempat Tinggal",
    "Lantai Tempat Tinggal",
    "Sumber Penerangan",
    "Sumber Air Bersih",
    "Jumlah Tanggungan",
    "Pengeluaran Perbulan",
]

TEMPLATE_SAMPLE_ROWS = [
    ["Contoh Nama 1", "Yatim", "Milik Sendiri", "Permanent", "Seng", "Ubin", 900, "PDAM", 3, 1500000],
    ["Contoh Nama 2", "Piatu", "Sewa", "Semi Permanent", "Rumbia", "Semen", 450, "Mata Air", 5, 900000],
    ["Contoh Nama 3", "Yatim Piatu", "Panti Asuhan", "Tidak Permanent", "Rumbia", "Tanah", 220, "Air Hujan", 2, 600000],
]


def _build_template_csv() -> bytes:
    df_template = pd.DataFrame(TEMPLATE_SAMPLE_ROWS, columns=TEMPLATE_COLUMNS)
    return df_template.to_csv(index=False).encode("utf-8-sig")


def show(artifacts):
    st.markdown(
        """
        <div class="hero-box">
            <h1>📤 Upload Data</h1>
            <p>Unggah data penerima bantuan dalam format CSV untuk diproses melalui pipeline
            clustering (K-Means & K-Medoids) yang sama seperti data referensi.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if artifacts is None:
        st.error(
            "❌ Artifact model belum tersedia di folder `artifacts/`. "
            "Hubungi admin untuk melengkapi file model terlebih dahulu."
        )
        return

    cfg = artifacts["feature_config"]
    encoding_maps = artifacts["encoding_maps"]
    categorical_cols = cfg["categorical_cols"]
    numeric_cols = [c for c in cfg["original_feature_cols"] if c not in categorical_cols]

    col1, col2 = st.columns([1, 1.4])

    # -----------------------------------------------------------------
    # KOLOM 1 — Template CSV
    # -----------------------------------------------------------------
    with col1:
        st.markdown('<div class="section-title"><h2>1. Unduh Template</h2></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="ci-card">
                <p style="margin-bottom:0.8rem;">
                Gunakan template ini agar nama kolom dan format data Anda sesuai dengan
                yang dibutuhkan model clustering.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.download_button(
            label="⬇️ Download Template CSV",
            data=_build_template_csv(),
            file_name="template_data_clustering.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # -----------------------------------------------------------------
    # KOLOM 2 — Upload & Proses
    # -----------------------------------------------------------------
    with col2:
        st.markdown('<div class="section-title"><h2>2. Upload &amp; Proses</h2></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])

        if uploaded_file is not None:
            try:
                df_raw = pd.read_csv(uploaded_file)
            except Exception as e:
                st.error(f"❌ Gagal membaca file CSV: {e}")
                return

            missing_cols, has_id_col = validate_columns(df_raw, cfg)

            if missing_cols:
                st.error(
                    "❌ Kolom berikut tidak ditemukan di file Anda: "
                    + ", ".join(f"`{c}`" for c in missing_cols)
                )
                return

            if not has_id_col:
                st.warning(
                    f"⚠️ Kolom ID (`{cfg['id_column']}`) tidak ditemukan. "
                    "Data akan diberi label otomatis (Data 1, Data 2, dst)."
                )

            st.success(f"✅ File terbaca: {len(df_raw)} baris data siap diproses.")

            if st.button("🚀 Jalankan Clustering", use_container_width=True):
                with st.spinner("Memproses data..."):
                    df_selected, df_encoded, df_renamed, df_scaled, X_scaled, n_missing = preprocess_data(
                        df_raw, artifacts
                    )

                    if n_missing > 0:
                        st.error(
                            "❌ Ditemukan nilai kategori yang tidak dikenali (tidak sesuai kamus "
                            "encoding). Periksa kembali isi kolom kategorikal sesuai daftar di bawah."
                        )
                        return

                    results = run_clustering(X_scaled, artifacts)
                    for key, val in results.items():
                        st.session_state[key] = val

                    st.session_state.df_raw = df_raw
                    st.session_state.df_selected = df_selected
                    st.session_state.df_encoded = df_encoded
                    st.session_state.df_renamed = df_renamed
                    st.session_state.df_scaled = df_scaled
                    st.session_state.X_scaled = X_scaled
                    st.session_state.clustering_done = True
                    st.session_state._artifacts_fingerprint = artifacts.get("_fingerprint")

                st.success(
                    f"✅ Berhasil memproses {len(df_raw)} baris data. "
                    "Buka menu Dashboard / K-Means / K-Medoids / Perbandingan / Hasil Akhir "
                    "untuk melihat hasilnya."
                )

    # -----------------------------------------------------------------
    # KETENTUAN KOLOM
    # -----------------------------------------------------------------
    st.markdown('<div class="section-title"><h2>Ketentuan Kolom</h2></div>', unsafe_allow_html=True)
    with st.expander("📋 Lihat detail kolom yang dibutuhkan", expanded=False):
        st.markdown(f"**Kolom ID:** `{cfg['id_column']}` (opsional, tidak ikut dihitung dalam clustering)")

        st.markdown("**Kolom kategorikal** (isi harus persis sama dengan salah satu pilihan berikut):")
        for col in categorical_cols:
            options = ", ".join(f"`{v}`" for v in encoding_maps[col].keys())
            st.markdown(f"- **{col}**: {options}")

        st.markdown("**Kolom numerik** (isi dengan angka, tanpa simbol/tanda ribuan):")
        for col in numeric_cols:
            st.markdown(f"- **{col}**")
