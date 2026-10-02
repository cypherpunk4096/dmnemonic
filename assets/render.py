#!/usr/bin/env python3
# dmnemonic — Algorand keys in the dmnemonic and demonic tongues
# Copyright (C) 2026 Professor Codephreak and the cypherpunk4096 contributors
# SPDX-License-Identifier: MIT
# Backend component, MIT licensed; see LICENSE-MIT.
"""Render the PNG assets from their sources (dev-only; needs `pip install playwright`).

  assets/og.html      → assets/og-dmnemonic.png        1200×630 social card
  assets/favicon.svg  → assets/apple-touch-icon.png    180×180 home-screen icon
"""
import pathlib, sys
from playwright.sync_api import sync_playwright

A = pathlib.Path(__file__).resolve().parent
exe = sys.argv[1] if len(sys.argv) > 1 else None
with sync_playwright() as p:
    b = p.chromium.launch(**({"executable_path": exe} if exe else {}))
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto((A / "og.html").as_uri())
    pg.screenshot(path=str(A / "og-dmnemonic.png"))
    pg = b.new_page(viewport={"width": 180, "height": 180})
    pg.set_content(f'<body style="margin:0;background:#0d0a0c">'
                   f'<img src="data:image/svg+xml;utf8,{(A / "favicon.svg").read_text().replace(chr(10), "").replace("#", "%23")}" width="180" height="180" style="display:block">')
    pg.screenshot(path=str(A / "apple-touch-icon.png"), omit_background=False)
    b.close()
print("rendered og-dmnemonic.png, apple-touch-icon.png")
