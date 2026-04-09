#!/usr/bin/env python3
"""
ludora-versions.py — generates ludora-versions.html
Usage: python3 ~/ludora-versions.py
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

COPR_API = (
    "https://copr.fedorainfracloud.org/api_3/package/list"
    "?ownername=predze&projectname=ludora&with_latest_build=True"
)

# Displayed in order; kernel upstream is resolved dynamically from COPR version
CORE = [
    {
        "copr_name": "kernel-ludora",
        "label": "Kernel",
        "url": "https://www.kernel.org",
        "upstream": {"type": "kernel"},
    },
    {
        "copr_name": "mesa",
        "label": "Mesa",
        "url": "https://gitlab.freedesktop.org/mesa/mesa",
        "upstream": {"type": "arch", "pkgname": "mesa"},
    },
    {
        "copr_name": "libva",
        "label": "libva",
        "url": "https://github.com/intel/libva",
        "upstream": {"type": "github", "owner": "intel", "repo": "libva"},
    },
]

APPS = [
    {
        "copr_name": "mangohud",
        "label": "MangoHud",
        "url": "https://github.com/flightlessmango/MangoHud",
        "upstream": {"type": "github", "owner": "flightlessmango", "repo": "MangoHud"},
    },
    {
        "copr_name": "fastfetch",
        "label": "Fastfetch",
        "url": "https://github.com/fastfetch-cli/fastfetch",
        "upstream": {"type": "github", "owner": "fastfetch-cli", "repo": "fastfetch"},
    },
    {
        "copr_name": "goverlay",
        "label": "GOverlay",
        "url": "https://github.com/benjamimgois/goverlay",
        "upstream": {"type": "github", "owner": "benjamimgois", "repo": "goverlay"},
    },
    {
        "copr_name": "lact",
        "label": "LACT",
        "url": "https://github.com/ilya-zlobintsev/LACT",
        "upstream": {"type": "github", "owner": "ilya-zlobintsev", "repo": "LACT"},
    },
    {
        "copr_name": "coolercontrol",
        "label": "CoolerControl",
        "url": "https://gitlab.com/coolercontrol/coolercontrol",
        "upstream": {"type": "gitlab", "project": "coolercontrol/coolercontrol"},
    },
    {
        "copr_name": "protonplus",
        "label": "ProtonPlus",
        "url": "https://github.com/Vysp3r/ProtonPlus",
        "upstream": {"type": "github", "owner": "Vysp3r", "repo": "ProtonPlus"},
    },
]

# ── helpers ───────────────────────────────────────────────────────────────────

def fetch_json(url, headers=None):
    req = urllib.request.Request(
        url, headers={"User-Agent": "ludora-versions/1.0", **(headers or {})}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ! {url}: {e}", file=sys.stderr)
        return None


def clean_version(v):
    """Strip RPM epoch, release suffix, and leading 'v'."""
    if not v:
        return None
    if ":" in v:
        v = v.split(":", 1)[1]
    if "-" in v:
        v = v.rsplit("-", 1)[0]
    return v.lstrip("v")


def parse_version(v):
    """Parse a version string into a tuple of ints for comparison."""
    if not v:
        return ()
    parts = []
    for p in v.split("."):
        m = re.match(r"(\d+)", p)
        parts.append(int(m.group(1)) if m else 0)
    return tuple(parts)


def cmp_version(v1, v2):
    """Return -1, 0, or 1 comparing two version strings."""
    t1, t2 = parse_version(v1), parse_version(v2)
    n = max(len(t1), len(t2))
    t1 += (0,) * (n - len(t1))
    t2 += (0,) * (n - len(t2))
    return 0 if t1 == t2 else (-1 if t1 < t2 else 1)


def parse_iso(s):
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def days_ago(dt):
    if not dt:
        return None
    return (datetime.now(tz=timezone.utc) - dt).days


def fmt_date(dt):
    if not dt:
        return "unknown"
    return dt.strftime("%b %-d, %Y")


def rel_time(d):
    if d is None:
        return ""
    if d == 0:
        return "today"
    if d == 1:
        return "yesterday"
    return f"{d} days ago"


# ── upstream fetchers ─────────────────────────────────────────────────────────

def fetch_github(owner, repo):
    data = fetch_json(
        f"https://api.github.com/repos/{owner}/{repo}/releases/latest",
        headers={"Accept": "application/vnd.github.v3+json"},
    )
    if not data:
        return None, None
    return clean_version(data.get("tag_name")), parse_iso(data.get("published_at"))


def fetch_gitlab(project):
    encoded = urllib.parse.quote(project, safe="")
    data = fetch_json(
        f"https://gitlab.com/api/v4/projects/{encoded}/releases/permalink/latest"
    )
    if not data:
        return None, None
    return clean_version(data.get("tag_name")), parse_iso(
        data.get("released_at") or data.get("created_at")
    )


def fetch_arch(pkgname):
    data = fetch_json(f"https://archlinux.org/packages/search/json/?name={pkgname}")
    if not data or not data.get("results"):
        return None, None
    results = data["results"]
    pkg = next(
        (r for r in results if r.get("arch") == "x86_64" and r.get("repo") in ("extra", "core")),
        results[0],
    )
    return pkg.get("pkgver"), parse_iso(pkg.get("last_update"))


def fetch_kernel(copr_ver):
    """Find the latest stable/longterm release matching the COPR kernel branch."""
    data = fetch_json("https://www.kernel.org/releases.json")
    if not data:
        return None, None

    parts = (copr_ver or "").split(".")
    branch_prefix = f"{parts[0]}.{parts[1]}." if len(parts) >= 2 else None

    for release in data.get("releases", []):
        if release.get("moniker") not in ("stable", "longterm"):
            continue
        ver = release.get("version", "")
        if branch_prefix and ver.startswith(branch_prefix):
            isodate = release.get("released", {}).get("isodate")
            dt = (
                datetime.fromisoformat(isodate).replace(tzinfo=timezone.utc)
                if isodate else None
            )
            return ver, dt

    return None, None


def get_upstream(spec, copr_ver=None):
    t = spec["type"]
    if t == "github":
        return fetch_github(spec["owner"], spec["repo"])
    if t == "gitlab":
        return fetch_gitlab(spec["project"])
    if t == "arch":
        return fetch_arch(spec["pkgname"])
    if t == "kernel":
        return fetch_kernel(copr_ver)
    return None, None


# ── COPR ──────────────────────────────────────────────────────────────────────

def get_copr_packages():
    data = fetch_json(COPR_API)
    if not data:
        return {}
    result = {}
    for pkg in data.get("items", []):
        latest = pkg.get("builds", {}).get("latest")
        if not latest:
            continue
        result[pkg["name"]] = {
            "version": clean_version(latest.get("source_package", {}).get("version")),
            "built_at": datetime.fromtimestamp(latest["ended_on"], tz=timezone.utc)
            if latest.get("ended_on") else None,
            "state": latest.get("state", "unknown"),
        }
    return result


# ── status ────────────────────────────────────────────────────────────────────

def get_status(copr_ver, upstream_ver, upstream_days):
    if not upstream_ver or not copr_ver:
        return "unknown"
    cmp = cmp_version(copr_ver, upstream_ver)
    if cmp == 0:
        return "up-to-date"
    if cmp > 0:
        return "ahead"
    # behind
    if upstream_days is None:
        return "behind-old"
    if upstream_days <= 3:
        return "behind-new"
    if upstream_days <= 14:
        return "behind-soon"
    return "behind-old"


STATUS_ORDER = {
    "behind-old": 0,
    "behind-soon": 1,
    "behind-new": 2,
    "up-to-date": 3,
    "ahead": 4,
    "unknown": 5,
}


# ── HTML ──────────────────────────────────────────────────────────────────────

BADGE_MAP = {
    "up-to-date":  ("up-to-date",  "Up to date"),
    "ahead":       ("ahead",       "Ahead"),
    "behind-new":  ("behind-new",  "Just released"),
    "behind-soon": ("behind-soon", "Needs update"),
    "behind-old":  ("behind-old",  "Overdue"),
    "unknown":     ("unknown",     "Unknown"),
}

ARROW_MAP = {
    "up-to-date": "✓",
    "ahead":      "↑",
}


def render_card(c):
    status = c["status"]
    badge_cls, badge_text = BADGE_MAP[status]
    copr_ver = c["copr_version"] or "—"
    up_ver   = c["upstream_version"] or "—"
    failed   = c.get("copr_state") not in ("succeeded", None)
    arrow    = ARROW_MAP.get(status, "→")

    return f"""    <div class="card {status}">
      <div class="card-header">
        <a class="pkg-name" href="{c['url']}" target="_blank" rel="noopener">{c['label']}</a>
        <span class="badge {badge_cls}">{badge_text}</span>
      </div>
      <div class="versions">
        <div class="ver-block">
          <div class="ver-label">COPR</div>
          <div class="ver-value{' failed' if failed else ''}">{copr_ver}</div>
          <div class="ver-date">{fmt_date(c['copr_built_at'])}</div>
          <div class="ver-rel">{rel_time(c['copr_days'])}</div>
        </div>
        <div class="arrow {status}">{arrow}</div>
        <div class="ver-block">
          <div class="ver-label">Upstream</div>
          <div class="ver-value">{up_ver}</div>
          <div class="ver-date">{fmt_date(c['upstream_released_at'])}</div>
          <div class="ver-rel">{rel_time(c['upstream_days'])}</div>
        </div>
      </div>
    </div>"""


def render_section(title, cards):
    sorted_cards = sorted(cards, key=lambda c: STATUS_ORDER.get(c["status"], 9))
    cards_html = "\n".join(render_card(c) for c in sorted_cards)
    return f"""  <section>
    <h2 class="section-title">{title}</h2>
    <div class="grid">
{cards_html}
    </div>
  </section>"""


def build_html(core_cards, apps_cards):
    now_str = datetime.now().strftime("%B %-d, %Y at %H:%M")
    core_html = render_section("Core", core_cards)
    apps_html = render_section("Apps", apps_cards)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ludora Packages</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: #0d1117;
      color: #c9d1d9;
      min-height: 100vh;
      padding: 2.5rem 1.5rem;
    }}

    header {{
      text-align: center;
      margin-bottom: 2.5rem;
    }}

    h1 {{
      font-size: 1.6rem;
      font-weight: 700;
      color: #f0f6fc;
      letter-spacing: -0.01em;
    }}

    .generated {{
      margin-top: 0.4rem;
      font-size: 0.8rem;
      color: #484f58;
    }}

    .legend {{
      display: flex;
      justify-content: center;
      gap: 1.2rem;
      margin-top: 1rem;
      flex-wrap: wrap;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.75rem;
      color: #8b949e;
    }}

    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex-shrink: 0;
    }}

    .dot-green  {{ background: #238636; }}
    .dot-blue   {{ background: #1f6feb; }}
    .dot-yellow {{ background: #9e6a03; }}
    .dot-orange {{ background: #bd561d; }}
    .dot-red    {{ background: #b91c1c; }}

    section {{
      max-width: 1000px;
      margin: 0 auto 2.5rem;
    }}

    .section-title {{
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #484f58;
      margin-bottom: 0.85rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #21262d;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
      gap: 0.85rem;
    }}

    .card {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 10px;
      padding: 1.1rem 1.3rem;
      border-left: 3px solid;
    }}

    .card.up-to-date  {{ border-left-color: #238636; }}
    .card.ahead       {{ border-left-color: #1f6feb; }}
    .card.behind-new  {{ border-left-color: #9e6a03; }}
    .card.behind-soon {{ border-left-color: #bd561d; }}
    .card.behind-old  {{ border-left-color: #b91c1c; }}
    .card.unknown     {{ border-left-color: #30363d; }}

    .card-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1rem;
    }}

    .pkg-name {{
      font-size: 1rem;
      font-weight: 600;
      color: #f0f6fc;
      text-decoration: none;
    }}

    .pkg-name:hover {{ color: #58a6ff; text-decoration: underline; }}

    .badge {{
      font-size: 0.68rem;
      font-weight: 600;
      padding: 0.18rem 0.5rem;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      white-space: nowrap;
    }}

    .badge.up-to-date  {{ background: #0f2d1a; color: #3fb950; border: 1px solid #238636; }}
    .badge.ahead       {{ background: #0d1f3c; color: #58a6ff; border: 1px solid #1f6feb; }}
    .badge.behind-new  {{ background: #2d1f04; color: #d29922; border: 1px solid #9e6a03; }}
    .badge.behind-soon {{ background: #2d1308; color: #f0883e; border: 1px solid #bd561d; }}
    .badge.behind-old  {{ background: #2d0b0b; color: #f85149; border: 1px solid #b91c1c; }}
    .badge.unknown     {{ background: #1c2128; color: #8b949e; border: 1px solid #30363d; }}

    .versions {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}

    .ver-block {{ flex: 1; min-width: 0; }}

    .ver-label {{
      font-size: 0.65rem;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: #484f58;
      margin-bottom: 0.2rem;
    }}

    .ver-value {{
      font-family: 'SFMono-Regular', 'Fira Code', 'JetBrains Mono', monospace;
      font-size: 0.92rem;
      font-weight: 600;
      color: #e6edf3;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .ver-value.failed {{ color: #f85149; }}

    .ver-date {{
      font-size: 0.72rem;
      color: #6e7681;
      margin-top: 0.15rem;
    }}

    .ver-rel {{
      font-size: 0.68rem;
      color: #484f58;
    }}

    .arrow {{
      font-size: 1rem;
      flex-shrink: 0;
      align-self: center;
      color: #30363d;
    }}

    .arrow.up-to-date {{ color: #238636; }}
    .arrow.ahead      {{ color: #1f6feb; }}
  </style>
</head>
<body>
  <header>
    <h1>Ludora Packages</h1>
    <p class="generated">Generated {now_str}</p>
    <div class="legend">
      <span class="legend-item"><span class="legend-dot dot-green"></span>Up to date</span>
      <span class="legend-item"><span class="legend-dot dot-blue"></span>Ahead of upstream</span>
      <span class="legend-item"><span class="legend-dot dot-yellow"></span>Released ≤ 3 days ago</span>
      <span class="legend-item"><span class="legend-dot dot-orange"></span>Behind 4–14 days</span>
      <span class="legend-item"><span class="legend-dot dot-red"></span>Behind &gt; 14 days</span>
    </div>
  </header>
{core_html}
{apps_html}
</body>
</html>"""


