# ui/input_page.py
# ─────────────────────────────────────────────────────────────────────────────
# Responsible for ONE thing: rendering the step-by-step scoring UI.
# Reads from data.py, writes to st.session_state. Knows nothing about charts.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

from data import CATEGORIES, CAT_NAMES


# ── SCORE DESCRIPTIONS ────────────────────────────────────────────────────────
# This is where you'll eventually add per-subcategory score descriptions.
# The structure is: { "Subcategory Label": { 0: "description", 1: "description", ... } }
#
# Right now every subcategory uses the GENERIC_DESCRIPTIONS fallback below.
# To add specific descriptions for a subcategory, add an entry here like:
#
#   "Irrigation Scheduling": {
#       0: "No irrigation scheduling in place.",
#       1: "Informal scheduling with no documentation.",
#       2: "Basic schedule exists but is rarely adjusted.",
#       3: "Seasonal schedule with some monitoring.",
#       4: "Data-driven schedule with regular audits.",
#       5: "Full smart irrigation with real-time adjustment.",
#   },
#
# When a subcategory has no entry here, it falls back to GENERIC_DESCRIPTIONS.

SCORE_DESCRIPTIONS = {
    # Add subcategory-specific descriptions here as you develop them
}

GENERIC_DESCRIPTIONS = {
    0: "Not implemented.",
    1: "Minimal — early stages, limited application.",
    2: "Developing — some practices in place but inconsistent.",
    3: "Established — consistently applied across the site.",
    4: "Advanced — well integrated with measurable outcomes.",
    5: "Exemplary — best practice, could serve as a model site.",
}


def get_description(subcategory_label, score):
    """
    Return the description for a given subcategory and score.
    Falls back to generic descriptions if no specific ones exist yet.
    """
    descriptions = SCORE_DESCRIPTIONS.get(subcategory_label, GENERIC_DESCRIPTIONS)
    return descriptions.get(score, "")


# ── STEP INDICATOR ────────────────────────────────────────────────────────────

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


# ── INPUT PAGE ────────────────────────────────────────────────────────────────

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

    
    st.markdown(
    f"""
    <style>
        button[kind="pills"][aria-pressed="true"] {{
            background-color: {cat["color"]} !important;
            color: white !important;
            border-color: {cat["color"]} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)



    # ── One pill selector per subcategory ─────────────────────────────────────
    # st.pills() renders a row of clickable rounded buttons.
    #
    # Key arguments:
    #   label        — the subcategory name shown above the buttons
    #   options      — the list of values to show as buttons
    #   default      — which value is selected when the page first loads
    #   key          — unique ID so Streamlit tracks this widget across reruns
    #   selection_mode="single" — only one button can be active at a time
    #
    # Like st.slider(), st.pills() returns the currently selected value,
    # so the rest of the app reads scores exactly the same way as before.

    for label, key in zip(cat["subcategories"], cat["keys"]):
        current_value = st.session_state.scores[key]

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

        # ── Score description ─────────────────────────────────────────────────
        # Shows the description for whichever score is currently selected.
        # Right now this uses generic descriptions for all subcategories.
        # As you build out SCORE_DESCRIPTIONS above, each subcategory will
        # automatically get its own specific text here — no other code changes.
        score_to_show = st.session_state.scores[key]
        description   = get_description(label, score_to_show)

        st.caption(f"_{description}_")
        st.divider()

    # ── Navigation buttons ────────────────────────────────────────────────────
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
