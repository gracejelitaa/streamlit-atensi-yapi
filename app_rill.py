import streamlit as st
from streamlit_option_menu import option_menu
from config import inject_css, init_session_state, PALETTE
from utils import load_artifacts, run_auto_pipeline
from pages import dashboard, preprocessing, kmeans, kmedoids, perbandingan, hasil_akhir

st.set_page_config(
    page_title="ClusterInsight",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    inject_css()
    init_session_state()

    artifacts, missing = load_artifacts()
    if artifacts is not None:
        pipeline_ok = run_auto_pipeline(artifacts)
        if not pipeline_ok:
            st.error(
                "❌ Dataset asli (`artifacts/reference_dataset.pkl`) tidak ditemukan atau gagal diproses. "
                "Pastikan file tersebut ada di folder `artifacts/` project ini."
            )

    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
                <h2 style="color:{PALETTE['primary_dark']}; margin-bottom:0;">🔷 ClusterInsight</h2>
                <p style="color:{PALETTE['muted']}; font-size:0.8rem;">Perbandingan K-Means & K-Medoids</p>
            </div>
            """, unsafe_allow_html=True,
        )

        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard", "Preprocessing",
                "K-Means", "K-Medoids", "Perbandingan",
                "Hasil Akhir",
            ],
            icons=[
                "house", "gear",
                "bar-chart", "diagram-3", "sliders",
                "file-earmark-text",
            ],
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"color": PALETTE["primary"], "font-size": "16px"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "2px 0", "border-radius": "10px"},
                "nav-link-selected": {"background-color": PALETTE["primary"], "color": "white"},
            },
        )

    # Routing Navigasi Halaman Dinamis
    if selected == "Dashboard":
        dashboard.show(artifacts)
    elif selected == "Preprocessing":
        preprocessing.show(artifacts)
    elif selected == "K-Means":
        kmeans.show(artifacts)
    elif selected == "K-Medoids":
        kmedoids.show(artifacts)
    elif selected == "Perbandingan":
        perbandingan.show(artifacts)
    elif selected == "Hasil Akhir":
        hasil_akhir.show(artifacts)


if __name__ == "__main__":
    main()
