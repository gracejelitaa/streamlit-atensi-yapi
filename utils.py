from pathlib import Path
import joblib
import joblib.numpy_pickle as _jnp
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, pairwise_distances

ARTIFACT_DIR = Path(__file__).parent / "artifacts"

# =====================================================================
# CentroidModel — SHIM WAJIB ADA UNTUK BISA LOAD kmeans_model.pkl
# =====================================================================
# File 'kmeans_model.pkl' yang di-export dari Colab ternyata BUKAN
# objek sklearn KMeans asli, melainkan instance dari class custom
# bernama 'CentroidModel' yang didefinisikan di __main__ notebook
# (isinya cuma menyimpan atribut cluster_centers_).
# =====================================================================
class CentroidModel:
    """Pengganti minimal untuk objek KMeans: hanya butuh cluster_centers_
    dan method predict() berbasis jarak terdekat (sama seperti KMeans.predict)."""
    cluster_centers_ = None

    def predict(self, X):
        X = np.asarray(X)
        D = pairwise_distances(X, self.cluster_centers_, metric="euclidean")
        return D.argmin(axis=1)


# =====================================================================
# _SafeUnpickler & _safe_joblib_load
# =====================================================================
# Pendekatan sebelumnya (menaruh CentroidModel di sys.modules['__main__'])
# TIDAK bisa diandalkan karena tergantung cara Streamlit menjalankan
# app.py — kadang sys.modules['__main__'] bukan module yang kita kira,
# atau bisa berubah identitas antar rerun.
#
# Solusi yang pasti jalan di komputer manapun: pakai unpickler custom
# yang meng-override find_class(), sehingga SETIAP kali pickle stream
# minta class '__main__.CentroidModel', kita langsung kasih class
# CentroidModel di atas -- tidak peduli __main__ sesungguhnya itu apa.
# Ini dibangun di atas NumpyUnpickler milik joblib sendiri (bukan
# pickle.Unpickler biasa) supaya array numpy di dalam file tetap
# direkonstruksi dengan benar persis seperti joblib.load() normal.
# =====================================================================
class _SafeUnpickler(_jnp.NumpyUnpickler):
    def find_class(self, module, name):
        if module == "__main__" and name == "CentroidModel":
            return CentroidModel
        return super().find_class(module, name)


def _safe_joblib_load(filepath):
    filepath = str(filepath)
    with open(filepath, "rb") as fobj:
        unpickler = _SafeUnpickler(filepath, fobj, ensure_native_byte_order=True)
        return unpickler.load()

def _artifacts_fingerprint():
    """
    Menghasilkan 'sidik jari' (fingerprint) dari seluruh file .pkl di folder
    artifacts/ berdasarkan waktu modifikasi terakhirnya (mtime). Dipakai
    sebagai cache-key untuk _load_artifacts_impl() supaya Streamlit otomatis
    membaca ULANG file yang berubah -- tanpa perlu restart server manual.
    """
    if not ARTIFACT_DIR.exists():
        return ()
    return tuple(
        (f.name, f.stat().st_mtime_ns)
        for f in sorted(ARTIFACT_DIR.glob("*.pkl"))
    )