# ── main ──────────────────────────────────────────────────────────────────────

def build_card(pkg, copr_info):
    copr_ver   = copr_info.get("version")
    copr_built = copr_info.get("built_at")

    up_ver, up_dt = get_upstream(pkg["upstream"], copr_ver=copr_ver)
    up_days   = days_ago(up_dt)
    copr_days = days_ago(copr_built)
    status    = get_status(copr_ver, up_ver, up_days)

    print(f"  {pkg['copr_name']}: copr={copr_ver}  upstream={up_ver}  [{status}]")

    return {
        "label":                pkg["label"],
        "url":                  pkg["url"],
        "copr_version":         copr_ver,
        "copr_built_at":        copr_built,
        "copr_days":            copr_days,
        "copr_state":           copr_info.get("state"),
        "upstream_version":     up_ver,
        "upstream_released_at": up_dt,
        "upstream_days":        up_days,
        "status":               status,
    }


def main():
    print("Fetching COPR packages...")
    copr = get_copr_packages()

    print("\nCore:")
    core_cards = [build_card(pkg, copr.get(pkg["copr_name"], {})) for pkg in CORE]

    print("\nApps:")
    apps_cards = [build_card(pkg, copr.get(pkg["copr_name"], {})) for pkg in APPS]

    out = os.path.join(os.path.expanduser("~"), "ludora-versions.html")
    with open(out, "w") as f:
        f.write(build_html(core_cards, apps_cards))

    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
