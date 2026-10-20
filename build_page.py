"""Rebuild index.html with the editorial layout, keeping every word of content.

Content (decisions, captions, alt text, reflection) is read from content.html,
the filled course template, so the write-up is edited in one place.
Run: .venv/bin/python build_page.py
"""

import html
import re

src = open("content.html", encoding="utf-8").read()


def sections():
    out = {}
    for side in ("FOR", "AGAINST"):
        start = src.index(f"<h3>{side} the Proposition</h3>")
        end = src.index("</section>", start)
        block = src[start:end]
        img = re.search(r'<img src="([^"]+)" alt="([^"]*)"', block)
        cap = re.search(r"<figcaption>(.*?)</figcaption>", block, re.S).group(1).strip()
        items = []
        for li in re.findall(r"<li>(.*?)</li>", block, re.S):
            m = re.match(r"\s*<strong>(.*?)\s*\(([−+\-]?[\d.]+)\)\.?</strong>\s*(.*)", li, re.S)
            title, score, body = m.group(1).strip().rstrip("."), m.group(2), m.group(3).strip()
            items.append((title, float(score.replace("−", "-")), body))
        out[side] = dict(src=img.group(1), alt=img.group(2), cap=cap, items=items)
    return out


def scale(score):
    """A -2..+2 diverging track with a marker; the number is also printed, so
    the meaning never rests on position alone."""
    pct = (score + 2) / 4 * 100
    label = f"{score:+g}".replace("-", "−")
    word = "deceptive" if score < 0 else ("earnest" if score > 0 else "neutral")
    return (
        f'<div class="scale" role="img" aria-label="Score {label} on a scale from −2 '
        f'(fully deceptive) to +2 (fully earnest)">'
        f'<span class="scale-end">−2</span>'
        f'<span class="track"><span class="mid"></span>'
        f'<span class="dot" style="left:{pct:.1f}%"></span></span>'
        f'<span class="scale-end">+2</span>'
        f'<span class="score {word}">{label} <small>{word}</small></span></div>'
    )


def side_html(key, label, kicker, data, n):
    items = "\n".join(
        f"""        <li class="decision">
          <div class="decision-head"><h4>{t}</h4>{scale(s)}</div>
          <p>{b}</p>
        </li>"""
        for t, s, b in data["items"]
    )
    return f"""    <section class="side" id="{key.lower()}" aria-labelledby="{key.lower()}-h">
      <p class="kicker">{kicker}</p>
      <h2 id="{key.lower()}-h">{label}</h2>
      <figure>
        <img src="{data['src']}" alt="{data['alt']}" width="1600" height="1120" />
        <figcaption><span class="fig-n">Figure {n}.</span> {data['cap']}</figcaption>
      </figure>
      <h3 class="decisions-h">Design decisions and rationale</h3>
      <ol class="decisions">
{items}
      </ol>
    </section>"""


s = sections()
reflection = re.search(r"<h2>Final Reflection</h2>\s*(.*?)\s*</section>", src, re.S).group(1)
proposition = re.search(r"<h2>Proposition: (.*?)</h2>", src, re.S).group(1).strip()

