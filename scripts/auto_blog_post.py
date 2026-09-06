#!/usr/bin/env python3
"""Pulls the newest plant-science story from a science-news RSS feed and
publishes it as a new blog post, entirely without an LLM -- see
scripts/run_auto_blog_post.sh for how this gets invoked on a schedule.

Content is a short, clearly-attributed summary (the RSS feed's own
description field) plus a link back to the original source -- standard,
legal RSS syndication practice, not full-article reproduction.

Keeps its own record of which items it has already posted in
blog/.rss-posted.json (committed to the repo) so it never repeats a story.
"""
import html
import json
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = SITE_ROOT / "blog"
POSTED_LOG = BLOG_DIR / ".rss-posted.json"
TEMPLATE_POST = BLOG_DIR / "why-are-my-monstera-leaves-turning-yellow.html"
INDEX_FILE = BLOG_DIR / "index.html"

# RunAtLoad on the launchd job means this script fires at every login/boot,
# not just the scheduled Mon/Thu 9am slots -- that's deliberate, so a run
# missed because the Mac was fully shut down (not just asleep) still gets
# caught up at the next startup. This cooldown stops that from causing
# multiple runs if the Mac reboots several times in the same day; it's
# comfortably shorter than the 3-4 day posting cadence so it never blocks a
# genuinely due scheduled run.
COOLDOWN = timedelta(hours=36)

FEEDS = [
    "https://www.sciencedaily.com/rss/plants_animals/botany.xml",
    "https://phys.org/rss-feed/biology-news/plants-animals/",
]

PLANT_KEYWORDS = [
    "plant", "flower", "tree", "species", "garden", "botan", "crop", "leaf",
    "leaves", "root", "forest", "seed", "pollinat", "moss", "fern", "orchid",
    "vine", "shrub", "bloom", "horticult", "photosynth", "soil", "fungi",
    "fungal", "mycorrhiz", "houseplant",
]

EXCLUDE_KEYWORDS = [
    "monkey", "chimpanzee", "human evolution", "fossil feet", "primate",
    "dinosaur", "fish", "bird", "insect behavior",
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_items(xml_text: str):
    root = ET.fromstring(xml_text)
    items = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        guid = (item.findtext("guid") or link).strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        if title and link:
            items.append({"title": title, "link": link, "description": description, "guid": guid, "pubDate": pub_date})
    return items


def is_plant_relevant(item) -> bool:
    text = (item["title"] + " " + item["description"]).lower()
    if any(bad in text for bad in EXCLUDE_KEYWORDS):
        return False
    return any(kw in text for kw in PLANT_KEYWORDS)


def load_posted_log():
    if POSTED_LOG.exists():
        return json.loads(POSTED_LOG.read_text())
    return {"posted_guids": []}


def save_posted_log(log):
    POSTED_LOG.write_text(json.dumps(log, indent=2) + "\n")


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:80].rstrip("-")


def build_post_html(item) -> tuple[str, str]:
    shell = TEMPLATE_POST.read_text()
    title = html.unescape(item["title"]).strip()
    description_raw = html.unescape(item["description"]).strip()
    slug = slugify(title)
    filename = f"{slug}.html"

    safe_title = html.escape(title)
    safe_meta_desc = html.escape(description_raw[:300])
    source_link = item["link"]

    try:
        pub_dt = datetime.strptime(item["pubDate"][:25].strip(), "%a, %d %b %Y %H:%M:%S")
        date_str = pub_dt.strftime("%B %d, %Y")
    except Exception:
        date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")

    body = f"""<main>
  <span class="eyebrow">Plant Science News</span>
  <h1>{safe_title}</h1>
  <p class="meta">Plant Doctor Team · Curated from Science News · {date_str}</p>

  <p>{html.escape(description_raw)}</p>

  <p><a href="{html.escape(source_link)}" target="_blank" rel="noopener">Read the full research coverage at the original source →</a></p>

  <div class="callout">
    <p><strong>Curious about a plant of your own?</strong> Point Plant Doctor's camera at any plant for an instant AI diagnosis and care plan, or preview how new plants would look in your own space before buying anything.</p>
    <a class="btn" href="https://play.google.com/store/apps/details?id=com.getplantdoctor.app">Scan your plant free</a>
  </div>
</main>"""

    # Replace the <title>, meta description, and the whole <main>...</main> block.
    new_html = shell
    new_html = re.sub(r"<title>.*?</title>", f"<title>{safe_title} — Plant Doctor</title>", new_html, count=1, flags=re.S)
    new_html = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{safe_meta_desc}">', new_html, count=1, flags=re.S)
    new_html = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="https://getplantdoctor.com/blog/{filename}">', new_html, count=1, flags=re.S)
    new_html = re.sub(r"<main>.*?</main>", body, new_html, count=1, flags=re.S)

    return filename, new_html


def update_index(filename: str, title: str, description: str):
    index_html = INDEX_FILE.read_text()
    excerpt = html.escape(description[:150].rsplit(" ", 1)[0] + "…")
    safe_title = html.escape(title)
    new_li = f'    <li>\n      <a class="title" href="./{filename}">{safe_title}</a>\n      <p class="excerpt">{excerpt}</p>\n    </li>\n'
    updated = index_html.replace('<ul class="post-list">\n', '<ul class="post-list">\n' + new_li, 1)
    INDEX_FILE.write_text(updated)


def git(*args):
    subprocess.run(["git", "-C", str(SITE_ROOT), *args], check=True)


def main():
    log = load_posted_log()
    posted = set(log.get("posted_guids", []))

    last_run_raw = log.get("last_run_at")
    if last_run_raw:
        try:
            last_run = datetime.fromisoformat(last_run_raw)
            elapsed = datetime.now(timezone.utc) - last_run
            if elapsed < COOLDOWN:
                print(f"Last run was {elapsed} ago (< {COOLDOWN} cooldown) -- skipping, likely a repeat login/boot today.")
                return
        except Exception:
            pass  # malformed timestamp shouldn't block a real run

    chosen = None
    for feed_url in FEEDS:
        try:
            xml_text = fetch(feed_url)
        except Exception as e:
            print(f"Could not fetch {feed_url}: {e}", file=sys.stderr)
            continue
        try:
            items = parse_items(xml_text)
        except Exception as e:
            print(f"Could not parse {feed_url}: {e}", file=sys.stderr)
            continue
        for item in items:
            if item["guid"] in posted:
                continue
            if not is_plant_relevant(item):
                continue
            chosen = item
            break
        if chosen:
            break

    if not chosen:
        print("No new plant-relevant story found this run. Nothing published.")
        log["last_run_at"] = datetime.now(timezone.utc).isoformat()
        save_posted_log(log)
        return

    filename, new_post_html = build_post_html(chosen)
    out_path = BLOG_DIR / filename
    if out_path.exists():
        print(f"Post file {filename} already exists, skipping to avoid overwrite.")
        log["last_run_at"] = datetime.now(timezone.utc).isoformat()
        save_posted_log(log)
        return

    out_path.write_text(new_post_html)
    update_index(filename, html.unescape(chosen["title"]), html.unescape(chosen["description"]))

    posted.add(chosen["guid"])
    log["posted_guids"] = sorted(posted)
    log["last_run_at"] = datetime.now(timezone.utc).isoformat()
    save_posted_log(log)

    git("add", "blog/")
    git("commit", "-m", f"Auto-post: {chosen['title']}")
    git("push", "origin", "main")
    print(f"Published: {filename}")


if __name__ == "__main__":
    main()
