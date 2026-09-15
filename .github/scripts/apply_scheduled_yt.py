"""Pone el ID de YouTube en index.html cuando toca (GitHub Action). Idempotente."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "index.html"

PIECES = {
    "ford": {
        "slug": "el-minuto-que-abarato-el-mundo",
        "yt": "gWqXk4PS-bU",
        "dur_sec": 55,
        "short": {
            "title": "El minuto que abarató el mundo",
            "desc": "En 1913 Ford puso el chasis en movimiento. Doce horas cayeron a noventa y tres minutos.",
            "dur": 55,
            "thumb": "MEDIA_ROOT+'/stories/ford/2.jpg'",
        },
    },
    "tambora": {
        "slug": "el-ano-sin-verano",
        "yt": "Xe7jQShYMqg",
        "dur_sec": 240,
        "short": None,
    },
}


def apply(name: str) -> bool:
    spec = PIECES[name]
    html = HTML.read_text(encoding="utf-8")
    orig = html
    slug, yt = spec["slug"], spec["yt"]
    if f"slug:'{slug}'" in html and f"yt:'{yt}'" in html.split(f"slug:'{slug}'", 1)[1][:500]:
        print("ya estaba", name, yt)
        return False
    html, n = re.subn(
        rf"(slug:'{re.escape(slug)}'[\s\S]{{0,500}}yt:)null",
        rf"\1'{yt}'",
        html,
        count=1,
    )
    if n != 1:
        raise SystemExit(f"no encontré yt:null de {name}")
    html = re.sub(
        rf"(slug:'{re.escape(slug)}'[\s\S]{{0,400}}durSec:)\d+",
        rf"\g<1>{spec['dur_sec']}",
        html,
        count=1,
    )
    sh = spec["short"]
    if sh:
        shorts_body = html.split("const SHORTS = [", 1)[1]
        if f"slug:'{slug}'" not in shorts_body[:3000]:
            line = (
                f" {{slug:'{slug}', story:'{slug}', title:'{sh['title']}', "
                f"desc:'{sh['desc']}', dur:{sh['dur']}, views:0, yt:'{yt}'}},\n"
            )
            html = html.replace("const SHORTS = [\n", "const SHORTS = [\n" + line, 1)
        thumb = sh["thumb"]
        marker = f"  'story-{slug}': {thumb},"
        short_key = f"  'short-{slug}': {thumb},"
        if short_key not in html and marker in html:
            html = html.replace(marker, marker + "\n" + short_key, 1)
    if html == orig:
        raise SystemExit(f"sin cambios {name}")
    HTML.write_text(html, encoding="utf-8", newline="\n")
    print("ok", name, yt)
    return True


def main() -> None:
    name = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PIECE", "")).strip()
    if name not in PIECES:
        raise SystemExit("uso: apply_scheduled_yt.py ford|tambora")
    apply(name)


if __name__ == "__main__":
    main()
