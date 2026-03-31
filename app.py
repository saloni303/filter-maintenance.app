import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="HydroGuard · Filter Health Monitor",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg:     #060A10;
    --surf:   #0B1119;
    --card:   #0F1824;
    --card2:  #131E2C;
    --bdr:    #192438;
    --bdr2:   #1F2E44;
    --blue:   #3B82F6;
    --cyan:   #06B6D4;
    --teal:   #14B8A6;
    --green:  #10B981;
    --amber:  #F59E0B;
    --orange: #F97316;
    --red:    #EF4444;
    --txt:    #E2E8F0;
    --txt2:   #94A3B8;
    --muted:  #475569;
    --acc:    #38BDF8;
    --glow:   rgba(59,130,246,0.2);
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background: var(--bg) !important;
    color: var(--txt) !important;
    font-family: 'Inter', sans-serif !important;
}
.main .block-container {
    background: var(--bg) !important;
    padding: 26px 34px 52px 34px !important;
    max-width: 100% !important;
}
#MainMenu, footer,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; }

::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--bdr2); border-radius:3px; }

h1,h2,h3,h4,h5,h6 {
    font-family:'Inter',sans-serif !important;
    color:var(--txt) !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background:var(--surf) !important;
    border-right:1px solid var(--bdr) !important;
    min-width:234px !important; max-width:234px !important;
}
[data-testid="stSidebar"] > div:first-child { padding:0 !important; }
section[data-testid="stSidebarNav"] { display:none !important; }

/* ── INPUTS ── */
input[type="text"], input[type="password"], input[type="number"],
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background:var(--surf) !important;
    border:1px solid var(--bdr) !important;
    border-radius:8px !important;
    color:var(--txt) !important;
    font-family:'Inter',sans-serif !important;
    font-size:13px !important;
    transition:border-color .18s, box-shadow .18s !important;
}
input:focus {
    border-color:var(--blue) !important;
    box-shadow:0 0 0 3px rgba(59,130,246,0.12) !important;
    outline:none !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background:linear-gradient(135deg,#1D4ED8,#0891B2) !important;
    border:none !important; border-radius:8px !important;
    color:#fff !important;
    font-family:'Inter',sans-serif !important;
    font-weight:700 !important; font-size:12px !important;
    letter-spacing:0.07em !important;
    padding:10px 20px !important;
    text-transform:uppercase !important;
    width:100% !important;
    transition:all .2s !important; cursor:pointer !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 5px 18px var(--glow) !important;
    filter:brightness(1.1) !important;
}
.stButton > button:active { transform:translateY(0) !important; }

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background:var(--surf) !important;
    border:1px solid var(--bdr) !important;
    border-radius:8px !important; color:var(--txt) !important;
}

/* ── LABELS ── */
label, [data-testid="stWidgetLabel"] p {
    color:var(--txt2) !important; font-size:11px !important;
    font-weight:600 !important; letter-spacing:0.09em !important;
    text-transform:uppercase !important;
    font-family:'Inter',sans-serif !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border-radius:11px !important;
    border:1px solid var(--bdr) !important; overflow:hidden !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius:9px !important; border:none !important;
    background:var(--surf) !important;
}

hr { border-color:var(--bdr) !important; margin:14px 0 !important; }

/* ════════════════════════════════════
   CUSTOM COMPONENTS
════════════════════════════════════ */

/* AUTH */
.auth-card {
    background:var(--card); border:1px solid var(--bdr);
    border-radius:16px; padding:32px 28px 26px;
    box-shadow:0 24px 64px rgba(0,0,0,0.55);
    position:relative; overflow:hidden;
}
.auth-card::before {
    content:''; position:absolute; inset:0 0 auto 0; height:2px;
    background:linear-gradient(90deg,#1D4ED8,#06B6D4,#14B8A6);
}
.auth-divider {
    text-align:center; font-size:11px; color:var(--muted);
    margin:11px 0; position:relative;
}
.auth-divider::before, .auth-divider::after {
    content:''; position:absolute; top:50%; width:40%; height:1px;
    background:var(--bdr);
}
.auth-divider::before { left:0; }
.auth-divider::after  { right:0; }

/* GLASS CARD */
.gc {
    background:var(--card); border:1px solid var(--bdr);
    border-radius:14px; padding:18px 20px;
    position:relative; overflow:hidden;
    transition:border-color .2s, box-shadow .2s;
}
.gc:hover { border-color:var(--bdr2); box-shadow:0 5px 24px rgba(0,0,0,0.3); }
.gc::before {
    content:''; position:absolute; inset:0 0 auto 0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.04),transparent);
}

/* KPI */
.kpi {
    background:var(--card); border:1px solid var(--bdr);
    border-radius:12px; padding:16px 18px;
    position:relative; overflow:hidden;
}
.kpi-accent { position:absolute; bottom:0; left:0; right:0; height:2px; }
.kpi-lbl { font-size:10px; font-weight:700; letter-spacing:.1em;
           text-transform:uppercase; color:var(--muted); margin-bottom:6px; }
.kpi-val { font-family:'Inter',sans-serif; font-size:28px; font-weight:800;
           letter-spacing:-0.04em; line-height:1; }
.kpi-hint { font-size:11px; color:var(--muted); margin-top:4px; }

/* PAGE HEADER */
.top-bar {
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:22px; padding-bottom:16px; border-bottom:1px solid var(--bdr);
}
.pg-title { font-family:'Inter',sans-serif; font-size:20px; font-weight:800;
            color:var(--txt); letter-spacing:-0.03em; }
.pg-sub   { font-size:12px; color:var(--muted); margin-top:2px; }
.date-chip { font-size:11.5px; color:var(--muted); background:var(--surf);
             border:1px solid var(--bdr); border-radius:7px; padding:5px 12px; }

/* SECTION */
.sec-h { font-family:'Inter',sans-serif; font-size:14.5px; font-weight:700;
         color:var(--txt); margin-bottom:3px; letter-spacing:-0.02em; }
.sec-s { font-size:11.5px; color:var(--muted); margin-bottom:14px; }

/* STRIPS */
.info-strip {
    background:rgba(59,130,246,0.07);
    border:1px solid rgba(59,130,246,0.2);
    border-left:3px solid #3B82F6;
    border-radius:0 8px 8px 0;
    padding:10px 14px; font-size:12px; color:var(--txt2);
    margin-bottom:14px; line-height:1.7;
}
.info-strip strong { color:var(--txt); }
.warn-strip {
    background:rgba(239,68,68,0.07);
    border:1px solid rgba(239,68,68,0.2);
    border-left:3px solid #EF4444;
    border-radius:0 8px 8px 0;
    padding:10px 14px; font-size:12px; color:#FCA5A5;
    margin-bottom:14px;
}
.ok-strip {
    background:rgba(16,185,129,0.07);
    border:1px solid rgba(16,185,129,0.2);
    border-left:3px solid #10B981;
    border-radius:0 8px 8px 0;
    padding:10px 14px; font-size:12px; color:#6EE7B7;
    margin-bottom:14px;
}

/* WEEK HEADER */
.week-hdr {
    font-family:'Inter',sans-serif; font-size:13px; font-weight:700;
    color:var(--acc); text-align:center;
    padding:7px 0 10px; border-bottom:1px solid var(--bdr); margin-bottom:9px;
}

