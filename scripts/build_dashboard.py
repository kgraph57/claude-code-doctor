#!/usr/bin/env python3
"""findings JSON → 1枚HTMLダッシュボード生成。

Usage:
    python3 build_dashboard.py input.json output.html

入力スキーマは references/report-format.md 参照。標準ライブラリのみで動く。
"""
import json
import html
import sys

SEV_JA = {"high": "影響 高", "medium": "影響 中", "low": "影響 低"}
EFF_JA = {"low": "工数 低", "medium": "工数 中", "high": "工数 高"}
SEV_RANK = {"high": 0, "medium": 1, "low": 2}

CSS = """
:root{--ink:#1a1a1a;--sub:#5c6166;--faint:#9aa0a5;--line:#e3e5e7;
  --teal:#0B7DA3;--orange:#E8801A;--bg:#fff;--panel:#f7f8f9}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Hiragino Sans","Noto Sans JP",system-ui,sans-serif;color:var(--ink);
  background:var(--bg);font-size:15.5px;line-height:1.85;font-feature-settings:"palt"}
.wrap{max-width:1040px;margin:0 auto;padding:0 40px}
.kicker{font-family:"Helvetica Neue",Inter,sans-serif;font-size:11px;letter-spacing:.22em;
  color:var(--teal);text-transform:uppercase;font-weight:600;margin-bottom:14px}
header{padding:84px 0 0}
h1{font-size:44px;font-weight:800;line-height:1.3}
.lede{color:var(--sub);margin-top:18px;max-width:44em}
.meta{display:flex;flex-wrap:wrap;gap:28px;margin-top:30px;padding:18px 0;
  border-top:1px solid var(--ink);border-bottom:1px solid var(--line);
  font-size:12.5px;color:var(--sub)}
.meta b{color:var(--ink);font-weight:600;margin-right:.6em}
.stats{display:grid;grid-template-columns:repeat(4,1fr);margin:56px 0 0;
  border-top:1px solid var(--line)}
.stat{padding:26px 22px 22px;border-bottom:1px solid var(--line)}
.stat+.stat{border-left:1px solid var(--line)}
.stat:nth-child(4n+1){border-left:none}
.stat .num{font-family:"Helvetica Neue",Inter,sans-serif;font-size:34px;font-weight:700;
  line-height:1.1}
.stat .num small{font-size:15px;font-weight:600;color:var(--sub);margin-left:2px}
.stat .lab{font-size:12px;color:var(--sub);margin-top:8px;line-height:1.6}
.stat.alert .num{color:var(--orange)}
.stat.key .num{color:var(--teal)}
section{padding:76px 0 0}
.snum{font-family:"Helvetica Neue",Inter,sans-serif;font-size:12px;color:var(--teal);
  letter-spacing:.18em;font-weight:600}
h2{font-size:28px;font-weight:800;margin:8px 0 10px}
.sdesc{color:var(--sub);max-width:46em;margin-bottom:34px}
.decision{display:grid;grid-template-columns:64px 1fr;gap:20px;padding:30px 0;
  border-top:1px solid var(--line)}
.decision:first-of-type{border-top:1px solid var(--ink)}
.dnum{font-family:"Helvetica Neue",Inter,sans-serif;font-size:26px;font-weight:700;
  color:var(--teal)}
.decision h3{font-size:18.5px;font-weight:700;margin-bottom:8px}
.decision .why{font-size:13.5px;color:var(--sub);margin-bottom:14px;max-width:52em}
.opts{display:flex;flex-wrap:wrap;gap:10px}
.opt{border:1px solid var(--line);padding:10px 16px;font-size:13.5px;line-height:1.6;
  background:var(--panel)}
.opt b{display:block;font-size:12px;color:var(--teal);
  font-family:"Helvetica Neue",Inter,sans-serif;letter-spacing:.08em;margin-bottom:2px}
.toplist{counter-reset:t;border-top:1px solid var(--ink)}
.topitem{display:grid;grid-template-columns:64px 1fr;gap:20px;padding:22px 0;
  border-bottom:1px solid var(--line)}
.topitem::before{counter-increment:t;content:counter(t,decimal-leading-zero);
  font-family:"Helvetica Neue",Inter,sans-serif;font-size:22px;font-weight:700;
  color:var(--faint)}
.topitem h3{font-size:16.5px;font-weight:700;margin-bottom:4px}
.topitem h3 .tag{display:inline-block;font-size:11px;font-weight:600;color:var(--orange);
  border:1px solid var(--orange);padding:1px 8px;margin-left:10px;vertical-align:2px;
  font-family:"Helvetica Neue",Inter,sans-serif}
.topitem p{font-size:13.5px;color:var(--sub);max-width:56em}
.mgrid{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.mcell{border:1px solid var(--line);padding:26px 28px}
.mcell.prime{border-color:var(--teal);border-width:1.5px}
.mcell h3{font-size:15px;font-weight:800;margin-bottom:4px}
.mcell h3 span{font-family:"Helvetica Neue",Inter,sans-serif;font-size:11px;
  color:var(--teal);letter-spacing:.14em;display:block;margin-bottom:6px;font-weight:600}
.mcell .when{font-size:12px;color:var(--orange);font-weight:600;margin-bottom:12px}
.mcell ul{list-style:none}
.mcell li{font-size:13.5px;padding:7px 0 7px 16px;border-top:1px solid var(--line);
  position:relative;line-height:1.7}
.mcell li::before{content:"";position:absolute;left:0;top:16px;width:6px;height:6px;
  background:var(--teal)}
.mcell.skip li::before{background:var(--faint)}
.phase{display:grid;grid-template-columns:150px 1fr;gap:24px;padding:26px 0;
  border-top:1px solid var(--line)}
.phase:first-of-type{border-top:1px solid var(--ink)}
.pname{font-family:"Helvetica Neue",Inter,sans-serif;font-weight:700;font-size:15px}
.pname small{display:block;font-size:11.5px;color:var(--orange);font-weight:600;
  margin-top:4px;font-family:inherit}
.phase ol{margin-left:1.3em;font-size:13.8px;color:#333}
.phase li{padding:3px 0}
.phase .note{font-size:12px;color:var(--sub);margin-top:8px}
pre.tree{font-family:"SF Mono",Menlo,monospace;font-size:12px;line-height:1.75;
  background:var(--panel);border:1px solid var(--line);padding:24px 28px;
  overflow-x:auto;color:#333}
.maprow{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.maprow h3{font-size:14px;font-weight:700;margin-bottom:10px}
.domain{border:1px solid var(--line);margin-bottom:14px}
.domain>summary{display:flex;align-items:baseline;gap:18px;padding:18px 24px;
  cursor:pointer;list-style:none;flex-wrap:wrap}
.domain>summary::-webkit-details-marker{display:none}
.domain>summary::before{content:"+";color:var(--teal);font-weight:600;font-size:18px;
  width:16px;font-family:"Helvetica Neue",sans-serif}
.domain[open]>summary::before{content:"\\2212"}
.dname{font-weight:800;font-size:16px}
.dsub{font-size:12.5px;color:var(--sub);flex:1}
.dcounts{font-size:12px;color:var(--sub);font-family:"Helvetica Neue",Inter,sans-serif}
.dcounts em{font-style:normal;font-weight:700;color:var(--orange)}
.dsummary{font-size:13px;color:var(--sub);padding:0 24px 16px 58px;max-width:60em}
.finding{border-top:1px solid var(--line);margin:0 24px 0 58px}
.finding:last-child{margin-bottom:20px}
.finding summary{display:flex;align-items:center;gap:10px;padding:12px 0;
  cursor:pointer;list-style:none}
.finding summary::-webkit-details-marker{display:none}
.ftitle{font-size:13.8px;font-weight:600;line-height:1.6}
.chip{font-family:"Helvetica Neue",Inter,sans-serif;font-size:10.5px;font-weight:600;
  padding:2px 9px;white-space:nowrap;flex-shrink:0}
.chip.sev.high{color:#fff;background:var(--orange)}
.chip.sev.medium{color:var(--ink);border:1px solid var(--ink)}
.chip.sev.low{color:var(--faint);border:1px solid var(--line)}
.chip.eff{color:var(--sub);background:var(--panel)}
.fbody{padding:4px 0 18px;font-size:13.3px;color:#333}
.fbody p{max-width:62em;margin-bottom:8px}
.flabel{font-family:"Helvetica Neue",Inter,sans-serif;font-size:10.5px;
  letter-spacing:.16em;color:var(--teal);font-weight:700;margin:10px 0 2px}
.controls{margin-bottom:22px}
.controls button{font:inherit;font-size:12px;padding:6px 14px;border:1px solid var(--line);
  background:var(--bg);cursor:pointer;color:var(--sub)}
.controls button:hover{border-color:var(--teal);color:var(--teal)}
footer{margin-top:90px;padding:34px 0 60px;border-top:1px solid var(--ink);
  font-size:12px;color:var(--sub);display:flex;justify-content:space-between;
  flex-wrap:wrap;gap:12px}
@media(max-width:860px){.stats{grid-template-columns:repeat(2,1fr)}
.mgrid,.maprow{grid-template-columns:1fr}.wrap{padding:0 22px}h1{font-size:32px}
.phase,.decision,.topitem{grid-template-columns:1fr;gap:6px}}
"""


