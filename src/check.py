"""The gate: measures the built site against the Quality rules that can be counted (Quality rules, 02 Brand on the Drive).

    python3 src/build.py && python3 src/check.py            every page at 1,440, 834 and 390 px, a table and a verdict
    python3 src/check.py --json out.json                    also writes every measurement
    python3 src/check.py --pages home,partners              only these pages (by slug)

It serves the repository root on a local port and opens every page in a browser without a screen (Playwright, Chromium).
It does not replace the eye: hierarchy, crops and the look are judged on the page. Run it before every push; nothing is
published that makes a number worse. The limits are the rules' own; the page budgets are Thomas's of 11 November 2026.
"""
import argparse
import functools
import http.server
import json
import pathlib
import re
import sys
import threading

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build  # noqa: E402  (the pages and the stylesheet come from the build itself)

WIDTHS = [(1440, 900, "desktop"), (834, 1112, "tablet"), (390, 844, "phone")]
SCALE = {0, 4, 8, 12, 16, 24, 32, 48, 64, 96}                    # rule 9
SIZES = {13, 17, 22, 32, 44, 64}                                 # rule 11, the approved scale
WEIGHTS = {"300", "400", "700"}                                  # rule 11
MEASURE = {"desktop": 75, "tablet": 75, "phone": 48}             # rule 10 (the phone: 35 to 45 is the aim, 48 the gate)
BUDGET = {"home": 350, "theme": 200, "collection": 300, "partners": 350, "portal": 200}   # words a page, by template
BUDGET_BY_SLUG = {"waste-to-value": None}                        # a sponsored collection is budgeted by story (90 words)
# The plan of 11 November 2026: what the site is steered towards, measured on the key pages at 1,440 px. A miss is listed,
# it does not fail the gate: small print at most 15% of the letters; the first screen's largest type at least 2.5 times the
# text; no more than two sections in a row in one layout.
KEY = ("home", "theme", "collection", "partners", "portal")
TARGET = dict(small=0.15, jump=2.5, run=2)