@st.cache_resource(show_spinner=False)
def _load_artifacts_impl(fingerprint):
    # 'fingerprint' sengaja dijadikan bagian dari cache key (bukan
    # underscore-prefixed) -- begitu ada file .pkl yang berubah mtime-nya,
    # fingerprint berubah, dan Streamlit akan menganggapnya cache MISS lalu
    # menjalankan ulang fungsi ini dari awal (baca file .pkl yang terbaru).
    required_files = [
        "scaler.pkl", "encoding_maps.pkl", "feature_config.pkl",
        "kmeans_model.pkl", "kmedoids_medoids.pkl", "elbow_data.pkl",
    ]
    missing = [f for f in required_files if not (ARTIFACT_DIR / f).exists()]
    if missing:
        return None, missing

    artifacts = {f.split('.')[0]: _safe_joblib_load(ARTIFACT_DIR / f) for f in required_files}

    ref_path = ARTIFACT_DIR / "reference_results.pkl"
    artifacts["reference_results"] = _safe_joblib_load(ref_path) if ref_path.exists() else None

    # --- Artifact opsional: centroid/medoid AWAL (skala normalisasi) ---
    # Tidak wajib ada, supaya project lama yang belum re-export tetap jalan
    kmeans_awal_path = ARTIFACT_DIR / "kmeans_centroids_awal.pkl"
    artifacts["kmeans_centroids_awal"] = _safe_joblib_load(kmeans_awal_path) if kmeans_awal_path.exists() else None

    kmedoids_awal_path = ARTIFACT_DIR / "kmedoids_medoids_awal.pkl"
    artifacts["kmedoids_medoids_awal"] = _safe_joblib_load(kmedoids_awal_path) if kmedoids_awal_path.exists() else None

    # --- Dataset asli (mentah, sebelum encoding/normalisasi) ---
    # Dipakai supaya aplikasi bisa langsung menjalankan clustering otomatis
    # begitu dibuka, tanpa perlu user mengunggah dataset secara manual.
    ref_dataset_path = ARTIFACT_DIR / "reference_dataset.pkl"
    artifacts["reference_dataset"] = _safe_joblib_load(ref_dataset_path) if ref_dataset_path.exists() else None

    artifacts["_fingerprint"] = fingerprint
    return artifacts, []


def load_artifacts():
    """Wrapper publik: selalu hitung fingerprint file .pkl TERBARU setiap
    kali dipanggil (murah/cepat, cuma baca mtime), lalu serahkan ke
    _load_artifacts_impl() yang di-cache berdasarkan fingerprint tsb."""
    fingerprint = _artifacts_fingerprint()
    return _load_artifacts_impl(fingerprint)

def validate_columns(df_raw: pd.DataFrame, cfg: dict):
    missing_cols = [c for c in cfg["original_feature_cols"] if c not in df_raw.columns]
    has_id_col = cfg["id_column"] in df_raw.columns or df_raw.index.name == cfg["id_column"]
    return missing_cols, has_id_col

def preprocess_data(df_raw: pd.DataFrame, artifacts: dict):
    cfg = artifacts["feature_config"]
    encoding_maps = artifacts["encoding_maps"]

    df_selected = df_raw[cfg["original_feature_cols"]].copy()
    df_encoded = df_selected.copy()
    for col in cfg["categorical_cols"]:
        if col in df_encoded.columns:
            df_encoded[col] = df_encoded[col].map(encoding_maps[col])

    # =================================================================
    # TRANSFORMASI PEMBALIKAN NILAI (REFLECTION) — WAJIB ADA
    # =================================================================
    reflect_cols = cfg.get("reflect_cols", ["Sumber Penerangan", "Pengeluaran Perbulan"])
    for col in reflect_cols:
        if col in df_encoded.columns:
            max_v = df_encoded[col].max()
            min_v = df_encoded[col].min()
            df_encoded[col] = (max_v + min_v) - df_encoded[col]

    df_renamed = df_encoded.rename(columns=cfg["rename_map"])
    df_renamed = df_renamed[cfg["feature_order"]]
    n_missing_after_encoding = int(df_renamed.isnull().sum().sum())

    scaler = artifacts["scaler"]
    X_scaled = scaler.transform(df_renamed)
    df_scaled = pd.DataFrame(X_scaled, columns=cfg["feature_order"], index=df_raw.index)

    return df_selected, df_encoded, df_renamed, df_scaled, X_scaled, n_missing_after_encoding

