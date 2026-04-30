# chart.py
# ─────────────────────────────────────────────────────────────────────────────
# Responsible for ONE thing: taking a scores dictionary and returning a
# matplotlib figure. No Streamlit code lives here at all.
#
# Layout:
#   ROW 0 (height ratio 1): summary panel — 3 columns, one per category
#   ROW 1 (height ratio 3): radar chart centered
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from data import CATEGORIES


def build_radar_figure(scores_dict):
    """
    Build and return the TROLL radar chart as a matplotlib Figure.

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

    # ── Pre-calculate category totals ─────────────────────────────────────────
    cat_totals  = {}
    grand_total = 0
    grand_max   = 0

    for cat_name, cat_data in CATEGORIES.items():
        sub_scores = [scores_dict[k] for k in cat_data["keys"]]
        total      = sum(sub_scores)
        maximum    = len(sub_scores) * 5
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

    # ── Smooth curve ──────────────────────────────────────────────────────────
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
    # Two rows, one column:
    #   row 0 (height ratio 1): summary panel
    #   row 1 (height ratio 3): radar chart
    #
    # height_ratios=[1, 3] gives the radar 3x the vertical space.
    # hspace controls the vertical gap between the two rows.

    fig = plt.figure(figsize=(13, 16))
    fig.patch.set_facecolor("#ffffff")

    outer_gs = gridspec.GridSpec(
        nrows=2, ncols=1,
        height_ratios=[1, 1],
        figure=fig,
        hspace=0.75
    )

    # ── Summary row: 3 side-by-side columns ──────────────────────────────────
    # We nest a second GridSpec inside row 0 to get 3 equal columns.
    # This is called a "nested GridSpec" — it lets you have different
    # grid structures in different parts of the same figure.

    summary_gs = gridspec.GridSpecFromSubplotSpec(
        nrows=1, ncols=3,
        subplot_spec=outer_gs[0],
        wspace=0.05
    )

    cat_names = list(CATEGORIES.keys())

    for col_idx, cat_name in enumerate(cat_names):
        cat_data           = CATEGORIES[cat_name]
        color              = cat_data["color"]
        total, maximum, sub_scores = cat_totals[cat_name]

        ax_col = fig.add_subplot(summary_gs[0, col_idx])
        ax_col.set_facecolor("#ffffff")
        ax_col.set_xlim(0, 1)
        ax_col.set_ylim(0, 1)
        ax_col.axis("off")

        # Light border around each column using a Rectangle patch
        # This visually separates the three category panels
        import matplotlib.patches as mpatches
        border = mpatches.FancyBboxPatch(
            (0.02, 0.02), 0.96, 0.96,
            boxstyle="round,pad=0.01",
            linewidth=1, edgecolor="#eeeeee",
            facecolor="#ffffff",
            transform=ax_col.transAxes, zorder=0
        )
        ax_col.add_patch(border)

        # Category name header
        ax_col.text(
            0.5, 0.95, cat_name,
            ha="center", va="top",
            fontsize=9, fontweight="bold", color=color,
            transform=ax_col.transAxes
        )

        # Thin rule under header
        ax_col.axhline(y=0.89, xmin=0.05, xmax=0.95,
                       color=color, linewidth=1.0, alpha=0.3)

        # Subcategory rows
        # We have ~8 items (6 subs + total + gap) to fit between y=0.87 and y=0.08
        # That's 0.79 of axes height divided by 8 = ~0.099 per row
        y_cursor = 0.86
        row_h    = 0.093

        for sub_label, score in zip(cat_data["subcategories"], sub_scores):
            filled = "█" * score
            empty  = "░" * (5 - score)

            # Subcategory label
            ax_col.text(
                0.06, y_cursor, sub_label,
                ha="left", va="top",
                fontsize=7.5, color="#000000",
                transform=ax_col.transAxes
            )
            # Score bar + number
            ax_col.text(
                0.94, y_cursor, f"{filled}{empty} {score}/5",
                ha="right", va="top",
                fontsize=7.5, color=color,
                fontfamily="monospace",
                transform=ax_col.transAxes
            )
            y_cursor -= row_h

        # Divider above total
        ax_col.axhline(y=y_cursor + 0.04, xmin=0.05, xmax=0.95,
                       color=color, linewidth=0.8, alpha=0.3)

        # Category total
        ax_col.text(
            0.06, y_cursor, "TOTAL",
            ha="left", va="top",
            fontsize=8.5, fontweight="bold", color=color,
            transform=ax_col.transAxes
        )
        ax_col.text(
            0.94, y_cursor, f"{total} / {maximum}",
            ha="right", va="top",
            fontsize=8.5, fontweight="bold", color=color,
            transform=ax_col.transAxes
        )

    # Overall total — placed just below the three columns using fig.text()
    # We use figure coordinates (0-1 across the whole figure) rather than
    # axes coordinates since this text spans all three columns.
    fig.text(
        0.5, 0.665,
        f"OVERALL TOTAL:  {grand_total} / {grand_max}",
        ha="center", va="top",
        fontsize=10, fontweight="bold", color="#333333"
    )

    # ── Radar axes ────────────────────────────────────────────────────────────
    ax_radar = fig.add_subplot(outer_gs[1], projection="polar")
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
    fig.text(0.78, 0.63, "WATER CONSERVATION",
             ha="center", va="center", fontsize=13, fontweight="bold",
             color=CATEGORIES["WATER CONSERVATION"]["color"])
    fig.text(0.5,  0.03, "ECOSYSTEM SERVICES",
             ha="center", va="center", fontsize=13, fontweight="bold",
             color=CATEGORIES["ECOSYSTEM SERVICES"]["color"])
    fig.text(0.22, 0.63, "DESIGN AND MANAGEMENT",
             ha="center", va="center", fontsize=13, fontweight="bold",
             color=CATEGORIES["DESIGN AND MANAGEMENT"]["color"])


    return fig