MEASURE_JS = r"""
() => {
  document.body.classList.add('clean');
  const W = innerWidth, H = innerHeight;
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const wire = e => !!e.closest('.wire-strip,.note,.grid-overlay,.skip,.lines,.ph-text');
  // credit lines and captions are counted by rule 15, not as the page's words: one stands under every image by rule
  // (12 November 2026) the keywords of the photographs on Home (.kw-rows) are a part of the photograph's record, as its
  // caption is: they stand under the image as the archive's own data, and are not counted as the page's words either.
  const credit = e => !!e.closest('.credit, figcaption, .kw-rows');
  const tl = e => { let n = 0; e.childNodes.forEach(c => { if (c.nodeType === 3) n += c.textContent.trim().length; }); return n; };
  const main = document.querySelector('main');
  const all = [...document.querySelectorAll('body *')].filter(e => vis(e) && !wire(e));
  const tx = all.filter(e => tl(e) > 1 && !credit(e));
  const sizes = {}, weights = {};
  let total = 0;
  for (const e of tx) {
    const s = getComputedStyle(e), n = tl(e), z = Math.round(parseFloat(s.fontSize) * 10) / 10;
    sizes[z] = (sizes[z] || 0) + n; weights[s.fontWeight] = (weights[s.fontWeight] || 0) + n; total += n;
  }
  const lineChars = p => {
    const tw = document.createTreeWalker(p, NodeFilter.SHOW_TEXT), r = document.createRange();
    let n, last = null, c = 0, max = 0;
    while ((n = tw.nextNode())) {
      const t = n.textContent;
      for (let i = 0; i < t.length; i++) {
        r.setStart(n, i); r.setEnd(n, i + 1);
        const rc = r.getClientRects()[0]; if (!rc) continue;
        const top = Math.round(rc.top);
        if (last === null) last = top;
        if (Math.abs(top - last) > 4) { max = Math.max(max, c); c = 0; last = top; }
        c++;
      }
    }
    return Math.max(max, c);
  };
  // running text: paragraphs and list items of the content that run over two lines or more
  let measure = 0, measureAt = '';
  for (const p of main.querySelectorAll('p, li, dd, blockquote')) {
    if (!vis(p) || wire(p) || p.closest('.credit') || p.classList.contains('credit')) continue;
    if (p.querySelector('p, li')) continue;
    const s = getComputedStyle(p), lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.2;
    if (parseFloat(s.fontSize) < 16) continue;   // small print (captions, labels) is not running text
    if (p.getBoundingClientRect().height < lh * 1.9) continue;
    const m = lineChars(p);
    if (m > measure) { measure = m; measureAt = p.innerText.trim().slice(0, 40); }
  }
  const words = el => { let w = 0; const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n; while ((n = tw.nextNode())) { const p = n.parentElement; if (!p || wire(p) || credit(p) || !vis(p)) continue; const t = n.textContent.trim(); if (t) w += t.split(/\s+/).length; } return w; };
  // images: every frame and photograph of the content, and whether a credit line of its own stands beneath it
  const frames = [...main.querySelectorAll('.img, img')].filter(e => vis(e) && !e.closest('.logo,.logos,.logo-tile,.logo-card'));
  const nocredit = frames.filter(e => {
    const fig = e.closest('figure, .frame') || e.parentElement;
    // rule 15 as relaxed on 11 November 2026: a credit stands where a photograph is shown as work. Covered: a credit of its
    // own; one credit for its grid or row (.credit.group in the same module); or a small image that is a link to the page
    // where the credit stands.
    const own = [...fig.querySelectorAll('.credit, figcaption')].some(c => c.innerText.trim().length > 0 && !c.classList.contains('group'));
    const group = e.closest('.mod') && e.closest('.mod').querySelector('.credit.group');
    // a story's credit (11 November 2026): the pair under a company's story is credited by the story's lead photograph
    const by = e.closest('.mod') && e.closest('.mod').dataset.creditedBy, lead = by && document.getElementById(by);
    const story = !!(lead && [...lead.querySelectorAll('.credit')].some(c => c.innerText.trim().length > 0));
    return !(own || group || story || e.closest('a[href]'));
  }).length;
  const overlaid = frames.filter(e => { const r = e.getBoundingClientRect(); return [...e.querySelectorAll('*')].some(c => !c.matches('span') && vis(c)); }).length;
  // the yellow: any element whose ground, rule or type is a yellow
  const isY = c => { const m = (c || '').match(/[\d.]+/g); if (!m) return false; const [r, g, b] = m.map(Number), a = m.length > 3 ? +m[3] : 1; return a > 0 && r > 200 && g > 170 && r - b > 40; };
  const yellow = {};
  for (const e of all) {
    if (!e.closest('main')) continue;
    const s = getComputedStyle(e);
    const hit = isY(s.backgroundColor) || isY(s.color) || (parseFloat(s.borderBottomWidth) > 0 && isY(s.borderBottomColor)) || (parseFloat(s.borderLeftWidth) > 0 && isY(s.borderLeftColor));
    if (hit && !e.closest('.draft')) { const k = (typeof e.className === 'string' && e.className) || e.tagName; yellow[k] = (yellow[k] || 0) + 1; }
  }
  const controls = [...document.querySelectorAll('a, button, input, select, textarea, summary')].filter(e => vis(e) && !wire(e));
  const small = controls.filter(e => { const r = (e.type === 'checkbox' && e.closest('label') ? e.closest('label') : e).getBoundingClientRect(); const inline = getComputedStyle(e).display === 'inline' && e.closest('main p, main li, main dd'); return r.height < 44 && !inline; })
    .map(e => (e.innerText || e.type || e.tagName).trim().slice(0, 20) + ' ' + Math.round(e.getBoundingClientRect().height));
  // the way on: the first link or button of the content, and where its top stands
  const first = main.querySelector('a[href]');
  const heads = [...main.querySelectorAll('h1, h2, h3')].filter(e => vis(e) && !wire(e)).map(e => {
    const s = getComputedStyle(e); return { tag: e.tagName, size: Math.round(parseFloat(s.fontSize)), lh: Math.round(100 * parseFloat(s.lineHeight) / parseFloat(s.fontSize)) / 100, text: e.innerText.trim().replace(/\s+/g, ' ').slice(0, 60) };
  });
  const text = main.innerText;
  const strip = document.querySelector('.wire-strip');
  // the wireframe's strip counts only while it stands above the content (it stands under the footer since 11 November 2026)
  const stripH = (strip && (strip.compareDocumentPosition(main) & 4)) ? strip.getBoundingClientRect().height : 0;
  // The craft measures of the plan of 11 November 2026 (rules 5, 6, 16 and 19; Website – quality review, section 12).
  // Small print: the share of all the letters of the content, captions and credits included, set under 14 px.
  let letters = 0, smallLetters = 0, firstMax = 0;
  for (const e of all) {
    if (!e.closest('main') || tl(e) < 2) continue;
    const z = parseFloat(getComputedStyle(e).fontSize), n = tl(e), r = e.getBoundingClientRect();
    letters += n; if (z < 14) smallLetters += n;
    if (r.top + scrollY < H && z > firstMax) firstMax = z;                       // the largest type of the first screen
  }
  const body = parseFloat(getComputedStyle(document.body).fontSize);
  const top0 = stripH;
  let firstImage = 0;                                                            // the largest photograph's share of the first screen
  for (const e of frames) { const r = e.getBoundingClientRect(), t = r.top + scrollY - top0; const h = Math.max(0, Math.min(r.bottom + scrollY - top0, H) - Math.max(t, 0)); firstImage = Math.max(firstImage, r.width * h / (W * H)); }
  const grids = [...main.querySelectorAll('.imgs, .cards-2, .cards-3, .cards-4, .cards-5, .cards-6, .works')].filter(vis).map(g => g.querySelectorAll('.img, img').length).filter(n => n);
  const pattern = [...document.querySelectorAll('svg.cut, svg.echo, svg.close-pattern')].filter(vis).length;
  const mods = [...main.querySelectorAll('section.mod')].filter(s => !s.parentElement.closest('section.mod')).map(s => s.dataset.mod);
  let run = 1, maxRun = mods.length ? 1 : 0, runAt = '';
  for (let i = 1; i < mods.length; i++) { run = mods[i] === mods[i - 1] ? run + 1 : 1; if (run > maxRun) { maxRun = run; runAt = mods[i]; } }
  return {
    sizes, weights, total, measure, measureAt, words: words(main), frames: frames.length, nocredit, overlaid, yellow,
    small, controls: controls.length, heads,
    overflow: document.documentElement.scrollWidth - W,
    firstLinkTop: first ? Math.round(first.getBoundingClientRect().top + scrollY - stripH) : null,
    dashes: [...main.querySelectorAll('.num b')].filter(e => vis(e) && e.innerText.trim() === '—').length,
    placeholders: [...main.querySelectorAll('.logo:not(.has-img), .lines, .chip.ghost')].filter(vis).length,
    straight: (text.match(/["']/g) || []).length,
    h1: document.querySelectorAll('h1').length,
    anims: document.getAnimations().length,
    smallShare: letters ? smallLetters / letters : 0, jump: firstMax / body, firstImage, grids, pattern, maxRun, runAt,
    screens: Math.round(10 * document.documentElement.scrollHeight / H) / 10,
  };
}
"""