page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Who drives the climate crisis? · DSC 106 Project 2 · Group 37</title>
  <meta name="description" content="DSC 106 Project 2, Group 37: two persuasive visualizations of the same World Bank CO2 data, one for and one against the proposition that China, not the West, is now the main driver of the climate crisis." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:wght@500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --ink: #14171c;
      --ink-2: #3d4450;
      --muted: #5b6370;
      --rule: #dfe2e7;
      --paper: #ffffff;
      --page: #f6f5f1;
      --tint: #f1f0ec;
      --accent: #2b2f36;
      --measure: 68ch;
    }}
    *, *::before, *::after {{ box-sizing: border-box; }}
    html {{ -webkit-text-size-adjust: 100%; }}
    body {{
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font: 400 1.0625rem/1.65 "Atkinson Hyperlegible", system-ui, sans-serif;
    }}
    a {{ color: inherit; text-decoration-thickness: 1px; text-underline-offset: 0.18em; }}
    a:hover {{ text-decoration-thickness: 2px; }}
    a:focus-visible {{ outline: 3px solid var(--accent); outline-offset: 3px; border-radius: 2px; }}

    .wrap {{ max-width: 960px; margin: 0 auto; padding: 0 1.25rem; }}
    .prose {{ max-width: var(--measure); }}

    /* Masthead */
    header.masthead {{ padding: 3.5rem 0 2.25rem; }}
    .tag {{
      display: inline-block; font-size: 0.8125rem; letter-spacing: 0.08em;
      text-transform: uppercase; color: var(--muted); margin: 0 0 1rem;
    }}
    h1, h2, h3, h4 {{ font-family: "Crimson Pro", Georgia, serif; color: var(--ink); text-wrap: balance; }}
    h1 {{ font-size: clamp(2.4rem, 6.4vw, 4.25rem); line-height: 1.02; letter-spacing: -0.015em; margin: 0 0 1.25rem; font-weight: 700; }}
    .dek {{ font-size: 1.1875rem; color: var(--ink-2); margin: 0 0 1.75rem; max-width: 60ch; }}
    .byline {{ font-size: 0.9375rem; color: var(--ink-2); margin: 0; }}
    .byline span {{ white-space: nowrap; }}
    .byline em {{ font-style: normal; color: var(--muted); }}

    /* Proposition */
    .proposition {{
      margin: 2.25rem 0 0; padding: 1.5rem 0 0; border-top: 2px solid var(--ink);
    }}
    .proposition p.label {{ font-size: 0.8125rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin: 0 0 0.5rem; }}
    .proposition blockquote {{
      margin: 0; font-family: "Crimson Pro", Georgia, serif; font-weight: 600;
      font-size: clamp(1.6rem, 3.6vw, 2.3rem); line-height: 1.15;
    }}
    .meta {{ font-size: 0.9375rem; color: var(--muted); margin: 1rem 0 0; }}

    /* Sides */
    main {{ background: var(--paper); border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }}
    .side {{ padding: 3rem 0 2.5rem; border-bottom: 1px solid var(--rule); }}
    .side:last-of-type {{ border-bottom: 0; }}
    .kicker {{
      display: inline-block; margin: 0 0 0.5rem; padding: 0.15rem 0.6rem;
      font-size: 0.8125rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
      color: var(--paper); background: var(--ink); border-radius: 2px;
    }}
    .side h2 {{ font-size: clamp(1.6rem, 3.4vw, 2.1rem); line-height: 1.1; margin: 0 0 1.5rem; }}

    figure {{ margin: 0 0 2rem; }}
    figure img {{
      display: block; width: 100%; height: auto; background: var(--paper);
      border: 1px solid var(--rule); border-radius: 4px;
    }}
    figcaption {{ margin-top: 0.75rem; font-size: 0.9375rem; color: var(--ink-2); max-width: var(--measure); }}
    .fig-n {{ font-weight: 700; color: var(--ink); }}

    .decisions-h {{ font-size: 1.375rem; margin: 0 0 1rem; }}
    ol.decisions {{ list-style: none; margin: 0; padding: 0; counter-reset: d; }}
    .decision {{
      counter-increment: d; padding: 1.25rem 0; border-top: 1px solid var(--rule);
    }}
    .decision-head {{ display: grid; grid-template-columns: 1fr auto; gap: 0.75rem 1.5rem; align-items: start; }}
    .decision h4 {{ font-size: 1.25rem; line-height: 1.2; margin: 0; }}
    .decision h4::before {{ content: counter(d) ". "; color: var(--muted); }}
    .decision p {{ margin: 0.6rem 0 0; max-width: var(--measure); color: var(--ink-2); }}

    /* -2..+2 diverging scale, monochrome so it never reads as the charts' red or blue */
    .scale {{ display: flex; align-items: center; gap: 0.45rem; font-size: 0.8125rem; color: var(--muted); white-space: nowrap; }}
    .track {{ position: relative; width: 112px; height: 6px; background: linear-gradient(90deg, #9aa0a8, #e3e5e8 50%, #9aa0a8); border-radius: 3px; }}
    .track .mid {{ position: absolute; left: 50%; top: -4px; width: 1px; height: 14px; background: var(--muted); }}
    .track .dot {{
      position: absolute; top: 50%; width: 14px; height: 14px; margin: -7px 0 0 -7px;
      border-radius: 50%; background: var(--ink); border: 2px solid var(--paper);
      box-shadow: 0 0 0 1px var(--ink);
    }}
    .score {{ font-weight: 700; color: var(--ink); min-width: 6.5em; }}
    .score small {{ font-weight: 400; color: var(--muted); font-size: 1em; }}

    /* Reflection */
    .reflection {{ padding: 3rem 0 3.5rem; }}
    .reflection h2 {{ font-size: clamp(1.6rem, 3.4vw, 2.1rem); margin: 0 0 1.25rem; }}
    .reflection p {{ margin: 0 0 1.1rem; }}
    .reflection p:first-of-type::first-letter {{
      font-family: "Crimson Pro", Georgia, serif; float: left; font-size: 3.4em; line-height: 0.85;
      padding: 0.08em 0.08em 0 0; font-weight: 700;
    }}

    footer {{ padding: 2rem 0 3rem; font-size: 0.875rem; color: var(--muted); }}
    footer p {{ margin: 0 0 0.4rem; max-width: var(--measure); }}

    @media (max-width: 640px) {{
      body {{ font-size: 1rem; }}
      header.masthead {{ padding-top: 2.25rem; }}
      .decision-head {{ grid-template-columns: 1fr; }}
      .byline span {{ white-space: normal; }}
    }}
    @media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto !important; transition: none !important; }} }}
    @media print {{ body {{ background: #fff; }} main {{ border: 0; }} .side {{ break-inside: avoid-page; }} }}
  </style>
</head>
<body>
  <header class="masthead">
    <div class="wrap">
      <p class="tag">DSC 106 · Project 2 · Persuasive or deceptive visualization?</p>
      <h1>Same data, opposite verdicts</h1>
      <p class="dek">Two charts built from one World Bank series. One argues China now drives the climate crisis; the other argues the United States does. Every number on both is correct.</p>
      <p class="byline"><strong>Group 37</strong> ·
        <span>Aryen Palkar <em>apalkar@ucsd.edu</em></span> ·
        <span>Haoyu Lin <em>hal150@ucsd.edu</em></span> ·
        <span>Jayden Liauw <em>jliauw@ucsd.edu</em></span></p>
      <div class="proposition">
        <p class="label">Proposition</p>
        <blockquote>{proposition}</blockquote>
        <p class="meta">Dataset: World Bank climate-change indicators (CO<sub>2</sub> emissions in kilotonnes and per capita), 1960–2018, from the cleaned course repository. Scores run from −2 (fully deceptive) to +2 (fully earnest).</p>
      </div>
    </div>
  </header>

  <main>
    <div class="wrap">
{side_html("FOR", "For the proposition", "Argues it’s true", s["FOR"], 1)}
{side_html("AGAINST", "Against the proposition", "Argues it’s false", s["AGAINST"], 2)}
    </div>
  </main>

  <section class="reflection" aria-labelledby="refl-h">
    <div class="wrap prose">
      <h2 id="refl-h">Final reflection</h2>
      {reflection}
    </div>
  </section>

  <footer>
    <div class="wrap">
      <p>Source: World Bank, World Development Indicators, climate-change indicators, via
        <a href="https://github.com/light-and-salt/World-Bank-Data-by-Indicators">light-and-salt/World-Bank-Data-by-Indicators</a>.
        Charts are regenerated from the data by <a href="https://github.com/AryenP/dsc106-project2/blob/main/make_viz.py">make_viz.py</a>.</p>
      <p>DSC 106, Fall 2026, UC San Diego.</p>
    </div>
  </footer>
</body>
</html>
"""

for bad in ("RATIONALE_", "IMAGE_FILENAME", "[WRITE", "[STATE"):
    assert bad not in page, bad
n_items = sum(len(v["items"]) for v in s.values())
assert n_items == 10, n_items
open("index.html", "w", encoding="utf-8").write(page)
print(f"index.html: {len(page):,} bytes, {n_items} decisions, scores:",
      [x[1] for v in s.values() for x in v["items"]])
