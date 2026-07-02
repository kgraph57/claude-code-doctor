#!/usr/bin/env python3
"""findings JSON → 1枚HTMLダッシュボード生成。

Usage:
    python3 build_dashboard.py input.json output.html

入力スキーマは references/report-format.md 参照。標準ライブラリのみで動く。
"""
import json
import html
import sys

SEV_RANK = {"high": 0, "medium": 1, "low": 2}
GRADE_ORDER = ["A", "B", "C", "D", "E"]


SEV_W = {"high": 3, "medium": 1, "low": 0.25}
EFF_OK = {"low", "medium", "high"}


def normalize(data):
    """Coerce LLM-generated JSON into safe shape: unknown enums, missing keys,
    stringly-typed numbers. One pass at the boundary so rendering never crashes."""
    for dom in data.get("domains", []) or []:
        for f in dom.get("findings", []) or []:
            if f.get("severity") not in SEV_W:
                f["severity"] = "medium"
            if f.get("effort") not in EFF_OK:
                f["effort"] = "medium"
    ck = data.get("checkup") or {}
    for sy in ck.get("systems", []) or []:
        if sy.get("score") is not None:
            try:
                sy["score"] = max(0, min(100, int(float(str(sy["score"])))))
            except (ValueError, TypeError):
                sy["score"] = None
        if sy.get("grade") not in (None, "A", "B", "C", "D", "E"):
            sy["grade"] = None
    if ck.get("overall") not in (None, "A", "B", "C", "D", "E"):
        ck["overall"] = None
    return data


def compute_score(findings):
    """0-100 health score from a domain's findings (severity-weighted burden)."""
    burden = sum(SEV_W[f["severity"]] for f in findings)
    return max(5, round(100 - 5 * burden))


def grade_from_score(score):
    for grade, floor in (("A", 95), ("B", 80), ("C", 55), ("D", 25)):
        if score >= floor:
            return grade
    return "E"


def has_red_flag(findings):
    """Critical findings (marked "critical": true) force grade E regardless of score."""
    return any(f.get("critical") for f in findings)

LABELS = {
    "en": {
        "sev": {"high": "impact high", "medium": "impact med", "low": "impact low"},
        "eff": {"low": "effort low", "medium": "effort med", "high": "effort high"},
        "meta": [("Date", "date"), ("Method", "method"), ("Status", "note")],
        "decisions_t": "Decisions you own", "decisions_d": "The AI does not decide. Pick an option per item.",
        "top_t": "Top findings", "top_d": "Ordered by impact.",
        "matrix_t": "Impact x Effort matrix", "matrix_d": "Start from A.",
        "phases_t": "Phased plan", "phases_d": "Executed only after approval.",
        "trees_t": "Current state map", "trees_d": "Measured snapshot.",
        "checkup_t": "The checkup report",
        "checkup_d": "Your Claude Code setup, examined as a body. Grades follow a standard checkup scale.",
        "overall": "Overall",
        "grades": {"A": "Healthy", "B": "Minor findings", "C": "Watch",
                   "D": "Needs work", "E": "Treat now"},
        "actions_t": "The prescription: action plan",
        "actions_d": "Each item carries a ready-to-paste prompt for Claude Code. Check off as you go (saved in your browser).",
        "rx_show": "Show the prompt to paste into Claude Code",
        "rx_copy": "Copy prompt", "rx_copied": "Copied",
        "risk": {"safe": "safe", "careful": "careful", "surgery": "surgery"},
        "domains_t": "All {n} findings by domain",
        "domains_d": "Each finding pairs evidence with a proposal. Nothing has been executed.",
        "fact": "Evidence", "rec": "Proposal", "unmeasured": "not measured",
        "counts": ("high", "med", "low"),
        "expand": "Expand all", "collapse": "Collapse all",
        "footer_note": "read-only audit / no changes before approval",
    },
    "ja": {
        "sev": {"high": "影響 高", "medium": "影響 中", "low": "影響 低"},
        "eff": {"low": "工数 低", "medium": "工数 中", "high": "工数 高"},
        "meta": [("実施日", "date"), ("方式", "method"), ("状態", "note")],
        "decisions_t": "決めていただく事項", "decisions_d": "AIは決めません。方針だけください。",
        "top_t": "最重要の発見", "top_d": "影響が大きい順。",
        "matrix_t": "影響度 × 工数マトリクス", "matrix_d": "Aから順に着手する。",
        "phases_t": "段階的実行プラン", "phases_d": "全フェーズ承認後に実行。",
        "trees_t": "現状マップ", "trees_d": "実測値ベースのスナップショット。",
        "checkup_t": "健診結果",
        "checkup_d": "あなたのClaude Codeという身体の状態。判定は人間ドックの5段階。",
        "overall": "総合判定",
        "grades": {"A": "異常なし", "B": "軽度所見", "C": "要経過観察",
                   "D": "要精密検査", "E": "要治療"},
        "actions_t": "処方箋 ── アクションプラン",
        "actions_d": "各項目に、そのままClaude Codeへ貼れる実行プロンプト付き。チェックはブラウザに保存されます。",
        "rx_show": "Claude Codeに貼るプロンプトを表示",
        "rx_copy": "処方箋をコピー", "rx_copied": "コピーしました",
        "risk": {"safe": "安全", "careful": "要注意", "surgery": "手術"},
        "domains_t": "全指摘 {n}件（領域別）",
        "domains_d": "各指摘は「事実」と「提案」のペア。提案は未実行。",
        "fact": "事実", "rec": "提案", "unmeasured": "未測定（スコアなし）",
        "counts": ("高", "中", "低"),
        "expand": "すべて展開", "collapse": "すべて閉じる",
        "footer_note": "read-only 監査・承認前変更なし",
    },
}