def run_clustering(X_scaled: np.ndarray, artifacts: dict):
    kmeans_model = artifacts["kmeans_model"]
    medoid_coords = artifacts["kmedoids_medoids"]
    reference = artifacts.get("reference_results")

    n = X_scaled.shape[0]

    used_reference = bool(reference is not None and reference.get("n_data") == n)

    if used_reference:
        kmeans_labels = np.asarray(reference["kmeans_labels"])
        kmedoids_labels = np.asarray(reference["kmedoids_labels"])
        silhouette_kmeans = reference["silhouette_kmeans"]
        silhouette_kmedoids = reference["silhouette_kmedoids"]
    else:
        kmeans_labels = kmeans_model.predict(X_scaled)

        # Menggunakan rumus pairwise_distances yang sudah sinkron 100% dengan Colab
        D_medoid = pairwise_distances(X_scaled, medoid_coords, metric='euclidean')
        kmedoids_labels = np.argmin(D_medoid, axis=1)

        try:
            silhouette_kmeans = silhouette_score(X_scaled, kmeans_labels)
        except ValueError:
            silhouette_kmeans = np.nan
        try:
            silhouette_kmedoids = silhouette_score(X_scaled, kmedoids_labels)
        except ValueError:
            silhouette_kmedoids = np.nan

    results = {
        "kmeans_labels": kmeans_labels,
        "kmedoids_labels": kmedoids_labels,
        "silhouette_kmeans": silhouette_kmeans,
        "silhouette_kmedoids": silhouette_kmedoids,
        "used_reference_results": used_reference,
    }

    # Proses PCA yang aman dan terkendali (visualisasi saja, tidak
    # memengaruhi label/silhouette yang sudah ditentukan di atas)
    pca = PCA(n_components=2, random_state=42)
    pca_coords = pca.fit_transform(X_scaled)
    results["pca_coords"] = pca_coords
    results["pca_centroids_kmeans"] = pca.transform(kmeans_model.cluster_centers_)
    results["pca_medoids_kmedoids"] = pca.transform(medoid_coords)

    return results


def run_auto_pipeline(artifacts: dict) -> bool:
    """
    Menjalankan seluruh pipeline (preprocessing + clustering) secara OTOMATIS
    memakai dataset asli ('reference_dataset.pkl') begitu aplikasi dibuka,
    tanpa memerlukan halaman "Upload Dataset". Hasilnya disimpan ke
    st.session_state persis seperti alur upload manual sebelumnya, sehingga
    semua halaman lain (Dashboard, Preprocessing, K-Means, dst) tetap bisa
    jalan tanpa perubahan.

    Pipeline dijalankan ulang setiap kali fingerprint file .pkl di artifacts/
    berubah (misal kamu update encoding_maps.pkl, scaler.pkl, atau
    reference_dataset.pkl) -- jadi TIDAK perlu restart server manual supaya
    perubahan file kebaca. Kalau fingerprint sama seperti sebelumnya, tidak
    dihitung ulang (supaya tidak lambat tiap pindah halaman).

    Return True kalau pipeline berhasil dijalankan / sudah pernah dijalankan,
    False kalau dataset asli tidak ditemukan atau gagal diproses.
    """
    current_fingerprint = artifacts.get("_fingerprint")
    already_done = (
        st.session_state.get("clustering_done")
        and st.session_state.get("_artifacts_fingerprint") == current_fingerprint
    )
    if already_done:
        return True

    df_raw = artifacts.get("reference_dataset")
    if df_raw is None:
        return False

    df_selected, df_encoded, df_renamed, df_scaled, X_scaled, n_missing = preprocess_data(df_raw, artifacts)
    if n_missing > 0:
        st.error(
            "❌ Gagal memproses `reference_dataset.pkl`: ditemukan nilai kategori yang "
            "tidak dikenali oleh `encoding_maps.pkl`. Periksa kembali kedua artifact tersebut."
        )
        return False

    results = run_clustering(X_scaled, artifacts)
    for k, v in results.items():
        st.session_state[k] = v

    st.session_state.df_raw = df_raw
    st.session_state.df_selected = df_selected
    st.session_state.df_encoded = df_encoded
    st.session_state.df_renamed = df_renamed
    st.session_state.df_scaled = df_scaled
    st.session_state.X_scaled = X_scaled
    st.session_state.clustering_done = True
    st.session_state._artifacts_fingerprint = current_fingerprint

    return True

def get_id_series(df_raw: pd.DataFrame, cfg: dict):
    id_col = cfg["id_column"]
    if id_col in df_raw.columns:
        return df_raw[id_col]
    if df_raw.index.name == id_col:
        return pd.Series(df_raw.index, index=df_raw.index)
    return pd.Series([f"Data {i+1}" for i in range(len(df_raw))], index=df_raw.index)

