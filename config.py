import streamlit as st

# =====================================================================
# PALETTE WARNA (TEMA VISUAL APLIKASI REDESIGN)
# =====================================================================
PALETTE = {
    "primary": "#1E3A8A",        # Deep Blue
    "primary_dark": "#172554",   # Very Dark Deep Blue
    "primary_light": "#EFF6FF",  # Soft Blue highlight
    "secondary": "#2563EB",      # Royal Blue
    "accent": "#38BDF8",         # Sky Accent
    "kmeans": "#2563EB",         # K-Means (Secondary Blue)
    "kmedoids": "#F59E0B",       # K-Medoids (Gold/Amber)
    "gold": "#F59E0B",           # Gold/Amber
    "success": "#22C55E",        # Emerald Success
    "bg": "#F8FAFC",             # Slate BG
    "card": "#FFFFFF",           # Pure White Card
    "text": "#0F172A",           # Slate Dark Text
    "muted": "#64748B",          # Slate Muted Text
    "border": "#E2E8F0",         # Border Light Slate
}

# =====================================================================
# CUSTOM CSS INJECTION
# =====================================================================
def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700;9..144,800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        /* --- GLOBAL FONTS & STYLES --- */
        html, body, [class*="css"], section[data-testid="stSidebar"] * {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            color: {PALETTE['text']};
        }}

        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}
        
        .stApp {{ 
            background-color: {PALETTE['bg']}; 
        }}

        /* --- CUSTOM SCROLLBAR --- */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #F1F5F9;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #CBD5E1;
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #94A3B8;
        }}

        /* --- SIDEBAR --- */
        section[data-testid="stSidebar"] {{
            background-color: {PALETTE['card']} !important;
            border-right: 1px solid {PALETTE['border']} !important;
            box-shadow: 4px 0 24px rgba(15, 23, 42, 0.02) !important;
        }}

        /* --- TYPOGRAPHY --- */
        h1, h2, h3, h4, h5, h6 {{
            color: {PALETTE['text']} !important;
            font-family: 'Fraunces', serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }}

        /* --- HERO --- */
        .hero-box {{
            position: relative;
            background: linear-gradient(135deg, {PALETTE['primary']} 0%, {PALETTE['secondary']} 60%, #1D4ED8 100%);
            padding: 2rem 2.5rem;
            border-radius: 24px;
            color: white;
            margin-bottom: 1.5rem;
            overflow: hidden;
            box-shadow: 0 20px 40px -15px rgba(30, 58, 138, 0.3), 0 0 50px -10px rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }}
        .hero-box::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            opacity: 0.18;
            background-image: 
                radial-gradient(at 10% 20%, {PALETTE['accent']} 0px, transparent 40%),
                radial-gradient(at 90% 30%, {PALETTE['gold']} 0px, transparent 40%),
                radial-gradient(at 50% 80%, {PALETTE['secondary']} 0px, transparent 50%);
            filter: blur(40px);
            pointer-events: none;
        }}
        .hero-box::after {{
            content: "";
            position: absolute;
            top: 0; right: 0;
            width: 100%; height: 100%;
            opacity: 0.05;
            pointer-events: none;
            background-image: radial-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 0), radial-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 0);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
        }}
        .hero-box h1 {{
            color: white !important;
            margin-bottom: 0.3rem;
            font-size: 2.2rem;
            font-weight: 800;
        }}
        .hero-box p {{ 
            color: #E2E8F0 !important; 
            margin: 0; 
            font-size: 1rem; 
            line-height: 1.7;
            max-width: 70%; 
        }}

        /* --- CARDS (GLOBAL OVERRIDES) --- */
        .ci-card {{
            background-color: {PALETTE['card']} !important;
            border: 1px solid {PALETTE['border']} !important;
            border-radius: 22px !important;
            padding: 1.8rem 1.6rem !important;
            box-shadow: 0 4px 20px -2px rgba(148, 163, 184, 0.06), 0 2px 8px -1px rgba(148, 163, 184, 0.04) !important;
            margin-bottom: 1rem !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            position: relative !important;
            overflow: hidden !important;
            animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }}
        .ci-card:hover {{
            transform: translateY(-5px) !important;
            box-shadow: 0 20px 25px -5px rgba(30, 41, 59, 0.08), 0 10px 10px -5px rgba(30, 41, 59, 0.03) !important;
            border-color: {PALETTE['accent']} !important;
        }}

        /* --- STREAMLIT CONTAINER BORDER CARDS --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {PALETTE['card']} !important;
            border: 1px solid {PALETTE['border']} !important;
            border-radius: 22px !important;
            padding: 1.6rem !important;
            box-shadow: 0 4px 20px -2px rgba(148, 163, 184, 0.06), 0 2px 8px -1px rgba(148, 163, 184, 0.04) !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 20px 25px -5px rgba(30, 41, 59, 0.07), 0 10px 10px -5px rgba(30, 41, 59, 0.03) !important;
            border-color: {PALETTE['accent']} !important;
        }}

        /* --- BADGES --- */
        .badge-success {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background-color: rgba(34, 197, 94, 0.12) !important;
            color: #22C55E !important;
            border: 1px solid rgba(34, 197, 94, 0.25) !important;
            padding: 0.4rem 1rem !important;
            border-radius: 9999px !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.05) !important;
        }}
        .badge-success::before {{
            content: "";
            display: inline-block;
            width: 6px;
            height: 6px;
            background-color: #22C55E;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        
        .badge-pending {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background-color: rgba(245, 158, 11, 0.12) !important;
            color: #F59E0B !important;
            border: 1px solid rgba(245, 158, 11, 0.25) !important;
            padding: 0.4rem 1rem !important;
            border-radius: 9999px !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.05) !important;
        }}

        .feature-tag {{
            display: inline-block; 
            background-color: rgba(37, 99, 235, 0.08); 
            color: {PALETTE['primary']};
            padding: 0.35rem 0.8rem; 
            border-radius: 8px; 
            font-weight: 600; 
            font-size: 0.78rem;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid rgba(37, 99, 235, 0.15);
        }}

        /* --- BUTTONS --- */
        .stButton > button, .stDownloadButton > button {{
            background: linear-gradient(135deg, {PALETTE['secondary']} 0%, {PALETTE['primary']} 100%) !important;
            color: white !important; 
            border-radius: 9999px !important; 
            border: none !important;
            padding: 0.65rem 1.8rem !important; 
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.25) !important;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
            cursor: pointer !important;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{ 
            background: linear-gradient(135deg, #1D4ED8 0%, {PALETTE['primary']} 100%) !important;
            transform: translateY(-2px) !important; 
            box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.35) !important;
            color: white !important;
        }}
        .stButton > button:active, .stDownloadButton > button:active {{
            transform: translateY(0) !important;
        }}
        .stButton > button:focus, .stDownloadButton > button:focus {{
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.5) !important;
            outline: none !important;
        }}

        /* --- SECTION TITLE --- */
        .section-title {{
            border-left: 4px solid {PALETTE['secondary']} !important;
            padding-left: 0.8rem !important;
            margin: 2.2rem 0 1.2rem 0 !important;
        }}
        .section-title h2 {{ 
            margin: 0 !important;
            font-size: 1.6rem !important;
            font-family: 'Fraunces', serif !important;
            color: {PALETTE['primary']} !important;
        }}

        /* --- CONCLUSION & ALERT CARDS --- */
        .conclusion-card {{
            background: linear-gradient(135deg, rgba(239, 246, 255, 0.6) 0%, rgba(219, 234, 254, 0.4) 100%) !important;
            border: 1px solid rgba(191, 219, 254, 0.8) !important;
            border-left: 4px solid {PALETTE['gold']} !important;
            border-radius: 18px !important;
            padding: 1.6rem 1.8rem !important;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.01) !important;
            margin-top: 1rem !important;
        }}

        /* --- ST EXPANDER --- */
        div[data-testid="stExpander"] {{
            border: 1px solid {PALETTE['border']} !important;
            border-radius: 16px !important;
            background-color: {PALETTE['card']} !important;
            box-shadow: 0 4px 12px rgba(148, 163, 184, 0.03) !important;
            margin-bottom: 1rem !important;
        }}

        /* --- ST TABS --- */
        div[data-testid="stTabBar"] {{
            border-bottom: 1px solid {PALETTE['border']} !important;
            gap: 1.5rem !important;
        }}
        button[data-baseweb="tab"] {{
            background-color: transparent !important;
            border: none !important;
            color: {PALETTE['muted']} !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            padding: 0.75rem 0.5rem !important;
            transition: all 0.2s ease !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {PALETTE['secondary']} !important;
            border-bottom: 2px solid {PALETTE['secondary']} !important;
        }}

        /* --- ANIMATIONS KEYFRAMES --- */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulse {{
            0% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }}
            70% {{ transform: scale(1.1); box-shadow: 0 0 0 5px rgba(34, 197, 94, 0); }}
            100% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def card_html(title, value, subtitle="", icon="📌"):
    # Penentuan warna background dan teks ikon berdasarkan icon emoji
    icon_bg = "rgba(37, 99, 235, 0.08)"
    icon_color = "#2563EB"
    
    if icon in ["🏆", "👑"]:
        icon_bg = "rgba(245, 158, 11, 0.08)"
        icon_color = "#F59E0B"
    elif icon in ["✅", "✔", "🟢", "🔷"]:
        icon_bg = "rgba(34, 197, 94, 0.08)"
        icon_color = "#22C55E"
    elif icon in ["⚠️", "🟠", "🎯"]:
        icon_bg = "rgba(249, 115, 22, 0.08)"
        icon_color = "#F97316"
    elif icon in ["🧬", "🔵", "⚙️", "🛠️", "📊"]:
        icon_bg = "rgba(56, 189, 248, 0.08)"
        icon_color = "#0284C7"
        
    return f"""
    <div class="ci-card">
        <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1.2rem;">
            <div style="display:flex; align-items:center; justify-content:center; width:2.75rem; height:2.75rem; border-radius:12px; background-color:{icon_bg}; font-size:1.4rem; color:{icon_color};">
                {icon}
            </div>
            <span style="font-family:'Plus Jakarta Sans', sans-serif; font-weight:600; color:{PALETTE['muted']}; font-size:0.85rem; letter-spacing:0.02em; text-transform:uppercase;">{title}</span>
        </div>
        <div style="font-size:2.2rem; font-weight:700; color:{PALETTE['text']}; font-family:'JetBrains Mono', monospace; margin-bottom:0.4rem; line-height:1.1;">{value}</div>
        <div style="color:{PALETTE['muted']}; font-size:0.8rem; font-weight:400;">{subtitle}</div>
    </div>
    """

def init_session_state():
    defaults = {
        "df_raw": None, "df_selected": None, "df_encoded": None, "df_renamed": None,
        "df_scaled": None, "X_scaled": None, "clustering_done": False, "kmeans_labels": None,
        "kmedoids_labels": None, "silhouette_kmeans": None, "silhouette_kmedoids": None,
        "pca_coords": None, "pca_centroids_kmeans": None, "pca_medoids_kmedoids": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