/* SIDEBAR */
.sb-logo  { padding:18px 16px 14px; border-bottom:1px solid var(--bdr); }
.sb-brand { font-family:'Inter',sans-serif; font-size:16px; font-weight:800;
            background:linear-gradient(130deg,#60A5FA,#06B6D4);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.sb-tag   { font-size:10px; color:var(--muted); letter-spacing:.07em;
            text-transform:uppercase; margin-top:1px; }
.sb-user  { padding:12px 14px; border-top:1px solid var(--bdr);
            display:flex; align-items:center; gap:9px; }
.sb-av    { width:30px; height:30px; border-radius:50%;
            background:linear-gradient(135deg,#1D4ED8,#0891B2);
            display:flex; align-items:center; justify-content:center;
            font-family:'Inter',sans-serif; font-weight:700; font-size:13px;
            color:#fff; flex-shrink:0; }
.sb-un    { font-size:12px; font-weight:600; color:var(--txt); }
.sb-ft    { font-size:10.5px; color:var(--muted); margin-top:1px; }

/* COMPARISON TABLE */
.cmp-table { width:100%; border-collapse:collapse; font-size:12.5px; }
.cmp-table th {
    background:var(--card2); color:var(--txt2); font-family:'Inter',sans-serif;
    font-size:11px; letter-spacing:.08em; text-transform:uppercase;
    padding:10px 14px; text-align:left; border-bottom:1px solid var(--bdr);
}
.cmp-table td {
    padding:10px 14px; border-bottom:1px solid var(--bdr);
    color:var(--txt); vertical-align:middle;
}
.cmp-table tr:last-child td { border-bottom:none; }
.cmp-table tr:hover td { background:rgba(255,255,255,0.02); }
.tag {
    display:inline-block; font-size:10px; font-weight:700;
    letter-spacing:.08em; text-transform:uppercase;
    padding:3px 10px; border-radius:20px;
}
.tag-ok   { background:rgba(16,185,129,0.15); color:#10B981; }
.tag-warn { background:rgba(245,158,11,0.15);  color:#F59E0B; }
.tag-bad  { background:rgba(239,68,68,0.15);   color:#EF4444; }
.tag-tap  { background:rgba(99,102,241,0.15);  color:#A5B4FC; }

/* REMARK BOX */
.remark-box {
    text-align:center; padding:20px;
    border-radius:12px; margin-bottom:4px;
}
.remark-icon { font-size:36px; margin-bottom:8px; }
.remark-text { font-family:'Inter',sans-serif; font-size:17px; font-weight:700; }
.remark-sub  { font-size:12px; margin-top:4px; }

/* LIMITS GRID */
.limits-grid { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px; }
.limit-chip {
    flex:1; min-width:160px;
    background:var(--surf); border:1px solid var(--bdr);
    border-radius:9px; padding:10px 13px; font-size:11.5px;
    color:var(--txt2); line-height:1.6;
}
.limit-chip .lc-name { font-family:'Inter',sans-serif; font-weight:700;
                        color:var(--txt); font-size:12.5px; margin-bottom:4px; }
.limit-chip .lc-row  { display:flex; justify-content:space-between; }
.limit-chip .lc-bis  { color:#38BDF8; font-weight:600; }
.limit-chip .lc-prac { color:#A5B4FC; }
.limit-chip .lc-hard { color:#94A3B8; }

/* FOOTER */
.footer-bar { text-align:center; padding:24px 0 4px;
              font-size:11px; color:var(--muted);
              border-top:1px solid var(--bdr); margin-top:38px; }

/* NO SB */
.no-sb [data-testid="stSidebar"],
.no-sb [data-testid="stSidebarCollapsedControl"] { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  ❶ PARAMETER DEFINITIONS — THREE TIERS
# ══════════════════════════════════════════════════════════════
#
#  NO INPUT RESTRICTIONS — users can enter any realistic value.
#  Validation only shows informational warnings (never blocks calculation).
#  This is intentional: real deteriorating filters produce values outside
#  BIS limits — restricting input would prevent the model from detecting
#  actual degradation and predicting maintenance.
#
#  BIS values shown purely as REFERENCE, not as enforced limits.
#
PARAMS = {
    "ph": {
        "label":     "pH",
        "unit":      "(dimensionless)",
        "bis_min":   6.5,  "bis_max":  8.5,   # BIS IS 10500 — reference only
        "bis_ideal": 7.5,
        "inp_min":   0.0,  "inp_max":  14.0,  # physical range for number_input
        "step":      0.01, "fmt":      "%.2f",
        "default":   7.2,
        "desc":      "Acidity / Basicity of water",
    },
    "tds": {
        "label":     "TDS",
        "unit":      "mg/L",
        "bis_min":   150,  "bis_max":  300,
        "bis_ideal": 225,
        "inp_min":   0.0,  "inp_max":  2000.0,
        "step":      1.0,  "fmt":      "%.0f",
        "default":   200.0,
        "desc":      "Total Dissolved Solids",
    },
    "hardness": {
        "label":     "Hardness",
        "unit":      "mg/L as CaCO₃",
        "bis_min":   0,    "bis_max":  200,
        "bis_ideal": 100,
        "inp_min":   0.0,  "inp_max":  1000.0,
        "step":      1.0,  "fmt":      "%.0f",
        "default":   120.0,
        "desc":      "Calcium & Magnesium salts",
    },
    "alkalinity": {
        "label":     "Alkalinity",
        "unit":      "mg/L as CaCO₃",
        "bis_min":   0,    "bis_max":  300,
        "bis_ideal": 150,
        "inp_min":   0.0,  "inp_max":  1000.0,
        "step":      1.0,  "fmt":      "%.0f",
        "default":   140.0,
        "desc":      "Buffering capacity of water",
    },
}

# ══════════════════════════════════════════════════════════════
#  ❷ INFORMATIONAL VALIDATION  (warns only — never blocks)
# ══════════════════════════════════════════════════════════════
def validate_param(key, value):
    """
    Returns:
        ("warn", message)  — value is outside BIS reference range (info only)
        ("ok",   "")       — value is within BIS reference range
    No "block" tier: the system must be able to process bad water to detect
    filter deterioration and predict maintenance.
    """
    p   = PARAMS[key]
    lbl = p["label"]

    if value < p["bis_min"] or value > p["bis_max"]:
        return ("warn",
                f"{lbl} {value} {p['unit']} is outside BIS IS 10500 "
                f"({p['bis_min']}–{p['bis_max']}). "
                f"This deviation will lower the FHI score.")

    return ("ok", "")


def validate_all(readings: dict):
    """
    readings = {key: value}
    Returns list of ("warn", msg) for any value outside BIS reference.
    Never returns "block" — all values are always allowed to calculate.
    """
    results = []
    for key, val in readings.items():
        lvl, msg = validate_param(key, val)
        if msg:
            results.append((lvl, msg))
    return results


# ══════════════════════════════════════════════════════════════
#  ❸ BIS-BASED SCORING ENGINE
# ══════════════════════════════════════════════════════════════
#
#  Core concept:
#    Score = 100  when value is inside BIS ideal range
#    Score drops  as deviation from ideal increases
#    Score = 0    at extreme ends
#
def score_ph(ph):
    """
    BIS ideal: 6.5 – 8.5, ideal centre 7.5
    Full 100 inside [6.5, 8.5]. Penalise outside.
    """
    p = PARAMS["ph"]
    if p["bis_min"] <= ph <= p["bis_max"]:
        # small internal variation still gives ≥ 85
        return round(max(85.0, 100 - abs(ph - p["bis_ideal"]) * 10), 2)
    else:
        dev = min(abs(ph - p["bis_min"]), abs(ph - p["bis_max"]))
        return round(max(0.0, 85 - dev * 28), 2)


def score_tds(tds):
    """
    BIS ideal: 150 – 300, centre 225
    Full 100 inside ideal. Penalise proportionally outside.
    """
    p = PARAMS["tds"]
    if p["bis_min"] <= tds <= p["bis_max"]:
        return round(max(80.0, 100 - abs(tds - p["bis_ideal"]) / 5), 2)
    else:
        dev = min(abs(tds - p["bis_min"]), abs(tds - p["bis_max"]))
        return round(max(0.0, 80 - dev / 4), 2)


def score_hardness(h):
    """
    BIS max 200. Lower is better. Ideal centre 100.
    """
    if h <= 200:
        return round(max(70.0, 100 - (h / 200) * 20), 2)
    else:
        return round(max(0.0, 70 - ((h - 200) / 10) * 3), 2)


def score_alkalinity(a):
    """
    BIS max 300. Ideal 150.
    """
    p = PARAMS["alkalinity"]
    if a <= p["bis_max"]:
        return round(max(70.0, 100 - abs(a - p["bis_ideal"]) / 6), 2)
    else:
        return round(max(0.0, 70 - ((a - p["bis_max"]) / 10) * 2.5), 2)


def calc_fhi(ph, tds, hardness, alkalinity):
    """
    Weighted FHI from BIS-based individual scores.
    Weights: pH 30% (most critical for drinking), TDS 30%, Hardness 20%, Alkalinity 20%
    """
    s = {
        "ph":        score_ph(ph),
        "tds":       score_tds(tds),
        "hardness":  score_hardness(hardness),
        "alkalinity":score_alkalinity(alkalinity),
    }
    fhi = 0.30 * s["ph"] + 0.30 * s["tds"] + 0.20 * s["hardness"] + 0.20 * s["alkalinity"]
    return round(fhi, 2), s


# ══════════════════════════════════════════════════════════════
#  ❹ FHI CLASSIFICATION + REMARK
# ══════════════════════════════════════════════════════════════
def fhi_status(fhi):
    """Returns (status_label, hex_color, bg_color, emoji)"""
    if fhi >= 80: return "Healthy",  "#10B981", "rgba(16,185,129,0.08)",  "🟢"
    if fhi >= 60: return "Moderate", "#F59E0B", "rgba(245,158,11,0.08)",  "🟡"
    if fhi >= 40: return "Poor",     "#F97316", "rgba(249,115,22,0.08)",  "🟠"
    return             "Critical",   "#EF4444", "rgba(239,68,68,0.08)",   "🔴"


def water_remark(fhi):
    """Drinking water safety remark based on FHI."""
    if fhi > 80:
        return ("✅ Safe for Drinking",
                "Water quality is close to BIS ideal. Filter is performing well.",
                "#10B981", "rgba(16,185,129,0.07)")
    elif fhi > 60:
        return ("⚠️ Acceptable — Needs Monitoring",
                "Minor deviation from BIS standards. Monitor weekly and plan maintenance.",
                "#F59E0B", "rgba(245,158,11,0.07)")
    elif fhi > 40:
        return ("🚫 Not Recommended for Drinking",
                "Significant deviation from BIS. Filter efficiency is degraded. Schedule maintenance.",
                "#F97316", "rgba(249,115,22,0.07)")
    else:
        return ("🔴 Unsafe — Immediate Action Required",
                "Water quality approaching raw tap water levels. Filter has failed. Replace immediately.",
                "#EF4444", "rgba(239,68,68,0.08)")


# ══════════════════════════════════════════════════════════════
#  ❺ DETERIORATION & PREDICTION
# ══════════════════════════════════════════════════════════════
def deterioration_rate(fhis):
    """Linear slope of FHI values (FHI points per week). Negative = deteriorating."""
    if len(fhis) < 2:
        return 0.0
    slope, _ = np.polyfit(np.arange(len(fhis), dtype=float), fhis, 1)
    return round(float(slope), 3)


def predict_days(cur_fhi, rate, threshold=40):
    """Days until FHI crosses critical threshold (40)."""
    if rate >= 0:
        return None   # stable or improving
    weeks = (cur_fhi - threshold) / abs(rate)
    return max(1, round(weeks * 7))


# ══════════════════════════════════════════════════════════════
#  ❻ TAP WATER COMPARISON
# ══════════════════════════════════════════════════════════════
#  Typical raw tap water values for Indian municipal supply
TAP_WATER_REF = {"ph": 7.8, "tds": 520.0, "hardness": 310.0, "alkalinity": 340.0}
TAP_FHI, TAP_SCORES = calc_fhi(**TAP_WATER_REF)   # pre-compute once

BIS_IDEAL_REF  = {"ph": 7.5, "tds": 225.0, "hardness": 100.0, "alkalinity": 150.0}
BIS_FHI, _     = calc_fhi(**BIS_IDEAL_REF)


def compare_with_tap(filter_fhi, tap_fhi=TAP_FHI):
    """
    Returns improvement % of filtered water over tap water.
    Also returns how far it has 'fallen back' toward tap quality.
    """
    gap    = BIS_FHI - tap_fhi
    gained = filter_fhi - tap_fhi
    pct    = round((gained / gap) * 100, 1) if gap > 0 else 0.0
    return pct


# ══════════════════════════════════════════════════════════════
#  ❼ DATABASE
# ══════════════════════════════════════════════════════════════
DB = "hydroguard.db"

def get_db():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = get_db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        filter_type   TEXT,
        created_date  TEXT
    );
    CREATE TABLE IF NOT EXISTS water_data (
        data_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER,
        week       INTEGER,
        ph         REAL, tds REAL, hardness REAL, alkalinity REAL,
        fhi        REAL,
        timestamp  TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    CREATE TABLE IF NOT EXISTS results (
        result_id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id             INTEGER,
        calc_date           TEXT,
        fhi_w1 REAL, fhi_w2 REAL, fhi_w3 REAL, fhi_w4 REAL,
        deterioration_rate  REAL,
        maintenance_days    INTEGER,
        is_post_maintenance INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    """)
    c.commit(); c.close()

init_db()

FILTER_TYPES = [
    "RO Membrane", "UF Membrane", "Activated Carbon",
    "Sand Filter", "Candle Filter", "Multi-stage Filter", "Other",
]

def hp(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password, filter_type):
    c = get_db()
    try:
        c.execute(
            "INSERT INTO users (username,password_hash,filter_type,created_date) VALUES (?,?,?,?)",
            (username.strip(), hp(password), filter_type, datetime.now().isoformat()))
        c.commit(); return True, "Account created!"
    except sqlite3.IntegrityError:
        return False, "Username already taken."
    finally: c.close()

def login_user(username, password):
    c = get_db()
    r = c.execute(
        "SELECT * FROM users WHERE username=? AND password_hash=?",
        (username.strip(), hp(password))).fetchone()
    c.close(); return dict(r) if r else None

def save_water(uid, entries):
    """entries: list of (week, ph, tds, hardness, alkalinity, fhi)"""
    c = get_db()
    c.execute("DELETE FROM water_data WHERE user_id=?", (uid,))
    for w, ph, tds, h, a, fhi in entries:
        c.execute(
            "INSERT INTO water_data (user_id,week,ph,tds,hardness,alkalinity,fhi,timestamp) VALUES (?,?,?,?,?,?,?,?)",
            (uid, w, ph, tds, h, a, fhi, datetime.now().isoformat()))
    c.commit(); c.close()

def load_water(uid):
    c = get_db()
    r = c.execute("SELECT * FROM water_data WHERE user_id=? ORDER BY week", (uid,)).fetchall()
    c.close(); return [dict(x) for x in r]

def save_result(uid, fhis, rate, days, is_post=0):
    c = get_db()
    v = (fhis + [None]*4)[:4]
    c.execute(
        "INSERT INTO results (user_id,calc_date,fhi_w1,fhi_w2,fhi_w3,fhi_w4,"
        "deterioration_rate,maintenance_days,is_post_maintenance) VALUES (?,?,?,?,?,?,?,?,?)",
        (uid, datetime.now().isoformat(), *v, rate, days, is_post))
    c.commit(); c.close()

def load_latest(uid):
    c = get_db()
    r = c.execute(
        "SELECT * FROM results WHERE user_id=? AND is_post_maintenance=0 "
        "ORDER BY result_id DESC LIMIT 1", (uid,)).fetchone()
    c.close(); return dict(r) if r else None

def load_all_results(uid):
    c = get_db()
    r = c.execute(
        "SELECT * FROM results WHERE user_id=? ORDER BY result_id DESC", (uid,)).fetchall()
    c.close(); return [dict(x) for x in r]


# ══════════════════════════════════════════════════════════════
#  ❽ PLOTLY CHARTS  — fixed layout, Inter font, no dict conflict
# ══════════════════════════════════════════════════════════════

# Base layout — used via fig.update_layout(**_base_layout()) to avoid
# xaxis/yaxis key conflicts when we need to extend them per chart.
def _base_layout(height=320, title_text="", show_legend=True):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(11,17,25,0.85)",
        font=dict(family="Inter", color="#64748B", size=12),
        margin=dict(l=48, r=24, t=44, b=40),
        height=height,
        title=dict(
            text=title_text,
            font=dict(family="Inter", size=13, color="#CBD5E1"),
            x=0, xanchor="left", pad=dict(l=0, t=4),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0)",
            font=dict(color="#64748B", size=11),
        ) if show_legend else dict(visible=False),
        xaxis=dict(
            gridcolor="rgba(25,36,60,1)",
            zeroline=False,
            showline=False,
            tickfont=dict(color="#64748B", size=11),
        ),
        yaxis=dict(
            gridcolor="rgba(25,36,60,1)",
            zeroline=False,
            showline=False,
            tickfont=dict(color="#64748B", size=11),
        ),
    )


def _add_annotation(fig, y, text, color, xanchor="right", yanchor="bottom"):
    """Safe annotation helper — no deprecated annotation_position string."""
    fig.add_annotation(
        x=1, xref="paper", xanchor=xanchor,
        y=y, yref="y",     yanchor=yanchor,
        text=text,
        showarrow=False,
        font=dict(color=color, size=10, family="Inter"),
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
    )


def chart_trend(fhis, tap_fhi=TAP_FHI, bis_fhi=BIS_FHI):
    xs   = [f"Week {i+1}" for i in range(len(fhis))]
    rate = deterioration_rate(fhis)
    fw   = max(0, fhis[-1] + rate) if len(fhis) >= 2 else fhis[-1]

    fig = go.Figure()

    # ── Background zone bands
    for y0, y1, col in [
        (80, 100, "rgba(16,185,129,0.05)"),
        (60, 80,  "rgba(245,158,11,0.05)"),
        (40, 60,  "rgba(249,115,22,0.05)"),
        (0,  40,  "rgba(239,68,68,0.06)"),
    ]:
        fig.add_hrect(y0=y0, y1=y1, fillcolor=col, line_width=0)

    # ── Reference horizontal lines (no annotation_position keyword)
    fig.add_shape(type="line", x0=0, x1=1, xref="paper",
                  y0=40, y1=40, yref="y",
                  line=dict(color="#EF4444", dash="dash", width=1.5))
    _add_annotation(fig, 40, "  Critical threshold (40)", "#EF4444", xanchor="right", yanchor="top")

    fig.add_shape(type="line", x0=0, x1=1, xref="paper",
                  y0=round(tap_fhi, 1), y1=round(tap_fhi, 1), yref="y",
                  line=dict(color="#A78BFA", dash="dot", width=1.3))
    _add_annotation(fig, round(tap_fhi, 1), f"  Tap Water ~{tap_fhi:.0f}", "#A78BFA",
                    xanchor="left", yanchor="bottom")

    fig.add_shape(type="line", x0=0, x1=1, xref="paper",
                  y0=round(bis_fhi, 1), y1=round(bis_fhi, 1), yref="y",
                  line=dict(color="#10B981", dash="dot", width=1.3))
    _add_annotation(fig, round(bis_fhi, 1), f"  BIS Ideal ~{bis_fhi:.0f}", "#10B981",
                    xanchor="right", yanchor="bottom")

    # ── Main FHI line with fill
    fig.add_trace(go.Scatter(
        x=xs, y=fhis,
        mode="lines+markers+text",
        name="Filter FHI",
        line=dict(color="#3B82F6", width=3),
        marker=dict(size=10, color="#38BDF8",
                    line=dict(color="#060A10", width=2)),
        text=[f"{v:.1f}" for v in fhis],
        textposition="top center",
        textfont=dict(color="#E2E8F0", size=12, family="Inter"),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
        hovertemplate="<b>%{x}</b><br>FHI: %{y:.1f}<extra></extra>",
    ))

    # ── Forecast dotted extension
    if len(fhis) >= 2:
        fig.add_trace(go.Scatter(
            x=[xs[-1], "Forecast"],
            y=[fhis[-1], fw],
            mode="lines+markers",
            name="Forecast",
            line=dict(color="#F59E0B", width=2, dash="dot"),
            marker=dict(size=8, color="#F59E0B", symbol="diamond"),
            hovertemplate="<b>%{x}</b><br>Predicted FHI: %{y:.1f}<extra></extra>",
        ))

    lay = _base_layout(height=330,
                       title_text="Filter Health Deterioration Trend",
                       show_legend=True)
    lay["yaxis"]["range"] = [0, 108]
    lay["yaxis"]["title"] = "FHI Score"
    lay["xaxis"]["title"] = "Week"
    lay["margin"] = dict(l=52, r=100, t=44, b=40)  # extra right space for annotations
    fig.update_layout(**lay)
    return fig


def chart_radar(scores, label="Current"):
    params = ["pH", "TDS", "Hardness", "Alkalinity"]
    vals   = [scores["ph"], scores["tds"], scores["hardness"], scores["alkalinity"]]

    # BIS ideal reference ring
    _, bis_s = calc_fhi(**BIS_IDEAL_REF)
    bis_v    = [bis_s["ph"], bis_s["tds"], bis_s["hardness"], bis_s["alkalinity"]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=bis_v + [bis_v[0]], theta=params + [params[0]],
        fill="toself", fillcolor="rgba(16,185,129,0.06)",
        line=dict(color="#10B981", width=1.5, dash="dot"),
        name="BIS Ideal",
        marker=dict(size=3, color="#10B981"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=params + [params[0]],
        fill="toself", fillcolor="rgba(59,130,246,0.13)",
        line=dict(color="#38BDF8", width=2.5),
        name=label,
        marker=dict(size=6, color="#38BDF8",
                    line=dict(color="#060A10", width=1.5)),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#64748B", size=12),
        polar=dict(
            bgcolor="rgba(11,17,25,0.85)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="rgba(25,36,60,1)",
                tickfont=dict(color="#475569", size=10, family="Inter"),
                tickvals=[0, 25, 50, 75, 100],
            ),
            angularaxis=dict(
                gridcolor="rgba(25,36,60,0.8)",
                tickfont=dict(family="Inter", color="#CBD5E1",
                              size=12, weight=600),
            ),
        ),
        margin=dict(l=28, r=28, t=44, b=28),
        height=280,
        title=dict(
            text="Parameter Scores vs BIS Ideal",
            font=dict(family="Inter", size=13, color="#CBD5E1"),
            x=0.5, xanchor="center",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#64748B", size=11),
            orientation="h",
            x=0.5, xanchor="center", y=-0.08,
        ),
    )
    return fig


def chart_gauge(fhi):
    status, color, _, _ = fhi_status(fhi)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fhi,
        number=dict(
            font=dict(family="Inter", size=34, color=color),
            suffix=" / 100",
        ),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickfont=dict(color="#475569", size=10, family="Inter"),
                tickvals=[0, 20, 40, 60, 80, 100],
            ),
            bar=dict(color=color, thickness=0.68),
            bgcolor="rgba(11,17,25,0.9)",
            borderwidth=0,
            steps=[
                dict(range=[0,  40],  color="rgba(239,68,68,0.1)"),
                dict(range=[40, 60],  color="rgba(249,115,22,0.1)"),
                dict(range=[60, 80],  color="rgba(245,158,11,0.1)"),
                dict(range=[80, 100], color="rgba(16,185,129,0.1)"),
            ],
        ),
        title=dict(
            text=f"<b>{status}</b>",
            font=dict(family="Inter", size=14, color=color),
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        height=230,
        margin=dict(l=16, r=16, t=28, b=8),
    )
    return fig


def chart_bar_comparison(fhis, tap_fhi=TAP_FHI, bis_fhi=BIS_FHI):
    """Bar chart: Filter W1-W4 vs Tap Water vs BIS Ideal."""
    labels = [f"Week {i+1}" for i in range(len(fhis))] + ["🚰 Tap Water", "🟢 BIS Ideal"]
    values = list(fhis) + [tap_fhi, bis_fhi]

    bar_colors = []
    for v in fhis:
        _, c, _, _ = fhi_status(v)
        bar_colors.append(c)
    bar_colors += ["#A78BFA", "#10B981"]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker=dict(
            color=bar_colors,
            opacity=0.85,
            line=dict(width=0),
        ),
        text=[f"{v:.1f}" for v in values],
        textposition="outside",
        textfont=dict(family="Inter", size=12, color="#CBD5E1"),
        hovertemplate="<b>%{x}</b><br>FHI: %{y:.1f}<extra></extra>",
        width=0.55,
    ))

    # Critical threshold line via shape (no annotation_position bug)
    fig.add_shape(type="line", x0=-0.5, x1=len(labels) - 0.5,
                  xref="x", y0=40, y1=40, yref="y",
                  line=dict(color="#EF4444", dash="dash", width=1.5))
    fig.add_annotation(
        x=len(labels) - 1, xref="x",
        y=40, yref="y", yanchor="bottom",
        text=" Critical (40)", showarrow=False,
        font=dict(color="#EF4444", size=10, family="Inter"),
        bgcolor="rgba(0,0,0,0)",
    )

    lay = _base_layout(height=300,
                       title_text="Filter Output vs Tap Water vs BIS Ideal",
                       show_legend=False)
    lay["yaxis"]["range"]  = [0, 115]
    lay["yaxis"]["title"]  = "FHI Score"
    lay["margin"] = dict(l=52, r=24, t=44, b=40)
    fig.update_layout(**lay)
    return fig


# ══════════════════════════════════════════════════════════════
#  ❾ SESSION STATE
# ══════════════════════════════════════════════════════════════
_def = dict(
    logged_in=False, user=None, page="login", nav="dashboard",
    calc_fhis=None, calc_scores=None, calc_rate=None, calc_days=None,
)
for k, v in _def.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════
#  ❿ SIDEBAR
# ══════════════════════════════════════════════════════════════
def render_sidebar():
    u  = st.session_state.user
    av = u["username"][0].upper()
    ft = u.get("filter_type", "—") or "—"
    with st.sidebar:
        st.markdown(f"""
        <div class="sb-logo">
            <div style="font-size:24px;margin-bottom:4px">💧</div>
            <div class="sb-brand">HydroGuard</div>
            <div class="sb-tag">Filter Health Monitor</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="padding:14px 12px 4px;">
            <div style="font-size:9.5px;font-weight:700;letter-spacing:.15em;
                text-transform:uppercase;color:#475569;padding:0 4px;margin-bottom:4px;">
                Navigation
            </div>
        </div>""", unsafe_allow_html=True)

        for key, icon, label in [
            ("dashboard",   "📊", "Dashboard"),
            ("enter_data",  "📝", "Enter Data"),
            ("maintenance", "🔧", "Maintenance"),
            ("history",     "📋", "History"),
        ]:
            if st.button(f"{icon}  {label}", key=f"nav_{key}"):
                st.session_state.nav = key
                st.rerun()

        st.markdown('<hr style="border-color:#192438;margin:8px 12px;">', unsafe_allow_html=True)

        # BIS quick-ref in sidebar
        st.markdown("""
        <div style="padding:0 14px 10px;">
            <div style="font-size:9.5px;font-weight:700;letter-spacing:.15em;
                text-transform:uppercase;color:#475569;margin-bottom:8px;">
                BIS IS 10500 Reference
            </div>
            <div style="font-size:11px;color:#64748B;line-height:2;">
                pH &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6.5 – 8.5<br>
                TDS &nbsp;&nbsp;&nbsp;&nbsp;150 – 300 mg/L<br>
                Hardness &nbsp;≤ 200 mg/L<br>
                Alkalinity &nbsp;≤ 300 mg/L
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr style="border-color:#192438;margin:4px 12px 0;">', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sb-user">
            <div class="sb-av">{av}</div>
            <div>
                <div class="sb-un">{u["username"]}</div>
                <div class="sb-ft">🔩 {ft}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪  Sign Out", key="sb_logout"):
            for k in _def: st.session_state[k] = _def[k]
            st.rerun()


# ══════════════════════════════════════════════════════════════
#  AUTH PAGES
# ══════════════════════════════════════════════════════════════
_NO_SB = """<style>
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] { display:none !important; }
.main .block-container { padding:0 !important; max-width:100% !important; }
</style>"""

def _left_panel(icon, headline, sub, bullets):
    items_html = "".join(
        f'<div style="background:{c};border:1px solid {bc};border-radius:8px;'
        f'padding:9px 14px;font-size:12px;color:#94A3B8;">'
        f'<span style="color:{ic};font-weight:700;">{em}</span>&nbsp; {txt}</div>'
        for em, ic, c, bc, txt in bullets
    )
    return f"""
    <div style="min-height:100vh;
        background:linear-gradient(145deg,#0B1119 0%,#060A10 100%);
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        padding:56px 48px;border-right:1px solid #192438;
        position:relative;overflow:hidden;">
      <div style="position:absolute;top:-80px;left:-80px;width:300px;height:300px;
        border-radius:50%;background:radial-gradient(circle,rgba(29,78,216,0.14),transparent 70%);
        pointer-events:none;"></div>
      <div style="position:absolute;bottom:-50px;right:-40px;width:220px;height:220px;
        border-radius:50%;background:radial-gradient(circle,rgba(8,145,178,0.09),transparent 70%);
        pointer-events:none;"></div>
      <div style="position:relative;z-index:1;text-align:center;max-width:360px;">
        <div style="font-size:60px;margin-bottom:16px;
            filter:drop-shadow(0 0 20px rgba(56,189,248,0.35))">{icon}</div>
        <div style="font-family:'Inter',sans-serif;font-size:30px;font-weight:800;
            letter-spacing:-0.04em;line-height:1.12;
            background:linear-gradient(130deg,#E2E8F0 30%,#38BDF8);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            margin-bottom:12px;">{headline}</div>
        <div style="font-size:12.5px;color:#475569;line-height:1.75;margin-bottom:26px;">{sub}</div>
        <div style="display:flex;flex-direction:column;gap:8px;text-align:left;">{items_html}</div>
      </div>
    </div>"""


def page_login():
    st.markdown(_NO_SB, unsafe_allow_html=True)
    L, R = st.columns(2, gap="small")
    with L:
        st.markdown(_left_panel(
            "💧",
            "Filter Health<br>Monitoring System",
            "Compare your filtered water against BIS IS 10500:2012 standards "
            "and predict maintenance before failure.",
            [
                ("📊", "#38BDF8", "rgba(59,130,246,0.08)",  "rgba(59,130,246,0.2)",  "4-week BIS-based FHI analysis"),
                ("⚡", "#14B8A6", "rgba(20,184,166,0.08)",  "rgba(20,184,166,0.2)",  "3-tier input validation engine"),
                ("🔮", "#F59E0B", "rgba(245,158,11,0.08)",  "rgba(245,158,11,0.2)",  "Tap water → Filter deterioration tracking"),
            ]
        ), unsafe_allow_html=True)

    with R:
        st.markdown("""
        <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
            padding:40px 70px;background:#060A10;">
        <div style="width:100%;max-width:370px;">
          <div style="text-align:center;margin-bottom:26px;">
            <div style="font-family:'Inter',sans-serif;font-size:19px;font-weight:800;color:#E2E8F0;">
              Welcome back</div>
            <div style="font-size:12px;color:#475569;margin-top:4px;">
              Sign in to your monitoring dashboard</div>
          </div>
          <div class="auth-card">
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter username", key="li_u")
        password = st.text_input("Password", placeholder="Enter password", type="password", key="li_p")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Sign In →", key="login_btn"):
            if not username or not password:
                st.error("Please enter username and password.")
            else:
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.page = "dashboard"
                    st.session_state.nav  = "dashboard"
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password.")

        st.markdown('<div class="auth-divider">new here?</div>', unsafe_allow_html=True)
        if st.button("Create Account", key="go_reg"):
            st.session_state.page = "register"; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;font-size:10.5px;color:#334155;margin-top:18px;">
            BIS IS 10500:2012 Compliant · HydroGuard v3.0</div>
        </div></div>""", unsafe_allow_html=True)


def page_register():
    st.markdown(_NO_SB, unsafe_allow_html=True)
    L, R = st.columns(2, gap="small")
    with L:
        st.markdown(_left_panel(
            "🛡️",
            "Create Your<br>Monitor Account",
            "Track your filter's health over time. Just 3 fields — you're ready in seconds.",
            [
                ("✅", "#10B981", "rgba(16,185,129,0.07)", "rgba(16,185,129,0.2)", "Username + Password"),
                ("🔩", "#38BDF8", "rgba(59,130,246,0.07)", "rgba(59,130,246,0.2)", "Select your filter type"),
                ("🚀", "#F59E0B", "rgba(245,158,11,0.07)", "rgba(245,158,11,0.2)", "Start entering data immediately"),
            ]
        ), unsafe_allow_html=True)

    with R:
        st.markdown("""
        <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
            padding:40px 70px;background:#060A10;">
        <div style="width:100%;max-width:380px;">
          <div style="text-align:center;margin-bottom:24px;">
            <div style="font-family:'Inter',sans-serif;font-size:19px;font-weight:800;color:#E2E8F0;">
              Create Account</div>
            <div style="font-size:12px;color:#475569;margin-top:4px;">3 fields. That's all.</div>
          </div>
          <div class="auth-card">
        """, unsafe_allow_html=True)

        new_u  = st.text_input("Username", placeholder="Choose a username (min 3 chars)", key="reg_u")
        new_p  = st.text_input("Password", placeholder="Min 6 characters", type="password", key="reg_p")
        new_cp = st.text_input("Confirm Password", placeholder="Re-enter password", type="password", key="reg_cp")
        new_ft = st.selectbox("Filter Type", FILTER_TYPES, key="reg_ft")

        if new_p:
            if len(new_p) < 6:
                st.markdown('<div style="font-size:11px;color:#EF4444;margin-top:-5px;margin-bottom:5px;">⚠ Too short — min 6 chars</div>', unsafe_allow_html=True)
            elif len(new_p) < 10:
                st.markdown('<div style="font-size:11px;color:#F59E0B;margin-top:-5px;margin-bottom:5px;">🔒 Moderate strength</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:11px;color:#10B981;margin-top:-5px;margin-bottom:5px;">✅ Strong password</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Create Account →", key="reg_btn"):
            errs = []
            if len(new_u) < 3: errs.append("Username must be at least 3 characters.")
            if len(new_p) < 6: errs.append("Password must be at least 6 characters.")
            if new_p != new_cp: errs.append("Passwords do not match.")
            for e in errs: st.error(e)
            if not errs:
                ok, msg = register_user(new_u, new_p, new_ft)
                if ok:
                    st.success("✅ Account created! Sign in below.")
                    st.session_state.page = "login"; st.rerun()
                else:
                    st.error(f"❌ {msg}")

        st.markdown('<div class="auth-divider">already have an account?</div>', unsafe_allow_html=True)
        if st.button("← Back to Login", key="back_li"):
            st.session_state.page = "login"; st.rerun()

        st.markdown('</div></div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SHARED UI HELPERS
# ══════════════════════════════════════════════════════════════
def top_bar(title, subtitle):
    today = datetime.now().strftime("%d %b %Y")
    st.markdown(f"""
    <div class="top-bar">
        <div>
            <div class="pg-title">{title}</div>
            <div class="pg-sub">{subtitle}</div>
        </div>
        <div class="date-chip">📅 {today}</div>
    </div>""", unsafe_allow_html=True)


def kpi_card(lbl, val, hint="", color="#38BDF8", border_color=None):
    bc = border_color or color + "33"
    return f"""<div class="kpi" style="border-color:{bc};">
        <div class="kpi-lbl">{lbl}</div>
        <div class="kpi-val" style="color:{color}">{val}</div>
        <div class="kpi-hint">{hint}</div>
        <div class="kpi-accent" style="background:{color};"></div>
    </div>"""


def param_status_tag(level):
    if level == "warn": return '<span class="tag tag-warn">⚠ Outside BIS</span>'
    if level == "ok":   return '<span class="tag tag-ok">✓ BIS OK</span>'
    return ""


def render_validation_messages(readings: dict):
    """
    Show warning strips for values outside BIS reference.
    Always returns False (never blocks calculation).
    """
    results = validate_all(readings)
    for lvl, msg in results:
        st.markdown(
            f'<div style="background:rgba(245,158,11,0.07);border:1px solid '
            f'rgba(245,158,11,0.2);border-left:3px solid #F59E0B;'
            f'border-radius:0 8px 8px 0;padding:9px 13px;font-size:11.5px;'
            f'color:#FCD34D;margin-bottom:8px;">⚠️ {msg}</div>',
            unsafe_allow_html=True,
        )
    return False  # never blocks


# ══════════════════════════════════════════════════════════════
#  NAV: DASHBOARD
# ══════════════════════════════════════════════════════════════
def nav_dashboard():
    top_bar("📊 Dashboard", "Filter health overview — BIS-based analysis at a glance")
    uid  = st.session_state.user["user_id"]
    data = load_water(uid)
    res  = load_latest(uid)

    if not res or not data:
        st.markdown("""
        <div class="gc" style="text-align:center;padding:56px 40px;">
            <div style="font-size:48px;margin-bottom:14px">📊</div>
            <div class="sec-h" style="font-size:18px;margin-bottom:8px;">No data yet</div>
            <div style="font-size:13px;color:#475569;max-width:380px;margin:0 auto;line-height:1.75;">
                Go to <strong style="color:#38BDF8;">Enter Data</strong> to record 4 weeks of
                filter output readings. The system will compare them against BIS IS 10500:2012
                standards and track deterioration toward raw tap water quality.
            </div>
        </div>""", unsafe_allow_html=True)
        return

    fhis   = [v for v in [res.get(f"fhi_w{i}") for i in range(1,5)] if v is not None]
    rate   = res.get("deterioration_rate", 0) or 0
    days   = res.get("maintenance_days")
    cur    = fhis[-1] if fhis else 0
    status, color, bg, icon = fhi_status(cur)
    remark_text, remark_sub, remark_col, remark_bg = water_remark(cur)
    imp_pct = compare_with_tap(cur)
    rc  = "#EF4444" if rate < -8 else "#F59E0B" if rate < -4 else "#10B981"
    dcol = "#EF4444" if days and days < 14 else "#F59E0B" if days and days < 30 else "#10B981"

    # ── Remark Banner
    st.markdown(f"""
    <div class="gc" style="border-color:{remark_col}44;background:{remark_bg};
        margin-bottom:18px;padding:16px 22px;">
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="font-size:32px;">{remark_text.split()[0]}</div>
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:16px;font-weight:700;color:{remark_col};">
                    {" ".join(remark_text.split()[1:])}</div>
                <div style="font-size:12px;color:#94A3B8;margin-top:3px;">{remark_sub}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── KPI Row
    k1, k2, k3, k4, k5 = st.columns(5, gap="small")
    with k1: st.markdown(kpi_card("Current FHI", f"{cur:.1f}", "/ 100", color), unsafe_allow_html=True)
    with k2: st.markdown(kpi_card("Filter Status", f"{icon} {status}", "BIS Assessment", color), unsafe_allow_html=True)
    with k3: st.markdown(kpi_card("vs Tap Water", f"+{imp_pct:.0f}%",
                                   f"Tap FHI ≈ {TAP_FHI:.0f}", "#A78BFA"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_card("Deterioration", f"{rate:+.2f}",
                                   "FHI pts / week", rc), unsafe_allow_html=True)
    with k5:
        dval  = f"{days}d" if days else "Stable ✓"
        dhint = (datetime.now()+timedelta(days=days)).strftime('%d %b %Y') if days else "No maintenance needed"
        st.markdown(kpi_card("Until Maintenance", dval, dhint, dcol), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.markdown('<div class="gc">', unsafe_allow_html=True)
        st.plotly_chart(chart_trend(fhis), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="gc">', unsafe_allow_html=True)
        st.plotly_chart(chart_gauge(cur), use_container_width=True,
                        config={"displayModeBar": False})
        if days:
            mdate   = (datetime.now()+timedelta(days=days)).strftime('%d %b %Y')
            bar_pct = min(100, max(4, int((days/60)*100)))
            st.markdown(f"""
            <div style="margin-top:8px;padding:11px 14px;background:var(--surf);
                border:1px solid {dcol}33;border-radius:10px;">
                <div style="font-size:10px;text-transform:uppercase;letter-spacing:.1em;
                    color:var(--muted);margin-bottom:4px;">Next Maintenance</div>
                <div style="font-family:'Inter',sans-serif;font-size:20px;font-weight:800;
                    color:{dcol}">{days} Days</div>
                <div style="font-size:11px;color:var(--muted);margin-bottom:8px;">{mdate}</div>
                <div style="background:var(--bdr);border-radius:3px;height:4px;">
                    <div style="background:{dcol};width:{bar_pct}%;height:4px;border-radius:3px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tap vs Filter Comparison
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="gc">', unsafe_allow_html=True)
    st.markdown('<div class="sec-h">🔬 Tap Water → Filter → BIS Ideal Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">How your filtered water quality compares against raw tap water and BIS standards each week</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_bar_comparison(fhis), use_container_width=True,
                    config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Weekly parameters table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="gc">', unsafe_allow_html=True)
    st.markdown('<div class="sec-h">Weekly Parameter Detail</div>', unsafe_allow_html=True)
    rows = []
    for r in data:
        vr = validate_all({"ph": r["ph"], "tds": r["tds"],
                            "hardness": r["hardness"], "alkalinity": r["alkalinity"]})
        any_warn  = any(l=="warn" for l, _ in vr)
        compliance = "⚠️ Outside BIS" if any_warn else "✅ BIS OK"
        rows.append({
            "Week":             f"Week {r['week']}",
            "pH":               f"{r['ph']:.2f}",
            "TDS (mg/L)":       f"{r['tds']:.0f}",
            "Hardness (mg/L)":  f"{r['hardness']:.0f}",
            "Alkalinity (mg/L)":f"{r['alkalinity']:.0f}",
            "FHI":              f"{r['fhi']:.1f}",
            "BIS Compliance":   compliance,
        })
    st.dataframe(pd.DataFrame(rows).set_index("Week"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  NAV: ENTER DATA
# ══════════════════════════════════════════════════════════════
def nav_enter_data():
    top_bar("📝 Enter Filter Output Data", "Record 4 weeks of water quality to calculate BIS-based Filter Health Index")
    uid      = st.session_state.user["user_id"]
    existing = {r["week"]: r for r in load_water(uid)}

    # Theory strip
    st.markdown("""
    <div class="info-strip">
        <strong>How the model works:</strong> You enter <em>filtered water</em> readings each week.
        The system calculates how close your filter output is to
        <strong>BIS IS 10500:2012 ideal values</strong>.
        As the filter ages, readings drift toward raw tap water levels — the FHI drops.
        When FHI &lt; 40, filter quality ≈ untreated tap water → maintenance required.
    </div>
    """, unsafe_allow_html=True)

    # BIS reference info — informational only, no restrictions
    st.markdown("""
    <div class="limits-grid">
      <div class="limit-chip">
        <div class="lc-name">pH <span style="font-weight:400;font-size:11px;">(dimensionless)</span></div>
        <div class="lc-row"><span>BIS Safe Range</span><span class="lc-bis">6.5 – 8.5</span></div>
        <div class="lc-row"><span>BIS Ideal Centre</span><span style="color:#F59E0B;">7.5</span></div>
        <div class="lc-row"><span>You can enter</span><span class="lc-hard">0 – 14</span></div>
      </div>
      <div class="limit-chip">
        <div class="lc-name">TDS <span style="font-weight:400;font-size:11px;">(mg/L)</span></div>
        <div class="lc-row"><span>BIS Safe Range</span><span class="lc-bis">150 – 300</span></div>
        <div class="lc-row"><span>BIS Ideal Centre</span><span style="color:#F59E0B;">225</span></div>
        <div class="lc-row"><span>You can enter</span><span class="lc-hard">0 – 2000</span></div>
      </div>
      <div class="limit-chip">
        <div class="lc-name">Hardness <span style="font-weight:400;font-size:11px;">(mg/L)</span></div>
        <div class="lc-row"><span>BIS Safe Max</span><span class="lc-bis">≤ 200</span></div>
        <div class="lc-row"><span>BIS Ideal</span><span style="color:#F59E0B;">≤ 100</span></div>
        <div class="lc-row"><span>You can enter</span><span class="lc-hard">0 – 1000</span></div>
      </div>
      <div class="limit-chip">
        <div class="lc-name">Alkalinity <span style="font-weight:400;font-size:11px;">(mg/L)</span></div>
        <div class="lc-row"><span>BIS Safe Max</span><span class="lc-bis">≤ 300</span></div>
        <div class="lc-row"><span>BIS Ideal</span><span style="color:#F59E0B;">150</span></div>
        <div class="lc-row"><span>You can enter</span><span class="lc-hard">0 – 1000</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 4-week input grid
    weekly = {}
    cols   = st.columns(4, gap="medium")

    for i, col in enumerate(cols):
        week = i + 1
        ex   = existing.get(week, {})
        with col:
            st.markdown(f'<div class="gc"><div class="week-hdr">📅 Week {week}</div>',
                        unsafe_allow_html=True)

            ph  = st.number_input("pH",
                min_value=0.0, max_value=14.0, step=0.01,
                value=float(ex.get("ph",  7.2)), format="%.2f", key=f"ph_{week}",
                help="BIS safe range: 6.5–8.5  |  Any value accepted")
            tds = st.number_input("TDS (mg/L)",
                min_value=0.0, max_value=2000.0, step=1.0,
                value=float(ex.get("tds", 200.0)), key=f"tds_{week}",
                help="BIS safe range: 150–300 mg/L  |  Any value accepted")
            har = st.number_input("Hardness (mg/L)",
                min_value=0.0, max_value=1000.0, step=1.0,
                value=float(ex.get("hardness", 120.0)), key=f"har_{week}",
                help="BIS safe max: 200 mg/L  |  Any value accepted")
            alk = st.number_input("Alkalinity (mg/L)",
                min_value=0.0, max_value=1000.0, step=1.0,
                value=float(ex.get("alkalinity", 140.0)), key=f"alk_{week}",
                help="BIS safe max: 300 mg/L  |  Any value accepted")

            # Informational BIS warnings — never block
            readings = {"ph": ph, "tds": tds, "hardness": har, "alkalinity": alk}
            vresults = validate_all(readings)
            for lvl, msg in vresults:
                st.markdown(
                    f'<div style="font-size:10.5px;color:#F59E0B;'
                    f'margin-top:-3px;margin-bottom:3px;">⚠ {msg}</div>',
                    unsafe_allow_html=True,
                )
            if not vresults:
                st.markdown(
                    '<div style="font-size:10.5px;color:#10B981;'
                    'margin-top:-3px;">✅ All within BIS range</div>',
                    unsafe_allow_html=True,
                )

            # Live FHI preview
            fp, _ = calc_fhi(ph, tds, har, alk)
            fs, fc, _, _ = fhi_status(fp)
            imp = compare_with_tap(fp)
            st.markdown(f"""
            <div style="margin-top:8px;padding:9px 11px;background:var(--surf);
                border:1px solid {fc}33;border-radius:9px;text-align:center;">
                <div style="font-size:9.5px;text-transform:uppercase;letter-spacing:.1em;
                    color:var(--muted);margin-bottom:2px;">FHI Preview</div>
                <div style="font-family:'Inter',sans-serif;font-size:20px;font-weight:800;
                    color:{fc};">{fp:.1f}</div>
                <div style="font-size:10px;color:{fc};">{fs}</div>
                <div style="font-size:10px;color:#A78BFA;margin-top:2px;">{imp:+.0f}% vs Tap</div>
            </div>""", unsafe_allow_html=True)

            weekly[week] = (ph, tds, har, alk)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    bc, _ = st.columns([2, 3])
    with bc:
        if st.button("⚡  Calculate Filter Health Index", key="calc_btn"):
            entries, fhis, all_scores = [], [], []
            for w in range(1, 5):
                ph, tds, h, a = weekly[w]
                fhi, sc = calc_fhi(ph, tds, h, a)
                fhis.append(fhi); all_scores.append(sc)
                entries.append((w, ph, tds, h, a, fhi))

            rate = deterioration_rate(fhis)
            days = predict_days(fhis[-1], rate)
            save_water(uid, entries)
            save_result(uid, fhis, rate, days, is_post=0)
            st.session_state.calc_fhis   = fhis
            st.session_state.calc_scores = all_scores
            st.session_state.calc_rate   = rate
            st.session_state.calc_days   = days
            st.success("✅ FHI calculated and saved to your account!")
            st.rerun()

    # ── Results
    if st.session_state.calc_fhis:
        fhis       = st.session_state.calc_fhis
        all_scores = st.session_state.calc_scores
        rate       = st.session_state.calc_rate
        days       = st.session_state.calc_days
        cur        = fhis[-1]
        status, color, bg, icon = fhi_status(cur)
        remark_text, remark_sub, remark_col, remark_bg = water_remark(cur)
        imp_pct = compare_with_tap(cur)
        dcol = "#EF4444" if days and days < 14 else "#10B981"
        dhint = (datetime.now()+timedelta(days=days)).strftime('%d %b %Y') if days else "Filter stable"
        rc = "#EF4444" if rate < -8 else "#F59E0B" if rate < -4 else "#10B981"

        st.markdown("<br>", unsafe_allow_html=True)

        # Remark
        st.markdown(f"""
        <div class="gc" style="border-color:{remark_col}44;background:{remark_bg};margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="font-size:28px;">{remark_text.split()[0]}</div>
                <div>
                    <div style="font-family:'Inter',sans-serif;font-size:15px;font-weight:700;color:{remark_col};">
                        {" ".join(remark_text.split()[1:])}</div>
                    <div style="font-size:11.5px;color:#94A3B8;margin-top:2px;">{remark_sub}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # KPIs
        k1,k2,k3,k4,k5 = st.columns(5, gap="small")
        with k1: st.markdown(kpi_card("Current FHI", f"{cur:.1f}", "/ 100", color), unsafe_allow_html=True)
        with k2: st.markdown(kpi_card("Status", f"{icon} {status}", "BIS Assessment", color), unsafe_allow_html=True)
        with k3: st.markdown(kpi_card("vs Tap Water", f"+{imp_pct:.0f}%", f"Tap ≈ {TAP_FHI:.0f}", "#A78BFA"), unsafe_allow_html=True)
        with k4: st.markdown(kpi_card("Rate/Week", f"{rate:+.2f}", "FHI pts", rc), unsafe_allow_html=True)
        with k5: st.markdown(kpi_card("Maintenance In", f"{days}d" if days else "Stable", dhint, dcol), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts
        ch1, ch2 = st.columns([3, 2], gap="medium")
        with ch1:
            st.markdown('<div class="gc">', unsafe_allow_html=True)
            st.plotly_chart(chart_trend(fhis), use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with ch2:
            st.markdown('<div class="gc">', unsafe_allow_html=True)
            if all_scores:
                st.plotly_chart(chart_radar(all_scores[-1], f"Week {len(fhis)}"),
                                use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        # Bar comparison
        st.markdown('<div class="gc" style="margin-top:4px;">', unsafe_allow_html=True)
        st.plotly_chart(chart_bar_comparison(fhis), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Detailed breakdown table with BIS comparison
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="gc">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">Weekly FHI & BIS Deviation Breakdown</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-s">Score = 100 when inside BIS ideal. Drops as water deviates from standard.</div>', unsafe_allow_html=True)

        # Build parameter comparison table HTML
        week_data = load_water(uid)
        tbl_html = """
        <table class="cmp-table">
        <thead><tr>
            <th>Week</th>
            <th>pH <small style="font-weight:400;">(BIS 6.5–8.5)</small></th>
            <th>TDS <small style="font-weight:400;">(BIS 150–300)</small></th>
            <th>Hardness <small style="font-weight:400;">(BIS ≤200)</small></th>
            <th>Alkalinity <small style="font-weight:400;">(BIS ≤300)</small></th>
            <th>FHI Score</th>
            <th>vs Tap</th>
            <th>Water Remark</th>
        </tr></thead><tbody>"""

        for i, (fhi, sc) in enumerate(zip(fhis, all_scores)):
            s, c, _, ico = fhi_status(fhi)
            imp = compare_with_tap(fhi)
            wd  = week_data[i] if i < len(week_data) else {}

            def p_tag(key, val):
                lvl, _ = validate_param(key, val)
                if lvl == "block": return f'<span style="color:#EF4444;font-weight:600;">{val}</span> <span class="tag tag-bad">Block</span>'
                if lvl == "warn":  return f'<span style="color:#F59E0B;">{val}</span> <span class="tag tag-warn">Warn</span>'
                return f'<span style="color:#10B981;">{val}</span> <span class="tag tag-ok">OK</span>'

            ph_v  = wd.get("ph",        0)
            tds_v = wd.get("tds",       0)
            har_v = wd.get("hardness",  0)
            alk_v = wd.get("alkalinity",0)

            rem_t, _, rem_c, _ = water_remark(fhi)
            short_rem = " ".join(rem_t.split()[1:3]) if len(rem_t.split()) > 2 else rem_t

            tbl_html += f"""<tr>
                <td><strong>Week {i+1}</strong></td>
                <td>{p_tag("ph", f"{ph_v:.2f}")}</td>
                <td>{p_tag("tds", f"{tds_v:.0f}")}</td>
                <td>{p_tag("hardness", f"{har_v:.0f}")}</td>
                <td>{p_tag("alkalinity", f"{alk_v:.0f}")}</td>
                <td><span style="font-family:'Inter',sans-serif;font-weight:800;color:{c};font-size:15px;">{fhi:.1f}</span></td>
                <td><span style="color:#A78BFA;font-weight:600;">+{imp:.0f}%</span></td>
                <td><span style="color:{rem_c};font-size:11px;">{short_rem}</span></td>
            </tr>"""

        # Tap water reference row
        tap_imp = 0
        tbl_html += f"""<tr style="background:rgba(99,102,241,0.05);">
            <td><strong>🚰 Tap Water</strong><br><small style="color:#64748B;">Reference (typical)</small></td>
            <td><span class="tag tag-tap">~7.8</span></td>
            <td><span class="tag tag-tap">~520</span></td>
            <td><span class="tag tag-tap">~310</span></td>
            <td><span class="tag tag-tap">~340</span></td>
            <td><span style="font-family:'Inter',sans-serif;font-weight:800;color:#A78BFA;font-size:15px;">{TAP_FHI:.1f}</span></td>
            <td><span style="color:#64748B;">baseline</span></td>
            <td><span style="color:#EF4444;font-size:11px;">Unsafe Raw</span></td>
        </tr>"""

        # BIS ideal row
        tbl_html += f"""<tr style="background:rgba(16,185,129,0.04);">
            <td><strong>🟢 BIS Ideal</strong><br><small style="color:#64748B;">IS 10500:2012</small></td>
            <td><span class="tag tag-ok">7.5</span></td>
            <td><span class="tag tag-ok">225</span></td>
            <td><span class="tag tag-ok">100</span></td>
            <td><span class="tag tag-ok">150</span></td>
            <td><span style="font-family:'Inter',sans-serif;font-weight:800;color:#10B981;font-size:15px;">{BIS_FHI:.1f}</span></td>
            <td><span style="color:#10B981;">target</span></td>
            <td><span style="color:#10B981;font-size:11px;">Safe for Drinking</span></td>
        </tr>"""

        tbl_html += "</tbody></table>"
        st.markdown(tbl_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  NAV: MAINTENANCE
# ══════════════════════════════════════════════════════════════
def nav_maintenance():
    top_bar("🔧 Post-Maintenance Prediction",
            "Enter a fresh reading after cleaning/replacing — predict next service window")
    uid    = st.session_state.user["user_id"]
    latest = load_latest(uid)
    saved_rate = latest.get("deterioration_rate") if latest else None

    # Concept explanation
    st.markdown("""
    <div class="info-strip">
        <strong>How post-maintenance prediction works:</strong><br>
        After cleaning or replacing your filter, it resets toward BIS-ideal quality (high FHI).
        The system applies your <em>historically measured deterioration rate</em> to the new FHI
        and calculates how many days until the filter degrades back to the critical threshold (FHI = 40).
    </div>
    """, unsafe_allow_html=True)

    if not saved_rate:
        st.markdown("""<div class="warn-strip">
            ⚠️ No deterioration rate available. Complete the
            <strong>Enter Data</strong> tab with 4 weeks of readings first.
        </div>""", unsafe_allow_html=True)
    else:
        rd = "#EF4444" if saved_rate < -8 else "#F59E0B" if saved_rate < -4 else "#10B981"
        st.markdown(f"""<div class="ok-strip">
            ✅ <strong>Using saved deterioration rate:</strong>
            <span style="font-family:'Inter',sans-serif;font-weight:700;color:{rd};">{saved_rate:+.3f} FHI/week</span>
            — This rate was measured from your 4-week data and represents how fast your filter degrades.
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="gc">', unsafe_allow_html=True)
    st.markdown('<div class="sec-h">Post-Maintenance Water Quality Reading</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Enter one fresh reading immediately after maintenance</div>', unsafe_allow_html=True)

    mc1, mc2, mc3, mc4 = st.columns(4, gap="medium")
    with mc1:
        m_ph  = st.number_input("pH", min_value=0.0, max_value=14.0, step=0.01,
                                value=7.2, format="%.2f", key="m_ph",
                                help="BIS safe: 6.5–8.5  |  Any value accepted")
    with mc2:
        m_tds = st.number_input("TDS (mg/L)", min_value=0.0, max_value=2000.0,
                                step=1.0, value=200.0, key="m_tds",
                                help="BIS safe: 150–300 mg/L  |  Any value accepted")
    with mc3:
        m_har = st.number_input("Hardness (mg/L)", min_value=0.0, max_value=1000.0,
                                step=1.0, value=100.0, key="m_har",
                                help="BIS safe max: 200 mg/L  |  Any value accepted")
    with mc4:
        m_alk = st.number_input("Alkalinity (mg/L)", min_value=0.0, max_value=1000.0,
                                step=1.0, value=140.0, key="m_alk",
                                help="BIS safe max: 300 mg/L  |  Any value accepted")

    readings_m = {"ph": m_ph, "tds": m_tds, "hardness": m_har, "alkalinity": m_alk}
    render_validation_messages(readings_m)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    bc, _ = st.columns([2, 3])
    with bc:
        if st.button("🔮  Predict Next Maintenance Date", key="maint_btn"):
            new_fhi, new_scores = calc_fhi(m_ph, m_tds, m_har, m_alk)
            use_rate = saved_rate if saved_rate and saved_rate < 0 else -5.0
            m_days   = predict_days(new_fhi, use_rate)
            save_result(uid, [new_fhi], use_rate, m_days, is_post=1)

            status, color, bg, icon = fhi_status(new_fhi)
            remark_text, remark_sub, remark_col, remark_bg = water_remark(new_fhi)
            mdate   = (datetime.now()+timedelta(days=m_days)).strftime('%d %b %Y') if m_days else "—"
            dcol    = "#EF4444" if m_days and m_days < 14 else "#10B981"
            imp_pct = compare_with_tap(new_fhi)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="gc" style="border-color:{remark_col}44;background:{remark_bg};">
                <div style="font-family:'Inter',sans-serif;font-size:14px;font-weight:700;
                    color:{remark_col};margin-bottom:14px;">✅ Next Maintenance Prediction</div>
                <div style="display:flex;gap:12px;flex-wrap:wrap;">
                    {kpi_card("Post-Maint FHI", f"{new_fhi:.1f}", "/ 100", color)}
                    {kpi_card("Condition", f"{icon} {status}", "BIS Assessment", color)}
                    {kpi_card("vs Tap Water", f"+{imp_pct:.0f}%", f"Tap ≈ {TAP_FHI:.0f}", "#A78BFA")}
                    {kpi_card("Next Service In", f"{m_days}d" if m_days else "Stable", mdate, dcol)}
                    {kpi_card("Rate Applied", f"{use_rate:+.3f}", "FHI / week", "#F59E0B")}
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="gc">', unsafe_allow_html=True)
            st.plotly_chart(chart_radar(new_scores, "Post-Maintenance"),
                            use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f"""
            <div class="gc" style="border-color:{remark_col}44;background:{remark_bg};">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="font-size:28px;">{remark_text.split()[0]}</div>
                    <div>
                        <div style="font-family:'Inter',sans-serif;font-weight:700;color:{remark_col};">
                            {" ".join(remark_text.split()[1:])}</div>
                        <div style="font-size:11.5px;color:#94A3B8;margin-top:2px;">{remark_sub}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  NAV: HISTORY
# ══════════════════════════════════════════════════════════════
def nav_history():
    top_bar("📋 Assessment History", "All saved filter health records for your account")
    uid     = st.session_state.user["user_id"]
    all_res = load_all_results(uid)

    if not all_res:
        st.markdown("""
        <div class="gc" style="text-align:center;padding:52px;">
            <div style="font-size:44px;margin-bottom:12px;">📭</div>
            <div class="sec-h">No history yet</div>
            <div style="font-size:12.5px;color:#475569;margin-top:5px;">
                Complete your first data entry to see records here.</div>
        </div>""", unsafe_allow_html=True)
        return

    rows, fhi_tl, date_tl = [], [], []
    for r in all_res:
        fhis_r = [v for v in [r.get(f"fhi_w{i}") for i in range(1,5)] if v]
        cur = fhis_r[-1] if fhis_r else 0
        s, c, _, ico = fhi_status(cur)
        rt, _, rc, _ = water_remark(cur)
        imp = compare_with_tap(cur)
        dt  = r.get("calc_date","")[:16].replace("T"," ")
        rows.append({
            "Date":           dt,
            "FHI":            f"{cur:.1f}",
            "Status":         f"{ico} {s}",
            "vs Tap Water":   f"+{imp:.0f}%",
            "Rate (FHI/wk)":  f"{r.get('deterioration_rate',0):+.3f}",
            "Maintenance In": f"{r.get('maintenance_days','—')}d" if r.get('maintenance_days') else "Stable",
            "Water Remark":   " ".join(rt.split()[1:]),
            "Type":           "🔧 Post-Maint." if r.get("is_post_maintenance") else "📊 Assessment",
        })
        fhi_tl.append(cur); date_tl.append(dt)

    st.markdown('<div class="gc">', unsafe_allow_html=True)
    st.markdown('<div class="sec-h">All Assessments</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if len(fhi_tl) >= 2:
        st.markdown("<br>", unsafe_allow_html=True)
        fig = go.Figure()

        # Zone bands
        for y0, y1, col in [
            (80,100,"rgba(16,185,129,0.05)"),
            (60,80, "rgba(245,158,11,0.05)"),
            (40,60, "rgba(249,115,22,0.05)"),
            (0, 40, "rgba(239,68,68,0.06)"),
        ]:
            fig.add_hrect(y0=y0, y1=y1, fillcolor=col, line_width=0)

        # Critical + tap lines via shapes (no deprecated annotation_position)
        fig.add_shape(type="line", x0=0, x1=1, xref="paper",
                      y0=40, y1=40, yref="y",
                      line=dict(color="#EF4444", dash="dash", width=1.4))
        fig.add_annotation(x=1, xref="paper", xanchor="right",
                           y=40, yref="y", yanchor="top",
                           text=" Critical (40)", showarrow=False,
                           font=dict(color="#EF4444", size=10, family="Inter"),
                           bgcolor="rgba(0,0,0,0)")

        fig.add_shape(type="line", x0=0, x1=1, xref="paper",
                      y0=round(TAP_FHI,1), y1=round(TAP_FHI,1), yref="y",
                      line=dict(color="#A78BFA", dash="dot", width=1.2))
        fig.add_annotation(x=0, xref="paper", xanchor="left",
                           y=round(TAP_FHI,1), yref="y", yanchor="bottom",
                           text=f" Tap Water ~{TAP_FHI:.0f}", showarrow=False,
                           font=dict(color="#A78BFA", size=10, family="Inter"),
                           bgcolor="rgba(0,0,0,0)")

        fig.add_trace(go.Scatter(
            x=date_tl[::-1], y=fhi_tl[::-1],
            mode="lines+markers", name="FHI",
            line=dict(color="#3B82F6", width=2.5),
            marker=dict(size=8, color="#38BDF8",
                        line=dict(color="#060A10", width=2)),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
            hovertemplate="<b>%{x}</b><br>FHI: %{y:.1f}<extra></extra>",
        ))

        lay = _base_layout(height=290,
                           title_text="FHI History vs Tap Water Reference",
                           show_legend=False)
        lay["yaxis"]["range"] = [0, 110]
        lay["yaxis"]["title"] = "FHI Score"
        lay["xaxis"]["title"] = "Session Date"
        lay["margin"] = dict(l=52, r=100, t=44, b=40)
        fig.update_layout(**lay)

        st.markdown('<div class="gc">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-bar">
        💧 HydroGuard · BIS IS 10500:2012 Compliant · Data-Driven Virtual Filter Maintenance Model<br>
        <span style="opacity:.4;font-size:10px;">
            Not a substitute for certified laboratory analysis · For educational/monitoring purposes
        </span>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page == "register":
        page_register()
    else:
        page_login()
else:
    render_sidebar()
    nav = st.session_state.nav
    if   nav == "dashboard":   nav_dashboard()
    elif nav == "enter_data":  nav_enter_data()
    elif nav == "maintenance": nav_maintenance()
    elif nav == "history":     nav_history()
    else:                      nav_dashboard()