def esc(s):
    return html.escape(str(s or ""))


def section(num, title, desc, body):
    return (f'<section><p class="snum">SECTION {num:02d}</p><h2>{esc(title)}</h2>'
            f'<p class="sdesc">{esc(desc)}</p>{body}</section>')


def build(data):
    meta = data.get("meta", {})
    parts = []
    n = 0

    # header + stats
    stats_html = "".join(
        f'<div class="stat {esc(s.get("tone", "key"))}">'
        f'<div class="num">{esc(s["n"])}<small>{esc(s.get("unit", ""))}</small></div>'
        f'<div class="lab">{esc(s["label"])}</div></div>'
        for s in data.get("stats", []))
    meta_html = "".join(
        f'<span><b>{esc(k)}</b>{esc(v)}</span>'
        for k, v in [("実施日", meta.get("date", "")), ("方式", meta.get("method", "")),
                     ("状態", meta.get("note", ""))] if v)
    parts.append(
        f'<header><p class="kicker">{esc(meta.get("kicker", "CLAUDE CODE DOCTOR"))}</p>'
        f'<h1>{esc(meta.get("title", "環境監査"))}</h1>'
        f'<p class="lede">{esc(meta.get("lede", ""))}</p>'
        f'<div class="meta">{meta_html}</div>'
        f'<div class="stats">{stats_html}</div></header>')

    if data.get("decisions"):
        n += 1
        body = "".join(
            f'<div class="decision"><div class="dnum">{i + 1}</div><div>'
            f'<h3>{esc(d["q"])}</h3><p class="why">{esc(d.get("why", ""))}</p>'
            f'<div class="opts">' + "".join(
                f'<div class="opt"><b>{esc(o["tag"])}</b>{esc(o["body"])}</div>'
                for o in d.get("options", [])) + "</div></div></div>"
            for i, d in enumerate(data["decisions"]))
        parts.append(section(n, "決めていただく事項", "AIは決めません。方針だけください。", body))

    if data.get("top"):
        n += 1
        body = '<div class="toplist">' + "".join(
            f'<div class="topitem"><div><h3>{esc(t["title"])}'
            + (f'<span class="tag">{esc(t["tag"])}</span>' if t.get("tag") else "")
            + f'</h3><p>{esc(t["body"])}</p></div></div>'
            for t in data["top"]) + "</div>"
        parts.append(section(n, "最重要の発見", "影響が大きい順。", body))

    if data.get("matrix"):
        n += 1
        body = '<div class="mgrid">' + "".join(
            f'<div class="mcell{" prime" if c.get("prime") else ""}'
            f'{" skip" if c.get("skip") else ""}">'
            f'<h3><span>{esc(key)} ・ {esc(c["title"])}</span></h3>'
            f'<p class="when">{esc(c.get("when", ""))}</p><ul>'
            + "".join(f"<li>{esc(i)}</li>" for i in c.get("items", []))
            + "</ul></div>"
            for key, c in data["matrix"].items()) + "</div>"
        parts.append(section(n, "影響度 × 工数マトリクス", "Aから順に着手する。", body))

    if data.get("phases"):
        n += 1
        body = "".join(
            f'<div class="phase"><div class="pname">{esc(p["name"])}'
            f'<small>{esc(p.get("when", ""))}</small></div><div><ol>'
            + "".join(f"<li>{esc(s)}</li>" for s in p.get("steps", []))
            + "</ol>"
            + (f'<p class="note">{esc(p["note"])}</p>' if p.get("note") else "")
            + "</div></div>"
            for p in data["phases"])
        parts.append(section(n, "段階的実行プラン", "全フェーズ承認後に実行。", body))

    if data.get("trees"):
        n += 1
        body = '<div class="maprow">' + "".join(
            f'<div><h3>{esc(t["title"])}</h3><pre class="tree">{esc(t["body"])}</pre></div>'
            for t in data["trees"]) + "</div>"
        parts.append(section(n, "現状マップ", "実測値ベースのスナップショット。", body))

    if data.get("domains"):
        n += 1
        total = sum(len(d.get("findings", [])) for d in data["domains"])
        doms = []
        for d in data["domains"]:
            fs = sorted(d.get("findings", []),
                        key=lambda f: (SEV_RANK[f["severity"]], f["effort"]))
            c = {"high": 0, "medium": 0, "low": 0}
            for f in fs:
                c[f["severity"]] += 1
            items = "".join(
                f'<details class="finding"><summary>'
                f'<span class="chip sev {f["severity"]}">{SEV_JA[f["severity"]]}</span>'
                f'<span class="chip eff">{EFF_JA[f["effort"]]}</span>'
                f'<span class="ftitle">{esc(f["title"])}</span></summary>'
                f'<div class="fbody"><p class="flabel">事実</p><p>{esc(f["detail"])}</p>'
                f'<p class="flabel">提案</p><p>{esc(f["recommendation"])}</p></div></details>'
                for f in fs)
            doms.append(
                f'<details class="domain"><summary><span class="dname">{esc(d["name"])}</span>'
                f'<span class="dsub">{esc(d.get("sub", ""))}</span>'
                f'<span class="dcounts"><em>{c["high"]}</em> 高 / {c["medium"]} 中 / '
                f'{c["low"]} 低</span></summary>'
                f'<p class="dsummary">{esc(d.get("summary", ""))}</p>{items}</details>')
        controls = ('<div class="controls">'
                    '<button onclick="document.querySelectorAll(\'details\')'
                    '.forEach(d=>d.open=true)">すべて展開</button> '
                    '<button onclick="document.querySelectorAll(\'details\')'
                    '.forEach(d=>d.open=false)">すべて閉じる</button></div>')
        parts.append(section(n, f"全指摘 {total}件（領域別）",
                             "各指摘は「事実」と「提案」のペア。提案は未実行。",
                             controls + "".join(doms)))

    parts.append(
        f'<footer><span>{esc(meta.get("footer", "claude-code-doctor"))}</span>'
        f'<span>read-only 監査・承認前変更なし</span></footer>')

    return (f'<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            f'<title>{esc(meta.get("title", "環境監査"))}</title><style>{CSS}</style></head>'
            f'<body><div class="wrap">{"".join(parts)}</div></body></html>')


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    data = json.load(open(sys.argv[1]))
    out = build(data)
    open(sys.argv[2], "w").write(out)
    print(f"OK {sys.argv[2]} ({len(out):,} bytes)")


if __name__ == "__main__":
    main()
