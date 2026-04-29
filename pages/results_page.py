# pages/results_page.py
# ─────────────────────────────────────────────────────────────────────────────
# Responsible for ONE thing: the review + chart generation page.
# Reads scores from st.session_state, calls build_radar_figure from chart.py,
# and handles the download. Knows nothing about sliders or input steps.
#
# HOW the main app uses this:
#   from pages.results_page import page_review
# ─────────────────────────────────────────────────────────────────────────────

import io

import matplotlib.pyplot as plt
import streamlit as st

from chart import build_radar_figure
from data import CATEGORIES


def page_review():
    """Render the review summary and chart generation page."""

    st.markdown("## Your Assessment")
    st.caption("Review your scores below, then generate your radar chart.")

    # ── Score summary — one column per category ───────────────────────────────
    cols = st.columns(3)
    for col, (cat_name, cat) in zip(cols, CATEGORIES.items()):
        with col:
            st.markdown(
                f'<div style="color:{cat["color"]};font-weight:600;font-size:0.85rem;'
                f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">'
                f'{cat_name}</div>',
                unsafe_allow_html=True
            )
            for label, key in zip(cat["subcategories"], cat["keys"]):
                score = st.session_state.scores[key]
                bar   = "█" * score + "░" * (5 - score)
                st.markdown(
                    f'<div style="font-size:0.8rem;margin-bottom:4px;">'
                    f'{label}<br>'
                    f'<span style="color:{cat["color"]};font-family:monospace;">{bar}</span>'
                    f' <span style="color:#aaa;">{score}/5</span></div>',
                    unsafe_allow_html=True
                )

    st.divider()

    # ── Action buttons ────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("← Edit Scores", use_container_width=True):
            st.session_state.step = 0
            st.rerun()

    with col2:
        if st.button("Generate Chart", type="primary", use_container_width=True):
            with st.spinner("Building your radar chart..."):
                fig = build_radar_figure(st.session_state.scores)

                # BytesIO = an in-memory file buffer.
                # We save to memory instead of disk so the app works cleanly
                # on any server without needing write permissions.
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=150,
                            facecolor=fig.get_facecolor(), bbox_inches="tight")
                buf.seek(0)
                plt.close(fig)

            st.pyplot(fig)

            st.download_button(
                label="⬇ Download PNG",
                data=buf,
                file_name="urban_landscape_radar.png",
                mime="image/png",
                use_container_width=True
            )
