#!/usr/bin/env python3
"""TulisAja Navigation Site — Static Site Builder"""
import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

DOMAIN = "officialdownloadhub.com"
SRC = Path(__file__).parent / "src"
DIST = Path(__file__).parent / "dist"

# Load software data
with open(SRC / "data" / "software.json", "r") as f:
    software_list = json.load(f)

# Build indices
software_by_slug = {}
categories = {}
for sw in software_list:
    software_by_slug[sw["slug"]] = sw
    cat = sw["category"]
    if cat not in categories:
        categories[cat] = {"name": sw["category_name"], "items": []}
    categories[cat]["items"].append(sw)

# Jinja2 setup
env = Environment(loader=FileSystemLoader(str(SRC / "templates")))
env.globals["domain"] = DOMAIN

def render(template, dest, **kwargs):
    """Render template and write to dist"""
    html = template.render(**kwargs, page_url=dest)
    out_path = DIST / dest.lstrip("/")
    if dest.endswith("/") or dest == "":
        out_path = out_path / "index.html"
    elif not dest.endswith(".html"):
        out_path = out_path / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path

def build():
    print("🚀 Building Official Download Hub...")

    # Clean dist
    if DIST.exists():
        import shutil
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # Homepage
    cat_list = [(cid, cat["name"], cat["items"]) for cid, cat in categories.items()]
    render(env.get_template("index.html"), "/", categories=cat_list)
    print(f"  ✅ / → index.html")

    # Category pages
    for cid, cat in categories.items():
        path = f"/categories/{cid}/"
        render(env.get_template("category.html"), path,
               cat_name=cat["name"], cat_id=cid, items=cat["items"])
        print(f"  ✅ {path} → index.html")

    # Software pages
    for sw in software_list:
        path = f"/{sw['slug']}/"
        render(env.get_template("software.html"), path, sw=sw)
        print(f"  ✅ {path} → index.html")

    # Copy static assets
    static_src = SRC / "static"
    if static_src.exists():
        import shutil
        shutil.copytree(static_src, DIST / "static", dirs_exist_ok=True)

    # Generate sitemap
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap.append(f"  <url><loc>https://{DOMAIN}/</loc><priority>1.0</priority></url>")
    for cid in categories:
        sitemap.append(f"  <url><loc>https://{DOMAIN}/categories/{cid}/</loc><priority>0.8</priority></url>")
    for sw in software_list:
        sitemap.append(f"  <url><loc>https://{DOMAIN}/{sw['slug']}/</loc><priority>0.7</priority></url>")
    sitemap.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")
    print(f"  ✅ sitemap.xml generated")

    # robots.txt
    robots = ["User-agent: *", "Allow: /",
              f"Sitemap: https://{DOMAIN}/sitemap.xml"]
    (DIST / "robots.txt").write_text("\n".join(robots), encoding="utf-8")
    print(f"  ✅ robots.txt generated")

    total = len(software_list) + len(categories) + 1  # +1 homepage
    print(f"\n✨ Done! {total} pages built → {DIST}")
    print(f"📦 Size: {sum(f.stat().st_size for f in DIST.rglob('*') if f.is_file()) / 1024:.0f} KB")

if __name__ == "__main__":
    build()
