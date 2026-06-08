import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import io
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
  text-shadow:0 0 20px #00d4ff88,0 0 40px #00d4ff44; letter-spacing:4px; text-align:center; margin-bottom:0;
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
.kpi-desc  { font-family:'Rajdhani',sans-serif; font-size:0.72rem; color:#3a7ca5; letter-spacing:2px; text-transform:uppercase; margin-bottom:5px; }
.kpi-value { font-family:'Orbitron',monospace; font-size:1.65rem; font-weight:700; color:#00d4ff; text-shadow:0 0 10px #00d4ff88; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:0.7rem; margin-top:3px; }
.kpi-warn  { color:#ff6b35; }
.kpi-ok    { color:#00ff88; }

/* Meta bar */
.meta-grid {
  display:grid; grid-template-columns:repeat(5,1fr); gap:0;
  background:#030f20; border:1px solid #0d3a5e; border-radius:8px;
  overflow:hidden; margin-bottom:4px;
}
.meta-cell {
  padding:14px 18px; border-right:1px solid #0d3a5e;
  display:flex; flex-direction:column; gap:4px;
}
.meta-cell:last-child { border-right:none; }
.meta-label {
  font-family:'Rajdhani',sans-serif; font-weight:600; font-size:0.65rem;
  color:#3a7ca5; letter-spacing:3px; text-transform:uppercase;
}
.meta-value {
  font-family:'Rajdhani',sans-serif; font-weight:700; font-size:1.05rem;
  color:#e0f4ff; letter-spacing:1px;
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
  font-family:'Rajdhani',sans-serif; font-size:0.9rem; color:#b0d4e8; line-height:1.55;
}
.insight-warn { border-left-color:#ff6b35; background:linear-gradient(135deg,#160800,#0d0400); color:#ffbe96; }
.insight-ok   { border-left-color:#00ff88; background:linear-gradient(135deg,#001a0a,#00100a); color:#90ffcc; }
.insight-title { font-family:'Orbitron',monospace; font-size:0.68rem; letter-spacing:3px; margin-bottom:4px; }

h1,h2,h3 { color:#00d4ff !important; }
.stButton>button {
  background:linear-gradient(135deg,#041625,#0d3a5e) !important;
  border:1px solid #00d4ff !important; color:#00d4ff !important;
  font-family:'Orbitron',monospace !important; letter-spacing:2px !important;
  padding:10px 28px !important;
}
div[data-testid="metric-container"] { background:#041625 !important; border:1px solid #0d3a5e !important; border-radius:6px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Paths ────────────────────────────────────────────────────────────────────
CDR_FOLDER  = Path(r"C:\Users\rdangelo\reportes_python_2026\analitycs_cdrs_darwin\datos_cdr_darwin")
TMP_FOLDER  = Path(r"C:\Users\rdangelo\reportes_python_2026\analitycs_cdrs_darwin\tmp_darwin")

# ─── Causa dictionary ─────────────────────────────────────────────────────────
CAUSA_MAP = {
    1:  ("Unallocated Number",          "Número no asignado / inválido",           "error"),
    2:  ("No Route to Destination",     "Sin ruta al destino",                     "error"),
    3:  ("No Route to Transit",         "Sin ruta de tránsito",                    "error"),
    6:  ("Channel Unacceptable",        "Canal no aceptable",                      "warning"),
    16: ("Normal Clearing",             "Corte normal",                            "normal"),
    17: ("User Busy",                   "Número ocupado",                          "warning"),
    18: ("No User Responding",          "Sin respuesta — timeout ring",            "warning"),
    19: ("No Answer",                   "Sin contestación",                        "warning"),
    20: ("Subscriber Absent",           "Abonado ausente / apagado",               "warning"),
    21: ("Call Rejected",               "Llamada rechazada",                       "warning"),
    22: ("Number Changed",              "Número cambiado",                         "error"),
    27: ("Destination Out of Order",    "Destino fuera de servicio",               "error"),
    28: ("Invalid Number Format",       "Formato de número inválido",              "error"),
    31: ("Normal Unspecified",          "Corte normal sin especificar",            "normal"),
    34: ("No Circuit Available",        "Sin circuito — CONGESTIÓN",               "congestion"),
    38: ("Network Out of Order",        "Red fuera de servicio",                   "error"),
    41: ("Temporary Failure",           "Falla temporal de red",                   "warning"),
    42: ("Switching Equip Congestion",  "Congestión switching",                    "congestion"),
    44: ("Requested Circuit Unavail",   "Circuito no disponible",                  "congestion"),
    47: ("Resources Unavailable",       "Recursos no disponibles",                 "congestion"),
    50: ("Facility Not Subscribed",     "Servicio no suscripto",                   "error"),
    55: ("Incoming Calls Barred",       "Llamadas entrantes bloqueadas",           "error"),
    57: ("Bearer Cap Not Auth",         "Capacidad portadora no autorizada",       "error"),
    58: ("Bearer Cap Unavailable",      "Capacidad portadora no disponible",       "warning"),
    65: ("Bearer Cap Not Implemented",  "Capacidad portadora no implementada",     "error"),
    79: ("Not Implemented Unspec",      "No implementado sin especificar",         "error"),
    87: ("User Not Member CUG",         "Usuario no miembro grupo cerrado",        "error"),
    88: ("Incompatible Destination",    "Destino incompatible",                    "error"),
    95: ("Invalid Message",             "Mensaje inválido",                        "error"),
    96: ("Mandatory IE Missing",        "IE obligatorio faltante",                 "error"),
    97: ("Message Type Non-Existent",   "Tipo de mensaje inexistente",             "error"),
    100:("Invalid IE Contents",         "Contenido de IE inválido",                "error"),
    101:("Wrong Message State",         "Estado de mensaje incorrecto",            "error"),
    102:("Recovery on Timer Expiry",    "Recovery por timeout — PL/RTT/Jitter",   "packet_loss"),
    111:("Protocol Error Unspecified",  "Error de protocolo sin especificar",      "error"),
    127:("Interworking Unspecified",    "Error de interworking",                   "error"),
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

# ─── Data loaders ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_prefix_master(raw: bytes) -> dict:
    df = pd.read_csv(io.BytesIO(raw), sep=";", low_memory=False)
    df.columns = df.columns.str.strip()
    df["Prefijo"] = df["Prefijo"].astype(str).str.strip()
    return {
        "desc":  dict(zip(df["Prefijo"], df["Descripcion"])),
        "modal": dict(zip(df["Prefijo"], df["Modalidad"])),
        "grupo": dict(zip(df["Prefijo"], df["Grupo Destino"])),
    }

@st.cache_data(show_spinner=False)
def load_cdr(raw: bytes, pm_raw: bytes | None) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(raw), sep=";", low_memory=False)
    df.columns = df.columns.str.strip()

    for c in ["Fecha Inicio","Fecha Alert","Fecha Conexion","Fecha Desconexion"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    df["Durac.Seg Total"] = pd.to_numeric(df["Durac.Seg Total"], errors="coerce").fillna(0)
    df["Causa"]           = pd.to_numeric(df["Causa"], errors="coerce").fillna(0).astype(int)
    df["is_connected"]    = df["Fecha Conexion"].notna() & (df["Durac.Seg Total"] > 0)
    df["has_ringback"]    = df["Fecha Alert"].notna() & ~df["is_connected"]
    df["not_connected"]   = ~df["is_connected"]
    df["duration_min"]    = df["Durac.Seg Total"] / 60
    df["proveedor"]       = df["Carrier Destino"].fillna("Desconocido").str.strip()
    df["ruta_dest"]       = df["Ruta Dest"].fillna("Desconocida").str.strip()
    df["pref_str"]        = df["Prefijo Dest"].astype(str).str.strip()
    df["causa_cat"]       = df["Causa"].map(lambda x: CAUSA_MAP.get(x,("","","other"))[2])

    # Mobile/Fijo from prefix
    p = df["pref_str"]
    df["traffic_type"] = np.where(
        p.str.startswith("115") | p.str.startswith("116") | p.str.startswith("113"),
        "Móvil", "Fijo"
    )

    # Prefix master join
    if pm_raw:
        pm = load_prefix_master(pm_raw)
        df["dest_nombre"] = df["pref_str"].map(pm["desc"]).fillna("Desconocido")
        df["dest_modal"]  = df["pref_str"].map(pm["modal"]).fillna("Desconocido")
        df["dest_grupo"]  = df["pref_str"].map(pm["grupo"]).fillna("Desconocido")
    else:
        df["dest_nombre"] = df["pref_str"]
        df["dest_modal"]  = "N/D"
        df["dest_grupo"]  = "N/D"

    return df

# ─── File discovery ───────────────────────────────────────────────────────────
def discover_files(folder: Path):
    """Returns (cdr_path, maestro_path) from folder. CDR = only non-maestro csv."""
    if not folder.exists():
        return None, None
    csvs = list(folder.glob("*.csv"))
    maestro = next((f for f in csvs if f.name.lower().startswith("maestro")), None)
    cdrs    = [f for f in csvs if not f.name.lower().startswith("maestro")]
    cdr     = sorted(cdrs, key=lambda f: f.stat().st_mtime, reverse=True)[0] if cdrs else None
    return cdr, maestro

# ═════════════════════════════════════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">📡 DARWIN CDR ANALYTICS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">IPLAN · PLATAFORMA DE ANÁLISIS DE TRÁFICO EN TIEMPO REAL</div>', unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00d4ff;letter-spacing:2px;font-size:0.82rem;margin-bottom:10px;">📁 CONFIGURACIÓN</div>', unsafe_allow_html=True)

    cdr_folder_str = st.text_input("Carpeta datos CDR", value=str(CDR_FOLDER), label_visibility="visible")
    tmp_folder_str = st.text_input("Carpeta temporal (PDF)", value=str(TMP_FOLDER), label_visibility="visible")

    cdr_folder = Path(cdr_folder_str)
    tmp_folder = Path(tmp_folder_str)

    raw_cdr     = None
    raw_maestro = None
    cdr_name    = ""
    maestro_name= ""

    # Auto-discover
    cdr_path, maestro_path = discover_files(cdr_folder)

    if cdr_path:
        st.markdown(f'<div style="color:#00ff88;font-family:Share Tech Mono;font-size:0.7rem;margin-top:6px;">✓ CDR: {cdr_path.name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#3a7ca5;font-family:Share Tech Mono;font-size:0.67rem;">🕐 {pd.Timestamp(cdr_path.stat().st_mtime,unit="s").strftime("%Y-%m-%d %H:%M")} · {cdr_path.stat().st_size/1024:.0f} KB</div>', unsafe_allow_html=True)
        with open(cdr_path,"rb") as f: raw_cdr = f.read()
        cdr_name = cdr_path.name
    else:
        st.markdown(f'<div style="color:#ff6b35;font-family:Share Tech Mono;font-size:0.7rem;">⚠ Sin CDR en carpeta</div>', unsafe_allow_html=True)

    if maestro_path:
        st.markdown(f'<div style="color:#ffcc00;font-family:Share Tech Mono;font-size:0.7rem;margin-top:2px;">📋 Maestro: {maestro_path.name}</div>', unsafe_allow_html=True)
        with open(maestro_path,"rb") as f: raw_maestro = f.read()
        maestro_name = maestro_path.name
    else:
        st.markdown(f'<div style="color:#3a7ca5;font-family:Share Tech Mono;font-size:0.7rem;margin-top:2px;">ℹ Sin maestro de prefijos</div>', unsafe_allow_html=True)

    # Manual upload fallback
    st.markdown('<div style="font-family:Share Tech Mono;color:#3a7ca5;font-size:0.65rem;margin:10px 0 3px;">— SUBIR MANUALMENTE —</div>', unsafe_allow_html=True)
    up_cdr = st.file_uploader("CDR (.csv)", type=["csv"], key="up_cdr", label_visibility="collapsed")
    up_mae = st.file_uploader("Maestro (.csv)", type=["csv"], key="up_mae", label_visibility="collapsed")
    if up_cdr: raw_cdr = up_cdr.read(); cdr_name = up_cdr.name
    if up_mae: raw_maestro = up_mae.read(); maestro_name = up_mae.name

    # Demo fallback
    if raw_cdr is None:
        for demo in ["/mnt/user-data/uploads/reportCDR-08-06-26-01-56-38.csv"]:
            try:
                with open(demo,"rb") as f: raw_cdr = f.read()
                cdr_name = Path(demo).name
                st.markdown('<div style="color:#ffcc00;font-family:Share Tech Mono;font-size:0.7rem;">⚡ CDR DEMO</div>', unsafe_allow_html=True)
                break
            except: pass
    if raw_maestro is None:
        for demo in ["/mnt/user-data/uploads/Maestro_de_prefijos-08-06-26-03-44-17.csv"]:
            try:
                with open(demo,"rb") as f: raw_maestro = f.read()
                maestro_name = Path(demo).name
                break
            except: pass

    st.markdown("---")
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00d4ff;letter-spacing:2px;font-size:0.78rem;margin-bottom:8px;">FILTROS</div>', unsafe_allow_html=True)

if raw_cdr is None:
    st.info("📂 No se encontró ningún CDR. Verificá la carpeta o subí el archivo manualmente.")
    st.stop()

df = load_cdr(raw_cdr, raw_maestro)

# Sidebar filters
with st.sidebar:
    provs    = sorted(df["proveedor"].unique())
    rutas    = sorted(df["ruta_dest"].unique())
    tipos    = sorted(df["traffic_type"].unique())
    sel_prov = st.multiselect("Proveedor destino", provs,  default=provs)
    sel_ruta = st.multiselect("Ruta destino",      rutas,  default=rutas)
    sel_tipo = st.multiselect("Tipo destino",       tipos,  default=tipos)

mask = (df["proveedor"].isin(sel_prov) &
        df["ruta_dest"].isin(sel_ruta) &
        df["traffic_type"].isin(sel_tipo))
df = df[mask]
if df.empty:
    st.warning("Sin datos para los filtros seleccionados."); st.stop()

# ─── Core metrics ─────────────────────────────────────────────────────────────
total     = len(df)
connected = int(df["is_connected"].sum())
ringback  = int(df["has_ringback"].sum())
no_conn   = int(df["not_connected"].sum())
tot_min   = df["duration_min"].sum()
asr       = connected / total * 100 if total else 0
t_span    = (df["Fecha Inicio"].max() - df["Fecha Inicio"].min()).total_seconds()
avg_cps   = total / t_span if t_span > 0 else 0
pm_ts     = df.groupby(df["Fecha Inicio"].dt.floor("1min")).size()
peak_cps  = pm_ts.max() / 60 if not pm_ts.empty else 0
mob_pct   = (df["traffic_type"]=="Móvil").sum() / total * 100 if total else 0

carrier_ent = df["Carrier Origen"].dropna().mode().iloc[0] if not df["Carrier Origen"].dropna().empty else "N/D"
ruta_ent    = df["Ruta Orig"].dropna().mode().iloc[0]      if not df["Ruta Orig"].dropna().empty else "N/D"
fecha_cdr_s = df["Fecha Inicio"].min().strftime("%Y-%m-%d") if pd.notna(df["Fecha Inicio"].min()) else "N/D"
hora_prim   = df["Fecha Inicio"].min().strftime("%H:%M:%S") if pd.notna(df["Fecha Inicio"].min()) else "N/D"
hora_ult    = df["Fecha Inicio"].max().strftime("%H:%M:%S") if pd.notna(df["Fecha Inicio"].max()) else "N/D"

# ═════════════════════════════════════════════════════════════════════════════
# KPIs
# ═════════════════════════════════════════════════════════════════════════════
section("KPIs PRINCIPALES")
cols = st.columns(6)
kpis = [
    ("TOTAL RECIBIDAS",  fmt_n(total),       None,                            ""),
    ("CONECTADAS",       fmt_n(connected),   f"{connected/total*100:.0f}% del total", "kpi-ok" if asr>50 else "kpi-warn"),
    ("CON RINGBACK",     fmt_n(ringback),    f"{ringback/total*100:.0f}% del total",  ""),
    ("NO CONECTADAS",    fmt_n(no_conn),     f"{no_conn/total*100:.0f}% del total",   "kpi-warn" if no_conn/total>0.5 else ""),
    ("ASR",              f"{int(asr)}%",     "Answer Seizure Ratio",          "kpi-ok" if asr>50 else "kpi-warn"),
    ("CPS PROMEDIO",     f"{avg_cps:.2f}",   f"Peak {peak_cps:.2f} cps",     "kpi-warn" if peak_cps>10 else ""),
]
for col,(desc,val,sub,cls) in zip(cols, kpis):
    col.markdown(kpi_card(desc,val,sub,cls), unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# META BAR
# ═════════════════════════════════════════════════════════════════════════════
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

# ═════════════════════════════════════════════════════════════════════════════
# PERFIL DE TRÁFICO  +  RELEASE CAUSES
# ═════════════════════════════════════════════════════════════════════════════
section("PERFIL DE TRÁFICO  ·  RELEASE CAUSES")

# Build causa data
causa_cnt = df["Causa"].value_counts().reset_index()
causa_cnt.columns = ["causa","count"]
causa_cnt["pct"] = (causa_cnt["count"]/total*100).round(1)
def enrich_causa(row):
    info = CAUSA_MAP.get(row["causa"], None)
    if info: return pd.Series({"nombre":info[0],"desc":info[1],"cat":info[2]})
    return pd.Series({"nombre":f"Causa {row['causa']}","desc":"Desconocida","cat":"other"})
causa_cnt = causa_cnt.join(causa_cnt.apply(enrich_causa, axis=1))

c1, c2, c3 = st.columns([0.9, 0.9, 1.5])

with c1:
    # Call status donut
    vals   = [connected, ringback, no_conn - ringback]
    labs   = ["Conectadas","Con Ringback","Sin Conexión"]
    clrs   = [C["green"], C["yellow"], C["orange"]]
    fig = go.Figure(go.Pie(
        labels=labs, values=vals, hole=0.62,
        marker=dict(colors=clrs, line=dict(color=C["bg"],width=3)),
        textinfo="percent", textfont=dict(size=11,color=C["text"]),
        hovertemplate="<b>%{label}</b><br>%{value:,} llamadas · %{percent}<extra></extra>",
    ))
    fig.update_layout(**pl({"title":dict(text="Estado de Llamadas",font=dict(color=C["cyan"],size=12)),"height":280}))
    fig.add_annotation(text=f"<b>{int(asr)}%</b><br>ASR",
                       x=0.5, y=0.5, showarrow=False, align="center",
                       font=dict(family="Orbitron",size=15,color=C["green"] if asr>50 else C["orange"]))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    # Fijo vs Móvil donut
    mob = (df["traffic_type"]=="Móvil").sum()
    fij = (df["traffic_type"]=="Fijo").sum()
    fig = go.Figure(go.Pie(
        labels=["Móvil","Fijo"], values=[mob,fij], hole=0.62,
        marker=dict(colors=[C["purple"],C["cyan"]], line=dict(color=C["bg"],width=3)),
        textinfo="percent+label", textfont=dict(size=11,color=C["text"]),
        hovertemplate="<b>%{label}</b><br>%{value:,} · %{percent}<extra></extra>",
    ))
    fig.update_layout(**pl({"title":dict(text="Fijo vs Móvil",font=dict(color=C["cyan"],size=12)),"height":280}))
    fig.add_annotation(text=f"<b>{int(mob_pct)}%</b><br>MÓVIL",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(family="Orbitron",size=15,color=C["purple"]))
    st.plotly_chart(fig, use_container_width=True)

with c3:
    # Release causes bar + table side by side
    top10 = causa_cnt.head(10)
    bar_colors = [CAT_COLORS.get(c, C["muted"]) for c in top10["cat"]]
    fig = go.Figure(go.Bar(
        y=top10["desc"],
        x=top10["count"],
        orientation="h",
        marker=dict(color=bar_colors, line=dict(color=C["bg"],width=0.5)),
        text=[f"{v:,}  ({p}%)" for v,p in zip(top10["count"],top10["pct"])],
        textposition="outside",
        textfont=dict(color=C["text"],size=9),
        hovertemplate="<b>%{y}</b><br>%{x:,} llamadas<extra></extra>",
    ))
    fig.update_layout(**pl({
        "height":280,
        "title":dict(text="Top Release Causes",font=dict(color=C["cyan"],size=12)),
        "yaxis":dict(autorange="reversed", gridcolor="#0d3a5e", zerolinecolor="#0d3a5e"),
        "xaxis":dict(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e"),
        "margin":dict(l=10,r=60,t=45,b=20),
    }))
    st.plotly_chart(fig, use_container_width=True)

# Causa distribution table (below, full width)
with st.expander("📋 Distribución completa de Release Causes — llamadas por causa"):
    tbl_data = causa_cnt[["causa","nombre","desc","cat","count","pct"]].rename(columns={
        "causa":"Código Q.850","nombre":"Nombre técnico","desc":"Descripción",
        "cat":"Categoría","count":"Llamadas","pct":"%"
    })
    st.dataframe(tbl_data, hide_index=True, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# DISTRIBUCIÓN POR DESTINO
# ═════════════════════════════════════════════════════════════════════════════
section("DISTRIBUCIÓN POR DESTINO")

dest_df = df.groupby(["dest_nombre","dest_modal","dest_grupo"]).agg(
    llamadas  =("Causa","count"),
    conectadas=("is_connected","sum"),
    minutos   =("duration_min","sum"),
).reset_index()
dest_df["asr_d"]   = (dest_df["conectadas"]/dest_df["llamadas"]*100).round(0)
dest_df["minutos"] = dest_df["minutos"].round(1)
dest_top25 = dest_df.sort_values("llamadas",ascending=False).head(25)

# Bar + ASR dual axis
fig = make_subplots(specs=[[{"secondary_y":True}]])
fig.add_trace(go.Bar(
    name="Llamadas",
    x=dest_top25["dest_nombre"], y=dest_top25["llamadas"],
    marker=dict(color=dest_top25["llamadas"],
                colorscale=[[0,"#0d3a5e"],[0.5,"#0066aa"],[1,C["cyan"]]]),
    text=dest_top25["llamadas"], textposition="outside",
    textfont=dict(size=9,color=C["cyan"]),
    hovertemplate="<b>%{x}</b><br>Llamadas: %{y:,}<extra></extra>",
))
fig.add_trace(go.Scatter(
    name="ASR %",
    x=dest_top25["dest_nombre"], y=dest_top25["asr_d"],
    mode="lines+markers+text",
    line=dict(color=C["green"],width=2),
    marker=dict(size=6),
    text=dest_top25["asr_d"].astype(int).astype(str)+"%",
    textposition="top center", textfont=dict(size=8,color=C["green"]),
), secondary_y=True)
fig.add_hline(y=50, line_dash="dot", line_color=C["orange"],
              annotation_text="ASR 50%", secondary_y=True)
layout2 = {**pl(),
    "height":340, "xaxis_tickangle":-40, "barmode":"group",
    "title":dict(text="Llamadas y ASR% por destino (Top 25)",font=dict(color=C["cyan"],size=12)),
    "legend":dict(font=dict(color=C["text"])),
    "yaxis2":dict(range=[0,115], gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", title="ASR %"),
}
fig.update_layout(**layout2)
st.plotly_chart(fig, use_container_width=True)

# Destination table
dest_show = dest_top25.rename(columns={
    "dest_nombre":"Destino","dest_modal":"Modalidad","dest_grupo":"Grupo",
    "llamadas":"Llamadas","conectadas":"Conectadas","minutos":"Minutos","asr_d":"ASR %"
})
st.dataframe(dest_show, hide_index=True, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# ANÁLISIS POR PROVEEDOR + RUTA
# ═════════════════════════════════════════════════════════════════════════════
section("ANÁLISIS POR PROVEEDOR Y RUTA")

prov_df = df.groupby("proveedor").agg(
    llamadas  =("Causa","count"),
    conectadas=("is_connected","sum"),
    minutos   =("duration_min","sum"),
).reset_index()
prov_df["asr_p"] = (prov_df["conectadas"]/prov_df["llamadas"]*100).round(1)

ruta_df = df.groupby(["proveedor","ruta_dest"]).agg(
    llamadas  =("Causa","count"),
    conectadas=("is_connected","sum"),
    minutos   =("duration_min","sum"),
).reset_index()
ruta_df["asr_r"] = (ruta_df["conectadas"]/ruta_df["llamadas"]*100).round(1)

cp1, cp2 = st.columns(2)
with cp1:
    ps = prov_df.sort_values("llamadas", ascending=True)
    asr_dot_colors = [C["red"] if a<30 else (C["yellow"] if a<60 else C["green"]) for a in ps["asr_p"]]
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(
        name="Llamadas", y=ps["proveedor"].str[:28], x=ps["llamadas"],
        orientation="h", marker=dict(color=C["cyan"],opacity=0.75),
        text=ps["llamadas"], textposition="outside", textfont=dict(size=9),
    ))
    fig.add_trace(go.Scatter(
        name="ASR %", y=ps["proveedor"].str[:28], x=ps["asr_p"],
        mode="markers+text",
        marker=dict(color=asr_dot_colors,size=11,symbol="diamond"),
        text=ps["asr_p"].astype(str)+"%",
        textposition="middle right", textfont=dict(size=8,color=C["text"]),
    ), secondary_y=True)
    fig.update_layout(**pl({
        "height":280,
        "title":dict(text="Proveedor: Llamadas & ASR",font=dict(color=C["cyan"],size=12)),
        "yaxis2":dict(range=[0,130],gridcolor="#0d3a5e",zerolinecolor="#0d3a5e"),
        "xaxis":dict(gridcolor="#0d3a5e",zerolinecolor="#0d3a5e"),
        "legend":dict(font=dict(color=C["text"])),
        "margin":dict(l=10,r=60,t=45,b=20),
    }))
    st.plotly_chart(fig, use_container_width=True)

with cp2:
    rs = ruta_df.sort_values("llamadas",ascending=False)
    fig = go.Figure(go.Bar(
        x=rs["ruta_dest"].str[:22], y=rs["llamadas"],
        marker=dict(color=rs["llamadas"],colorscale=[[0,"#0d3a5e"],[1,C["purple"]]]),
        text=[f"{r}%  ({c:,})" for r,c in zip(rs["asr_r"].astype(int), rs["llamadas"])],
        textposition="outside", textfont=dict(color=C["text"],size=9),
        customdata=rs["proveedor"],
        hovertemplate="<b>%{x}</b><br>%{y:,} llamadas<br>ASR: %{text}<br>%{customdata}<extra></extra>",
    ))
    fig.update_layout(**pl({
        "height":280, "xaxis_tickangle":-25,
        "title":dict(text="Ruta destino: Llamadas & ASR",font=dict(color=C["cyan"],size=12)),
    }))
    st.plotly_chart(fig, use_container_width=True)

with st.expander("📋 Tabla completa proveedor / ruta"):
    st.dataframe(ruta_df.sort_values("llamadas",ascending=False).rename(columns={
        "proveedor":"Proveedor","ruta_dest":"Ruta","llamadas":"Llamadas",
        "conectadas":"Conectadas","minutos":"Minutos","asr_r":"ASR %"
    }), hide_index=True, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PROVEEDORES CAÍDOS / DEGRADADOS
# ═════════════════════════════════════════════════════════════════════════════
section("DETECCIÓN DE PROVEEDORES CAÍDOS / DEGRADADOS")
down = prov_df[(prov_df["asr_p"]<5)  & (prov_df["llamadas"]>=10)]
deg  = prov_df[(prov_df["asr_p"]>=5) & (prov_df["asr_p"]<30) & (prov_df["llamadas"]>=10)]
cd1, cd2 = st.columns(2)
with cd1:
    st.markdown('<div style="font-family:Orbitron;font-size:0.72rem;color:#ff2d55;letter-spacing:2px;margin-bottom:6px;">🔴 POSIBLEMENTE CAÍDOS — ASR &lt; 5%</div>', unsafe_allow_html=True)
    if down.empty:
        st.markdown('<div style="color:#00ff88;font-family:Rajdhani;font-size:0.9rem;">✓ Sin proveedores caídos detectados</div>', unsafe_allow_html=True)
    else:
        st.dataframe(down[["proveedor","llamadas","conectadas","asr_p"]].rename(columns={"proveedor":"Proveedor","llamadas":"Llamadas","conectadas":"Conectadas","asr_p":"ASR %"}), hide_index=True, use_container_width=True)
with cd2:
    st.markdown('<div style="font-family:Orbitron;font-size:0.72rem;color:#ffcc00;letter-spacing:2px;margin-bottom:6px;">🟡 DEGRADADOS — ASR 5%–30%</div>', unsafe_allow_html=True)
    if deg.empty:
        st.markdown('<div style="color:#00ff88;font-family:Rajdhani;font-size:0.9rem;">✓ Sin degradación detectada</div>', unsafe_allow_html=True)
    else:
        st.dataframe(deg[["proveedor","llamadas","conectadas","asr_p"]].rename(columns={"proveedor":"Proveedor","llamadas":"Llamadas","conectadas":"Conectadas","asr_p":"ASR %"}), hide_index=True, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PACKET LOSS / RTT / JITTER
# ═════════════════════════════════════════════════════════════════════════════
section("DETECCIÓN: PACKET LOSS · RTT · JITTER")
pl_causas = [102,41,38,34,44,47]
pl_df     = df[df["Causa"].isin(pl_causas)]
pl_total  = len(pl_df)
pl_pct    = pl_total/total*100 if total else 0
c102      = int((df["Causa"]==102).sum())
c41       = int((df["Causa"]==41).sum())
c38       = int((df["Causa"]==38).sum())
short_ok  = df[df["is_connected"] & (df["Durac.Seg Total"]>0) & (df["Durac.Seg Total"]<3)]
sc_total  = len(short_ok)
sc_pct    = sc_total/connected*100 if connected else 0

pp1,pp2,pp3,pp4 = st.columns(4)
pp1.markdown(kpi_card("CAUSAS SOSPECHOSAS", fmt_n(pl_total), f"{pl_pct:.1f}% del total", "kpi-warn" if pl_pct>2 else ""), unsafe_allow_html=True)
pp2.markdown(kpi_card("CAUSA 102 — TIMER", fmt_n(c102), "Recovery/PL/RTT", "kpi-warn" if c102>5 else ""), unsafe_allow_html=True)
pp3.markdown(kpi_card("CAUSA 41 — TEMP FAIL", fmt_n(c41), "Falla temporal red", "kpi-warn" if c41>5 else ""), unsafe_allow_html=True)
pp4.markdown(kpi_card("CONECTADAS &lt; 3 SEG", fmt_n(sc_total), f"{sc_pct:.1f}% conectadas", "kpi-warn" if sc_pct>5 else "kpi-ok"), unsafe_allow_html=True)

if pl_total > 0:
    pl_ts = pl_df.copy()
    pl_ts["minute"] = pl_ts["Fecha Inicio"].dt.floor("1min")
    pl_ts_agg = pl_ts.groupby(["minute","Causa"]).size().reset_index(name="n")
    pl_ts_agg["etiqueta"] = pl_ts_agg["Causa"].map(
        lambda c: f"C{c} — {CAUSA_MAP[c][0]}" if c in CAUSA_MAP else str(c))
    fig = px.bar(pl_ts_agg, x="minute", y="n", color="etiqueta",
                 color_discrete_sequence=[C["orange"],C["red"],C["purple"],C["yellow"],C["muted"]],
                 labels={"n":"Eventos","minute":"Hora","etiqueta":"Causa"})
    fig.update_layout(**pl({
        "height":230,
        "title":dict(text="Evolución temporal — síntomas PL/RTT/Jitter",font=dict(color=C["cyan"],size=12)),
        "legend":dict(font=dict(color=C["text"],size=9)),
    }))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown('<div style="color:#00ff88;font-family:Rajdhani;font-size:0.9rem;padding:8px;">✓ Sin síntomas de packet loss o RTT detectados en este CDR.</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# REINTENTOS SIN CONEXIÓN
# ═════════════════════════════════════════════════════════════════════════════
section("LLAMADAS AL MISMO NÚMERO SIN CONEXIÓN — REINTENTOS")
failed = df[~df["is_connected"]].copy()
failed["num_b"] = failed["Numero B Mod"].astype(str).str.replace(".0","",regex=False).str.strip()
retry = failed.groupby("num_b").agg(
    intentos    =("Causa","count"),
    causas_top  =("Causa", lambda x: " | ".join([f"C{k}:{v}" for k,v in x.value_counts().head(3).items()])),
    causa_princ =("Causa", lambda x: CAUSA_MAP.get(int(x.mode().iloc[0]),("","Desconocida",""))[1] if len(x)>0 else "N/D"),
    proveedor   =("proveedor", lambda x: x.mode().iloc[0] if len(x)>0 else "N/D"),
    dest_nombre =("dest_nombre", lambda x: x.mode().iloc[0] if len(x)>0 else "N/D"),
).reset_index().sort_values("intentos",ascending=False)

cr1, cr2 = st.columns([1.4,1])
with cr1:
    top20 = retry.head(20)
    bar_clrs = [C["red"] if i<3 else (C["orange"] if i<8 else C["yellow"]) for i in range(len(top20))]
    fig = go.Figure(go.Bar(
        x=top20["num_b"], y=top20["intentos"],
        marker=dict(color=bar_clrs),
        text=top20["intentos"], textposition="outside", textfont=dict(color=C["text"],size=9),
        customdata=np.stack([top20["causa_princ"], top20["proveedor"], top20["dest_nombre"]], axis=-1),
        hovertemplate="<b>%{x}</b><br>Intentos: %{y}<br>Causa: %{customdata[0]}<br>Carrier: %{customdata[1]}<br>Destino: %{customdata[2]}<extra></extra>",
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

# ═════════════════════════════════════════════════════════════════════════════
# TRAFFIC PROFILE — CARGA TEMPORAL (gráfico de líneas con labels)
# ═════════════════════════════════════════════════════════════════════════════
section("TRAFFIC PROFILE — CARGA TEMPORAL")

ts = (df.assign(minute=df["Fecha Inicio"].dt.floor("1min"))
        .groupby("minute")
        .agg(llamadas  =("Causa","count"),
             conectadas=("is_connected","sum"),
             minutos   =("duration_min","sum"))
        .reset_index())
ts["cps"]     = (ts["llamadas"]/60).round(2)
ts["asr_ts"]  = (ts["conectadas"]/ts["llamadas"]*100).round(1)
ts["no_conn"] = ts["llamadas"] - ts["conectadas"]
ts["hora"]    = ts["minute"].dt.strftime("%H:%M")

fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    row_heights=[0.45, 0.3, 0.25],
    vertical_spacing=0.06,
    subplot_titles=["Llamadas / minuto", "CPS  (Calls per Second)", "ASR  %"],
)

# Panel 1 — líneas llamadas conectadas / no conectadas
fig.add_trace(go.Scatter(
    x=ts["hora"], y=ts["llamadas"], name="Total llamadas",
    mode="lines+markers+text",
    line=dict(color=C["cyan"],width=2),
    marker=dict(size=5),
    text=ts["llamadas"], textposition="top center",
    textfont=dict(size=8,color=C["cyan"]),
    fill="tozeroy", fillcolor="rgba(0,212,255,0.06)",
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=ts["hora"], y=ts["conectadas"], name="Conectadas",
    mode="lines+markers",
    line=dict(color=C["green"],width=1.5, dash="dot"),
    marker=dict(size=4),
    fill="tozeroy", fillcolor="rgba(0,255,136,0.04)",
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=ts["hora"], y=ts["no_conn"], name="No conectadas",
    mode="lines+markers",
    line=dict(color=C["orange"],width=1.5),
    marker=dict(size=4),
), row=1, col=1)

# Panel 2 — CPS con labels
fig.add_trace(go.Scatter(
    x=ts["hora"], y=ts["cps"], name="CPS",
    mode="lines+markers+text",
    line=dict(color=C["yellow"],width=2),
    marker=dict(size=5),
    text=ts["cps"].round(2), textposition="top center",
    textfont=dict(size=8,color=C["yellow"]),
    fill="tozeroy", fillcolor="rgba(255,204,0,0.06)",
), row=2, col=1)

# Panel 3 — ASR% con labels
fig.add_trace(go.Scatter(
    x=ts["hora"], y=ts["asr_ts"], name="ASR %",
    mode="lines+markers+text",
    line=dict(color=C["green"],width=2),
    marker=dict(size=5, color=[C["red"] if a<30 else (C["yellow"] if a<60 else C["green"]) for a in ts["asr_ts"]]),
    text=ts["asr_ts"].astype(str)+"%", textposition="top center",
    textfont=dict(size=8,color=C["green"]),
), row=3, col=1)
fig.add_hline(y=50, line_dash="dot", line_color=C["orange"],
              annotation_text="50% ASR", annotation_font_color=C["orange"],
              row=3, col=1)

for r in [1,2,3]:
    fig.update_xaxes(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", row=r, col=1)
    fig.update_yaxes(gridcolor="#0d3a5e", zerolinecolor="#0d3a5e", row=r, col=1)

fig.update_layout(**{**pl(),
    "height":520, "showlegend":True,
    "legend":dict(font=dict(color=C["text"],size=9), orientation="h", y=1.02, x=0),
    "title":dict(text="Evolución temporal del tráfico — línea temporal completa",
                 font=dict(color=C["cyan"],size=12)),
})
st.plotly_chart(fig, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# INSIGHTS — diagnóstico analítico detallado
# ═════════════════════════════════════════════════════════════════════════════
section("DIAGNÓSTICO AUTOMÁTICO — INSIGHTS")

# ── 1. ASR global ──────────────────────────────────────────────────────────
top_causa_desc = causa_cnt.iloc[0]["desc"] if not causa_cnt.empty else "N/D"
top_causa_pct  = causa_cnt.iloc[0]["pct"]  if not causa_cnt.empty else 0

if asr < 10:
    insight("ASR CRÍTICO — POSIBLE FALLA MASIVA",
        f"ASR global <b>{int(asr)}%</b> — extremadamente bajo. Solo <b>{fmt_n(connected)}</b> de "
        f"<b>{fmt_n(total)}</b> llamadas se conectaron. "
        f"La causa más frecuente es <b>{top_causa_desc}</b> ({top_causa_pct}%). "
        f"Esto sugiere una falla en rutas salientes o en el carrier destino. "
        f"Verificar estado de trunks en Darwin y rutas configuradas.", "warn")
elif asr < 30:
    insight("ASR MUY BAJO — DEGRADACIÓN SEVERA",
        f"ASR <b>{int(asr)}%</b> — muy por debajo del umbral operativo (>50%). "
        f"Causa dominante: <b>{top_causa_desc}</b> ({top_causa_pct}%). "
        f"Posibles causas: congestión en carrier destino, prefijos mal rutados, "
        f"o degradación del enlace SIP saliente. Revisar rutas y carriers afectados.", "warn")
elif asr < 50:
    insight("ASR BAJO — REVISAR RUTAS",
        f"ASR <b>{int(asr)}%</b> — por debajo del umbral saludable. "
        f"Causa principal de fallas: <b>{top_causa_desc}</b> ({top_causa_pct}%). "
        f"Verificar si algún carrier específico está degradado.", "warn")
else:
    insight("ASR EN RANGO OPERATIVO",
        f"ASR global <b>{int(asr)}%</b>. Parámetro dentro de valores normales. "
        f"Causa de liberación más frecuente: <b>{top_causa_desc}</b> ({top_causa_pct}%).", "ok")

# ── 2. Perfil de tráfico ───────────────────────────────────────────────────
top_dest    = dest_df.sort_values("llamadas",ascending=False).iloc[0] if not dest_df.empty else None
top_prov    = prov_df.sort_values("llamadas",ascending=False).iloc[0] if not prov_df.empty else None
prov_conc   = top_prov["llamadas"]/total*100 if top_prov is not None else 0

insight("PERFIL DE TRÁFICO — DESTINOS Y CONCENTRACIÓN",
    f"Destino con mayor volumen: <b>{top_dest['dest_nombre'] if top_dest is not None else 'N/D'}</b> "
    f"({fmt_n(top_dest['llamadas']) if top_dest is not None else 0} llamadas, ASR {int(top_dest['asr_d']) if top_dest is not None else 0}%). "
    f"El tráfico es <b>{int(mob_pct)}% móvil</b> y <b>{100-int(mob_pct)}% fijo</b>. "
    f"Proveedor dominante: <b>{top_prov['proveedor'] if top_prov is not None else 'N/D'}</b> "
    f"concentra el <b>{prov_conc:.0f}%</b> del total de llamadas. "
    + (f"Alta concentración en un solo carrier — riesgo si ese proveedor falla." if prov_conc > 70 else
       "Distribución de tráfico entre múltiples carriers."))

# ── 3. CPS ─────────────────────────────────────────────────────────────────
if peak_cps > 10:
    insight("PICO DE CPS ELEVADO — RIESGO DE SATURACIÓN",
        f"Se detectó un pico de <b>{peak_cps:.2f} CPS</b> (promedio: {avg_cps:.2f}). "
        f"Un CPS alto puede saturar los recursos SIP y RTP disponibles, generando causa 34 (no circuit). "
        f"Verificar capacity planning, dimensionamiento de trunks y configuración de límites en Darwin.", "warn")
else:
    insight("CPS EN RANGO NORMAL",
        f"CPS promedio: <b>{avg_cps:.2f}</b> · Peak: <b>{peak_cps:.2f}</b>. "
        f"Sin señales de saturación de capacidad en el período analizado.", "ok")

# ── 4. Congestión ──────────────────────────────────────────────────────────
cong_total = (df["causa_cat"]=="congestion").sum()
cong_pct   = cong_total/total*100 if total else 0
if cong_pct > 5:
    cong_top = causa_cnt[causa_cnt["cat"]=="congestion"].head(2)
    cong_detail = " | ".join([f"{r['desc']} ({r['pct']}%)" for _,r in cong_top.iterrows()])
    insight("CONGESTIÓN DETECTADA",
        f"<b>{fmt_n(cong_total)} llamadas ({cong_pct:.1f}%)</b> fallaron por causas de congestión. "
        f"Causas: <b>{cong_detail}</b>. "
        f"Indica saturación de trunks salientes o falta de capacidad en el carrier destino. "
        f"Revisar dimensionamiento y activar rutas de overflow si están disponibles.", "warn")

# ── 5. Errores de número ────────────────────────────────────────────────────
err_total = causa_cnt[causa_cnt["cat"]=="error"]["count"].sum()
err_pct   = err_total/total*100 if total else 0
if err_pct > 10:
    insight("ALTO PORCENTAJE DE NÚMEROS INVÁLIDOS",
        f"<b>{fmt_n(int(err_total))} llamadas ({err_pct:.1f}%)</b> fallaron por errores de número "
        f"(inválido, sin ruta, fuera de servicio). "
        f"Puede indicar problemas en la tabla de traducción de números del cliente, "
        f"o marcaciones incorrectas hacia destinos no configurados en Darwin.", "warn")

# ── 6. Packet loss / RTT / Jitter ──────────────────────────────────────────
if c102 > 0 or pl_pct > 2:
    insight("SÍNTOMAS DE PACKET LOSS / RTT / JITTER",
        f"Detectados <b>{fmt_n(pl_total)} eventos ({pl_pct:.1f}%)</b> compatibles con problemas de red. "
        f"Causa 102 (Recovery on Timer Expiry): <b>{c102}</b> — indica timeouts en señalización SIP, "
        f"compatible con pérdida de paquetes o latencia excesiva. "
        f"Causa 41 (Temporal Failure): <b>{c41}</b>. "
        f"Estos síntomas pueden generar audio entrecortado, one-way audio o fallas de establecimiento. "
        f"Recomendación: captura RTP/PCAP y análisis con Wireshark o Homer SIP. "
        f"Verificar QoS en el enlace entre cliente y Darwin.", "warn")
else:
    insight("SIN SÍNTOMAS DE PL/RTT/JITTER",
        "No se detectaron causas compatibles con problemas de red (packet loss, delay, jitter) en este CDR.", "ok")

# ── 7. Llamadas cortas ──────────────────────────────────────────────────────
if sc_pct > 5:
    insight("LLAMADAS CORTAS CONECTADAS (< 3 SEG) — POSIBLE PROBLEMA DE AUDIO",
        f"<b>{fmt_n(sc_total)} llamadas ({sc_pct:.1f}% de las conectadas)</b> se establecieron pero "
        f"duraron menos de 3 segundos — síntoma clásico de problemas de audio: "
        f"packet loss unidireccional, one-way audio, o incompatibilidad de codecs. "
        f"Cruzar con análisis de MOS y captura RTP. Verificar negociación SDP.", "warn")

# ── 8. Reintentos ──────────────────────────────────────────────────────────
max_retry = retry["intentos"].iloc[0] if not retry.empty else 0
if max_retry > 10:
    top_num        = retry["num_b"].iloc[0]
    top_cause_desc = retry["causa_princ"].iloc[0]
    top_carrier    = retry["proveedor"].iloc[0]
    insight("NÚMERO CON ALTO REINTENTO SIN CONEXIÓN",
        f"El número <b>{top_num}</b> fue marcado <b>{max_retry} veces</b> sin conectar nunca. "
        f"Causa dominante: <b>{top_cause_desc}</b>. Carrier: <b>{top_carrier}</b>. "
        f"Verificar si el número existe, si está fuera de servicio, o si hay un bloqueo "
        f"específico en el carrier. Alta probabilidad de número inválido o portado.", "warn")

# ── 9. Proveedores caídos ──────────────────────────────────────────────────
if not down.empty:
    names = ", ".join(down["proveedor"].tolist())
    insight("PROVEEDOR(ES) POSIBLEMENTE CAÍDO(S)",
        f"Carriers con ASR < 5%: <b>{names}</b>. "
        f"Con volumen significativo de llamadas y casi cero conexiones, es probable que estos carriers "
        f"no estén respondiendo correctamente. Verificar rutas en Darwin, estado del BGP/SIP y "
        f"contactar al carrier para confirmar incidencia.", "warn")

# ── 10. ASR por destino ────────────────────────────────────────────────────
low_asr_dests = dest_df[(dest_df["asr_d"]<20) & (dest_df["llamadas"]>=50)]
if not low_asr_dests.empty:
    dest_names = ", ".join(low_asr_dests.sort_values("llamadas",ascending=False).head(5)["dest_nombre"].tolist())
    insight("DESTINOS CON ASR MUY BAJO",
        f"Los siguientes destinos tienen ASR < 20% con volumen relevante: <b>{dest_names}</b>. "
        f"Puede indicar problemas de cobertura del carrier en esas zonas, rutas mal configuradas "
        f"o destinos con alta proporción de números inválidos.", "warn")

# ═════════════════════════════════════════════════════════════════════════════
# EXPORTAR PDF
# ═════════════════════════════════════════════════════════════════════════════
section("EXPORTAR REPORTE")
st.markdown('<div style="font-family:Rajdhani;font-size:0.9rem;color:#3a7ca5;margin-bottom:10px;">Generá un PDF con el resumen ejecutivo. Se guarda también en la carpeta tmp_darwin.</div>', unsafe_allow_html=True)

if st.button("⬇  EXPORTAR REPORTE PDF"):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl_colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import cm

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)

        BG   = rl_colors.HexColor("#020b18")
        CYN  = rl_colors.HexColor("#00d4ff")
        GRN  = rl_colors.HexColor("#00ff88")
        ORN  = rl_colors.HexColor("#ff6b35")
        RED  = rl_colors.HexColor("#ff2d55")
        YEL  = rl_colors.HexColor("#ffcc00")
        WHT  = rl_colors.HexColor("#e0f4ff")
        DARK = rl_colors.HexColor("#041625")
        MID  = rl_colors.HexColor("#0d3a5e")
        MID2 = rl_colors.HexColor("#051a2e")

        styles = getSampleStyleSheet()
        ts_  = ParagraphStyle("T",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=18,textColor=CYN,alignment=1,spaceAfter=4)
        ss_  = ParagraphStyle("S",parent=styles["Normal"],fontName="Helvetica",fontSize=9,textColor=MID,alignment=1,spaceAfter=12)
        h2_  = ParagraphStyle("H2",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=11,textColor=CYN,spaceBefore=14,spaceAfter=6)
        bd_  = ParagraphStyle("B",parent=styles["Normal"],fontName="Helvetica",fontSize=8.5,textColor=WHT,leading=13,spaceAfter=4)
        wn_  = ParagraphStyle("W",parent=bd_,textColor=ORN)
        ok_  = ParagraphStyle("OK",parent=bd_,textColor=GRN)

        def tbl_rl(data, col_widths=None):
            t = Table(data, colWidths=col_widths)
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

        story = []
        story += [Paragraph("📡 DARWIN CDR ANALYTICS", ts_),
                  Paragraph("IPLAN · REPORTE DE TRÁFICO", ss_),
                  HRFlowable(width="100%",thickness=0.5,color=MID), Spacer(1,8)]

        story.append(Paragraph("INFORMACIÓN DEL CDR", h2_))
        story.append(tbl_rl([
            ["Carrier Entrante","Ruta Entrante","Fecha CDR","Primer CDR","Último CDR"],
            [carrier_ent, ruta_ent, fecha_cdr_s, hora_prim, hora_ult],
        ]))
        story.append(Spacer(1,10))

        story.append(Paragraph("KPIs PRINCIPALES", h2_))
        story.append(tbl_rl([
            ["Total","Conectadas","Ringback","No Conectadas","ASR","CPS Prom","CPS Peak"],
            [fmt_n(total),fmt_n(connected),fmt_n(ringback),fmt_n(no_conn),
             f"{int(asr)}%",f"{avg_cps:.2f}",f"{peak_cps:.2f}"],
        ]))
        story.append(Spacer(1,10))

        story.append(Paragraph("TOP RELEASE CAUSES", h2_))
        rc_rows = [["Código","Descripción","Categoría","Llamadas","%"]]
        for _,row in causa_cnt.head(10).iterrows():
            rc_rows.append([str(row["causa"]),row["desc"][:45],row["cat"],fmt_n(row["count"]),f"{row['pct']}%"])
        story.append(tbl_rl(rc_rows,[1.5*cm,7.5*cm,2.5*cm,2*cm,1.5*cm]))
        story.append(Spacer(1,10))

        story.append(Paragraph("TOP DESTINOS", h2_))
        dt_rows = [["Destino","Modalidad","Llamadas","Conectadas","Min","ASR"]]
        for _,row in dest_df.sort_values("llamadas",ascending=False).head(12).iterrows():
            dt_rows.append([row["dest_nombre"][:30],str(row["dest_modal"])[:12],
                            fmt_n(row["llamadas"]),fmt_n(row["conectadas"]),
                            f"{row['minutos']:.0f}",f"{row['asr_d']:.0f}%"])
        story.append(tbl_rl(dt_rows,[5*cm,2*cm,2.5*cm,2.5*cm,1.5*cm,1.5*cm]))
        story.append(Spacer(1,10))

        story.append(Paragraph("ANÁLISIS POR PROVEEDOR", h2_))
        pv_rows = [["Proveedor","Llamadas","Conectadas","Minutos","ASR"]]
        for _,row in prov_df.sort_values("llamadas",ascending=False).iterrows():
            pv_rows.append([row["proveedor"][:35],fmt_n(row["llamadas"]),
                            fmt_n(row["conectadas"]),f"{row['minutos']:.0f}",f"{row['asr_p']:.1f}%"])
        story.append(tbl_rl(pv_rows,[7*cm,2.5*cm,2.5*cm,2*cm,1.5*cm]))
        story.append(Spacer(1,10))

        if max_retry > 0:
            story.append(Paragraph("TOP REINTENTOS SIN CONEXIÓN", h2_))
            rt_rows = [["Número B","Intentos","Causa Principal","Carrier"]]
            for _,row in retry.head(10).iterrows():
                rt_rows.append([row["num_b"],fmt_n(row["intentos"]),
                                row["causa_princ"][:38],row["proveedor"][:25]])
            story.append(tbl_rl(rt_rows,[4.5*cm,2*cm,6.5*cm,3*cm]))
            story.append(Spacer(1,10))

        story.append(Paragraph("DIAGNÓSTICO AUTOMÁTICO", h2_))
        diag_items = []
        if asr < 40: diag_items.append(("warn", f"⚠ ASR {int(asr)}% — por debajo del umbral. Causa dominante: {top_causa_desc} ({top_causa_pct}%)."))
        else:        diag_items.append(("ok",   f"✓ ASR {int(asr)}% — operativo. Causa dominante: {top_causa_desc}."))
        if peak_cps > 10: diag_items.append(("warn", f"⚠ Peak CPS {peak_cps:.2f} — verificar capacity."))
        if c102>0 or pl_pct>2: diag_items.append(("warn", f"⚠ Síntomas PL/RTT/Jitter: {pl_total} eventos, Causa 102: {c102}."))
        if not down.empty: diag_items.append(("warn", f"⚠ Carrier(s) caído(s): {', '.join(down['proveedor'].tolist())}."))
        if cong_pct>5: diag_items.append(("warn", f"⚠ Congestión: {fmt_n(int(cong_total))} llamadas ({cong_pct:.1f}%)."))
        if sc_pct>5: diag_items.append(("warn", f"⚠ Llamadas cortas <3s: {sc_total} ({sc_pct:.1f}% de conectadas)."))
        if max_retry>10: diag_items.append(("warn", f"⚠ Número {retry['num_b'].iloc[0]}: {max_retry} intentos sin conectar."))

        for kind, text in diag_items:
            story.append(Paragraph(text, wn_ if kind=="warn" else ok_))

        story += [Spacer(1,14),
                  HRFlowable(width="100%",thickness=0.3,color=MID),
                  Paragraph(f"Generado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} · Archivo: {cdr_name} · DARWIN CDR Analytics · IPLAN", ss_)]

        doc.build(story)
        buf.seek(0)
        pdf_bytes = buf.getvalue()

        # Save to tmp folder
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
    f'<div style="font-family:Share Tech Mono;color:#1a4060;font-size:0.63rem;'
    f'text-align:center;margin-top:18px;">'
    f'DARWIN CDR ANALYTICS · IPLAN · {fecha_cdr_s} {hora_prim}–{hora_ult} · {cdr_name}</div>',
    unsafe_allow_html=True)
