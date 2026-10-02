#!/usr/bin/env python3
# dmnemonic — Algorand keys in the dmnemonic and demonic tongues
# Copyright (C) 2026 Professor Codephreak and the cypherpunk4096 contributors
# SPDX-License-Identifier: MIT
# Backend component, MIT licensed; see LICENSE-MIT.
"""Assemble the page from src/ into its three forms.

  dmnemonic.html               standalone document with a no-network CSP (use this offline)
  dist/demonic-creator.html    fragment for publishing as a claude.ai Artifact
  ~/DeltaVerse/pages/dmnemonic.html   standalone copy inside the DeltaVerse site
"""
import base64, hashlib, json, os, pathlib, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import dmnemonic as d

data = "const ROOTS=%s;\nconst SUFFIXES=%s;\nconst ALGORAND_WORDS=%s.split(' ');\n" % (
    json.dumps(d.ROOTS), json.dumps(d.SUFFIXES), json.dumps(" ".join(d.ALGORAND_WORDS)))
core = (ROOT / "src/core.js").read_text().replace("/*@@VECTORS@@*/", json.dumps(d.VECTORS))
engine = data + core
version = hashlib.sha256(engine.encode()).hexdigest()[:12]
fragment = (ROOT / "src/ui.html").read_text()
fragment = fragment.replace("/*@@CORE@@*/", engine).replace("/*@@BUILD@@*/", f"engine {version}")

# Where the standalone page is served; drives canonical, Open Graph and JSON-LD URLs.
ORIGIN = os.environ.get("DMNEMONIC_ORIGIN", "https://deltaverse.pythai.net")
SITE = ORIGIN + "/dmnemonic"
OG_IMAGE = ORIGIN + "/gfx/og-dmnemonic.png"
SEO_TITLE = "dmnemonic Creator: Algorand seed phrases and post-quantum keys"

favicon = (ROOT / "assets/favicon.svg").read_text().replace("\n", "").replace('"', "'")
seo = (ROOT / "src/head.html").read_text()
for k, v in {
    "@@SITE@@": SITE, "@@ORIGIN@@": ORIGIN, "@@OG_IMAGE@@": OG_IMAGE,
    "@@FAVICON_SVG@@": "data:image/svg+xml," + urllib.parse.quote(favicon, safe=" /:=';,"),
    "@@APPLE_ICON@@": "data:image/png;base64," + base64.b64encode((ROOT / "assets/apple-touch-icon.png").read_bytes()).decode(),
}.items():
    seo = seo.replace(k, v)
assert "@@" not in seo

title_end = fragment.index("</style>") + len("</style>")
head, body = fragment[:title_end], fragment[title_end:]
# The artifact keeps its short name; the standalone page gets a search title and the SEO head.
head = head.replace("<title>dmnemonic Creator</title>", f"<title>{SEO_TITLE}</title>\n{seo}", 1)
standalone = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; form-action 'none'; base-uri 'none'">
<meta name="referrer" content="no-referrer">
{head}
</head>
<body>{body}</body>
</html>
"""
outs = {
    ROOT / "dmnemonic.html": standalone,
    ROOT / "dist/demonic-creator.html": fragment,
}
dv = pathlib.Path.home() / "DeltaVerse/pages"
if dv.is_dir():
    outs[dv / "dmnemonic.html"] = standalone
sums = []
for path, text in outs.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    sums.append(f"{hashlib.sha256(text.encode()).hexdigest()}  {path.name}")
    print(f"wrote {path}")
(ROOT / "dist/SHA256SUMS").write_text("\n".join(dict.fromkeys(sums)) + "\n")
print(f"engine {version}")
