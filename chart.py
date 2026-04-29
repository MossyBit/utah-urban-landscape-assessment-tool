# chart.py
# ─────────────────────────────────────────────────────────────────────────────
# Responsible for ONE thing: taking a scores dictionary and returning a
# matplotlib figure. No Streamlit code lives here at all.
#
# WHY that matters:
#   This function could be called from a Streamlit app, a Jupyter notebook,
#   a script, or anything else — it doesn't care. It just makes a chart.
#   This is called being "UI-agnostic" and makes code much easier to reuse.
#
# HOW other files use this:
#   from chart import build_radar_figure
#   fig = build_radar_figure(scores_dict)
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np
import matplotlib.pyplot as plt

from data import CATEGORIES


def build_radar_figure(scores_dict):
    """
    Build and return the TROLL radar chart as a matplotlib Figure.

    Parameters
    ----------
    scores_dict : dict
        Keys are the string keys from CATEGORIES (e.g. "IrrigationScheduling"),
        values are integers 0–5.

    Returns
    -------
    matplotlib.figure.Figure
    """

    # ── Flatten data into parallel lists ─────────────────────────────────────
    # We need three aligned lists — labels, scores, colors — one entry per
    # spoke, in the order they'll appear around the chart.
    all_labels, all_scores, all_colors = [], [], []
    cat_ranges = {}   # tracks which index range belongs to each category
    idx = 0

    for cat_name, cat_data in CATEGORIES.items():
        n = len(cat_data["subcategories"])
        cat_ranges[cat_name] = (idx, idx + n)
        all_labels.extend(cat_data["subcategories"])
        all_scores.extend([scores_dict[k] for k in cat_data["keys"]])
        all_colors.extend([cat_data["color"]] * n)
        idx += n

    # ── Geometry ──────────────────────────────────────────────────────────────
    N             = len(all_labels)
    spoke_gap     = 2 * np.pi / N          # angle between spokes
    half_gap      = spoke_gap / 2.0
    spoke_angles  = np.linspace(0, 2 * np.pi, N, endpoint=False)
    center_angles = spoke_angles + half_gap # label sits between spokes
    scores_norm   = np.array(all_scores) / 5

    # ── Smooth curve via interpolation ────────────────────────────────────────
    # We wrap the array at both ends so the interpolation closes smoothly.
    extended_angles = np.concatenate([
        [center_angles[-1] - 2*np.pi],
        center_angles,
        [center_angles[0]  + 2*np.pi],
    ])
    extended_scores = np.concatenate([
        [scores_norm[-1]], scores_norm, [scores_norm[0]]
    ])
    DENSE        = 600
    dense_angles = np.linspace(
        center_angles[0] - half_gap,
        center_angles[-1] + half_gap,
        DENSE
    )
    dense_scores = np.interp(dense_angles, extended_angles, extended_scores)

    # ── Figure setup ─────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 11), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    LABEL_R  = 1.25
    RING_BOT = 1.125
    RING_H   = 0.1
    CAT_R    = RING_BOT + RING_H

    # ── Category fills and lines ──────────────────────────────────────────────
    for cat_name, cat_data in CATEGORIES.items():
        start, end  = cat_ranges[cat_name]
        color       = cat_data["color"]
        angle_start = center_angles[start] - half_gap
        angle_end   = center_angles[end - 1] + half_gap
        mask        = (dense_angles >= angle_start) & (dense_angles <= angle_end)
        slice_angles = dense_angles[mask]
        slice_scores = dense_scores[mask]
        fill_a = np.concatenate([[slice_angles[0]], slice_angles, [slice_angles[-1]]])
        fill_r = np.concatenate([[-0.2], slice_scores, [-0.2]])
        ax.fill(fill_a, fill_r, color=color, alpha=0.30, zorder=2)
        ax.plot(slice_angles, slice_scores, color=color, linewidth=2.5, alpha=0.90, zorder=3)

    # ── Scatter points ────────────────────────────────────────────────────────
    for cat_name, cat_data in CATEGORIES.items():
        start, end = cat_ranges[cat_name]
        ax.scatter(
            center_angles[start:end], scores_norm[start:end],
            color=cat_data["color"], s=60, zorder=5, linewidths=0
        )

    # ── Grid ──────────────────────────────────────────────────────────────────
    ax.set_ylim(-.2, CAT_R)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0", "1", "2", "3", "4", "5"], color="black", size=7.5)
    ax.grid(color="black", linestyle="-", linewidth=0.5, alpha=0.7)
    ax.spines["polar"].set_visible(False)
    ax.set_xticks([])

    # ── Spoke labels ──────────────────────────────────────────────────────────
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

    # ── Outer color rings ─────────────────────────────────────────────────────
    spoke_index = 0
    for cat_name, cat_data in CATEGORIES.items():
        n_sub      = len(cat_data["subcategories"])
        cat_angles = spoke_angles[spoke_index:spoke_index + n_sub]
        ax.bar(
            x=cat_angles, height=RING_H, width=spoke_gap * 0.97,
            bottom=RING_BOT, color=cat_data["color"],
            alpha=0.92, linewidth=0, zorder=4, align="edge"
        )
        spoke_index += n_sub

    # ── Category title labels ─────────────────────────────────────────────────
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
