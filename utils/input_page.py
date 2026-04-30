# pages/input_page.py
# ─────────────────────────────────────────────────────────────────────────────
# Responsible for ONE thing: rendering the step-by-step scoring UI.
# Reads from data.py, writes to st.session_state. Knows nothing about charts.
#
# HOW the main app uses this:
#   from pages.input_page import page_category, render_step_dots
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

from data import CATEGORIES, CAT_NAMES


def render_step_dots(current_step):
    """Render the row of progress dots at the top of each input step."""
    dots_html = '<div class="step-indicator">'
    for i in range(len(CAT_NAMES)):
        if i < current_step:
            dots_html += '<div class="step-dot done"></div>'
        elif i == current_step:
            dots_html += '<div class="step-dot active"></div>'
        else:
            dots_html += '<div class="step-dot"></div>'
    dots_html += '</div>'
    st.markdown(dots_html, unsafe_allow_html=True)


def page_category(step_idx):
    """
    Render the input page for one category.

    Parameters
    ----------
    step_idx : int
        Index into CAT_NAMES — which category we're currently scoring.
    """
    cat_name = CAT_NAMES[step_idx]
    cat      = CATEGORIES[cat_name]

    render_step_dots(step_idx)

    st.markdown(
        f'<h2 class="{cat["css_class"]}">{cat_name}</h2>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="score-guide">
        <b>Score guide:</b> &nbsp;
        0 = Not implemented &nbsp;|&nbsp;
        1 = Minimal &nbsp;|&nbsp;
        2 = Developing &nbsp;|&nbsp;
        3 = Established &nbsp;|&nbsp;
        4 = Advanced &nbsp;|&nbsp;
        5 = Exemplary
    </div>
    """, unsafe_allow_html=True)

    for label, key in zip(cat["subcategories"], cat["keys"]):
        selected = st.pills(
            label=label,
            options=[0, 1, 2, 3, 4, 5],
            default=current_value,
            key=f"pills_{key}",
            selection_mode="single",
        )
 
        # st.pills() returns None if the user deselects everything.
        # We guard against that by keeping the previous value if None.
        if selected is not None:
            st.session_state.scores[key] = selected

    st.divider()

    col1, col2 = st.columns([1, 1])
    with col1:
        if step_idx > 0:
            if st.button("← Back", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()
    with col2:
        btn_label = "Next →" if step_idx < len(CAT_NAMES) - 1 else "Review & Generate Chart →"
        if st.button(btn_label, type="primary", use_container_width=True):
            st.session_state.step += 1
            st.rerun()
