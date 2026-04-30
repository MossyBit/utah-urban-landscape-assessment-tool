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
import matplotlib.gridspec as gridspec
# gridspec lets us divide a figure into a custom grid of panels (subplots).
# Think of it like a table layout — you define rows and columns, then place
# axes into specific cells. Much more flexible than plt.subplots() alone.

from data import CATEGORIES


def build_radar_figure(scores_dict):
    """
    Build and return the TROLL radar chart as a matplotlib Figure.
    The figure contains two panels side by side:
      - Left (wider):  the radar plot
      - Right (narrower): the score summary per category

    Parameters
    ----------
    scores_dict : dict
        Keys are the string keys from CATEGORIES (e.g. "IrrigationScheduling"),
        values are integers 0-5.

    Returns
    -------
    matplotlib.figure.Figure
    """

    # ── Flatten data into parallel lists ─────────────────────────────────────
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

    # ── Pre-calculate category totals for the summary panel ───────────────────
    # We do this before drawing anything so the summary panel has its data ready.
    # cat_totals: { cat_name: (total_score, max_possible, [subcategory_scores]) }
    cat_totals  = {}
    grand_total = 0
    grand_max   = 0

    for cat_name, cat_data in CATEGORIES.items():
        sub_scores = [scores_dict[k] for k in cat_data["keys"]]
        total      = sum(sub_scores)
        maximum    = len(sub_scores) * 5        # 6 subcategories x 5 = 30
        cat_totals[cat_name] = (total, maximum, sub_scores)
        grand_total += total
        grand_max   += maximum

    # ── Geometry ──────────────────────────────────────────────────────────────
    N             = len(all_labels)
    spoke_gap     = 2 * np.pi / N
    half_gap      = spoke_gap / 2.0
    spoke_angles  = np.linspace(0, 2 * np.pi, N, endpoint=False)
    center_angles = spoke_angles + half_gap
    scores_norm   = np.array(all_scores) / 5

    # ── Smooth curve via interpolation ────────────────────────────────────────
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

    # ── Figure and GridSpec layout ────────────────────────────────────────────
    # We create one figure with two columns:
    #   column 0 (width ratio 3): the radar chart
    #   column 1 (width ratio 1): the summary panel
    #
    # width_ratios=[3, 1] means the radar gets 3x the horizontal space.
    # wspace controls the gap between panels (in fraction of average axis width).

    fig = plt.figure(figsize=(15, 11))
    fig.patch.set_facecolor("#ffffff")

    gs = gridspec.GridSpec(
        nrows=1, ncols=2,
        width_ratios=[3, 1],
        figure=fig,
        wspace=0.05
    )

    # add_subplot with projection="polar" for the radar
    # gs[row, col] selects which cell in the grid
    ax_radar   = fig.add_subplot(gs[0, 0], projection="polar")
    ax_summary = fig.add_subplot(gs[0, 1])

    # ── Radar axes setup ──────────────────────────────────────────────────────
    ax_radar.set_facecolor("#ffffff")
    ax_radar.set_theta_offset(np.pi / 2)
    ax_radar.set_theta_direction(-1)

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
        ax_radar.fill(fill_a, fill_r, color=color, alpha=0.30, zorder=2)
        ax_radar.plot(slice_angles, slice_scores, color=color, linewidth=2.5, alpha=0.90, zorder=3)

    # ── Scatter points ────────────────────────────────────────────────────────
    for cat_name, cat_data in CATEGORIES.items():
        start, end = cat_ranges[cat_name]
        ax_radar.scatter(
            center_angles[start:end], scores_norm[start:end],
            color=cat_data["color"], s=60, zorder=5, linewidths=0
        )

    # ── Grid ──────────────────────────────────────────────────────────────────
    ax_radar.set_ylim(-.2, CAT_R)
    ax_radar.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax_radar.set_yticklabels(["0", "1", "2", "3", "4", "5"], color="black", size=7.5)
    ax_radar.grid(color="black", linestyle="-", linewidth=0.5, alpha=0.7)
    ax_radar.spines["polar"].set_visible(False)
    ax_radar.set_xticks([])

    # ── Spoke labels ──────────────────────────────────────────────────────────
    for label, angle, color in zip(all_labels, center_angles, all_colors):
        screen_deg = (90 - np.degrees(angle) + 180) % 360 - 180
        if -90 < screen_deg <= 90:
            rot, ha = screen_deg, "left"
        else:
            rot, ha = screen_deg + 180, "right"
        ax_radar.text(
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
        ax_radar.bar(
            x=cat_angles, height=RING_H, width=spoke_gap * 0.97,
            bottom=RING_BOT, color=cat_data["color"],
            alpha=0.92, linewidth=0, zorder=4, align="edge"
        )
        spoke_index += n_sub

    # ── Category title labels ─────────────────────────────────────────────────
    fig.text(0.72, 0.95, "WATER CONSERVATION",
             ha="center", va="center", fontsize=13, fontweight="bold",
             color=CATEGORIES["WATER CONSERVATION"]["color"])
    fig.text(0.38, -0.02, "ECOSYSTEM SERVICES",
             ha="center", va="center", fontsize=13, fontweight="bold",
             color=CATEGORIES["ECOSYSTEM SERVICES"]["color"])
    fig.text(0.04, 0.95, "DESIGN AND MANAGEMENT",
             ha="center", va="center", fontsize=13, fontweight="bold",
             color=CATEGORIES["DESIGN AND MANAGEMENT"]["color"])

    ax_radar.set_title("Urban Landscape Assessment", size=24, color="black",
                       fontweight="bold", pad=150)

    # ── Summary panel ─────────────────────────────────────────────────────────
    # ax_summary is a plain (non-polar) axes. We turn off all its normal
    # chart elements and use it purely as a canvas for text using ax.text().
    #
    # Coordinates use "axes fraction":
    #   (0, 0) = bottom-left corner of this axes
    #   (1, 1) = top-right corner
    # transform=ax_summary.transAxes tells matplotlib to use this system.

    ax_summary.set_facecolor("#ffffff")
    ax_summary.set_xlim(0, 1)
    ax_summary.set_ylim(0, 1)
    ax_summary.axis("off")      # hides ticks, labels, and border entirely

    # Panel title
    ax_summary.text(
        0.5, 0.97, "SCORE SUMMARY",
        ha="center", va="top",
        fontsize=11, fontweight="bold", color="#333333",
        transform=ax_summary.transAxes
    )

    # Thin rule under the title
    ax_summary.axhline(y=0.94, xmin=0.05, xmax=0.95,
                       color="#cccccc", linewidth=0.8)

    # ── Per-category blocks ───────────────────────────────────────────────────
    # y_cursor tracks our vertical position as we draw downward.
    # We subtract a small amount after each line to move down the panel.
    # This is a simple manual layout approach — no automatic text wrapping.

    y_cursor = 0.90

    for cat_name, cat_data in CATEGORIES.items():
        total, maximum, sub_scores = cat_totals[cat_name]
        color = cat_data["color"]

        # Category name header
        ax_summary.text(
            0.05, y_cursor, cat_name,
            ha="left", va="top",
            fontsize=8.5, fontweight="bold", color=color,
            transform=ax_summary.transAxes
        )
        y_cursor -= 0.04

        # Each subcategory row: label on left, bar + score on right
        for sub_label, score in zip(cat_data["subcategories"], sub_scores):
            filled = "█" * score
            empty  = "░" * (5 - score)

            ax_summary.text(
                0.05, y_cursor, sub_label,
                ha="left", va="top",
                fontsize=7, color="#444444",
                transform=ax_summary.transAxes
            )
            ax_summary.text(
                0.95, y_cursor, f"{filled}{empty}  {score}/5",
                ha="right", va="top",
                fontsize=7, color=color,
                fontfamily="monospace",
                transform=ax_summary.transAxes
            )
            y_cursor -= 0.038

        # Category total row
        ax_summary.text(
            0.05, y_cursor, "Total",
            ha="left", va="top",
            fontsize=8, fontweight="bold", color=color,
            transform=ax_summary.transAxes
        )
        ax_summary.text(
            0.95, y_cursor, f"{total} / {maximum}",
            ha="right", va="top",
            fontsize=8, fontweight="bold", color=color,
            transform=ax_summary.transAxes
        )
        y_cursor -= 0.03

        # Light divider between categories
        ax_summary.axhline(y=y_cursor + 0.005,
                           xmin=0.05, xmax=0.95,
                           color="#eeeeee", linewidth=0.8)
        y_cursor -= 0.025

    # ── Overall grand total ───────────────────────────────────────────────────
    ax_summary.axhline(y=y_cursor + 0.01,
                       xmin=0.05, xmax=0.95,
                       color="#aaaaaa", linewidth=1.2)
    y_cursor -= 0.02

    ax_summary.text(
        0.05, y_cursor, "OVERALL TOTAL",
        ha="left", va="top",
        fontsize=9, fontweight="bold", color="#333333",
        transform=ax_summary.transAxes
    )
    ax_summary.text(
        0.95, y_cursor, f"{grand_total} / {grand_max}",
        ha="right", va="top",
        fontsize=9, fontweight="bold", color="#333333",
        transform=ax_summary.transAxes
    )

    return fig