def radar_svg(systems):
    """Decagon radar chart of per-system scores (0-100)."""
    import math
    cx, cy, r = 205, 160, 112
    n = len(systems)
    if n < 3:
        return ""

    def pt(i, frac):
        a = -math.pi / 2 + 2 * math.pi * i / n
        return (cx + r * frac * math.cos(a), cy + r * frac * math.sin(a))

    rings = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, frac) for i in range(n)))
        rings.append(f'<polygon points="{pts}" fill="none" stroke="#e3e5e7" stroke-width="1"/>')
    axes = []
    labels = []
    for i, sy in enumerate(systems):
        x, y = pt(i, 1.0)
        axes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#e3e5e7" stroke-width="1"/>')
        lx, ly = pt(i, 1.22)
        anchor = "middle" if abs(lx - cx) < 12 else ("start" if lx > cx else "end")
        label = html.escape(str(sy.get("organ") or sy.get("short") or sy.get("domain", ""))[:18])
        labels.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="10.5" fill="#5c6166" '
                      f'text-anchor="{anchor}" dominant-baseline="middle">{label}</text>')
    data_pts = " ".join(
        f"{x:.1f},{y:.1f}" for x, y in
        (pt(i, max(0.04, sy["score"] / 100)) for i, sy in enumerate(systems)))
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#0B7DA3"/>' for x, y in
        (pt(i, max(0.04, sy["score"] / 100)) for i, sy in enumerate(systems)))
    return (f'<svg viewBox="0 0 410 320" font-family="Helvetica Neue,Inter,sans-serif">'
            f'{"".join(rings)}{"".join(axes)}'
            f'<polygon points="{data_pts}" fill="rgba(11,125,163,.14)" '
            f'stroke="#0B7DA3" stroke-width="2"/>{dots}{"".join(labels)}</svg>')


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
/* checkup */
.overallrow{display:grid;grid-template-columns:170px 1fr 360px;gap:34px;align-items:center;
  border:1.5px solid var(--ink);padding:26px 32px;margin-bottom:40px}
.overallrow .radar svg{width:100%;height:auto}
.overallrow .oscore{font-size:13px;color:var(--sub);margin-top:8px;
  font-family:"Helvetica Neue",Inter,sans-serif}
.redflags{border:1.5px solid var(--orange);padding:16px 22px;margin:0 0 36px;
  font-size:13px;line-height:1.8}
.redflags b{color:var(--orange);font-family:"Helvetica Neue",Inter,sans-serif;
  font-size:11px;letter-spacing:.14em;display:block;margin-bottom:4px}
@media(max-width:860px){.overallrow{grid-template-columns:1fr}}
.overallrow .og{display:flex;align-items:baseline;gap:14px}
.overallrow .og b{font-family:"Helvetica Neue",Inter,sans-serif;font-size:74px;
  font-weight:800;line-height:1}
