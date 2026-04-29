# troll_radar_app.py
# ─────────────────────────────────────────────────────────────────────────────
# Entry point — the only file Streamlit runs directly.
# Its job is three things only:
#   1. Page config and shared CSS styles
#   2. Initialize session state
#   3. Route to the right page based on st.session_state.step
#
# If you want to change how a page looks or works, go to pages/.
# If you want to change the chart, go to chart.py.
# If you want to change categories or colors, go to data.py.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

from data import CATEGORIES, CAT_NAMES
from pages.input_page import page_category
from pages.results_page import page_review

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Utah Urban Landscape Assessment",
    page_icon="🌳",
    layout="centered"
)

# ── SHARED CSS STYLES ─────────────────────────────────────────────────────────
# These styles live here because they apply to every page.
# Page-specific styles belong in the page files themselves.
st.markdown("""
<style>
    /* Dark background to match the chart aesthetic */
    .stApp { background-color: #1a1b1e; color: #e0e0e0; }
    .stApp h1, .stApp h2, .stApp h3 { color: #ffffff; }

    /* Progress step indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 1.5rem;
    }
    .step-dot {
        width: 12px; height: 12px;
        border-radius: 50%;
        background: #444;
        display: inline-block;
    }
    .step-dot.active { background: #4285F4; }
    .step-dot.done  { background: #2A9D8F; }

    /* Category header colors */
    .cat-water     { color: #4285F4 !important; }
    .cat-ecosystem { color: #2A9D8F !important; }
    .cat-design    { color: #E9C46A !important; }

    /* Score guide box */
    .score-guide {
        background: #ffffff;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.8rem;
        color: #aaa;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INITIALIZATION ──────────────────────────────────────────────
# We only set these if they don't exist yet.
# On the very first run, step=0 and all scores=0.
# On every subsequent rerun (caused by any widget interaction),
# these lines are skipped and the existing values are preserved.

if "step" not in st.session_state:
    st.session_state.step = 0

if "scores" not in st.session_state:
    st.session_state.scores = {
        key: 0
        for cat in CATEGORIES.values()
        for key in cat["keys"]
    }

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🌿 Urban Landscape Assessment")
st.caption("TROLL Radar Plot — step through each category to enter your scores.")
st.divider()

# ── ROUTER ────────────────────────────────────────────────────────────────────
# One line of logic: if we're still on an input step, show that step's page.
# Once step equals the number of categories, show the results page.

current = st.session_state.step

if current < len(CAT_NAMES):
    page_category(current)
else:
    page_review()