def plot_elbow(elbow_dict: dict, optimal_k: int):
    ks = list(elbow_dict.keys())
    values = list(elbow_dict.values())

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ks,
        y=values,
        mode="lines+markers",
        line=dict(color="#2563EB", width=3),
        marker=dict(size=10, color="#2563EB", symbol="circle", line=dict(color="white", width=1.5)),
        name="WCSS"
    ))

    if optimal_k in ks:
        fig.add_trace(go.Scatter(
            x=[optimal_k],
            y=[values[ks.index(optimal_k)]],
            mode="markers",
            marker=dict(size=16, color="#F59E0B", symbol="star", line=dict(color="white", width=1.5)),
            name=f"K optimal = {optimal_k}"
        ))

    fig.update_layout(
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
        title=dict(
            text="<b>Elbow Method (Jumlah Cluster Optimal)</b>",
            font=dict(family="Fraunces, serif", size=15, color="#1E3A8A"),
            x=0.0, y=0.95
        ),
        xaxis=dict(
            title="Jumlah Cluster (k)",
            tickmode="array",
            tickvals=ks,
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#64748B")
        ),
        yaxis=dict(
            title="WCSS",
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#64748B")
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=40, l=40, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor="#E2E8F0",
            borderwidth=1
        )
    )
    return fig

def plot_distribution(labels: np.ndarray, color: str = None):
    warna_batang = ['#2563EB', '#F59E0B', '#22C55E']
    counts = pd.Series(labels).value_counts().sort_index()
    cluster_names = [f"Cluster {i}" for i in counts.index]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cluster_names,
        y=counts.values,
        marker=dict(
            color=warna_batang[:len(counts)],
            line=dict(color="white", width=1.5),
            opacity=0.9
        ),
        text=counts.values,
        textposition="outside",
        textfont=dict(family="JetBrains Mono, monospace", size=11, color="#0F172A"),
        width=0.45
    ))

    max_val = max(counts.values) if len(counts) > 0 else 10
    y_limit = max_val + (max_val * 0.18)

    fig.update_layout(
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
        xaxis=dict(
            title="Kelompok Cluster",
            title_font=dict(size=11, color="#64748B"),
            showgrid=False,
            tickfont=dict(color="#0F172A")
        ),
        yaxis=dict(
            title="Jumlah Anggota",
            title_font=dict(size=11, color="#64748B"),
            range=[0, y_limit],
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(family="JetBrains Mono, monospace", color="#64748B")
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=40, l=40, r=20)
    )
    return fig

def plot_pca_scatter(pca_coords, labels, center_coords, center_label, title):
    colors_km = ['#2563EB', '#F59E0B', '#22C55E']

    df_plot = pd.DataFrame({
        "PC1": pca_coords[:, 0],
        "PC2": pca_coords[:, 1],
        "Cluster_Int": labels
    })

    fig = go.Figure()

    unique_labels = sorted(df_plot["Cluster_Int"].unique())

    for label_id in unique_labels:
        cluster_data = df_plot[df_plot["Cluster_Int"] == label_id]
        color_idx = int(label_id) % len(colors_km)

        fig.add_trace(go.Scatter(
            x=cluster_data["PC1"],
            y=cluster_data["PC2"],
            mode="markers",
            name=f"Cluster {label_id}",
            marker=dict(
                size=8,
                color=colors_km[color_idx],
                opacity=0.75,
                line=dict(color="white", width=0.5)
            )
        ))

    fig.add_trace(go.Scatter(
        x=center_coords[:, 0],
        y=center_coords[:, 1],
        mode="markers",
        name=center_label,
        marker=dict(
            symbol="star",
            size=15,
            color="#FF3366",
            line=dict(color="white", width=1.5)
        )
    ))

    fig.update_layout(
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family="Fraunces, serif", size=14, color="#1E3A8A"),
            x=0.0, y=0.95
        ),
        xaxis=dict(
            title="Principal Component 1 (PC1)",
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(family="JetBrains Mono, monospace", size=9, color="#64748B")
        ),
        yaxis=dict(
            title="Principal Component 2 (PC2)",
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(family="JetBrains Mono, monospace", size=9, color="#64748B")
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, b=40, l=40, r=20),
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0.7)",
            bordercolor="#E2E8F0",
            borderwidth=1,
            font=dict(size=10)
        )
    )
    return fig

def show_model_visual(artifacts, image_key, caption, interactive_fig_fn):
    st.plotly_chart(interactive_fig_fn(), use_container_width=True)
    if caption:
        st.caption(caption)