"""Find the first chorus of each song from LRCLIB time-synced lyrics.

The chorus is the block of lyric lines that repeats most often; its first
occurrence is the first chorus. Writes lyrics_chorus.json:
{name: {"t": chorus_sec_in_audio, "dur": audio_duration, "line": first chorus line}}
"""
import json, re, time, urllib.request, urllib.parse, pathlib

here = pathlib.Path(__file__).parent
# name, (trad title, trad artist), (simp title, simp artist), MV length (s)
SONGS = [
 ("周華健〈朋友〉", ("朋友","周華健"), ("朋友","周华健"), 279),
 ("張信哲〈愛如潮水〉", ("愛如潮水","張信哲"), ("爱如潮水","张信哲"), 271),
 ("任賢齊〈對面的女孩看過來〉", ("對面的女孩看過來","任賢齊"), ("对面的女孩看过来","任贤齐"), 194),
 ("張宇〈月亮惹的禍〉", ("月亮惹的禍","張宇"), ("月亮惹的祸","张宇"), 259),
 ("動力火車〈當〉", ("當","動力火車"), ("当","动力火车"), 295),
 ("五月天〈擁抱〉", ("擁抱","五月天"), ("拥抱","五月天"), 257),
 ("張震嶽〈愛我別走〉", ("愛我別走","張震嶽"), ("爱我别走","张震岳"), 282),
 ("張韶涵〈歐若拉〉", ("歐若拉","張韶涵"), ("欧若拉","张韶涵"), 260),
 ("孫燕姿〈綠光〉", ("綠光","孫燕姿"), ("绿光","孙燕姿"), 191),
 ("王力宏〈唯一〉", ("唯一","王力宏"), ("唯一","王力宏"), 261),
 ("陳奕迅〈愛情轉移〉", ("愛情轉移","陳奕迅"), ("爱情转移","陈奕迅"), 0),
 ("信樂團〈死了都要愛〉", ("死了都要愛","信樂團"), ("死了都要爱","信乐团"), 276),
 ("孫燕姿〈遇見〉", ("遇見","孫燕姿"), ("遇见","孙燕姿"), 207),
 ("蔡依林〈說愛你〉", ("說愛你","蔡依林"), ("说爱你","蔡依林"), 228),
 ("范瑋琪〈最初的夢想〉", ("最初的夢想","范瑋琪"), ("最初的梦想","范玮琪"), 295),
 ("陳奕迅〈十年〉", ("十年","陳奕迅"), ("十年","陈奕迅"), 204),
 ("伍佰〈突然的自我〉", ("突然的自我","伍佰"), ("突然的自我","伍佰"), 217),
 ("梁靜茹〈寧夏〉", ("寧夏","梁靜茹"), ("宁夏","梁静茹"), 381),
 ("五月天〈知足〉", ("知足","五月天"), ("知足","五月天"), 271),
 ("梁靜茹〈可惜不是你〉", ("可惜不是你","梁靜茹"), ("可惜不是你","梁静茹"), 288),
 ("S.H.E〈不想長大〉", ("不想長大","S.H.E"), ("不想长大","S.H.E"), 269),
 ("林俊傑〈一千年以後〉", ("一千年以後","林俊傑"), ("一千年以后","林俊杰"), 279),
 ("蔡依林〈舞孃〉", ("舞孃","蔡依林"), ("舞娘","蔡依林"), 222),
 ("陳奕迅〈好久不見〉", ("好久不見","陳奕迅"), ("好久不见","陈奕迅"), 251),
 ("S.H.E〈中國話〉", ("中國話","S.H.E"), ("中国话","S.H.E"), 227),
 ("林俊傑〈小酒窩〉", ("小酒窩","林俊傑"), ("小酒窝","林俊杰"), 239),
 ("林宥嘉〈說謊〉", ("說謊","林宥嘉"), ("说谎","林宥嘉"), 284),
 ("田馥甄〈你就不要想起我〉", ("你就不要想起我","田馥甄"), ("你就不要想起我","田馥甄"), 317),
 ("張棟樑〈當你孤單你會想起誰〉", ("當你孤單你會想起誰","張棟樑"), ("当你孤单你会想起谁","张栋梁"), 0),
 ("林俊傑〈修煉愛情〉", ("修煉愛情","林俊傑"), ("修炼爱情","林俊杰"), 354),
]

def search(t, a):
    url = "https://lrclib.net/api/search?" + urllib.parse.urlencode({"track_name": t, "artist_name": a})
    req = urllib.request.Request(url, headers={"User-Agent": "party-games-song-quiz/1.0"})
    for _ in range(3):
        try:
            return json.load(urllib.request.urlopen(req, timeout=25))
        except Exception:
            time.sleep(2)
    return []

