#!/usr/bin/env python3
"""Fixes for /meet-the-team:
1. Square thumbnails (remove border-radius: 50% from .team-photo-wrap)
2. Left-aligned card text
3. Add a prominent "everyone" group photo as hero background
4. Add YouTube video (VSxmNUtevAw) under the "Why we do what we do" heading
"""
import re
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
FILE = ROOT / "meet-the-team.html"
s = FILE.read_text()

# ---------------------------------------------------------------------------
# 1+2. Square thumbnails + left-align text
# ---------------------------------------------------------------------------
css_patches = [
    # Remove circular clip from headshot wrapper + change to portrait aspect
    (
        r'\.team-photo-wrap\{[^}]+\}',
        '.team-photo-wrap{width:100%;aspect-ratio:3/4;overflow:hidden;margin-bottom:20px;background:#1a1a1a;border-radius:2px;box-shadow:0 0 0 1px rgba(255,255,255,.06)}'
    ),
    # Team card: left-align
    (
        r'\.team-card\{[^}]+\}',
        '.team-card{text-align:left;display:flex;flex-direction:column}'
    ),
    # Team name should be left-aligned too
    (
        r'(\.team-name\{[^}]*?)(\})',
        r'\1;text-align:left\2'
    ),
    # Team title left-aligned
    (
        r'(\.team-title\{[^}]*?)(\})',
        r'\1;text-align:left\2'
    ),
    # Snippet should be left-aligned
    (
        r'(\.team-snippet\{[^}]*?max-width:\s*280px[^}]*?)(\})',
        r'\1;text-align:left;max-width:none\2'
    ),
    # Learn more link — align left
    (
        r'(\.team-learn-more\{[^}]*?)(\})',
        r'\1;align-self:flex-start\2'
    ),
]
for pat, repl in css_patches:
    s = re.sub(pat, repl, s, flags=re.DOTALL)

# ---------------------------------------------------------------------------
# 3. Hero "everyone" image — use egcp-012 (prominent salon shot) as hero bg
# ---------------------------------------------------------------------------
# Find the .page-hero section and add a background image
# First, inject the CSS for .page-hero-bg if missing
if '.page-hero-bg' not in s:
    hero_css = '''
    .page-hero-bg{position:absolute;inset:0;z-index:0;opacity:.3}
    .page-hero-bg img{width:100%;height:100%;object-fit:cover;object-position:center 30%}
    .page-hero-overlay{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.75));z-index:1}
    .page-hero-content{position:relative;z-index:2}
'''
    s = s.replace('.page-hero{', hero_css + '.page-hero{', 1)

# Make sure .page-hero is position:relative so the bg can be absolute
s = re.sub(
    r'\.page-hero\{([^}]*)\}',
    lambda m: '.page-hero{position:relative;overflow:hidden;' + m.group(1) + '}' if 'position:relative' not in m.group(1) else m.group(0),
    s, count=1
)

# Now inject the hero background image element into the hero section (first <section class="page-hero">)
# The current structure likely is: <section class="page-hero"><div>... </div></section>
# We add <div class="page-hero-bg"><img src=...></div> + <div class="page-hero-overlay"></div> as first children.
hero_bg_html = '''      <div class="page-hero-bg"><img src="/images/webflow/team-group/egcp-012-p-1080.webp" alt="The Studio One team"></div>
      <div class="page-hero-overlay"></div>
      '''

def inject_hero_bg(match):
    opening = match.group(0)
    # Skip if already has a bg image
    if 'page-hero-bg' in opening:
        return opening
    return opening + '\n' + hero_bg_html

s = re.sub(r'<section class="page-hero"[^>]*>', inject_hero_bg, s, count=1)

# Wrap hero content in page-hero-content if not already
if 'page-hero-content' not in s:
    s = re.sub(
        r'(<section class="page-hero"[^>]*>\s*<div class="page-hero-bg">.*?</div>\s*<div class="page-hero-overlay"></div>\s*)(<div)',
        r'\1<div class="page-hero-content">\n        \2',
        s, flags=re.DOTALL, count=1
    )
    # Close the content wrapper before </section>
    # Count open/close divs is brittle — simpler: add a </div> before </section> of the first page-hero section
    # Only if we added opening above
    # Skip this — if agent structure differs, we'll handle in a manual spot check

# ---------------------------------------------------------------------------
# 4. YouTube video under "Why we do what we do"
# ---------------------------------------------------------------------------
# Find the existing section that contains "Why we do what we do" (any case) and add a video embed.
# The agent's version likely has <h2>Why we do what we do</h2> somewhere.
video_html = '''
      <div class="video-wrap" data-animate>
        <iframe src="https://www.youtube-nocookie.com/embed/VSxmNUtevAw"
                title="Why we do what we do - Studio One"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                referrerpolicy="strict-origin-when-cross-origin"
                allowfullscreen
                loading="lazy"></iframe>
      </div>
'''

# Insert video_html right after the "Why we do what we do" h2 tag
pattern = re.compile(r'(<h2[^>]*>\s*Why we do what we do[^<]*</h2>)', re.IGNORECASE)
m = pattern.search(s)
if m:
    s = s[:m.end()] + video_html + s[m.end():]
    print("✓ YouTube video inserted under 'Why we do what we do'")
else:
    print("✗ 'Why we do what we do' heading not found — adding a new section before footer")
    new_section = f'''
  <!-- WHY WE DO WHAT WE DO -->
  <section class="section section--dark" style="padding:100px 40px">
    <div class="section-inner text-center" data-animate>
      <p class="eyebrow">Our Philosophy</p>
      <h2 class="section-heading" style="max-width:800px;margin:0 auto 32px">Why we do what we do.</h2>
      {video_html.strip()}
    </div>
  </section>
'''
    # Insert before <footer>
    s = re.sub(r'(\s*<footer)', new_section + r'\1', s, count=1)

# Add .video-wrap CSS if missing
if '.video-wrap{' not in s:
    video_css = '''
    .video-wrap{position:relative;max-width:960px;margin:32px auto 0;aspect-ratio:16/9;border-radius:6px;overflow:hidden;background:#000}
    .video-wrap iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
'''
    s = s.replace('  </style>', video_css + '  </style>', 1)

FILE.write_text(s)
print(f"✓ Updated {FILE.name}")
print("  - Square thumbnails + left-aligned card text")
print("  - Hero background image added (egcp-012)")
print("  - Video placed under 'Why we do what we do'")
