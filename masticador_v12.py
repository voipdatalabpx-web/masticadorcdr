import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import io, re
from pathlib import Path

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DARWIN CDR Analytics",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts: Syncopate (section titles only) — body/UI uses Arial ── */
@import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Orbitron:wght@400;500;700&display=swap');

/* ── Root tokens ── */
:root {
  --font-title:    'Syncopate', 'Orbitron', monospace;
  --font-ui:       Arial, Helvetica, sans-serif;
  --font-mono:     Arial, Helvetica, sans-serif;
  --c-bg:          #020b18;
  --c-card:        #041625;
  --c-border:      #0d3a5e;
  --c-cyan:        #00d4ff;
  --c-cyan-dim:    #006e84;
  --c-text:        #d0e8f8;
  --c-muted:       #2e5f7e;
  --c-green:       #00ff88;
  --c-yellow:      #ffcc00;
  --c-orange:      #ff6b35;
  --c-red:         #ff2d55;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--c-bg) !important;
  color: var(--c-text) !important;
  font-family: Arial, Helvetica, sans-serif !important;
  font-weight: 300 !important;
}
[data-testid="stSidebar"] {
  background: #030e1f !important;
  border-right: 1px solid var(--c-border) !important;
  font-family: Arial, Helvetica, sans-serif !important;
}

/* ══ HEADER ══════════════════════════════════════════════════ */
.main-title {
  font-family: var(--font-title);
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--c-cyan);
  text-shadow: 0 0 24px #00d4ff66, 0 0 60px #00d4ff22;
  letter-spacing: 10px;
  text-transform: uppercase;
  text-align: center;
  margin-bottom: 0;
}
.sub-title {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 300;
  color: var(--c-muted);
  text-align: center;
  letter-spacing: 12px;
  text-transform: uppercase;
  margin-top: 6px;
  margin-bottom: 18px;
}

/* ══ KPI CARDS ═══════════════════════════════════════════════ */
.kpi-card {
  background: linear-gradient(160deg, #041625 0%, #051b2c 100%);
  border: 1px solid var(--c-border);
  border-top: 1px solid var(--c-cyan-dim);
  border-radius: 4px;
  padding: 14px 10px 12px;
  text-align: center;
  position: relative;
  overflow: hidden;
  margin-bottom: 4px;
}
/* subtle scan-line shimmer on top edge */
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--c-cyan), transparent);
  opacity: 0.7;
}
.kpi-desc {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  font-weight: 300;
  color: var(--c-muted);
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.kpi-value {
  font-family: var(--font-mono);
  font-size: 1.55rem;
  font-weight: 300;
  color: #ffffff;
  letter-spacing: 2px;
  line-height: 1.1;
}
.kpi-sub {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  font-weight: 300;
  color: var(--c-muted);
  margin-top: 5px;
  letter-spacing: 1px;
}
.kpi-warn    { color: var(--c-orange) !important; }
.kpi-ok      { color: var(--c-green)  !important; }
.kpi-caution { color: var(--c-yellow) !important; }

/* ══ META BAR ════════════════════════════════════════════════ */
.meta-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0;
  background: #030f20;
  border: 1px solid var(--c-border);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}
.meta-cell {
  padding: 14px 16px;
  border-right: 1px solid var(--c-border);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.meta-cell:last-child { border-right: none; }
.meta-label {
  font-family: var(--font-mono);
  font-weight: 300;
  font-size: 0.55rem;
  color: var(--c-muted);
  letter-spacing: 4px;
  text-transform: uppercase;
}
.meta-value {
  font-family: var(--font-mono);
  font-weight: 400;
  font-size: 0.92rem;
  color: #ffffff;
  letter-spacing: 1px;
}

/* ══ SECTION HEADERS ═════════════════════════════════════════ */
.section-header {
  font-family: var(--font-title);
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--c-cyan);
  letter-spacing: 6px;
  text-transform: uppercase;
  border-bottom: 1px solid var(--c-border);
  padding-bottom: 8px;
  margin: 24px 0 14px 0;
}

