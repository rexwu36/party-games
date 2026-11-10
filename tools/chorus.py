"""Pick a chorus start for each song from a loudness profile + YouTube "most replayed" heatmap.

loud.json : {name: {"prof": [dB per second, 0..130]}}
heat.json : {name: {"len": seconds, "mk": [[sec, intensity], ...]}}
Prints {name: chorus_sec} as JSON.

Rule: the first chorus is usually the first sustained section that is clearly louder
than the verse before it. Find the first second t in [25, 120] where the 4 s mean
loudness is >= 3 dB above the median of the 20 s before it and stays there for 6 s.
If a heatmap local peak (>= 85 % of the window max) lies within 10 s, snap to it.
Without a loudness hit, fall back to the first strong heatmap peak in 15-60 % of the song.
"""
import json, statistics, sys, pathlib

here = pathlib.Path(__file__).parent
loud = json.loads((here / "loud.json").read_text(encoding="utf-8"))
heat = json.loads((here / "heat.json").read_text(encoding="utf-8"))

def smooth(p, w=4):
    out = []
    for i in range(len(p)):
        seg = [x for x in p[max(0, i - w // 2): i + w // 2] if x is not None and x > -90]
        out.append(sum(seg) / len(seg) if seg else None)
    return out

def heat_peaks(h):
    mk = h.get("mk") or []
    L = h.get("len") or 0
    win = [m for m in mk if L * 0.12 < m[0] < L * 0.6]
    if not win:
        return []
    mx = max(m[1] for m in win)
    return [m[0] for i, m in enumerate(win)
            if m[1] >= 0.85 * mx and (i == 0 or m[1] >= win[i - 1][1]) and (i == len(win) - 1 or m[1] >= win[i + 1][1])]

res = {}
for name in set(loud) | set(heat):
    prof = (loud.get(name) or {}).get("prof") or []
    sm = smooth(prof)
    hit = None
    for t in range(25, min(121, len(sm) - 6)):
        prev = [x for x in sm[t - 20:t] if x is not None]
        if len(prev) < 10 or sm[t] is None:
            continue
        base = statistics.median(prev)
        if all(sm[t + k] is not None and sm[t + k] >= base + 3 for k in range(6)):
            hit = t
            break
    peaks = heat_peaks(heat.get(name) or {})
    if hit is not None:
        near = [p for p in peaks if abs(p - hit) <= 10]
        c = min(near, key=lambda p: abs(p - hit)) if near else hit
    elif peaks:
        c = peaks[0]
    else:
        c = None
    res[name] = None if c is None else max(0, int(c) - 1)
print(json.dumps(res, ensure_ascii=False, indent=0))
