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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] { background:#020b18 !important; color:#c8e6ff !important; }
[data-testid="stSidebar"] { background:#030e1f !important; border-right:1px solid #0d3a5e !important; }

.main-title {
  font-family:'Orbitron',monospace; font-size:2rem; font-weight:900; color:#00d4ff;
  text-shadow:0 0 20px #00d4ff88,0 0 40px #00d4ff44; letter-spacing:4px;
  text-align:center; margin-bottom:0;
}
.sub-title {
  font-family:'Share Tech Mono',monospace; font-size:0.78rem; color:#3a7ca5;
  text-align:center; letter-spacing:8px; margin-top:4px; margin-bottom:16px;
}

/* KPI cards */
.kpi-card {
  background:linear-gradient(160deg,#041625 0%,#061e30 100%);
  border:1px solid #0d3a5e; border-top:2px solid #00d4ff; border-radius:8px;
  padding:12px 10px 10px 10px; text-align:center;
  box-shadow:0 0 14px #00d4ff14; margin-bottom:4px;
}
.kpi-desc  { font-family:'Rajdhani',sans-serif; font-size:0.68rem; font-weight:600;
             color:#3a7ca5; letter-spacing:2px; text-transform:uppercase; margin-bottom:5px; }
.kpi-value { font-family:'Orbitron',monospace; font-size:1.6rem; font-weight:700;
             color:#00d4ff; text-shadow:0 0 10px #00d4ff88; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:0.68rem; margin-top:3px; }
.kpi-warn  { color:#ff6b35; }
.kpi-ok    { color:#00ff88; }
.kpi-caution { color:#ffcc00; }

/* Meta bar */
.meta-grid {
  display:grid; grid-template-columns:repeat(5,1fr); gap:0;
  background:#030f20; border:1px solid #0d3a5e; border-radius:8px;
  overflow:hidden; margin-bottom:6px;
}
.meta-cell {
  padding:13px 16px; border-right:1px solid #0d3a5e;
  display:flex; flex-direction:column; gap:5px;
}
.meta-cell:last-child { border-right:none; }
.meta-label {
  font-family:'Rajdhani',sans-serif; font-weight:700; font-size:0.62rem;
  color:#3a7ca5; letter-spacing:3px; text-transform:uppercase;
}
.meta-value {
  font-family:'Rajdhani',sans-serif; font-weight:700; font-size:1.05rem;
  color:#e8f6ff;
}

/* Section headers */
.section-header {
  font-family:'Orbitron',monospace; font-size:0.85rem; color:#00d4ff;
  letter-spacing:3px; text-transform:uppercase;
  border-bottom:1px solid #0d3a5e; padding-bottom:6px; margin:20px 0 12px 0;
}

/* Insight boxes */
.insight-box {
  background:linear-gradient(135deg,#041625,#061e30);
  border:1px solid #0d3a5e; border-left:3px solid #00d4ff; border-radius:4px;
  padding:11px 15px; margin:6px 0;
  font-family:'Rajdhani',sans-serif; font-size:0.9rem;
  color:#b0d4e8; line-height:1.55;
}
.insight-warn { border-left-color:#ff6b35;
  background:linear-gradient(135deg,#160800,#0d0400); color:#ffbe96; }
.insight-ok   { border-left-color:#00ff88;
  background:linear-gradient(135deg,#001a0a,#00100a); color:#90ffcc; }
.insight-title { font-family:'Orbitron',monospace; font-size:0.68rem;
  letter-spacing:3px; margin-bottom:4px; }

/* ASR badge */
.asr-badge {
  display:inline-block; border-radius:6px; padding:3px 10px;
  font-family:'Orbitron',monospace; font-size:0.75rem; font-weight:700;
  letter-spacing:2px; margin-right:6px;
}
.asr-ok   { background:#003a1a; color:#00ff88; border:1px solid #00ff88; }
.asr-warn { background:#3a1200; color:#ff6b35; border:1px solid #ff6b35; }
.asr-crit { background:#2a0008; color:#ff2d55; border:1px solid #ff2d55; }

h1,h2,h3 { color:#00d4ff !important; }
.stButton>button {
  background:linear-gradient(135deg,#041625,#0d3a5e) !important;
  border:1px solid #00d4ff !important; color:#00d4ff !important;
  font-family:'Orbitron',monospace !important; letter-spacing:2px !important;
  padding:10px 28px !important;
}
div[data-testid="metric-container"] {
  background:#041625 !important; border:1px solid #0d3a5e !important;
  border-radius:6px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Paths ────────────────────────────────────────────────────────────────────
CDR_FOLDER = Path(r"C:\Users\rdangelo\reportes_python_2026\analitycs_cdrs_darwin\datos_cdr_darwin")
TMP_FOLDER = Path(r"C:\Users\rdangelo\reportes_python_2026\analitycs_cdrs_darwin\tmp_darwin")
# Maestro de prefijos (TMP) vive en tmp_darwin
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
    font=dict(family="Rajdhani, sans-serif", color=C["text"], size=11),
    xaxis=dict(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", linecolor="#0d3a5e"),
    yaxis=dict(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", linecolor="#0d3a5e"),
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
    """Load TMP master file (comma-sep, with leading 0 on prefixes)."""
    df = pd.read_csv(io.BytesIO(raw), sep=",", on_bad_lines="skip", low_memory=False)
    df.columns = df.columns.str.strip()
    # Fix rows where digits+letters are merged in Prefijo column
    def fix_row(row):
        pref = str(row.get("Prefijo","")).strip()
        desc = str(row.get("Descripcion","")).strip()
        mod  = str(row.get("Modalidad","")).strip() if pd.notna(row.get("Modalidad")) else ""
        m = re.match(r"^(\d+)([A-Za-z\s]+)$", pref)
        if m:
            return pd.Series({"Prefijo": m.group(1), "Descripcion": m.group(2).strip(), "Modalidad": desc})
        return pd.Series({"Prefijo": pref, "Descripcion": desc, "Modalidad": mod})
    df = df.apply(fix_row, axis=1)
    # Strip leading zeros to match CDR Prefijo Dest format
    df["Prefijo_key"] = df["Prefijo"].str.lstrip("0")
    df = df.drop_duplicates("Prefijo_key")
    return {
        "desc":  dict(zip(df["Prefijo_key"], df["Descripcion"])),
        "modal": dict(zip(df["Prefijo_key"], df["Modalidad"])),
    }

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

    # Destination name from TMP master
    if pm_raw:
        pm = load_tmp_master(pm_raw)
        df["dest_nombre"] = df["pref_str"].map(pm["desc"]).fillna("Desconocido")
        df["dest_modal"]  = df["pref_str"].map(pm["modal"]).fillna("N/D")
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
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00d4ff;letter-spacing:2px;'
                'font-size:0.82rem;margin-bottom:10px;">📁 CONFIGURACIÓN</div>', unsafe_allow_html=True)

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
        st.markdown(f'<div style="color:#00ff88;font-family:Share Tech Mono;font-size:0.7rem;margin-top:6px;">'
                    f'✓ CDR: {cdr_path.name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#3a7ca5;font-family:Share Tech Mono;font-size:0.66rem;">'
                    f'🕐 {pd.Timestamp(cdr_path.stat().st_mtime,unit="s").strftime("%Y-%m-%d %H:%M")} '
                    f'· {cdr_path.stat().st_size/1024:.0f} KB</div>', unsafe_allow_html=True)
        with open(cdr_path,"rb") as f: raw_cdr = f.read()
        cdr_name = cdr_path.name
    else:
        st.markdown('<div style="color:#ff6b35;font-family:Share Tech Mono;font-size:0.7rem;">⚠ Sin CDR en carpeta</div>',
                    unsafe_allow_html=True)

    if maestro_path:
        st.markdown(f'<div style="color:#ffcc00;font-family:Share Tech Mono;font-size:0.7rem;margin-top:2px;">'
                    f'📋 Maestro: {maestro_path.name}</div>', unsafe_allow_html=True)
        with open(maestro_path,"rb") as f: raw_maestro = f.read()
        maestro_name = maestro_path.name
    else:
        st.markdown('<div style="color:#3a7ca5;font-family:Share Tech Mono;font-size:0.7rem;margin-top:2px;">'
                    'ℹ Sin maestro de prefijos</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-family:Share Tech Mono;color:#3a7ca5;font-size:0.65rem;'
                'margin:10px 0 3px;">— SUBIR MANUALMENTE —</div>', unsafe_allow_html=True)
    up_cdr = st.file_uploader("CDR (.csv)",     type=["csv"], key="up_cdr", label_visibility="collapsed")
    up_mae = st.file_uploader("Maestro (.csv)", type=["csv"], key="up_mae", label_visibility="collapsed")
    if up_cdr: raw_cdr = up_cdr.read(); cdr_name = up_cdr.name
    if up_mae: raw_maestro = up_mae.read(); maestro_name = up_mae.name

    # Demo fallback
    if raw_cdr is None:
        for p in ["/mnt/user-data/uploads/reportCDR-08-06-26-01-56-38.csv"]:
            try:
                with open(p,"rb") as f: raw_cdr = f.read()
                cdr_name = Path(p).name
                st.markdown('<div style="color:#ffcc00;font-family:Share Tech Mono;font-size:0.7rem;">⚡ CDR DEMO</div>',
                            unsafe_allow_html=True)
                break
            except: pass
    if raw_maestro is None:
        for p in ["/mnt/user-data/uploads/Maestro_de_prefijos-TMP.csv",
                  "/mnt/user-data/uploads/Maestro_de_prefijos-08-06-26-03-44-17.csv"]:
            try:
                with open(p,"rb") as f: raw_maestro = f.read()
                maestro_name = Path(p).name
                break
            except: pass

    st.markdown("---")
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00d4ff;letter-spacing:2px;'
                'font-size:0.78rem;margin-bottom:8px;">FILTROS</div>', unsafe_allow_html=True)

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
# KPIs
# ═══════════════════════════════════════════════════════════════════════════════
section("KPIs PRINCIPALES")
cols = st.columns(7)
kpis = [
    ("TOTAL RECIBIDAS",   fmt_n(total),        None,                                     ""),
    ("CONECTADAS",        fmt_n(connected),    f"{connected/total*100:.0f}% del total",  "kpi-ok" if asr_global>=50 else "kpi-warn"),
    ("CON RINGBACK",      fmt_n(ringback),     f"{ringback/total*100:.0f}% del total",   ""),
    ("NO CONECTADAS",     fmt_n(no_conn),      f"{no_conn/total*100:.0f}% del total",    "kpi-warn" if no_conn/total>0.5 else ""),
    ("ASR GLOBAL",        f"{asr_global:.2f}%","TLC / TL",                               "kpi-ok" if asr_global>=50 else "kpi-warn"),
    ("ASR REAL",          f"{asr_real:.2f}%",  f"Excl. {fmt_n(excl_count)} llamadas",   "kpi-ok" if asr_real>=50 else "kpi-warn"),
    ("CPS PROMEDIO",      f"{avg_cps:.2f}",    f"Peak {peak_cps:.2f} cps",              "kpi-warn" if peak_cps>10 else ""),
]
for col,(desc,val,sub,cls) in zip(cols, kpis):
    col.markdown(kpi_card(desc,val,sub,cls), unsafe_allow_html=True)

# ─── Meta bar ─────────────────────────────────────────────────────────────────
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

# ASR explanation strip
st.markdown(
    f'<div style="font-family:Share Tech Mono;font-size:0.72rem;color:#3a7ca5;'
    f'padding:6px 12px;background:#030f20;border:1px solid #0d3a5e;border-radius:4px;'
    f'margin-bottom:4px;">'
    f'<b style="color:#00d4ff">ASR Global</b> = Llamadas con duración &gt;0 / Total llamadas &nbsp;|&nbsp; '
    f'<b style="color:#00d4ff">ASR Real</b> = Excluye causas de corte por decisión del destino (C16-Orig, C1/17/18/19/20/22/27/28/102-Dest)'
    f'</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL DE TRÁFICO + RELEASE CAUSES
# ═══════════════════════════════════════════════════════════════════════════════
section("PERFIL DE TRÁFICO  ·  RELEASE CAUSES")

# Causa dataframe
causa_cnt = df["Causa"].value_counts().reset_index()
causa_cnt.columns = ["causa","count"]
causa_cnt["pct"] = (causa_cnt["count"]/total*100).round(1)
def enrich_causa(row):
    info = CAUSA_MAP.get(row["causa"], None)
    if info: return pd.Series({"nombre":info[0],"desc":info[1],"cat":info[2]})
    return pd.Series({"nombre":f"Causa {row['causa']}","desc":"Desconocida","cat":"other"})
causa_cnt = causa_cnt.join(causa_cnt.apply(enrich_causa, axis=1))

c1, c2, c3 = st.columns([0.85, 0.85, 1.6])

with c1:
    vals  = [connected, ringback, no_conn - ringback]
    labs  = ["Conectadas","Con Ringback","Sin Conexión"]
    clrs  = [C["green"], C["yellow"], C["orange"]]
    fig = go.Figure(go.Pie(
        labels=labs, values=vals, hole=0.62,
        marker=dict(colors=clrs, line=dict(color=C["bg"],width=3)),
        textinfo="percent", textfont=dict(size=11,color=C["text"]),
        hovertemplate="<b>%{label}</b><br>%{value:,} · %{percent}<extra></extra>",
    ))
    fig.update_layout(**pl({"title":dict(text="Estado de Llamadas",font=dict(color=C["cyan"],size=12)),"height":290}))
    fig.add_annotation(
        text=f"<b>{asr_global:.0f}%</b><br><span style='font-size:9px'>ASR GLOBAL</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(family="Orbitron",size=14,color=C["green"] if asr_global>=50 else C["orange"]))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    mob = (df["traffic_type"]=="Móvil").sum()
    fij = (df["traffic_type"]=="Fijo").sum()
    fig = go.Figure(go.Pie(
        labels=["Móvil","Fijo"], values=[mob,fij], hole=0.62,
        marker=dict(colors=[C["purple"],C["cyan"]], line=dict(color=C["bg"],width=3)),
        textinfo="percent+label", textfont=dict(size=11,color=C["text"]),
        hovertemplate="<b>%{label}</b><br>%{value:,} · %{percent}<extra></extra>",
    ))
    fig.update_layout(**pl({"title":dict(text="Fijo vs Móvil",font=dict(color=C["cyan"],size=12)),"height":290}))
    fig.add_annotation(
        text=f"<b>{int(mob_pct)}%</b><br><span style='font-size:9px'>MÓVIL</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(family="Orbitron",size=14,color=C["purple"]))
    st.plotly_chart(fig, use_container_width=True)

with c3:
    top12 = causa_cnt.head(12)
    bar_colors = [CAT_COLORS.get(c, C["muted"]) for c in top12["cat"]]
    fig = go.Figure(go.Bar(
        y=top12["desc"], x=top12["count"],
        orientation="h",
        marker=dict(color=bar_colors, line=dict(color=C["bg"],width=0.5)),
        text=[f"{v:,}  ({p}%)" for v,p in zip(top12["count"],top12["pct"])],
        textposition="outside", textfont=dict(color=C["text"],size=9),
        hovertemplate="<b>%{y}</b><br>%{x:,} llamadas<extra></extra>",
    ))
    fig.update_layout(**pl({
        "height":290,
        "title":dict(text="Top Release Causes",font=dict(color=C["cyan"],size=12)),
        "yaxis":dict(autorange="reversed", gridcolor="#0d3a5e", zerolinecolor="#0d3a5e"),
        "xaxis":dict(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e"),
        "margin":dict(l=10,r=80,t=45,b=20),
    }))
    st.plotly_chart(fig, use_container_width=True)

# Causa distribution table
with st.expander("📋 Distribución completa de Release Causes — llamadas por causa"):
    tbl_causa = causa_cnt[["causa","nombre","desc","cat","count","pct"]].copy()
    tbl_causa.columns = ["Código Q.850","Nombre técnico","Descripción","Categoría","Llamadas","%"]
    st.dataframe(tbl_causa, hide_index=True, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DISTRIBUCIÓN POR DESTINO (con TMP master)
# ═══════════════════════════════════════════════════════════════════════════════
section("DISTRIBUCIÓN POR DESTINO")

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

# Bar chart with dual ASR lines
fig = make_subplots(specs=[[{"secondary_y":True}]])
fig.add_trace(go.Bar(
    name="Llamadas",
    x=dest_top["dest_nombre"], y=dest_top["llamadas"],
    marker=dict(
        color=dest_top["llamadas"],
        colorscale=[[0,"#0d3a5e"],[0.5,"#0066aa"],[1,C["cyan"]]],
    ),
    text=dest_top["llamadas"], textposition="outside",
    textfont=dict(size=9, color=C["cyan"]),
    hovertemplate="<b>%{x}</b><br>Llamadas: %{y:,}<extra></extra>",
))
fig.add_trace(go.Scatter(
    name="ASR Global %",
    x=dest_top["dest_nombre"], y=dest_top["asr_global_d"],
    mode="lines+markers+text",
    line=dict(color=C["yellow"], width=2, dash="dot"),
    marker=dict(size=5),
    text=dest_top["asr_global_d"].round(0).astype(int).astype(str)+"%",
    textposition="top center", textfont=dict(size=8, color=C["yellow"]),
), secondary_y=True)
fig.add_trace(go.Scatter(
    name="ASR Real %",
    x=dest_top["dest_nombre"], y=dest_top["asr_real_d"],
    mode="lines+markers+text",
    line=dict(color=C["green"], width=2),
    marker=dict(size=6),
    text=dest_top["asr_real_d"].round(0).astype(int).astype(str)+"%",
    textposition="bottom center", textfont=dict(size=8, color=C["green"]),
), secondary_y=True)
fig.add_hline(y=50, line_dash="dot", line_color=C["orange"],
              annotation_text="50% ASR", secondary_y=True)
fig.update_layout(**{**pl(),
    "height":360, "xaxis_tickangle":-40,
    "title":dict(text="Llamadas, ASR Global y ASR Real por destino (Top 30)",
                 font=dict(color=C["cyan"],size=12)),
    "legend":dict(font=dict(color=C["text"],size=9)),
    "yaxis2":dict(range=[0,130], gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", title="ASR %"),
})
st.plotly_chart(fig, use_container_width=True)

# Destination table
dest_show = dest_top.copy().rename(columns={
    "dest_nombre":"Destino","dest_modal":"Modalidad",
    "llamadas":"Llamadas","conectadas":"Conectadas",
    "minutos":"Minutos","asr_global_d":"ASR Global %","asr_real_d":"ASR Real %",
    "excluidas":"Excluidas (ASR Real)",
})
st.dataframe(dest_show[["Destino","Modalidad","Llamadas","Conectadas",
                          "Minutos","ASR Global %","ASR Real %","Excluidas (ASR Real)"]],
             hide_index=True, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISIS POR PROVEEDOR + RUTA
# ═══════════════════════════════════════════════════════════════════════════════
section("ANÁLISIS POR PROVEEDOR Y RUTA")

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

with st.expander("📋 Tabla completa proveedor / ruta"):
    st.dataframe(ruta_df.sort_values("llamadas",ascending=False).rename(columns={
        "proveedor":"Proveedor","ruta_dest":"Ruta","llamadas":"Llamadas",
        "conectadas":"Conectadas","excluidas":"Excluidas","asr_global":"ASR Global %",
        "asr_real":"ASR Real %",
    }), hide_index=True, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PROVEEDORES CAÍDOS / DEGRADADOS
# ═══════════════════════════════════════════════════════════════════════════════
section("DETECCIÓN DE PROVEEDORES CAÍDOS / DEGRADADOS")
down = prov_df[(prov_df["asr_real"]<5)  & (prov_df["llamadas"]>=10)]
deg  = prov_df[(prov_df["asr_real"]>=5) & (prov_df["asr_real"]<30) & (prov_df["llamadas"]>=10)]
cd1, cd2 = st.columns(2)
with cd1:
    st.markdown('<div style="font-family:Orbitron;font-size:0.72rem;color:#ff2d55;'
                'letter-spacing:2px;margin-bottom:6px;">🔴 POSIBLEMENTE CAÍDOS — ASR Real &lt; 5%</div>',
                unsafe_allow_html=True)
    if down.empty:
        st.markdown('<div style="color:#00ff88;font-family:Rajdhani;font-size:0.9rem;">'
                    '✓ Sin proveedores caídos</div>', unsafe_allow_html=True)
    else:
        st.dataframe(down[["proveedor","llamadas","conectadas","asr_global","asr_real"]].rename(
            columns={"proveedor":"Proveedor","llamadas":"Llamadas","conectadas":"Conectadas",
                     "asr_global":"ASR Global %","asr_real":"ASR Real %"}),
            hide_index=True, use_container_width=True)
with cd2:
    st.markdown('<div style="font-family:Orbitron;font-size:0.72rem;color:#ffcc00;'
                'letter-spacing:2px;margin-bottom:6px;">🟡 DEGRADADOS — ASR Real 5%–30%</div>',
                unsafe_allow_html=True)
    if deg.empty:
        st.markdown('<div style="color:#00ff88;font-family:Rajdhani;font-size:0.9rem;">'
                    '✓ Sin degradación detectada</div>', unsafe_allow_html=True)
    else:
        st.dataframe(deg[["proveedor","llamadas","conectadas","asr_global","asr_real"]].rename(
            columns={"proveedor":"Proveedor","llamadas":"Llamadas","conectadas":"Conectadas",
                     "asr_global":"ASR Global %","asr_real":"ASR Real %"}),
            hide_index=True, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PACKET LOSS / RTT / JITTER
# ═══════════════════════════════════════════════════════════════════════════════
section("DETECCIÓN: PACKET LOSS · RTT · JITTER")
pl_causas = [102,41,38,34,44,47]
pl_df     = df[df["Causa"].isin(pl_causas)]
pl_total  = len(pl_df)
pl_pct    = pl_total/total*100 if total else 0
c102      = int((df["Causa"]==102).sum())
c41       = int((df["Causa"]==41).sum())
short_ok  = df[df["is_connected"] & (df["Durac.Seg Total"]>0) & (df["Durac.Seg Total"]<3)]
sc_total  = len(short_ok)
sc_pct    = sc_total/connected*100 if connected else 0

pp1,pp2,pp3,pp4 = st.columns(4)
pp1.markdown(kpi_card("CAUSAS SOSPECHOSAS",   fmt_n(pl_total), f"{pl_pct:.1f}% del total",    "kpi-warn" if pl_pct>2 else ""), unsafe_allow_html=True)
pp2.markdown(kpi_card("CAUSA 102 — TIMER",    fmt_n(c102),     "Recovery/PL/RTT",              "kpi-warn" if c102>5  else ""), unsafe_allow_html=True)
pp3.markdown(kpi_card("CAUSA 41 — TEMP FAIL", fmt_n(c41),      "Falla temporal red",           "kpi-warn" if c41>5   else ""), unsafe_allow_html=True)
pp4.markdown(kpi_card("CONECTADAS &lt; 3 SEG",fmt_n(sc_total), f"{sc_pct:.1f}% conectadas",   "kpi-warn" if sc_pct>5 else "kpi-ok"), unsafe_allow_html=True)

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
    st.markdown('<div style="color:#00ff88;font-family:Rajdhani;font-size:0.9rem;padding:8px;">'
                '✓ Sin síntomas de packet loss o RTT detectados.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# REINTENTOS SIN CONEXIÓN
# ═══════════════════════════════════════════════════════════════════════════════
section("LLAMADAS AL MISMO NÚMERO SIN CONEXIÓN — REINTENTOS")
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

cr1, cr2 = st.columns([1.4, 1])
with cr1:
    top20 = retry.head(20)
    clrs  = [C["red"] if i<3 else (C["orange"] if i<8 else C["yellow"]) for i in range(len(top20))]
    fig = go.Figure(go.Bar(
        x=top20["num_b"], y=top20["intentos"],
        marker=dict(color=clrs),
        text=top20["intentos"], textposition="outside", textfont=dict(color=C["text"],size=9),
        customdata=np.stack([top20["causa_princ"],top20["proveedor"],top20["dest_nombre"]],axis=-1),
        hovertemplate="<b>%{x}</b><br>Intentos: %{y}<br>Causa: %{customdata[0]}<br>"
                      "Carrier: %{customdata[1]}<br>Destino: %{customdata[2]}<extra></extra>",
    ))
    fig.update_layout(**pl({
        "height":290, "xaxis_tickangle":-45,
        "title":dict(text="Top 20 números con más intentos fallidos",font=dict(color=C["cyan"],size=12)),
    }))
    st.plotly_chart(fig, use_container_width=True)
with cr2:
    st.dataframe(retry.head(25).rename(columns={
        "num_b":"Número B","intentos":"Intentos","causas_top":"Top 3 causas",
        "causa_princ":"Causa principal","proveedor":"Carrier","dest_nombre":"Destino",
    }), hide_index=True, use_container_width=True, height=290)

# ═══════════════════════════════════════════════════════════════════════════════
# TRAFFIC PROFILE — CARGA TEMPORAL (líneas + labels)
# ═══════════════════════════════════════════════════════════════════════════════
section("TRAFFIC PROFILE — CARGA TEMPORAL")

ts = (df.assign(minute=df["Fecha Inicio"].dt.floor("1min"))
        .groupby("minute")
        .agg(llamadas  =("Causa","count"),
             conectadas=("is_connected","sum"),
             minutos   =("duration_min","sum"),
             excluidas =("excl_asr_real","sum"))
        .reset_index())
ts["cps"]       = (ts["llamadas"]/60).round(2)
ts["no_conn"]   = ts["llamadas"] - ts["conectadas"]
ts["asr_g"]     = (ts["conectadas"]/ts["llamadas"]*100).round(1)
ts["ll_real"]   = ts["llamadas"] - ts["excluidas"]
ts["asr_r"]     = np.where(ts["ll_real"]>0,
                            (ts["conectadas"]/ts["ll_real"]*100).round(1), 0)
ts["hora"]      = ts["minute"].dt.strftime("%H:%M")

fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    row_heights=[0.45, 0.28, 0.27],
    vertical_spacing=0.06,
    subplot_titles=["Llamadas / minuto","CPS (Calls per Second)","ASR Global %  vs  ASR Real %"],
)

# Panel 1
fig.add_trace(go.Scatter(
    x=ts["hora"], y=ts["llamadas"], name="Total",
    mode="lines+markers+text", line=dict(color=C["cyan"],width=2),
    marker=dict(size=5),
    text=ts["llamadas"], textposition="top center", textfont=dict(size=8,color=C["cyan"]),
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

# Panel 2 — CPS
fig.add_trace(go.Scatter(
    x=ts["hora"], y=ts["cps"], name="CPS",
    mode="lines+markers+text", line=dict(color=C["yellow"],width=2),
    marker=dict(size=5),
    text=ts["cps"].round(2), textposition="top center", textfont=dict(size=8,color=C["yellow"]),
    fill="tozeroy", fillcolor="rgba(255,204,0,0.05)",
), row=2, col=1)

# Panel 3 — ASR Global vs Real
fig.add_trace(go.Scatter(
    x=ts["hora"], y=ts["asr_g"], name="ASR Global %",
    mode="lines+markers+text", line=dict(color=C["yellow"],width=1.5,dash="dot"),
    marker=dict(size=5),
    text=ts["asr_g"].astype(str)+"%", textposition="top center",
    textfont=dict(size=8,color=C["yellow"]),
), row=3, col=1)
fig.add_trace(go.Scatter(
    x=ts["hora"], y=ts["asr_r"], name="ASR Real %",
    mode="lines+markers+text", line=dict(color=C["green"],width=2),
    marker=dict(size=5,
                color=[C["red"] if a<30 else (C["yellow"] if a<60 else C["green"]) for a in ts["asr_r"]]),
    text=ts["asr_r"].astype(str)+"%", textposition="bottom center",
    textfont=dict(size=8,color=C["green"]),
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
# INSIGHTS — diagnóstico analítico detallado
# ═══════════════════════════════════════════════════════════════════════════════
section("DIAGNÓSTICO AUTOMÁTICO — INSIGHTS")

top_causa_desc = causa_cnt.iloc[0]["desc"] if not causa_cnt.empty else "N/D"
top_causa_pct  = causa_cnt.iloc[0]["pct"]  if not causa_cnt.empty else 0
top_prov       = prov_df.sort_values("llamadas",ascending=False).iloc[0] if not prov_df.empty else None
top_dest       = dest_df.sort_values("llamadas",ascending=False).iloc[0] if not dest_df.empty else None
prov_conc      = top_prov["llamadas"]/total*100 if top_prov is not None else 0

# 1. ASR comparación
delta_asr = asr_real - asr_global
insight("ASR GLOBAL vs ASR REAL — INTERPRETACIÓN",
    f"<b>ASR Global: {asr_global:.2f}%</b> · <b>ASR Real: {asr_real:.2f}%</b> "
    f"(diferencia: +{delta_asr:.2f} pp). "
    f"Se excluyeron <b>{fmt_n(excl_count)} llamadas</b> del denominador del ASR Real "
    f"(cortes por decisión del destino: ocupado, no responde, abonado ausente, etc.). "
    + ("La diferencia significativa indica que <b>gran parte de las fallas son por comportamiento del destino</b>, "
       "no por problemas en la red Darwin." if delta_asr > 20 else
       "La diferencia reducida sugiere que las fallas tienen origen mayoritariamente en la infraestructura."),
    "ok" if asr_real >= 50 else "warn")

# 2. Perfil global
if asr_real < 30:
    insight("ASR REAL CRÍTICO — REVISAR RUTAS Y CARRIERS",
        f"ASR Real <b>{asr_real:.2f}%</b> — muy por debajo del umbral operativo (>50%). "
        f"Causa dominante: <b>{top_causa_desc}</b> ({top_causa_pct}%). "
        f"Revisar disponibilidad de carriers, rutas configuradas en Darwin y estado de trunks SIP.", "warn")
elif asr_real < 50:
    insight("ASR REAL BAJO — INVESTIGAR",
        f"ASR Real <b>{asr_real:.2f}%</b> — por debajo del umbral. "
        f"Causa principal: <b>{top_causa_desc}</b> ({top_causa_pct}%). "
        f"Verificar si algún carrier o destino específico está traccionando el indicador a la baja.", "warn")
else:
    insight("ASR REAL EN RANGO OPERATIVO",
        f"ASR Real <b>{asr_real:.2f}%</b> — dentro de valores operativos normales. "
        f"Causa de liberación más frecuente: <b>{top_causa_desc}</b> ({top_causa_pct}%).", "ok")

# 3. Perfil de tráfico
insight("PERFIL DE TRÁFICO — DESTINOS, CONCENTRACIÓN Y TIPO",
    f"Destino con mayor volumen: <b>{top_dest['dest_nombre'] if top_dest is not None else 'N/D'}</b> "
    f"({fmt_n(top_dest['llamadas']) if top_dest is not None else 0} llamadas · "
    f"ASR Real {top_dest['asr_real_d']:.0f}% · "
    f"ASR Global {top_dest['asr_global_d']:.0f}%). "
    f"Composición: <b>{int(mob_pct)}% Móvil</b> / <b>{100-int(mob_pct)}% Fijo</b>. "
    f"Proveedor dominante: <b>{top_prov['proveedor'] if top_prov is not None else 'N/D'}</b> "
    f"({prov_conc:.0f}% del total). "
    + ("<b>Alta concentración en un solo carrier</b> — riesgo de impacto masivo si ese proveedor falla." if prov_conc>70
       else "Distribución de tráfico aceptable entre carriers."))

# 4. CPS
if peak_cps > 10:
    insight("PICO DE CPS ELEVADO — POSIBLE SATURACIÓN",
        f"Peak detectado: <b>{peak_cps:.2f} CPS</b> (promedio: {avg_cps:.2f} CPS). "
        f"Un CPS elevado puede saturar los recursos SIP/RTP de Darwin y generar causa 34 (no circuit). "
        f"Verificar dimensionamiento de trunks y configurar límites de CPS en el switch.", "warn")
else:
    insight("CPS EN RANGO NORMAL",
        f"CPS promedio: <b>{avg_cps:.2f}</b> · Peak: <b>{peak_cps:.2f}</b>. "
        f"Sin señales de saturación de capacidad.", "ok")

# 5. Congestión
cong_total = (df["causa_cat"]=="congestion").sum()
cong_pct   = cong_total/total*100 if total else 0
if cong_pct > 3:
    cong_detail = " | ".join([
        f"{r['desc']} ({r['pct']}%)"
        for _,r in causa_cnt[causa_cnt["cat"]=="congestion"].head(2).iterrows()
    ])
    insight("CONGESTIÓN DETECTADA",
        f"<b>{fmt_n(int(cong_total))} llamadas ({cong_pct:.1f}%)</b> con causas de congestión. "
        f"Detalle: <b>{cong_detail}</b>. "
        f"Puede indicar saturación de trunks salientes o falta de capacidad en el carrier. "
        f"Revisar dimensionamiento y activar rutas de overflow si están disponibles.", "warn")

# 6. Errores de número
err_total = int(causa_cnt[causa_cnt["cat"]=="error"]["count"].sum())
err_pct   = err_total/total*100 if total else 0
if err_pct > 10:
    insight("ALTO PORCENTAJE DE ERRORES DE NÚMERO / RUTA",
        f"<b>{fmt_n(err_total)} llamadas ({err_pct:.1f}%)</b> fallaron por errores de número o ruta. "
        f"Puede indicar problemas en la tabla de traducción del cliente, números portados sin actualizar, "
        f"o destinos no configurados correctamente en Darwin.", "warn")

# 7. Packet loss / RTT
if c102 > 0 or pl_pct > 2:
    insight("SÍNTOMAS DE PACKET LOSS / RTT / JITTER DETECTADOS",
        f"<b>{fmt_n(pl_total)} eventos ({pl_pct:.1f}%)</b> compatibles con problemas de red. "
        f"Causa 102 (Recovery on Timer Expiry): <b>{c102}</b> — timeout en señalización SIP, "
        f"compatible con pérdida de paquetes o latencia elevada (RTT). "
        f"Causa 41 (Temp Failure): <b>{c41}</b>. "
        f"Síntomas esperados: audio entrecortado, one-way audio, cortes abruptos. "
        f"Acción: captura PCAP/RTP, análisis con Wireshark o Homer SIP, "
        f"verificar QoS y jitter en el enlace IP entre cliente y Darwin.", "warn")
else:
    insight("SIN SÍNTOMAS DE PL/RTT/JITTER",
        "No se detectaron causas compatibles con problemas de red en este CDR.", "ok")

# 8. Llamadas cortas
if sc_pct > 5:
    insight("LLAMADAS CORTAS CONECTADAS — POSIBLE PROBLEMA DE AUDIO",
        f"<b>{fmt_n(sc_total)} llamadas ({sc_pct:.1f}% de las conectadas)</b> duraron menos de 3 segundos. "
        f"Síntoma clásico de one-way audio, packet loss unidireccional o incompatibilidad de codecs. "
        f"Cruzar con análisis de MOS y captura RTP. Verificar negociación SDP.", "warn")

# 9. Reintentos
max_retry = retry["intentos"].iloc[0] if not retry.empty else 0
if max_retry > 10:
    insight("NÚMERO CON ALTO REINTENTO SIN CONEXIÓN",
        f"Número <b>{retry['num_b'].iloc[0]}</b>: <b>{max_retry} intentos</b> sin conectar. "
        f"Causa dominante: <b>{retry['causa_princ'].iloc[0]}</b>. "
        f"Carrier: <b>{retry['proveedor'].iloc[0]}</b>. "
        f"Verificar validez del número, portabilidad y si hay bloqueo en el carrier.", "warn")

# 10. Destinos con ASR Real bajo
low_dest = dest_df[(dest_df["asr_real_d"]<20) & (dest_df["llamadas"]>=30)]
if not low_dest.empty:
    names = ", ".join(low_dest.sort_values("llamadas",ascending=False).head(5)["dest_nombre"].tolist())
    insight("DESTINOS CON ASR REAL BAJO",
        f"Destinos con ASR Real < 20% y volumen relevante: <b>{names}</b>. "
        f"Revisar cobertura del carrier en esas zonas, configuración de rutas "
        f"y si los números tienen alta tasa de inválidos/portados.", "warn")

# 11. Proveedores caídos
if not down.empty:
    names = ", ".join(down["proveedor"].tolist())
    insight("PROVEEDOR(ES) POSIBLEMENTE CAÍDO(S)",
        f"Carriers con ASR Real < 5%: <b>{names}</b>. "
        f"Con volumen significativo y casi cero conexiones, es probable que estos carriers no respondan. "
        f"Verificar rutas en Darwin, estado del enlace SIP y contactar al carrier.", "warn")

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTAR PDF
# ═══════════════════════════════════════════════════════════════════════════════
section("EXPORTAR REPORTE")
st.markdown('<div style="font-family:Rajdhani;font-size:0.9rem;color:#3a7ca5;margin-bottom:10px;">'
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
    f'<div style="font-family:Share Tech Mono;color:#1a4060;font-size:0.62rem;'
    f'text-align:center;margin-top:18px;">'
    f'DARWIN CDR ANALYTICS · IPLAN · {fecha_cdr_s} {hora_prim}–{hora_ult} · {cdr_name}'
    f'</div>', unsafe_allow_html=True)