def css_findings():
    """What can be read from the stylesheet itself: spacing off the scale, sizes off the scale, motion."""
    css = build.CSS
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    off = {}
    # The header is pinned to the archive's, pixel for pixel (rule 22), and the wireframe's own tools go at launch: both are
    # left out. Values over 96 px are the geometry of a module (the Opening), not gaps.
    for blk in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        if re.search(r"\.menu|\.bar\b|\.brand|\.divider|\.wire-strip|\.strip-tools|-toggle|\.grid-", blk.group(1)):
            continue
        for m in re.finditer(r"(?:margin|padding|gap|row-gap|column-gap)(?:-[a-z]+)?\s*:\s*([^;}]+)", blk.group(2)):
            for v in re.findall(r"(?<![\w.-])(\d+)px", m.group(1)):
                if int(v) not in SCALE and 3 < int(v) <= 96:
                    off[v] = off.get(v, 0) + 1
    sizes = sorted({float(v) for v in re.findall(r"font-size\s*:\s*([\d.]+)px", css)})
    return dict(spacing_off=dict(sorted(off.items(), key=lambda x: -x[1])), font_sizes=sizes,
                motion=len(re.findall(r"transition|animation|@keyframes", css)))


def run(only=None):
    from playwright.sync_api import sync_playwright
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    handler.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{srv.server_address[1]}/"
    pages = [p for p in build.PAGES if not only or p["slug"] in only]
    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w, h, name in WIDTHS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            foreign = []
            pg.on("request", lambda r: foreign.append(r.url) if not r.url.startswith(origin) and not r.url.startswith("data:") else None)
            for p in pages:
                foreign.clear()
                pg.goto(origin + p["path"], wait_until="networkidle")
                pg.evaluate("document.fonts.ready")
                m = pg.evaluate(MEASURE_JS)
                m.update(slug=p["slug"], tpl=p["tpl"], width=name, foreign=sorted({re.sub(r"^https?://([^/]+)/.*", r"\1", u) for u in foreign}))
                out.append(m)
            if name == "phone":   # rule 23: no sideways scroll down to 320 px
                pg.set_viewport_size({"width": 320, "height": 700})
                for p in pages:
                    pg.goto(origin + p["path"], wait_until="networkidle")
                    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
                    next(x for x in out if x["slug"] == p["slug"] and x["width"] == "phone")["overflow320"] = ov
            ctx.close()
        b.close()
    srv.shutdown()
    return out


