#!/usr/bin/env python3
"""cards JSON → X共有用サニタイズ済みカードPNG（1600x900 × 最大4枚）。

Usage:
    python3 build_share_cards.py cards.json outdir/ [--chrome /path/to/chrome]

要件: headless Chrome/Chromium と Pillow。
サニタイズのシートベルトとして /Users/<name> 形式のパスは自動マスクする。

入力スキーマ:
{
  "brand": "フッター署名",
  "hero":    {"kicker": "...", "lines": ["行1", "行2", "<em>強調行</em>"],
              "big": {"n": "104", "unit": "件の指摘", "note": "内訳など"}, "sub": "..."},
  "numbers": {"kicker": "...", "title": "...",
              "cells": [{"n": "45,000", "unit": "tk", "label": "..."}]},   // 6個まで
  "lessons": {"kicker": "...", "title": "...",
              "items": [{"title": "...", "body": "..."}]},                 // 4個まで
  "howto":   {"kicker": "...", "title": "...",
              "steps": [{"title": "...", "body": "..."}],                  // 3個まで
              "tease": {"title": "...", "note": "..."}}                    // 任意
}
"""
import json
import html
import os
import re
import subprocess
import sys
import tempfile

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
]

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Hiragino Sans","Noto Sans JP",sans-serif;color:#1a1a1a;background:#fff;
  font-feature-settings:"palt"}
.card{width:1600px;height:900px;position:relative;overflow:hidden;background:#fff;
  padding:90px 110px 150px;display:flex;flex-direction:column}
