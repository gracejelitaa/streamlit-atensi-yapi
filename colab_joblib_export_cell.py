# =====================================================================
# CELL JOBLIB EXPORT — KHUSUS UNTUK APLIKASI STREAMLIT "ClusterInsight"
# =====================================================================

import joblib
import os
import shutil
import numpy as np
from google.colab import files
from sklearn.metrics import silhouette_score

os.makedirs("artifacts", exist_ok=True)

# 1. Scaler — MinMaxScaler yang sudah di-fit pada X1-X9
joblib.dump(scaler, "artifacts/scaler.pkl")

# 2. Dictionary encoding manual
encoding_maps = {
    'Status Orang Tua': {
        'Piatu': 1,
        'Yatim': 2,
        'Yatim Piatu': 3
    },
    'Kondisi Tempat Tinggal': {
        'Milik Sendiri': 1,
        'Sewa': 2,
        'Menumpang': 3,
        'Panti Asuhan': 4
    },
    'Kondisi Bangunan': {
        'Permanent': 1,
        'Semi Permanent': 2,
        'Tidak Permanent': 3
    },
    'Atap Tempat Tinggal': {
        'Seng': 1,
        'Rumbia': 2
    },
    'Lantai Tempat Tinggal': {
        'Ubin': 1,
        'Semen': 2,
        'Tanah': 3
    },
    'Sumber Air Bersih': {
        'PDAM': 1,
        'Mata Air': 2,
        'Air Hujan': 3
    },
}
joblib.dump(encoding_maps, "artifacts/encoding_maps.pkl")

# 3. Konfigurasi fitur & metadata pipeline
feature_config = {
    "id_column": "Nama Penerima",
    "original_feature_cols": [
        'Status Orang Tua',
        'Kondisi Tempat Tinggal',
        'Kondisi Bangunan',
        'Atap Tempat Tinggal',
        'Lantai Tempat Tinggal',
        'Sumber Penerangan',
        'Sumber Air Bersih',
        'Jumlah Tanggungan',
        'Pengeluaran Perbulan',
    ],
    "rename_map": {
        'Status Orang Tua': 'X1',
        'Kondisi Tempat Tinggal': 'X2',
        'Kondisi Bangunan': 'X3',
        'Atap Tempat Tinggal': 'X4',
        'Lantai Tempat Tinggal': 'X5',
        'Sumber Penerangan': 'X6',
        'Sumber Air Bersih': 'X7',
        'Jumlah Tanggungan': 'X8',
        'Pengeluaran Perbulan': 'X9',
    },
    "feature_order": ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9'],
    "categorical_cols": list(encoding_maps.keys()),
    "k": k,  # jumlah cluster final (=3)
}
joblib.dump(feature_config, "artifacts/feature_config.pkl")

# ---------------------------------------------------------------
# 4. Model K-Means final (variabel 'kmeans_akhir')
# ---------------------------------------------------------------
joblib.dump(kmeans_akhir, "artifacts/kmeans_model.pkl")

# ---------------------------------------------------------------
# 5. Koordinat Medoid akhir K-Medoids
# ---------------------------------------------------------------
medoid_coords = df_normalisasi[kolom_fitur].values[current_medoids]
joblib.dump(medoid_coords, "artifacts/kmedoids_medoids.pkl")

# ---------------------------------------------------------------
# 6. Data Elbow Method (WCSS per k, dari cell "Elbow Method")
# ---------------------------------------------------------------
elbow_data = {
    "kmeans": dict(zip(df_elbow_method['Jumlah Cluster (k)'], df_elbow_method['Nilai WCSS'])),
    "optimal_k": k,
}
joblib.dump(elbow_data, "artifacts/elbow_data.pkl")

# ---------------------------------------------------------------
# 7. SANITY CHECK — mendeteksi kasus "current_medoids" tidak sinkron
# ---------------------------------------------------------------
_dist_check = np.array([
    np.linalg.norm(X_arr - medoid_coords[i], axis=1)
    for i in range(len(medoid_coords))
]).T
_labels_check = np.argmin(_dist_check, axis=1)