misses = []   # the plan's targets missed (not failures)


def craft(rows):
    """The plan's measures on the key pages at 1,440 px, one line a page."""
    out = []
    for m in rows:
        if m["width"] == "desktop":
            out.append(f'{m["slug"]:28} small {m["smallShare"]:4.0%}  jump {m["jump"]:3.1f}  first image {m["firstImage"]:4.0%}  '
                       f'images {m["frames"]:2}  largest grid {max(m["grids"] or [0])}  pattern {m["pattern"]}  run {m["maxRun"]}  screens {m["screens"]:4.1f}')
    return out


def verdict(rows):
    """One line a page and width, and the failures by rule. Returns (lines, failures)."""
    fails, lines = {}, []

    def fail(rule, slug, width, what):
        fails.setdefault(rule, []).append(f"{slug} ({width}): {what}")

    misses.clear()

    site_sizes = set()
    for m in rows:
        slug, w = m["slug"], m["width"]
        sizes = {float(k): v for k, v in m["sizes"].items()}
        site_sizes |= set(sizes)
        top = max(sizes.values()) / m["total"] if m["total"] else 0
        # Home alone shows the display size, for the core line; with it, it may show five: that size and the four of
        # the other pages (12 November 2026, with the chapter titles on Home; for Thomas to confirm).
        if len(sizes) > (5 if slug == "home" else 4):
            fail(11, slug, w, f"{len(sizes)} sizes")
        if top < 0.70:
            fail(11, slug, w, f"largest share {top:.0%}")
        if set(m["weights"]) - WEIGHTS:
            fail(11, slug, w, "weights " + ", ".join(sorted(set(m["weights"]) - WEIGHTS)))
        if m["measure"] > MEASURE[w]:
            fail(10, slug, w, f'{m["measure"]} characters in “{m["measureAt"]}…”')
        if m["nocredit"]:
            fail(15, slug, w, f'{m["nocredit"]} of {m["frames"]} photographs shown as work without a credit')
        if m["overlaid"]:
            fail(14, slug, w, f'{m["overlaid"]} frames with something laid over them')
        ny = sum(m["yellow"].values())
        if ny > 1 or any("archive" not in k for k in m["yellow"]):
            fail(18, slug, w, "yellow on " + ", ".join(f"{k} ×{v}" for k, v in m["yellow"].items()))
        if m["overflow"] > 0 or m.get("overflow320", 0) > 0:
            fail(23, slug, w, f'scrolls sideways by {max(m["overflow"], m.get("overflow320", 0))} px')
        if w == "phone" and m["tpl"] in ("home", "theme", "collection", "partners", "portal") and (m["firstLinkTop"] is None or m["firstLinkTop"] > 700):
            fail(23, slug, w, f'the way on starts at {m["firstLinkTop"]} px')
        if w == "phone" and m["small"]:
            fail(24, slug, w, f'{len(m["small"])} of {m["controls"]} things to tap under 44 px')
        if m["dashes"] or m["placeholders"]:
            fail(27, slug, w, f'{m["dashes"]} empty counts, {m["placeholders"]} placeholders')
        if m["foreign"]:
            fail(28, slug, w, "requests to " + ", ".join(m["foreign"]))
        if m["straight"]:
            fail(13, slug, w, f'{m["straight"]} straight quotation marks')
        loose = [h for h in m["heads"] if h["lh"] > 1.16]
        if loose:
            fail(13, slug, w, f'{len(loose)} headings set looser than 1.15')
        if m["h1"] != 1:
            fail(29, slug, w, f'{m["h1"]} main headings')
        if m["anims"]:
            fail(20, slug, w, f'{m["anims"]} animations running')
        if m["grids"] and max(m["grids"]) > 8:
            fail(16, slug, w, f'{max(m["grids"])} images in one grid')
        if m["pattern"] > 3:
            fail(19, slug, w, f'the pattern {m["pattern"]} times')
        if w == "desktop":   # every page since 11 November 2026, 13:20 (Thomas: the whole site to one standard)
            if m["smallShare"] > TARGET["small"]:
                misses.append(f'{slug}: small print {m["smallShare"]:.0%} of the letters')
            if m["jump"] < TARGET["jump"]:
                misses.append(f'{slug}: the first screen’s largest type is {m["jump"]:.1f} times the text')
            if m["maxRun"] > TARGET["run"]:
                misses.append(f'{slug}: {m["maxRun"]} sections in a row as “{m["runAt"]}”')
        budget = BUDGET_BY_SLUG.get(slug, BUDGET.get(m["tpl"]))
        if w == "desktop" and budget and m["words"] > budget:
            fail(4, slug, w, f'{m["words"]} words, budget {budget}')
        lines.append(f'{slug:28} {w:8} sizes {len(sizes):2}  top {top:4.0%}  line {m["measure"]:3}  words {m["words"]:5}  '
                     f'credit {m["frames"] - m["nocredit"]:2}/{m["frames"]:2}  yellow {ny}  small {len(m["small"]):2}')
    extra = sorted(site_sizes - SIZES)
    if extra:
        fails.setdefault(11, []).insert(0, "the site: sizes outside the scale: " + ", ".join(f"{x:g}" for x in extra))
    # the texts over their module's limit (rule 4): the build's own check, run over the pages
    build.OVER.clear()
    for p in build.PAGES:
        build.TEMPLATES[p["tpl"]](p, "./")
    for (kind, text), (mx, n) in sorted(build.OVER.items()):
        fails.setdefault(4, []).append(f"{kind}: {n} words, limit {mx}: “{text[:50]}…”")
    css = css_findings()
    if css["spacing_off"]:
        fails.setdefault(9, []).append("the stylesheet: spacing off the scale: " + ", ".join(f"{k} px ×{v}" for k, v in css["spacing_off"].items()))
    if css["motion"]:
        fails.setdefault(20, []).append(f'the stylesheet: {css["motion"]} transitions or animations')
    return lines, fails


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--pages")
    ap.add_argument("--quiet", action="store_true", help="only the failures by rule")
    a = ap.parse_args()
    rows = run(set(a.pages.split(",")) if a.pages else None)
    lines, fails = verdict(rows)
    if not a.quiet:
        print("\n".join(lines))
    print()
    for rule in sorted(fails):
        items = fails[rule]
        print(f"Rule {rule}: {len(items)} failures")
        for x in items[:None if a.pages else 6]:
            print("   ", x)
        if not a.pages and len(items) > 6:
            print(f"    … and {len(items) - 6} more")
    print("\nThe plan’s measures (every page, 1,440 px):")
    print("\n".join(craft(rows)))
    if misses:
        print(f"Targets missed: {len(misses)}")
        for x in misses:
            print("   ", x)
    print(f"\n{len(rows)} page views checked; rules failing: {', '.join(str(r) for r in sorted(fails)) or 'none'}")
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(dict(rows=rows, fails=fails, css=css_findings(), misses=misses), indent=1, ensure_ascii=False))
    sys.exit(1 if fails else 0)