.kicker{font-family:"Helvetica Neue",sans-serif;font-size:22px;letter-spacing:.24em;
  color:#0B7DA3;font-weight:600;margin-bottom:34px}
.rule{position:absolute;left:110px;right:110px;bottom:84px;border-top:1px solid #1a1a1a}
.foot{position:absolute;left:110px;bottom:44px;font-size:20px;color:#9aa0a5}
.pager{position:absolute;right:110px;bottom:44px;font-size:20px;color:#9aa0a5;
  font-family:"Helvetica Neue",sans-serif}
h1{font-size:76px;font-weight:800;line-height:1.42}
h1 em{font-style:normal;color:#0B7DA3}
.sub{font-size:28px;color:#5c6166;margin-top:36px;line-height:1.8}
.hero-num{margin-top:52px;display:flex;align-items:baseline;gap:28px}
.hero-num .n{font-family:"Helvetica Neue",sans-serif;font-size:170px;font-weight:700;
  color:#E8801A;line-height:1}
.hero-num .u{font-size:44px;font-weight:800}
.hero-num .d{font-size:26px;color:#5c6166}
h2{font-size:58px;font-weight:800;margin-bottom:34px}
.grid{display:grid;grid-template-columns:1fr 1fr 1fr;flex:1;border-top:1px solid #ddd}
.cell{padding:44px 36px;border-bottom:1px solid #ddd}
.cell:nth-child(3n+2){border-left:1px solid #ddd;border-right:1px solid #ddd}
.cell .n{font-family:"Helvetica Neue",sans-serif;font-size:72px;font-weight:700;line-height:1}
.cell .n small{font-size:32px;color:#5c6166;font-weight:600}
.cell:nth-child(-n+3) .n{color:#E8801A}
.cell:nth-child(n+4) .n{color:#0B7DA3}
.cell .l{font-size:23px;color:#5c6166;margin-top:16px;line-height:1.7}
ol.learn{list-style:none;counter-reset:l;flex:1}
ol.learn li{counter-increment:l;display:grid;grid-template-columns:90px 1fr;
  padding:19px 0;border-top:1px solid #ddd;align-items:baseline}
ol.learn li::before{content:counter(l,decimal-leading-zero);
  font-family:"Helvetica Neue",sans-serif;font-size:34px;font-weight:700;color:#0B7DA3}
ol.learn li b{font-size:32px;font-weight:800;display:block;margin-bottom:6px}
ol.learn li span{font-size:22px;color:#5c6166;line-height:1.6}
ol.steps{list-style:none;counter-reset:s;flex:1}
ol.steps li{counter-increment:s;display:grid;grid-template-columns:90px 1fr;
  padding:20px 0;border-top:1px solid #ddd;align-items:baseline}
ol.steps li::before{content:counter(s,decimal-leading-zero);
  font-family:"Helvetica Neue",sans-serif;font-size:34px;font-weight:700;color:#0B7DA3}
ol.steps li div{font-size:29px;line-height:1.65}
ol.steps li div small{display:block;font-size:23px;color:#5c6166;margin-top:4px}
.tease{margin-top:auto;background:#f7f8f9;border-left:6px solid #0B7DA3;
  padding:22px 34px;font-size:28px;font-weight:700}
.tease small{display:block;font-size:22px;color:#5c6166;font-weight:400;margin-top:6px}
"""

ALLOWED_TAGS = re.compile(r"</?(em|br)>")


def esc_keep(s):
    """emとbrだけ許可してエスケープする。"""
    s = str(s or "")
    placeholder = {}
    def stash(m):
        key = f"\x00{len(placeholder)}\x00"
        placeholder[key] = m.group(0)
        return key
    s = ALLOWED_TAGS.sub(stash, s)
    s = html.escape(s)
    for k, v in placeholder.items():
        s = s.replace(k, v)
    return s


def sanitize(s):
    """公開向けシートベルト: 個人パス・ホームディレクトリ名をマスクする。"""
    s = re.sub(r"/(?:Users|home)/[A-Za-z0-9_.-]+", "~", str(s or ""))
    return s


def build_html(d):
    brand = esc_keep(sanitize(d.get("brand", "")))
    cards = []

    def foot(i, total):
        return (f'<div class="rule"></div><p class="foot">{brand}</p>'
                f'<p class="pager">{i} / {total}</p></div>')

    specs = [k for k in ("hero", "numbers", "lessons", "howto") if d.get(k)]
    total = len(specs)
    for i, key in enumerate(specs, 1):
        c = d[key]
        kicker = esc_keep(sanitize(c.get("kicker", key.upper())))
        if key == "hero":
            lines = "<br>".join(esc_keep(sanitize(x)) for x in c.get("lines", []))
            big = c.get("big", {})
            cards.append(
                f'<div class="card"><p class="kicker">{kicker}</p><h1>{lines}</h1>'
                f'<div class="hero-num"><span class="n">{esc_keep(big.get("n", ""))}</span>'
                f'<span class="u">{esc_keep(big.get("unit", ""))}</span>'
                f'<span class="d">{esc_keep(sanitize(big.get("note", "")))}</span></div>'
                f'<p class="sub">{esc_keep(sanitize(c.get("sub", "")))}</p>' + foot(i, total))
        elif key == "numbers":
            cells = "".join(
                f'<div class="cell"><div class="n">{esc_keep(x["n"])}'
                f'<small>{esc_keep(x.get("unit", ""))}</small></div>'
                f'<div class="l">{esc_keep(sanitize(x["label"]))}</div></div>'
                for x in c.get("cells", [])[:6])
            cards.append(
                f'<div class="card"><p class="kicker">{kicker}</p>'
                f'<h2>{esc_keep(sanitize(c.get("title", "")))}</h2>'
                f'<div class="grid">{cells}</div>' + foot(i, total))
        elif key == "lessons":
            items = "".join(
                f'<li><div><b>{esc_keep(sanitize(x["title"]))}</b>'
                f'<span>{esc_keep(sanitize(x["body"]))}</span></div></li>'
                for x in c.get("items", [])[:4])
            cards.append(
                f'<div class="card"><p class="kicker">{kicker}</p>'
                f'<h2>{esc_keep(sanitize(c.get("title", "")))}</h2>'
                f'<ol class="learn">{items}</ol>' + foot(i, total))
        elif key == "howto":
            steps = "".join(
                f'<li><div>{esc_keep(sanitize(x["title"]))}'
                f'<small>{esc_keep(sanitize(x["body"]))}</small></div></li>'
                for x in c.get("steps", [])[:3])
            tease = c.get("tease")
            tease_html = ""
            if tease:
                tease_html = (f'<div class="tease">{esc_keep(sanitize(tease["title"]))}'
                              f'<small>{esc_keep(sanitize(tease.get("note", "")))}</small></div>')
            cards.append(
                f'<div class="card"><p class="kicker">{kicker}</p>'
                f'<h2>{esc_keep(sanitize(c.get("title", "")))}</h2>'
                f'<ol class="steps">{steps}</ol>{tease_html}' + foot(i, total))

    return (f'<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">'
            f'<style>{CSS}</style></head><body>{"".join(cards)}</body></html>'), total


def find_chrome(override=None):
    for p in ([override] if override else []) + CHROME_CANDIDATES:
        if p and os.path.exists(p):
            return p
    sys.exit("headless Chrome/Chromiumが見つかりません。--chrome でパスを指定してください。")


def main():
    args = sys.argv[1:]
    chrome_override = None
    if "--chrome" in args:
        i = args.index("--chrome")
        chrome_override = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__)
        sys.exit(1)

    from PIL import Image  # 遅延import（ヘルプ表示に依存を要求しない）

    data = json.load(open(args[0]))
    outdir = args[1]
    os.makedirs(outdir, exist_ok=True)
    doc, total = build_html(data)

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(doc)
        src = f.name
    shot = src + ".png"
    subprocess.run([find_chrome(chrome_override), "--headless=new", "--disable-gpu",
                    "--hide-scrollbars", f"--screenshot={shot}",
                    f"--window-size=1600,{900 * total}", f"file://{src}"],
                   capture_output=True, check=True)

    im = Image.open(shot)
    names = [k for k in ("hero", "numbers", "lessons", "howto") if data.get(k)]
    for i, name in enumerate(names):
        path = os.path.join(outdir, f"card{i + 1}-{name}.png")
        im.crop((0, i * 900, 1600, (i + 1) * 900)).save(path)
        print(path)
    os.unlink(src)
    os.unlink(shot)


if __name__ == "__main__":
    main()