CREDIT = re.compile(r"(作詞|作词|作曲|編曲|编曲|監製|监制|製作|制作|詞：|词：|曲：|Lyrics|Composer|Producer|OP:|SP:|和聲|和声|混音|吉他|貝斯|鼓：)")
def parse(lrc):
    out = []
    for ln in lrc.splitlines():
        ms = re.findall(r"\[(\d+):(\d+(?:\.\d+)?)\]", ln)
        txt = re.sub(r"\[[^\]]*\]", "", ln).strip()
        if not ms or not txt or CREDIT.search(txt):
            continue
        key = re.sub(r"[\s，,。.!！?？、~～…\-—()（）\"“”'‘’：:]", "", txt).lower()
        if len(key) < 2:
            continue
        for m, s in ms:
            out.append((int(m) * 60 + float(s), key, txt))
    out.sort()
    return out

def first_chorus(lines):
    n = len(lines)
    pairs = {}
    for i in range(n - 1):
        pairs.setdefault((lines[i][1], lines[i + 1][1]), []).append(i)
    best = None
    for idx in pairs.values():
        if len(idx) < 2:
            continue
        cand = (len(idx), -idx[0])
        if best is None or cand > best[0]:
            best = (cand, idx[0])
    if best is None:
        return None
    i = best[1]
    # walk back while the previous line is also part of a repeated block
    while i > 0 and len(pairs.get((lines[i - 1][1], lines[i][1]), [])) >= 2 and lines[i][0] - lines[i - 1][0] < 12:
        i -= 1
    return i


KEY = {
 "周華健〈朋友〉":["朋友一生一起走"], "張信哲〈愛如潮水〉":["我的愛如潮水","我的爱如潮水"],
 "任賢齊〈對面的女孩看過來〉":["對面的女孩看過來","对面的女孩看过来"], "張宇〈月亮惹的禍〉":["月亮惹的禍","月亮惹的祸"],
 "動力火車〈當〉":["讓我們紅塵作伴","让我们红尘作伴"], "五月天〈擁抱〉":["昨天太近"],
 "張震嶽〈愛我別走〉":["愛我別走","爱我别走"], "張韶涵〈歐若拉〉":["歐若拉","欧若拉"],
 "孫燕姿〈綠光〉":["期待著一個幸運","期待着一个幸运"], "王力宏〈唯一〉":["你就是我的唯一"],
 "陳奕迅〈愛情轉移〉":["轉移到另一個","转移到另一个"], "信樂團〈死了都要愛〉":["死了都要愛","死了都要爱"],
 "孫燕姿〈遇見〉":["我遇見誰","我遇见谁"], "蔡依林〈說愛你〉":["說愛你","说爱你"],
 "范瑋琪〈最初的夢想〉":["最初的夢想","最初的梦想"], "陳奕迅〈十年〉":["十年之前"],
 "伍佰〈突然的自我〉":["跟我一起走","手牽手","手牵手"], "梁靜茹〈寧夏〉":["寧靜的夏天","宁静的夏天"],
 "五月天〈知足〉":["一道彩虹"], "梁靜茹〈可惜不是你〉":["可惜不是你"],
 "S.H.E〈不想長大〉":["不想長大","不想长大"], "林俊傑〈一千年以後〉":["一千年以後","一千年以后"],
 "蔡依林〈舞孃〉":["旋轉","旋转"], "陳奕迅〈好久不見〉":["忽然的出現","忽然的出现"],
 "S.H.E〈中國話〉":["都在學中國話","都在学中国话"], "林俊傑〈小酒窩〉":["小酒窩","小酒窝"],
 "林宥嘉〈說謊〉":["沒有說謊","没有说谎"], "田馥甄〈你就不要想起我〉":["你就不要想起我"],
 "張棟樑〈當你孤單你會想起誰〉":["當你孤單","当你孤单"], "林俊傑〈修煉愛情〉":["修煉愛情","修炼爱情"],
}
MIN_T = 25   # a chorus that only appears at the very start is taken from its next appearance
def keyed(name, L):
    ks = [re.sub(r"\s", "", k).lower() for k in KEY.get(name, [])]
    hits = [x for x in L if any(k in x[1] for k in ks)]
    later = [x for x in hits if x[0] >= MIN_T]
    return (later or hits or [None])[0]

res = {}
for name, tr, si, mvlen in SONGS:
    cands = [x for x in search(*tr) + search(*si) if x.get("syncedLyrics") and not re.search(r"live|演奏|伴奏|remix|dj|cover|版\)|版）", x["trackName"], re.I)]
    if not cands:
        res[name] = None; print(name, "no synced lyrics"); continue
    if mvlen: cands.sort(key=lambda x: abs(x["duration"] - mvlen))
    pick = None
    for c in cands[:8]:
        L = parse(c["syncedLyrics"])
        hit = keyed(name, L)
        if hit: pick = (c, L, hit); break
    if not pick:
        res[name] = None; print(name, "keyword not found"); continue
    c, L, hit = pick
    res[name] = {"t": round(hit[0], 1), "dur": round(c["duration"]), "first": round(L[0][0], 1)}
    print(f"{name}: chorus {hit[0]:.1f}s  audio {c['duration']:.0f}s / MV {mvlen}s")
    time.sleep(0.5)
(here / "lyrics_chorus.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
