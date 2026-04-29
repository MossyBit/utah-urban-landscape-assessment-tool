import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Urban Landscape Assessment",
    page_icon="🌿",
    layout="centered"
)

# ── CUSTOM STYLES ─────────────────────────────────────────────────────────────
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

    /* Score guide */
    .score-guide {
        background: #25262B;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.8rem;
        color: #aaa;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ── DATA STRUCTURE ────────────────────────────────────────────────────────────
# This mirrors your notebook exactly — one dictionary drives the whole app.
# If you ever add a category or subcategory, you only change this block.

CATEGORIES = {
    "WATER CONSERVATION": {
        "subcategories": [
            "Irrigation Scheduling",
            "Irrigation Audit",
            "Functional Turf Coverage",
            "Turfgrass Species & Management",
            "Non-Turfgrass Areas",
            "Other Water Conservation",
        ],
        "color": "#4285F4",
        "keys": [
            "IrrigationScheduling",
            "IrrigationAudit",
            "FunctionalTurfCoverage",
            "TurfgrassSpeciesManagement",
            "NonTurfgrassAreas",
            "OtherWaterConservation",
        ],
        "css_class": "cat-water",
    },
    "ECOSYSTEM SERVICES": {
        "subcategories": [
            "Soil Health",
            "Biodiversity & Biomass",
            "Invasive Plants",
            "Native Plants",
            "Urban Heat Reduction",
            "Wildlife & Pollinator Support",
        ],
        "color": "#2A9D8F",
        "keys": [
            "SoilHealth",
            "BiodiversityBiomass",
            "InvasivePlants",
            "NativePlants",
            "UrbanHeatReduction",
            "WildlifePollinatorSupport",
        ],
        "css_class": "cat-ecosystem",
    },
    "DESIGN AND MANAGEMENT": {
        "subcategories": [
            "Energy Consumption",
            "Light Pollution",
            "Responsible Waste Disposal",
            "Sustainable Care",
            "Physical & Social Wellbeing",
            "Mental Wellbeing",
        ],
        "color": "#E9C46A",
        "keys": [
            "EnergyConsumption",
            "LightPollution",
            "ResponsibleWasteDisposal",
            "SustainableCare",
            "PhysicalSocialWellbeing",
            "MentalWellbeing",
        ],
        "css_class": "cat-design",
    },
}

CAT_NAMES = list(CATEGORIES.keys())

# ── SESSION STATE ─────────────────────────────────────────────────────────────
# st.session_state is Streamlit's way of remembering values between reruns.
# Every time a user interacts with a widget, Streamlit reruns the whole script
# from top to bottom — session_state lets values persist across those reruns.

if "step" not in st.session_state:
    st.session_state.step = 0        # which category we're on (0, 1, 2, or 3=review)

if "scores" not in st.session_state:
    # Pre-fill every key with 0 so sliders always have a starting value
    st.session_state.scores = {
        key: 0
        for cat in CATEGORIES.values()
        for key in cat["keys"]
    }


# ── HELPER: step indicator dots ───────────────────────────────────────────────
def render_step_dots(current_step):
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


# ── HELPER: build and return the radar figure ─────────────────────────────────
# This is your original chart code, reorganized into a function.
# A function is better here because we call it on the review page — keeping
# the chart logic separate from the UI logic makes both easier to maintain.

def build_radar_figure(scores_dict):
    # Flatten all data into parallel lists (same logic as your notebook)
    all_labels, all_scores, all_colors = [], [], []
    cat_ranges = {}
    idx = 0

    for cat_name, cat_data in CATEGORIES.items():
        n = len(cat_data["subcategories"])
        cat_ranges[cat_name] = (idx, idx + n)
        all_labels.extend(cat_data["subcategories"])
        all_scores.extend([scores_dict[k] for k in cat_data["keys"]])
        all_colors.extend([cat_data["color"]] * n)
        idx += n

    N = len(all_labels)
    spoke_gap   = 2 * np.pi / N
    half_gap    = spoke_gap / 2.0
    spoke_angles  = np.linspace(0, 2 * np.pi, N, endpoint=False)
    center_angles = spoke_angles + half_gap
    scores_norm   = np.array(all_scores) / 5

    # Smooth interpolated curve (same as your notebook)
    extended_angles = np.concatenate([
        [center_angles[-1] - 2*np.pi],
        center_angles,
        [center_angles[0]  + 2*np.pi],
    ])
    extended_scores = np.concatenate([
        [scores_norm[-1]], scores_norm, [scores_norm[0]]
    ])
    DENSE = 600
    dense_angles = np.linspace(
        center_angles[0] - half_gap,
        center_angles[-1] + half_gap,
        DENSE
    )
    dense_scores = np.interp(dense_angles, extended_angles, extended_scores)

    # ── FIGURE ────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 11), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    LABEL_R = 1.25
    RING_BOT = 1.125
    RING_H   = 0.1
    CAT_R    = RING_BOT + RING_H

    # Category fills & lines
    for cat_name, cat_data in CATEGORIES.items():
        start, end = cat_ranges[cat_name]
        color = cat_data["color"]
        angle_start = center_angles[start] - half_gap
        angle_end   = center_angles[end - 1] + half_gap
        mask = (dense_angles >= angle_start) & (dense_angles <= angle_end)
        slice_angles = dense_angles[mask]
        slice_scores = dense_scores[mask]
        fill_a = np.concatenate([[slice_angles[0]], slice_angles, [slice_angles[-1]]])
        fill_r = np.concatenate([[-0.2], slice_scores, [-0.2]])
        ax.fill(fill_a, fill_r, color=color, alpha=0.30, zorder=2)
        ax.plot(slice_angles, slice_scores, color=color, linewidth=2.5, alpha=0.90, zorder=3)

    # Scatter points
    for cat_name, cat_data in CATEGORIES.items():
        start, end = cat_ranges[cat_name]
        ax.scatter(
            center_angles[start:end], scores_norm[start:end],
            color=cat_data["color"], s=60, zorder=5, linewidths=0
        )

    # Grid
    ax.set_ylim(-.2, CAT_R)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0","1","2","3","4","5"], color="black", size=7.5)
    ax.grid(color="black", linestyle="-", linewidth=0.5, alpha=0.7)
    ax.spines["polar"].set_visible(False)
    ax.set_xticks([])

    # Spoke labels
    for label, angle, color in zip(all_labels, center_angles, all_colors):
        screen_deg = (90 - np.degrees(angle) + 180) % 360 - 180
        if -90 < screen_deg <= 90:
            rot, ha = screen_deg, "left"
        else:
            rot, ha = screen_deg + 180, "right"
        ax.text(
            angle, LABEL_R, "  " + label,
            ha=ha, va="center", fontsize=10,
            color=color, fontweight="bold",
            rotation=rot, rotation_mode="anchor", zorder=6
        )

    # Outer rings (colored bars per category)
    spoke_index = 0
    for cat_name, cat_data in CATEGORIES.items():
        n_sub = len(cat_data["subcategories"])
        cat_angles = spoke_angles[spoke_index:spoke_index + n_sub]
        ax.bar(
            x=cat_angles, height=RING_H, width=spoke_gap * 0.97,
            bottom=RING_BOT, color=cat_data["color"],
            alpha=0.92, linewidth=0, zorder=4, align="edge"
        )
        spoke_index += n_sub

    # Category legend labels
    fig.text(1,    0.95, "WATER CONSERVATION",
             ha="center", va="center", fontsize=15, fontweight="bold",
             color=CATEGORIES["WATER CONSERVATION"]["color"])
    fig.text(0.51, -0.1, "ECOSYSTEM SERVICES",
             ha="center", va="center", fontsize=15, fontweight="bold",
             color=CATEGORIES["ECOSYSTEM SERVICES"]["color"])
    fig.text(0.0,  0.95, "DESIGN AND MANAGEMENT",
             ha="center", va="center", fontsize=15, fontweight="bold",
             color=CATEGORIES["DESIGN AND MANAGEMENT"]["color"])

    ax.set_title("Urban Landscape Assessment", size=24, color="black",
                 fontweight="bold", pad=150)

    return fig


# ── PAGES ─────────────────────────────────────────────────────────────────────

def page_category(step_idx):
    """Input page for one category."""
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

    # One slider per subcategory.
    # st.slider returns the current value and automatically stores it via the key= argument.
    # The key= parameter links the widget directly to st.session_state[key].
    for label, key in zip(cat["subcategories"], cat["keys"]):
        st.session_state.scores[key] = st.slider(
            label=label,
            min_value=0,
            max_value=5,
            value=st.session_state.scores[key],
            key=f"slider_{key}"   # unique widget ID — Streamlit requires these to be unique
        )

    st.divider()

    col1, col2 = st.columns([1, 1])
    with col1:
        if step_idx > 0:
            if st.button("← Back", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()   # tells Streamlit to re-run the script immediately
    with col2:
        label = "Next →" if step_idx < len(CAT_NAMES) - 1 else "Review & Generate Chart →"
        if st.button(label, type="primary", use_container_width=True):
            st.session_state.step += 1
            st.rerun()


def page_review():
    """Final review page with chart generation and download."""
    st.markdown("## Your Assessment")
    st.caption("Review your scores below, then generate your radar chart.")

    # Summary table — one column per category
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

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("← Edit Scores", use_container_width=True):
            st.session_state.step = 0
            st.rerun()

    with col2:
        if st.button("Generate Chart", type="primary", use_container_width=True):
            with st.spinner("Building your radar chart..."):
                fig = build_radar_figure(st.session_state.scores)

                # Save figure to an in-memory buffer (BytesIO) instead of a file.
                # This is important for web apps — you don't want to write to disk
                # on a server you don't control.
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=150,
                            facecolor=fig.get_facecolor(), bbox_inches="tight")
                buf.seek(0)   # rewind buffer to the start so it can be read
                plt.close(fig)

            st.pyplot(fig)   # display in the app

            # st.download_button gives the user a real file download
            st.download_button(
                label="⬇ Download PNG",
                data=buf,
                file_name="urban_landscape_radar.png",
                mime="image/png",
                use_container_width=True
            )


# ── MAIN ROUTER ───────────────────────────────────────────────────────────────
# This is the "router" — it decides which page function to call based on
# the current step stored in session_state. This is a simple but powerful
# pattern you'll see in almost every multi-page app.

st.title("🌿 Urban Landscape Assessment")
st.caption("TROLL Radar Plot — step through each category to enter your scores.")
st.divider()

current = st.session_state.step

if current < len(CAT_NAMES):
    page_category(current)
else:
    page_review()
