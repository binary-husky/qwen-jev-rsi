"""Fifteen-episode boss-HP overview, seaborn styling, English labels.

Same layout as the original overview: 15 lines (one per episode), per-arm
light-to-dark shades, solid/dashed/dotted by arm, and the three-row
kill / alive-at-cap strip underneath. Nothing is averaged across episodes.

Outputs: boss15_overview.png / .pdf / .svg

Usage:
  python3 plot_boss15.py --hud-dir <dir> --out <dir>
"""
import argparse
import glob
import importlib.util
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hp", os.path.join(HERE, "build_hp_report.py"))
hp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hp)

ARMS = ["BASE", "V1", "V2"]
BASE_COLOR = {"BASE": "#2a78d6", "V1": "#1baf7a", "V2": "#eb6834"}
LABEL = {"BASE": "zzz-rsi-base", "V1": "zzz-rsi-v1", "V2": "zzz-rsi-v2"}
LS = {"BASE": "-", "V1": (0, (4, 2)), "V2": (0, (1.5, 1.5))}

sns.set_theme(
    context="paper",
    style="whitegrid",
    font="DejaVu Sans",
    rc={
        "figure.facecolor": "#fcfcfb",
        "axes.facecolor": "#fcfcfb",
        "savefig.facecolor": "#fcfcfb",
        "axes.edgecolor": "#b9b7ae",
        "grid.color": "#e8e7e2",
        "axes.labelcolor": "#52514e",
        "text.color": "#0b0b0b",
        "xtick.color": "#52514e",
        "ytick.color": "#52514e",
    },
)


def load(hud_dir):
    eps = []
    for p in sorted(glob.glob(os.path.join(hud_dir, "*.jsonl"))):
        base = os.path.basename(p)[:-6]
        if "__" not in base:
            continue
        tag, ep = base.split("__", 1)
        if tag not in ARMS:
            continue
        eps.append((tag, ep, hp.process(p, tag, ep, "B", 1.5)))
    return eps


def shades(arm, n):
    """Light-to-dark steps of the arm colour (seaborn ramp), n per arm."""
    return sns.light_palette(BASE_COLOR[arm], n_colors=n + 2)[1:-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hud-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    eps = load(args.hud_dir)

    fig = plt.figure(figsize=(13.0, 7.2), dpi=170)
    gs = fig.add_gridspec(2, 1, height_ratios=[4.4, 1.25], hspace=0.10)
    ax = fig.add_subplot(gs[0, 0])
    strip = fig.add_subplot(gs[1, 0], sharex=ax)

    for ti, arm in enumerate(ARMS):
        sel = sorted([e for e in eps if e[0] == arm], key=lambda e: e[1])
        c = BASE_COLOR[arm]
        for k, (_, ep, d) in enumerate(sel):
            m = d["metrics"]
            t = d["times"] - d["times"][d["start"]]
            ax.plot(t, d["boss"], color=c, lw=1.8, ls=LS[arm], alpha=0.9,
                    label=f"{LABEL[arm]}" if k == 0 else "_nolegend_")
            if m["boss_killed"]:
                ax.plot([m["battle_end_abs_s"] - m["start_s"]], [0], marker="x",
                        ms=6, mew=1.6, color=c, ls="none")
            else:
                ax.plot([m["dur_s"]], [d["boss"][d["end"]], ], marker="o", ms=6,
                        mfc="white", mec=c, mew=1.5, ls="none")

        row = len(ARMS) - 1 - ti
        strip.hlines(row, 0, 300, color="#ecebe6", lw=3)
        for _, _, d in sel:
            m = d["metrics"]
            if m["boss_killed"]:
                strip.plot([m["battle_end_abs_s"] - m["start_s"]], [row], marker="o",
                           ms=7, color=BASE_COLOR[arm], ls="none")
            else:
                strip.plot([m["dur_s"]], [row], marker="o", ms=7, mfc="white",
                           mec=BASE_COLOR[arm], mew=1.5, ls="none")
        nkill = sum(1 for _, _, d in sel if d["metrics"]["boss_killed"])
        strip.text(305, row, f"{nkill}/{len(sel)}", va="center", fontsize=9,
                   color=BASE_COLOR[arm], fontweight="bold")
        strip.text(-3, row, LABEL[arm], va="center", ha="right", fontsize=9)

    ax.set_xlim(0, 305)
    ax.set_ylim(-0.03, 1.05)
    ax.set_ylabel("Boss HP (normalised per episode)")
    # no title (removed on request)
    ax.legend(loc="upper right", fontsize=9, ncol=1, frameon=True,
              framealpha=0.9, edgecolor="#e4e3de", handlelength=2.4)
    ax.set_yticks([i / 5 for i in range(6)])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    strip.set_xlim(0, 320)
    strip.set_ylim(-0.6, len(ARMS) - 0.4)
    strip.set_yticks([])
    strip.set_xlabel("Time since detected battle start (seconds)")
    for s in ("top", "right", "left"):
        strip.spines[s].set_visible(False)
    strip.tick_params(length=0)

    fig.subplots_adjust(left=0.13, right=0.965, top=0.93, bottom=0.09)
    p = os.path.join(args.out, "boss15_overview.png")
    fig.savefig(p, bbox_inches="tight")
    fig.savefig(p.replace(".png", ".pdf"), bbox_inches="tight")
    fig.savefig(p.replace(".png", ".svg"), bbox_inches="tight")
    plt.close(fig)
    print("WROTE", p)


if __name__ == "__main__":
    main()