.overallrow .og span{font-size:14px;color:var(--sub)}
.overallrow p{font-size:14px;color:#333;max-width:56em;line-height:1.9}
.overallrow .ol{font-size:11px;letter-spacing:.16em;color:var(--teal);font-weight:700;
  font-family:"Helvetica Neue",Inter,sans-serif;margin-bottom:6px}
.bodymap{display:grid;grid-template-columns:1fr 250px 1fr;gap:0 26px;align-items:center}
.bodymap.plain{grid-template-columns:1fr 1fr;gap:14px 26px;align-items:start}
.syscol{display:flex;flex-direction:column;gap:14px}
.sys{border:1px solid var(--line);padding:14px 16px;display:grid;
  grid-template-columns:44px 1fr;gap:14px;align-items:center;background:var(--bg)}
.sys .note{grid-column:1/-1;font-size:12px;color:var(--sub);line-height:1.65;
  border-top:1px dashed var(--line);padding-top:8px;margin-top:2px}
.gbadge{width:44px;height:44px;display:flex;align-items:center;justify-content:center;
  font-family:"Helvetica Neue",Inter,sans-serif;font-size:24px;font-weight:800}
.g-A{border:2px solid var(--teal);color:var(--teal);background:rgba(11,125,163,.07)}
.g-B{border:2px solid var(--teal);color:var(--teal)}
.g-N{border:2px dashed var(--line);color:var(--faint)}
.g-C{border:2px solid var(--ink);color:var(--ink)}
.g-D{border:2px solid var(--orange);color:var(--orange)}
.g-E{background:var(--orange);color:#fff}
.sys .organ{font-size:10.5px;letter-spacing:.14em;color:var(--teal);font-weight:700;
  font-family:"Helvetica Neue",Inter,sans-serif;text-transform:uppercase}
.sys .dn{font-size:14px;font-weight:700;line-height:1.5}
.sys .gl{font-size:11px;color:var(--sub)}
.sys .gl i{font-style:normal;font-family:"Helvetica Neue",Inter,sans-serif;
  color:var(--faint);margin-left:6px}
.figure{display:flex;justify-content:center}
.figure svg{width:220px;height:auto}
@media(max-width:860px){.bodymap{grid-template-columns:1fr}.figure{order:-1}}
/* prescription */
.rxphase{font-family:"Helvetica Neue",Inter,sans-serif;font-size:13px;
  letter-spacing:.14em;color:var(--teal);font-weight:700;margin:34px 0 14px;
  padding-bottom:8px;border-bottom:1px solid var(--ink)}
.rxphase:first-of-type{margin-top:0}
.rxphase small{color:var(--sub);font-weight:400;letter-spacing:0;margin-left:12px}
.rx{border:1px solid var(--line);margin-bottom:12px;background:var(--bg)}
.rxhead{display:flex;align-items:center;gap:12px;padding:14px 18px;cursor:pointer;
  flex-wrap:wrap}
.rxhead input{width:17px;height:17px;accent-color:var(--teal);flex-shrink:0}
.rxid{font-family:"Helvetica Neue",Inter,sans-serif;font-size:12px;font-weight:700;
  color:var(--faint)}
.rxtitle{font-size:14.5px;font-weight:700;flex:1;min-width:200px}
.rx.done .rxtitle{text-decoration:line-through;color:var(--faint)}
.rxeffect{font-family:"Helvetica Neue",Inter,sans-serif;font-size:12px;font-weight:700;
  color:var(--teal);white-space:nowrap}
.chip.risk.safe{color:var(--teal);border:1px solid var(--teal)}
.chip.risk.careful{color:var(--ink);border:1px solid var(--ink)}
.chip.risk.surgery{color:#fff;background:var(--orange)}
.rxsteps{list-style:none;padding:0 18px 4px 46px;font-size:13px;color:#333}
.rxsteps li{padding:3px 0 3px 14px;position:relative;line-height:1.7}
.rxsteps li::before{content:"";position:absolute;left:0;top:12px;width:5px;height:5px;
  background:var(--teal)}
.rxprompt{margin:6px 18px 16px 46px}
.rxprompt summary{font-size:12px;color:var(--sub);cursor:pointer;list-style:none}
.rxprompt summary::-webkit-details-marker{display:none}
.rxprompt summary::before{content:"+ ";color:var(--teal);font-weight:700}
.rxprompt[open] summary::before{content:"\2212 "}
.rxprompt pre{font-family:"SF Mono",Menlo,monospace;font-size:12px;line-height:1.8;
  background:var(--panel);border:1px solid var(--line);padding:16px 18px;
  white-space:pre-wrap;margin:10px 0 8px}
.copybtn{font:inherit;font-size:12px;padding:6px 16px;border:1px solid var(--teal);
  background:var(--bg);color:var(--teal);cursor:pointer;font-weight:600}
.copybtn:hover{background:var(--teal);color:#fff}
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


RX_JS = """
document.querySelectorAll('.copybtn').forEach(function(b){
  b.addEventListener('click',function(){
    var pre=b.parentElement.querySelector('pre');
    navigator.clipboard.writeText(pre.textContent).then(function(){
      var t=b.textContent;b.textContent=b.dataset.copied||'Copied';
      setTimeout(function(){b.textContent=t;},1600);});});});
var KEY='ccd-rx-'+location.pathname;
var saved={};try{saved=JSON.parse(localStorage.getItem(KEY)||'{}');}catch(e){}
document.querySelectorAll('.rx').forEach(function(rx){
  var id=rx.dataset.rx,cb=rx.querySelector('input');
  if(saved[id]){cb.checked=true;rx.classList.add('done');}
  cb.addEventListener('change',function(){
    rx.classList.toggle('done',cb.checked);saved[id]=cb.checked;
    localStorage.setItem(KEY,JSON.stringify(saved));});});
"""


def build(data):
    meta = data.get("meta", {})
    L = LABELS.get(meta.get("lang", "en"), LABELS["en"])
    parts = []
    n = 0

    # header + stats
    stats_html = "".join(
        f'<div class="stat {esc(s.get("tone", "key"))}">'
        f'<div class="num">{esc(s.get("n", ""))}<small>{esc(s.get("unit", ""))}</small></div>'
        f'<div class="lab">{esc(s.get("label", ""))}</div></div>'
        for s in data.get("stats", []))
    meta_html = "".join(
        f'<span><b>{esc(k)}</b>{esc(v)}</span>'
        for k, key in L["meta"] for v in [meta.get(key, "")] if v)
    parts.append(
        f'<header><p class="kicker">{esc(meta.get("kicker", "CLAUDE CODE DOCTOR"))}</p>'
        f'<h1>{esc(meta.get("title", "環境監査"))}</h1>'
        f'<p class="lede">{esc(meta.get("lede", ""))}</p>'
        f'<div class="meta">{meta_html}</div>'
        f'<div class="stats">{stats_html}</div></header>')

    if data.get("checkup"):
        n += 1
        ck = data["checkup"]
        systems = list(ck.get("systems", []))
        dom_by_name = {d["name"]: d for d in data.get("domains", [])}
        red_flags = list(ck.get("red_flags", []))
        for i, sy in enumerate(systems):
            dom = dom_by_name.get(sy.get("domain", ""))
            if dom is None and len(systems) == len(data.get("domains", [])):
                dom = data["domains"][i]
            findings = dom.get("findings", []) if dom else []
            if sy.get("score") is None and dom is not None:
                sy["score"] = compute_score(findings)
            if not sy.get("grade") and sy.get("score") is not None:
                sy["grade"] = grade_from_score(sy["score"])
                if findings:
                    if has_red_flag(findings):
                        sy["grade"] = "E"
                    elif any(f["severity"] == "high" for f in findings) \
                            and sy["grade"] in ("A", "B"):
                        sy["grade"] = "C"
        measured = [sy for sy in systems if sy.get("score") is not None]
        overall_score = ck.get("overall_score")
        if overall_score is None and measured:
            overall_score = round(sum(sy["score"] for sy in measured) / len(measured))
        overall = ck.get("overall") or (
            grade_from_score(overall_score) if overall_score is not None else "C")
        if any(sy.get("grade") == "E" for sy in systems) and overall in ("A", "B"):
            overall = "C"

        def chip(sy):
            g = sy.get("grade")
            if g is None:
                organ = (f'<div class="organ">{esc(sy["organ"])}</div>'
                         if sy.get("organ") else "")
                return (f'<div class="sys"><div class="gbadge g-N">&#8212;</div><div>'
                        f'{organ}<div class="dn">{esc(sy.get("domain", ""))}</div>'
                        f'<div class="gl">{esc(L["unmeasured"])}</div></div></div>')
            organ = (f'<div class="organ">{esc(sy["organ"])}</div>'
                     if sy.get("organ") else "")
            return (f'<div class="sys"><div class="gbadge g-{g}">{g}</div><div>'
                    f'{organ}'
                    f'<div class="dn">{esc(sy.get("domain", ""))}</div>'
                    f'<div class="gl">{esc(L["grades"].get(g, g))}<i>{sy["score"]}/100</i></div></div>'
                    + (f'<div class="note">{esc(sy["note"])}</div>' if sy.get("note") else "")
                    + '</div>')

        use_figure = any(sy.get("organ") for sy in systems)
        half = (len(systems) + 1) // 2
        left = "".join(chip(sy) for sy in systems[:half])
        right = "".join(chip(sy) for sy in systems[half:])
        svg = ('<svg viewBox="0 0 200 430" fill="none" stroke="#1a1a1a" '
               'stroke-width="2.5"><circle cx="100" cy="42" r="27"/>'
               '<rect x="67" y="76" width="66" height="132" rx="28"/>'
               '<rect x="36" y="84" width="22" height="112" rx="11"/>'
               '<rect x="142" y="84" width="22" height="112" rx="11"/>'
               '<rect x="71" y="212" width="25" height="142" rx="12"/>'
               '<rect x="104" y="212" width="25" height="142" rx="12"/>'
               '<g fill="#0B7DA3" stroke="none"><circle cx="100" cy="42" r="4"/>'
               '<circle cx="88" cy="108" r="4"/><circle cx="100" cy="150" r="4"/>'
               '<circle cx="47" cy="150" r="4"/><circle cx="153" cy="150" r="4"/>'
               '<circle cx="100" cy="190" r="4"/><circle cx="83" cy="280" r="4"/>'
               '<circle cx="116" cy="280" r="4"/></g></svg>')
        rf_html = ""
        if red_flags:
            rf_html = ('<div class="redflags"><b>RED FLAGS</b>'
                       + "<br>".join(esc(r) for r in red_flags) + "</div>")
        body = (f'<div class="overallrow"><div><div class="ol">{esc(L["overall"])}</div>'
                f'<div class="og"><b>{esc(overall)}</b>'
                f'<span>{esc(L["grades"].get(overall, overall))}</span></div>'
                f'<div class="oscore">{overall_score if overall_score is not None else ""}'
                f'{" / 100" if overall_score is not None else ""}</div></div>'
                f'<p>{esc(ck.get("comment", ""))}</p>'
                f'<div class="radar">{radar_svg(measured)}</div></div>'
                + rf_html
                + (f'<div class="bodymap"><div class="syscol">{left}</div>'
                   f'<div class="figure">{svg}</div>'
                   f'<div class="syscol">{right}</div></div>'
                   if use_figure else
                   f'<div class="bodymap plain"><div class="syscol">{left}</div>'
                   f'<div class="syscol">{right}</div></div>'))
        parts.append(section(n, L["checkup_t"], L["checkup_d"], body))

    if data.get("decisions"):
        n += 1
        body = "".join(
            f'<div class="decision"><div class="dnum">{i + 1}</div><div>'
            f'<h3>{esc(d.get("q", ""))}</h3><p class="why">{esc(d.get("why", ""))}</p>'
            f'<div class="opts">' + "".join(
                f'<div class="opt"><b>{esc(o.get("tag", ""))}</b>{esc(o.get("body", ""))}</div>'
                for o in d.get("options", [])) + "</div></div></div>"
            for i, d in enumerate(data["decisions"]))
        parts.append(section(n, L["decisions_t"], L["decisions_d"], body))

    if data.get("top"):
        n += 1
        body = '<div class="toplist">' + "".join(
            f'<div class="topitem"><div><h3>{esc(t.get("title", ""))}'
            + (f'<span class="tag">{esc(t["tag"])}</span>' if t.get("tag") else "")
            + f'</h3><p>{esc(t.get("body", ""))}</p></div></div>'
            for t in data["top"]) + "</div>"
        parts.append(section(n, L["top_t"], L["top_d"], body))

    if data.get("matrix"):
        n += 1
        body = '<div class="mgrid">' + "".join(
            f'<div class="mcell{" prime" if c.get("prime") else ""}'
            f'{" skip" if c.get("skip") else ""}">'
            f'<h3><span>{esc(key)} ・ {esc(c.get("title", ""))}</span></h3>'
            f'<p class="when">{esc(c.get("when", ""))}</p><ul>'
            + "".join(f"<li>{esc(i)}</li>" for i in c.get("items", []))
            + "</ul></div>"
            for key, c in data["matrix"].items()) + "</div>"
        parts.append(section(n, L["matrix_t"], L["matrix_d"], body))

    if data.get("actions"):
        n += 1
        rows = []
        prev_phase = None
        for a in data["actions"]:
            ph = a.get("phase", "")
            if ph != prev_phase:
                when = f'<small>{esc(a.get("phase_when", ""))}</small>' if a.get("phase_when") else ""
                rows.append(f'<h3 class="rxphase">{esc(ph)}{when}</h3>')
                prev_phase = ph
            steps = "".join(f"<li>{esc(st)}</li>" for st in a.get("steps", []))
            prompt = ""
            if a.get("prompt"):
                prompt = (f'<details class="rxprompt"><summary>{L["rx_show"]}</summary>'
                          f'<pre>{esc(a["prompt"])}</pre>'
                          f'<button class="copybtn" type="button" data-copied="{esc(L["rx_copied"])}">{L["rx_copy"]}</button>'
                          f'</details>')
            risk = a.get("risk", "safe")
            rows.append(
                f'<div class="rx" data-rx="{esc(a.get("id", ""))}">'
                f'<label class="rxhead"><input type="checkbox">'
                f'<span class="rxid">{esc(a.get("id", ""))}</span>'
                f'<span class="rxtitle">{esc(a.get("title", ""))}</span>'
                f'<span class="chip risk {esc(risk)}">{esc(L["risk"].get(risk, risk))}</span>'
                f'<span class="chip eff">{esc(a.get("effort", ""))}</span>'
                f'<span class="rxeffect">{esc(a.get("effect", ""))}</span></label>'
                f'{"<ul class=\"rxsteps\">" + steps + "</ul>" if steps else ""}'
                f'{prompt}</div>')
        parts.append(section(n, L["actions_t"], L["actions_d"], "".join(rows)))

    if data.get("phases"):
        n += 1
        body = "".join(
            f'<div class="phase"><div class="pname">{esc(p.get("name", ""))}'
            f'<small>{esc(p.get("when", ""))}</small></div><div><ol>'
            + "".join(f"<li>{esc(s)}</li>" for s in p.get("steps", []))
            + "</ol>"
            + (f'<p class="note">{esc(p["note"])}</p>' if p.get("note") else "")
            + "</div></div>"
            for p in data["phases"])
        parts.append(section(n, L["phases_t"], L["phases_d"], body))

    if data.get("trees"):
        n += 1
        body = '<div class="maprow">' + "".join(
            f'<div><h3>{esc(t.get("title", ""))}</h3><pre class="tree">{esc(t.get("body", ""))}</pre></div>'
            for t in data["trees"]) + "</div>"
        parts.append(section(n, L["trees_t"], L["trees_d"], body))

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
                f'<span class="chip sev {f["severity"]}">{L["sev"][f["severity"]]}</span>'
                f'<span class="chip eff">{L["eff"][f["effort"]]}</span>'
                f'<span class="ftitle">{esc(f["title"])}</span></summary>'
                f'<div class="fbody"><p class="flabel">{L["fact"]}</p><p>{esc(f["detail"])}</p>'
                f'<p class="flabel">{L["rec"]}</p><p>{esc(f["recommendation"])}</p></div></details>'
                for f in fs)
            doms.append(
                f'<details class="domain"><summary><span class="dname">{esc(d.get("name", ""))}</span>'
                f'<span class="dsub">{esc(d.get("sub", ""))}</span>'
                f'<span class="dcounts"><em>{c["high"]}</em> {L["counts"][0]} / {c["medium"]} '
                f'{L["counts"][1]} / {c["low"]} {L["counts"][2]}</span></summary>'
                f'<p class="dsummary">{esc(d.get("summary", ""))}</p>{items}</details>')
        controls = ('<div class="controls">'
                    '<button onclick="document.querySelectorAll(\'details\')'
                    '.forEach(d=>d.open=true)">' + L["expand"] + '</button> '
                    '<button onclick="document.querySelectorAll(\'details\')'
                    '.forEach(d=>d.open=false)">' + L["collapse"] + '</button></div>')
        parts.append(section(n, L["domains_t"].format(n=total), L["domains_d"],
                             controls + "".join(doms)))

    parts.append(
        f'<footer><span>{esc(meta.get("footer", "claude-code-doctor"))}</span>'
        f'<span>{L["footer_note"]}</span></footer>')

    return (f'<!DOCTYPE html><html lang="{esc(meta.get("lang", "en"))}"><head><meta charset="UTF-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            f'<title>{esc(meta.get("title", "環境監査"))}</title><style>{CSS}</style></head>'
            f'<body><div class="wrap">{"".join(parts)}</div>'
            f'<script>{RX_JS}</script></body></html>')


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    data = normalize(json.load(open(sys.argv[1])))
    out = build(data)
    open(sys.argv[2], "w").write(out)
    print(f"OK {sys.argv[2]} ({len(out):,} bytes)")


if __name__ == "__main__":
    main()
