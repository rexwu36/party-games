"""Write PLAYLISTS / BANK_X into song.html from playlists_src.py + measured data.

data.json: {"<display name>": [videoId, introStartSec, chorusSec|null], ...}
The first playlist (華語經典 30) is read from the CLASSIC block below.
"""
import json, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playlists_src import PLAYLISTS, EXTRA_BANK, CHORUS_LIST
from new_lists import NEW_LISTS, MOVIE_BANK
EXTRA_BANK = dict(EXTRA_BANK, movie=MOVIE_BANK)

ROOT = pathlib.Path(__file__).parent.parent
data = json.loads((ROOT / "tools" / "data.json").read_text(encoding="utf-8"))
data.update(json.loads((ROOT / "tools" / "chorus_data.json").read_text(encoding="utf-8")))
data.update(json.loads((ROOT / "tools" / "data_new.json").read_text(encoding="utf-8")))
classic = json.loads((ROOT / "tools" / "classic.json").read_text(encoding="utf-8"))  # [[name, year, id, start], ...]

def ts(x): return f"{int(x)//60}:{int(x)%60:02d}"

def line(name, year, vid, start, chorus, tag="副"):
    s = f"{name} [{year}] https://www.youtube.com/watch?v={vid} {ts(start)}"
    if chorus is not None: s += f" {tag}{ts(chorus)}"
    return s

HEAD = ("# 一行一首：歌名　[發行年份]　YouTube 網址　開始時間　副歌時間\n"
        "# 開始時間已設在 MV 開頭聲音出現的地方（保留前奏、跳過空白）\n")

lists = []
classic_lines = [line(n, y, v, st, None) for n, y, v, st in classic]
lists.append({"name": "華語經典 30", "tag": "zh", "mode": "intro", "text": HEAD + "\n".join(classic_lines)})
missing = []
for title, tag, songs in PLAYLISTS:
    rows = []
    for n, y, _q in songs:
        d = data.get(n)
        if not d or not d[0]:
            missing.append(n); continue
        rows.append(line(n, y, d[0], d[1] or 0, d[2]))
    lists.append({"name": title, "tag": tag, "mode": "intro", "text": HEAD + "\n".join(rows)})
ct, ctag, csongs = CHORUS_LIST
crow = []
for n, y in csongs:
    d = data.get(n)
    if not d or not d[0]:
        missing.append(n); continue
    crow.append(line(n, y, d[0], d[1] or 0, d[2], "難"))
lists.append({"name": ct, "tag": ctag, "mode": "hard", "text": HEAD + "\n".join(crow)})
# 30-song lists added later go after the hard list so saved list indexes stay valid.
for title, tag, songs in NEW_LISTS:
    rows = []
    for n, y, _q in songs:
        d = data.get(n)
        if not d or not d[0]:
            missing.append(n); continue
        rows.append(line(n, y, d[0], d[1] or 0, None))
    lists.append({"name": title, "tag": tag, "mode": "intro", "text": HEAD + "\n".join(rows)})

js = "const PLAYLISTS=" + json.dumps(lists, ensure_ascii=False, indent=0) + ";\n"
js += "const SAMPLE=PLAYLISTS[0].text;\n"
js += "const BANK_X=" + json.dumps({k: [[n, y] for n, y in v] for k, v in EXTRA_BANK.items()}, ensure_ascii=False, separators=(",", ":")) + ";\n"

p = ROOT / "song.html"
s = p.read_text(encoding="utf-8")
start_marks = ["const SAMPLE=`", "const PLAYLISTS="]
a = min(i for i in (s.find(m) for m in start_marks) if i >= 0)
if s[a:].startswith("const SAMPLE=`"):
    b = s.index("`;", a) + 3
else:
    b = s.index("const BANK_X=", a); b = s.index("\n", b) + 1
s = s[:a] + js + s[b:]
p.write_text(s, encoding="utf-8")
print("lists:", [(l["name"], l["text"].count("\n") - 1) for l in lists])
print("missing:", missing)