_labels_match = np.array_equal(_labels_check, labels)
_sil_check = silhouette_score(df_normalisasi, _labels_check, metric='euclidean')
_sil_diff = abs(_sil_check - silhouette_kmedoids)

print("=" * 70)
print("🔍 SANITY CHECK EXPORT K-MEDOIDS")
print("-" * 70)
print(f"Label hasil re-assign dari medoid_coords sama dengan 'labels'? -> {_labels_match}")
print(f"Silhouette dari medoid_coords : {_sil_check:.4f}")
print(f"Silhouette 'silhouette_kmedoids' (dicatat di skripsi) : {silhouette_kmedoids:.4f}")
if not _labels_match or _sil_diff > 1e-6:
    print("⚠️  PERINGATAN: TIDAK SINKRON! Artifact yang akan diexport TIDAK akan")
    print("    menghasilkan hasil yang sama dengan yang ada di skripsi kamu.")
    print("    Penyebab paling umum: cell 'Medoid Awal (M0,M1,M2)' di-run ulang")
    print("    setelah cell iterasi PAM konvergen dijalankan.")
    print("    SOLUSI: klik Runtime -> Run All (jalankan seluruh notebook dari")
    print("    awal berurutan), lalu jalankan cell export ini paling akhir,")
    print("    TANPA menjalankan ulang cell 'Medoid Awal' secara terpisah.")
else:
    print("✅ Sinkron — artifact yang diexport konsisten dengan hasil di skripsi.")
print("=" * 70)

# ---------------------------------------------------------------
# 8. Menyalin GAMBAR ASLI (PNG) hasil visualisasi dari notebook, agar
# ---------------------------------------------------------------
os.makedirs("artifacts/images", exist_ok=True)

image_files = [
    "Elbow Method.png",
    "Scatterplot KMeans.png",
    "Scatterplot KMedoids.png",
    "Bar Chart Distribusi KMeans.png",
    "Bar Chart Distribusi KMedoids.png",
]
missing_images = []
for img in image_files:
    if os.path.exists(img):
        shutil.copy(img, f"artifacts/images/{img}")
    else:
        missing_images.append(img)

if missing_images:
    print("⚠️  Gambar berikut TIDAK ditemukan di sesi Colab (jalankan dulu cell")
    print("    visualisasi terkait sebelum menjalankan cell export ini):")
    for img in missing_images:
        print("   -", img)

# ---------------------------------------------------------------
# 9. Hasil referensi (angka final) dari model asli — dipakai Streamlit
# ---------------------------------------------------------------
reference_results = {
    "kmeans_labels": labels_kmeans,
    "kmedoids_labels": labels,
    "silhouette_kmeans": float(silhouette_kmeans),
    "silhouette_kmedoids": float(silhouette_kmedoids),
    "n_data": int(len(df_normalisasi)),
}
joblib.dump(reference_results, "artifacts/reference_results.pkl")

# ---------------------------------------------------------------
# 10. Centroid AWAL K-Means & Medoid AWAL K-Medoids (skala normalisasi)
# ---------------------------------------------------------------
joblib.dump(kmeans_awal.cluster_centers_, "artifacts/kmeans_centroids_awal.pkl")
joblib.dump(X_arr[medoid_indices], "artifacts/kmedoids_medoids_awal.pkl")

# ---------------------------------------------------------------
# Ringkasan & download
# ---------------------------------------------------------------
print("✅ Semua artifact berhasil dibuat di folder artifacts/:")
for f in sorted(os.listdir("artifacts")):
    print("  -", f)
print("Gambar di artifacts/images/:")
for f in sorted(os.listdir("artifacts/images")):
    print("  -", f)

shutil.make_archive("artifacts_clusterinsight", "zip", "artifacts")
files.download("artifacts_clusterinsight.zip")

print("\n📦 File 'artifacts_clusterinsight.zip' sedang didownload.")
print("   Extract isinya ke folder artifacts/ pada project Streamlit ClusterInsight")
print("   (folder images/ dan file reference_results.pkl ikut ter-extract).")