/* ══ INSIGHT BOXES ═══════════════════════════════════════════ */
.insight-box {
  background: linear-gradient(135deg, #041625, #061e30);
  border: 1px solid var(--c-border);
  border-left: 2px solid var(--c-cyan);
  border-radius: 2px;
  padding: 12px 16px;
  margin: 6px 0;
  font-family: var(--font-ui);
  font-size: 0.85rem;
  font-weight: 300;
  color: #a8cce0;
  line-height: 1.6;
}
.insight-warn {
  border-left-color: var(--c-orange);
  background: linear-gradient(135deg, #140700, #0c0300);
  color: #f0b090;
}
.insight-ok {
  border-left-color: var(--c-green);
  background: linear-gradient(135deg, #001508, #000e05);
  color: #80f0b8;
}
.insight-title {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  font-weight: 400;
  letter-spacing: 4px;
  text-transform: uppercase;
  margin-bottom: 6px;
  color: inherit;
  opacity: 0.8;
}

/* ══ ASR BADGE ═══════════════════════════════════════════════ */
.asr-badge {
  display: inline-block;
  border-radius: 2px;
  padding: 2px 10px;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 400;
  letter-spacing: 2px;
  margin-right: 6px;
}
.asr-ok   { background: #002a12; color: var(--c-green);  border: 1px solid #005522; }
.asr-warn { background: #2a0e00; color: var(--c-orange); border: 1px solid #662200; }
.asr-crit { background: #1e0008; color: var(--c-red);    border: 1px solid #550011; }

/* ══ GLOBAL OVERRIDES ════════════════════════════════════════ */
h1, h2, h3 {
  font-family: var(--font-title) !important;
  color: var(--c-cyan) !important;
  letter-spacing: 4px !important;
}
.stButton > button {
  background: linear-gradient(135deg, #041625, #0a2e4a) !important;
  border: 1px solid var(--c-cyan-dim) !important;
  color: var(--c-cyan) !important;
  font-family: var(--font-mono) !important;
  font-weight: 300 !important;
  letter-spacing: 4px !important;
  font-size: 0.72rem !important;
  padding: 10px 28px !important;
  border-radius: 2px !important;
  text-transform: uppercase !important;
}
.stButton > button:hover {
  border-color: var(--c-cyan) !important;
  box-shadow: 0 0 16px #00d4ff22 !important;
}
div[data-testid="metric-container"] {
  background: var(--c-card) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: 4px !important;
}
/* Make Streamlit native text inputs/selects use Arial */
input, select, textarea, [data-baseweb="input"] input {
  font-family: Arial, Helvetica, sans-serif !important;
  font-weight: 300 !important;
}
/* Sidebar labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown {
  font-family: Arial, Helvetica, sans-serif !important;
  font-weight: 300 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Paths ────────────────────────────────────────────────────────────────────
# SCRIPT_DIR = directorio donde vive este .py (funciona local y en Streamlit Cloud)
SCRIPT_DIR = Path(__file__).parent

# Paths Windows locales (se usan si existen, ej: entorno de desarrollo local)
_LOCAL_CDR = Path(r"C:\Users\rdangelo\reportes_python_2026\analitycs_cdrs_darwin\datos_cdr_darwin")
_LOCAL_TMP = Path(r"C:\Users\rdangelo\reportes_python_2026\analitycs_cdrs_darwin\tmp_darwin")

# En Streamlit Cloud los paths Windows no existen → usa paths relativos al repo
CDR_FOLDER     = _LOCAL_CDR if _LOCAL_CDR.exists() else SCRIPT_DIR / "datos_cdr_darwin"
TMP_FOLDER     = _LOCAL_TMP if _LOCAL_TMP.exists() else SCRIPT_DIR / "tmp_darwin"
MAESTRO_FOLDER = TMP_FOLDER

# ─── Causa map ───────────────────────────────────────────────────────────────
CAUSA_MAP = {
    1:  ("Unallocated Number",         "Número no asignado / inválido",       "error"),
    2:  ("No Route to Destination",    "Sin ruta al destino",                  "error"),
    3:  ("No Route to Transit",        "Sin ruta de tránsito",                 "error"),
    6:  ("Channel Unacceptable",       "Canal no aceptable",                   "warning"),
    16: ("Normal Clearing",            "Corte normal",                         "normal"),
    17: ("User Busy",                  "Número ocupado",                       "warning"),
    18: ("No User Responding",         "Sin respuesta — timeout ring",         "warning"),
    19: ("No Answer",                  "Sin contestación",                     "warning"),
    20: ("Subscriber Absent",          "Abonado ausente / apagado",            "warning"),
    21: ("Call Rejected",              "Llamada rechazada",                    "warning"),
    22: ("Number Changed",             "Número cambiado",                      "error"),
    27: ("Destination Out of Order",   "Destino fuera de servicio",            "error"),
    28: ("Invalid Number Format",      "Formato de número inválido",           "error"),
    31: ("Normal Unspecified",         "Corte normal sin especificar",         "normal"),
    34: ("No Circuit Available",       "Sin circuito — CONGESTIÓN",            "congestion"),
    38: ("Network Out of Order",       "Red fuera de servicio",                "error"),
    41: ("Temporary Failure",          "Falla temporal de red",                "warning"),
    42: ("Switching Equip Congestion", "Congestión switching",                 "congestion"),
    44: ("Requested Circuit Unavail",  "Circuito no disponible",               "congestion"),
    47: ("Resources Unavailable",      "Recursos no disponibles",              "congestion"),
    50: ("Facility Not Subscribed",    "Servicio no suscripto",                "error"),
    55: ("Incoming Calls Barred",      "Llamadas entrantes bloqueadas",        "error"),
    57: ("Bearer Cap Not Auth",        "Cap. portadora no autorizada",         "error"),
    58: ("Bearer Cap Unavailable",     "Cap. portadora no disponible",         "warning"),
    65: ("Bearer Cap Not Impl.",       "Cap. portadora no implementada",       "error"),
    79: ("Not Implemented Unspec",     "No implementado sin especificar",      "error"),
    87: ("User Not Member CUG",        "Usuario no miembro grupo cerrado",     "error"),
    88: ("Incompatible Destination",   "Destino incompatible",                 "error"),
    95: ("Invalid Message",            "Mensaje inválido",                     "error"),
    96: ("Mandatory IE Missing",       "IE obligatorio faltante",              "error"),
    97: ("Message Type Non-Existent",  "Tipo de mensaje inexistente",          "error"),
    100:("Invalid IE Contents",        "Contenido de IE inválido",             "error"),
    101:("Wrong Message State",        "Estado de mensaje incorrecto",         "error"),
    102:("Recovery on Timer Expiry",   "Recovery por timeout — PL/RTT/Jitter","packet_loss"),
    111:("Protocol Error Unspecified", "Error de protocolo sin especificar",   "error"),
    127:("Interworking Unspecified",   "Error de interworking",                "error"),
}

# Causas que se excluyen para ASR Real (causa, disc)
ASR_REAL_EXCL = {
    (16,  "Orig."),
    (1,   "Dest."),
    (17,  "Dest."),
    (18,  "Dest."),
    (19,  "Dest."),
    (20,  "Dest."),
    (22,  "Dest."),
    (27,  "Dest."),
    (28,  "Dest."),
    (102, "Dest."),
}

CAT_COLORS = {
    "normal":      "#00ff88",
    "congestion":  "#ff6b35",
    "error":       "#ff2d55",
    "warning":     "#ffcc00",
    "packet_loss": "#a855f7",
    "other":       "#3a7ca5",
}

C = dict(
    bg="#020b18", card="#041625", border="#0d3a5e",
    cyan="#00d4ff", green="#00ff88", yellow="#ffcc00",
    orange="#ff6b35", red="#ff2d55", purple="#a855f7",
    text="#c8e6ff", muted="#3a7ca5",
)

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#020f1c",
    font=dict(family="Arial, Helvetica, sans-serif", color=C["text"], size=11),
    xaxis=dict(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", linecolor="#0d3a5e",
               tickfont=dict(family="Arial, Helvetica, sans-serif", size=10)),
    yaxis=dict(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", linecolor="#0d3a5e",
               tickfont=dict(family="Arial, Helvetica, sans-serif", size=10)),
    margin=dict(l=40, r=20, t=45, b=40),
)

# ─── Helpers ─────────────────────────────────────────────────────────────────
def fmt_n(n, d=0):
    if d == 0: return f"{int(n):,}".replace(",", ".")
    return f"{n:,.{d}f}".replace(",","X").replace(".",",").replace("X",".")

def asr_badge(val, label="ASR"):
    cls = "asr-ok" if val >= 50 else ("asr-warn" if val >= 20 else "asr-crit")
    return f'<span class="asr-badge {cls}">{label}: {val:.2f}%</span>'

def kpi_card(desc, value, sub=None, cls=""):
    sub_html = f'<div class="kpi-sub {cls}">{sub}</div>' if sub else ""
    return (f'<div class="kpi-card">'
            f'<div class="kpi-desc">{desc}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'{sub_html}</div>')

def section(t):
    st.markdown(f'<div class="section-header">▸ {t}</div>', unsafe_allow_html=True)

def insight(title, text, kind="info"):
    cls  = "insight-warn" if kind=="warn" else ("insight-ok" if kind=="ok" else "")
    icon = "⚠️" if kind=="warn" else ("✅" if kind=="ok" else "📡")
    st.markdown(
        f'<div class="insight-box {cls}">'
        f'<div class="insight-title">{icon} {title}</div>{text}</div>',
        unsafe_allow_html=True)

def pl(extra=None):
    l = {**BASE_LAYOUT}
    if extra: l.update(extra)
    return l

# ─── TMP prefix loader ───────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_tmp_master(raw: bytes) -> dict:
    """Load TMP master file (comma-sep, with leading 0 on prefixes).
    Handles malformed rows where digits+city name are merged in Prefijo column.
    Builds exact + longest-prefix lookup.
    """
    df = pd.read_csv(io.BytesIO(raw), sep=",", on_bad_lines="skip", low_memory=False)
    df.columns = df.columns.str.strip()

    # Fix rows where digits and city name are merged: '023615450JUNIN (PROV...)' -> split
    def fix_row(row):
        pref = str(row.get("Prefijo","")).strip()
        desc = str(row.get("Descripcion","")).strip()
        mod  = str(row.get("Modalidad","")).strip() if pd.notna(row.get("Modalidad")) else ""
        # Match digits followed by any non-digit characters (city names may have spaces, dots, parens)
        m = re.match(r"^(\d+)([A-Za-z].*)$", pref)
        if m:
            return pd.Series({"Prefijo": m.group(1), "Descripcion": m.group(2).strip(), "Modalidad": desc})
        return pd.Series({"Prefijo": pref, "Descripcion": desc, "Modalidad": mod})

    df = df.apply(fix_row, axis=1)
    # Keep only numeric keys, strip leading zeros, deduplicate
    df["Prefijo_key"] = df["Prefijo"].str.lstrip("0")
    df = df[df["Prefijo_key"].str.match(r"^\d+$", na=False)]
    df = df.drop_duplicates("Prefijo_key")

    desc_dict  = dict(zip(df["Prefijo_key"], df["Descripcion"]))
    modal_dict = dict(zip(df["Prefijo_key"], df["Modalidad"]))

    # Pre-sort by key length descending for longest-prefix matching
    sorted_keys = sorted(desc_dict.keys(), key=len, reverse=True)

    return {
        "desc":        desc_dict,
        "modal":       modal_dict,
        "sorted_keys": sorted_keys,
    }


def tmp_lookup(pref_str: str, pm: dict) -> tuple:
    """Lookup prefix in TMP master. Returns (descripcion, modalidad).
    Strategy: 1) exact match  2) longest-prefix (CDR starts with TMP key)
              3) reverse prefix (TMP key starts with CDR num)  4) fallback label
    """
    if pm is None:
        return pref_str, "N/D"

    desc_d  = pm["desc"]
    modal_d = pm["modal"]
    skeys   = pm["sorted_keys"]
    num     = str(pref_str).strip()

    # 1. Exact match
    if num in desc_d:
        return desc_d[num], modal_d.get(num, "N/D")

    # 2. Longest prefix: CDR number starts with TMP key (TMP key is prefix of CDR num)
    for k in skeys:
        if len(k) >= 5 and num.startswith(k):
            return desc_d[k], modal_d.get(k, "N/D")

    # 3. Reverse: TMP key starts with CDR number (CDR num is shorter prefix of key)
    for k in skeys:
        if len(num) >= 5 and k.startswith(num):
            return desc_d[k], modal_d.get(k, "N/D")

    # 4. Special / unknown
    if num in ("7009801001","70096001") or num.startswith("700"):
        return "Número Especial / Prueba", "N/A"
    return f"Desconocido ({num[:6]}...)", "N/D"

# ─── CDR loader ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_cdr(raw: bytes, pm_raw: bytes | None) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(raw), sep=";", low_memory=False)
    df.columns = df.columns.str.strip()

    for col in ["Fecha Inicio","Fecha Alert","Fecha Conexion","Fecha Desconexion"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df["Durac.Seg Total"] = pd.to_numeric(df["Durac.Seg Total"], errors="coerce").fillna(0)
    df["Causa"]           = pd.to_numeric(df["Causa"], errors="coerce").fillna(0).astype(int)
    df["Disc"]            = df["Disc"].fillna("").str.strip()

    # Connection flags
    df["is_connected"]  = df["Fecha Conexion"].notna() & (df["Durac.Seg Total"] > 0)
    df["has_ringback"]  = df["Fecha Alert"].notna() & ~df["is_connected"]
    df["not_connected"] = ~df["is_connected"]
    df["duration_min"]  = df["Durac.Seg Total"] / 60

    # ASR Real exclusion flag
    excl_mask = df.apply(
        lambda r: (int(r["Causa"]), r["Disc"]) in ASR_REAL_EXCL, axis=1
    )
    df["excl_asr_real"] = excl_mask

    df["proveedor"] = df["Carrier Destino"].fillna("Desconocido").str.strip()
    df["ruta_dest"] = df["Ruta Dest"].fillna("Desconocida").str.strip()
    df["pref_str"]  = df["Prefijo Dest"].astype(str).str.strip()
    df["causa_cat"] = df["Causa"].map(lambda x: CAUSA_MAP.get(x, ("","","other"))[2])

    # Mobile / Fijo from CDR prefix
    p = df["pref_str"]
    df["traffic_type"] = np.where(
        p.str.startswith("115") | p.str.startswith("116") | p.str.startswith("113"),
        "Móvil", "Fijo"
    )

    # Destination name from TMP master using longest-prefix lookup
    if pm_raw:
        pm = load_tmp_master(pm_raw)
        df[["dest_nombre","dest_modal"]] = df["pref_str"].apply(
            lambda p: pd.Series(tmp_lookup(p, pm))
        )
    else:
        df["dest_nombre"] = df["pref_str"]
        df["dest_modal"]  = "N/D"

    return df

# ─── File discovery ───────────────────────────────────────────────────────────
def discover_files(cdr_folder: Path, maestro_folder: Path = None):
    """CDR = único .csv en cdr_folder. Maestro = primer .csv en maestro_folder."""
    cdr = None
    if cdr_folder.exists():
        cdrs = [f for f in cdr_folder.glob("*.csv")]
        cdr  = sorted(cdrs, key=lambda f: f.stat().st_mtime, reverse=True)[0] if cdrs else None

    maestro = None
    mfolder = maestro_folder if maestro_folder else cdr_folder
    if mfolder.exists():
        candidates = [f for f in mfolder.glob("*.csv")
                      if f.name.lower().startswith("maestro")]
        if not candidates:
            # Fallback: any csv in maestro folder that is NOT the CDR
            candidates = [f for f in mfolder.glob("*.csv")
                          if cdr is None or f != cdr]
        maestro = sorted(candidates, key=lambda f: f.stat().st_mtime, reverse=True)[0] if candidates else None

    return cdr, maestro

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">📡 DARWIN CDR ANALYTICS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">IPLAN · PLATAFORMA DE ANÁLISIS DE TRÁFICO EN TIEMPO REAL</div>', unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;color:#00d4ff;letter-spacing:4px;'
                'font-size:0.65rem;margin-bottom:10px;text-transform:uppercase;">📁 CONFIGURACIÓN</div>', unsafe_allow_html=True)

    cdr_folder_str     = st.text_input("Carpeta datos CDR",       value=str(CDR_FOLDER))
    maestro_folder_str = st.text_input("Carpeta TMP (Maestro)",   value=str(MAESTRO_FOLDER))
    tmp_folder_str     = st.text_input("Carpeta temporal (PDF)",  value=str(TMP_FOLDER))
    cdr_folder    = Path(cdr_folder_str)
    maestro_folder= Path(maestro_folder_str)
    tmp_folder    = Path(tmp_folder_str)

    raw_cdr = raw_maestro = None
    cdr_name = maestro_name = ""

    cdr_path, maestro_path = discover_files(cdr_folder, maestro_folder)

    if cdr_path:
        st.markdown(f'<div style="color:#00ff88;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.65rem;margin-top:6px;">'
                    f'✓ CDR: {cdr_path.name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#2e5f7e;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.6rem;">'
                    f'🕐 {pd.Timestamp(cdr_path.stat().st_mtime,unit="s").strftime("%Y-%m-%d %H:%M")} '
                    f'· {cdr_path.stat().st_size/1024:.0f} KB</div>', unsafe_allow_html=True)
        with open(cdr_path,"rb") as f: raw_cdr = f.read()
        cdr_name = cdr_path.name
    else:
        st.markdown('<div style="color:#ff6b35;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.65rem;">⚠ Sin CDR en carpeta</div>',
                    unsafe_allow_html=True)

    if maestro_path:
        st.markdown(f'<div style="color:#ffcc00;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.65rem;margin-top:2px;">'
                    f'📋 Maestro: {maestro_path.name}</div>', unsafe_allow_html=True)
        with open(maestro_path,"rb") as f: raw_maestro = f.read()
        maestro_name = maestro_path.name
    else:
        st.markdown('<div style="color:#2e5f7e;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.65rem;margin-top:2px;">'
                    'ℹ Sin maestro de prefijos</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;color:#2e5f7e;font-size:0.6rem;'
                'margin:10px 0 3px;letter-spacing:3px;">— SUBIR MANUALMENTE —</div>', unsafe_allow_html=True)
    up_cdr = st.file_uploader("CDR (.csv)",     type=["csv"], key="up_cdr", label_visibility="collapsed")
    up_mae = st.file_uploader("Maestro (.csv)", type=["csv"], key="up_mae", label_visibility="collapsed")
    if up_cdr: raw_cdr = up_cdr.read(); cdr_name = up_cdr.name
    if up_mae: raw_maestro = up_mae.read(); maestro_name = up_mae.name

    # ── Entorno: detectar si estamos en Streamlit Cloud o local ──
    is_cloud = not _LOCAL_CDR.exists()
    if is_cloud:
        st.markdown(
            '<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.6rem;'
            'color:#ffcc00;background:#1a1000;border:1px solid #443300;border-radius:2px;'
            'padding:4px 8px;margin-bottom:6px;">☁ STREAMLIT CLOUD — paths relativos al repo</div>',
            unsafe_allow_html=True)

    # Demo / repo fallback: busca en paths relativos al repo y en uploads (dev)
    if raw_cdr is None:
        fallback_cdr_paths = [
            SCRIPT_DIR / "datos_cdr_darwin",   # carpeta en el repo
        ]
        for folder in fallback_cdr_paths:
            if folder.exists():
                cdrs = sorted(folder.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
                if cdrs:
                    with open(cdrs[0],"rb") as f: raw_cdr = f.read()
                    cdr_name = cdrs[0].name
                    st.markdown(f'<div style="color:#00ff88;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.65rem;">✓ CDR auto: {cdr_name}</div>',
                                unsafe_allow_html=True)
                    break

    if raw_maestro is None:
        # Buscar en tmp_darwin del repo primero, luego por nombre en el mismo repo
        maestro_search = [
            SCRIPT_DIR / "tmp_darwin",
            SCRIPT_DIR,
        ]
        for folder in maestro_search:
            if folder.exists():
                candidates = sorted(folder.glob("Maestro*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
                if not candidates:
                    candidates = sorted(folder.glob("maestro*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
                if candidates:
                    with open(candidates[0],"rb") as f: raw_maestro = f.read()
                    maestro_name = candidates[0].name
                    st.markdown(f'<div style="color:#ffcc00;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.65rem;">📋 Maestro auto: {maestro_name}</div>',
                                unsafe_allow_html=True)
                    break

    st.markdown("---")
    st.markdown('<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;color:#00d4ff;letter-spacing:4px;'
                'font-size:0.62rem;margin-bottom:8px;text-transform:uppercase;">FILTROS</div>', unsafe_allow_html=True)

if raw_cdr is None:
    st.info("📂 No se encontró ningún CDR. Verificá la carpeta o subí el archivo manualmente.")
    st.stop()

df = load_cdr(raw_cdr, raw_maestro)

with st.sidebar:
    provs    = sorted(df["proveedor"].unique())
    rutas    = sorted(df["ruta_dest"].unique())
    tipos    = sorted(df["traffic_type"].unique())
    sel_prov = st.multiselect("Proveedor destino", provs, default=provs)
    sel_ruta = st.multiselect("Ruta destino",      rutas, default=rutas)
    sel_tipo = st.multiselect("Tipo destino",       tipos, default=tipos)

mask = (df["proveedor"].isin(sel_prov) &
        df["ruta_dest"].isin(sel_ruta) &
        df["traffic_type"].isin(sel_tipo))
df = df[mask]
if df.empty:
    st.warning("Sin datos para los filtros seleccionados."); st.stop()

# ─── Core metrics ─────────────────────────────────────────────────────────────
total       = len(df)
connected   = int(df["is_connected"].sum())
ringback    = int(df["has_ringback"].sum())
no_conn     = int(df["not_connected"].sum())
tot_min     = df["duration_min"].sum()

# ASR Global: TLC / TL  (llamadas con duración > 0 / total)
asr_global  = connected / total * 100 if total else 0

# ASR Real: exclude specific (causa, disc) combos
df_real     = df[~df["excl_asr_real"]]
total_real  = len(df_real)
conn_real   = int(df_real["is_connected"].sum())
asr_real    = conn_real / total_real * 100 if total_real > 0 else 0
excl_count  = int(df["excl_asr_real"].sum())

t_span      = (df["Fecha Inicio"].max() - df["Fecha Inicio"].min()).total_seconds()
avg_cps     = total / t_span if t_span > 0 else 0
pm_ts       = df.groupby(df["Fecha Inicio"].dt.floor("1min")).size()
peak_cps    = pm_ts.max() / 60 if not pm_ts.empty else 0
mob_pct     = (df["traffic_type"]=="Móvil").sum() / total * 100 if total else 0

carrier_ent = df["Carrier Origen"].dropna().mode().iloc[0]  if not df["Carrier Origen"].dropna().empty  else "N/D"
ruta_ent    = df["Ruta Orig"].dropna().mode().iloc[0]       if not df["Ruta Orig"].dropna().empty        else "N/D"
fecha_cdr_s = df["Fecha Inicio"].min().strftime("%Y-%m-%d") if pd.notna(df["Fecha Inicio"].min())        else "N/D"
hora_prim   = df["Fecha Inicio"].min().strftime("%H:%M:%S") if pd.notna(df["Fecha Inicio"].min())        else "N/D"
hora_ult    = df["Fecha Inicio"].max().strftime("%H:%M:%S") if pd.notna(df["Fecha Inicio"].max())        else "N/D"

# ═══════════════════════════════════════════════════════════════════════════════
# PRE-CÁLCULO DE MÉTRICAS DE ANÁLISIS (necesarias para el semáforo)
# ═══════════════════════════════════════════════════════════════════════════════
causa_cnt = df["Causa"].value_counts().reset_index()
causa_cnt.columns = ["causa","count"]
causa_cnt["pct"] = (causa_cnt["count"]/total*100).round(1)
def enrich_causa(row):
    info = CAUSA_MAP.get(row["causa"], None)
    if info: return pd.Series({"nombre":info[0],"desc":info[1],"cat":info[2]})
    return pd.Series({"nombre":f"Causa {row['causa']}","desc":"Desconocida","cat":"other"})
causa_cnt = causa_cnt.join(causa_cnt.apply(enrich_causa, axis=1))

# Packet loss pre-calc
pl_causas = [102,41,38,34,44,47]
pl_df     = df[df["Causa"].isin(pl_causas)]
pl_total  = len(pl_df)
pl_pct    = pl_total/total*100 if total else 0
c102      = int((df["Causa"]==102).sum())
c41       = int((df["Causa"]==41).sum())
short_ok  = df[df["is_connected"] & (df["Durac.Seg Total"]>0) & (df["Durac.Seg Total"]<3)]
sc_total  = len(short_ok)
sc_pct    = sc_total/connected*100 if connected else 0

# Destino / proveedor pre-calc
dest_df = df.groupby(["dest_nombre","dest_modal"]).agg(
    llamadas  =("Causa","count"),
    conectadas=("is_connected","sum"),
    minutos   =("duration_min","sum"),
    excluidas =("excl_asr_real","sum"),
).reset_index()
dest_df["asr_global_d"] = (dest_df["conectadas"] / dest_df["llamadas"] * 100).round(2)
dest_df["llamadas_real"]= dest_df["llamadas"] - dest_df["excluidas"]
dest_df["asr_real_d"]   = np.where(
    dest_df["llamadas_real"] > 0,
    (dest_df["conectadas"] / dest_df["llamadas_real"] * 100).round(2), 0
)
dest_df["minutos"] = dest_df["minutos"].round(1)
dest_top = dest_df.sort_values("llamadas", ascending=False).head(30)

prov_df = df.groupby("proveedor").agg(
    llamadas  =("Causa","count"),
    conectadas=("is_connected","sum"),
    minutos   =("duration_min","sum"),
    excluidas =("excl_asr_real","sum"),
).reset_index()
prov_df["asr_global"] = (prov_df["conectadas"]/prov_df["llamadas"]*100).round(2)
prov_df["ll_real"]    = prov_df["llamadas"] - prov_df["excluidas"]
prov_df["asr_real"]   = np.where(
    prov_df["ll_real"]>0,
    (prov_df["conectadas"]/prov_df["ll_real"]*100).round(2), 0
)

ruta_df = df.groupby(["proveedor","ruta_dest"]).agg(
    llamadas  =("Causa","count"),
    conectadas=("is_connected","sum"),
    excluidas =("excl_asr_real","sum"),
).reset_index()
ruta_df["asr_global"] = (ruta_df["conectadas"]/ruta_df["llamadas"]*100).round(1)
ruta_df["ll_real"]    = ruta_df["llamadas"] - ruta_df["excluidas"]
ruta_df["asr_real"]   = np.where(
    ruta_df["ll_real"]>0,
    (ruta_df["conectadas"]/ruta_df["ll_real"]*100).round(1), 0
)

down = prov_df[(prov_df["asr_real"]<5)  & (prov_df["llamadas"]>=10)]
deg  = prov_df[(prov_df["asr_real"]>=5) & (prov_df["asr_real"]<30) & (prov_df["llamadas"]>=10)]

failed = df[~df["is_connected"]].copy()
failed["num_b"] = failed["Numero B Mod"].astype(str).str.replace(".0","",regex=False).str.strip()
retry = (failed.groupby("num_b")
    .agg(
        intentos   =("Causa","count"),
        causas_top =("Causa", lambda x: " | ".join([f"C{k}:{v}" for k,v in x.value_counts().head(3).items()])),
        causa_princ=("Causa", lambda x: CAUSA_MAP.get(int(x.mode().iloc[0]),("","Desconocida",""))[1] if len(x)>0 else "N/D"),
        proveedor  =("proveedor",   lambda x: x.mode().iloc[0] if len(x)>0 else "N/D"),
        dest_nombre=("dest_nombre", lambda x: x.mode().iloc[0] if len(x)>0 else "N/D"),
    )
    .reset_index()
    .sort_values("intentos",ascending=False)
)
max_retry  = retry["intentos"].iloc[0] if not retry.empty else 0
delta_asr  = asr_real - asr_global
cong_total = (df["causa_cat"]=="congestion").sum()
cong_pct   = cong_total/total*100 if total else 0
err_total  = int(causa_cnt[causa_cnt["cat"]=="error"]["count"].sum())
err_pct    = err_total/total*100 if total else 0
low_dest   = dest_df[(dest_df["asr_real_d"]<20) & (dest_df["llamadas"]>=30)]
top_causa_desc = causa_cnt.iloc[0]["desc"] if not causa_cnt.empty else "N/D"
top_causa_pct  = causa_cnt.iloc[0]["pct"]  if not causa_cnt.empty else 0
top_prov       = prov_df.sort_values("llamadas",ascending=False).iloc[0] if not prov_df.empty else None
top_dest       = dest_df.sort_values("llamadas",ascending=False).iloc[0] if not dest_df.empty else None
prov_conc      = top_prov["llamadas"]/total*100 if top_prov is not None else 0

# Build alert list for semaphore
alerts = []
if not down.empty:
    alerts.append(("crit", f"🔴 CARRIER CAÍDO — {', '.join(down['proveedor'].tolist())} (ASR Real &lt; 5%)"))
if asr_real < 30:
    alerts.append(("crit", f"🔴 ASR REAL CRÍTICO — {asr_real:.1f}% · causa dominante: {top_causa_desc}"))
elif asr_real < 50:
    alerts.append(("warn", f"🟡 ASR REAL BAJO — {asr_real:.1f}% (umbral operativo: 50%)"))
if peak_cps > 10:
    alerts.append(("warn", f"🟡 PICO CPS ELEVADO — peak {peak_cps:.2f} CPS"))
if cong_pct > 3:
    alerts.append(("warn", f"🟡 CONGESTIÓN — {fmt_n(int(cong_total))} llamadas ({cong_pct:.1f}%)"))
if c102 > 0 or pl_pct > 2:
    alerts.append(("warn", f"🟡 SÍNTOMAS PL/RTT — {pl_total} eventos · C102={c102}"))
if sc_pct > 5:
    alerts.append(("warn", f"🟡 LLAMADAS CORTAS &lt;3s — {sc_total} ({sc_pct:.1f}% conectadas)"))
if max_retry > 10:
    alerts.append(("warn", f"🟡 REINTENTOS — {retry['num_b'].iloc[0]} × {max_retry} intentos sin conexión"))
if not low_dest.empty:
    alerts.append(("warn", f"🟡 DESTINOS ASR BAJO &lt;20% — {', '.join(low_dest.head(3)['dest_nombre'].tolist())}"))
if err_pct > 10:
    alerts.append(("warn", f"🟡 ERRORES DE NÚMERO/RUTA — {err_pct:.1f}% del tráfico"))

n_crit = sum(1 for sev,_ in alerts if sev=="crit")
n_warn = sum(1 for sev,_ in alerts if sev=="warn")

if n_crit > 0:
    status_color, status_bg, status_label = "#ff2d55", "#160008", f"⛔  {n_crit} ALERTA{'S' if n_crit>1 else ''} CRÍTICA{'S' if n_crit>1 else ''}"
    if n_warn: status_label += f"  ·  {n_warn} ADVERTENCIA{'S' if n_warn>1 else ''}"
elif n_warn > 0:
    status_color, status_bg, status_label = "#ffcc00", "#100a00", f"⚠  {n_warn} ADVERTENCIA{'S' if n_warn>1 else ''} ACTIVA{'S' if n_warn>1 else ''}"
else:
    status_color, status_bg, status_label = "#00ff88", "#001508", "✓  SISTEMA NOMINAL"

# ═══════════════════════════════════════════════════════════════════════════════
# ▓▓ ZONA 1 — SEMÁFORO GLOBAL (lectura 3 segundos) ▓▓
# ═══════════════════════════════════════════════════════════════════════════════

# Meta bar
st.markdown(f"""
<div class="meta-grid">
  <div class="meta-cell">
    <div class="meta-label">Carrier Entrante</div>
    <div class="meta-value">{carrier_ent}</div>
  </div>
  <div class="meta-cell">
    <div class="meta-label">Ruta Entrante</div>
    <div class="meta-value">{ruta_ent}</div>
  </div>
  <div class="meta-cell">
    <div class="meta-label">Fecha CDR</div>
    <div class="meta-value">{fecha_cdr_s}</div>
  </div>
  <div class="meta-cell">
    <div class="meta-label">Hora Primer CDR</div>
    <div class="meta-value">{hora_prim}</div>
  </div>
  <div class="meta-cell">
    <div class="meta-label">Hora Último CDR</div>
    <div class="meta-value">{hora_ult}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Semáforo
alerts_html = "".join([
    f'<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.82rem;'
    f'color:{"#ff6060" if sev=="crit" else "#ffe066"};padding:3px 0;border-bottom:1px solid #0a2030;">{msg}</div>'
    for sev, msg in alerts
]) if alerts else '<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.82rem;color:#00ff88;">Sin alertas activas en este CDR.</div>'

st.markdown(f"""
<div style="display:flex;gap:12px;align-items:stretch;margin-bottom:10px;">
  <div style="flex:0 0 auto;background:{status_bg};border:1px solid {status_color};border-radius:4px;
              padding:16px 32px;display:flex;align-items:center;justify-content:center;min-width:280px;">
    <div style="font-family:Syncopate,monospace;font-weight:700;font-size:1.05rem;
                color:{status_color};letter-spacing:4px;text-align:center;text-transform:uppercase;">
      {status_label}
    </div>
  </div>
  <div style="flex:1;background:#030f20;border:1px solid #0a2030;border-radius:4px;padding:10px 16px;
              display:flex;flex-direction:column;gap:2px;">
    {alerts_html}
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ▓▓ ZONA 2 — KPIs AGRUPADOS POR ÁREA (lectura 30 segundos) ▓▓
# ═══════════════════════════════════════════════════════════════════════════════
section("ESTADO DEL TRÁFICO")

# ASR legend strip
st.markdown(
    f'<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.58rem;color:#2e5f7e;'
    f'padding:5px 14px;background:#030f20;border:1px solid #0a2030;border-radius:2px;'
    f'margin-bottom:10px;letter-spacing:0.5px;">'
    f'<b style="color:#00d4ff;font-weight:400;">ASR GLOBAL</b> = Llamadas con duración &gt;0 / Total '
    f'&nbsp;·&nbsp; '
    f'<b style="color:#00d4ff;font-weight:400;">ASR REAL</b> = Excluye C16-Orig y C1/17/18/19/20/22/27/28/102-Dest'
    f'</div>', unsafe_allow_html=True)

# Grupo A — Volumen de tráfico
st.markdown(
    '<div style="font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:300;'
    'color:#2e5f7e;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">'
    '▸ VOLUMEN</div>', unsafe_allow_html=True)
col_v = st.columns(4)
vol_kpis = [
    ("TOTAL RECIBIDAS", fmt_n(total),     None,                                    ""),
    ("CONECTADAS",      fmt_n(connected), f"{connected/total*100:.0f}% del total", "kpi-ok" if asr_global>=50 else "kpi-warn"),
    ("CON RINGBACK",    fmt_n(ringback),  f"{ringback/total*100:.0f}% del total",  ""),
    ("NO CONECTADAS",   fmt_n(no_conn),   f"{no_conn/total*100:.0f}% del total",   "kpi-warn" if no_conn/total>0.5 else ""),
]
for col,(desc,val,sub,cls) in zip(col_v, vol_kpis):
    col.markdown(kpi_card(desc,val,sub,cls), unsafe_allow_html=True)

st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

# Grupo B — Calidad + Capacidad + Red en una fila
col_q = st.columns(6)
mix_kpis = [
    ("ASR GLOBAL",       f"{asr_global:.2f}%", "TLC / TL",                            "kpi-ok" if asr_global>=50 else "kpi-warn"),
    ("ASR REAL",         f"{asr_real:.2f}%",   f"Excl. {fmt_n(excl_count)} llamadas", "kpi-ok" if asr_real>=50 else "kpi-warn"),
    ("CPS PROMEDIO",     f"{avg_cps:.2f}",      f"Peak {peak_cps:.2f} cps",           "kpi-warn" if peak_cps>10 else "kpi-ok"),
    ("CAUSAS RED/PL",    fmt_n(pl_total),       f"{pl_pct:.1f}% del total",            "kpi-warn" if pl_pct>2 else "kpi-ok"),
    ("CONGESTIÓN",       fmt_n(int(cong_total)),f"{cong_pct:.1f}% del total",          "kpi-warn" if cong_pct>3 else "kpi-ok"),
    ("CALLS &lt;3 SEG",  fmt_n(sc_total),       f"{sc_pct:.1f}% conectadas",           "kpi-warn" if sc_pct>5 else "kpi-ok"),
]
for col,(desc,val,sub,cls) in zip(col_q, mix_kpis):
    col.markdown(kpi_card(desc,val,sub,cls), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ▓▓ ZONA 3 — DIAGNÓSTICO RÁPIDO + ANÁLISIS DETALLADO EN TABS ▓▓
# ═══════════════════════════════════════════════════════════════════════════════
section("DIAGNÓSTICO AUTOMÁTICO")

# Insights compactos arriba de los tabs
def insight(title, text, kind="info"):
    cls  = "insight-warn" if kind=="warn" else ("insight-ok" if kind=="ok" else "")
    icon = "⚠️" if kind=="warn" else ("✅" if kind=="ok" else "📡")
    st.markdown(
        f'<div class="insight-box {cls}">'
        f'<div class="insight-title">{icon} {title}</div>{text}</div>',
        unsafe_allow_html=True)

# 1. ASR
insight("ASR GLOBAL vs ASR REAL",
    f"<b>ASR Global: {asr_global:.2f}%</b> · <b>ASR Real: {asr_real:.2f}%</b> "
    f"(diferencia: +{delta_asr:.2f} pp). "
    f"Se excluyeron <b>{fmt_n(excl_count)} llamadas</b> del denominador. "
    + ("Diferencia significativa → fallas principalmente por comportamiento del destino, no por Darwin." if delta_asr > 20
       else "Diferencia reducida → fallas con origen mayoritariamente en la infraestructura."),
    "ok" if asr_real >= 50 else "warn")

if asr_real < 30:
    insight("ASR REAL CRÍTICO",
        f"ASR Real <b>{asr_real:.2f}%</b> — muy por debajo del umbral (&gt;50%). "
        f"Causa dominante: <b>{top_causa_desc}</b> ({top_causa_pct}%). "
        f"Revisar carriers, rutas Darwin y trunks SIP.", "warn")
elif asr_real < 50:
    insight("ASR REAL BAJO",
        f"ASR Real <b>{asr_real:.2f}%</b>. Causa principal: <b>{top_causa_desc}</b> ({top_causa_pct}%). "
        f"Verificar si un carrier o destino específico traccionó el indicador.", "warn")
else:
    insight("ASR REAL NOMINAL",
        f"ASR Real <b>{asr_real:.2f}%</b> — en rango operativo. "
        f"Causa de liberación más frecuente: <b>{top_causa_desc}</b> ({top_causa_pct}%).", "ok")

if top_prov is not None:
    insight("PERFIL DE TRÁFICO",
        f"Destino líder: <b>{top_dest['dest_nombre'] if top_dest is not None else 'N/D'}</b> "
        f"({fmt_n(top_dest['llamadas']) if top_dest is not None else 0} llamadas · ASR Real {top_dest['asr_real_d']:.0f}%). "
        f"Composición: <b>{int(mob_pct)}% Móvil / {100-int(mob_pct)}% Fijo</b>. "
        f"Carrier dominante: <b>{top_prov['proveedor']}</b> ({prov_conc:.0f}% del total). "
        + ("<b>Alta concentración</b> — riesgo de impacto masivo." if prov_conc>70 else "Distribución aceptable entre carriers."))

if peak_cps > 10:
    insight("PICO CPS ELEVADO",
        f"Peak: <b>{peak_cps:.2f} CPS</b> (prom: {avg_cps:.2f}). "
        f"Puede saturar recursos SIP/RTP y generar C34. Verificar dimensionamiento.", "warn")
if cong_pct > 3:
    insight("CONGESTIÓN",
        f"<b>{fmt_n(int(cong_total))} llamadas ({cong_pct:.1f}%)</b> con causas de congestión. "
        f"Activar rutas de overflow si disponibles.", "warn")
if err_pct > 10:
    insight("ERRORES DE NÚMERO / RUTA",
        f"<b>{fmt_n(err_total)} llamadas ({err_pct:.1f}%)</b> por errores de número o ruta. "
        f"Revisar tabla de traducción, portabilidad y configuración de destinos.", "warn")
if c102 > 0 or pl_pct > 2:
    insight("SÍNTOMAS PL / RTT / JITTER",
        f"<b>{fmt_n(pl_total)} eventos ({pl_pct:.1f}%)</b>. C102={c102} (timeout SIP) · C41={c41}. "
        f"Captura PCAP/RTP, Wireshark o Homer SIP. Verificar QoS y jitter en el enlace.", "warn")
else:
    insight("SIN SÍNTOMAS DE PL/RTT/JITTER", "No se detectaron causas compatibles con problemas de red.", "ok")
if sc_pct > 5:
    insight("LLAMADAS CORTAS &lt;3 SEG",
        f"<b>{fmt_n(sc_total)} ({sc_pct:.1f}% conectadas)</b>. "
        f"Síntoma de one-way audio o incompatibilidad de codecs. Cruzar con análisis MOS.", "warn")
if max_retry > 10:
    insight("REINTENTOS SIN CONEXIÓN",
        f"Número <b>{retry['num_b'].iloc[0]}</b>: <b>{max_retry} intentos</b>. "
        f"Causa: <b>{retry['causa_princ'].iloc[0]}</b> · Carrier: <b>{retry['proveedor'].iloc[0]}</b>.", "warn")
if not low_dest.empty:
    names = ", ".join(low_dest.sort_values("llamadas",ascending=False).head(5)["dest_nombre"].tolist())
    insight("DESTINOS ASR REAL &lt;20%",
        f"<b>{names}</b>. Revisar cobertura del carrier, rutas y tasa de inválidos/portados.", "warn")
if not down.empty:
    names = ", ".join(down["proveedor"].tolist())
    insight("CARRIER(S) POSIBLEMENTE CAÍDO(S)",
        f"<b>{names}</b> con ASR Real &lt;5% y volumen significativo. "
        f"Verificar rutas Darwin, enlace SIP y contactar al carrier.", "warn")

# ─── TABS DE ANÁLISIS DETALLADO ───────────────────────────────────────────────
section("ANÁLISIS DETALLADO")

tab_trafico, tab_destinos, tab_proveedores, tab_temporal = st.tabs([
    "  📊  PERFIL DE TRÁFICO  ",
    "  🗺  DESTINOS  ",
    "  🔗  PROVEEDORES  ",
    "  📈  EVOLUCIÓN TEMPORAL  ",
])

# ════════════════════════════════════════════════════════
# TAB 1 — PERFIL DE TRÁFICO
# ════════════════════════════════════════════════════════
with tab_trafico:

    # DONUTS
    dc1, dc2 = st.columns(2)
    with dc1:
        vals  = [connected, ringback, no_conn - ringback]
        labs  = ["Conectadas","Con Ringback","Sin Conexión"]
        clrs  = [C["green"], C["yellow"], C["orange"]]
        fig = go.Figure(go.Pie(
            labels=labs, values=vals, hole=0.55,
            marker=dict(colors=clrs, line=dict(color="#020b18", width=5)),
            textinfo="label+percent",
            textfont=dict(size=13, color="#e8f4ff", family="Arial"),
            insidetextfont=dict(size=13, color="#e8f4ff"),
            hovertemplate="<b>%{label}</b><br>%{value:,} · %{percent}<extra></extra>",
        ))
        fig.update_layout(**pl({
            "title":dict(text="ESTADO DE LLAMADAS",font=dict(color=C["cyan"],size=11,family="Syncopate")),
            "height":340, "showlegend":True,
            "legend":dict(font=dict(color=C["text"],size=11,family="Arial"),orientation="h",y=-0.08),
        }))
        fig.add_annotation(
            text=f"<b>{asr_global:.0f}%</b><br><span style='font-size:9px'>ASR GLOBAL</span>",
            x=0.5, y=0.5, showarrow=False, align="center",
            font=dict(family="Arial", size=18,
                      color=C["green"] if asr_global>=50 else C["orange"]))
        st.plotly_chart(fig, use_container_width=True)

    with dc2:
        mob = (df["traffic_type"]=="Móvil").sum()
        fij = (df["traffic_type"]=="Fijo").sum()
        fig = go.Figure(go.Pie(
            labels=["Móvil","Fijo"], values=[mob,fij], hole=0.55,
            marker=dict(colors=[C["purple"],C["cyan"]], line=dict(color="#020b18", width=5)),
            textinfo="label+percent",
            textfont=dict(size=13, color="#e8f4ff", family="Arial"),
            insidetextfont=dict(size=13, color="#e8f4ff"),
            hovertemplate="<b>%{label}</b><br>%{value:,} · %{percent}<extra></extra>",
        ))
        fig.update_layout(**pl({
            "title":dict(text="FIJO VS MÓVIL",font=dict(color=C["cyan"],size=11,family="Syncopate")),
            "height":340, "showlegend":True,
            "legend":dict(font=dict(color=C["text"],size=11,family="Arial"),orientation="h",y=-0.08),
        }))
        fig.add_annotation(
            text=f"<b>{int(mob_pct)}%</b><br><span style='font-size:9px'>MÓVIL</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(family="Arial", size=18, color=C["purple"]))
        st.plotly_chart(fig, use_container_width=True)

    # TOP RELEASE CAUSES BAR
    st.markdown('<div style="font-family:Syncopate,monospace;font-size:0.65rem;font-weight:700;'
                'color:#00d4ff;letter-spacing:5px;text-transform:uppercase;margin:14px 0 8px;">TOP RELEASE CAUSES</div>',
                unsafe_allow_html=True)
    top12 = causa_cnt.head(12)
    bar_colors = [CAT_COLORS.get(c, C["muted"]) for c in top12["cat"]]
    fig = go.Figure(go.Bar(
        y=top12["desc"], x=top12["count"], orientation="h",
        marker=dict(color=bar_colors, line=dict(color=C["bg"],width=0.5)),
        text=[f"{v:,}  ({p}%)" for v,p in zip(top12["count"],top12["pct"])],
        textposition="outside", textfont=dict(color="#d0e8f8",size=10,family="Arial"),
        hovertemplate="<b>%{y}</b><br>%{x:,} llamadas<extra></extra>",
    ))
    fig.update_layout(**pl({
        "height":360,
        "title":dict(text="TOP RELEASE CAUSES  —  distribución por tipo de corte",
                     font=dict(color=C["cyan"],size=11,family="Syncopate")),
        "yaxis":dict(autorange="reversed", gridcolor="#0d3a5e", zerolinecolor="#0d3a5e",
                     tickfont=dict(size=11,color="#d0e8f8",family="Arial")),
        "xaxis":dict(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e",
                     tickfont=dict(family="Arial",size=10)),
        "margin":dict(l=10,r=100,t=50,b=20),
    }))
    st.plotly_chart(fig, use_container_width=True)

    # TABLA COMPLETA DE CAUSAS
    with st.expander("📋 Distribución completa de Release Causes"):
        tbl_causa = causa_cnt[["causa","nombre","desc","cat","count","pct"]].copy()
        tbl_causa["Llamadas_fmt"] = tbl_causa["count"].apply(lambda v: f"{v:,}".replace(",","."))
        max_calls = tbl_causa["count"].max()
        rows_html = ""
        for _, r in tbl_causa.iterrows():
            intensity = r["count"] / max_calls
            green_alpha = max(0.06, intensity * 0.55)
            cat_color = {"normal":"#00ff88","congestion":"#ff6b35","error":"#ff2d55",
                         "warning":"#ffcc00","packet_loss":"#a855f7","other":"#3a7ca5"}.get(r["cat"],"#3a7ca5")
            rows_html += f"""<tr style="background:rgba(0,255,100,{green_alpha:.2f});">
              <td style="padding:6px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.72rem;font-weight:400;color:#00d4ff;text-align:center;">{r["causa"]}</td>
              <td style="padding:6px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.68rem;font-weight:300;color:#6ea0b8;">{r["nombre"]}</td>
              <td style="padding:6px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.85rem;font-weight:300;color:#d0e8f8;">{r["desc"]}</td>
              <td style="padding:6px 10px;text-align:center;"><span style="background:{cat_color}22;color:{cat_color};border:1px solid {cat_color}55;border-radius:2px;padding:2px 8px;font-family:Arial,Helvetica,sans-serif;font-size:0.62rem;letter-spacing:1px;">{r["cat"]}</span></td>
              <td style="padding:6px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.78rem;font-weight:400;color:#ffffff;text-align:right;">{r["Llamadas_fmt"]}</td>
              <td style="padding:6px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.75rem;font-weight:300;color:#00ff88;text-align:right;">{r["pct"]}%</td>
            </tr>"""
        st.markdown(f"""
        <div style="overflow-x:auto;border:1px solid #0d3a5e;border-radius:4px;">
        <table style="width:100%;border-collapse:collapse;background:#020f1c;">
          <thead><tr style="background:#0a2540;border-bottom:1px solid #00d4ff44;">
            <th style="padding:8px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;text-align:center;">CÓDIGO</th>
            <th style="padding:8px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;">NOMBRE Q.850</th>
            <th style="padding:8px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;">DESCRIPCIÓN</th>
            <th style="padding:8px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;text-align:center;">CATEGORÍA</th>
            <th style="padding:8px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;text-align:right;">LLAMADAS</th>
            <th style="padding:8px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;text-align:right;">%</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table></div>""", unsafe_allow_html=True)

    # PACKET LOSS sub-section
    st.markdown('<div style="font-family:Syncopate,monospace;font-size:0.65rem;font-weight:700;'
                'color:#00d4ff;letter-spacing:5px;text-transform:uppercase;margin:18px 0 8px;">'
                'PACKET LOSS · RTT · JITTER</div>', unsafe_allow_html=True)
    pp1,pp2,pp3,pp4 = st.columns(4)
    pp1.markdown(kpi_card("CAUSAS SOSPECHOSAS",   fmt_n(pl_total), f"{pl_pct:.1f}% del total",  "kpi-warn" if pl_pct>2 else ""), unsafe_allow_html=True)
    pp2.markdown(kpi_card("CAUSA 102 — TIMER",    fmt_n(c102),     "Recovery/PL/RTT",             "kpi-warn" if c102>5  else ""), unsafe_allow_html=True)
    pp3.markdown(kpi_card("CAUSA 41 — TEMP FAIL", fmt_n(c41),      "Falla temporal red",          "kpi-warn" if c41>5   else ""), unsafe_allow_html=True)
    pp4.markdown(kpi_card("CALLS &lt;3 SEG",      fmt_n(sc_total), f"{sc_pct:.1f}% conectadas",  "kpi-warn" if sc_pct>5 else "kpi-ok"), unsafe_allow_html=True)

    if pl_total > 0:
        pl_ts_df = pl_df.copy()
        pl_ts_df["minute"] = pl_ts_df["Fecha Inicio"].dt.floor("1min")
        pl_agg = pl_ts_df.groupby(["minute","Causa"]).size().reset_index(name="n")
        pl_agg["etiqueta"] = pl_agg["Causa"].map(
            lambda c: f"C{c} — {CAUSA_MAP[c][0]}" if c in CAUSA_MAP else str(c))
        fig = px.bar(pl_agg, x="minute", y="n", color="etiqueta",
                     color_discrete_sequence=[C["orange"],C["red"],C["purple"],C["yellow"],C["muted"]],
                     labels={"n":"Eventos","minute":"Hora","etiqueta":"Causa"})
        fig.update_layout(**pl({
            "height":230,
            "title":dict(text="Evolución temporal — síntomas PL/RTT/Jitter",font=dict(color=C["cyan"],size=12)),
            "legend":dict(font=dict(color=C["text"],size=9)),
        }))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<div style="color:#00ff88;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.88rem;padding:8px;">'
                    '✓ Sin síntomas de packet loss o RTT detectados.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 2 — DESTINOS
# ════════════════════════════════════════════════════════
with tab_destinos:
    ASR_REAL_GREEN = "#00994d"

    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(
        name="Llamadas",
        x=dest_top["dest_nombre"], y=dest_top["llamadas"],
        marker=dict(
            color=dest_top["llamadas"],
            colorscale=[[0,"#0d3a5e"],[0.5,"#0066aa"],[1,C["cyan"]]],
            line=dict(color="#020b18",width=0.5),
        ),
        text=dest_top["llamadas"].apply(lambda v: f"{v:,}".replace(",",".")),
        textposition="outside",
        textfont=dict(size=9, color="#a0c8e0", family="Arial"),
        hovertemplate="<b>%{x}</b><br>Llamadas: %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        name="ASR Global %",
        x=dest_top["dest_nombre"], y=dest_top["asr_global_d"],
        mode="lines+markers+text",
        line=dict(color=C["yellow"], width=2, dash="dot"),
        marker=dict(size=5),
        text=dest_top["asr_global_d"].round(1).astype(str)+"%",
        textposition="top center",
        textfont=dict(size=9, color=C["yellow"], family="Arial"),
    ), secondary_y=True)
    fig.add_trace(go.Scatter(
        name="ASR Real %",
        x=dest_top["dest_nombre"], y=dest_top["asr_real_d"],
        mode="lines+markers+text",
        line=dict(color=ASR_REAL_GREEN, width=2.5),
        marker=dict(size=7, color=ASR_REAL_GREEN, line=dict(color="#ffffff",width=1)),
        text=dest_top["asr_real_d"].round(1).astype(str)+"%",
        textposition="bottom center",
        textfont=dict(size=9, color=ASR_REAL_GREEN, family="Arial"),
    ), secondary_y=True)
    fig.add_hline(y=50, line_dash="dot", line_color=C["orange"],
                  annotation_text="50% ASR", annotation_font_color=C["orange"],
                  secondary_y=True)
    fig.update_xaxes(
        tickfont=dict(size=10, color="#a0c8e0", family="Arial"),
        tickangle=-40, gridcolor="#0d3a5e", zerolinecolor="#0d3a5e",
    )
    fig.update_yaxes(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e")
    fig.update_layout(**{**pl(),
        "height":440,
        "title":dict(text="Llamadas · ASR Global · ASR Real — por destino (Top 30)",
                     font=dict(color=C["cyan"],size=13)),
        "legend":dict(font=dict(color=C["text"],size=11), orientation="h", y=1.05, x=0),
        "yaxis2":dict(range=[0,130], gridcolor="#0d3a5e", zerolinecolor="#0d3a5e",
                      title="ASR %", tickfont=dict(color=C["text"])),
        "margin":dict(l=40,r=40,t=60,b=80),
    })
    st.plotly_chart(fig, use_container_width=True)

    # Tabla destinos
    def asr_dots(val):
        if val >= 70:   color, label = "#00ff88", "●●●"
        elif val >= 40: color, label = "#ffcc00", "●●○"
        else:           color, label = "#ff6b35", "●○○"
        return f'<span style="color:{color};font-size:0.9rem;">{label}</span> <b style="color:{color};font-family:Arial,Helvetica,sans-serif;font-size:0.8rem;font-weight:400;">{val:.0f}%</b>'

    def bar_html(val, max_val, color="#00d4ff"):
        pct = min(val/max_val*100, 100) if max_val > 0 else 0
        return (f'<div style="display:flex;align-items:center;gap:6px;">'
                f'<div style="background:{color};height:6px;width:{pct:.0f}%;'
                f'min-width:4px;border-radius:2px;max-width:120px;opacity:0.8;"></div>'
                f'<span style="font-family:Arial,Helvetica,sans-serif;font-size:0.78rem;font-weight:300;color:#e0f0ff;">'
                f'{val:,}'.replace(",",".") + f'</span></div>')

    max_calls_d = dest_top["llamadas"].max()
    rows_html = ""
    for i,(_, r) in enumerate(dest_top.iterrows(), 1):
        bg = "rgba(4,22,37,0.9)" if i % 2 == 0 else "rgba(6,30,48,0.9)"
        calls_fmt = f"{int(r['llamadas']):,}".replace(",",".")
        conn_fmt  = f"{int(r['conectadas']):,}".replace(",",".")
        min_fmt   = f"{r['minutos']:,.1f}".replace(",",".")
        rows_html += (
            f'<tr style="background:{bg};border-bottom:1px solid #0a2030;">' +
            f'<td style="padding:7px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.65rem;font-weight:300;color:#2e5f7e;text-align:center;">{i}</td>' +
            f'<td style="padding:7px 14px;font-family:Arial,Helvetica,sans-serif;font-size:0.9rem;font-weight:300;color:#e0f0ff;">{r["dest_nombre"]}</td>' +
            f'<td style="padding:7px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.65rem;font-weight:300;color:#2e5f7e;text-align:center;">{r["dest_modal"]}</td>' +
            f'<td style="padding:7px 10px;">{asr_dots(r["asr_real_d"])}</td>' +
            f'<td style="padding:7px 10px;">{bar_html(r["llamadas"], max_calls_d)}</td>' +
            f'<td style="padding:7px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.78rem;font-weight:300;color:#a0c8e0;text-align:right;">{conn_fmt}</td>' +
            f'<td style="padding:7px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.75rem;font-weight:400;color:#ffcc00;text-align:right;">{min_fmt}</td>' +
            f'<td style="padding:7px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.72rem;font-weight:300;color:#00d4ff;text-align:center;">{r["asr_global_d"]:.1f}%</td>' +
            '</tr>'
        )
    st.markdown(
        '<div style="overflow-x:auto;border:1px solid #0d3a5e;border-radius:4px;margin-top:4px;">'
        '<table style="width:100%;border-collapse:collapse;background:#020f1c;">'
        '<thead><tr style="background:#061e30;border-bottom:1px solid #00d4ff33;">'
        '<th style="padding:9px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;text-align:center;">N°</th>'
        '<th style="padding:9px 14px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;">DESTINO</th>'
        '<th style="padding:9px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;text-align:center;">MODAL</th>'
        '<th style="padding:9px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;">ASR REAL</th>'
        '<th style="padding:9px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;">TOTAL CALLS</th>'
        '<th style="padding:9px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;text-align:right;">CALLS OK</th>'
        '<th style="padding:9px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#ffcc00;letter-spacing:3px;text-align:right;">MINUTOS</th>'
        '<th style="padding:9px 10px;font-family:Arial,Helvetica,sans-serif;font-size:0.55rem;font-weight:400;color:#00d4ff;letter-spacing:3px;text-align:center;">ASR GLOBAL</th>'
        '</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 3 — PROVEEDORES
# ════════════════════════════════════════════════════════
with tab_proveedores:

    cp1, cp2 = st.columns(2)
    with cp1:
        ps = prov_df.sort_values("llamadas", ascending=True)
        dot_colors = [C["red"] if a<30 else (C["yellow"] if a<60 else C["green"]) for a in ps["asr_real"]]
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(
            name="Llamadas", y=ps["proveedor"].str[:26], x=ps["llamadas"],
            orientation="h", marker=dict(color=C["cyan"],opacity=0.75),
            text=ps["llamadas"], textposition="outside", textfont=dict(size=9),
        ))
        fig.add_trace(go.Scatter(
            name="ASR Real %", y=ps["proveedor"].str[:26], x=ps["asr_real"],
            mode="markers+text",
            marker=dict(color=dot_colors, size=11, symbol="diamond"),
            text=ps["asr_real"].round(1).astype(str)+"%",
            textposition="middle right", textfont=dict(size=8,color=C["text"]),
        ), secondary_y=True)
        fig.update_layout(**pl({
            "height":280,
            "title":dict(text="Proveedor: Llamadas & ASR Real",font=dict(color=C["cyan"],size=12)),
            "yaxis2":dict(range=[0,140],gridcolor="#0d3a5e",zerolinecolor="#0d3a5e"),
            "xaxis":dict(gridcolor="#0d3a5e",zerolinecolor="#0d3a5e"),
            "legend":dict(font=dict(color=C["text"])),
            "margin":dict(l=10,r=70,t=45,b=20),
        }))
        st.plotly_chart(fig, use_container_width=True)

    with cp2:
        rs = ruta_df.sort_values("llamadas",ascending=False)
        fig = go.Figure(go.Bar(
            x=rs["ruta_dest"].str[:24], y=rs["llamadas"],
            marker=dict(color=rs["llamadas"],colorscale=[[0,"#0d3a5e"],[1,C["purple"]]]),
            text=[f"ASR Real {r}% · {c:,}" for r,c in zip(rs["asr_real"].astype(int), rs["llamadas"])],
            textposition="outside", textfont=dict(color=C["text"],size=9),
            customdata=rs["proveedor"],
            hovertemplate="<b>%{x}</b><br>%{y:,} llamadas<br>%{text}<br>%{customdata}<extra></extra>",
        ))
        fig.update_layout(**pl({
            "height":280, "xaxis_tickangle":-25,
            "title":dict(text="Ruta destino: Llamadas & ASR Real",font=dict(color=C["cyan"],size=12)),
        }))
        st.plotly_chart(fig, use_container_width=True)

    # Caídos / degradados
    cd1, cd2 = st.columns(2)
    with cd1:
        st.markdown('<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.6rem;color:#ff2d55;'
                    'letter-spacing:3px;margin-bottom:6px;text-transform:uppercase;">🔴 POSIBLEMENTE CAÍDOS — ASR Real &lt; 5%</div>',
                    unsafe_allow_html=True)
        if down.empty:
            st.markdown('<div style="color:#00ff88;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.88rem;">'
                        '✓ Sin proveedores caídos</div>', unsafe_allow_html=True)
        else:
            st.dataframe(down[["proveedor","llamadas","conectadas","asr_global","asr_real"]].rename(
                columns={"proveedor":"Proveedor","llamadas":"Llamadas","conectadas":"Conectadas",
                         "asr_global":"ASR Global %","asr_real":"ASR Real %"}),
                hide_index=True, use_container_width=True)
    with cd2:
        st.markdown('<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.6rem;color:#ffcc00;'
                    'letter-spacing:3px;margin-bottom:6px;text-transform:uppercase;">🟡 DEGRADADOS — ASR Real 5%–30%</div>',
                    unsafe_allow_html=True)
        if deg.empty:
            st.markdown('<div style="color:#00ff88;font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.88rem;">'
                        '✓ Sin degradación detectada</div>', unsafe_allow_html=True)
        else:
            st.dataframe(deg[["proveedor","llamadas","conectadas","asr_global","asr_real"]].rename(
                columns={"proveedor":"Proveedor","llamadas":"Llamadas","conectadas":"Conectadas",
                         "asr_global":"ASR Global %","asr_real":"ASR Real %"}),
                hide_index=True, use_container_width=True)

    with st.expander("📋 Tabla completa proveedor / ruta"):
        st.dataframe(ruta_df.sort_values("llamadas",ascending=False).rename(columns={
            "proveedor":"Proveedor","ruta_dest":"Ruta","llamadas":"Llamadas",
            "conectadas":"Conectadas","excluidas":"Excluidas","asr_global":"ASR Global %",
            "asr_real":"ASR Real %",
        }), hide_index=True, use_container_width=True)

    # Reintentos
    st.markdown('<div style="font-family:Syncopate,monospace;font-size:0.65rem;font-weight:700;'
                'color:#00d4ff;letter-spacing:5px;text-transform:uppercase;margin:18px 0 8px;">'
                'REINTENTOS SIN CONEXIÓN</div>', unsafe_allow_html=True)
    cr1, cr2 = st.columns([1.4, 1])
    with cr1:
        top20 = retry.head(20)
        clrs  = [C["red"] if i<3 else (C["orange"] if i<8 else C["yellow"]) for i in range(len(top20))]
        med = top20["intentos"].median()
        use_log = top20["intentos"].max() > med * 10
        fig = go.Figure(go.Bar(
            x=top20["num_b"], y=top20["intentos"],
            marker=dict(color=clrs, line=dict(color=C["bg"], width=0.5)),
            text=top20["intentos"].apply(lambda v: f"{v:,}"),
            textposition="outside", textfont=dict(color=C["text"], size=9),
            customdata=np.stack([top20["causa_princ"],top20["proveedor"],top20["dest_nombre"]],axis=-1),
            hovertemplate="<b>%{x}</b><br>Intentos: %{y:,}<br>Causa: %{customdata[0]}<br>"
                          "Carrier: %{customdata[1]}<br>Destino: %{customdata[2]}<extra></extra>",
        ))
        yaxis_cfg = dict(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e",
                         type="log" if use_log else "linear",
                         title="Intentos (escala log)" if use_log else "Intentos")
        fig.update_layout(**pl({
            "height":300, "xaxis_tickangle":-45,
            "title":dict(text="Top 20 números con más intentos fallidos"
                             + (" (escala logarítmica)" if use_log else ""),
                         font=dict(color=C["cyan"],size=12)),
            "yaxis": yaxis_cfg,
        }))
        if use_log:
            st.markdown(
                f'<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.65rem;color:#ffcc00;letter-spacing:1px;">'
                f'⚠ Escala logarítmica — outlier detectado: '
                f'<b style="font-weight:400;">{top20["num_b"].iloc[0]}</b> con <b style="font-weight:400;">{top20["intentos"].iloc[0]:,}</b> intentos</div>',
                unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
    with cr2:
        st.dataframe(retry.head(25).rename(columns={
            "num_b":"Número B","intentos":"Intentos","causas_top":"Top 3 causas",
            "causa_princ":"Causa principal","proveedor":"Carrier","dest_nombre":"Destino",
        }), hide_index=True, use_container_width=True, height=290)

# ════════════════════════════════════════════════════════
# TAB 4 — EVOLUCIÓN TEMPORAL
# ════════════════════════════════════════════════════════
with tab_temporal:
    ts = (df.assign(minute=df["Fecha Inicio"].dt.floor("1min"))
            .groupby("minute")
            .agg(llamadas  =("Causa","count"),
                 conectadas=("is_connected","sum"),
                 minutos   =("duration_min","sum"),
                 excluidas =("excl_asr_real","sum"))
            .reset_index())
    ts["cps"]     = (ts["llamadas"]/60).round(2)
    ts["no_conn"] = ts["llamadas"] - ts["conectadas"]
    ts["asr_g"]   = (ts["conectadas"]/ts["llamadas"]*100).round(1)
    ts["ll_real"] = ts["llamadas"] - ts["excluidas"]
    ts["asr_r"]   = np.where(ts["ll_real"]>0, (ts["conectadas"]/ts["ll_real"]*100).round(1), 0)
    ts["hora"]    = ts["minute"].dt.strftime("%H:%M")

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.45, 0.28, 0.27],
        vertical_spacing=0.06,
        subplot_titles=["Llamadas / minuto","CPS (Calls per Second)","ASR Global %  vs  ASR Real %"],
    )
    fig.add_trace(go.Scatter(
        x=ts["hora"], y=ts["llamadas"], name="Total",
        mode="lines+markers+text", line=dict(color=C["cyan"],width=2),
        marker=dict(size=5),
        text=ts["llamadas"], textposition="top center",
        textfont=dict(size=8,color=C["cyan"],family="Arial"),
        fill="tozeroy", fillcolor="rgba(0,212,255,0.05)",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=ts["hora"], y=ts["conectadas"], name="Conectadas",
        mode="lines+markers", line=dict(color=C["green"],width=1.5,dash="dot"),
        marker=dict(size=4),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=ts["hora"], y=ts["no_conn"], name="No conectadas",
        mode="lines+markers", line=dict(color=C["orange"],width=1.5),
        marker=dict(size=4),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=ts["hora"], y=ts["cps"], name="CPS",
        mode="lines+markers+text", line=dict(color=C["yellow"],width=2),
        marker=dict(size=5),
        text=ts["cps"].round(2), textposition="top center",
        textfont=dict(size=8,color=C["yellow"],family="Arial"),
        fill="tozeroy", fillcolor="rgba(255,204,0,0.05)",
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=ts["hora"], y=ts["asr_g"], name="ASR Global %",
        mode="lines+markers+text", line=dict(color=C["yellow"],width=1.5,dash="dot"),
        marker=dict(size=5),
        text=ts["asr_g"].astype(str)+"%", textposition="top center",
        textfont=dict(size=8,color=C["yellow"],family="Arial"),
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=ts["hora"], y=ts["asr_r"], name="ASR Real %",
        mode="lines+markers+text", line=dict(color=C["green"],width=2),
        marker=dict(size=5,
                    color=[C["red"] if a<30 else (C["yellow"] if a<60 else C["green"]) for a in ts["asr_r"]]),
        text=ts["asr_r"].astype(str)+"%", textposition="bottom center",
        textfont=dict(size=8,color=C["green"],family="Arial"),
    ), row=3, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color=C["orange"],
                  annotation_text="50%", annotation_font_color=C["orange"], row=3, col=1)
    for r in [1,2,3]:
        fig.update_xaxes(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", row=r, col=1)
        fig.update_yaxes(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", row=r, col=1)
    fig.update_layout(**{**pl(),
        "height":520, "showlegend":True,
        "legend":dict(font=dict(color=C["text"],size=9), orientation="h", y=1.02, x=0),
        "title":dict(text="Evolución temporal del tráfico — ASR Global vs ASR Real",
                     font=dict(color=C["cyan"],size=12)),
    })
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTAR PDF
# ═══════════════════════════════════════════════════════════════════════════════
section("EXPORTAR REPORTE")
st.markdown('<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;font-size:0.85rem;color:#2e5f7e;margin-bottom:10px;">'
            'Genera un PDF con el resumen ejecutivo. Se guarda también en la carpeta tmp_darwin.</div>',
            unsafe_allow_html=True)

if st.button("⬇  EXPORTAR REPORTE PDF"):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl_c
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable)
        from reportlab.lib.units import cm

        buf  = io.BytesIO()
        doc  = SimpleDocTemplate(buf, pagesize=A4,
                                 leftMargin=1.5*cm, rightMargin=1.5*cm,
                                 topMargin=1.5*cm,  bottomMargin=1.5*cm)

        CYN  = rl_c.HexColor("#00d4ff")
        GRN  = rl_c.HexColor("#00ff88")
        ORN  = rl_c.HexColor("#ff6b35")
        WHT  = rl_c.HexColor("#e0f4ff")
        DARK = rl_c.HexColor("#041625")
        MID  = rl_c.HexColor("#0d3a5e")
        MID2 = rl_c.HexColor("#051a2e")

        sty = getSampleStyleSheet()
        T_  = ParagraphStyle("T",parent=sty["Normal"],fontName="Helvetica-Bold",fontSize=17,textColor=CYN,alignment=1,spaceAfter=4)
        S_  = ParagraphStyle("S",parent=sty["Normal"],fontName="Helvetica",fontSize=9,textColor=MID,alignment=1,spaceAfter=12)
        H2_ = ParagraphStyle("H",parent=sty["Normal"],fontName="Helvetica-Bold",fontSize=11,textColor=CYN,spaceBefore=14,spaceAfter=6)
        B_  = ParagraphStyle("B",parent=sty["Normal"],fontName="Helvetica",fontSize=8.5,textColor=WHT,leading=13,spaceAfter=4)
        W_  = ParagraphStyle("W",parent=B_,textColor=ORN)
        OK_ = ParagraphStyle("K",parent=B_,textColor=GRN)

        def tblrl(data, cw=None):
            t = Table(data, colWidths=cw)
            t.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),MID),("TEXTCOLOR",(0,0),(-1,0),CYN),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),
                ("BACKGROUND",(0,1),(-1,-1),DARK),("TEXTCOLOR",(0,1),(-1,-1),WHT),
                ("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,1),(-1,-1),8),
                ("GRID",(0,0),(-1,-1),0.3,MID),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[DARK,MID2]),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),6),
            ]))
            return t

        story = [
            Paragraph("📡 DARWIN CDR ANALYTICS", T_),
            Paragraph("IPLAN · REPORTE DE TRÁFICO", S_),
            HRFlowable(width="100%",thickness=0.5,color=MID), Spacer(1,8),
        ]
        story += [Paragraph("INFORMACIÓN DEL CDR", H2_), tblrl([
            ["Carrier Entrante","Ruta Entrante","Fecha CDR","Primer CDR","Último CDR"],
            [carrier_ent,ruta_ent,fecha_cdr_s,hora_prim,hora_ult],
        ]), Spacer(1,10)]

        story += [Paragraph("KPIs PRINCIPALES", H2_), tblrl([
            ["Total","Conectadas","Ringback","No Conectadas","ASR Global","ASR Real","CPS Prom","CPS Peak"],
            [fmt_n(total),fmt_n(connected),fmt_n(ringback),fmt_n(no_conn),
             f"{asr_global:.2f}%",f"{asr_real:.2f}%",f"{avg_cps:.2f}",f"{peak_cps:.2f}"],
        ]), Spacer(1,10)]

        story += [Paragraph("TOP RELEASE CAUSES", H2_)]
        rcr = [["Código","Descripción","Categoría","Llamadas","%"]]
        for _,r in causa_cnt.head(10).iterrows():
            rcr.append([str(r["causa"]),r["desc"][:45],r["cat"],fmt_n(r["count"]),f"{r['pct']}%"])
        story += [tblrl(rcr,[1.5*cm,7.5*cm,2.5*cm,2*cm,1.5*cm]), Spacer(1,10)]

        story += [Paragraph("TOP DESTINOS", H2_)]
        dtr = [["Destino","Modalidad","Llamadas","Conectadas","Min","ASR Global","ASR Real"]]
        for _,r in dest_df.sort_values("llamadas",ascending=False).head(12).iterrows():
            dtr.append([r["dest_nombre"][:28],str(r["dest_modal"])[:10],
                        fmt_n(r["llamadas"]),fmt_n(r["conectadas"]),
                        f"{r['minutos']:.0f}",f"{r['asr_global_d']:.1f}%",f"{r['asr_real_d']:.1f}%"])
        story += [tblrl(dtr,[4.5*cm,1.8*cm,2.2*cm,2.2*cm,1.3*cm,2*cm,2*cm]), Spacer(1,10)]

        story += [Paragraph("ANÁLISIS POR PROVEEDOR", H2_)]
        pvr = [["Proveedor","Llamadas","Conectadas","ASR Global","ASR Real"]]
        for _,r in prov_df.sort_values("llamadas",ascending=False).iterrows():
            pvr.append([r["proveedor"][:36],fmt_n(r["llamadas"]),
                        fmt_n(r["conectadas"]),f"{r['asr_global']:.1f}%",f"{r['asr_real']:.1f}%"])
        story += [tblrl(pvr,[7.5*cm,2.5*cm,2.5*cm,2.0*cm,2.0*cm]), Spacer(1,10)]

        if max_retry > 0:
            story += [Paragraph("TOP REINTENTOS SIN CONEXIÓN", H2_)]
            rtr = [["Número B","Intentos","Causa Principal","Carrier"]]
            for _,r in retry.head(10).iterrows():
                rtr.append([r["num_b"],fmt_n(r["intentos"]),r["causa_princ"][:38],r["proveedor"][:25]])
            story += [tblrl(rtr,[4.5*cm,2*cm,7*cm,3*cm]), Spacer(1,10)]

        story += [Paragraph("DIAGNÓSTICO AUTOMÁTICO", H2_)]
        diags = []
        diags.append(("ok" if asr_real>=50 else "warn",
                       f"ASR Global {asr_global:.2f}% · ASR Real {asr_real:.2f}% · Δ+{delta_asr:.2f}pp"))
        if peak_cps > 10: diags.append(("warn",f"Peak CPS {peak_cps:.2f} — verificar capacity"))
        if c102>0 or pl_pct>2: diags.append(("warn",f"Síntomas PL/RTT: {pl_total} eventos, C102={c102}"))
        if not down.empty: diags.append(("warn",f"Carrier caído: {', '.join(down['proveedor'].tolist())}"))
        if cong_pct>3: diags.append(("warn",f"Congestión: {fmt_n(int(cong_total))} ({cong_pct:.1f}%)"))
        if sc_pct>5: diags.append(("warn",f"Llamadas cortas <3s: {sc_total} ({sc_pct:.1f}%)"))
        if max_retry>10: diags.append(("warn",f"Reintentos: {retry['num_b'].iloc[0]} × {max_retry}"))
        for kind,text in diags:
            story.append(Paragraph(("⚠ " if kind=="warn" else "✓ ")+text, W_ if kind=="warn" else OK_))

        story += [Spacer(1,14), HRFlowable(width="100%",thickness=0.3,color=MID),
                  Paragraph(f"Generado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} · {cdr_name} · DARWIN CDR Analytics · IPLAN", S_)]

        doc.build(story)
        buf.seek(0)
        pdf_bytes = buf.getvalue()

        try:
            tmp_folder.mkdir(parents=True, exist_ok=True)
            pdf_name = f"CDR_Report_{fecha_cdr_s}_{hora_prim.replace(':','')}.pdf"
            (tmp_folder / pdf_name).write_bytes(pdf_bytes)
            st.success(f"✓ PDF guardado en: {tmp_folder / pdf_name}")
        except Exception as e:
            st.warning(f"No se pudo guardar en disco: {e}")

        st.download_button(
            label="📥 DESCARGAR PDF",
            data=pdf_bytes,
            file_name=f"CDR_Report_{fecha_cdr_s}_{hora_prim.replace(':','')}.pdf",
            mime="application/pdf",
        )
    except ImportError:
        st.error("Instalá reportlab: pip install reportlab")
    except Exception as e:
        st.error(f"Error generando PDF: {e}")

st.markdown(
    f'<div style="font-family:Arial,Helvetica,sans-serif;font-weight:300;color:#0e2840;font-size:0.58rem;'
    f'text-align:center;margin-top:20px;letter-spacing:3px;text-transform:uppercase;">'
    f'DARWIN CDR ANALYTICS · IPLAN · {fecha_cdr_s} {hora_prim}–{hora_ult} · {cdr_name}'
    f'</div>', unsafe_allow_html=True)
