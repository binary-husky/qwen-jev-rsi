"""Generic per-episode HP / boss / imbalance report for ZZZ rollouts.

Works for any number of versions (BASE / V1 / V2 / ...), any episode counts.

Input : <hud-dir>/<TAG>__<episode>.jsonl   (raw geometry from extract_hud_v5.py)
Output: <out>/plots/<TAG>_<episode>.png
        <out>/overview.png
        <out>/per_episode_metrics.json
        <out>/hp_metrics.csv
        <out>/selfcheck_selection.json
        <out>/selfcheck_stats.json

Rules (v4 pipeline, chief-approved 2026-10-30):
  * green = HP, yellow-green gradient = HP, red tail = damage trail (excluded)
  * standby bar: presence only, never a curve source; missing -> NaN
  * identity from front portrait brightness (not current_player)
  * 1.2 s switch settling discarded; monotone envelope per character
  * battle start = first run of 3 frames with boss HP >= 0.98
  * battle end = LAST frame with the front portrait (not min with boss bar)
  * boss bar disappearance is auxiliary only (recorded, not used for end)
"""
import argparse
import csv
import glob
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

plt.rcParams["font.family"] = ["Noto Serif CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

A_LEFT, A_FULL = 88, 115
BOSS_RIGHT = 570
IMB_RIGHT, IMB_DEN = 546, 166
SETTLE_S = 1.2

CHAR_COLORS = {"猫又": "#d64545", "照": "#e08a1b", "Boss": "#2f8f4e", "imb": "#c79a12"}
TAG_MAIN = {"BASE": "#3B6BB5", "V1": "#3A8B3A", "V2": "#D97706"}
TAG_PAL = {
    "BASE": ["#A9C4E4", "#7FA6D2", "#5A88C0", "#3B6BB5", "#2A4F86"],
    "V1": ["#A8D5A2", "#7FBF77", "#5AA54F", "#3A8B3A", "#2A6B2A"],
    "V2": ["#F6D08A", "#EFB55C", "#E89A33", "#D97706", "#A85A05"],
}
TAG_LABEL = {"BASE": "BASE 基线", "V1": "V1 新版", "V2": "V2 新版"}
FALLBACK = plt.get_cmap("tab10")


def palette(tag, n=5):
    if tag in TAG_PAL:
        return TAG_PAL[tag]
    base = FALLBACK(hash(tag) % 10)
    return [tuple(0.35 + 0.65 * (base[k] * (0.55 + 0.12 * i)) for k in range(3)) for i in range(n)]


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def identity(x):
    fb = x["front_bright"]
    if fb < 0.1 or fb > 0.95:
        return None
    if fb >= 0.65:
        return "照"
    if fb < 0.55:
        return "猫又"
    return None


def smooth_identity(ids):
    out = list(ids)
    n = len(out)
    i = 0
    while i < n:
        if out[i] is None:
            j = i
            while j < n and out[j] is None:
                j += 1
            if i > 0 and j < n and out[i - 1] == out[j] and (j - i) <= 2:
                for k in range(i, j):
                    out[k] = out[i - 1]
            i = j
        else:
            i += 1
    i = 0
    while i < n:
        j = i
        while j < n and out[j] == out[i]:
            j += 1
        if out[i] is not None and (j - i) < 3 and i > 0 and j < n and out[i - 1] == out[j]:
            for k in range(i, j):
                out[k] = out[i - 1]
        i = j
    return out


def switch_indices(ids):
    return [i for i in range(1, len(ids)) if ids[i] and ids[i - 1] and ids[i] != ids[i - 1]]


def in_settle(i, times, ids, switches):
    for s in reversed(switches):
        if s > i:
            continue
        if times[i] - times[s] > SETTLE_S:
            return False
        return ids[s] == ids[i]
    return False


def denoise(vals):
    v = np.array(vals, dtype=float)
    n = len(v)
    for i in range(n):
        if not np.isfinite(v[i]):
            continue
        win = [v[j] for j in range(max(0, i - 3), min(n, i + 4)) if j != i and np.isfinite(v[j])]
        if len(win) < 2:
            v[i] = np.nan
            continue
        if abs(v[i] - float(np.median(win))) > 0.15:
            v[i] = np.nan
    for i in range(n):
        if np.isfinite(v[i]) and v[i] < 0.05:
            lo, hi = max(0, i - 4), min(n, i + 5)
            nb = [v[j] for j in range(lo, hi) if j != i and np.isfinite(v[j])]
            if sum(1 for u in nb if u < 0.1) < 2:
                v[i] = np.nan
    return v


def fill_series(vals):
    out = np.full(len(vals), np.nan)
    last = np.nan
    for i, v in enumerate(vals):
        if np.isfinite(v):
            last = v
        out[i] = last
    return out


def monotone(v):
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isfinite(out[i]) and np.isfinite(out[i - 1]) and out[i] > out[i - 1]:
            out[i] = out[i - 1]
    return out


def process(path, tag, ep, end_rule="B", kill_grace=1.5):
    rows = load_jsonl(path)
    times = np.array([r["t_ms"] / 1000.0 for r in rows])
    ids = smooth_identity([identity(r) for r in rows])
    switches = switch_indices(ids)

    # ---- battle window ----
    boss_full_left = min([r["boss_left_px"] for r in rows if r["boss_left_px"]] or [381])
    boss_raw = np.array([
        np.nan if r["boss_left_px"] is None
        else (BOSS_RIGHT - r["boss_left_px"]) / (BOSS_RIGHT - boss_full_left)
        for r in rows
    ])
    start = next((i for i in range(len(rows) - 3)
                  if all(np.isfinite(boss_raw[i + k]) and boss_raw[i + k] >= 0.98 for k in range(3))), None)
    if start is None:
        start = next((i for i in range(len(rows)) if np.isfinite(boss_raw[i])), 0)

    front_present = [r["front_bright"] > 0.1 for r in rows]
    boss_idx = [i for i in range(len(rows)) if np.isfinite(boss_raw[i])]
    last_front = max([i for i in range(len(rows)) if front_present[i]] or [len(rows) - 1])
    last_boss = boss_idx[-1] if boss_idx else last_front
    boss_killed = np.isfinite(boss_raw[last_boss]) and boss_raw[last_boss] <= 0.06
    if end_rule == "B":
        if boss_killed:
            end = last_boss
            while end + 1 <= last_front and times[end + 1] - times[last_boss] <= kill_grace:
                end += 1
        else:
            end = last_front
    elif end_rule == "front":
        end = last_front
    else:
        end = last_boss if boss_killed else min(last_front, last_boss)

    # ---- character series ----
    chars, death, raws = {}, {}, {}
    for ch in ("猫又", "照"):
        vals = np.full(len(rows), np.nan)
        for i in range(start, end + 1):
            if ids[i] != ch or in_settle(i, times, ids, switches):
                continue
            if rows[i]["a_hp_px"] is not None:
                v = (rows[i]["a_hp_px"] - A_LEFT) / A_FULL
                if 0 <= v <= 1.05:
                    vals[i] = min(v, 1.0)
        last_read = max([i for i in range(start, end + 1) if np.isfinite(vals[i])] or [-1])
        if last_read >= 0 and last_read < end - 20:
            back = any(ids[i] == ch and rows[i]["a_hp_px"] is not None for i in range(last_read + 1, end + 1))
            standby = any(rows[i]["s_present"] and ids[i] and ids[i] != ch for i in range(last_read + 1, end + 1))
            if not back and not standby:
                death[ch] = last_read + 1
        vals = denoise(vals)
        raws[ch] = vals.copy()
        arr = monotone(fill_series(vals))
        fv = next((i for i in range(start, end + 1) if np.isfinite(arr[i])), None)
        if fv is not None and arr[fv] > 0.5:
            arr = np.clip(arr / arr[fv], 0, 1)
        if ch in death:
            arr[death[ch]:] = 0.0
        chars[ch] = arr

    # ---- boss series (truncate at its own last frame) ----
    boss_raw[:start] = np.nan
    b = monotone(np.clip(fill_series(boss_raw), 0, 1))
    if np.isfinite(b[start]) and b[start] > 0.5:
        b = np.clip(b / b[start], 0, 1)
    b[last_boss + 1:] = np.nan
    if boss_killed:
        b[last_boss] = 0.0

    # ---- imbalance ----
    imb = np.full(len(rows), np.nan)
    red = np.array([bool(r["imb_red"]) for r in rows])
    white = np.array([bool(r["imb_white"]) for r in rows])
    for i, r in enumerate(rows):
        near_red = red[max(0, i - 2): i + 3].any()
        if r["imb_left_px"] is not None and not near_red:
            imb[i] = min(1.0, max(0.0, (IMB_RIGHT - r["imb_left_px"]) / IMB_DEN))
        elif r["imb_red"]:
            imb[i] = 0.0
    finite = np.isfinite(imb)
    idx = np.flatnonzero(finite)
    for a, c in zip(idx, idx[1:]):
        if 1 < c - a <= 9 and np.all(~finite[a + 1:c]):
            for k in range(1, c - a):
                imb[a + k] = imb[a] + (imb[c] - imb[a]) * k / (c - a)

    # ---- metrics ----
    sl = slice(start, end + 1)
    m = {
        "tag": tag, "ep": ep,
        "start_s": round(float(times[start]), 1),
        "battle_end_abs_s": round(float(times[end]), 1),
        "front_last_s": round(float(times[last_front]), 1),
        "last_boss_s": round(float(times[last_boss]), 1),
        "tail_s": round(float(times[last_front] - times[last_boss]), 1),
        "end_s": round(float(times[end]), 1),
        "dur_s": round(float(times[end] - times[start]), 1),
        "boss_killed": bool(boss_killed),
        "boss_end": round(float(np.nanmin(b[sl])), 3) if np.isfinite(b[sl]).any() else None,
        "end_rule": end_rule,
    }
    dt_med = float(np.median(np.diff(times))) if len(times) > 1 else 0.24
    dt = np.clip(np.diff(times, prepend=times[0] - dt_med), 0.0, 0.5)
    for ch in ("猫又", "照"):
        a = chars[ch][sl]
        on = np.array([ids[i] == ch for i in range(start, end + 1)])
        m[f"{ch}_on_field_s"] = round(float(dt[start:end + 1][on].sum()), 1)
        if np.isfinite(a).any():
            m[f"{ch}_mean"] = round(float(np.nanmean(a)), 3)
            m[f"{ch}_mean_onfield"] = round(float(np.nanmean(a[on])), 3) if on.any() and np.isfinite(a[on]).any() else None
            m[f"{ch}_min"] = round(float(np.nanmin(a)), 3)
            m[f"{ch}_end"] = round(float(a[np.isfinite(a)][-1]), 3)
            m[f"{ch}_death_s"] = round(float(times[death[ch]]), 1) if ch in death else None
        else:
            for k in ("mean", "mean_onfield", "min", "end"):
                m[f"{ch}_{k}"] = None
            m[f"{ch}_death_s"] = None
    iv = imb[sl]
    m["imb_mean"] = round(float(np.nanmean(iv)), 3) if np.isfinite(iv).any() else None
    f90 = next((float(times[i]) for i in range(start, end + 1) if np.isfinite(imb[i]) and imb[i] >= 0.9), None)
    m["first_imb90_s"] = round(f90, 1) if f90 else None
    f50 = next((float(times[i]) for i in range(start, end + 1) if np.isfinite(imb[i]) and imb[i] >= 0.5), None)
    m["first_imb50_s"] = round(f50, 1) if f50 else None
    fr = next((float(times[i]) for i in range(start, end + 1) if red[i]), None)
    m["first_stun_s"] = round(fr, 1) if fr else None
    ri = [i for i in range(start, end + 1) if red[i]]
    wins, prev = 0, -999
    for i in ri:
        if times[i] - prev > 1.5:
            wins += 1
        prev = times[i]
    m["stun_windows"] = wins
    m["stun_s"] = round(float(red[sl].sum() * dt_med), 1)
    m["recovery_s"] = round(float(white[sl].sum() * dt_med), 1)
    return {"rows": rows, "times": times, "ids": ids, "chars": chars, "raws": raws,
            "boss": b, "imb": imb, "red": red, "white": white,
            "start": start, "end": end, "metrics": m}


def shade(ax, t, mask, color, alpha=0.25, merge_s=1.5):
    if not mask.any():
        return
    edges = np.flatnonzero(np.diff(np.r_[0, mask.astype(int), 0]))
    spans = []
    for a, b in zip(edges[::2], edges[1::2]):
        if spans and t[a] - spans[-1][1] <= merge_s:
            spans[-1][1] = t[min(b, len(t) - 1)]
        else:
            spans.append([t[a], t[min(b, len(t) - 1)]])
    for a, b in spans:
        ax.axvspan(a, b, color=color, alpha=alpha, lw=0)


def field_spans(d):
    out = {}
    t = d["times"]
    for ch in ("猫又", "照"):
        mask = np.zeros(len(t), dtype=bool)
        for i in range(d["start"], d["end"] + 1):
            mask[i] = d["ids"][i] == ch
        edges = np.flatnonzero(np.diff(np.r_[0, mask.astype(int), 0]))
        spans = []
        for a, b in zip(edges[::2], edges[1::2]):
            end_t = t[min(b, len(t) - 1)]
            if spans and t[a] - spans[-1][1] <= 0.6:
                spans[-1][1] = end_t
            else:
                spans.append([t[a], end_t])
        out[ch] = spans
    return out


def plot_episode(d, out_dir, tag):
    m = d["metrics"]
    origin = d["times"][d["start"]]
    t = d["times"] - origin
    sl = slice(d["start"], d["end"] + 1)
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(13.2, 7.4), sharex=True,
                                  gridspec_kw={"height_ratios": [2.5, 1.15]})
    for ch, col in (("猫又", CHAR_COLORS["猫又"]), ("照", CHAR_COLORS["照"])):
        for a, b in field_spans(d)[ch]:
            ax.axvspan(a - origin, b - origin, color=col, alpha=0.055, lw=0, zorder=0)
    shade(ax, t, d["red"], "#8a8a8a", 0.18)
    shade(ax, t, d["white"], "#7fb3d5", 0.18)
    for ch in ("猫又", "照"):
        ax.plot(t[sl], d["chars"][ch][sl], color=CHAR_COLORS[ch], lw=2.2, label=f"{ch} HP")
        if m.get(f"{ch}_death_s") is not None:
            ax.scatter([m[f"{ch}_death_s"] - origin], [0], marker="x", s=80, color=CHAR_COLORS[ch], zorder=5)
    ax.plot(t[sl], d["boss"][sl], color=CHAR_COLORS["Boss"], lw=2.2, label="Boss HP")
    ax.set_ylim(-0.03, 1.05)
    ax.set_ylabel("HP 比例（归一，单调不增）")
    ax.grid(alpha=0.25)
    h, l = ax.get_legend_handles_labels()
    h += [Patch(facecolor=CHAR_COLORS["猫又"], alpha=0.16, label="猫又 在场"),
          Patch(facecolor=CHAR_COLORS["照"], alpha=0.16, label="照 在场")]
    l += ["猫又 在场", "照 在场"]
    ax.legend(h, l, loc="lower left", fontsize=8.5, ncol=3)
    ax.set_title(f"{TAG_LABEL.get(tag, tag)}  {m['ep']}", fontsize=13)
    shade(ax2, t, d["red"], "#8a8a8a", 0.25)
    shade(ax2, t, d["white"], "#7fb3d5", 0.25)
    ax2.plot(t[sl], d["imb"][sl], color=CHAR_COLORS["imb"], lw=1.8, label="Boss 失衡值")
    ax2.set_ylim(-0.03, 1.06)
    ax2.set_ylabel("失衡值")
    ax2.set_xlabel("Boss 血条满值后的秒数（每局独立对齐 0）")
    ax2.grid(alpha=0.25)
    ax2.legend(loc="upper left", fontsize=9)
    txt = (f"战斗窗 {m['dur_s']:.0f}s   猫又均值 {m['猫又_mean']} 末 {m['猫又_end']}   "
           f"照均值 {m['照_mean']} 末 {m['照_end']}\n"
           f"Boss 末 {m['boss_end']} ({'击杀' if m['boss_killed'] else '存活'})   "
           f"失衡均值 {m['imb_mean']}   首次满失衡 {m['first_imb90_s']}s   眩晕 {m['stun_s']:.0f}s")
    ax.text(0.995, 0.015, txt, transform=ax.transAxes, fontsize=9, va="bottom", ha="right",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#cccccc", alpha=0.9))
    fig.tight_layout()
    fn = os.path.join(out_dir, "plots", f"{tag}_{m['ep']}.png")
    fig.savefig(fn, dpi=130)
    plt.close(fig)
    return fn


def plot_overview(data, out_dir):
    tags = sorted({d["metrics"]["tag"] for d in data})
    fig = plt.figure(figsize=(14.2, 7.4))
    gs = fig.add_gridspec(2, 1, height_ratios=[4.4, 1.25], hspace=0.10)
    ax = fig.add_subplot(gs[0, 0])
    strip = fig.add_subplot(gs[1, 0], sharex=ax)
    ls_cycle = ["-", (0, (4, 2)), (0, (1.5, 1.5))]
    for ti, tag in enumerate(tags):
        pal = palette(tag)
        eps = sorted([d for d in data if d["metrics"]["tag"] == tag], key=lambda d: d["metrics"]["ep"])
        for k, d in enumerate(eps):
            m = d["metrics"]
            t = d["times"] - d["times"][d["start"]]
            c = pal[k % len(pal)]
            ax.plot(t, d["boss"], color=c, lw=1.8, ls=ls_cycle[ti % 3], alpha=0.95,
                    label=f"{TAG_LABEL.get(tag, tag)} ep{k+1}")
            if m["boss_killed"]:
                ax.plot([m["battle_end_abs_s"] - m["start_s"]], [0], marker="x", ms=6, mew=1.6, color=c, ls="none")
            else:
                y = d["boss"][d["end"]]
                ax.plot([m["dur_s"]], [y], marker="o", ms=6, mfc="white", mec=c, mew=1.5, ls="none")
        row = len(tags) - 1 - ti
        strip.hlines(row, 0, 300, color="#e6e6e6", lw=3)
        for d in eps:
            m = d["metrics"]
            if m["boss_killed"]:
                strip.plot([m["battle_end_abs_s"] - m["start_s"]], [row], marker="o", ms=7, color=TAG_MAIN.get(tag, "gray"), ls="none")
            else:
                strip.plot([300], [row], marker="o", ms=7, mfc="white", mec=TAG_MAIN.get(tag, "gray"),
                           mew=1.5, ls="none")
        nkill = sum(1 for d in eps if d["metrics"]["boss_killed"])
        strip.text(305, row, f"{nkill}/{len(eps)}", va="center", fontsize=9,
                   color=TAG_MAIN.get(tag, "gray"), fontweight="bold")
        strip.text(-3, row, TAG_LABEL.get(tag, tag), va="center", ha="right", fontsize=9)
    ax.set_xlim(0, 305)
    ax.set_ylim(-0.03, 1.05)
    ax.set_ylabel("Boss HP 比例（每局首值归一）")
    ax.grid(alpha=0.22)
    ax.legend(loc="upper right", fontsize=8, ncol=2, framealpha=0.9)
    ax.set_title("Boss HP 逐局总览（每局一条线，不做跨局平均）", fontsize=14)
    strip.set_xlim(0, 320)
    strip.set_ylim(-0.6, len(tags) - 0.4)
    strip.set_yticks([])
    strip.grid(axis="x", alpha=0.2)
    strip.set_xlabel("Boss 血条满值后的秒数")
    for s in ("top", "right", "left"):
        strip.spines[s].set_visible(False)
    fn = os.path.join(out_dir, "overview.png")
    fig.savefig(fn, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hud-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tags", default="", help="optional comma list; default auto from filenames")
    ap.add_argument("--end-rule", default="B", choices=["B", "front", "min"])
    ap.add_argument("--kill-grace", type=float, default=1.5, help="extra seconds after boss last frame for killed episodes (capped at front last)")
    args = ap.parse_args()
    os.makedirs(os.path.join(args.out, "plots"), exist_ok=True)
    files = sorted(glob.glob(os.path.join(args.hud_dir, "*.jsonl")))
    wanted = [t.strip() for t in args.tags.split(",") if t.strip()]
    data = []
    for p in files:
        base = os.path.basename(p)[:-6]
        if "__" not in base:
            continue
        tag, ep = base.split("__", 1)
        if wanted and tag not in wanted:
            continue
        d = process(p, tag, ep, args.end_rule, args.kill_grace)
        d["metrics"]["png"] = plot_episode(d, args.out, tag)
        data.append(d)
        print(f"{tag} {ep}: battle_end_abs={d['metrics']['battle_end_abs_s']} last_boss={d['metrics']['last_boss_s']} "
              f"front_last={d['metrics']['front_last_s']} killed={d['metrics']['boss_killed']} tail={d['metrics']['tail_s']}")
    overview = plot_overview(data, args.out)
    metrics = [d["metrics"] for d in data]
    json.dump(metrics, open(os.path.join(args.out, "per_episode_metrics.json"), "w"),
              ensure_ascii=False, indent=1)
    keys = ["tag", "ep", "start_s", "battle_end_abs_s", "front_last_s", "last_boss_s", "tail_s", "dur_s",
            "boss_killed", "boss_end", "猫又_mean", "猫又_mean_onfield", "猫又_end", "猫又_min",
            "猫又_on_field_s", "猫又_death_s", "照_mean", "照_mean_onfield", "照_end", "照_min",
            "照_on_field_s", "照_death_s", "imb_mean", "first_imb50_s", "first_imb90_s",
            "first_stun_s", "stun_windows", "stun_s", "recovery_s", "end_rule"]
    disp = {"dur_s": "dur_s (from battle start)"}
    headers = [disp.get(k, k) for k in keys]
    with open(os.path.join(args.out, "hp_metrics.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for m in metrics:
            w.writerow([m.get(k) for k in keys])
    # self-check stats
    first_ok = mono_ok = n_curves = rises = near = 0
    deaths = []
    for d in data:
        ids = d["ids"]
        sw = [d["times"][i] for i in range(1, len(ids)) if ids[i] and ids[i - 1] and ids[i] != ids[i - 1]]
        for ch in ("猫又", "照"):
            a = d["chars"][ch][d["start"]:d["end"] + 1]
            fin = a[np.isfinite(a)]
            n_curves += 1
            first_ok += bool(abs(float(fin[0]) - 1.0) <= 1e-6)
            mono_ok += bool(np.all(np.diff(fin) <= 1e-9))
            raw = d["raws"][ch]
            for i in range(1, len(raw)):
                if np.isfinite(raw[i]) and np.isfinite(raw[i - 1]) and raw[i] - raw[i - 1] > 0.02:
                    rises += 1
                    if min([abs(d["times"][i] - s) for s in sw] or [99]) <= 3.0:
                        near += 1
            if d["metrics"].get(f"{ch}_death_s") is not None:
                deaths.append({"tag": d["metrics"]["tag"], "ep": d["metrics"]["ep"],
                               "char": ch, "death_s": d["metrics"][f"{ch}_death_s"]})
    stats = {"first_ok": int(first_ok), "curves": int(n_curves), "monotone_ok": int(mono_ok),
             "raw_rises_gt_0.02": int(rises), "rises_within_3s_of_switch": int(near), "deaths": deaths}
    json.dump(stats, open(os.path.join(args.out, "selfcheck_stats.json"), "w"), ensure_ascii=False, indent=1)
    # self-check selection
    sel = []
    for d in data:
        m = d["metrics"]
        for ch in ("猫又", "照"):
            arr = d["chars"][ch]
            picks = []
            for i in range(d["start"] + 3, d["end"] + 1):
                if d["ids"][i] != ch or not np.isfinite(arr[i]) or not np.isfinite(arr[i - 1]):
                    continue
                if in_settle(i, d["times"], d["ids"], switch_indices(d["ids"])):
                    continue
                if not np.isfinite(d["raws"][ch][i]) or abs(d["raws"][ch][i] - arr[i]) > 0.02:
                    continue
                picks.append({"tag": m["tag"], "ep": m["ep"], "image": d["rows"][i]["image"],
                              "t_s": round(float(d["times"][i]), 1), "char": ch,
                              "hp": round(float(arr[i]), 3), "raw": round(float(d["raws"][ch][i]), 3),
                              "drop": round(float(arr[i - 1] - arr[i]), 3), "px": d["rows"][i]["a_hp_px"]})
            picks.sort(key=lambda x: -x["drop"])
            chosen = []
            for cand in picks:
                if all(abs(cand["t_s"] - c["t_s"]) >= 3.0 for c in chosen):
                    chosen.append(cand)
                if len(chosen) >= 6:
                    break
            sel.extend(chosen)
    json.dump(sel, open(os.path.join(args.out, "selfcheck_selection.json"), "w"), ensure_ascii=False, indent=1)
    print("WROTE", os.path.join(args.out, "overview.png"), "picks", len(sel))


if __name__ == "__main__":
    main()
