#!/usr/bin/env python3
"""Generate the Africa Reframed main site as a live wireframe (version 4, 6 November 2026: arranged by the page priorities).

Structure from "Website – Site map and user flows" (05 Website on the Drive): 16 pages from 9 templates.
Header: Themes · Collections · Partners · About | Log in (Log in opens the Partner portal; About moved up from the footer, Thomas, 9 November 2026); the archive adds its own
tools on its side, Browse images · Lightbox, and this site shows them too to a partner it remembers (PARTNER_SCRIPT, 10 November 2026). Footer: the about line, then About · Press · Contact · Privacy · Request access · Terms.

Wireframe conventions: grey boxes with a cross are images still to choose, at the size and proportion they will
have; grey bars are text still to write; yellow notes say what goes there. Real words appear only where they
already exist in the master documents (each carries its source in a comment). "Clean view" in the strip under
the header hides the notes.
Run: python3 src/build.py  (writes the pages and assets/ into the repository root)
"""
import html
import math
import pathlib
import re
import shutil
import subprocess
import time
from urllib.parse import quote, urlparse

ROOT = pathlib.Path(__file__).parent.parent
ARCHIVE = "https://archive.africareframed.com"
SITE_URL = "https://africareframed.github.io/africareframed-site/"   # becomes https://africareframed.com/ at launch
STAMP = time.strftime("%Y%m%d%H%M")
# Launch switch. False while the site is in development: every page is noindex, carries the wireframe strip,
# and /dev/ is generated. True at launch: /dev/ is removed and the strip and noindex go.
LAUNCH = False
e = html.escape

# ---------------------------------------------------------------------------------------------
# Content that already exists (with sources)
# ---------------------------------------------------------------------------------------------
CORE_LINE = "Visual storytelling for a new partnership between Europe and Africa."          # Strategic Platform, Brand and language
ABOUT_LINE = ("Spotlighting African innovation and African–European collaboration. "
              "An independent initiative established by Commerce & Culture.")             # Strategic Platform, Brand and language
NUMBERS = [("1,122", "images"), ("3", "countries")]   # the number of themes is not a fixed fact (Thomas, 11 November 2026)                        # Website brief, Home; AR Metadata, 2 Nov 2026
# The momentum numbers (engine brief, section 5; Thomas, 8 November 2026): a download is a licence for one stated use, so
# downloads and uses are one count. Uses by kind: the eight licence categories (AR Archive – Status, the pricing profile),
# generated at every download in PhotoDeck, so the numbers are ours and tell where the images go.
MOMENTUM = [("—", "partners"), ("—", "uses")]
# Partner types: from the Request access form (type of organisation); aggregates, so shown before any partner is named.
PARTNER_TYPES = ["NGOs", "media", "educational institutions", "embassies and ministries", "development finance institutions", "companies"]
PARTNER_WHERE = ["Denmark", "the Nordics", "the EU", "Africa", "elsewhere"]   # from the form's Country field; an aggregate
# Threshold rule (Thomas, 8 November 2026): an evidence row goes live only above a threshold he sets (for example ten uses,
# five partners); below it the row is left out, as the "only what exists" rule says. The same records feed each sponsor's
# report for its own collection (uses by kind, partner types, countries, over time): part of what the sponsorship buys.
USE_KINDS = ["report or publication", "grant or funding application", "presentation or internal use", "website or social media",
             "press and editorial", "exhibition or event", "education or training material", "other use"]
EMAIL_MAIN, EMAIL_PRESS, EMAIL_PARTNERS = ("hello@africareframed.com", "press@africareframed.com",
                                           "partnerships@africareframed.com")                 # Start here, Addresses
HOUSE_LINE = "Africa Reframed’s own collection: 1,122 images from Mali, Kenya and The Gambia."
# Draft, 11 November 2026: the Keywording Guide's statement (section 2) ran to 27 words against the limit of 25; the range of
# IDs stays in the facts. The master's wording: "Africa Reframed’s own collection: 1,122 images, AR‑1000 to AR‑2121, made in
# own productions in connection with photography workshops with local partners in Mali, Kenya and The Gambia."
HOUSE_STATEMENT = ("Africa Reframed’s own collection: 1,122 images made in our own productions, alongside photography "
                   "workshops in Mali, Kenya and The Gambia.")
HOUSE_FACTS = [("Images", "1,122"), ("IDs", "AR-1000 to AR-2121"), ("Countries", "Mali, Kenya, The Gambia"),
               ("Shot", "2013–2018"), ("Shoots", "21")]                                                 # AR Shoot list
GAMBIA_SERIES = ["Culinary training, Banjul", "Women in trades, Banjul"]                                # Keywording Guide, section 9

# The five public themes in story order: Keywording Guide v2.5, section 8b. Counts from the AR Metadata sheet, 2 Nov 2026.
# "query" is an interim archive search until each theme has its own keyword (Keywording Guide 8b, tagging).
THEMES = [
    dict(slug="learning", name="Learning", count=198, query="education",
         statement="Classrooms, campuses, training kitchens and homework at home: people of every age building skills for the work ahead."),
    dict(slug="work-and-enterprise", name="Work and enterprise", count=279, query="skills and jobs",
         statement="Tradespeople, cooks, farmers, shopkeepers and young professionals making a living with skill."),
    dict(slug="everyday-digital", name="Everyday digital", count=354, query="everyday technology",
         statement="Phones, laptops and money on a screen: work, study and keeping in touch as a normal part of the day."),   # 20 words since 11 November 2026 (the Keywording Guide, 8b, changed with it)
    dict(slug="city-life", name="City life", count=237, query="urban life",
         statement="Cafés, campuses, rooftops and busy streets: the everyday rhythm of Bamako, Banjul and Nairobi."),
    dict(slug="creativity-and-culture", name="Creativity and culture", count=137, query="creativity and culture",
         statement="Portraits, style and street art."),
]
# The themes grow with the collections (Thomas, 11 November 2026, 14:57): these five are what the House Collection delivers
# today, and more will come, so nothing on the site presents them as a closed set. No "coming soon" either: the wording
# says where the themes come from. Until 15:00 that day: "In order, the five themes are the archive’s argument: …".
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
THEMES_SOURCE = ["Themes come from collections",   # the Themes page's closing section, a draft
                 "These five are drawn from the House Collection. Each new collection can bring a theme of its own."]
THEMES_LEAD = ("These five themes come from the House Collection: people learn, put their skills to work, "
               "live connected lives in modern cities, and make culture.")                            # Keywording Guide, 8b

# Who gets access: AR Archive – Status, "Who gets access, and sponsors" (Thomas, 3 Nov 2026)
ACCESS_WHO = ("The archive is free for selected non-profit and public partners: NGOs, media, educational institutions, "
              "embassies, ministries and development finance institutions.")
ACCESS_COMPANIES = ("Companies get access through a collection sponsorship: a sponsor gets the whole archive, "
                    "under the same partner licence as everyone else.")
PUBLIC_SAMPLE = "Public-sample rule: released images, no minors."
NOT_FOUND_LINE = "The address may have changed. The menu above leads to the themes, the collections and the pages for partners."   # draft


# ---------------------------------------------------------------------------------------------
# Only what exists (Quality rules, rule 27; page priorities, "for all five pages"). A module whose data does not exist yet
# is not built: no dash for a number, no empty grid, no placeholder logo, no "coming soon". The data lives here; when the
# closed preview brings the first real numbers, partners and uses, they are entered here and their modules appear.
# /dev/modules still shows every module with placeholders (SHOW_EMPTY is switched on while that page is built).
# ---------------------------------------------------------------------------------------------
SHOW_EMPTY = False
PARTNERS_NAMED = []   # partners and sponsors by name, each with consent on file
USES = []             # reported uses, each with its partner, kind, month and consent
NEWS = []             # news for partners
THEME_SPONSORS = {}   # theme slug -> sponsor, once a sponsor has funded the theme


def exists(values):
    """True when every number in a row is real."""
    return bool(values) and all(n != "—" for n, _ in values)


# ---------------------------------------------------------------------------------------------
# Text length (Quality rules, rules 4 and 10; Thomas, 11 November 2026: "very important"). Every module knows its limit in
# words, from Website – modules. A text over its limit is listed on /dev/ and fails the gate (src/check.py), so a text that
# is too long cannot slip in. The page budgets (words a page) are in src/check.py.
# ---------------------------------------------------------------------------------------------
LIMITS = {"headline": 12, "page title": 6, "kicker": 4, "statement": 25, "heading": 8, "text section": 160, "lead": 25,
          "caption": 40, "door kicker": 2, "door title": 4, "door line": 15, "item title": 6, "item line": 40,
          "card line": 25, "action line": 20, "theme statement": 20, "company story": 90, "thank-you": 40}
OVER = {}


def n_words(text):
    return len(re.findall(r"\S+", re.sub(r"<[^>]+>", " ", text or "")))


def limit(kind, text):
    """Checks a text against its module's limit; returns the text unchanged."""
    n = n_words(text)
    if text and n > LIMITS[kind]:
        OVER[(kind, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()[:80])] = (LIMITS[kind], n)
    return text


def archive(path, src):
    """A link into the archive, tagged with where it came from."""
    sep = "&" if "?" in path else "?"
    return f"{ARCHIVE}{path}{sep}src=main-{src}"


# ---------------------------------------------------------------------------------------------
# Wireframe parts (step 2, 8 November 2026): grey boxes, bars, notes and the draft mark
# ---------------------------------------------------------------------------------------------
def img(label, ratio="3/2", dark=False, cls=""):
    """An image still to choose, at its real proportion."""
    c = "img" + (" dark" if dark else "") + (f" {cls}" if cls else "")
    style = f' style="aspect-ratio:{ratio}"' if ratio else ""
    return f'<div class="{c}"{style} role="img" aria-label="Image to choose: {e(label)}"><span>{e(label)}</span></div>'


def note(text):
    """What goes here: an annotation, hidden in clean view."""
    return f'<p class="note">{e(text)}</p>'


def lines(n=3):
    """Text still to write (used only where no draft can be written yet: content that does not exist)."""
    return '<div class="lines" aria-hidden="true">' + "<i></i>" * n + "</div>"


def draft(text, tag="p", cls=""):
    """Draft copy: written now from the masters, marked as a draft until Thomas approves it. Never placeholder text."""
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c}><span class="draft">{e(text)}</span></{tag}>'


def button(href, label, quiet=False):
    kind = " quiet" if quiet else " archive" if href.startswith(ARCHIVE) else ""
    return f'<a class="button{kind}" href="{href}">{e(label)}</a>'


def dead_button(label, quiet=False):
    return f'<span class="button{" quiet" if quiet else ""} dead" aria-disabled="true">{e(label)}</span>'


# ---------------------------------------------------------------------------------------------
# The modules (Website – modules, 05 Website, approved 8 November 2026): sixteen, each a function with its variants.
# A module renders as <section class="mod mod-NAME" data-mod="2.n Name (variant)"> on the grid; the label shows in
# the wireframe and hides in clean view. Every page below is a sequence of modules in the order of the page
# priorities (Website – Site map and user flows, section 6). Only the grid and DM Sans are styled; the look is step 4.
# ---------------------------------------------------------------------------------------------
MODULES = {  # number and name, as in Website – modules
    "header": "2.1 Header", "opening": "2.2 Opening", "page-head": "2.3 Page head", "text": "2.4 Text section",
    "photo": "2.5 Photograph", "grid": "2.6 Image grid", "themes": "2.7 Theme sequence", "collection": "2.8 Collection card",
    "numbers": "2.9 Numbers and counts", "partners": "2.10 Partner strip", "use": "2.11 Use example",
    "doors": "2.12 Doors and actions", "items": "2.13 Item list", "sponsor": "2.14 Sponsor credit", "form": "2.15 Form",
    "footer": "2.16 Footer",
}


def mod(name, variant, inner, cls="", sid=None, wrap=True, tight=False):
    """One module on the page: the section, its label and its inner content on the grid."""
    label = MODULES[name] + (f" ({variant})" if variant else "")
    a = f' id="{sid}"' if sid else ""
    body = f'<div class="wrap">{inner}</div>' if wrap else inner
    return f'<section class="mod mod-{name} {cls}{" tight" if tight else ""}" data-mod="{e(label)}"{a}>{body}</section>'


DRAFT_HEADINGS = {"How access works", "The rules in short", "Themes come from collections"}
# Headings that say something (Quality rules, rule 7), decided on 11 November 2026 on Thomas's authority; each is built from
# sentences already on its page, and none repeats the first sentence of the text beneath it (rule 4).


def chapter(html):
    """A new chapter of a page: twice the distance of a section before it (rule 9: space shows what belongs together)."""
    return html.replace('<section class="mod ', '<section class="mod chapter ', 1)


def heading(title, level=2, cls=""):
    c = f' class="{cls}"' if cls else ""
    limit("heading", title)
    inner = f'<span class="draft">{e(title)}</span>' if title in DRAFT_HEADINGS else e(title)
    return f"<h{level}{c}>{inner}</h{level}>"


def bars_svg(w, h, bar, bars, tris, cls, anchor):
    """White bars at 60 degrees that run in from the bottom edge and end in a point cut at 120 degrees, with a few triangles
    pointing up between them (the guide, Opening). bars: (x at the bottom edge, height); tris: (x, y of the base's left end)."""
    k, tip, side = 0.57735, 0.86603 * bar, 0.4 * bar
    poly = "".join(f'<polygon points="{x:.1f},{h} {x + bar:.1f},{h} {x + bar + k * b:.1f},{h - b:.1f} {x + k * (b + tip):.1f},{h - b - tip:.1f}"/>' for x, b in bars)
    poly += "".join(f'<polygon points="{x:.1f},{y:.1f} {x + side:.1f},{y:.1f} {x + side / 2:.1f},{y - 0.86603 * side:.1f}"/>' for x, y in tris)
    return f'<svg class="{cls}" viewBox="0 0 {w} {h}" preserveAspectRatio="{anchor} slice" aria-hidden="true" fill="#fff">{poly}</svg>'


# The cut on the Opening, a first version (11 November 2026; the exact drawing belongs to its canvas in Claude Design): the
# white of the page runs into the photograph from the edge below it, on the side of the words. Four bars a sixth of the
# photograph's height wide on desktop, three below it: each width its own composition, never one scaled into another.
OPENING_CUT = (bars_svg(928, 512, 85, [(-30, 320), (125, 210), (280, 130), (435, 60)],
                        [(130, 412), (188, 312), (262, 452), (314, 362), (406, 472), (590, 490)], "cut cut-wide", "xMinYMax")
               + bars_svg(300, 200, 33, [(-8, 120), (52, 75), (112, 40)], [(55, 160), (103, 180), (165, 190)], "cut cut-narrow", "xMinYMax"))
# The close: the footer on black, the pattern at full strength in white, the logo once (open, quiet, close).
CLOSE_PATTERN = bars_svg(640, 320, 48, [(40, 110), (157, 250), (274, 170), (391, 330), (508, 80)],
                         [(140, 260), (295, 200), (372, 270), (480, 280)], "close-pattern", "xMaxYMax")


# 2.2 Opening: the full Opening on Home, in three versions that stand side by side at /dev/opening/ (the plan of
# 11 November 2026, step 1). Nothing lies on the photograph but the cut (rule 14); the headline stands on white.
# - "across": the photograph across the whole window under the header, the cut coming in from the white below it, and the
#   headline at the display size beneath, so that photograph and headline are the first screen.
# - "words": the headline first on white, then the photograph across the window, the cut coming in from the white above.
# - "column": the version of 11 November 2026, 12:05: words in columns 1 to 4, the photograph from column 5 off the right edge.
OPENING_VERSION = "across"   # the version Home is built with
CUT_ACROSS = bars_svg(1440, 600, 96, [(-36, 380), (150, 250), (336, 150), (522, 70)],
                      [(170, 470), (250, 350), (330, 520), (420, 420), (520, 545), (700, 570)], "cut cut-wide", "xMinYMax")
CUT_NARROW = bars_svg(300, 200, 33, [(-8, 120), (52, 75), (112, 40)], [(55, 160), (103, 180), (165, 190)], "cut cut-narrow", "xMinYMax")


def m_opening(title, line=None, label="Opening photograph · released, no minors", version=None):
    v = version or OPENING_VERSION
    words = f"<h1>{e(limit('headline', title))}</h1>" + (draft(limit("lead", line), "p", "lead") if line else "")
    if v == "column":
        return mod("opening", "a, in the columns", f'<div class="cols"><div class="opening-words c1-4">{words}</div>'
                   f'<div class="c5-off"><figure class="frame"><div class="opening-frame">{img(label + " · from the line of column 5 off the right edge (2 below desktop)", None, cls="opening-img")}'
                   f'{OPENING_CUT}</div>{credit_line(cap=caption_html(slot("opening-column", None, label)))}</figure></div></div>',
                   cls="opening column")
    cut = (CUT_ACROSS + CUT_NARROW) if v == "across" else (CUT_ACROSS + CUT_NARROW).replace('class="cut ', 'class="cut from-top ')
    photo = (f'<figure class="frame"><div class="opening-frame bleed">{img(label + " · across the window", None, cls="opening-img")}{cut}</div>'
             f'<div class="wrap">{credit_line(cap=caption_html(slot("opening", "21/9", label)))}</div></figure>')
    text = f'<div class="wrap"><div class="cols"><div class="opening-words c1-9">{words}</div></div></div>'
    return mod("opening", "b, across the window" if v == "across" else "c, the words first", photo + text if v == "across" else text + photo,
               cls=f"opening {v}", wrap=False)


ECHO = ""   # the one echo between the Opening and the close (rule 19): drawn in step 5


# 2.3 Page head: kicker, title, statement, meta; variants (a) plain, (b) with two doors under it, (c) with the lead photograph.
def m_page_head(title, statement=None, kicker=None, meta=None, doors=None, lead=None, statement_draft=False):
    limit("page title", title); limit("statement", statement); limit("kicker", kicker)
    k = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
    # a meta item may be a link, (label, address): the way on, in the first screen of a phone (rule 23)
    item = lambda x: f'<a href="{x[1]}">{e(x[0])}</a>' if isinstance(x, tuple) else f"<span>{e(x)}</span>"
    m = ('<p class="meta-row">' + "".join(item(x) for x in meta) + "</p>") if meta else ""
    s = (draft(statement, "p", "statement") if statement_draft else f'<p class="statement">{e(statement)}</p>') if statement else ""
    variant = "b, with doors" if doors else "c, with the lead photograph" if lead else "a"
    inner = f'<div class="cols"><div class="c1-4">{k}<h1>{e(title)}</h1></div><div class="c6-12 head-right">{s}{m}</div></div>'
    if doors:
        inner += doors
    if lead:
        inner += f'<div class="lead-photo">{lead}</div>'
    return mod("page-head", variant, inner, cls="page-head has-doors" if doors else "page-head")


# 2.4 Text section: title left, text right; (b) with a facts box, (c) with a contact, (d) the intro on Home.
def m_text(title, paras, variant="a", box=None, contact=None, links=None, is_draft=True, sid=None, level=2, meta=None, lead_first=False):
    limit("text section", " ".join(p for p in paras if p))
    body = "".join(draft(p) if is_draft else f"<p>{e(p)}</p>" for p in paras if p)
    if lead_first and paras:       # a chapter's opener: its first sentence at the intro size, the rest as text
        body = draft(limit("lead", paras[0]), "p", "lead") + "".join(draft(p) for p in paras[1:] if p)
    if variant == "d" and paras:   # the intro on Home: the first sentence at the intro size, the rest as text
        body = draft(paras[0], "p", "lead") + "".join(draft(p) for p in paras[1:] if p)
    if links:
        body += f'<p class="doors">{"".join(links)}</p>'
    if meta:
        body += '<p class="meta-row">' + "".join(f"<span>{e(x)}</span>" for x in meta) + "</p>"
    if variant == "d":
        inner = f'<div class="cols"><div class="c1-8">{body}</div></div>'
        return mod("text", "d, the intro", inner, sid=sid)
    right = body
    if variant == "b" and box:
        right += f'<aside class="facts-box">{box}</aside>'
    if variant == "c" and contact:
        right += f'<div class="contact-box"><p class="kicker">{e(contact[0])}</p><p class="h-big"><a href="mailto:{contact[1]}">{contact[1]}</a></p></div>'
    names = {"a": "a, title left, text right", "b": "b, with a facts box", "c": "c, with a contact"}
    inner = f'<div class="cols"><div class="c1-4">{heading(title, level)}</div><div class="c6-12">{right}</div></div>'
    return mod("text", names[variant], inner, sid=sid)


# 2.5 Photograph: (a) full bleed, (b) on the columns, (c) photograph and text side by side, alternating.
CREDIT = "Photo: Africa Reframed"


# ---------------------------------------------------------------------------------------------
# Images (Thomas, 11 November 2026, second round). Three things are decided here, once, for every module:
# - The slot. Every image position on the site is recorded as it is built: its page, how it is shown, its proportion and
#   the size its file needs. The list is /dev/images/; choosing the images is filling these slots.
# - The caption. A photograph shown as work carries its AR ID, place and year, and the ID is a link to that image in the
#   archive: the proof beside the picture, which is the site's point of view. Until a slot is filled the pattern is shown.
# - The credit. A credit line stands where a photograph is shown as work: under a lead or featured photograph, and once
#   under a grid or a row from one collection. A small image that is a link to a page where the credit stands has none.
#   (Quality rules, rule 15, as relaxed on 11 November 2026: the credit is our choice, not a quality in itself.)
# ---------------------------------------------------------------------------------------------
PICKS = {}   # slot id -> dict(ar="AR-1022", place="Bamako, Mali", year="2014", text=None): entered as the images are chosen
SLOTS = []   # every image position, in page order
CUR = {"slug": None, "title": None, "n": 0}
ROLES = {    # how an image is shown -> (in words, its width in px on a 1,440 px screen)
    "opening": ("The Opening: across the window", 1920), "opening-column": ("The Opening: from column 5 off the right edge", 928),
    "lead": ("Lead photograph, the full content width", 1312), "lead-bleed": ("Lead photograph, full bleed, the width of the window", 1920),
    "two-thirds": ("Large photograph, columns 5 to 12", 864), "pair": ("One of a pair, half the columns each", 652),
    "feature": ("Full bleed, the width of the window", 1920), "half": ("Half the columns", 640), "third": ("A third of the columns", 416),
    "grid-3": ("Grid, three in a row", 432), "grid-4": ("Grid, four portraits in a row", 322), "strip": ("Strip of three squares", 432),
    "row-strip": ("Square in a theme’s row", 216), "row": ("A theme’s photograph on the Themes page", 512), "theme": ("Theme entry, five in a row", 237), "theme-nav": ("Previous or next theme", 640),
}


def slot(role, ratio, label):
    """Records an image position; returns its id (None on the development pages)."""
    if not CUR["slug"]:
        return None
    CUR["n"] += 1
    sid = f'{CUR["slug"]}-{CUR["n"]:02d}'
    SLOTS.append(dict(id=sid, page=CUR["title"], role=role, ratio=(ratio or "29/16").replace("/", ":"), label=label))
    return sid


def caption_html(sid, caption=None):
    """The caption of a photograph shown as work: the AR ID, linked into the archive, then the caption or the place and year."""
    if caption:
        return e(limit("caption", caption))
    pick = PICKS.get(sid)
    if pick:
        return (f'<a href="{archive("/-/galleries/archive?search=" + pick["ar"], "image")}">{e(pick["ar"])}</a> · '
                + e(limit("caption", pick.get("text") or f'{pick["place"]}, {pick["year"]}')))
    return "AR ID · Place, year"


def credit_line(caption=None, credit=None, own=True, group=False, cap=None):
    """Caption and credit beneath an image: the caption on its line, the credit on the line beneath. `cap` is caption html."""
    c = cap if cap is not None else (e(limit("caption", caption)) if caption else "")
    c = f'<span class="caption">{c}</span> ' if c else ""
    cr = f"<span>{e(credit or CREDIT)}</span>" if own else ""
    return f'<p class="credit{" group" if group else ""}">{c}{cr}</p>' if (c or cr) else ""


def frame(label, ratio="3/2", caption=None, credit=None, cls="", role="grid-3", own=True, cap=True):
    """An image in its slot, with what stands beneath it. own: its own credit line; cap: its caption (AR ID, place, year)."""
    sid = slot(role, ratio, label)
    below = credit_line(credit=credit, own=own, cap=caption_html(sid, caption) if (cap or caption) else "")
    return f'<figure class="frame"{f" data-slot={chr(34)}{sid}{chr(34)}" if sid else ""}>{img(label, ratio, cls=cls)}{below}</figure>'


def m_photo(label, ratio="3/2", variant="b", caption=None, text=None, side="left", span="c1-12", credit=None, sid=None, lead=False, echo=False, wide=False):
    role = "lead-bleed" if lead else "two-thirds" if wide else {"a": "feature", "c": "half"}.get(variant, "lead" if span == "c1-12" else "half")
    below = credit_line(credit=credit, cap=caption_html(slot(role, ratio, label), caption))
    if variant == "a":
        inner = f'<figure class="frame"><div class="bleed">{img(label, ratio, cls="bleed-img")}{ECHO if echo else ""}</div><div class="wrap">{below}</div></figure>'
        return mod("photo", "a, full bleed" + (", the lead" if lead else ""), inner, wrap=False, sid=sid, tight=lead, cls="lead-bleed" if lead else "")
    if variant == "c":
        # wide: the photograph over eight columns and the words in four, so that it is the large one of its story
        photo = f'<div class="{"c-wide" if wide else "c-half"} photo-half">{img(label, ratio)}{below}</div>'
        words = f'<div class="{"c-side" if wide else "c-half"}">{text}</div>'
        order = photo + words if side == "left" else words + photo
        return mod("photo", f"c, photograph and text, photograph {side}", f'<div class="cols">{order}</div>', sid=sid)
    return mod("photo", "b, on the columns", f'<div class="cols"><div class="{span}">{img(label, ratio)}{below}</div></div>')


# 2.6 Image grid: (a) three in a row, (b) four portraits, (c) a strip of three squares, (d) six to eight mixed.
def m_grid(variant="d", n=None, label="Image", line=None, link=None, title=None, credit=None, level=2, aside=None, cap=True):
    cell = lambda r: frame(label, r, role={"3/2": "grid-3", "4/5": "grid-4", "1/1": "strip"}[r], own=False, cap=False)
    top = heading(title, level, "project-title" if level == 3 else "") if title else ""
    top += f'<p class="small">{e(line)}</p>' if line else ""
    foot = credit_line(credit=credit, group=True) + (f'<p class="doors">{link}</p>' if link else "")
    if variant == "e":
        # One large photograph and one row of three (rule 16: the strongest is shown larger rather than more being shown
        # smaller). The large one carries its caption; one credit stands for the four. The words that belong to the
        # evidence stand beside the large photograph in columns 1 to 4 (aside): no empty column beside it.
        big = frame(label + ", the strongest, large", "3/2", role="two-thirds", own=False, cap=cap)
        cells = "".join(cell("3/2") for _ in range(3))
        return mod("grid", "e, one large and a row of three",
                   f'<div class="cols"><div class="c1-4 e-words">{top}{aside or ""}</div><div class="c5-12">{big}</div></div><div class="imgs grid-3 row-3">{cells}</div>{foot}')
    if variant == "a":
        cells = "".join(cell("3/2") for _ in range(n or 3)); cls = "grid-3"; name = "a, three in a row"
    elif variant == "b":
        cells = "".join(cell("4/5") for _ in range(n or 4)); cls = "grid-4"; name = "b, four portraits"
    elif variant == "c":
        cells = "".join(cell("1/1") for _ in range(3)); cls = "grid-strip"; name = "c, a strip of three"
    else:
        n = n or 6
        ratio, cls = ("3/2", "grid-3") if n <= 6 else ("4/5", "grid-4")
        cells = "".join(cell(ratio) for _ in range(n)); name = f"d, {n} in rows of {3 if n <= 6 else 4}"
    return mod("grid", name, f'{top}<div class="imgs {cls}">{cells}</div>{foot}')


def m_pair(labels, credited_by=None, credit=None):
    """2.6 (f): a pair, two frames at half the columns each. Under a company's story it is credited by the story's lead
    photograph (credited_by: that module's id); standing alone it carries one credit for the two."""
    cells = "".join(frame(label, "3/2", role="pair", own=False, cap=False) for label in labels)
    html = mod("grid", "f, a pair", f'<div class="imgs grid-pair">{cells}</div>{"" if credited_by else credit_line(credit=credit, group=True)}', tight=True)
    return html.replace('<section class="mod ', f'<section data-credited-by="{credited_by}" class="mod ', 1) if credited_by else html


def m_rows(items):
    """2.4 (e): a list under rules: several short sections as one module, each a heading left and its text right."""
    return mod("text", "e, a list under rules", "".join(
        f'<div class="cols"><div class="c1-4">{heading(h)}</div><div class="c6-12">{draft(limit("text section", t))}</div></div>' for h, t in items), cls="rows")


# 2.7 Theme sequence: (a) five entries in a row (Home), (b) five rows (Themes index), (c) previous and next.
def theme_entry(t, base, i, row=False, ratio="4/5"):
    strip = (frame(f'Image for {t["name"]}', "3/2", role="row", own=False, cap=False) if row
             else frame("Theme image", ratio, role="theme-nav" if ratio == "5/2" else "theme", own=False, cap=False))
    return (f'<a class="theme-entry{" row" if row else ""}" href="{base}themes/{t["slug"]}/">'
            f'<span class="order">{i}</span>{"" if row else strip}<div><h3>{e(t["name"])}</h3><p>{e(limit("theme statement", t["statement"]))}</p>'
            f'<span class="count">{t["count"]} images</span></div>{strip if row else ""}</a>')


def m_themes(base, variant="a", current=None):
    if variant == "c":
        n = THEMES.index(current)
        prv, nxt = THEMES[n - 1], THEMES[(n + 1) % len(THEMES)]
        inner = (f'<div class="cols"><div class="c-half theme-nav"><span class="dir">← Previous theme</span>{theme_entry(prv, base, THEMES.index(prv) + 1, ratio="5/2")}</div>'
                 f'<div class="c-half theme-nav"><span class="dir">Next theme →</span>{theme_entry(nxt, base, THEMES.index(nxt) + 1, ratio="5/2")}</div></div>')
        return mod("themes", "c, previous and next", inner)
    lead = draft(limit("lead", THEMES_LEAD), "p", "lead")
    title = f"The first {NUMBER_WORDS[len(THEMES)]} themes"
    DRAFT_HEADINGS.add(title)
    if variant == "b":
        rows = "".join(theme_entry(t, base, i, row=True) for i, t in enumerate(THEMES, 1))
        return mod("themes", "b, rows", f'<div class="theme-rows">{rows}</div>')
    cards = "".join(theme_entry(t, base, i) for i, t in enumerate(THEMES, 1))
    # up to five stand in one row; from six they stand in two even rows, so a new theme needs no new design
    n = len(THEMES)
    return mod("themes", "a, in a row", f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">{lead}</div></div>'
               f'<div class="theme-row" style="--theme-cols:{n if n <= 5 else -(-n // 2)}">{cards}</div>')


# About's helpers (About page – build brief): the three lines of activity under the head, and a project as proof of one of them.
def m_channels(rows):
    """The three lines of activity under About's head, in the order of the sections, each linking down the page."""
    li = "".join(f'<li><a href="#{sid}"><strong>{e(name)}</strong>{draft(line, "span", "channel-line")}</a></li>' for sid, name, line in rows)
    return mod("items", "a, the three lines of activity", f'<ul class="channels">{li}</ul>', tight=True)


def state_label(x):
    return f'<p class="kicker state">{STATES[x["state"]]}</p>' if STATES.get(x["state"]) else ""


def m_project(x, extra=""):
    """A project as proof of a line of activity: its title, its text and its photograph. No year as structure: the year sits
    in the caption. (bleed) the photograph full bleed, the words under it, title left, text right; (side) photograph and text."""
    if not x.get("text"):
        # The area's text names the project; here it is shown: its photograph with the specifics in the caption (place,
        # year, who made and funded it), then at most one row of three, each with what it shows.
        n = note(x["note"]) if x.get("note") else ""
        if x["layout"] == "bleed":
            out = m_photo(x["image"], "21/9", "a", caption=x["caption"], credit=x["credit"])
            if x.get("row"):
                cells = "".join(frame(label, "3/2", caption=cap, own=False) for label, cap in x["row"])
                out += mod("grid", "a, three in a row, each with what it shows",
                           f'<div class="imgs grid-3">{cells}</div>{credit_line(credit=x["credit"], group=True)}{n}', tight=True)
            return out
        sid = slot("lead", "21/9", x["image"])
        return mod("photo", "b, on the columns", f'<div class="cols"><div class="c1-12">{img(x["image"], "21/9")}'
                   f'{credit_line(credit=x["credit"], cap=caption_html(sid, x["caption"]))}{n}</div></div>')
    words = state_label(x) + heading(x["title"], 3, "project-title")
    body = "".join(draft(t) for t in x["text"]) + (note(x["note"]) if x.get("note") else "")
    if x["layout"] == "bleed":
        out = m_photo(x["image"], "21/9", "a", caption=x["caption"], credit=x["credit"])
        if x.get("gallery"):
            # The project's words beside one large view, then a row of three (rule 16; the plan of 11 November 2026):
            # the first four of the gallery's views, the strongest first.
            g = x["gallery"]
            big = frame(g["labels"][0], "3/2", role="two-thirds", own=False, cap=False)
            cells = "".join(frame(label, "3/2", own=False, cap=False) for label in g["labels"][1:4])
            out += mod("grid", "e, the project: its words, one large view and a row of three",
                       f'<div class="cols"><div class="c1-4 e-words">{words}{body}{extra}</div><div class="c5-12">{big}</div></div>'
                       f'<div class="imgs grid-3 row-3">{cells}</div>{credit_line(g["caption"], g["credit"], group=True)}', tight=True)
        else:
            out += mod("text", "a, the project", f'<div class="cols"><div class="c1-4">{words}</div><div class="c6-12">{body}{extra}</div></div>', tight=True)
        return out
    return m_photo(x["image"], "3/2", "c", text=words + body + extra, side="left", caption=x["caption"], credit=x["credit"], wide=True)


def collection_entry(x, base):
    """A collection in the archive (the collection card, 2.8), as proof of the archive."""
    meta = "".join(f"<span>{e(m)}</span>" for m in x["meta"])
    return (f'<a class="collection-card cols" href="{base}{x["href"]}"><div class="c-half">{frame(x["image"], "3/2", role="half", own=False, cap=False)}</div>'
            f'<div class="c-half">{state_label(x) if x.get("state") else ""}<p class="kicker">{e(x["kicker"])}</p><h3 class="h-big">{e(x["title"])}</h3>{draft(limit("card line", x["line"]))}'
            f'<p class="meta-row">{meta}</p><span class="textlink">Open the collection</span></div></a>')


# 2.8 Collection card: (a) one card at the full width, (b) a list of cards. The cards come from COLLECTIONS.
def collection_card(c, base):
    return collection_entry(dict(c["card"], title=c["title"], href=f'collections/{c["slug"]}/'), base)


HOME_COLLECTIONS_TITLE = "Two collections, one of them sponsored"   # true while COLLECTIONS holds these two; the build checks it


def m_collection(base, variant="a", title=True):
    assert len(COLLECTIONS) == 2 and sum(1 for c in COLLECTIONS if c.get("sponsor")) == 1, "HOME_COLLECTIONS_TITLE no longer fits the collections"
    top = f'<div class="cols"><div class="c1-8">{heading(HOME_COLLECTIONS_TITLE)}</div></div>' if title else ""
    n = note("A new sponsored collection appears here once it is signed, shown as in production with behind-the-scenes material; never as a plan.")
    cards = "".join(collection_card(c, base) for c in COLLECTIONS)
    return mod("collection", "b, a list of cards", f'{top}<div class="collection-list">{cards}</div>{n}')


# 2.9 Numbers and counts: (a) a row of three, (b) one count with its action (used inside Doors b), (c) by country.
def numbers_row(values=NUMBERS, asof="as of 2 November 2026"):
    items = "".join(f'<div class="num"><b>{n}</b><span>{e(t)}</span></div>' for n, t in values)
    return f'<div class="numbers">{items}</div><p class="credit">{e(asof)}</p>'


def m_numbers(values=NUMBERS, asof="as of 2 November 2026", variant="a", title=None, note_text=None, tight=False, sid=None):
    if not exists(values) and not SHOW_EMPTY:
        return ""
    top = f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">{note(note_text) if note_text else ""}</div></div>' if title else ""
    if variant == "c":
        rows = "".join(f'<div class="num small-num"><b>{n}</b><span>{e(t)}</span></div>' for n, t in values)
        return mod("numbers", "c, counts in a row", f'{top}<div class="numbers by-kind">{rows}</div>', tight=tight, sid=sid)
    return mod("numbers", "a, a row", top + numbers_row(values, asof), tight=tight, sid=sid)


# 2.10 Partner strip: shown only once there are partners; here in grey so the layout exists.
def m_partners(n=6, title="In use by", tight=False):
    if not PARTNERS_NAMED and not SHOW_EMPTY:
        return ""
    logos = '<div class="logos">' + '<span class="logo">Partner logo</span>' * n + "</div>"
    return mod("partners", "", f'<div class="cols"><div class="c1-4">{heading(title) if title else ""}</div><div class="c6-12">'
               + note("Partners and sponsors by name, with their consent, from the closed preview. Until there are any, this module is left out of the live page.")
               + f'</div></div>{logos}', tight=tight)


# 2.10, supporters (About, Thomas, 10 November 2026): the institutions that have supported the work, strongest first, at equal
# size (the guide's PartnerStrip: one-colour logos, no tiers, no boxes; the order is the only ranking).
def m_supporters(rows, title, base):
    def one(x):
        if not x.get("logo"):
            return f'<span class="logo">{e(x["name"])}</span>'
        r = x["ratio"]
        h = min(LOGO_MAX_H, math.sqrt(LOGO_AREA * x.get("weight", 1) ** 2 / r))
        w = r * h
        if w > LOGO_MAX_W:
            w, h = LOGO_MAX_W, LOGO_MAX_W / r
        return (f'<span class="logo has-img"><img src="{base}assets/supporters/{x["logo"]}" alt="{e(x["name"])}" '
                f'width="{w:.0f}" height="{h:.0f}" decoding="async"></span>')
    logos = '<div class="logos supporters">' + "".join(one(x) for x in rows) + "</div>"
    return mod("partners", "supporters", f'<div class="cols"><div class="c1-12">{draft(title, "p", "kicker supporters-title")}</div></div>{logos}'
               + note("The logos are each organisation’s own, taken from its website on 10 November 2026 and shown in one dark tone at equal optical weight. "
                      "Before launch each gets a short courtesy note (we show you among those who supported our work), which also brings its official "
                      "one-colour file to replace these. CKU is left out (closed); Canon only if it supported Øksnehallen."), tight=True)


# 2.11 Use example: (a) one, side by side; (b) three in a row; (c) partner news.
def use_card(kind="use"):
    if kind == "news":
        return f'<div class="example">{frame("News image", "3/2")}<p class="kicker">Date</p>{lines(2)}</div>'
    return (f'<div class="example">{frame("The use: a page, a slide, a post or an exhibition wall", "3/2", caption="AR-ID · the caption")}'
            f'<p class="small">Partner · publication · use · month, year</p>{lines(2)}</div>')


def m_use(variant="a", title="In use", tight=False):
    if not SHOW_EMPTY and not (NEWS if variant == "c" else USES):
        return ""
    n = note("Images in use, reported back by partners with their consent. Shown once there are any; until then left out of the live page.")
    if variant == "a":
        inner = (f'<div class="cols"><div class="c1-4">{heading(title) if title else ""}</div><div class="c6-12">{n}</div></div>'
                 f'<div class="cols"><div class="c-half">{frame("The use: a page, a slide, a post or an exhibition wall", "3/2", caption="AR-ID · the caption")}</div>'
                 f'<div class="c-half"><p class="small">Partner · publication · use · month, year</p>{lines(2)}</div></div>')
        return mod("use", "a, one example", inner, tight=tight)
    if variant == "c":
        return mod("use", "c, partner news", f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">'
                   + note("News for partners and the numbers as they grow; aggregates and consented examples only. Shown once there is something to show.")
                   + f'</div></div><div class="cards-3">{use_card("news") * 3}</div>', tight=tight)
    return mod("use", "b, three in a row", f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">{n}</div></div>'
               f'<div class="cards-3">{use_card() * 3}</div>', tight=tight)


# 2.12 Doors and actions: (a) two doors, (b) the action band with a count, (c) the ways on, (d) the contact band.
def door(href, kicker, title, line, dark=False):
    limit("door kicker", kicker); limit("door title", title); limit("door line", line)
    kind = " archive" if href.startswith(ARCHIVE) else ""
    return (f'<a class="panel{kind}" href="{href}"><span class="kicker">{e(kicker)}</span>'
            f'<strong>{e(title)}</strong><span>{e(line)}</span></a>')


def m_doors(variant, *, doors=None, count=None, count2=None, main=None, quiet=None, line=None, address=None, kicker=None, links=None, sid=None, tight=False, left=False):
    if variant == "a":
        return mod("doors", "a, two doors", f'<div class="door-panels">{"".join(doors)}</div>', sid=sid, tight=tight)
    if variant == "b":
        c = f'<div class="num"><b>{count[0]}</b><span>{e(count[1])}</span></div>'
        if count2 and (count2[0] != "—" or SHOW_EMPTY):
            c = f'<div class="numbers">{c}<div class="num"><b>{count2[0]}</b><span>{e(count2[1])}</span></div></div>'
        inner = f'<div class="action">{c}<p class="doors">{main}{quiet or ""}</p></div>' + (draft(limit("action line", line), "p", "small") if line else "")
        return mod("doors", "b, the action band", inner, cls="band archive" if 'class="button archive"' in (main or "") else "band", sid=sid, tight=tight)
    if variant == "d":
        inner = f'<div class="cols"><div class="c1-4">{heading(kicker)}</div><div class="c6-12"><p class="h-big"><a href="mailto:{address}">{address}</a></p>{draft(line, "p", "small") if line else ""}</div></div>'
        return mod("doors", "d, the contact band", inner, cls="band", sid=sid, tight=tight)
    return mod("doors", "c, the ways on", f'<div class="cols"><div class="{"c1-12" if left else "c6-12 c-offset"}"><p class="doors">{"".join(links)}</p></div></div>', sid=sid, tight=tight)


# 2.13 Item list: (a) plain under rules, (b) numbered steps, (c) accordion, (d) with images, (e) chips.
def m_items(title, items, variant="a", lead=None, is_draft=True, sid=None, image_ratio="3/2", image_label="Image", tight=False, cols=3, level=2, cls="", credit=None):
    h = heading(title, level, "project-title" if level == 3 else "") if title else ""
    top = f'<div class="cols"><div class="c1-4">{h}</div><div class="c6-12">{lead or ""}</div></div>' if title else ""
    t = (lambda s: draft(s)) if is_draft else (lambda s: f"<p>{e(s)}</p>")
    if variant != "e":
        for x in items:
            limit("item title", x[0]); limit("item line", x[1])
    if variant == "b":
        li = "".join(f'<li><span class="step-n">{i}</span><h3>{e(a)}</h3>{t(b)}</li>' for i, (a, b) in enumerate(items, 1))
        return mod("items", "b, numbered steps", f'{top}<ol class="steps">{li}</ol>', sid=sid, tight=tight)
    if variant == "c":
        li = "".join(f'<details class="acc"><summary>{e(a)}<span class="plus" aria-hidden="true"></span></summary>{t(b)}</details>' for a, b in items)
        return mod("items", "c, accordion", f'{top}<div class="cols"><div class="c6-12 c-offset">{li}</div></div>', sid=sid, tight=tight)
    if variant == "d":
        def card(x):
            extra = x[3] if len(x) > 3 and x[3] else {}
            pic = extra.get("image") or frame(x[2] if len(x) > 2 and x[2] else image_label, image_ratio, role="third", own=False, cap=False)
            name = f'<a href="{extra["href"]}">{e(x[0])}</a>' if extra.get("href") else e(x[0])
            return f'<div class="item">{pic}<h3>{name}</h3>{t(x[1]) if x[1] else ""}</div>'
        li = "".join(card(x) for x in items)
        foot = credit_line(credit=credit, group=True) if 'class="frame"' in li and "card-work" not in li and credit is not False else ""
        return mod("items", "d, with images", f'{top}<div class="cards-{cols}">{li}</div>{foot}', sid=sid, tight=tight)
    if variant == "e":
        chips = "".join(f'<a class="chip" href="{h}">{e(a)}</a>' if h else f'<span class="chip">{e(a)}</span>' for a, h in items)
        top = f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">{lead or ""}<div class="chips">{chips}</div></div></div>'
        return mod("items", "e, chips", top, sid=sid, tight=tight)
    li = "".join(f'<li><strong>{e(a)}</strong>{t(b)}</li>' for a, b in items)
    return mod("items", "a, plain under rules", f'{top}<ul class="principles {cls}">{li}</ul>', sid=sid, tight=tight)


# 2.14 Sponsor credit: (theme) "Made possible by …" under the statement; (collection) the full name as the title.
def m_sponsor(variant="theme", tight=False, sponsor=None):
    if variant == "collection" and sponsor:
        inner = (f'<div class="cols"><div class="c1-4"><p class="kicker">Made possible by</p><h2>{e(sponsor["name"])}</h2></div>'
                 f'<div class="c6-12">{'<div class="logos"><span class="logo">Sponsor logo</span></div>' if SHOW_EMPTY else ""}{draft(sponsor["text"])}{note(sponsor["note"])}</div></div>')
        return mod("sponsor", "collection page", inner, tight=tight)
    if variant == "collection":
        inner = (f'<div class="cols"><div class="c1-4"><p class="kicker">Collection</p><h2>Africa Reframed / [Full collection name]</h2></div>'
                 f'<div class="c6-12"><div class="logos"><span class="logo">Sponsor logo</span></div>{lines(3)}<p class="small">The sponsor’s contact</p></div></div>'
                 + note("The sponsor’s statement (at most 80 words) and contact, after the work. Only once a collection is sponsored."))
        return mod("sponsor", "collection page", inner, tight=tight)
    if not sponsor and not SHOW_EMPTY:
        return ""
    inner = (f'<div class="cols"><div class="c6-12 c-offset"><p class="kicker">Made possible by</p><div class="logos"><span class="logo">Sponsor logo</span></div>'
             f'<p class="small">Founding Partner (working title) · <a href="#">About the collection</a></p></div></div>'
             + note("Shown under the theme’s statement only once a sponsor has funded the theme. Until then nothing is shown here."))
    return mod("sponsor", "theme page", inner, tight=tight)


# 2.15 Form: (a) the long form with an aside, (b) three short forms, (c) a single quiet action.
def field(label, kind="text", fid=""):
    if kind == "select":
        ctl = (f'<select id="{fid}" disabled><option>NGO</option><option>Media</option><option>Educational institution</option>'
               f'<option>Embassy or ministry</option><option>Development finance institution</option><option>Company</option></select>')
    elif kind == "textarea":
        ctl = f'<textarea id="{fid}" rows="3" disabled></textarea>'
    else:
        ctl = f'<input id="{fid}" type="{kind}" disabled>'
    return f'<label for="{fid}">{e(label)}</label>{ctl}'


def m_form(variant="a", title=None, fields=None, aside=None, consent=None, button_label="Send", forms=None, after=None, sid=None, lead=None, tight=False):
    if variant == "b":
        cards = ""
        for ft, fl, fs in forms:
            fl_html = "".join(field(l, k, f"{sid or 'f'}-{i}") for i, (l, k) in enumerate(fs))
            cards += f'<div class="card"><h3>{e(ft)}</h3>{draft(fl, "p", "small") if fl else ""}<form class="mini-form">{fl_html}{dead_button("Send")}</form></div>'
        top = f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">{lead or ""}</div></div>' if title else ""
        return mod("form", "b, three short forms", f'{top}<div class="cards-3">{cards}</div>', sid=sid, tight=tight)
    if variant == "c":
        inner = f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">{lead or ""}{dead_button(button_label, quiet=True)}</div></div>'
        return mod("form", "c, a single quiet action", inner, sid=sid, tight=tight)
    rows = "".join(field(l, k, f"f{i}") for i, (l, k) in enumerate(fields))
    if consent:
        rows += f'<label class="check"><input type="checkbox" disabled> <span class="draft">{e(consent)}</span></label>'
    form = f'<form class="form" aria-label="{e(title)} (not connected yet)">{rows}<button type="button" class="button" disabled>{e(button_label)}</button></form>' + (after or "")
    inner = f'<div class="cols"><div class="c1-6">{form}</div><div class="c7-12"><aside class="facts-box">{aside or ""}</aside></div></div>'
    return mod("form", "a, the long form with an aside", inner, sid=sid, tight=tight)


# ---------------------------------------------------------------------------------------------
# Draft copy (step 2): written from The engine – brief, the page priorities and the guide’s Words section, within the
# lengths in Website – modules; marked as draft on the page until Thomas approves it. Sources in comments.
# ---------------------------------------------------------------------------------------------
INTRO_HOME = [  # page priorities, Home 2: who it is for and who is behind it; one idea per sentence, the modules below carry the facts
    "Africa Reframed is a partner archive of photographs of modern life in Mali, Kenya and The Gambia.",
    "Organisations working with Africa use the images in their reports, exhibitions and channels. An independent initiative established by Commerce & Culture.",
]
PRINCIPLES = [  # engine brief, For design: the principles a company needs before it puts its name on the work
    ("Real images", "Every photograph is made by a photographer on location. Our images are never AI-generated and never altered."),
    ("Consent", "The people in the images agreed to be photographed and to the uses the archive allows."),
    ("Credited, fairly paid photographers", "The photographers are paid for their work, and every image carries its credit line."),
    ("Editorial independence", "Sponsors get name and stage, never editorial control over what the images show."),
]
THEME_TEXTS = {  # theme page 4: what the theme shows and why it matters to partners (Keywording Guide 8b)
    "learning": "Classrooms and campuses in Bamako and Nairobi, a training kitchen in Banjul, homework at the kitchen table: people of every age building skills, in lessons, in groups around a laptop and on their own. For a partner working in education or vocational training the theme shows teachers as much as learners, and adults building skills as much as children.",
    "work-and-enterprise": "Tradespeople, cooks, farmers, shopkeepers and young professionals at work, with the tools and the places of their trade: a bicycle repair, a carpenter’s workshop, a market stall, a café meeting, tea fields. For a partner working in skills, enterprise or agriculture the theme shows value being created by people who are good at what they do.",
    "everyday-digital": "Phones, laptops and money on a screen, used for work, study and keeping in touch: a call in a car, a lesson on a laptop, a payment at a stall. The largest of the five themes. For a partner working in digital services, finance or education it shows technology as an ordinary part of the day, not a novelty.",
    "city-life": "Cafés, campuses, rooftops and busy streets: the everyday rhythm of Bamako, Banjul and Nairobi, from the morning commute to the evening at a café. For a partner whose work is in cities it shows modern urban life as the given it is.",
    "creativity-and-culture": "Portraits, style and street art, mostly from Banjul: studio portraits, murals, the way people dress and present themselves. For a partner in culture, media or the creative economy it shows culture as current, made by the people in the frame.",
}
THEME_ACTION_LINE = "Partners open the theme in the archive; others are asked to log in or to request access first."  # brief, section 5
HOUSE_STORY = [  # collection page 2: the story (Keywording Guide 2; AR Archive – Status); partner names only once they agree
    "The House Collection is Africa Reframed’s own collection: 1,122 photographs made by our team between 2013 and 2018, in 21 shoots in Mali, Kenya and The Gambia, alongside photography workshops in Bamako, Nairobi and Banjul.",
    "The images show people at work, at study and at home in three modern cities and the countryside around them, photographed in natural light, in their own places. They are released for the uses the archive allows and carry one credit: Photo: Africa Reframed.",
]
# The House Collection names no photographers: "our team" is the credit (Thomas, 9 November 2026). Sponsored collections name theirs.
PLACES = [  # collection page 5: places and series (Keywording Guide 9, 11b; the shoot list)
    ("Mali", "Bamako: classrooms, a campus and the street, from the first productions."),
    ("Kenya", "Nairobi: cafés, offices and campuses; tea fields and a farming village outside the city."),
    ("The Gambia", "Banjul: a culinary training, women in trades, small businesses and studio portraits. Series: Culinary training, Banjul · Women in trades, Banjul."),
]
SPONSOR_TEXT = [  # Partners 4: sponsor a collection, in general terms (brief, Partners; engine brief)
    "We make new collections with companies and foundations as sponsors. The theme is close to the sponsor’s work, or one it wants to support, never its own operations.",
    "The sponsor is named on the collection’s page and the theme page, and gets the whole archive for its own channels, for good.",
]
ACCESS_STEPS = [  # Partners 2: how access works (AR Archive – Status, 3 and 6 November 2026)
    ("Request access", "Tell us who you are and how you will use the images. We reply within a working day."),
    ("Approved by name", "We approve each organisation by name; your account opens for the email address you give."),
    ("Collect, then download", "Gather images in the Lightbox. Each download is a free licence for the one use you state."),
]
RULES = [  # Partners 3: Using the images, drafted in the brief; to check against the licence
    ("Who may use the images", "Approved partners, one licence per organisation. The press set is for editorial use."),
    ("One download, one use", "Each download is a free licence for the use you state there: a report, an application, an exhibition, the press, a presentation or your own channels. A new use, a new download."),
    ("Credit", "The credit line on every use, on or beside the image: Photo: Africa Reframed. For a sponsored collection it names the collection in full, sponsor included."),
    ("Editing", "Cropping, resizing and colour are fine; changing what an image shows is not, and neither is altering images with AI or using them to train AI."),
    ("The people portrayed", "Accurate captions and contexts they would recognise; never a degrading or misleading one, and never presenting the images as your own operations or results."),
    ("No resale", "No resale, sublicensing or use as a logo."),
    ("Tell us where they appear", "Report a use through the Partner portal."),
]
PORTAL_LEAD = "The archive is for partners: NGOs, media, educational institutions, embassies, ministries and development finance institutions."
PORTAL_RULES = "One download is one licence, for the use you state. Credit every use, never change what an image shows, and tell us where the images appear."
REQUEST_NEXT = [("We read your request", "and reply within a working day."), ("You get a welcome email", "with your login; the account opens for the address you give."),
                ("You log in,", "collect in the Lightbox and download for each use, free.")]
REQUEST_CONSENT = "I agree that how we use the images may be reported, without personal details, to the funders who make new collections possible."
REQUEST_FOOT = "Companies get access through a collection sponsorship; write to partnerships@africareframed.com."

# ---------------------------------------------------------------------------------------------
# Collections (the collection template, 9 November 2026). One template for every collection: each collection is data, and
# its page is the list of sections it names, in order. A sponsored collection's page is a worked example for the next funder
# (Thomas, 9 November 2026): it shows what a sponsor gets, a body of work on a theme close to its own, the stories, named
# photographers, behind-the-scenes material and where the images went, and it ends with the invitation to make one on
# another theme. The work carries the case; the invitation comes once, at the end. No legal text on these pages.
# ---------------------------------------------------------------------------------------------
HOUSE_COLLECTION = dict(
    slug="house-collection", title="House Collection", kicker="Collection", statement=HOUSE_STATEMENT, statement_draft=True,
    lead="Collection image", story_title="Made by our own team, 2013 to 2018", story=HOUSE_STORY, facts=HOUSE_FACTS,
    grid_line="A spread across the five themes; released, no minors.",
    access=dict(count=("1,122", "images in the House Collection"), src="collection-house", line=f"Sponsoring a collection? Write to {EMAIL_PARTNERS}."),
    sections=["story", "grid", "places", "feature", "themes", "goals", "access", "uses"],
    card=dict(kicker="Our own collection", line="1,122 photographs made by our team in Mali, Kenya and The Gambia.",
              meta=["1,122 images", "21 shoots", "Mali · Kenya · The Gambia"], image="Collection image"),
)

# The BESTSELLER FOUNDATION Waste to Value Collection. Sources: Track Record (Bestseller Foundation case, from the mail);
# BESTSELLER FOUNDATION Waste to Value research (status 24 October 2026); the partnership announcement (20 November 2020).
# Tense rule (the research): present tense only for the companies with dated activity since 2024 (Gjenge Makers, Yo-Waste,
# Gracela Ventures); the others as photographed in 2021 until their founders confirm. Never "closed". The cohort was six
# (Intellecap's white paper); Vuma Biofuels was a separate investment by the foundation. Photographers named (Thomas).
WTV = "BESTSELLER FOUNDATION Waste to Value Collection"
WTV_CREDIT = f"Photo: Africa Reframed / {WTV}"
WTV_COMPANIES = [  # seven stories, stacked like a magazine feature (Thomas, 9 November 2026): teasers that start the funder's
    # imagination, no "read more" behind them. Strongest first; the first four show the four kinds of work.
    dict(name="Gjenge Makers", kind="Waste to building materials", headline="Paving stones from plastic waste", city="Nairobi",
         where="Nairobi, Kenya · founded by Nzambi Matee", photographer="Paul Mbugua",
         text="In a workshop in Nairobi’s Industrial Area, plastic waste from packaging factories and collectors is mixed with sand, heated and pressed into paving blocks and tiles, certified by the Kenya Bureau of Standards. The materials engineer Nzambi Matee founded the company in 2017 and was named a UN Environment Programme Young Champion of the Earth in 2020.",
         since="Since then: a gavel she made from recycled plastic was used at the UN Environment Assembly in 2022, and she joined the Explorers Club 50 in 2025."),
    dict(name="Yo-Waste", kind="Technology for waste", headline="Booking the rubbish collection by app", city="Kampala",
         where="Kampala, Uganda · founded by Martin Tumusiime", photographer="Jjumba Martin",
         text="Homes and businesses in Kampala book their rubbish collection on a phone, on schedule or on demand, and the app sends an independent collector to the door. Yo-Waste began as a student project at Makerere University.",
         since="Since then: runner-up for the Royal Academy of Engineering’s Africa Prize for Engineering Innovation, 2024."),
    dict(name="Gracela Ventures", kind="Waste to energy", headline="Cooking fuel from organic waste", city="Kampala",
         where="Kampala, Uganda · founded by Grace Nalugwa", photographer="Jjumba Martin",
         text="Organic waste is carbonised and pressed into briquettes that households, schools and hotels burn in place of charcoal and firewood. Grace Nalugwa started the business with a youth livelihood grant and built it in Kawempe, in the north of Kampala.",
         since="Since then: Grace Nalugwa has been a Mandela Washington Fellow, 2022, and a One Young World scholar, 2024."),
    dict(name="Umuti", kind="Waste to packaging", headline="Paper bags from banana trunks", city="Kigali",
         where="Kigali, Rwanda · founded by four students of the African Leadership University", photographer="Muhire Rukundo Dieudonné",
         text="In a country that banned plastic bags in 2008, Umuti set out to make paper ones from the banana and plantain trunks left in the fields after the harvest. When we photographed it in 2021, the young company was in its pilot phase, backed by the foundation."),
    dict(name="Zijani", kind="Waste to energy", headline="Used cooking oil, collected for fuel", city="Nairobi",
         where="Nairobi, Kenya · founded by Bryan Lukano", photographer="Paul Mbugua",
         text="When we photographed it in 2021, Zijani collected used cooking oil from hotels, restaurants and caterers in Nairobi, so that it went into biodiesel and other products instead of down the drain. Its founder first had the idea for a university assignment."),
    dict(name="Green Charcoal Uganda", kind="Waste to energy", headline="Farm husks made into charcoal", city="Tororo",
         where="Tororo, Uganda · founded by Geoffrey Okoth Yoga", photographer="Jjumba Martin",
         text="When we photographed it in 2021, the company bought rice, coffee and palm kernel husks and maize cobs from smallholder farmers in eastern Uganda and turned them into cooking briquettes: a farm’s leftovers, sold as fuel."),
    dict(name="Vuma Biofuels", kind="Waste to energy", headline="Sugarcane waste as fuel", city="Awendo",
         where="Awendo, western Kenya · founded by Aaron Pattillo and Ian Otula", photographer="Paul Mbugua",
         text="When we photographed it in 2021, Vuma turned the bagasse left over from sugarcane in western Kenya into briquettes and pellets: fuel for industrial boilers, schools and homes, in place of firewood."),
]
WTV_COLLECTION = dict(
    slug="waste-to-value", title=WTV, kicker="Sponsored collection", statement_draft=True,
    statement="Seven young companies in Kenya, Uganda and Rwanda turning waste into fuel, building materials, packaging and services, photographed by photographers from their own countries.",
    meta=["7 companies", "Kenya · Uganda · Rwanda", "3 photographers"],
    lead="Lead image: a founder at work, from the collection", lead_credit=WTV_CREDIT, credit=WTV_CREDIT,
    story_title="Businesses built on waste", companies_title="Seven companies in three countries",
    photographers_title="Photographers from Nairobi, Kampala and Kigali",
    story=["Waste is a raw material. Across East Africa, young companies build businesses on it: cooking fuel from husks and sugarcane, paving from plastic, paper bags from banana trunks, and an app that gets the rubbish collected. This collection shows seven of them, the people who run them and the work they do, in their own places.",
           "The companies came through BESTSELLER FOUNDATION’s Waste to Value Challenge, launched with Intellecap in December 2019 across Kenya, Uganda, Tanzania and Rwanda. From more than 400 applications, six were chosen for an accelerator that ran from August 2020 to March 2021, with up to USD 100,000 each and support on markets, products, business planning and finance. Alongside it, the foundation invested in a seventh: Vuma Biofuels."],
    facts=[("Companies", "7, six of them from the accelerator"), ("Countries", "Kenya, Uganda, Rwanda"),
           ("Photographers", "Paul Mbugua, Jjumba Martin, Muhire Rukundo Dieudonné"), ("Photographed", "February 2020 to May 2021"),
           ("Programme", "Waste to Value, BESTSELLER FOUNDATION with Intellecap"), ("Access", "By request, for partners and the press")],
    companies=WTV_COMPANIES,
    companies_lead="Seven companies, seven stories. Four turn waste into energy, one into building materials and one into packaging; one builds the technology to collect it.",
    grid_line="Founders, workers and products: in workshops, yards, markets and kitchens.",
    making=[("A brief with every founder", "A video call with each company first, then a brief and a shot list around what it needed to show: its product, its people and its place."),
            ("Photographers from each country", "Photographers from Nairobi, Kampala and Kigali, hired and briefed by us, with every shoot prepared together with the company’s team."),
            ("A gallery for everyone involved", "The foundation and each founder got a gallery of their own, to use across all their channels.")],
    photographers=[("Paul Mbugua", "Nairobi · Rubanipix. Photographed the programme’s kick-off bootcamp in February 2020, then Gjenge Makers, Zijani and Vuma Biofuels.", "Behind the scenes: Paul Mbugua at work"),
                   ("Jjumba Martin", "Kampala. Photographed Yo-Waste, Gracela Ventures and Green Charcoal Uganda.", "Behind the scenes: Jjumba Martin at work"),
                   ("Muhire Rukundo Dieudonné", "Kigali · CornWine Films. Photographed Umuti in Kigali and Musanze.", "Behind the scenes: Muhire Rukundo Dieudonné at work")],
    photographers_lead="Three photographers, one in each country, each credited by name.",
    bts="Every shoot came with images of the photographer at work, shared on the foundation’s and the founders’ social media with the photographer named.",
    # Shared storytelling (Thomas, 9 November 2026): the big picture on the page, the exact evidence in the docs (Website – copy,
    # section 4b, web check). General, never loose: every line is true at the level it is pitched.
    went_title="Shared storytelling",
    went_lead="A report tells what a programme did. Images let everyone in it tell their own part, and carry the story further than any report.",
    went=[("The founders", "They used the photographs to present their companies, at investor events and online, in their own words."),
          ("The foundation", "It carried them in its own channels, to show the businesses it backs."),
          ("The sector", "The programme’s report on waste-to-value businesses in East Africa opened with them, credited to Africa Reframed."),
          ("What followed", "The foundation asked us back, to photograph more of the circular economy in Kigali, Nairobi and Cape Town.")],
    words=[("I have begun benefiting from the photoshoots already.", "Geoffrey Okoth Yoga, Green Charcoal Uganda, February 2021"),
           ("Paul and his assistant were very professional, organized, and had a great eye for what to shoot.", "Aaron Pattillo, Vuma Biofuels, May 2021")],
    sponsor=dict(name="BESTSELLER FOUNDATION",
                 text="BESTSELLER FOUNDATION invests in inclusive and circular businesses across Africa. The collection was made in a strategic partnership with Africa Reframed, which the foundation announced in November 2020.",
                 note="The foundation’s own statement, at most 80 words, and its logo, as the foundation approves them."),
    invite=dict(title="A collection on your theme",
                text=["This collection began with a theme close to the foundation’s own work: waste turned into value. A collection can start from any theme close to a funder’s work, or one it wants to support: a sector, a skill, a city, a change under way.",
                      "We find the people and places that show it, work with photographers from the countries concerned, and deliver the collection with its stories and its behind-the-scenes material. From there the storytelling is shared: the funder, the people in the collection and the press each tell their part with the same images. The funder’s name stands on the collection; the work stays independent."]),
    access=dict(count=("7", "companies in the collection"), request=True, line="Access to this collection is by request, for partners and the press."),
    sections=["story", "companies", "making", "photographers", "went", "words", "access", "sponsor", "invite"],   # behind the scenes is told with the photographers   # the stories carry the images; ends on the invitation
    card=dict(kicker="Sponsored collection", line="Seven young companies in Kenya, Uganda and Rwanda that turn waste into fuel, building materials, packaging and services.",
              meta=["7 companies", "Kenya · Uganda · Rwanda", "Access by request"], image="A photograph from the Waste to Value Collection", credit=WTV_CREDIT),
)
COLLECTIONS = [HOUSE_COLLECTION, WTV_COLLECTION]   # the order on Collections and on Home
# About (About page – build brief, 05 Website; rebuilt 9 November 2026 with Thomas). The function pages are a machine; About is
# the cultural institution behind it. Three lines of activity, all current: the archive (always on), exhibitions and workshops
# (mediums we activate when a project is funded). Each opens with the activity in the present tense, then the proof as
# projects, strongest first; dates only in captions or inside a sentence, never as structure. A project in production or open
# is shown first with its label; nothing else carries a state. Calibres are never mixed: artists, students, our team.
# Afghan Tales and Commerce & Culture's other work stay off the site. Every line is draft until Thomas approves it.
ABOUT_STATEMENT = ("We bring contemporary Africa into view in Europe: through an archive of photographs, "
                   "exhibitions of its artists, and workshops with its photographers.")
STATES = {"in production": "In production", "now": "Now", "record": ""}   # the order projects are shown in, top first
ABOUT_CHANNELS = [  # (anchor, name, one line): the three lines of activity under the head, in the order of the sections
    ("archive", "The archive", "Photographs of contemporary Africa, open to the organisations we approve and growing with every collection."),
    ("exhibitions", "Exhibitions", "African artists and our own photographs, shown to European audiences."),
    ("workshops", "Workshops", "African photographers, connected to the international picture market."),
]

# 1 The archive: the activity, then the proof
ABOUT_ARCHIVE_LONG = [   # the wording until 11 November 2026, 15:00, kept
    "We run an archive of photographs of contemporary Africa for the organisations that work with the continent: NGOs, media, educational institutions, embassies, development finance institutions and companies. It is free for the non-profit and public partners we approve; companies take part by sponsoring a collection.",
    "Partners browse the archive, gather images and share them with colleagues, and download what they need. Every download is a licence for one stated use, so we know where the images go. The archive grows by collections.",
]
# Shortened as a draft for Thomas (11 November 2026): the first sentence opens the chapter at the intro size; how the archive
# works is told on the function pages (About page – build brief, 5.1).
ABOUT_ARCHIVE = [
    "We run an archive of photographs of contemporary Africa for the organisations that work with the continent.",
    "It is free for the non-profit and public partners we approve; companies take part by sponsoring a collection. Every download is a licence for one stated use, so we know where the images go. The archive grows by collections.",
]
ARCHIVE_COLLECTIONS = [  # the collections in the archive; a sponsored collection is one more entry, shown first while in production
    dict(title="House Collection", state="record", kicker="The first collection", href="collections/house-collection/",
         line="1,122 photographs made by our team in Bamako, Nairobi and Banjul, alongside our workshops.",
         meta=["1,122 images", "Mali · Kenya · The Gambia"], image="A photograph from the House Collection, from the picks once cleared"),
]
ABOUT_GETTY_BEFORE = "Before the archive, our team’s images were licensed through Getty Images by companies including"
ARCHIVE_LICENSEES = ["VISA", "Western Union", "MTN", "McKinsey Global Institute", "Airtel", "Samsung", "Pearson"]   # bought the team's images (Getty contract 5100359; Track Record)
ABOUT_GETTY_AFTER = ("In 2025 we took them back, so that they serve one purpose: to carry this picture of Africa "
                     "into the work of organisations that work with the continent.")
ABOUT_HINGE = "The name Africa Reframed comes from an exhibition."

# 2 Exhibitions: the activity, then the projects, then the artists
ABOUT_EXHIBITIONS_LONG = [   # the wording until 11 November 2026, 15:00, kept
    "We show African artists and our own photographs to European audiences: in halls and on screens, with programmes of film, talks and workshops around the work.",
    "An exhibition is curated from our network of artists, made with a venue and public funders, and can take a physical or a digital form. A collection can open as an exhibition.",
]
ABOUT_EXHIBITIONS_1500 = [   # the wording from 15:00 to 15:20 on 11 November 2026, kept
    "We show African artists and our own photographs to European audiences in halls and on screens, with film, talks and workshops around the work.",
    "An exhibition is curated from our network of artists, made with a venue and public funders, and can take a physical or a digital form.",
]
# The area, then its proof (Thomas, 11 November 2026, 15:14 and 15:18): one text tells what exhibitions are for us and
# names Øksnehallen inside it; the exhibition has no heading and no text of its own, and its specifics stand with its
# pictures. Not "for example" in words: the form says it. A draft for Thomas.
ABOUT_EXHIBITIONS = [
    "We show African artists and our own photographs to European audiences in halls and on screens, with film, talks and workshops around the work.",
    "Each exhibition is curated from the artists we follow and made with a venue and public funders. In 2016 Africa Reframed filled the 5,000 square metres of Øksnehallen in Copenhagen with more than 300 works by artists and designers from across the continent. The Danish Ministry of Foreign Affairs later put Namsa Leuba’s image from the show on the cover of its own evaluation.",
]
EXHIBITION_PROJECTS = [  # strongest first; a new exhibition is one more entry, shown first while in production or open
    dict(title="Africa Reframed at Øksnehallen", state="record", layout="bleed",
         image="Installation view, Africa Reframed at Øksnehallen", credit="Photo: DGI-byen",
         caption="Africa Reframed at Øksnehallen, Copenhagen, 2016. Produced with DGI-byen; supported by Danida and Augustinus Fonden.",
         # three more views, each with what it shows (draft captions; the facts are the earlier text's)
         row=[("Visitors among the works", "Visitors among the works"),
              ("Framed works on a display module", "Ten display modules in oriented strand board carried the works through the hall"),
              ("One of the two cinemas", "One of the two cinemas, with films every day")],
         text_1500=["In the summer of 2016 the exhibition filled the 5,000 square metres of Øksnehallen in Copenhagen with more than 300 works by artists and designers from across the continent. It was produced with DGI-byen and supported by Danida and Augustinus Fonden.",
               "The Danish Ministry of Foreign Affairs later put Namsa Leuba’s image from the show on the cover of its own evaluation. The exhibition gave Africa Reframed its name."],
         text_long=["In the summer of 2016 the exhibition filled the 5,000 square metres of Øksnehallen in Copenhagen with more than 300 works by artists and designers from across the continent: Omar Victor Diop, Namsa Leuba, Fabrice Monteiro, Dillon Marsh, Lien Botha and Tahir Carl Karmali, with furniture by Yinka Ilori and fashion by ChiChia. Shown alongside them: Bamako Nights, made by the students of CFP Bamako.",
               "It was produced with DGI-byen and supported by Danida and Augustinus Fonden. Ten display modules built in oriented strand board carried the works through the hall; two cinemas and a programme of talks and workshops ran alongside. The Danish Ministry of Foreign Affairs later put Namsa Leuba’s image from the show on the cover of its own evaluation. The exhibition gave Africa Reframed its name."],
         # More of the exhibition, not more exhibitions (Thomas, 9 November 2026): the scale of the hall in six views.
         gallery=dict(labels=["The hall: the full length of Øksnehallen", "Visitors among the works", "Framed works on a display module",
                              "One of the two cinemas", "A talk in the programme", "The exhibition’s poster: Namsa Leuba"],
                      caption="Africa Reframed at Øksnehallen, Copenhagen, 2016", credit="Photo: DGI-byen")),
]
# Bigger, not smaller (Thomas, 9 November 2026): About features only what enlarges the picture. A small project beside a
# large one shrinks the large one, so PixlArt (2018) is off the page; more of Øksnehallen instead.
ABOUT_EXHIBITION_DOOR = "A collection can open as an exhibition"   # open: now, or once a sponsored collection exists (Thomas)
ABOUT_ARTISTS_LEAD = ("Our exhibitions are curated from the artists we have followed and published for more than a decade. "
                      "The works remain the artists’ own, under their copyright, with their galleries’ credits where they apply.")
ABOUT_ARTISTS_LEAD_BEFORE = ABOUT_ARTISTS_LEAD   # until 15:20 on 11 November 2026; its first sentence is now in the chapter's text
ABOUT_ARTISTS_LEAD = "The works remain the artists’ own, under their copyright, with their galleries’ credits where they apply."
# The African Photography Network (Thomas, 10 November 2026): open, run by us since 2014 (online from May 2014, "Powered by
# Commerce & Culture"), named in words only (no logo, no page, no menu item, never a link to the old domain, which now
# forwards elsewhere). It shows up in two places: this section on About and the network artists' own pages. The exhibition
# artists are not tied to it: they came to us through the exhibition. "From and in Africa": Élise Fitte-Duval is from
# Martinique and works in Senegal.
NETWORK = "African Photography Network"
NETWORK_LEAD = "An open network of photographers from and in Africa, which we have run since 2014."
ARTISTS_SHOWN = [  # (name, origin · series · one line, image label); shown at Øksnehallen; artists, never "photographers"
    ("Omar Victor Diop", "Senegal · Studio des Vanités, Diaspora · Portraits that place African history inside the present. Courtesy MAGNIN-A, Paris.", "Omar Victor Diop, Diaspora"),
    ("Namsa Leuba", "Switzerland and Guinea · Khoi San, Zulu Kids, The Kingdom of Mountains · Staged photographs on how cultures see one another.", "Namsa Leuba, Khoi San"),
    ("Fabrice Monteiro", "Belgium and Senegal · The Prophecy, A Gorean Summer · Staged images on the environment and on heritage, made in Senegal.", "Fabrice Monteiro, The Prophecy"),
    ("Dillon Marsh", "South Africa · For What It’s Worth, Assimilation, Common Ground · The mines of South Africa and what they yielded.", "Dillon Marsh, For What It’s Worth"),
    ("Lien Botha", "South Africa · Parrot Jungle · Photographs of return and memory.", "Lien Botha, Parrot Jungle"),
    ("Tahir Carl Karmali", "Kenya · Jua Kali · Composites built from found objects in Nairobi.", "Tahir Carl Karmali, Jua Kali"),
    ("Yinka Ilori", "Nigeria and the United Kingdom · Furniture rebuilt from discarded chairs, telling Nigerian parables.", "Yinka Ilori, furniture"),
    ("Films at Øksnehallen", "Two cinemas in the hall.", "A film still"),  # replaces ChiChia's card (Thomas, 10 November 2026)
]
ARTISTS_NETWORK = [  # from the network, profiled in our journal; one line each, in our words
    ("Osborne Macharia", "Kenya · Staged commercial photography with a story in every frame."), ("Élise Fitte-Duval", "Martinique and Senegal · Contemporary dance, and the floods of Dakar."),
    ("Fatoumata Diabaté", "Mali · Sutigi: the night belongs to the young."), ("Isaac Kasamani", "Kenya and Uganda · Photojournalism of Uganda’s politics."),
    ("Antonia Steyn", "South Africa · Portraits of South African figures."), ("Ala Kheir", "Sudan · Landscapes and lives across the country."),
    ("Adeola Olagunju", "Nigeria · Performance photographs: Resurgence, a manifesto."), ("Jon Riordan", "South Africa · Landscapes shaped by memory."),
    ("Mpho Mokgadi", "South Africa · Everyday life, on film."), ("Charles Okereke", "Nigeria · Photographs close to abstraction, on people and the environment."),
    ("Hélène Amouzou", "Togo and Belgium · Self-portraits on displacement."), ("Sydelle Willow Smith", "South Africa · Migration and identity."),
    ("Jac Kritzinger", "South Africa · The ordinary, made visible."), ("Mouna Karray", "Tunisia · Noir; Identity at Stake."),
]

# The artist pages (Artist pages – template, 05 Website; Thomas, 10 November 2026). One entry per artist with a page; the
# template builds /about/artists/<slug>/ from it, and About links the artist's name to it. Works are shown whole (never
# cropped, filtered or under the pattern), credited to the artist and the series; never the archive's credit line.
# Rights: the exhibition agreement gives Africa Reframed and Commerce & Culture perpetual rights to publish the images of the
# artists shown at Øksnehallen (Thomas, 10 November 2026). Files: assets/artists/<slug>/, web versions at 2,000 and 1,000 px
# made from the originals (the masters and portraits are in the exhibition folder, to move into 11 Media library / 01 Artists).
# The facts box says what a museum label would: the artist's copyright, the gallery's courtesy where there is one, and for
# the artists shown at Øksnehallen why the works are here. Nothing that suggests a relationship with Africa Reframed
# (Thomas, 10 November 2026: no "by agreement", no "With Africa Reframed", no partners).
EXHIBITION = "Africa Reframed, Øksnehallen, Copenhagen, 2016"


def artist_rights(a):
    line = f"All images © {a['name']}."
    if a.get("courtesy"):
        line += f" {a['courtesy']}."
    if a["group"] == "films":
        return f"Stills © the films’ producers, with the photographer where known. Shown here because these films were part of the exhibition {EXHIBITION}."
    if a["group"] == "shown":
        line += f" Shown here because these works were part of the exhibition {EXHIBITION}."
    elif a["group"] == "network":
        line += f" Shown here as part of the {NETWORK}."
    return line


def artist_credit(a):
    if a["group"] == "films":
        return "Stills © the films’ producers"
    return f"© {a['name']}" + (f" · {a['courtesy']}" if a.get("courtesy") else "")
ARTISTS = [  # generated by the copy review of 10 November 2026; edit the lines here (the sources are in each src)
    dict(slug='omar-victor-diop',
         name='Omar Victor Diop',
         group='shown',
         country='Senegal',
         courtesy='Courtesy MAGNIN-A, Paris',
         card_focus=(0.571, 0.357),
         src=("MAGNIN-A's list of the works chosen (titles, years, the courtesy line); the exhibition's wall labels (2016); the artist's profile on the African "
             'Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas chose there); the 2016 catalogue '
             '(facts only). Born 1980 (catalogue, MAGNIN-A); the labels say 1981.'),
         line='Portraits and self-portraits that bring African history into the present.',
         text=['Omar Victor Diop was born in Dakar, Senegal, in 1980, and is a self-taught photographer. He studied at business school in Paris and worked in '
              'finance and corporate communications before he turned to photography full time in 2012, the year after his series The Future of Beauty was shown '
              'at the Bamako Biennale.',
              'His work joins photography with costume, styling and writing, and follows the West African studio portraitists who made the staged portrait their '
              'own.'],
         facts=[('Origin', 'Senegal'), ('Works in', 'Photography'), ('Series shown', 'Diaspora · Le Studio des Vanités'), ('Gallery', 'MAGNIN-A, Paris')],
         website=('omarviktor.com', 'https://www.omarviktor.com'),
         lead={'file': 'diaspora-albert-badin', 'title': 'Albert Badin', 'series': 'Diaspora', 'w': 667, 'h': 1000},
         series=[{'title': 'Diaspora',
                 'line': 'Made in 2014 and 2015: self-portraits in which Diop takes the place of Africans who made their mark in Europe and beyond between the '
                         'fifteenth and the nineteenth century, among them envoys, scholars, soldiers and a saint. Each is staged after an original portrait of the '
                         'figure, with an object from football added, which ties their stories to the place of Africans in Europe today.',
                 'works': [('diaspora-august-sabac-el-cher', 'August Sabac El Cher', 2362, 3543),
                           ('diaspora-malick-ambar', 'Malick Ambar', 2492, 3543),
                           ('diaspora-omar-ibn-said', 'Omar Ibn Said', 2362, 3543),
                           ('diaspora-jean-baptiste-belley', 'Jean-Baptiste Belley', 667, 1000)]},
                {'title': 'Le Studio des Vanités',
                 'line': 'Begun in 2011: portraits of figures from the young creative scene of Dakar and other African cities, made in the manner of the great '
                         'studio photographers. The backdrops are textiles from his mother’s collection, handed down through generations and chosen for their '
                         'colours and patterns.',
                 'works': [('vanites-adama', 'Adama', 1600, 1600),
                           ('vanites-aminata', 'Aminata', 1600, 1600),
                           ('vanites-selly', 'Selly', 1666, 2500),
                           ('vanites-oumy-ndour', 'Oumy Ndour', 2000, 3000)]}],
         note=('Text and series lines are draft. The lead (Albert Badin) and Jean-Baptiste Belley exist here only at 1,000 px: MAGNIN-A can send larger files. '
              'Website from his own profile (2014) and the catalogue, to confirm.')),
    dict(slug='namsa-leuba',
         name='Namsa Leuba',
         group='shown',
         country='Switzerland and Guinea',
         card_focus=(0.507, 0.241),
         src=("her biography (exhibition folder, 2016); namsaleuba.com (the series, read 10 November 2026); the artist's profile on the African Photography "
             'Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas chose there); the 2016 catalogue (facts only).'),
         line='Staged photographs that look at African identity through Western eyes.',
         text=['Namsa Leuba was born in 1982 to a Guinean mother and a Swiss father, and grew up by Lake Neuchâtel in Switzerland. She studied photography and art '
              'direction at ECAL, the University of Art and Design Lausanne.',
              'Spanning documentary, fashion and performance, she stages the signs and symbols of her heritage, from rituals and ceremonies to statuettes and '
              'masquerades, with careful attention to props, colours and gestures, and questions the line between fact and fiction, the sacred and the profane.'],
         facts=[('Origin', 'Switzerland and Guinea'), ('Works in', 'Photography'), ('Series shown', 'Khoisan · The Kingdom of Mountains · Zulu Kids')],
         website=('namsaleuba.com', 'https://www.namsaleuba.com'),
         lead={'file': 'khoisan-chunara', 'title': 'Chunara', 'series': 'Khoisan', 'w': 4135, 'h': 5079},
         series=[{'title': 'Khoisan',
                 'line': 'Made in 2014 in the Northern Cape, South Africa. Where her other series invent their own blend of cultures, Khoisan draws on the '
                         'traditions of the Khoisan people themselves. Clothing, props and accessories take over the figures, and the photographs sit between '
                         'documentary and fashion.',
                 'works': [('khoisan-keala', 'Keala', 4134, 5079),
                           ('khoisan-koos', 'Koos', 4134, 5078),
                           ('khoisan-chunara', 'Chunara', 4135, 5079),
                           ('khoisan-maria', 'Maria', 4134, 5079),
                           ('khoisan-kokos', 'Kokos', 4134, 5079)]},
                {'title': 'The Kingdom of Mountains',
                 'line': 'Made in 2014 around the Katse Dam in Lesotho, during a six-month residency in South Africa. Leuba staged the clothes and accessories of '
                         'the people who live there in the landscape around them: performative portraits rather than documents, on how African traditions are '
                         'translated into Western images.',
                 'works': [('kingdom-of-mountains-owesifazane', 'Owesifazane', 4133, 5086),
                           ('kingdom-of-mountains-umntanenkosi', 'Umntanenkosi', 4347, 5350),
                           ('kingdom-of-mountains-qkhwini', 'Qkhwini', 4351, 5355),
                           ('kingdom-of-mountains-sangoma', 'Sangoma', 4334, 5334)]},
                {'title': 'Zulu Kids',
                 'line': 'Made in 2014 with children in KwaZulu-Natal and Soweto, South Africa, following her series Ya Kala Ben, made in Guinea. The children pose '
                         'on wooden logs like statuettes, a tradition Leuba invented, since statuettes have no place in Zulu culture; Zulu, West African and '
                         'European signs are layered in each image.',
                 'works': [],
                 'pending': 'The three works shown follow when Thomas has exported them from the masters at about 2,000 px.'}],
         note='Text and series lines are draft, from her biography (2016), the exhibition catalogue (2016) and namsaleuba.com, read 10 November 2026.'),
    dict(slug='fabrice-monteiro',
         name='Fabrice Monteiro',
         group='shown',
         country='Benin and Belgium',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there); the 2016 catalogue (facts only).'),
         line='Photographs on the environment and the history of West Africa, made with the craft of fashion photography.',
         text=['Fabrice Monteiro was born in 1972 to a Beninese father and a Belgian mother, grew up in Benin and lives in Dakar. He worked as a model for ten '
              'years before he turned to photography, encouraged by the New York photographer Alfonse Pagano, whom he met in 2007.',
              'Between photojournalism, fashion and portraiture, he builds staged scenes in which the history and the present of West Africa meet.'],
         facts=[('Origin', 'Benin and Belgium, lives in Senegal'), ('Works in', 'Photography'), ('Series shown', 'The Prophecy · A Gorean Summer')],
         lead={'file': 'prophecy-3', 'title': None, 'series': 'The Prophecy', 'w': 2500, 'h': 1669},
         series=[{'title': 'The Prophecy',
                 'line': 'Made in 2013 with the costume designer Doulsy and the organisation Ecofund. Figures in costumes made from the waste found at each site '
                         'stand in polluted places across Senegal, like the djinns of West African tradition: spirits that warn of what is being done to the land.',
                 'works': [('prophecy-1', None, 2500, 1669), ('prophecy-2', None, 2500, 1669), ('prophecy-5', None, 2500, 1669), ('prophecy-6', None, 2500, 1669)]},
                {'title': 'A Gorean Summer',
                 'line': 'Made in 2012 on Gorée, the island off Dakar remembered as a place of the Atlantic slave trade and visited today by tourists from all over '
                         'the world. The series looks at what happens when memory and tourism meet in the same place.',
                 'works': [('gorean-summer-1', None, 2500, 1685),
                           ('gorean-summer-3', None, 2500, 1663),
                           ('gorean-summer-5', None, 2500, 1667),
                           ('gorean-summer-7', None, 2500, 1667)]}],
         note=('Text and series lines are draft. Images from his profile on commerceandculture.org, at 2,500 px (the exhibition folder has only small files). The '
              'works are untitled here: their titles, if they have them, to add. Website to find: he is now with MAGNIN-A, Paris.')),
    dict(slug='dillon-marsh',
         name='Dillon Marsh',
         group='shown',
         country='South Africa',
         courtesy='Courtesy Gallery MOMO',
         src=("the exhibition's wall labels (2016) (the series, years and the courtesy line); the artist's profile on the African Photography Network (archived "
             '2014–2023); the profile on commerceandculture.org (images, and the lead Thomas chose there); the 2016 catalogue (facts only).'),
         line='Photographs of the landscapes of southern Africa and the marks people leave on them.',
         text=['Dillon Marsh was born in Cape Town in 1981 and graduated in fine art from the University of Stellenbosch in 2003, where he turned to photography. '
              'He has also worked as a retoucher, and brings computer-generated imagery into some of his photographs to show what the camera alone cannot.',
              'His series pick out what is out of the ordinary in a landscape, often one kind of object that recurs, a family of things that would otherwise '
              'blend in, and photograph it place by place.'],
         facts=[('Origin', 'South Africa'),
               ('Works in', 'Photography'),
               ('Series shown', 'For What It’s Worth · Assimilation · Common Ground'),
               ('Gallery', 'Gallery MOMO')],
         lead={'file': 'central-rand-goldfield', 'title': 'Central Rand Goldfield', 'series': 'For What It’s Worth', 'w': 1500, 'h': 1200},
         series=[{'title': 'For What It’s Worth',
                 'line': 'Made in 2014 at mines across South Africa, from the copper mines of Namaqualand and the diamond mines of the Northern Cape to the gold '
                         'fields of the Witwatersrand. Into each photograph Marsh sets a sphere made with computer graphics, the size of all the metal or diamonds '
                         'the mine has produced, beside the place it came from.',
                 'works': [('copperton-mine', 'Copperton Mine', 2500, 2000),
                           ('kimberley-mine', 'Kimberley Mine', 2500, 2000),
                           ('koffiefontein-mine', 'Koffiefontein Mine', 2500, 2000),
                           ('east-rand-goldfield', 'East Rand Goldfield', 2500, 2000)]},
                {'title': 'Assimilation',
                 'line': 'Made in 2010 in the southern Kalahari, where sociable weaver birds take over the telephone poles that cross their habitat. Their nests of '
                         'twigs and grass are as still as statues and full of life, and give the poles strangely recognisable personalities.',
                 'works': [('assimilation-1', None, 2500, 2000),
                           ('assimilation-3', None, 2500, 2000),
                           ('assimilation-5', None, 2500, 2000),
                           ('assimilation-8', None, 2500, 2000)]},
                {'title': 'Common Ground',
                 'line': 'Made in 2013 in Gaborone, Botswana, where people and termites share the same neighbourhoods. The mounds rise as high as the houses around '
                         'them, around trees and between parked cars, and are a resource too: their clay is used as a mineral supplement.',
                 'works': [('common-ground-1', None, 5811, 4649),
                           ('common-ground-3', None, 5811, 4649),
                           ('common-ground-10', None, 5811, 4649),
                           ('common-ground-12', None, 5811, 4649)]}],
         note='Text and series lines are draft. Website from his own profile (2014), to confirm.'),
    dict(slug='lien-botha',
         name='Lien Botha',
         group='shown',
         country='South Africa',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there); the 2016 catalogue (facts only).'),
         line='Photographs of place and memory, from a practice that spans photography, printmaking and sculpture.',
         text=['Lien Botha was born in Gauteng, South Africa, in 1961. She worked as a press photographer for the daily Beeld before she moved to Cape Town in '
              '1984, where she took a degree in fine art at the Michaelis School of Fine Art in 1988.',
              'She works in photography, printmaking, painting and sculpture, and returns to the places of daily life to find in their details the traces of '
              'personal and shared memory.'],
         facts=[('Origin', 'South Africa'), ('Works in', 'Photography, printmaking and sculpture'), ('Series shown', 'Parrot Jungle')],
         lead={'file': 'parrot-jungle-lead', 'title': None, 'series': 'Parrot Jungle', 'w': 1500, 'h': 1000},
         series=[{'title': 'Parrot Jungle',
                 'line': 'Made in 2009: a disrupted road trip on the coast road between Betty’s Bay and Cape Town, returning to the places missed on the way to '
                         'somewhere else: roadkill, people walking, stray dogs, the road gone under the rain. Botha calls it a drive-by revisited. Part of the '
                         'series was shown at the Bamako Encounters in 2011.',
                 'works': [('parrot-jungle-01', None, 2500, 1666),
                           ('parrot-jungle-19', None, 2500, 1667),
                           ('parrot-jungle-27', None, 2500, 1667),
                           ('parrot-jungle-4422', None, 2500, 1813)]}],
         note=('Text and series line are draft. The lead is the image chosen on commerceandculture.org; that it belongs to Parrot Jungle is to confirm. Website '
              'from her own profile (2014), to confirm.')),
    dict(slug='tahir-carl-karmali',
         name='Tahir Carl Karmali',
         group='shown',
         country='Kenya',
         src=("the exhibition folder (the five works shown, as 1,500 px files named “Bamako Nights” by mistake); the artist's profile on the African Photography "
             'Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas chose there); the 2016 catalogue (facts only); '
             'okayafrica.com on Jua Kali.'),
         line='Digital composites built from found objects, between photography and installation.',
         text=['Tahir Carl Karmali was born in Kenya in 1987 and is based in Nairobi. He began as a painter, and took up the camera while he travelled and worked '
              'in Asia and Europe, first as a food and travel photographer.',
              'As an artist at the Kuona Trust in Nairobi he turned to conceptual work for photography and installation, building digital composites from found '
              'objects into surreal images.'],
         facts=[('Origin', 'Kenya'), ('Works in', 'Photography, mixed media and installation'), ('Series shown', 'Jua Kali')],
         lead={'file': 'jua-kali-lead', 'title': None, 'series': 'Jua Kali', 'w': 1001, 'h': 1500},
         series=[{'title': 'Jua Kali',
                 'line': 'Begun in 2014: portraits of creative workers in Nairobi’s informal economy, the jua kali, among them dancers, writers, designers and '
                         'sculptors. Each sitter was photographed outdoors in daylight, and each portrait is built up into a collage of objects Karmali gathered at '
                         'dump sites and recycling yards. The series asks whether the informal economy is the real power of the city.',
                 'works': [('jua-kali-3', None, 1001, 1500),
                           ('jua-kali-8', None, 1001, 1500),
                           ('jua-kali-11', None, 1001, 1500),
                           ('jua-kali-12', None, 1001, 1500)]}],
         note=('Text and series line are draft. The works are shown at 1,500 px; the masters (about 220 MB each) can replace them. Website from his own profile '
              '(2014), to confirm.')),
    dict(slug='yinka-ilori',
         name='Yinka Ilori',
         group='shown',
         country='Nigeria and the United Kingdom',
         src=('the profile on commerceandculture.org (images, and the lead Thomas chose there); the exhibition folder (Backbone, Helping Hand); the 2016 '
             'catalogue (facts only); design-milk.com on If Chairs Could Talk (2015).'),
         line='Furniture rebuilt from discarded chairs, telling the Nigerian parables of his childhood.',
         text=['Yinka Ilori was born in London in 1987 to Nigerian parents, and studied furniture and product design at London Metropolitan University.',
              'His work sits between art and design. He gives old chairs new life by joining parts of different chairs and adding textiles and colour, draws on '
              'the parables and the African fabrics he grew up with, and uses them to raise questions of hope, class and sexuality.'],
         facts=[('Origin', 'Nigeria and the United Kingdom'), ('Works in', 'Furniture and design'), ('Series shown', 'If Chairs Could Talk')],
         website=('yinkailori.com', 'https://yinkailori.com'),
         lead={'file': 'helping-hand', 'title': 'Helping Hand', 'series': 'If Chairs Could Talk', 'w': 3840, 'h': 5760},
         series=[{'title': 'If Chairs Could Talk',
                 'line': 'Made in 2015: chairs found and rebuilt, each telling a story drawn from a Nigerian parable. The collection was first shown at The Shop at '
                         'Bluebird in London, during the London Design Festival.',
                 'works': [('a-trapped-star', 'A Trapped Star', 1667, 2500),
                           ('captain-hook', 'Captain Hook', 1667, 2500),
                           ('flower-bomb', 'Flower Bomb', 1667, 2500),
                           ('backbone', 'Backbone', 3840, 5760)]}],
         note=('Text and series line are draft. The lead is a work, not the image chosen on commerceandculture.org, which is a portrait of him. That these chairs '
              'belong to If Chairs Could Talk is to confirm: the exhibition folder calls them his new collection.')),
    # From the network: the fourteen artists of the African Photography Network.
    dict(slug='osborne-macharia',
         name='Osborne Macharia',
         group='network',
         country='Kenya',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Staged photographs that bring African stories to life, with the finish of advertising.',
         text=['Osborne Macharia was born in Kenya and trained as an architect. A self-taught photographer, he works in commercial and advertising photography for '
              'brands and agencies in Kenya and abroad.',
              'Between commissions he works on personal projects: staged portraits, lit and composed with the care of an advertising shoot, each built around a '
              'story.'],
         facts=[('Origin', 'Kenya'), ('Works in', 'Photography')],
         lead={'file': 'work-00', 'title': None, 'series': 'Selected works', 'w': 1500, 'h': 1019},
         series=[{'title': 'Selected works',
                 'line': 'From his personal projects: elders and women in Maasai dress, lit as in a studio against a dark sky.',
                 'works': [('work-02', None, 1125, 1500), ('work-03', None, 1125, 1500), ('work-05', None, 1126, 1500), ('work-06', None, 1126, 1500)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find. The series these works come from is to name.'),
    dict(slug='elise-fitte-duval',
         name='Élise Fitte-Duval',
         group='network',
         country='Martinique and Senegal',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Photographs of contemporary dance in Africa, followed from the rehearsal room to the stage.',
         text=['Élise Fitte-Duval was born in Martinique and has lived in Senegal for many years. She studied at the École d’Arts Plastiques in Martinique and at '
              'the École Nationale Supérieure des Arts Décoratifs in Paris.',
              'In 2011 Casa África named her best female African photographer at the Bamako Encounters for Vivre les pieds dans l’eau, her series on the floods '
              'in Dakar.'],
         facts=[('Origin', 'Martinique, lives in Senegal'), ('Works in', 'Photography'), ('Series', 'Danser l’Espoir')],
         lead={'file': 'work-00', 'title': None, 'series': 'Danser l’Espoir', 'w': 1500, 'h': 1000},
         series=[{'title': 'Danser l’Espoir',
                 'line': 'An ongoing project since 2003: Fitte-Duval follows contemporary dancers from across the continent in their work sessions, offstage as '
                         'well as on, to show how the art is made and how it is changing.',
                 'works': [('work-01', None, 1500, 1000), ('work-02', None, 1500, 1000), ('work-03', None, 1500, 1000)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='fatoumata-diabate',
         name='Fatoumata Diabaté',
         group='network',
         country='Mali',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Photographs of youth, style and the night in Bamako and other cities.',
         text=['Fatoumata Diabaté was born in Bamako, Mali, in 1980. She trained there at the Centre de Formation Audiovisuel Promo-Femmes and, from 2002, at the '
              'Centre de Formation en Photographie.',
              'In 2005 her series Touaregs, en gestes et en mouvements won the Prix Afrique en Création of the Institut Français and was shown at the sixth '
              'Bamako Encounters.'],
         facts=[('Origin', 'Mali'), ('Works in', 'Photography'), ('Series', 'Sutigi')],
         lead={'file': 'work-00', 'title': None, 'series': 'Sutigi', 'w': 1500, 'h': 1000},
         series=[{'title': 'Sutigi',
                 'line': 'The night is ours. Begun in Bamako while she was training, and continued in other cities: young women, her friends among them, '
                         'photographed at night in the clothes they go out in, in the streets, cultural centres and clubs. For Diabaté, the night is when the young '
                         'feel most at ease.',
                 'works': [('work-01', None, 1500, 1000), ('work-03', None, 1500, 1000), ('work-04', None, 1500, 1000), ('work-06', None, 1500, 1000)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='isaac-kasamani',
         name='Isaac Kasamani',
         group='network',
         country='Kenya and Uganda',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Photojournalism of Uganda’s politics, from the middle of the protests.',
         text=['Isaac Kasamani is a photojournalist, born and raised in Kenya, who works freelance in Uganda. He trained at the Daily Monitor, Uganda’s leading '
              'independent daily, and works for it and for Agence France-Presse.',
              'Most of his work is political: protests, unrest and the events of public life, photographed from close in, where the confrontation is.'],
         facts=[('Origin', 'Kenya, works in Uganda'), ('Works in', 'Photojournalism')],
         lead={'file': 'work-00', 'title': None, 'series': 'Selected works', 'w': 1500, 'h': 1007},
         series=[{'title': 'Selected works',
                 'line': 'Protests in Uganda and their policing: the crowd, the fires, the riot police.',
                 'works': [('work-02', None, 1500, 1007), ('work-03', None, 1500, 996), ('work-04', None, 1500, 996), ('work-05', None, 1500, 1056)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='antonia-steyn',
         name='Antonia Steyn',
         group='network',
         country='South Africa',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Portraits of South African figures, made with a strong sense of staging.',
         text=['Antonia Steyn graduated from the University of Cape Town in 2000 and has worked as a professional photographer since 2005, in portraiture and in '
              'campaigns for advertising clients.',
              'Her portrait of the satirist Pieter-Dirk Uys won her Media24 Photographer of the Year in 2007, and her triptych Steyn & De Villiers the Vuleka Art '
              'Award in 2011.'],
         facts=[('Origin', 'South Africa'), ('Works in', 'Photography')],
         lead={'file': 'work-00', 'title': None, 'series': 'Selected works', 'w': 1500, 'h': 1125},
         series=[{'title': 'Selected works',
                 'line': 'Portraits set in the landscape: figures photographed in fields and cemeteries, under heavy skies.',
                 'works': [('work-01', None, 1500, 1126), ('work-03', None, 1500, 1199), ('work-04', None, 1500, 1200), ('work-05', None, 1500, 1199)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='ala-kheir',
         name='Ala Kheir',
         group='network',
         country='Sudan',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Photographs of cities, landscapes and everyday life, in Sudan and beyond.',
         text=['Ala Kheir was born in Nyala, in south-western Sudan, in 1985, and has photographed since he bought his first camera in 2005.',
              'He keeps to no single subject and photographs everything around him, inspired by the American photographer Robert Adams. His work has been shown '
              'at the Addis Foto Fest, with a solo exhibition in 2012, and in New York, Kuala Lumpur and Khartoum.'],
         facts=[('Origin', 'Sudan'), ('Works in', 'Photography')],
         lead={'file': 'work-00', 'title': None, 'series': 'Selected works', 'w': 1500, 'h': 1000},
         series=[{'title': 'Selected works',
                 'line': 'Streets, buildings and open land.',
                 'works': [('work-01', None, 1500, 1000), ('work-02', None, 1500, 1000), ('work-03', None, 1500, 1000), ('work-05', None, 1500, 885)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='adeola-olagunju',
         name='Adeola Olagunju',
         group='network',
         country='Nigeria',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Performance photographs that answer social, political and religious decay.',
         text=['Adeola Olagunju lives and works in Lagos. She graduated in fine and applied arts from Ladoke Akintola University of Technology in 2009, and '
              'received the LagosPhoto award in 2012 and the Young ArtFund Amsterdam award in 2013.',
              'Her work is mostly performance for the camera, through which she questions stereotypes and the state of society.'],
         facts=[('Origin', 'Nigeria'), ('Works in', 'Photography and performance'), ('Series', 'Resurgence: A Manifesto')],
         lead={'file': 'work-00', 'title': None, 'series': 'Resurgence: A Manifesto', 'w': 1500, 'h': 1000},
         series=[{'title': 'Resurgence: A Manifesto',
                 'line': 'Performances for the camera in abandoned industrial places: a refusal of the social, political and religious decay Olagunju sees around '
                         'her, and a call to wake from it.',
                 'works': [('work-01', None, 1500, 1000), ('work-02', None, 1500, 1000), ('work-03', None, 1500, 1000), ('work-05', None, 1500, 1000)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='jon-riordan',
         name='Jon Riordan',
         group='network',
         country='South Africa',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Landscapes of South Africa, read for the history that lies in them.',
         text=['Jon Riordan was born in Port Elizabeth in 1981 and lives in Cape Town. He studied photojournalism, and took a master’s degree in documentary arts '
              'at the University of Cape Town under Paul Weinberg.',
              'He photographs everyday surroundings rather than the personal, guided by Simon Schama’s idea that landscape is built up from layers of memory as '
              'much as of rock: in South Africa, the past is visible in the present.'],
         facts=[('Origin', 'South Africa'), ('Works in', 'Photography')],
         lead={'file': 'work-00', 'title': None, 'series': 'Selected works', 'w': 1500, 'h': 1001},
         series=[{'title': 'Selected works',
                 'line': 'Open land on the edges of Cape Town: grass, rubbish, a sofa left behind, washing on a line.',
                 'works': [('work-02', None, 1500, 994), ('work-06', None, 1500, 992), ('work-09', None, 1500, 1001), ('work-13', None, 1500, 1001)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='mpho-mokgadi',
         name='Mpho Mokgadi',
         group='network',
         country='South Africa',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Black-and-white photographs on film, a diary of the people and places around him.',
         text=['Mpho Mokgadi is a photographer based in Johannesburg. He has photographed since childhood, when his mother gave him a film camera, and works only '
              'on film.',
              'His photographs are personal: scenes and people as he meets them, kept as a visual diary.'],
         facts=[('Origin', 'South Africa'), ('Works in', 'Photography, on film')],
         lead={'file': 'work-00', 'title': None, 'series': 'Selected works', 'w': 1346, 'h': 1346},
         series=[{'title': 'Selected works',
                 'line': 'Portraits and interiors in black and white.',
                 'works': [('work-01', None, 1500, 1498), ('work-03', None, 1500, 1500), ('work-05', None, 1434, 1500), ('work-07', None, 1500, 1498)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='charles-okereke',
         name='Charles Okereke',
         group='network',
         country='Nigeria',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Photographs close to abstraction, on people and the environment.',
         text=['Charles Okereke was born in Kano, in northern Nigeria, in 1966. He works in painting, photography, sculpture and furniture design, from research '
              'into people and the environment.',
              'He is a member of the Black Box photography collective and a founding member of Invisible Borders, the trans-African photographers’ road trip. His '
              'work has been shown at the Bamako Encounters and at Skoto Gallery in New York, both in 2013.'],
         facts=[('Origin', 'Nigeria'), ('Works in', 'Photography, painting, sculpture and design')],
         lead={'file': 'work-00', 'title': None, 'series': 'Selected works', 'w': 1500, 'h': 1000},
         series=[{'title': 'Selected works',
                 'line': 'Traces pressed into the ground, a figure against the sky, forms like planets: photographs that come close to abstraction and ask for a '
                         'second look.',
                 'works': [('work-01', None, 1500, 1000), ('work-02', None, 1500, 1000), ('work-03', None, 1500, 1001), ('work-04', None, 1500, 1000)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='helene-amouzou',
         name='Hélène Amouzou',
         group='network',
         country='Togo and Belgium',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Self-portraits on film, made in long exposures while she waited for asylum in Belgium.',
         text=['Hélène Amouzou was born in Togo in 1969 and lives in Molenbeek, Belgium. She works on film, and lets chance into her long exposures.',
              'Self-portraiture is, in her words, a way of writing without words. She has drawn on the work of the American photographer Francesca Woodman.'],
         facts=[('Origin', 'Togo, lives in Belgium'), ('Works in', 'Photography')],
         lead={'file': 'work-00', 'title': None, 'series': 'Self-portraits', 'w': 1500, 'h': 1458},
         series=[{'title': 'Self-portraits',
                 'line': 'Made over two years while she went through the asylum process in Belgium and waited for her residence permit. In bare rooms with peeling '
                         'floral wallpaper, she, her clothes and often a suitcase appear as ghostly traces, between absence and presence.',
                 'works': [('work-01', None, 1453, 1500), ('work-02', None, 1483, 1500), ('work-03', None, 1477, 1500), ('work-05', None, 1500, 1430)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='sydelle-willow-smith',
         name='Sydelle Willow Smith',
         group='network',
         country='South Africa',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Photographs and films on memory, home and migration.',
         text=['Sydelle Willow Smith was born in Johannesburg in 1987 and is based in Cape Town. She trained at the Market Photo Workshop, and took degrees in '
              'social anthropology and in video production at the University of Cape Town.',
              'Her photographs and films follow people and the places they make home, with a focus on memory, placemaking and migration.'],
         facts=[('Origin', 'South Africa'), ('Works in', 'Photography and film')],
         lead={'file': 'work-00', 'title': None, 'series': 'Selected works', 'w': 1500, 'h': 1000},
         series=[{'title': 'Selected works',
                 'line': 'Homes, streets and gatherings: the private and public places where people make a life.',
                 'works': [('work-01', None, 1500, 1000), ('work-03', None, 1500, 1000), ('work-04', None, 1500, 959), ('work-08', None, 1500, 984)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='jac-kritzinger',
         name='Jac Kritzinger',
         group='network',
         country='South Africa',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Art, documentary and portrait photographs that look for what lies behind the everyday.',
         text=['Jac Kritzinger was born in Cape Town in 1976 and turned to photography after an honours degree in film studies. He works in art, documentary and '
              'portrait photography.',
              'He calls himself a poet before a photographer, and looks, with a sense of humour, for what shines behind the confines of everyday reality.'],
         facts=[('Origin', 'South Africa'), ('Works in', 'Photography')],
         lead={'file': 'work-00', 'title': None, 'series': 'Selected works', 'w': 1500, 'h': 995},
         series=[{'title': 'Selected works',
                 'line': 'A figure in the air, a dead tree, a frame standing in an empty field: everyday scenes, turned slightly strange.',
                 'works': [('work-02', None, 1500, 998), ('work-03', None, 1500, 998), ('work-04', None, 1500, 998), ('work-05', None, 1500, 998)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
    dict(slug='mouna-karray',
         name='Mouna Karray',
         group='network',
         country='Tunisia',
         src=("the artist's profile on the African Photography Network (archived 2014–2023); the profile on commerceandculture.org (images, and the lead Thomas "
             'chose there).'),
         line='Photographs on identity, memory and constraint.',
         text=['Mouna Karray was born in Sfax, Tunisia, in 1970, and took an MA in image media at the Tokyo Institute of Polytechnics and Arts in 2002. She lives '
              'and works between Sfax and Paris.',
              'Her work has been shown at the Bamako Encounters in 2011 and at Photoquai, at the Musée du Quai Branly in Paris, in 2009.'],
         facts=[('Origin', 'Tunisia'), ('Works in', 'Photography'), ('Series', 'Noir · Identity at Stake')],
         lead={'file': 'work-00', 'title': None, 'series': 'Noir', 'w': 1500, 'h': 1500},
         series=[{'title': 'Noir',
                 'line': 'Made in 2013. Her body hidden in a white sack, only her hand and the cable release showing: the act of photographing becomes, in her '
                         'words, a way to get free.',
                 'works': [('work-02', None, 1500, 1500), ('work-03', None, 1500, 1500)]},
                {'title': 'Identity at Stake',
                 'line': 'Made in 2005. Karray photographs women in their own surroundings, then takes their place in the same setting, in their clothes and with '
                         'their gestures: the resemblance is sought, and in the end, in her words, the difference is revealed.',
                 'works': [('work-04', None, 1500, 1500), ('work-05', None, 1500, 1500), ('work-06', None, 1500, 1500), ('work-07', None, 1500, 1500)]}],
         note='Text and series lines are draft, from the profile on commerceandculture.org. Website to find.'),
]
# The films at Øksnehallen (Thomas, 10 November 2026): ChiChia's card on About gives way to the film programme, so the grid stays
# eight. One page, on the artist template, between the exhibition artists and the network when browsing. Every film screened
# is listed (the 2016 catalogue, pp. 8-12); stills only where we have them (the exhibition folder, Movies / Stills), credited;
# no trailers and no links out (no agreements with the producers cover more, and visitors stay on the site).
FILMS = dict(slug="films", path="about/films/", name="Films at Øksnehallen", group="films",
             src="the 2016 catalogue (the programme, pp. 8-12; facts only); the stills in the exhibition folder (Movies / Stills)",
             line="Two cinemas in the hall: documentaries every day, and a feature film every Wednesday evening.",
             text=["Alongside the works, the exhibition ran two cinemas in Øksnehallen. The documentary cinema showed a daily programme on "
                   "Africa’s creative scenes, from music and dance to film and art; from 22 June to 27 July 2016 the feature-film theatre "
                   "showed a new film every Wednesday evening.",
                   "The films are listed here as they were screened, with stills from four of the Wednesday films."],
             facts=[("Cinemas", "Two, in the hall"), ("Documentaries", "Every day"), ("Feature films", "Wednesday evenings, 22 June to 27 July 2016")],
             lead=dict(file="run", title="Run, Philippe Lacôte, 2014", series=None, credit="Photo: F. Regairaz", w=5184, h=3456),
             series=[
                 dict(title="Every day: the documentary cinema", line="Documentaries and a series on the continent’s creative scenes, shown in turn through the day.",
                      works=[],
                      films=[("Afripedia", "Teddy Goitom, Benjamin Taft and Senay Berhe, Stocktown Films, 2014",
                              "A documentary series in five parts on the rising creative generation in Ghana, Kenya, South Africa, Senegal and Angola."),
                             ("A Kind of Paradise", "Andreas Johnsen, Denmark, 2011",
                              "Africa’s cultural voices, from Chimamanda Ngozi Adichie to artists, poets and musicians in six countries."),
                             ("Black President", "Mpumelelo Mcata, Zimbabwe, South Africa and the United Kingdom, 2015",
                              "The exiled Zimbabwean artist Kudzanai Chiurai, and the responsibility of African artists in a globalised art world."),
                             ("This Is Nollywood", "Franco Sacchi and Robert Caputo, Nigeria, 2007",
                              "The Nigerian film industry, followed through the director Bond Emeruwa’s attempt to make a feature film in nine days."),
                             ("Movement (R)evolution Africa", "Joan Frosch and Alla Kovgan, 2007",
                              "Contemporary African choreographers at work in the studio and on stage, among them Germaine Acogny and Faustin Linyekula."),
                             ("El Foukr R’Assembly", "Oualid Khelifi, Algeria, 2014",
                              "A short film on a group of Algerian musicians, and on music that links the Maghreb with the rest of the continent."),
                             ("An African City, season 1", "Nicole Amarteifio, Ghana, 2014",
                              "A web series on five Ghanaian and Nigerian women who return to the continent.")]),
                 dict(title="Wednesday evenings: the feature films", line="From 22 June to 27 July 2016, one film each Wednesday at 7 pm, opening with "
                      "a pre-screening of BUGS with its director present.",
                      works=[("ayanda", "Ayanda, Sara Blecher, 2015", 5616, 3744), ("necktie-youth", "Necktie Youth, Sibs Shongwe-La Mer, 2015", 2303, 1535),
                             ("crumbs", "Crumbs, Miguel Llansó, 2015", 1422, 800)],
                      films=[("BUGS", "Andreas Johnsen, Denmark, 2016", "Insects as food, and whether they can mend our broken food systems."),
                             ("Run", "Philippe Lacôte, Côte d’Ivoire, 2014",
                              "A man on the run after killing his country’s prime minister, his past returning in flashes through the years of conflict."),
                             ("Necktie Youth", "Sibs Shongwe-La Mer, South Africa, 2015",
                              "Shot in black and white: middle-class youth in Johannesburg, a year after a friend’s death."),
                             ("Crumbs", "Miguel Llansó, Ethiopia, 2015", "Ethiopian science fiction: a small man’s surreal journey through post-apocalyptic landscapes."),
                             ("Ayanda", "Sara Blecher, South Africa, 2015",
                              "A young woman brings her late father’s garage back to life, in a neighbourhood of migrants from across the continent."),
                             ("Mukwano", "Cecilie McNair, Denmark, 2016",
                              "An asylum seeker from Uganda searches for the girlfriend she lost on their escape.")]),
             ],
             note="Text and lines are draft, from the 2016 catalogue. Stills © the films’ producers; Mukwano’s still is in the folder but left out, "
                  "so that the row of stills stays in threes.")
# Browsing from page to page follows About: the exhibition artists, the films, then the African Photography Network.
NAV = [a for a in ARTISTS if a["group"] == "shown"] + [FILMS] + [a for a in ARTISTS if a["group"] == "network"]
ARTIST_BY_NAME = {a["name"]: a for a in ARTISTS + [FILMS]}


# 3 Workshops: the activity, then the projects, the voices, Bamako Nights, the partners
ABOUT_WORKSHOPS_LONG = [   # the wording until 11 November 2026, 15:00, kept
    "We connect African photographers with the international picture market, so that their own stories of the continent travel. Our workshops are built with photography schools, photographers’ unions and press associations, with a funder and a market partner in the same programme, so that training leads to work that sells, and to income.",
    "Photographers learn what buyers look for, how to brief and shoot for it, and how their work is licensed.",
]
ABOUT_WORKSHOPS_1500 = [   # the wording from 15:00 to 15:20 on 11 November 2026, kept
    "We connect African photographers with the international picture market, so that their own stories of the continent travel.",
    "Our workshops are built with photography schools, photographers’ unions and press associations, with a funder and a market partner in the same programme, so that training leads to work that sells, and to income.",
]
# The area, then its proof, as for Exhibitions (Thomas, 11 November 2026, 15:14 and 15:18). A draft for Thomas.
ABOUT_WORKSHOPS = [
    "We connect African photographers with the international picture market, so that their own stories of the continent travel.",
    "Our workshops are built with photography schools, photographers’ unions and press associations, with a funder and a market partner in the same programme, so that training leads to work that sells. In Bamako the programme ran for six years with the school CFP Bamako and Getty Images: the students’ images were licensed by EY, NBC, Pearson and Orange, among others, and two were chosen for the campaign that launched the UN Global Goals.",
]
WORKSHOP_PROJECTS = [  # strongest first; a new workshop is one more entry, shown first while in production or open
    dict(title="CFP Bamako and Getty Images", state="record", layout="side",
         image="Photography students at CFP Bamako", credit="Photo: Africa Reframed",
         caption="Photography students at CFP Bamako. The programme was funded through the Danish Embassy in Mali.",
         text_1500=["Our first workshop programme ran for six years with the photography school CFP Bamako and Getty Images, funded through the Danish Embassy in Mali. Students licensed their work through Getty while still in training.",
               "Their images were licensed by EY, NBC, Cambridge University Press, McKinsey & Company, Pearson, Orange and Vodacom, among others. Two were chosen for Tell Everyone, the campaign that launched the UN Global Goals."],
         text_long=["Our first workshop programme ran for six years with the photography school CFP Bamako and Getty Images, funded through the Danish Embassy in Mali. Students photographed for the world market and licensed their work through Getty while still in training, with feedback from Getty’s creative team.",
               "Their images were licensed by EY, NBC, Cambridge University Press, McKinsey & Company, Pearson, Orange and Vodacom, among others. Two of them were chosen for Tell Everyone, the campaign that launched the UN Global Goals and one of the largest ever run: the students’ own picture of Mali, carried to a global audience. An independent review for the Danish Centre for Culture and Development found that the programme “promotes positive images of Africa, moving away from editorial or ‘development’ photography”."],
         note="Tell Everyone: Case story – Getty Images and the UN Global Goals (2015). The students are not named, to spare them trouble at the school (Thomas)."),
]
ABOUT_INTERVIEWS = [("Aboubacar Traoré", "Photographer and teacher, CFP Bamako.", "Film: plays on click"),
                    ("Massaran Diankoumba", "Photographer, CFP Bamako.", "Film: plays on click"),
                    ("John Kalapo", "Photographer, CFP Bamako.", "Film: plays on click")]
BAMAKO_NIGHTS = ("An artistic project with the students: Bamako at night, in dialogue with Seydou Keïta and Malick Sidibé, "
                 "who photographed the city in its first years of independence. Shown at Øksnehallen.")
WORKSHOP_PARTNERS = [  # the network of workshop partners, by name and place; no years
    ("Sierra Leone Union of Photographers", "Freetown. A workshop on the market for photographers’ work."),
    ("Photojournalists Association of Kenya", "Nairobi, at PAWA254. A master class for young photographers."),
    ("Gambia Press Union", "Banjul. A week of visual storytelling."),
    ("Gambia Tourism and Hospitality Institute", "Banjul. Three months of shooting with local photographers."),
    ("The Africa Reframed team in Nairobi", "Kenyan photographers, brought together in a workshop."),
]
ABOUT_WORKSHOPS_TO_COLLECTION = "The House Collection was photographed by our team alongside the workshops."

# Supporters (Thomas, 10 November 2026): the institutions that helped build Africa Reframed's work, shown as one-colour logos
# at equal size, strongest first, directly under the overview, so the page does not read as work done alone. "Has been
# supported by": true without dates, never "is supported by" (ongoing) or "sponsored by". Africa Reframed's own projects only
# (Afghan Tales and Commerce & Culture's other work stay off the site); funders and in-kind support, never clients, buyers of
# the images or campaigns that used them. A future sponsor is one more entry. Order set by Thomas, 10 November 2026.
# CKU is left out (closed). Canon only if it supported Øksnehallen 2016: the Track Record finds its paper for Afghan Tales (2014)
# and, for 2016, only an invoice for inks. Sources: Track Record (Recognition, funding and media; the Øksnehallen, Stock Program
# and workshop entries).
SUPPORTERS_TITLE = "Our work has been supported by"
# The logo files (assets/supporters/) were taken on 10 November 2026 from each organisation's own website, the logo in its
# header, unaltered (Augustinus Fonden's mark and wordmark, two files on its site, are set together as its header shows them):
#   danish-mfa.png                um.dk/media/c0ybhb1u/um-logo-en.png
#   innovation-fund-denmark.svg   danmarksinnovationsfond.dk/wp-content/uploads/2026/06/ifd_logo.svg
#   bestseller-foundation.svg     bestseller.org, the header logo (inline SVG)
#   augustinus-fonden.svg         augustinusfonden.dk, the header logo (two inline SVGs)
#   al-jazeera.svg                aljazeera.com, the header logo (inline SVG)
#   danish-film-institute.svg     dfi.dk/themes/custom/p8z_proto/prototype/source/gfx/dfi_logo_standard.svg
#   dtda.png                      dtda.dk/wp-content/uploads/2026/03/DTDA_DK_logo1_Positiv.png (renamed from Ulandssekretariatet, April 2026)
#   pawa254.png                   pawa254.org/wp-content/uploads/2023/09/PAWA254-LOGO-white.png
# They are shown in one tone by a filter (greyscale, darkened), not redrawn; the official one-colour files replace them when the
# courtesy notes bring them. Sizes follow equal optical weight: the same area for every logo (LOGO_AREA), capped by the cell,
# times a factor set by eye for marks that read heavier or lighter than their area.
SUPPORTERS = [  # name (the logo's alt text), what it supported (for the record only, never on the page), file, width/height, weight
    dict(name="Ministry of Foreign Affairs of Denmark (Danida)", what="Øksnehallen 2016, through the information grant; the Bamako programme, through the Danish Embassy in Mali",
         logo="danish-mfa.png", ratio=886 / 200, weight=1.3),
    dict(name="Innovation Fund Denmark", what="An investment in Africa Reframed, 2020 (InnoBooster); never implied to back today's model",
         logo="innovation-fund-denmark.svg", ratio=172 / 33, weight=0.9),
    dict(name="BESTSELLER FOUNDATION", what="The Waste to Value Collection, 2020–2022", logo="bestseller-foundation.svg", ratio=426.17 / 27.03, weight=1.0),
    dict(name="Augustinus Fonden", what="Øksnehallen 2016", logo="augustinus-fonden.svg", ratio=219 / 74.35, weight=1.1),
    dict(name="Al Jazeera", what="Øksnehallen 2016: a supporter in the programme, and a partner in the film programme", logo="al-jazeera.svg", ratio=166 / 60, weight=1.0),
    dict(name="Danish Film Institute", what="Øksnehallen 2016", logo="danish-film-institute.svg", ratio=105.6683 / 25, weight=0.85),
    dict(name="DTDA, the Danish Trade Union Development Agency", what="Freetown 2013, as the LO/FTF Council (its name then)", logo="dtda.png", ratio=1148 / 324, weight=1.2),
    dict(name="PAWA254", what="Nairobi 2014: the master class with the Photojournalists Association of Kenya, in its premises", logo="pawa254.png", ratio=802 / 278, weight=0.9),
]
LOGO_AREA, LOGO_MAX_H, LOGO_MAX_W = 3000, 38, 150   # px² of logo per entry at desktop size; the cell caps height and width

# 4 Who is behind it
ABOUT_WHO_LONG = [   # the wording until 11 November 2026, 15:00, kept
    "Africa Reframed is an independent, non-commercial initiative established by Commerce & Culture, the Copenhagen studio founded in 2010 by Thomas Damgaard. Trained in design and art history, he advised the Danish Ministry of Foreign Affairs on culture and development from 2010 to 2014, and has produced photography and exhibitions with partners in Africa and Europe since.",
    "The visual identity is by the Danish designer Rune Høgsberg, first drawn for the exhibition at Øksnehallen. The archive’s photographs are made by our team.",
]
# The same words in a new order (11 November 2026): the first sentence opens the chapter.
ABOUT_WHO = [
    "Africa Reframed is an independent, non-commercial initiative established by Commerce & Culture, the Copenhagen studio founded in 2010 by Thomas Damgaard.",
    "Trained in design and art history, he advised the Danish Ministry of Foreign Affairs on culture and development from 2010 to 2014, and has produced photography and exhibitions with partners in Africa and Europe since. The visual identity is by the Danish designer Rune Høgsberg, first drawn for the exhibition at Øksnehallen. The archive’s photographs are made by our team.",
]
ABOUT_PEOPLE = [("Thomas Damgaard", "Founder.", "Portrait"), ("Rune Høgsberg", "The identity.", "Portrait or the mark"),
                ("CFP Bamako", "Partner school.", "The school"), ("The Nairobi team", "Photographers.", "The team")]


def by_state(items):
    """Projects in production or open first, then the rest in the order given (strongest first)."""
    order = list(STATES)
    return sorted(items, key=lambda x: order.index(x["state"]))

PRESS_FACTS = [("1,122 images", "in the House Collection, from Mali, Kenya and The Gambia"), ("The first five themes", "Learning, Work and enterprise, Everyday digital, City life, Creativity and culture"),
               ("Free for partners", "selected non-profit and public partners; companies through a collection sponsorship"), ("Established by", "Commerce & Culture, Copenhagen"),
               ("Real images", "our images are never AI-generated")]
PRIVACY = [("What we collect", "Your organisation, your name and role, your email address, how you expect to use the images, and the answers you give in the partner forms."),
           ("Why", "To approve access and keep in touch, and to report how the images are used, without personal details, to the funders who make new collections possible, with your consent."),
           ("How long, and your rights", "We keep your details while your organisation has access and for one year after. You can ask to see, change or delete them at any time."),
           ("On your device", "If you come to this site from the archive, your browser remembers it for 30 days, so the menu shows the archive’s links. Nothing is sent to us or anyone else, and clearing this site’s data in your browser removes it."),
           ("Who to write to", "hello@africareframed.com.")]


# ---------------------------------------------------------------------------------------------
# The pages, each a sequence of modules in the order of the page priorities (Site map, section 6) and the inventory
# (section 3). Nine templates; the five key pages first.
# ---------------------------------------------------------------------------------------------
def tpl_home(p, base):
    # 1 What this is: the Opening. 2 Who it is for and who is behind it, with the ways on. 3 In use: the numbers (exist),
    # partners and an example (from the closed preview). 4 The five themes. 5 The collections. 6 The principles.
    return (m_opening(CORE_LINE)
            + m_text(None, INTRO_HOME, "d", links=[button(base + "themes/", "Explore the themes", quiet=True),
                                                   button(base + "partners/", "How partners use the archive", quiet=True)], sid="intro",
                     meta=[f"{n} {t}" for n, t in NUMBERS])
            # 3 In use, one section (page priorities, Home 3): the numbers, the partners by name, one example. Built only
            # when each exists (rule 27). "Uses by kind" is not in the priorities and is out (Thomas, 11 November 2026).
            + m_numbers(MOMENTUM, "from the archive’s records; updated monthly", title="In use",
                        note_text="The momentum numbers (Thomas, 8 November 2026): partners, and uses, one per download, each with its stated kind (PhotoDeck’s orders).")
            + m_partners(title=None, tight=True) + m_use("a", title=None, tight=True)
            + chapter(m_themes(base, "a"))
            + m_photo("A photograph from the archive, full bleed · released, no minors", "21/9", "a")
            + chapter(m_collection(base))
            + chapter(m_items("Four principles behind every image", PRINCIPLES, "a", lead=note("One line each; the full story is on About."), sid="principles"))
            + m_doors("c", links=[button(base + "about/", "About Africa Reframed", quiet=True)], tight=True, left=True))   # under the principles, on their left edge


def tpl_index_themes(p, base):
    return (m_page_head(p["title"], THEMES_LEAD, statement_draft=True) + m_themes(base, "b")
            + m_text(THEMES_SOURCE[0], [THEMES_SOURCE[1]], "a",
                     links=[button(base + "partners/#sponsor", "Sponsor a collection on your theme →", quiet=True)]))


def tpl_index_collections(p, base):
    return (m_page_head(p["title"], "Each collection is a body of work with its own story and the people behind it.", statement_draft=True)
            + m_collection(base, "b", title=False)
            + m_doors("c", links=[button(base + "partners/#sponsor", "Sponsor a collection on your theme →", quiet=True)], tight=True, left=True))


def tpl_theme(p, base):
    t = p["theme"]
    n = THEMES.index(t)
    # 1 name, statement, count; 2 the evidence: a lead image and six to eight samples; 3 Open in the archive; 4 the text;
    # 5 the sponsor credit; 6 previous and next.
    return (m_page_head(t["name"], t["statement"], kicker=f"Theme {n + 1}",
                        meta=[(f'{t["count"]} images in the archive →', archive("/-/galleries/archive?search=" + quote(t["query"]), "theme-head-" + t["slug"])), "House Collection"])
            + m_photo(f"Lead image for {t['name']}", "21/9", "a", lead=True, echo=True)
            + m_grid("e", label="Image from the theme", title="What it shows", aside=draft(limit("text section", THEME_TEXTS[t["slug"]])))
            + m_sponsor("theme", tight=True, sponsor=THEME_SPONSORS.get(t["slug"]))
            # the way into the archive, as one yellow surface near the end of the page (the count in the head is its link at the top)
            + m_doors("b", count=(t["count"], f'images on {t["name"].lower()} in the archive'), count2=("—", "uses"),
                      main=button(archive("/-/galleries/archive?search=" + quote(t["query"]), "theme-" + t["slug"]), "Open in the archive →"),
                      quiet=button(base + "request-access/", "Request access", quiet=True), line=THEME_ACTION_LINE)
            + m_themes(base, "c", current=t))


def story_id(x):
    return "story-" + re.sub(r"[^a-z0-9]+", "-", x["name"].lower()).strip("-")


def m_contents(rows):
    """The stories' contents, like a magazine's: the kind of work, the company and the headline, each linking down."""
    li = "".join(f'<li><a href="#{story_id(x)}"><span class="kicker">{e(x["kind"])}</span><strong>{e(x["name"])}</strong>'
                 f'<span class="contents-line">{e(x["headline"])}</span></a></li>' for x in rows)
    return f'<ul class="contents">{li}</ul>'


def company_story(x, i):
    """One company as a story in a sponsored collection: a teaser told in photographs. The rhythm of a magazine feature: the
    lead photograph full bleed, then beside the words on the left, then on the right, and again; under each story a pair
    more from the shoot (the people at work, the product), credited to its photographer. No "read more": the story is the teaser."""
    words = (f'<p class="kicker">{e(x["kind"])}</p><h3 class="story-headline">{e(x["headline"])}</h3>'
             f'<p class="story-company"><strong>{e(x["name"])}</strong> · {e(x["where"])}</p>')
    limit("company story", x["text"] + " " + (x.get("since") or ""))
    body = draft(x["text"]) + (draft(x["since"], "p", "small since") if x.get("since") else "")
    # The credit line is the collection's (design guide: photographers named on the page, never in the credit); the
    # photographer is named in the caption, beside the pictures they made.
    credit, caption = WTV_CREDIT, f'{x["name"]}, {x["city"]}, 2021. Photographer: {x["photographer"]}'
    lead = f'{x["name"]}: the lead photograph from the shoot'
    if i % 3 == 0:
        out = m_photo(lead, "21/9", "a", caption=caption, credit=credit, sid=story_id(x))
        out += mod("text", "a, the story", f'<div class="cols story"><div class="c1-4">{words}</div><div class="c6-12">{body}</div></div>', tight=True)
    else:
        out = m_photo(lead, "3/2", "c", text=f'<div class="story">{words}{body}</div>', side="left" if i % 3 == 1 else "right",
                      caption=caption, credit=credit, sid=story_id(x), wide=True)
    # One photograph for each company (Thomas, 11 November 2026, 14:37): a few rightly chosen images, not a cascade. The
    # pair that stood under each story is gone; the collection itself is in the archive.
    return out


def cs_quotes(rows, title):
    q = "".join(f'<figure class="quote"><blockquote>{draft("“" + a + "”")}</blockquote><figcaption class="small">{e(b)}</figcaption></figure>' for a, b in rows)
    inner = (f'<div class="cols"><div class="c1-4">{heading(title, 3, "project-title")}</div><div class="c6-12 quotes">{q}'
             f'{note("From the founders’ emails; on the live page only once each has agreed, after launch.")}</div></div>')
    return mod("text", "a, in their words", inner, tight=True)


def facts_html(c):
    return '<dl class="facts">' + "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in c["facts"]) + "</dl>"


# The collection page's sections. Each takes the collection and the base path; a collection names the ones it uses, in order.
COLLECTION_SECTIONS = {
    "story": lambda c, base: (m_text(c["story_title"], c["story"], "a") if "grid" in c["sections"] else
                              m_text(c["story_title"], c["story"], "b", box=facts_html(c))),
    "companies": lambda c, base: (mod("items", "a, the stories’ contents",
                                      f'<div class="cols"><div class="c1-4">{heading(c.get("companies_title", "The companies"))}</div><div class="c6-12">{draft(c["companies_lead"])}'
                                      f'{note("Seven stories as teasers, one photograph each. Present tense where a company’s current activity is confirmed; otherwise as photographed in 2021, until its founder confirms.")}</div></div>'
                                      + m_contents(c["companies"]), sid="companies")
                                  + "".join(company_story(x, i) for i, x in enumerate(c["companies"]))),
    "grid": lambda c, base: m_grid("e", label="Image from the collection", line=c["grid_line"], title="From the collection", credit=c.get("credit"),
                                   aside=facts_html(c)),   # the evidence with the facts and the count (collection page 4)
    "making": lambda c, base: m_items("How it was made", c["making"], "b", lead=draft("From the first call with a founder to the last gallery.")),
    "photographers": lambda c, base: m_items(c.get("photographers_title", "The photographers"), c["photographers"], "d", lead=draft(c["photographers_lead"] + (" " + c["bts"] if c.get("bts") and "bts" not in c["sections"] else "")), image_ratio="4/5", sid="photographers", credit=c.get("credit")),
    "bts": lambda c, base: m_grid("c", label="Behind the scenes: a photographer at work", line=c["bts"], title="Behind the scenes", level=3, credit=c.get("credit")),
    "went": lambda c, base: m_items(c.get("went_title", "Where the images went"), c["went"], "a", sid="where",
                                    lead=draft(c["went_lead"], "p", "lead") if c.get("went_lead") else None),
    "words": lambda c, base: cs_quotes(c["words"], "In the founders’ words"),
    "sponsor": lambda c, base: m_sponsor("collection", sponsor=c["sponsor"]),
    "invite": lambda c, base: m_text(c["invite"]["title"], c["invite"]["text"], "c", contact=("Partnerships", EMAIL_PARTNERS), sid="your-theme",
                                     links=[button(base + "partners/#sponsor", "How sponsoring a collection works →", quiet=True)]),
    "places": lambda c, base: m_items("Three countries, three cities", [(k, t, f"Image from {k}") for k, t in PLACES], "d", credit=c.get("credit")),
    "feature": lambda c, base: m_photo("A photograph from the collection, full bleed", "21/9", "a", credit=c.get("credit")),
    "themes": lambda c, base: m_items("Themes it feeds", [(t["name"], f'{base}themes/{t["slug"]}/') for t in THEMES], "e"),
    "goals": lambda c, base: m_items("Goals it serves", [(g, None) for g in ("SDG 4 – Quality Education", "SDG 8 – Decent Work and Economic Growth", "SDG 5 – Gender Equality")], "e", tight=True,
                                     lead=note("From the SDG field in the metadata; the three most frequent for now, to confirm from the AR Metadata sheet.")),
    "access": lambda c, base: (
        m_doors("b", count=c["access"]["count"], main=button(base + "request-access/", "Request access to the collection"),
                quiet=button(f"mailto:{EMAIL_PRESS}", "Press", quiet=True), line=c["access"]["line"], sid="access")
        if c["access"].get("request") else
        m_doors("b", count=c["access"]["count"], main=button(archive("/-/galleries/archive", c["access"]["src"]), "Open in the archive →"),
                quiet=button(base + "partners/", "How partners use the archive", quiet=True), line=c["access"]["line"], sid="access")),
    "uses": lambda c, base: m_use("b"),   # collection page 8: in use, once there are any; the count by kind is out (11 November 2026)
}


def tpl_collection(p, base):
    # The head (name, statement, the lead photograph), then the collection's own sections in its order. House Collection:
    # the story, the evidence, places and series, themes and goals, Open in the archive, in use. A sponsored collection:
    # the theme, the companies, the evidence, how it was made, the photographers and behind the scenes, where the images
    # went, the sponsor, the invitation to a collection on another theme, and access by request.
    c = p["collection"]
    meta = list(c.get("meta") or [])
    if "companies" in c["sections"] and meta:
        meta[0] = (meta[0], "#companies")                       # a sponsored collection: the way on is down to its stories
    elif not c["access"].get("request"):
        meta.insert(0, (f'{c["access"]["count"][0]} images in the archive →', archive("/-/galleries/archive", c["access"]["src"] + "-head")))
    head = (m_page_head(c["title"], c["statement"], kicker=c["kicker"], meta=meta, statement_draft=c.get("statement_draft", False))
            + m_photo(c["lead"], "21/9", "a", credit=c.get("lead_credit"), lead=True, echo=True))
    return head + "".join(COLLECTION_SECTIONS[s](c, base) for s in c["sections"])


def tpl_partners(p, base):
    doors = [door("#use", "Organisations", "Use the images", "Free for selected non-profit and public partners.", dark=True),
             door("#sponsor", "Companies", "Sponsor a collection", "Companies get access through a collection sponsorship.")]
    # 1 the two doors; 2 how access works; 3 using the images; 4 sponsor a collection; 5 who already uses the archive; 6 request access, contact.
    return (m_page_head(p["title"], doors=m_doors("a", doors=doors))
            + m_text("How access works", [ACCESS_WHO], "a", is_draft=False, sid="use")
            + m_items(None, ACCESS_STEPS, "b", tight=True)
            + m_doors("c", links=[button(base + "request-access/", "Request access", quiet=True)], tight=True)
            + m_items("The rules for using the images", RULES, "c", lead=draft("The rules in plain language. The legal text is Terms on the archive.", "p", "small"), sid="using-the-images")
            + m_text("Sponsor a collection", SPONSOR_TEXT, "c", contact=("Partnerships", EMAIL_PARTNERS), sid="sponsor",
                     links=[button(base + "collections/waste-to-value/", "See the Waste to Value Collection →", quiet=True)])
            # 5 who already uses the archive: partners by name and examples of use, once there are any (rule 27). The counts by
            # type and by country are not in the page priorities and are out (Thomas, 11 November 2026).
            + m_partners(10, "Partners by name") + m_use("b", "In use", tight=True))


def tpl_portal(p, base):
    doors = [door(archive("/-/galleries/archive", "portal"), "Partners", "Partner log in →", "Signed in already? This takes you straight to the images.", dark=True),
             door(base + "request-access/", "New partners", "Request access", "Free for selected non-profit and public partners.")]
    forms = [("Report a use", "Where an image appeared, and what you need next.", [("Where it appeared", "text"), ("Link", "url"), ("Date", "text"), ("What you need next", "textarea"), ("Organisation", "text"), ("Email", "email")]),
             ("Request imagery", "Can’t find what you need?", [("What you are looking for", "textarea"), ("For what", "text"), ("By when", "text"), ("Organisation", "text"), ("Email", "email")]),
             ("What are you working on?", "The yearly question, any time.", [("Your project", "textarea"), ("Link", "url"), ("Organisation", "text"), ("Email", "email")])]
    # 1 who it is for and the two doors; 2 report a use; 3 request imagery and what are you working on; 4 news and numbers; 5 the rules reminder; 6 a feedback call.
    return (m_page_head(p["title"], PORTAL_LEAD, statement_draft=True, doors=m_doors("a", doors=doors))
            + m_form("b", title="The partner’s desk", forms=forms, sid="desk",
                     lead=draft("The one place to tell us how the images are used and what you need next. Every answer lands with us, and we answer.", "p"))
            + m_numbers(MOMENTUM, "from the archive’s records; updated monthly", title="Partner news")
            + m_use("c", "News", tight=True)
            + m_text("The rules in short", [PORTAL_RULES], "a", links=[button(base + "partners/#using-the-images", "All the rules", quiet=True),
                                                                    button(archive("/client", "portal-history"), "Your download history", quiet=True)], sid="rules")
            + m_form("c", title="Talk to us", button_label="Book a feedback call", sid="call", tight=True,
                     lead=draft("Optional, never required: a short call about what is missing and what you are working on.", "p", "small")))


def tpl_form(p, base):
    fields = [("Organisation", "text"), ("Your role", "text"), ("Type of organisation", "select"), ("Country", "text"), ("Focus of your work", "text"),
              ("How you will use the images", "textarea"), ("What imagery you are looking for", "textarea"), ("Email", "email")]
    aside = heading("What happens next", 3) + '<ol class="next-steps">' + "".join(f"<li><strong>{e(a)}</strong> <span class=\"draft\">{e(b)}</span></li>" for a, b in REQUEST_NEXT) + "</ol>" + draft(REQUEST_FOOT, "p", "small")
    after = (f'<p class="small">Read <a href="{base}partners/#using-the-images">the rules for using the images</a> first. '
             f'Until this form is connected, requests go through <a href="{archive("/contact", "request")}">the archive’s request form</a>.</p>')
    return (m_page_head(p["title"], ACCESS_WHO)
            + m_form("a", title="Request access", fields=fields, aside=aside, consent=REQUEST_CONSENT, button_label="Send the request", after=after)
            + m_text("Thank you", ["Your request is with us. We reply within a working day, and the welcome email that follows opens your account."], "a", sid="thanks"))


def tpl_press(p, base):
    facts = [(a, b) for a, b in PRESS_FACTS]
    release_text = heading("The relaunch", 3, "kicker-h") + draft("The press release, from the Strategic Platform’s draft, with date and quotes from named people who agreed to them.", "p") + f'<p class="doors">{dead_button("Download the release (PDF)", quiet=True)}</p>'
    return (m_page_head(p["title"], "Stories, images for editorial use, and someone to talk to.", statement_draft=True)
            + m_photo("Press image for the relaunch", "3/2", "c", text=release_text, side="left")
            + m_items("Fact sheet", facts, "a", is_draft=True, cls="five")
            + m_text("Track record", ["Exhibitions and collaborations since 2010, told as history: the proof behind the present."], "a")
            + m_grid("a", 3, "Press image", line="A curated set for editorial use with the credit line; no images with minors.", title="Press images",
                     link=dead_button("Download the press set", quiet=True))
            + m_items("Story leads", [(s, "Two sentences on the series, the place and who to talk to.", "Image from the series") for s in GAMBIA_SERIES], "d", cols=2)
            # the logos as they are (only what exists); the portrait is a photograph and carries its own credit
            + m_items("Logos and portrait", [
                ("Logo, black on white", "", None, {"image": f'<div class="logo-card"><img src="{base}assets/logo-black.svg" alt="The Africa Reframed logo in black" width="320" height="64"></div>'}),
                ("Logo, white on black", "", None, {"image": f'<div class="logo-card dark"><img src="{base}assets/logo-white.svg" alt="The Africa Reframed logo in white" width="320" height="64"></div>'}),
                ("Thomas Damgaard", "", None, {"image": frame("Portrait of Thomas Damgaard", "3/2", role="third", cap=False)})], "d", is_draft=False, credit=False)
            + m_doors("d", kicker="Press contact", address=EMAIL_PRESS, line="We answer the same day."))


def tpl_text(p, base):
    k = p["slug"]
    if k == "about":
        register = ('<div class="register">' + draft(ABOUT_GETTY_BEFORE, "p", "register-lead")
                    + '<p class="register-names">' + "".join(f"<span>{e(n)}</span>" for n in ARCHIVE_LICENSEES) + "</p>"
                    + draft(ABOUT_GETTY_AFTER, "p", "register-after")
                    + note("Companies that bought our team’s images, the images now in the archive. Institutional names (the UN, the World Bank, the BBC and others) are added once Thomas has checked they bought the team’s images.") + "</div>")
        # Four chapters (the plan of 11 November 2026, the whole site): the archive, exhibitions, workshops, who is behind
        # it. Each opens with twice the space above it and its title at the page-title size in Light. The order and the
        # words are the build brief's (About page – build brief): credibility, then wonder, then people.
        opener = lambda title, paras, sid: chapter(m_text(title, paras, "a", sid=sid, lead_first=True)).replace("<h2>", '<h2 class="chapter-title">', 1)
        head = (m_page_head(p["title"], ABOUT_STATEMENT, statement_draft=True)
                + m_channels(ABOUT_CHANNELS)
                + m_supporters(SUPPORTERS, SUPPORTERS_TITLE, base))
        # 1 The archive: always on. The activity, then the proof: its collections, where its images have been, the way in.
        the_archive = (opener("The archive", ABOUT_ARCHIVE, "archive")
                + mod("collection", "a, the collections in the archive", "".join(collection_entry(x, base) for x in by_state(ARCHIVE_COLLECTIONS)))
                + mod("text", "the register", f'<div class="cols"><div class="c6-12">{register}'
                      f'<p class="doors">{button(base + "partners/#use", "How partners use the archive →", quiet=True)}</p></div></div>', tight=True)
                + mod("text", "the hinge", f'<div class="cols"><div class="c6-12">{draft(ABOUT_HINGE, "p", "hinge")}</div></div>'))
        # 2 Exhibitions: a medium we activate. The activity, then the projects, the door, the artists. The page turns here.
        exhibitions = (opener("Exhibitions", ABOUT_EXHIBITIONS, "exhibitions")
                + "".join(m_project(x) for x in by_state(EXHIBITION_PROJECTS))
                # No door here and no lead over the artists (Thomas, 11 November 2026, 15:26): the chapter shows, it does not
                # offer, and each work carries its own © line, so the sentence on copyright said it twice.
                + m_items("The artists", [(n, about_country(n), l, artist_card(base, n)) for n, d, l in ARTISTS_SHOWN], "d", image_ratio="4/5", cols=4, sid="artists", level=3)
                + m_network(base))
        # 3 Workshops: a medium we activate. The activity, then the projects, Bamako Nights, the partners.
        workshops = (opener("Workshops", ABOUT_WORKSHOPS, "workshops")
                + "".join(m_project(x) for x in by_state(WORKSHOP_PROJECTS))
                + m_items("In their words", ABOUT_INTERVIEWS, "d", image_ratio="16/9", level=3,
                          lead=draft("Three of the programme’s photographers, on what it meant to them.")
                          + note("Short films of interviews with the photographers; played on click with a poster frame, never autoplaying (the one-motion rule)."))
                + m_grid("e", label="Bamako Nights", line=BAMAKO_NIGHTS, title="Bamako Nights", credit="Students of CFP Bamako, Bamako Nights, 2011", level=3, cap=False)
                + m_items("Workshop partners", WORKSHOP_PARTNERS, "a", level=3, cls="five")
                + mod("text", "the way to the collection", f'<div class="cols"><div class="c6-12">{draft(ABOUT_WORKSHOPS_TO_COLLECTION)}'
                      f'<p class="doors">{button(base + "collections/house-collection/", "The House Collection →", quiet=True)}</p></div></div>', tight=True))
        # 4 Who is behind it
        who = (opener("Who is behind it", ABOUT_WHO, "who")
                + m_items(None, ABOUT_PEOPLE, "d", image_ratio="1/1", tight=True, cols=4)
                + m_items("Principles", PRINCIPLES + [("Fair terms", "One download, one licence, free of charge; no resale, no sublicensing.")], "a", cls="five")
                + m_doors("d", kicker="Write to us", address=EMAIL_MAIN, line=f"Partnerships: {EMAIL_PARTNERS} · Press: {EMAIL_PRESS}"))
        # The exhibitions and the artists' works stand on black (Thomas, 11 November 2026, 14:33): the page turns here, and
        # the black ground groups them as one category (Quality rules, rule 18: each ground holds one kind of content).
        return head + the_archive + f'<div class="dark">{exhibitions}</div>' + workshops + who
    if k == "contact":
        return (m_page_head(p["title"], "One quiet way to reach us.", statement_draft=True)
                + m_doors("d", kicker="Write to us", address=EMAIL_MAIN, line=f"Press: {EMAIL_PRESS} · Partnerships: {EMAIL_PARTNERS} · Africa Reframed on LinkedIn."))
    return (m_page_head(p["title"], "What we collect when you request access or write to us, and why.", statement_draft=True)
            + m_rows(PRIVACY))


def artist_card(base, name):
    """On About: the artist's name links to the artist's page, and the card shows the page's lead work, once the page exists."""
    a = ARTIST_BY_NAME.get(name)
    if not a:
        return {}
    ld = a["lead"]
    return dict(href=artist_href(base, a),
                image='<figure class="frame">' + artwork(base, a, ld["file"], work_label(a, ld.get("title"), ld["series"]), ld["w"], ld["h"], "(max-width: 767px) 50vw, 25vw", "work card-work",
                                                         style=card_focus(a)) + f'<p class="credit">{e(artist_credit(a))}</p></figure>')


def card_focus(a):
    """The card on About is a thumbnail: the lead cropped to fill the 4:5 frame, as the Insights overview on
    commerceandculture.org crops it (Thomas, 10 November 2026), around the focal point set there; the centre otherwise."""
    x, y = a.get("card_focus", (0.5, 0.5))
    return "" if (x, y) == (0.5, 0.5) else f"object-position:{x * 100:.0f}% {y * 100:.0f}%"


def m_network(base):
    """From the network, on About: rows of text, no images (Thomas, 10 November 2026); each name links to its page once made."""
    def name(n):
        a = ARTIST_BY_NAME.get(n)
        return f'<a href="{artist_href(base, a)}">{e(n)}</a>' if a else e(n)
    li = "".join(f'<li><strong>{name(n)}</strong>{draft(about_line(n, d), "span")}</li>' for n, d in ARTISTS_NETWORK)
    join = f'Photographers who want to join can <a href="{base}contact/">write to us</a>.'
    return mod("items", "a, rows of text, the network",
               f'<div class="cols" id="network"><div class="c1-4">{heading(NETWORK, 3, "project-title")}</div><div class="c6-12">'
               f'<p class="network-lead">{e(NETWORK_LEAD)} {join}</p>'
               f'<ul class="network-rows">{li}</ul>'
               + note("Rows of text, no images (Thomas, 10 November 2026). Each name links to the artist’s own page once it is made (Artist pages – template).")
               + "</div></div>")


def work_label(a, title, series):
    """Caption and alt text of a work: the artist, the title where the work has one, the series."""
    if a["group"] == "films":
        return f"Still from {title}" if title else "Film still"
    return a["name"] + (f", {title}" if title else "") + (f", from the series {series}" if series and series != "Selected works" else "")


def about_country(name):
    """On About, under a work shown at the exhibition: the artist's country and nothing more (Thomas, 11 November 2026,
    15:14: the name is enough, the reader can click in). The network's rows keep their line: they have no picture."""
    a = ARTIST_BY_NAME.get(name)
    return a.get("country", "") if a else ""


def about_line(name, fallback):
    """On About, under the card or in the row: the country and the artist's one line, the same sentence as under the name on
    the artist's page, in the tone of the excerpt on the Insights overview (Thomas, 10 November 2026). No series titles."""
    a = ARTIST_BY_NAME.get(name)
    return (f"{a['country']} · {a['line']}" if a.get("country") else a["line"]) if a else fallback


def shape(w, h):
    """A work's shape, for its width on the grid: works of every shape carry a similar weight on the page."""
    r = w / h
    return "tall" if r < 0.9 else ("square" if r < 1.3 else "wide")


def artist_href(base, a):
    return f"{base}{a['path']}" if a.get("path") else f"{base}about/artists/{a['slug']}/"


def artwork(base, a, file, alt, w, h, sizes="(max-width: 767px) 100vw, 50vw", cls="work", style="", big=False):
    """One work, shown whole at its own proportion: never cropped, filtered or under the pattern (on the artist's page).
    The only exception is the card on About, a thumbnail cropped to its frame (artist_card)."""
    d = f"{base}assets/artists/{a['slug']}/{file}"
    st = f' style="{style}"' if style else ""
    # the versions are 1,000 and 2,000 px on the long side, never upscaled: declare their true widths, or the browser shows
    # an upright or a small original smaller than its column
    w1, w2 = (round(w * min(1, n / max(w, h))) for n in (1000, 2000))
    srcset = (f'srcset="{d}-1000.jpg {w1}w, {d}-2000.jpg {w2}w" sizes="{sizes}" ' if w2 > w1 else f'srcset="{d}-1000.jpg {w1}w" sizes="{sizes}" ') if big else ""
    return (f'<img class="{cls}" src="{d}-1000.jpg" {srcset}'
            f'width="{w}" height="{h}" alt="{e(alt)}" decoding="async"{st}>')


def tpl_artist(p, base):
    a = p["artist"]
    lead = a["lead"]
    lead_alt = work_label(a, lead.get("title"), lead["series"])
    lead_img = artwork(base, a, lead["file"], lead_alt, lead["w"], lead["h"],
                       {"tall": "(max-width: 767px) 100vw, 50vw", "square": "(max-width: 767px) 100vw, 60vw", "wide": "(max-width: 767px) 100vw, 70vw"}[shape(lead["w"], lead["h"])],
                       big=True)
    cap = lead_alt + (f" · {lead['credit']}" if lead.get("credit") else "")
    lead_html = (f'<div class="cols"><figure class="work-lead lead-{shape(lead["w"], lead["h"])}">{lead_img}'
                 f'<figcaption class="credit"><span>{e(cap)}</span></figcaption></figure></div>')
    kicker = NETWORK if a["group"] == "network" else "Shown at Øksnehallen"
    dl = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in a["facts"])
    dl += f'<dt>Exhibited</dt><dd><a href="{base}about/#exhibitions">{e(EXHIBITION)}</a></dd>' if a["group"] in ("shown", "films") else ""
    dl += f'<dt>Network</dt><dd><a href="{base}about/#network">{e(NETWORK)}</a></dd>' if a["group"] == "network" else ""
    if a.get("gallery"):
        dl += f"<dt>Gallery</dt><dd>{e(a['gallery'])}</dd>"
    if a.get("website"):
        dl += f'<dt>Website</dt><dd><a href="{a["website"][1]}" rel="noopener">{e(a["website"][0])}</a></dd>'
    # No portrait (Thomas, 10 November 2026): the template shows the work only, so every artist's page is the same.
    box = f'<aside class="facts-box"><dl class="facts">{dl}</dl><p class="small">{e(artist_rights(a))}</p></aside>'
    text = "".join(draft(t) for t in a["text"])
    out = (m_page_head(a["name"], a["line"], kicker=kicker, statement_draft=True)
           # On white (Thomas, 11 November 2026, 14:57): on black these pages confused. Black stays for the Exhibitions
           # chapter on About.
           + mod("photo", "b, the lead work, whole", lead_html, tight=True)
           + mod("text", "b, with a facts box (artist)", f'<div class="cols"><div class="c1-6 artist-text">{text}{note(a["note"]) if a.get("note") else ""}</div><div class="c8-12">{box}</div></div>'))
    for sr in a["series"]:
        shown = [x for x in sr["works"] if x[0] != lead["file"]]
        # a row of mostly horizontal works (wider than 1.1:1) takes three to a row, so each carries the weight of an upright work,
        # and shows three or six of them, so that no work is left alone on a line
        across = [w / h > 1.1 for f, t, w, h in shown]
        wide = " works-wide" if across and sum(across) * 2 > len(across) else ""
        if wide and len(shown) > 3:
            shown = shown[:len(shown) - len(shown) % 3]
        works = "".join("<figure>" + artwork(base, a, f, work_label(a, t, sr["title"]), w, h, "(max-width: 767px) 50vw, 25vw")
                        + "<figcaption>" + (f'<span class="caption">{e(t)}</span>' if t else "") + f"<span>{e(artist_credit(a))}</span></figcaption></figure>"
                        for f, t, w, h in shown)
        body = f'<div class="works{wide}">{works}</div>' if works else ("" if sr.get("films") else note(sr.get("pending", "Images follow.")))
        if sr.get("films"):
            body += ('<div class="cols"><div class="c1-12"><ul class="network-rows film-list">'
                     + "".join(f'<li><strong>{e(t)}</strong><span class="film-meta">{e(m)}</span>{draft(d, "span")}</li>' for t, m, d in sr["films"])
                     + "</ul></div></div>")
        out += mod("grid", "artwork row, whole works", f'<h3 class="project-title">{e(sr["title"])}</h3>'
                   f'<div class="cols"><div class="c1-8">{draft(sr["line"], "p", "series-text")}</div></div>{body}')
    others = [x for x in NAV if x is not a]
    if others:
        i = NAV.index(a)
        prev, nxt = NAV[i - 1], NAV[(i + 1) % len(NAV)]
        more = "".join(f'<a class="button quiet" href="{artist_href(base, x)}">{e(lbl)}: {e(x["name"])}</a>' for lbl, x in (("Previous", prev), ("Next", nxt)) if x is not a)
    else:
        more = ""
    out += mod("doors", "c, more artists", f'<div class="cols"><div class="c1-12"><p class="doors">{more}{button(base + "about/#artists", "All the artists on About →", quiet=True)}</p>'
               + (note("Previous and next artist appear once there are more artist pages.") if not others else "") + "</div></div>", tight=True)
    return out


TEMPLATES = {"home": tpl_home, "themes": tpl_index_themes, "collections": tpl_index_collections, "theme": tpl_theme,
             "collection": tpl_collection, "partners": tpl_partners, "portal": tpl_portal, "form": tpl_form,
             "press": tpl_press, "text": tpl_text, "artist": tpl_artist}


# ---------------------------------------------------------------------------------------------
# /dev/modules: every module with each of its variants on one page (step 2), generated by every build.
# ---------------------------------------------------------------------------------------------
TYPE_SCALE = [  # (the named style, size, weights, what it is for, a sample)
    ("fs-display", "64 px (44 px below desktop)", "700; 300 for a number", "The display size: the Home headline and the five themes’ numbers on Home.", "Visual storytelling", 700),
    ("fs-title", "44 px (32 px below desktop)", "700; 300 for a number", "The page title; the big number.", "House Collection · 1,122", 700),
    ("fs-head", "22 px", "700; 300 for the intro", "A section’s title and a card’s title; the statement under a page title; a lead.", "The story", 700),
    ("fs-text", "17 px", "400; 700 for an item’s title", "All text, the menu, buttons and fields. It carries most of a page’s words.", "The images show people at work, at study and at home.", 400),
    ("fs-small", "13 px", "400", "Captions, credits, kickers, labels, counts and the footer’s links.", "Photo: Africa Reframed", 400),
]


def tpl_type(base):
    """/dev/type/: the six sizes and three weights (Quality rules, rule 11), and the one open choice, shown not guessed."""
    rows = "".join(f'<div class="type-row"><div class="type-sample" style="font-size:var(--{k});font-weight:{w}">{e(sample)}</div>'
                   f'<p class="credit"><span class="mono">--{k}</span> · {e(size)} · weight {e(wt)} · {e(job)}</p></div>'
                   for k, size, wt, job, sample, w in TYPE_SCALE)
    out = m_page_head("Type", "Six sizes and three weights, each with one job. A page shows four at most: the page title, the heading and the intro, the text, the small print.",
                      kicker="Development")
    out += mod("text", "the scale", f'<div class="type-rows">{rows}</div>')
    out += mod("text", "the choice", f'<div class="cols"><div class="c1-4">{heading("The Home headline: 64 px")}</div><div class="c6-12">'
               f'<p>Since 11 November 2026 Home is built with its headline at the display size. The three versions of the Opening '
               f'stand side by side at <a href="{base}dev/opening/">/dev/opening/</a>.</p></div></div>', tight=True)
    return out


def tpl_opening(base):
    """/dev/opening/: the three versions of the Opening, each at its real size. Home is built with OPENING_VERSION."""
    names = [("across", "The photograph across the window, the headline at 64 px beneath it"),
             ("words", "The headline at 64 px first, then the photograph across the window"),
             ("column", "The version of 12:05: words at 44 px in columns 1 to 4, the photograph from column 5")]
    out = m_page_head("The Opening", "Three versions of Home’s first screen. Nothing lies on the photograph but the cut; the headline stands on white.",
                      kicker="Development")
    for i, (v, text) in enumerate(names, 1):
        on = " · on Home now" if v == OPENING_VERSION else ""
        out += f'<p class="wrap kicker type-label">Version {i}: {e(text)}{on}</p>' + m_opening(CORE_LINE, version=v)
    return out.replace("<h1>Visual storytelling", '<p class="h1">Visual storytelling').replace("Africa.</h1>", "Africa.</p>")


def tpl_images(base):
    """/dev/images/: every image position on the site. Choosing the images is filling these slots (Thomas, 11 November 2026)."""
    need = lambda r: -(-ROLES[r][1] * 2 // 100) * 100          # twice the shown width, rounded up to 100 px
    rows = "".join(f'<tr><td class="mono">{x["id"]}</td><td>{e(x["page"])}</td><td>{e(ROLES[x["role"]][0])}</td><td>{x["ratio"]}</td>'
                   f'<td class="n">{ROLES[x["role"]][1]:,}</td><td class="n">{need(x["role"]):,}</td>'
                   f'<td>{e(PICKS[x["id"]]["ar"]) if x["id"] in PICKS else "—"}</td></tr>' for x in SLOTS)
    by_page, by_ratio = {}, {}
    for x in SLOTS:
        by_page[x["page"]] = by_page.get(x["page"], 0) + 1
        by_ratio[x["ratio"]] = by_ratio.get(x["ratio"], 0) + 1
    pages = "".join(f"<li><span>{e(k)}</span><span>{v}</span></li>" for k, v in by_page.items())
    ratios = " · ".join(f"{v} at {k}" for k, v in sorted(by_ratio.items(), key=lambda kv: -kv[1]))
    return (sec(head("Images", f"Every image position on the site: {len(SLOTS)} slots, {len(PICKS)} filled. Choosing the images is filling these slots. "
                     "A photograph is entered in PICKS in src/build.py under its slot, with its AR ID, place and year; its caption and its "
                     "link into the archive then build themselves. By proportion: " + ratios + ".", level=1), "page-head")
            + sec(head("By page") + f'<ul class="dev-list">{pages}</ul>')
            + sec(head("Every slot", "Shown width is on a 1,440 px screen; the file is at least twice that. A full-bleed photograph is as wide as the window.")
                  + '<div class="table-scroll"><table class="dev-table"><thead><tr><th>Slot</th><th>Page</th><th>Shown as</th><th>Proportion</th>'
                    f'<th class="n">Shown, px</th><th class="n">File at least, px</th><th>Picked</th></tr></thead><tbody>{rows}</tbody></table></div>'))


def tpl_modules(base):
    """Every module with its variants. Built with SHOW_EMPTY on, so the modules that wait for data show their placeholders."""
    global SHOW_EMPTY
    SHOW_EMPTY = True
    try:
        return _tpl_modules(base)
    finally:
        SHOW_EMPTY = False


def _tpl_modules(base):
    t = THEMES[0]
    intro = (m_page_head("Modules", "Every module of the site with each of its variants, on the grid, as the wireframe builds them. "
                         "From Website – modules (05 Website), approved 8 November 2026. Grey boxes are images at their proportions; "
                         "text with a dotted underline is draft copy. The header and the footer are the page’s own.", statement_draft=True)
             + f'<div class="wrap"><p class="small">Show the grid with the button in the strip or the key G. Each module’s label gives its number and variant.</p></div>')
    sample_box = '<dl class="facts"><dt>Images</dt><dd>1,122</dd><dt>Countries</dt><dd>3</dd></dl>'
    return (intro
            + m_opening(CORE_LINE, "One line beneath the heading, at most; on Home nothing more.")
            + m_page_head("Page head", "A statement of at most 25 words under the title, in the right columns.", kicker="Kicker", meta=["279 images in the archive", "House Collection"])
            + m_page_head("Page head with doors", doors=m_doors("a", doors=[door("#", "Kicker", "First door", "A line of at most 15 words.", dark=True), door("#", "Kicker", "Second door", "A line of at most 15 words.")]))
            + m_page_head("Page head, then the lead", "The page opening of the theme and collection pages: the head, then the lead photograph, full bleed.")
            + m_photo("Lead image", "21/9", "a", lead=True)
            + m_text("Text section", ["Title left, text right: 60 to 160 words of text in the right columns, the measure capped at about 70 characters a line."], "a")
            + m_text("With a facts box", ["The text, then the facts box in the right columns under it."], "b", box=sample_box)
            + m_text("With a contact", ["The text, then the contact as the right column’s end."], "c", contact=("Partnerships", EMAIL_PARTNERS))
            + m_text(None, ["The intro on Home: two or three sentences in columns 1–8 under the Opening, with the ways on."], "d",
                     links=[button("#", "Explore the themes", quiet=True), button("#", "How partners use the archive", quiet=True)])
            + m_rows([("A list under rules", "Several short sections as one module, each a heading left and its text right."), ("The second", "Used on Privacy.")])
            + m_photo("Full bleed", "21/9", "a", caption="AR-ID · The caption, at most 40 words, led by the AR ID where the image is featured.")
            + m_photo("On the columns", "3/2", "b", caption="AR-ID · The caption.")
            + m_photo("Photograph and text", "3/2", "c", text=heading("Beside the photograph", 3) + draft("The text in the other half of the columns; the next one alternates."), side="left")
            + m_photo("Photograph and text", "4/5", "c", text=heading("Alternating", 3) + draft("The photograph on the right this time."), side="right")
            + m_photo("Photograph and text, wide", "3/2", "c", text=heading("The wide form", 3) + draft("The photograph over eight columns, the words in four: the large photograph of a story."), side="left", wide=True)
            + m_grid("e", label="Image", title="One large and a row of three", aside=draft("The words that belong to the set stand here, beside the large photograph: a theme’s text, a collection’s facts, a project’s words."))
            + m_grid("a", 3, "Image", title="Three in a row")
            + m_themes(base, "a") + m_themes(base, "b") + m_themes(base, "c", current=t)
            + m_collection(base)
            + m_numbers(title="Numbers: a row of three")
            + m_doors("b", count=("198", "images on learning in the archive"), main=button("#", "Open in the archive →"), quiet=button("#", "Request access", quiet=True), line=THEME_ACTION_LINE)
            + m_numbers([("72", "Mali"), ("21", "Kenya"), ("105", "The Gambia")], None, "c", title="A count by country", note_text="Illustrative figures; the real counts come from the AR Metadata sheet.")
            + m_partners(6)
            + m_use("a") + m_use("b") + m_use("c", "Partner news")
            + m_doors("c", links=[button("#", "The ways on", quiet=True), button("#", "A second quiet link", quiet=True)])
            + m_doors("c", links=[button("#", "On the left edge, under a full-width module", quiet=True)], tight=True, left=True)
            + m_doors("d", kicker="Contact band", address=EMAIL_PRESS, line="A line of at most 15 words.")
            + m_items("Item list: plain", PRINCIPLES[:3], "a")
            + m_items("Five in one row", PRINCIPLES + [("Fair terms", "One download, one licence, free of charge.")], "a", cls="five")
            + m_items("Numbered steps", ACCESS_STEPS, "b")
            + m_items("Accordion", RULES[:3], "c")
            + m_items("With images", [("Name", "Role, a line.", "Portrait"), ("Name", "Role, a line.", "Portrait"), ("Name", "Role, a line.", "Portrait")], "d", image_ratio="1/1")
            + m_items("Chips", [(x["name"], "#") for x in THEMES], "e")
            + m_sponsor("theme") + m_sponsor("collection")
            + m_form("a", title="The long form", fields=[("Organisation", "text"), ("Email", "email"), ("How you will use the images", "textarea")],
                     aside=heading("What happens next", 3) + draft("The aside in columns 7–12."), consent=REQUEST_CONSENT, button_label="Send the request")
            + m_form("b", title="Three short forms", forms=[("Report a use", "A line.", [("Where it appeared", "text"), ("Link", "url")]),
                                                               ("Request imagery", "A line.", [("What you are looking for", "textarea")]),
                                                               ("What are you working on?", "A line.", [("Your project", "textarea")])])
            + m_form("c", title="A single quiet action", button_label="Book a feedback call", lead=draft("Optional, never required.", "p", "small")))


# ---------------------------------------------------------------------------------------------
# The 16 pages (Website – Site map and user flows, 05 Website)
# ---------------------------------------------------------------------------------------------
PAGES = [
    dict(path="", title="Africa Reframed", slug="home", tpl="home", nav=None,
         desc="Visual storytelling for a new partnership between Europe and Africa: a partner archive of real images from Mali, Kenya and The Gambia."),
    dict(path="themes/", title="Themes", slug="themes", tpl="themes", nav="themes",
         desc="Five themes, read in order: people learn, put their skills to work, live connected lives in modern cities, and make culture."),
    *[dict(path=f"themes/{t['slug']}/", title=t["name"], slug=t["slug"], tpl="theme", nav="themes", theme=t,
           desc=t["statement"]) for t in THEMES],
    dict(path="collections/", title="Collections", slug="collections", tpl="collections", nav="collections",
         desc="The collections in the Africa Reframed archive and the people behind them."),
    dict(path="collections/house-collection/", title="House Collection", slug="house-collection", tpl="collection", nav="collections",
         collection=HOUSE_COLLECTION, desc=HOUSE_LINE),
    dict(path="collections/waste-to-value/", title=WTV, slug="waste-to-value", tpl="collection", nav="collections",
         collection=WTV_COLLECTION,
         desc="Seven young companies in Kenya, Uganda and Rwanda turning waste into fuel, building materials, packaging and services, photographed for BESTSELLER FOUNDATION."),
    dict(path="partners/", title="Partners", slug="partners", tpl="partners", nav="partners",
         desc="How organisations use the Africa Reframed archive, the rules for using the images, and how companies sponsor a collection."),
    dict(path="partner-portal/", title="Partner portal", slug="portal", tpl="portal", nav="portal",
         desc="Log in to the Africa Reframed archive, report a use, request imagery and see what is new for partners."),
    dict(path="request-access/", title="Request access", slug="request", tpl="form", nav=None,
         desc="Request access to the Africa Reframed archive: free for selected non-profit and public partners."),
    dict(path="about/", title="About", slug="about", tpl="text", nav="about", desc=ABOUT_LINE),
    dict(path="press/", title="Press room", slug="press", tpl="press", nav=None,
         desc="The Africa Reframed press room: the relaunch, a fact sheet, press images for editorial use and a press contact."),
    dict(path="contact/", title="Contact", slug="contact", tpl="text", nav=None, desc="How to reach Africa Reframed."),
    dict(path="privacy/", title="Privacy", slug="privacy", tpl="text", nav=None,
         desc="What Africa Reframed collects when you request access or write to us, and why."),
]
PAGES += [dict(path=f"about/artists/{a['slug']}/", title=a["name"], slug=f"artist-{a['slug']}", tpl="artist", nav="about",
                desc=a["line"], artist=a, doc_title=f"{a['name']} · Artists · Africa Reframed",
                share=f"assets/artists/{a['slug']}/share.jpg") for a in ARTISTS]
PAGES += [dict(path=FILMS["path"], title=FILMS["name"], slug="films", tpl="artist", nav="about", desc=FILMS["line"], artist=FILMS,
               doc_title="Films at Øksnehallen · Africa Reframed", share="assets/artists/films/share.jpg")]


# ---------------------------------------------------------------------------------------------
# The development page (/dev/): a view generated by every build, removed at launch (LAUNCH = True).
# Decisions and the log live on the Drive; this page only shows the state of the build and points to the masters.
# The repository and this site are public: nothing internal goes here, only links (which need sign-in).
# ---------------------------------------------------------------------------------------------
STAGES = ["Wireframe", "Copy", "Design", "Ready"]
STATE = {}            # slug -> stage; every page is at "Wireframe" until it moves on
TEMPLATE_NAMES = {"home": "Home", "themes": "Index", "collections": "Index", "theme": "Theme page",
                  "collection": "Collection page", "partners": "Partners", "portal": "Partner portal",
                  "form": "Form", "press": "Press room", "text": "Text page", "artist": "Artist page"}
ORDER_OF_WORK = [("Brief", "done", "Website – Brief and build plan"),
                 ("Site map and user flows", "done", "Website – Site map and user flows, and the two maps"),
                 ("Page priorities", "done", "Site map and user flows, section 6: what the five key pages must say and do, ranked"),
                 ("Live wireframe", "done", "This site, version 4: the five key pages arranged by the page priorities"),
                 ("Step 1: the grid, the module list and the header test", "done",
                  "The grid's values in the code with the overlay (below); the module list, Website – modules; what PhotoDeck's Custom CSS/HTML can carry"),
                 ("Step 2: low-resolution modules and the story mockup", "done",
                  "The wireframe rebuilt from the modules, every module at /dev/modules, the five key pages with draft copy, the phone first"),
                 ("Step 3: the look", "next", "The open visual questions in Claude Design canvases: the Opening, the close, the yellow and the black sections"),
                 ("Step 4: refine and build, module by module", "later", "The white header first; the five key pages to closed-preview quality, then the other eleven"),
                 ("Step 5: the archive's look on PhotoDeck", "later", "The white header, DM Sans and the brand yellow, with Thomas's go-ahead"),
                 ("Step 6: the closed preview", "later", "Cloudflare, the real domain, the lock, the forms, then the tests with invited partners"),
                 ("Public launch", "later", "The lock comes off once partners are on board; the checklist below")]
MASTERS = [
    ("Website build – start here", "https://docs.google.com/document/d/1PLereZFoiGvBbCnSAgmI92OPKzN_nVIwT0gmLK2ChW8/edit",
     "Drive, 05 Website", "The handover for the website build: where things stand, what the site follows, the work in order"),
    ("Website – Brief and build plan", "https://docs.google.com/document/d/1a5HFS7CtiNdi1dcYHTFwV089de4adyE8Lp5rNHstD0c/edit",
     "Drive, 05 Website", "What the site is for and how it is built; the master for decisions about the site"),
    ("The design guide", "https://claude.ai/artifact/Y8kTwb8jhEdkVu6buz2Fnx",
     "claude.ai", "The Design System “Africa Reframed”: the identity's rules and building blocks (version 19, 7 November 2026)"),
    ("Website – Site map and user flows", "https://docs.google.com/document/d/1a993qulyFc7dbc-RTrb5fPXg9f9ng9YO0jWs51-HX1E/edit",
     "Drive, 05 Website", "Every page, what it holds, and the journeys across the two sites"),
    ("Africa Reframed Site Map", "https://claude.ai/artifact/6L43Dyxn65x4XmdzoMSNTC",
     "claude.ai", "The site map as an interactive page"),
    ("Africa Reframed User Flows", "https://claude.ai/artifact/2KVB1LcaSvEZtr2WxBf4Yg",
     "claude.ai", "The journeys as an interactive page"),
    ("The engine – brief for brand and design", "https://docs.google.com/document/d/1CWjfHgcrYv1hu4kKf7QfrHZBf1WuqMXzvcFUDZiqLYI/edit",
     "Drive, 02 Brand", "What the brand and the design have to carry"),
    ("AR Archive – Keywording Guide", "https://docs.google.com/document/d/1ECZ01PVkoRsEF7xDRJJq9wQKxKNQcM0wRshxmdtQCYs/edit",
     "Drive, 03 Archive", "The five public themes (section 8b), collection names and credit lines (section 2)"),
    ("AR Archive – Status", "https://docs.google.com/document/d/1k1i4wInA5Ho3gjmkewsVJRLnTqqrXZZSrEkgmekxH8w/edit",
     "Drive, 03 Archive", "The archive's decisions and, for now, the website log"),
    ("Change history", "https://github.com/africareframed/africareframed-site/commits/main",
     "GitHub", "Every change to this site, with what changed and when"),
]
CHECKLIST = [
    ("Page priorities for the five key pages", "Website – Site map and user flows, section 6", "done"),
    ("Visual design applied to every template", "Brand and design project"),
    ("Draft copy approved by Thomas, and copy written for every note", "{drafts} drafts, {notes} notes open"),
    ("Public images chosen: released, no minors (the public column in the AR Metadata sheet)", "{images} image boxes open"),
    ("A share image for each page we share (1200 × 627, public-safe)", "Brief, Sharing and LinkedIn"),
    ("Theme keywords in the archive, replacing the interim searches", "Keywording Guide, section 8b"),
    ("Request access and the portal forms connected to the partner database", "Build decision (form service or Cloudflare)"),
    ("Header pixel-identical with the archive's", "PhotoDeck custom CSS"),
    ("Real domain: africareframed.com through Cloudflare, and SITE_URL switched", "src/build.py"),
    ("Archive pointed at the real domain: logo link, menu items, About and Contact redirects", "Brief, section 10"),
    ("About: the supporters’ logo files (official, one-colour) in, and a courtesy note sent to each", "About page – build brief, section 0"),
    ("Every archive link to this site keeps ?src=archive (the partner menu), and the Privacy line checked against the Danish cookie rules", "PhotoDeck menu, logo and footer; Privacy"),
    ("Terms proper confirmed, and Using the images checked against them", "Archive, Terms"),
    ("Tests: deep links signed out and in; phones inside LinkedIn's browser; previews in Post Inspector", "Brief, sections 1 and 5"),
    ("LAUNCH = True in src/build.py: removes this page, the wireframe strip and noindex", "src/build.py"),
]
LINK_RE = re.compile(r'href="(https://archive\.africareframed\.com[^"]*)"[^>]*>(.*?)</a>', re.S)


def sec(inner, cls="", sid=None):
    """A plain section (the development page only; the site's pages are built from modules)."""
    a = f' id="{sid}"' if sid else ""
    return f'<section class="sec {cls}"{a}><div class="wrap">{inner}</div></section>'


def head(title, lead=None, kicker=None, level=2):
    k = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
    l = f'<p class="lead">{e(lead)}</p>' if lead else ""
    return f'{k}<h{level}>{e(title)}</h{level}>{l}'


def doors(*buttons):
    return f'<p class="doors">{"".join(buttons)}</p>'


def page_stats(main):
    return dict(notes=main.count('class="note"'), images=main.count('class="img'), bars=main.count('class="lines"'), drafts=main.count('class="draft"'))


def git_log(n=12):
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "log", f"-n{n}", "--date=format:%d %b %Y, %H:%M",
                              "--pretty=format:%h|%ad|%s"], capture_output=True, text=True, timeout=20).stdout
        return [line.split("|", 2) for line in out.splitlines() if line.count("|") >= 2]
    except Exception:
        return []


def grid_table():
    """The grid's values, from GRID, for the development page."""
    d, t, p = GRID["desktop"], GRID["tablet"], GRID["phone"]
    rows = [
        ("Width", "1,024 px and up (the full width from 1,440 px)", "768–1,023 px", "below 768 px"),
        ("Columns", f'{d["cols"]}, each 80 px at the full width', f'{t["cols"]}', f'{p["cols"]}'),
        ("Gutter", f'{d["gutter"]} px', f'{t["gutter"]} px', f'{p["gutter"]} px'),
        ("Side margins", f'{d["margin"]} px; wider above 1,440 px, with the content centred', f'{t["margin"]} px', f'{p["margin"]} px'),
        ("Content width", f'up to {d["content_max"]:,} px', "fluid", "fluid"),
        ("Header height · logo width", f'{d["header"]} · {d["logo"]} px (the logo is two columns and a gutter)', f'{t["header"]} · {t["logo"]} px', f'{p["header"]} · {p["logo"]} px'),
        ("Measure", "running text up to 32 em, about 70 characters at 17 px, inside its columns", "the same", "the same"),
        ("Between sections", f'{d["section"]} px', f'{t["section"]} px', f'{p["section"]} px'),
        ("Title left, text right", "title in columns 1–4, text in 6–12", "title in 1–3, text in 4–8", "one column, the title first"),
        ("Photographs", "full bleed, edge to edge; on the columns; or from a column line off one edge (the Opening: from column 5 off the right edge, the words in 1–4)",
         "the same three cases; the Opening from the line of column 2 off the right edge, the words below", "the same; the Opening from column 2, the words below"),
    ]
    body = "".join(f"<tr><th>{e(a)}</th><td>{e(b)}</td><td>{e(c)}</td><td>{e(d_)}</td></tr>" for a, b, c, d_ in rows)
    return (f'<div class="table-scroll"><table class="dev-table grid-table"><thead><tr><th></th><th>Desktop</th><th>Tablet</th><th>Phone</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>'
            f'<p class="small">In the code: custom properties in <span class="mono">assets/site.css</span> (--cols, --gutter, --margin, --content-max, --header-h, '
            f'--logo-w, --section), set once per width in <span class="mono">src/build.py</span>; the utility classes .cols, .c1-4, .c6-12, .c5-off and .bleed. '
            f'Proposed as section U in Design guide – review and changes.</p>')


def tpl_dev(rows, links, base):
    def stepper(slug):
        cur = STAGES.index(STATE.get(slug, "Wireframe"))
        return '<span class="stepper">' + "".join(
            f'<span class="{"on" if i == cur else "done" if i < cur else ""}">{e(st)}</span>' for i, st in enumerate(STAGES)) + "</span>"
    tot = {k: sum(r["stats"][k] for r in rows) for k in ("notes", "images", "bars", "drafts")}
    body = "".join(
        f'<tr><td><a href="{base}{r["path"]}">{e(r["title"])}</a></td><td class="mono">/{e(r["path"])}</td>'
        f'<td>{e(TEMPLATE_NAMES[r["tpl"]])}</td><td>{stepper(r["slug"])}</td>'
        f'<td class="n">{r["stats"]["notes"]}</td><td class="n">{r["stats"]["images"]}</td><td class="n">{r["stats"]["bars"]}</td><td class="n">{r["stats"]["drafts"]}</td></tr>'
        for r in rows)
    inventory = (f'<div class="table-scroll"><table class="dev-table"><thead><tr><th>Page</th><th>Address</th><th>Template</th>'
                 f'<th>State</th><th class="n">Notes</th><th class="n">Images to choose</th><th class="n">Text to write</th><th class="n">Draft copy</th></tr></thead>'
                 f'<tbody>{body}</tbody><tfoot><tr><td colspan="4">{len(rows)} pages from {len(set(TEMPLATE_NAMES[r["tpl"]] for r in rows))} templates</td>'
                 f'<td class="n">{tot["notes"]}</td><td class="n">{tot["images"]}</td><td class="n">{tot["bars"]}</td><td class="n">{tot["drafts"]}</td></tr></tfoot></table></div>')
    work = "".join(f'<li class="{st}"><span class="tag {st}">{ {"done": "Done", "next": "Next", "later": "Later"}[st] }</span>'
                   f'<strong>{e(name)}</strong><span>{e(what)}</span></li>' for name, st, what in ORDER_OF_WORK)
    masters = "".join(f'<li><a href="{url}">{e(name)}</a> <span class="where">{e(where)}</span><span>{e(what)}</span></li>'
                      for name, url, where, what in MASTERS)
    deep = "".join(f'<tr><td>{e(label)}</td><td>{e(", ".join(pages))}</td><td class="mono"><a href="{e(url)}">{e(url.replace(ARCHIVE, ""))}</a></td></tr>'
                   for url, (label, pages) in links.items())
    checks = "".join(f'<li><span class="tag {st}">{ {"done": "Done", "open": "Open"}[st] }</span><strong>{e(item)}</strong>'
                     f'<span>{e(where.format(**tot))}</span></li>' for item, where, *rest in CHECKLIST for st in [(rest or ["open"])[0]])
    commits = git_log()
    changes = "".join(f'<li><span class="mono">{e(h)}</span> <span class="where">{e(d)}</span><span>{e(subj)}</span></li>' for h, d, subj in commits)
    changes = (f'<ul class="dev-list">{changes}</ul>' if changes else '<p class="small">No history available in this build.</p>')
    return (sec(head("Development", "How far the site has come, where its masters are, and what is left before launch. "
                     "This page is generated by every build and removed at launch.", level=1), "page-head")
            + sec(head("Where things live")
                  + '<ul class="dev-list"><li><strong>Decisions and the log</strong><span>On the Drive. The Website brief is the master for the site; '
                    'the log is in AR Archive – Status until the work moves to the Brand and design project.</span></li>'
                    '<li><strong>The code and its history</strong><span>On GitHub: every change is a commit with a message.</span></li>'
                    '<li><strong>This page</strong><span>A view of the build, generated from the code, so it cannot go out of date. '
                    'The site is public, so nothing internal is copied here; the links below need your sign-in.</span></li></ul>', "tight")
            + sec(head("Order of work") + f'<ol class="dev-list work">{work}</ol>')
            + sec(head("Pages", "Every page, its template and its state. The counts are what is still to fill: yellow notes, image boxes and text bars (text that cannot be drafted yet, since the content does not exist); and the pieces of draft copy awaiting approval.")
                  + inventory)
            + sec(head("How to read the wireframe")
                  + '<ul class="dev-list"><li><strong>Grey box with a cross</strong><span>An image still to choose, at the size and proportion it will have.</span></li>'
                    '<li><strong>Grey bars</strong><span>Text still to write.</span></li>'
                    '<li><strong>Yellow note</strong><span>What goes there, and where it comes from.</span></li>'
                    '<li><strong>Clean view</strong><span>In the yellow strip: hides the notes and labels, so a page can be shown as a layout.</span></li>'
                    '<li><strong>Grid</strong><span>In the yellow strip, or the key G, or ?grid in the address: draws the columns (blue) and margins (red) of the current width, with the values in a readout.</span></li>'
                    '<li><strong>Module labels</strong><span>Every section carries the number and variant of the module it is built from (Website – modules); hidden in clean view. All modules with their variants: <a href="modules/">/dev/modules</a>.</span></li>'
                    '<li><strong>Draft copy</strong><span>Text with a dotted underline is draft copy written from the masters, to be approved by Thomas; the mark hides in clean view.</span></li></ul>')
            + sec(head("The grid", "Starting values set in step 1 (8 November 2026), on what the design guide already had; to be locked after step 2. "
                       "Shared by the stylesheet, the overlay and this page.")
                  + grid_table())
            + sec(head("Masters") + f'<ul class="dev-list">{masters}</ul>')
            + sec(head("Links into the archive", "Every link from this site into the archive, with its source tag. Signed out, each meets the login wall.")
                  + f'<div class="table-scroll"><table class="dev-table"><thead><tr><th>Link</th><th>On</th><th>Address</th></tr></thead><tbody>{deep}</tbody></table></div>')
            + sec(head("Launch checklist") + f'<ul class="dev-list">{checks}</ul>')
            + sec(head("Recent changes") + changes
                  + doors(button("https://github.com/africareframed/africareframed-site/commits/main", "All changes on GitHub", quiet=True))))

# ---------------------------------------------------------------------------------------------
# The grid (step 1 of the website build, 8 November 2026; starting values, to be locked after step 2)
# ---------------------------------------------------------------------------------------------
# What the design guide already had (README, Layout; tokens): 12 columns with 32 px gutters on desktop; 4 columns with
# 16 px gutters and 16 px side margins on phones; the title in columns 1–4 and the text in 6–12; the 8 px spacing
# scale; the header logo 192–256 px wide on desktop and 128 px on phones; the hero drawn at 1440 × 720 under a header
# row (Opening). The values below fill in what was missing. They are shared: the CSS reads them as custom properties,
# the overlay (the Grid button in the wireframe strip, ?grid in the address, or the key G) draws them, and the
# development page lists them. Proposed as section U in "Design guide – review and changes".
GRID = {
    # Desktop, 1024 px and up. 12 × 80 px + 11 × 32 px = 1,312 px of content; with 64 px margins the page is 1,440 px
    # wide, the format the guide draws the hero in, so column 5 starts at 512 px and columns 1–4 span 416 px: the
    # photograph of the Opening starts on the line of column 5 and the words beside it fill columns 1–4. Above 1,440 px
    # the content stays 1,312 px wide and centred; the margins grow; a photograph that runs off the edge keeps running.
    "desktop": dict(min=1024, cols=12, gutter=32, margin=64, content_max=1312, header=128, logo=192, section=96),
    # Tablet, 768–1023 px: 8 columns with 24 px gutters and 32 px side margins; the menu folds into the menu control
    # (as the archive's does below tablet width); title left, text right becomes title in 1–3 and text in 4–8.
    "tablet": dict(min=768, cols=8, gutter=24, margin=32, header=128, logo=192, section=80),
    # Phone, below 768 px: the guide's 4 columns, 16 px gutters and 16 px margins; one column of content, the title first.
    "phone": dict(min=0, cols=4, gutter=16, margin=16, header=64, logo=128, section=64),
}
# One module (Thomas, 8 November 2026, after the question whether the grid meets a Pentagram or e-Types standard): the column
# pitch is 112 px (80 + 32), and the logo at 192 px is exactly two columns and a gutter, so it sits on the grid at every
# desktop width (inside the guide's 192–256 px range). Two header sizes only: 128 px with the 192 px logo on desktop and
# tablet, 64 px with the 128 px logo on phones. The measure: running text caps at 32 em (about 70 characters at 17 px),
# because the guide's text columns 6–12 are 752 px at the full width, about 95 characters, more than its own 60–75.
GRID_CSS_VARS = """  --cols:12; --gutter:32px; --margin:64px; --content-max:1312px;
  --page-max:calc(var(--content-max) + 2*var(--margin));
  --off-edge:calc((min(100vw,var(--page-max)) - 100vw)/2 - var(--margin));
  --header-h:128px; --logo-w:192px; --section:96px; --section-head:64px; --section-tight:32px; --measure:32em; --measure-intro:30em;
  --fs-display:64px; --fs-title:44px; --fs-head:22px; --fs-text:17px; --fs-small:13px;
"""
# Photographs relate to the grid in three ways (the guide's four image layouts all use the second):
# 1. full bleed (.bleed): edge to edge of the page, ignoring the margins; its caption and credit sit on the grid below;
# 2. on the columns (.cols with c1-12, c6-12 or any span): the photograph starts and ends on column lines;
# 3. off one edge (.c5-off, the Opening): the photograph starts on a column line and runs off one edge of the page,
#    so the words stand on white beside it in columns 1–4 (desktop); below 1,024 px the words move under it and the
#    photograph starts on the line of column 2 (tablet and phone), still running off the right edge.

# ---------------------------------------------------------------------------------------------
# The partner menu (Thomas, 10 November 2026). The archive (PhotoDeck) shows Browse images · Lightbox in its menu; this
# site cannot know who is signed in there (PhotoDeck runs none of our code and tells no other site who is logged in).
# So this site remembers, in the visitor's own browser, that the visitor came back from the archive: every link from the
# archive to this site carries ?src=archive (set in PhotoDeck's menu, logo and footer links). For 30 days after the last
# such return, the menu shows the archive's tools as well. A memory, not a login check: the archive's login stays the
# gate, and signed out the tools meet the login wall, as they do on the archive. ?partner=off forgets it (the wireframe
# strip has the switch). Nothing is sent anywhere; the Privacy page says so. The tag is removed from the address at once,
# so a copied link does not pass the memory on. Runs in the head, so the menu never flickers.
# ---------------------------------------------------------------------------------------------
PARTNER_DAYS = 30
PARTNER_SCRIPT = """<script>
(function(){
  var K = 'ar-partner', now = Date.now(), q = new URLSearchParams(location.search), t = 0;
  var back = q.get('src') === 'archive', off = q.get('partner') === 'off';
  try {
    if (back) localStorage.setItem(K, String(now));
    if (off) localStorage.removeItem(K);
    t = parseInt(localStorage.getItem(K) || '0', 10) || 0;
    if (t && now - t > DAYS * 864e5) { localStorage.removeItem(K); t = 0; }
  } catch (err) {}
  if (t) document.documentElement.classList.add('is-partner');
  if (back || q.has('partner')) {
    if (back) q.delete('src');
    q.delete('partner');
    var rest = q.toString();
    try { history.replaceState(null, '', location.pathname + (rest ? '?' + rest : '') + location.hash); } catch (err) {}
  }
})();
</script>
""".replace("DAYS", str(PARTNER_DAYS))

# ---------------------------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------------------------
LAYOUT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{doc_title}</title>
<meta name="description" content="{desc}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Africa Reframed">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{share}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="627">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="{base}assets/fonts/dm-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{base}assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png">
{partner_script}<link rel="stylesheet" href="{base}assets/site.css?v={stamp}">
</head>
<body class="page-{slug} tpl-{tpl}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="{base}" aria-label="Africa Reframed, home">
      <img src="{base}assets/logo-black.svg" alt="Africa Reframed" class="brand-logo">
    </a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
    <nav class="menu" id="menu" aria-label="Main">
      <a href="{base}themes/"{cur_themes}>Themes</a>
      <a href="{base}collections/"{cur_collections}>Collections</a>
      <a href="{base}partners/"{cur_partners}>Partners</a>
      <a href="{base}about/"{cur_about}>About</a>
      <span class="divider" aria-hidden="true"></span>
      <a class="partner-only" href="{archive_browse}">Browse images</a>
      <a class="partner-only" href="{archive_lightbox}">Lightbox</a>
      <a href="{base}partner-portal/"{cur_portal}>Log in</a>
    </nav>
  </div>
</header>
{strip}<main id="main">
{main}
</main>
<footer class="site-footer">
  <div class="wrap close">
    {close_pattern}
    <div class="close-words">
    <img src="{base}assets/logo-white.svg" alt="Africa Reframed" class="close-logo" width="192" height="39">
    <p class="about-line">{about_line}</p>
    <p class="links">
      <a href="{base}about/">About</a> ·
      <a href="{base}press/">Press</a> ·
      <a href="{base}contact/">Contact</a> ·
      <a href="{base}privacy/">Privacy</a> ·
      <a href="{base}request-access/">Request access</a> ·
      <a href="{archive}/terms">Terms</a> ·
      <span>&copy; Africa Reframed</span>
    </p>
    </div>
  </div>
</footer>
<script>
(function(){{
  var t = document.querySelector('.menu-toggle'), m = document.getElementById('menu');
  t.addEventListener('click', function(){{
    var open = t.getAttribute('aria-expanded') === 'true';
    t.setAttribute('aria-expanded', String(!open));
    m.classList.toggle('open', !open);
  }});
  var b = document.querySelector('.notes-toggle');
  if (!b) return;
  function setClean(on){{
    document.body.classList.toggle('clean', on);
    b.setAttribute('aria-pressed', String(on));
    b.textContent = on ? 'Show notes' : 'Clean view';
  }}
  try {{ setClean(localStorage.getItem('ar-clean') === '1'); }} catch (err) {{}}
  b.addEventListener('click', function(){{
    var on = !document.body.classList.contains('clean');
    setClean(on);
    try {{ localStorage.setItem('ar-clean', on ? '1' : '0'); }} catch (err) {{}}
  }});
  /* The grid overlay: the Grid button, ?grid in the address, or the key G. Draws the columns of the current width. */
  var g = document.querySelector('.grid-toggle'), ov = document.querySelector('.grid-overlay');
  if (!g || !ov) return;
  var cols = ov.querySelector('.cols'), read = ov.querySelector('.grid-read');
  function cssVar(name){{ return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }}
  function draw(){{
    var n = parseInt(cssVar('--cols'), 10) || 12, h = '';
    for (var i = 1; i <= n; i++) h += '<div class="col col-' + i + '">' + i + '</div>';
    cols.innerHTML = h;
    var first = cols.firstElementChild, w = first ? Math.round(first.getBoundingClientRect().width * 10) / 10 : 0;
    var bp = window.innerWidth >= 1024 ? 'desktop' : window.innerWidth >= 768 ? 'tablet' : 'phone';
    read.textContent = window.innerWidth + ' px · ' + bp + ' · ' + n + ' columns × ' + w + ' px · gutter ' + cssVar('--gutter')
      + ' · margin ' + cssVar('--margin') + ' · content up to ' + cssVar('--content-max') + ' · header ' + cssVar('--header-h') + ' · logo ' + cssVar('--logo-w');
  }}
  function setGrid(on){{
    document.body.classList.toggle('show-grid', on);
    g.setAttribute('aria-pressed', String(on));
    if (on) draw();
  }}
  var want = /[?&]grid(=|&|$)/.test(location.search);
  try {{ setGrid(want || localStorage.getItem('ar-grid') === '1'); }} catch (err) {{ setGrid(want); }}
  g.addEventListener('click', function(){{
    var on = !document.body.classList.contains('show-grid');
    setGrid(on);
    try {{ localStorage.setItem('ar-grid', on ? '1' : '0'); }} catch (err) {{}}
  }});
  document.addEventListener('keydown', function(ev){{
    if (ev.key !== 'g' || ev.metaKey || ev.ctrlKey || ev.altKey || /input|textarea|select/i.test(ev.target.tagName)) return;
    g.click();
  }});
  window.addEventListener('resize', function(){{ if (document.body.classList.contains('show-grid')) draw(); }});
}})();
</script>
</body>
</html>
"""

CSS = """/* DM Sans, served from this site (SIL Open Font License 1.1: assets/fonts/OFL.txt) */
@font-face{font-family:"DM Sans";font-style:normal;font-display:swap;font-weight:100 1000;src:url(fonts/dm-sans-latin-ext.woff2) format("woff2");
  unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:"DM Sans";font-style:normal;font-display:swap;font-weight:100 1000;src:url(fonts/dm-sans-latin.woff2) format("woff2");
  unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
:root{
  --ground:#151515; --paper:#ffffff; --ink:#151515; --ink-soft:#5c5a55;
  --text-on-dark:#e3e3e3; --accent:#eacb84; --line:#e6e4df; --wash:#f6f5f2;
  --wire-note:#fef98b;  /* the strip and notes of the wireframe; gone at launch */
  --wire:#ecebe7; --wire-line:#cfccc5; --bar:#e3e1dc;
  --font:"DM Sans",system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
""" + GRID_CSS_VARS + """}
*{box-sizing:border-box}
html,body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font);font-size:var(--fs-text);line-height:1.55}
a{color:inherit}
.wrap{max-width:var(--page-max);margin:0 auto;padding:0 var(--margin)}
/* The 12-column grid as a utility: children name their columns (c1-4: columns 1 to 4; c6-12: 6 to 12; c5-off: from column 5 off the right edge of the page) */
.cols{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));column-gap:var(--gutter)}
.c1-4{grid-column:1/5}.c6-12{grid-column:6/-1}.c1-12{grid-column:1/-1}.c1-8{grid-column:1/9}.c1-6{grid-column:1/7}.c7-12{grid-column:7/-1}
.c-half{grid-column:span 6}.c-offset{grid-column:6/-1}
.c5-off{grid-column:5/-1;margin-right:var(--off-edge)}
.c1-9{grid-column:1/10}.c5-12{grid-column:5/-1}.c-wide{grid-column:span 8}.c-side{grid-column:span 4}
.bleed{width:100%;max-width:none}
.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:8px;background:var(--ink);color:#fff;padding:8px 12px;z-index:20}
:focus-visible{outline:2px solid var(--ink);outline-offset:2px}

/* Header: white, the black logo top left, the menu in black (the guide, Header; Thomas, 8 November 2026: pulled forward
   from step 4 so both live sites match). Logo left, one flat menu right, pixel-identical to the archive's.
   On the grid: the logo's left edge on the line of column 1, the menu's right edge on the right edge of column 12. */
.site-header{background:var(--paper);color:var(--ink)}
.bar{display:flex;align-items:center;justify-content:space-between;gap:24px;min-height:var(--header-h)}
.brand{display:inline-flex;align-items:center;min-height:44px}
.brand-logo{width:var(--logo-w);height:auto;display:block}
.menu{display:flex;align-items:center;gap:24px;font-size:var(--fs-text)}
.menu a{padding:6px 0;border-bottom:2px solid transparent;color:var(--ink);white-space:nowrap;text-decoration:none}
.menu a:hover{color:var(--ink-soft)}
.menu a[aria-current="page"]{border-bottom-color:var(--ink)}
.divider{display:inline-block;width:1px;height:18px;background:var(--ink);margin:0 4px}
/* The partner menu: the archive's tools show only to a visitor this browser remembers coming back from the archive
   (PARTNER_SCRIPT); so does the strip's switch to the public menu. */
html:not(.is-partner) .partner-only,html:not(.is-partner) .partner-switch{display:none}
.menu-toggle{display:none;background:none;border:0;padding:8px;cursor:pointer;width:44px;height:44px;flex-direction:column;justify-content:center;gap:5px}
.menu-toggle span{display:block;height:2px;background:var(--ink)}

/* The wireframe strip */
.wire-strip{background:var(--wire-note);color:var(--ink);font-size:var(--fs-small);padding:6px 0}
.wire-strip .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px}
.strip-tools{display:flex;align-items:center;gap:14px;white-space:nowrap}
.strip-tools a{color:var(--ink)}
.notes-toggle{font:inherit;font-size:var(--fs-small);background:transparent;border:1px solid rgba(21,21,21,.4);border-radius:0;padding:3px 10px;cursor:pointer;white-space:nowrap;color:var(--ink)}

/* Wireframe parts */
.img{position:relative;width:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:0;
  background:
    linear-gradient(to top right,transparent calc(50% - .7px),var(--wire-line) calc(50% - .7px),var(--wire-line) calc(50% + .7px),transparent calc(50% + .7px)),
    linear-gradient(to bottom right,transparent calc(50% - .7px),var(--wire-line) calc(50% - .7px),var(--wire-line) calc(50% + .7px),transparent calc(50% + .7px)),
    var(--wire)}
.img span{background:var(--wire);color:#6b6862;font-size:var(--fs-small);line-height:1.35;padding:4px 8px;max-width:80%;text-align:center;border-radius:0}
.img.dark{background:
    linear-gradient(to top right,transparent calc(50% - .7px),#454545 calc(50% - .7px),#454545 calc(50% + .7px),transparent calc(50% + .7px)),
    linear-gradient(to bottom right,transparent calc(50% - .7px),#454545 calc(50% - .7px),#454545 calc(50% + .7px),transparent calc(50% + .7px)),
    #2a2a2a}
.img.dark span{background:#2a2a2a;color:#a9a6a0}
.note{display:block;width:fit-content;max-width:62ch;font-size:var(--fs-small);line-height:1.45;background:#fff8c2;border-left:3px solid #e0cf3c;padding:8px 12px;color:#4b4943;margin:4px 0 16px}
.lines{max-width:60ch;margin:8px 0 16px}
.lines i{display:block;height:10px;background:var(--bar);border-radius:0;margin:0 0 12px}
.lines i:last-child{width:62%}
.ph-text{color:#9a978f;font-style:italic;font-size:var(--fs-small);margin:0 0 8px}
body.clean .note,body.clean .img span{display:none}
/* Draft copy: written from the masters, marked until Thomas approves it; the mark hides in clean view */
.draft{text-decoration:underline dotted #b8a62a;text-decoration-thickness:1px;text-underline-offset:3px}
body.clean .draft{text-decoration:none}
/* Modules: each section carries its number and variant as a label (Website – modules); hidden in clean view */
.mod{position:relative;padding-top:var(--section)}
.mod::before{content:attr(data-mod);box-sizing:border-box;position:absolute;left:0;top:calc(var(--section) - 22px);font-size:var(--fs-small);letter-spacing:.04em;text-transform:uppercase;color:#8a877f;background:#fff8c2;padding:1px 8px;border-radius:0;z-index:2;max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mod.page-head::before,.mod.opening::before{top:8px}
body.clean .mod::before{display:none}
.mod.band .action{border-top:2px solid var(--ink);padding-top:24px}
/* The yellow as a whole surface, once on a page: the way into the archive (rule 18; the 2016 folder's own drawing of a website) */
.mod.band.archive{background:var(--accent);padding:var(--section-head) 0;margin-top:var(--section)}
.mod.band.archive .action{border-top:0;padding-top:0}
.mod.band.archive .button.archive{background:var(--ink);border-color:var(--ink);color:#fff}
.mod.band.archive .button.archive:hover{background:#fff;border-color:#fff;color:var(--ink)}
.mod.band.archive .button.quiet{border-color:var(--ink)}
.mod.band.archive .small,.mod.band.archive .num span{color:var(--ink)}
.mod.band::before{top:4px}
.mod .mod{padding-top:32px}
.mod .mod .wrap{padding:0;max-width:none}
.mod .mod::before{top:8px}
.mod.chapter{padding-top:calc(var(--section)*2)}
.mod.chapter::before{top:calc(var(--section)*2 - 22px)}
.mod.tight{padding-top:calc(var(--section)/2)}  /* grouped with the module before it: half the distance */
.mod.tight::before{top:calc(var(--section)/2 - 22px)}
.mod.band + .mod.band{margin-top:0}
.mod .cols + .cols{margin-top:24px}
.head-right{padding-top:8px}
.lead-photo{margin-top:32px}
.credit{font-size:var(--fs-small);line-height:1.45;color:var(--ink-soft);margin:8px 0 0;max-width:none}
.credit .caption{color:var(--ink);display:block}   /* one pattern: the caption, led by the AR ID; the credit on the line beneath */
.frame{margin:0;min-width:0}
.frame .credit,.theme-entry .credit{font-size:var(--fs-small);color:var(--ink-soft);margin:8px 0 0}
.credit a{color:inherit}
.credit.group{margin-top:8px}
.imgs .frame .credit{margin-bottom:8px}
.kicker-h{margin-top:0}
.imgs{display:grid;gap:8px;margin-top:8px}
.grid-3{grid-template-columns:repeat(3,minmax(0,1fr))}
.grid-4{grid-template-columns:repeat(4,minmax(0,1fr))}
.grid-strip{grid-template-columns:repeat(3,minmax(0,1fr))}
.grid-mixed{grid-template-columns:repeat(4,minmax(0,1fr));align-items:start}
.bleed-img{border-radius:0}
.theme-entry{display:flex;flex-direction:column;text-decoration:none;scroll-snap-align:start}
.theme-entry h3{margin:4px 0 8px}
.theme-entry p{font-size:var(--fs-text);color:var(--ink-soft);margin:0 0 8px}
.theme-entry:hover h3{text-decoration:underline}
.theme-rows{margin-top:8px}
.theme-entry.row{display:grid;grid-template-columns:72px 1.3fr 1fr;gap:32px;align-items:center;padding:32px 0;border-top:1px solid var(--line)}
.theme-entry.row .order{font-size:var(--fs-title);font-weight:300;line-height:1;margin:0;color:var(--ink)}
.theme-entry.row h3{font-size:var(--fs-head);font-weight:700;margin:0 0 8px}
.theme-nav .dir{display:block;font-size:var(--fs-text);color:var(--ink-soft);margin-bottom:8px}
.theme-nav .order{display:none}   /* previous and next say which way; the theme's number stands on its own page */
.e-words .facts{margin-top:24px}
.e-words p{max-width:var(--measure)}
.row-3{margin-top:24px}
.chapter-title{font-size:var(--fs-title);font-weight:300;line-height:1.05;letter-spacing:-.02em;margin:0 0 16px}   /* a chapter of a long page: its title at the page-title size, in Light */
/* A black section: the same modules with the ground and the ink exchanged. Black holds one kind of content, the exhibitions
   and the artists' works (Thomas, 11 November 2026; Quality rules, rule 18); it is also the ground of the footer's close. */
.dark{background:var(--ground);color:#fff;--ink:#fff;--ink-soft:#b9b7b1;--line:#3a3a3a;--paper:#151515;--wire:#242424;--wire-line:#3c3c3c;--wash:#1e1e1e;
  margin-top:calc(var(--section)*2);padding-bottom:var(--section)}
.dark > .mod.chapter:first-child{padding-top:var(--section)}
.dark > .mod.chapter:first-child::before{top:calc(var(--section) - 22px)}
.dark .img span{background:var(--wire);color:#9a978f}
.dark .button.quiet{background:transparent;border-color:#fff;color:#fff}
.dark .button.quiet:hover{background:#fff;color:var(--ground)}
.dark + .mod.chapter{padding-top:calc(var(--section)*2)}
.dark img.work{background:#1e1e1e}
.rows .cols{border-top:1px solid var(--line);padding-top:24px}
.rows .cols h2{margin:0}
.logo-card{aspect-ratio:3/2;display:flex;align-items:center;justify-content:center;border:1px solid var(--line);background:var(--paper)}
.logo-card.dark{background:var(--ground);border-color:var(--ground)}
.logo-card img{width:56%;height:auto}   /* air between the large photograph's caption and the row */
.collection-card{text-decoration:none;align-items:center;margin-top:8px}
.collection-card:hover .h-big{text-decoration:underline}
.item .img{margin-bottom:12px}
.acc{border-top:1px solid var(--ink);padding:0}
.acc:last-child{border-bottom:1px solid var(--ink)}
.acc summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;padding:16px 0;font-size:var(--fs-text)}
.acc summary::-webkit-details-marker{display:none}
.acc .plus{width:14px;height:14px;position:relative;flex:none}
.acc .plus::before,.acc .plus::after{content:"";position:absolute;background:var(--ink);left:0;top:6px;width:14px;height:2px}
.acc .plus::after{transform:rotate(90deg)}
.acc[open] .plus::after{display:none}
.acc p{margin:0 0 16px}

/* About: the three lines of activity, the register, the projects (About page – build brief) */
.channels{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--gutter)}
.channels a{display:block;text-decoration:none;border-top:2px solid var(--ink);padding-top:16px;height:100%}
.channels strong{display:block;font-weight:700;font-size:var(--fs-head);line-height:1.15;margin:0 0 8px}
.channels a:hover strong{text-decoration:underline}
.channels .channel-line{font-size:var(--fs-text);color:var(--ink-soft)}
.register{margin:0 0 8px;padding:24px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.register-lead{font-size:var(--fs-small);color:var(--ink-soft);margin:0 0 8px}
.register-names{display:flex;flex-wrap:wrap;gap:4px 32px;font-size:var(--fs-text);line-height:1.4;margin:0 0 12px;max-width:none}
.register-after{margin:0}
.hinge{font-size:var(--fs-head);font-weight:300;line-height:1.45;max-width:32ch;margin:0}
.project-title{font-size:var(--fs-head);font-weight:700;line-height:1.15;margin:0 0 12px}
.kicker.state{color:var(--ink);font-weight:700}
.principles.five{grid-template-columns:repeat(5,minmax(0,1fr))}
.cards-6{display:grid;gap:var(--gutter);margin-top:8px;grid-template-columns:repeat(6,minmax(0,1fr))}
.cards-6 .item h3{font-size:var(--fs-text);margin:8px 0 4px}
.cards-6 .item p{font-size:var(--fs-small);line-height:1.45}

/* Collections: the list of cards, and a sponsored collection's companies and the founders' words (the collection template) */
.collection-list .collection-card + .collection-card{margin-top:var(--section-tight);padding-top:var(--section-tight);border-top:1px solid var(--line)}
.contents{list-style:none;padding:0;margin:32px 0 0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gutter)}
.contents a{display:block;text-decoration:none;border-top:2px solid var(--ink);padding-top:12px;height:100%}
.contents .kicker{display:block;margin:0 0 8px}
.contents strong{display:block;font-weight:700;font-size:var(--fs-text);line-height:1.15;margin:0 0 4px}
.contents .contents-line{font-size:var(--fs-text);color:var(--ink-soft)}
.contents a:hover strong{text-decoration:underline}
.story-headline{font-size:var(--fs-head);font-weight:700;line-height:1.15;letter-spacing:-.01em;margin:0 0 12px;max-width:24ch;text-wrap:balance}
.story-company{font-size:var(--fs-text);color:var(--ink-soft);margin:0 0 16px}
.story-company strong{color:var(--ink);font-weight:700}
.story .since{border-top:1px solid var(--line);padding-top:12px;margin-top:12px}
[id^="story-"]{scroll-margin-top:24px}
.quote{margin:0 0 32px}
.quote blockquote{margin:0}
.quote blockquote p{font-size:var(--fs-head);font-weight:300;line-height:1.45;max-width:36ch;margin:0 0 8px}

/* Type: six sizes and three weights (Quality rules, rule 11; Thomas, 11 November 2026). Every size on the site is one of
   the named styles --fs-display 64, --fs-title 44, 32 (the page title below desktop), --fs-head 22, --fs-text 17 and
   --fs-small 13; nothing else sets a size. Weights: 400 text, 700 titles, 300 the big number and the intro.
   A page shows four sizes at most: the page title, the heading and the intro, the text, the small print.
   A title is told from its text by weight and position (title left, text right), not by a large jump in size. */
h1{font-weight:700;font-size:var(--fs-title);line-height:1.05;margin:0 0 16px;letter-spacing:-.02em;max-width:20ch;text-wrap:balance}
h2{font-weight:700;font-size:var(--fs-head);line-height:1.15;margin:0 0 12px;letter-spacing:-.01em;text-wrap:balance}
h3{font-weight:700;font-size:var(--fs-text);line-height:1.15;margin:12px 0 4px;text-wrap:balance}
p{margin:0 0 12px;max-width:var(--measure);text-wrap:pretty}  /* the measure: at most 75 characters a line, 60 to 70 the aim (rule 10) */
.lead,.statement{font-size:var(--fs-head);font-weight:300;line-height:1.45;max-width:var(--measure-intro);margin:0 0 24px;color:var(--ink);text-wrap:pretty}
.kicker{font-size:var(--fs-small);line-height:1.45;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft);margin:0 0 8px}
.small{color:var(--ink-soft)}
.h-big{font-size:var(--fs-head);font-weight:700;line-height:1.15;margin:4px 0 12px}
.h-big a{overflow-wrap:anywhere}
.list{margin:0 0 16px;padding-left:24px}
.list li{margin:4px 0}
main li{max-width:var(--measure)}
.dev-list li{max-width:none}
.meta-row{display:flex;flex-wrap:wrap;gap:4px 24px;color:var(--ink-soft);margin:0 0 16px}
.meta-row a{color:var(--ink);display:inline-block;padding:12px 0;margin:-12px 0}
.textlink{text-decoration:underline;text-underline-offset:4px}

/* Sections: the vertical rhythm on the 8 px scale (96 px between sections on desktop, 80 on tablets, 64 on phones) */
main{padding-bottom:var(--section)}
.sec{padding-top:var(--section)}
.sec.page-head{padding-top:var(--section-head)}
.sec.tight{padding-top:var(--section-tight)}
.sec.band{background:var(--wash);padding:var(--section-head) 0;margin-top:var(--section)}
.sec.band + .sec.band{margin-top:0}
.grid-2{display:grid;grid-template-columns:1.4fr 1fr;gap:56px;align-items:start}
.split{display:grid;grid-template-columns:1.2fr 1fr;gap:48px;align-items:center;text-decoration:none;margin-top:8px}
.card-link:hover .h-big{text-decoration:underline}
.cards-2,.cards-3,.cards-4,.cards-5{display:grid;gap:var(--gutter);margin-top:8px}
.cards-2{grid-template-columns:repeat(2,minmax(0,1fr))}
.cards-3{grid-template-columns:repeat(3,minmax(0,1fr))}
.cards-4{grid-template-columns:repeat(4,minmax(0,1fr))}
.cards-5{grid-template-columns:repeat(5,minmax(0,1fr))}
.card{border-top:2px solid var(--ink);padding:16px 0 0}
.card h3{margin-top:0}
.example .img{margin-bottom:12px}

/* Buttons */
.doors{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0 12px}
.button{display:inline-flex;align-items:center;min-height:48px;padding:0 24px;background:var(--ink);color:#fff;font:inherit;font-weight:400;font-size:var(--fs-text);border-radius:0;border:1px solid var(--ink);text-decoration:none;cursor:pointer}
.button:hover{background:#fff;color:var(--ink)}
.button:active{background:var(--wash);color:var(--ink)}
.button.archive{background:var(--accent);border-color:var(--accent);color:var(--ink)}   /* the yellow's one job: the way into the archive */
.button.archive:hover{background:var(--ink);border-color:var(--ink);color:#fff}
.button.quiet{background:transparent;border:1px solid var(--ink-soft);color:var(--ink)}
.button.quiet:hover{border-color:var(--ink);background:var(--ink);color:#fff}
.button[disabled],.button.dead,.button[disabled]:hover,.button.dead:hover{background:var(--wash);border-color:var(--line);color:var(--ink-soft);cursor:not-allowed}
main p a:hover,main li a:hover,.site-footer a:hover{text-decoration-thickness:2px}
::selection{background:var(--ink);color:#fff}

/* Home: the Opening on the grid (the third photograph case). The photograph starts on the line of column 5 and runs off
   the right edge; the words stand on white in columns 1–4. Proportions after the guide's hero at 1440 × 720: under the
   128 px header the photograph is 928 × 512 (29:16) with 80 px of white below it; the words start 160 px below the header.
   The stripes and triangles are drawn in step 3; here only the geometry. */
.opening{overflow-x:hidden;padding-bottom:96px;padding-top:0}
.opening .cols{row-gap:24px}
.opening-words{padding-top:160px}
.opening-words h1{max-width:none}
.opening-img{aspect-ratio:29/16;max-height:80vh;border-radius:0}
.opening-img span{position:absolute;top:16px;left:auto;right:16px;max-width:60%}
.opening-frame{position:relative}
.cut{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.cut-narrow{display:none}
#intro{padding-top:var(--section-tight)}
/* The Opening across the window (the plan of 11 November 2026, step 1). The photograph is as wide as the window and as high
   as leaves the headline in the first screen; the headline at the display size stands on white beneath it (or above it). */
.opening.across,.opening.words{padding-bottom:0;overflow:visible}
.opening.across .opening-img,.opening.words .opening-img{aspect-ratio:21/9;max-height:max(352px,calc(100vh - var(--header-h) - 280px))}
.opening.across .opening-words{padding-top:32px}
.opening.words .opening-words{padding-top:64px;padding-bottom:48px}
.opening.across h1,.opening.words h1,.opening.across .h1,.opening.words .h1{font-size:var(--fs-display);line-height:1;letter-spacing:-.03em;margin:0;max-width:none}
.from-top{transform:scaleY(-1)}
.imgs.grid-pair{grid-template-columns:repeat(2,minmax(0,1fr))}
.intro{padding-top:48px}
.intro-num{padding-top:8px}
.numbers{display:flex;flex-wrap:wrap;gap:16px 48px;margin:8px 0}
.num b{display:block;font-size:var(--fs-title);font-weight:300;line-height:1;font-variant-numeric:tabular-nums}
.num span{font-size:var(--fs-text);color:var(--ink-soft)}   /* what the number counts, at the text size (the plan of 11 November 2026, step 3: less small print) */
.numbers.by-kind{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px 32px;border-top:1px solid var(--ink);padding-top:16px;margin-top:16px}
.small-num b{font-size:var(--fs-head)}
.theme-row{display:grid;grid-template-columns:repeat(var(--theme-cols,5),minmax(0,1fr));gap:32px;margin-top:32px}
.order{font-size:var(--fs-small);color:var(--ink-soft);font-variant-numeric:tabular-nums;margin-top:12px}
.theme-row .order{font-size:var(--fs-display);font-weight:300;line-height:1;color:var(--ink);margin:0 0 12px}   /* the themes numbered in Light, as the chapters of the 2019 plan */
.count{font-size:var(--fs-small);font-weight:400;margin-top:auto}
.logos{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px;margin:8px 0 32px}
.logos.supporters{grid-template-columns:repeat(8,minmax(0,1fr));margin:12px 0 8px}
.supporters .logo{text-align:center;padding:8px;line-height:1.3}
.supporters .logo.has-img{border:0;aspect-ratio:auto;height:64px;padding:0}
.supporters .logo img{display:block;max-width:100%;height:auto;filter:grayscale(1) brightness(.6) contrast(1.6)}
@media (max-width:1359px){.logos.supporters{grid-template-columns:repeat(4,minmax(0,1fr));row-gap:24px}}
.supporters-title{margin:0}
.logo{aspect-ratio:5/2;border:1px dashed #c9c6bf;border-radius:0;display:flex;align-items:center;justify-content:center;font-size:var(--fs-small);color:#8a877f}


/* Theme and collection pages */
.wide{max-height:62vh}
.action{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px 32px}
.action .doors{margin:0}
.facts-box{border-top:1px solid var(--line);padding:16px 0 0;margin-top:24px}
/* Artist pages (Artist pages – template): works are shown whole at their own proportion, never cropped or filtered. */
.work{display:block;width:100%;height:auto;background:#f4f4f4}
.work-lead{margin:0}
.lead-tall{grid-column:6/-1}.lead-square{grid-column:5/-1}.lead-wide{grid-column:4/-1}
.works.works-wide{grid-template-columns:repeat(3,minmax(0,1fr))}
.work-lead img{width:auto;max-width:100%;max-height:86vh}
.work-lead .credit{margin-top:12px}
.works{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gutter);align-items:start;margin:24px 0 4px}
.works figure{margin:0}
.works figcaption{font-size:var(--fs-small);line-height:1.45;color:var(--ink-soft);margin-top:8px}
.works figcaption .caption{display:block;color:var(--ink)}
.artist-text p{margin-top:0}
.c8-12{grid-column:8/-1}
.card-work{aspect-ratio:4/5;object-fit:cover;object-position:50% 50%;background:#fff;margin-bottom:0}
.item h3 a{color:inherit;display:inline-block;line-height:1.2;padding:12px 0;margin:-12px 0;text-decoration:underline;text-decoration-color:var(--line);text-underline-offset:4px}
.item h3 a:hover{text-decoration-color:var(--ink)}
.network-lead{margin:0 0 24px;max-width:34em}
.film-list{margin-top:24px}.film-list .film-meta{display:block;font-size:var(--fs-small);color:var(--ink-soft);margin:2px 0 4px}
.network-rows{list-style:none;padding:0;margin:8px 0 0;columns:2;column-gap:var(--gutter)}
.network-rows li{break-inside:avoid;padding:12px 0;border-top:1px solid var(--line)}
.network-rows strong{display:block;font-weight:700}
.network-rows strong a{color:inherit;text-decoration:none;border-bottom:1px solid var(--line)}
.network-rows span{font-size:var(--fs-text);color:var(--ink-soft)}
.facts{display:grid;grid-template-columns:auto 1fr;gap:8px 24px;font-size:var(--fs-text);margin:0 0 16px}
.facts dt{color:var(--ink-soft)}
.facts dd{margin:0}
.place h3{margin-top:12px}
.chips{display:flex;flex-wrap:wrap;gap:12px;align-content:start}
.chip{display:inline-flex;align-items:center;min-height:48px;border:1px solid var(--ink-soft);border-radius:0;padding:0 16px;text-decoration:none}
span.chip{border:0;padding:0 16px 0 0;min-height:0}   /* not a link, so not a control: plain text */
.chip:hover{border-color:var(--ink)}
.chip.ghost{display:inline-block;width:120px;height:38px;padding:0;background:var(--bar);border-color:transparent}
.thanks{max-width:560px}
.person .img{margin-bottom:12px;max-width:260px}
.narrow{max-width:62ch}
.principles{list-style:none;padding:0;margin:8px 0 24px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gutter)}
.principles li{border-top:2px solid var(--ink);padding-top:12px}
.principles strong{display:block;font-weight:700;font-size:var(--fs-text);line-height:1.15;margin-bottom:8px}
.principles .lines{margin:8px 0 0}

/* Partners */
.steps{list-style:none;padding:0;margin:24px 0 16px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--gutter)}
.steps li{border-top:2px solid var(--ink);padding-top:16px}
.steps h3{margin:8px 0 4px}
.steps p{font-size:var(--fs-text);color:var(--ink-soft);margin:0}
.step-n{display:block;font-size:var(--fs-title);font-weight:300;line-height:1;color:var(--ink);font-variant-numeric:tabular-nums}   /* numbers in Light, as the themes on Home */
.rules{padding-left:24px;columns:2 320px;column-gap:64px;margin:8px 0 24px}
.rules li{margin:0 0 16px;break-inside:avoid}
.contact-box{border-top:1px solid var(--line);padding:16px 0 0;margin-top:48px}

/* Partner portal */
.door-panels{display:grid;grid-template-columns:1fr 1fr;gap:var(--gutter);margin-top:32px}
/* The doors: two lines of type under a rule, the largest thing on their page; no box (rule 6). The door into the archive
   stands on the yellow. */
.panel{display:flex;flex-direction:column;gap:8px;border-top:2px solid var(--ink);padding:24px 0 0;text-decoration:none}
.panel strong{font-size:var(--fs-head);font-weight:700;line-height:1.15;letter-spacing:-.01em;text-wrap:balance}   /* one step under the page's name (Thomas, 11 November 2026) */
.panel span:last-child{color:var(--ink-soft)}
.panel.archive{background:var(--accent);border-top-color:var(--accent);padding:24px}
.panel.archive .kicker,.panel.archive span:last-child{color:var(--ink)}
.panel:hover strong{text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:4px}
.mini-form{display:flex;flex-direction:column;gap:4px}
.f-label{font-size:var(--fs-small);color:var(--ink-soft);margin-top:8px}
.field{display:block;height:38px;border:1px solid #d6d3cc;border-radius:0;background:#fff}
.field.tall{height:76px}
.mini-form .button,.card .button{align-self:flex-start;margin-top:16px}
.call-card{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 32px}
.call-card .button{margin-top:0;align-self:center}
.logo-tile{background:var(--ground);aspect-ratio:3/2;display:flex;align-items:center;justify-content:center;border-radius:0;margin-bottom:12px}
.logo-tile img{width:62%}

/* Form */
.form{display:grid;gap:8px;max-width:560px;margin:8px 0 16px}
.form label,.mini-form label{color:var(--ink-soft);margin-top:12px}
main input,main select,main textarea{font:inherit;width:100%;min-height:48px;padding:8px 12px;border:1px solid var(--ink-soft);border-radius:0;background:#fff;color:var(--ink);appearance:none;-webkit-appearance:none}
main textarea{min-height:96px;resize:vertical}
main input:focus-visible,main select:focus-visible,main textarea:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
main input:disabled,main select:disabled,main textarea:disabled{background:#fff;opacity:1}
main select{padding-right:48px;background-image:linear-gradient(45deg,transparent 50%,var(--ink) 50%),linear-gradient(135deg,var(--ink) 50%,transparent 50%);background-position:calc(100% - 22px) 50%,calc(100% - 16px) 50%;background-size:6px 6px,6px 6px;background-repeat:no-repeat}
main input[type=checkbox]{flex:none;width:24px;min-height:24px;height:24px;padding:0;margin:0;cursor:pointer}
main input[type=checkbox]:checked{background:var(--ink);box-shadow:inset 0 0 0 4px #fff}
.form .check{display:flex;gap:12px;align-items:flex-start;min-height:48px;font-size:var(--fs-text);font-weight:400;color:var(--ink-soft)}
.form .button{justify-self:start;margin-top:16px}
.next-steps{padding-left:24px;margin:8px 0 16px}
.next-steps li{margin:8px 0}

/* Development: the type page */
.type-row{border-top:1px solid var(--line);padding:24px 0 16px}
.type-sample{line-height:1.1;margin:0 0 8px}
.type-label{margin-top:var(--section);margin-bottom:0}
.type-label + .mod{padding-top:16px}
.opening-words .h1{font-weight:700;font-size:var(--fs-title);line-height:1.05;letter-spacing:-.02em;margin:0 0 16px;text-wrap:balance}
.type-label{max-width:none}

/* Development page */
.table-scroll{overflow-x:auto;margin-top:8px}
.dev-table{width:100%;border-collapse:collapse;font-size:var(--fs-small);min-width:640px}
.dev-table th,.dev-table td{text-align:left;padding:12px 12px 12px 0;border-bottom:1px solid var(--line);vertical-align:top}
.dev-table th{font-weight:400;color:var(--ink-soft);font-size:var(--fs-small)}
.dev-table tfoot td{font-weight:700;border-bottom:0}
.dev-table .n{text-align:right;font-variant-numeric:tabular-nums}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:var(--fs-small);overflow-wrap:anywhere}
.stepper{display:inline-flex;gap:3px;flex-wrap:wrap}
.stepper span{font-size:var(--fs-small);padding:2px 8px;border-radius:0;background:var(--wash);color:#9a978f}
.stepper span.done{background:#e3e1dc;color:var(--ink)}
.stepper span.on{background:var(--ink);color:#fff}
.dev-list{list-style:none;padding:0;margin:8px 0 0;max-width:900px}
.dev-list li{display:grid;grid-template-columns:minmax(0,260px) 1fr;gap:4px 24px;padding:12px 0;border-top:1px solid var(--line)}
.dev-list li > span:last-child{color:var(--ink-soft)}
.dev-list .where{font-size:var(--fs-small);color:#8a877f}
.dev-list li:has(.tag){grid-template-columns:64px minmax(0,300px) 1fr}
.dev-list li:has(.where){grid-template-columns:minmax(0,300px) 140px 1fr}
.tag{display:inline-block;font-size:var(--fs-small);letter-spacing:.04em;padding:2px 8px;border-radius:0;height:fit-content;width:fit-content}
.tag.done{background:#e3e1dc}.tag.next{background:var(--wire-note)}.tag.later,.tag.open{border:1px solid #c9c6bf;color:var(--ink-soft)}

/* Footer */
/* The close (open, quiet, close): black, the pattern at full strength in white, the logo once in white. The archive's
   footer follows when its look is set on PhotoDeck (step 5). */
.site-footer{background:var(--ground);color:var(--text-on-dark);overflow:hidden}
.close{position:relative;display:flex;align-items:flex-end;min-height:320px}
.close-words{position:relative;z-index:1;padding:64px 0 48px;max-width:calc(50% - var(--gutter))}
.close-logo{display:block;width:var(--logo-w);height:auto;margin:0 0 32px}
.close-pattern{position:absolute;right:0;bottom:0;width:50%;height:100%;pointer-events:none}
.site-footer p{margin:0 0 8px;max-width:none}
.site-footer a{color:#fff;display:inline-block;padding:12px 0}
.about-line{color:#fff}

/* The grid overlay: switched on with the Grid button in the wireframe strip, ?grid in the address or the key G.
   Columns in blue, margins in red; the readout gives the values at the current width. Not built at launch. */
.grid-overlay{display:none;position:fixed;inset:0;pointer-events:none;z-index:999}
body.show-grid .grid-overlay{display:block}
.grid-overlay .wrap{height:100%;position:relative;background:
  linear-gradient(to right,rgba(220,60,60,.10) 0 var(--margin),transparent var(--margin) calc(100% - var(--margin)),rgba(220,60,60,.10) calc(100% - var(--margin)))}
.grid-overlay .cols{height:100%}
.grid-overlay .col{background:rgba(40,110,220,.10);border-left:1px solid rgba(40,110,220,.45);border-right:1px solid rgba(40,110,220,.45);font-size:var(--fs-small);color:rgba(40,110,220,.9);padding:4px 0 0 4px;font-variant-numeric:tabular-nums}
.grid-overlay .col.col-5{background:rgba(40,110,220,.16)}  /* the Opening starts here on desktop */
.grid-read{position:absolute;left:0;right:0;bottom:16px;width:fit-content;background:rgba(21,21,21,.9);color:#fff;font-size:var(--fs-small);line-height:1.4;padding:6px 10px;border-radius:0;font-variant-numeric:tabular-nums}
.grid-toggle{font:inherit;font-size:var(--fs-small);background:transparent;border:1px solid rgba(21,21,21,.4);border-radius:0;padding:3px 10px;cursor:pointer;white-space:nowrap;color:var(--ink)}
.grid-toggle[aria-pressed="true"],.notes-toggle[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}

@media print{.wire-strip,.grid-overlay,.menu,.menu-toggle,.skip,.site-footer .links{display:none!important}
  .mod{break-inside:avoid}.button{border:1px solid #000;background:none;color:#000}a{text-decoration:none}}

/* Tablet (768–1,023 px): 8 columns, 24 px gutters, 32 px margins; the menu folds, like the archive's below tablet width */
@media (max-width:1023px){
  .logos.supporters{grid-template-columns:repeat(4,minmax(0,1fr))}
  :root{--fs-title:32px;--fs-display:44px;--cols:8;--gutter:24px;--margin:32px;--section:80px;--section-head:56px;--section-tight:28px}
  .cards-6{grid-template-columns:repeat(3,minmax(0,1fr))}
  .principles.five{grid-template-columns:repeat(2,minmax(0,1fr))}
  .menu-toggle{display:flex}
  .menu{display:none;position:absolute;left:0;right:0;top:var(--header-h);background:var(--paper);flex-direction:column;align-items:flex-start;gap:0;padding:8px var(--margin) 24px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);z-index:10}
  .menu.open{display:flex}
  .menu a{padding:12px 0;font-size:var(--fs-text);width:100%}
  .divider{width:100%;height:1px;margin:8px 0}
  .site-header{position:relative}
  .lead-tall{grid-column:4/-1}.lead-square{grid-column:3/-1}.lead-wide{grid-column:2/-1}.works.works-wide{grid-template-columns:repeat(2,minmax(0,1fr))}
  .theme-entry.row h3{font-size:var(--fs-text)}   /* below desktop a theme's name stands at the text size, in Bold (rule 11: one size carries the page) */
  .c1-9,.c5-12,.c-wide,.c-side,.e-words{grid-column:1/-1}
  .e-words{margin-bottom:24px}
  .c-wide.photo-half{order:-1}  /* the photograph first below desktop, whichever side it sits on */
  .c-side{margin-top:24px}
  .opening.across .opening-img,.opening.words .opening-img{aspect-ratio:16/9;max-height:none}
  .opening.across .opening-words{padding-top:24px}
  .opening.words .opening-words{padding-top:32px;padding-bottom:32px;order:0}
  .c1-4{grid-column:1/4}.c6-12,.c-offset{grid-column:4/-1}.c1-8{grid-column:1/7}.c1-6{grid-column:1/5}.c7-12,.c8-12{grid-column:5/-1}.c-half{grid-column:span 4}
  .grid-4,.grid-mixed{grid-template-columns:repeat(2,minmax(0,1fr))}
  .grid-overlay .col.col-5{background:rgba(40,110,220,.10)}.grid-overlay .col.col-2{background:rgba(40,110,220,.16)}
  .wire-strip .wrap{flex-wrap:wrap}
  .theme-row{grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:minmax(220px,40%);overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:8px;gap:24px}
  .cards-4,.cards-5,.principles,.contents{grid-template-columns:repeat(2,minmax(0,1fr))}
  /* the Opening below desktop: the photograph first, from the line of column 2 off the right edge; the words under it */
  .opening{padding-bottom:0}
  .opening-words{grid-column:1/-1;order:2;padding-top:0}
  .opening .cols{row-gap:16px}
  .opening-words h1{max-width:24ch}
  .cut-wide{display:none}.cut-narrow{display:block}
  .c5-off{grid-column:2/-1;order:1}
  .opening-img{aspect-ratio:3/2}
}
/* Phone (below 768 px): the guide's 4 columns, 16 px gutters and 16 px margins; one column, the title first */
@media (max-width:767px){
  .logos.supporters{grid-template-columns:repeat(2,minmax(0,1fr))}
  :root{--cols:4;--gutter:16px;--margin:16px;--header-h:64px;--logo-w:128px;--section:64px;--section-head:40px;--section-tight:24px}
  .channels{grid-template-columns:1fr;gap:16px}
  .cards-6{grid-template-columns:repeat(2,minmax(0,1fr))}
  .mod-items .cards-4{grid-template-columns:repeat(2,minmax(0,1fr));gap:24px 16px}
  .principles.five{grid-template-columns:1fr}
  .c1-4,.c6-12,.c1-8,.c1-6,.c7-12,.c8-12,.c-half,.c-offset{grid-column:1/-1}
  .works{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
  .lead-tall,.lead-square,.lead-wide{grid-column:1/-1}.works.works-wide{grid-template-columns:minmax(0,1fr)}
  .network-rows{columns:1}
  .work-lead img{max-height:none;width:100%}
  .collection-card{row-gap:16px}
  #intro .doors{margin-top:16px}
  .opening-words h1{margin-bottom:8px}
  .close{flex-direction:column;align-items:stretch;min-height:0}
  .close-pattern{position:static;order:-1;width:100%;height:160px}
  .close-words{max-width:none;padding:32px 0}
  .opening.across .opening-img,.opening.words .opening-img{aspect-ratio:16/9}  /* 16:9 on phones, so the way on stands in the first screen (rule 23) */
  #intro{padding-top:16px}
  /* on a phone the ways on stand directly under the first sentence, in the first screen; the second paragraph follows them */
  #intro .c1-8{display:flex;flex-direction:column}
  #intro .lead{margin-bottom:16px}
  #intro .doors{order:1;margin:0 0 24px}
  #intro .c1-8 > p:not(.lead):not(.doors):not(.meta-row){order:2}
  #intro .meta-row{order:3}
  .opening.across h1,.opening.words h1,.opening.across .h1,.opening.words .h1{font-size:var(--fs-title);line-height:1.05;letter-spacing:-.02em}
  .opening.across .opening-words{padding-top:16px}
  .mod-photo.lead-bleed .bleed-img{aspect-ratio:3/2!important}
  .imgs.row-3{grid-template-columns:repeat(3,minmax(0,1fr))}  /* the row of three stays one row under its large photograph */
  .lead-photo .img{aspect-ratio:3/2!important}  /* the lead photograph has its own crop on a phone (rule 24) */
  .photo-half{order:-1}  /* photograph and text: the photograph first on phones, whichever side it sits on desktop */
  .grid-3,.grid-4,.grid-mixed{grid-template-columns:repeat(2,minmax(0,1fr))}
  .mod .cols + .cols{margin-top:16px}
  .theme-entry.row{grid-template-columns:44px 1fr;gap:12px 16px}
  .theme-entry.row .frame{grid-column:1 / -1}
  .numbers{gap:16px 32px}
  .numbers.by-kind{grid-template-columns:repeat(2,minmax(0,1fr))}
  .opening-img{aspect-ratio:3/2}  /* 3:2 on phones so the core line sits in the first screen (4:5 pushed it below) */
  .grid-2,.split,.door-panels,.steps,.theme-nav,.cards-2,.cards-3{grid-template-columns:1fr}
  .grid-2{gap:32px}
  .split{gap:24px}
  .contact-box{margin-top:0}
  .contact-box .h-big,.mod-doors .h-big{font-size:var(--fs-text)}
  /* running text on a phone: 35 to 45 characters a line (rule 10); the column is a little narrower than the images */
  main p:not(.doors):not(.credit):not(.meta-row):not(.kicker):not(.lead):not(.statement),main dd,main blockquote,main .film-list li > span,main .network-rows span{max-width:19em}   /* an address stays on one line on a phone */
  .theme-nav + .theme-nav{margin-top:32px}
  .dev-list li,.dev-list li:has(.tag),.dev-list li:has(.where){grid-template-columns:1fr}
  .strip-tools{gap:10px}
  .theme-row{grid-auto-columns:78%}
}
@media (max-width:480px){
  .cards-4,.cards-5,.principles,.contents{grid-template-columns:1fr}
  .wire-strip .wrap{align-items:flex-start}
  .strip-tools{flex-wrap:wrap;row-gap:4px}
}
"""


def share_image():
    """Default share image for link previews (1200 x 627): the logo on black, until real images are chosen."""
    out = ROOT / "assets" / "share-default.png"
    try:
        from PIL import Image
    except ImportError:
        return out
    logo = Image.open(ROOT / "assets" / "logo.png").convert("RGBA")
    canvas = Image.new("RGB", (1200, 627), (21, 21, 21))
    w = 640
    h = round(logo.height * w / logo.width)
    logo = logo.resize((w, h))
    canvas.paste(logo, ((1200 - w) // 2, (627 - h) // 2), logo)
    canvas.save(out, optimize=True)
    return out


def strip_html(base):
    if LAUNCH:
        return ""
    return (f'<div class="wire-strip"><div class="wrap"><span>Live wireframe · grey boxes are images to choose · '
            f'grey bars are text to write · yellow notes say what goes there</span><span class="strip-tools">'
            f'<a class="partner-switch" href="?partner=off" title="This browser remembers you came from the archive, so the menu shows its tools. Click to see the public menu.">Public menu</a>'
            f'<a href="{base}dev/">Development</a><a href="{base}dev/modules/">Modules</a><a href="{base}dev/type/">Type</a><a href="{base}dev/opening/">Opening</a><a href="{base}dev/images/">Images</a>'
            f'<button class="grid-toggle" type="button" aria-pressed="false" title="Show the grid (or press G)">Grid</button>'
            f'<button class="notes-toggle" type="button" aria-pressed="false">Clean view</button></span></div></div>\n'
            f'<div class="grid-overlay" aria-hidden="true"><div class="wrap"><div class="cols"></div><div class="grid-read"></div></div></div>\n')


def render(p, main, base):
    cur = lambda s: ' aria-current="page"' if p["nav"] == s else ""
    doc_title = p.get("doc_title") or ("Africa Reframed" if p["slug"] == "home" else f'{p["title"]} · Africa Reframed')
    return LAYOUT.format(
        doc_title=e(doc_title), og_title=e(p["title"] if p["slug"] != "home" else "Africa Reframed"),
        desc=e(p["desc"]), url=SITE_URL + p["path"], share=SITE_URL + p.get("share", "assets/share-default.png"),
        robots="" if LAUNCH else '<meta name="robots" content="noindex">\n', strip=strip_html(base),
        base=base, stamp=STAMP, slug=p["slug"], tpl=p["tpl"], main=main, about_line=e(ABOUT_LINE), close_pattern=CLOSE_PATTERN, archive=ARCHIVE, partner_script=PARTNER_SCRIPT,
        archive_browse=archive("/-/galleries/archive", "menu"), archive_lightbox=archive("/lightbox", "menu"),
        cur_themes=cur("themes"), cur_collections=cur("collections"), cur_partners=cur("partners"), cur_about=cur("about"), cur_portal=cur("portal"))


def build():
    (ROOT / "assets").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "site.css").write_text(CSS)
    share_image()
    rows, links = [], {}
    SLOTS.clear()
    (ROOT / "assets" / "logo-white.svg").write_text((ROOT / "assets" / "logo-black.svg").read_text().replace('fill="#000000"', 'fill="#ffffff"').replace(", black</title>", ", white</title>"))
    for p in PAGES:
        depth = p["path"].count("/")
        base = "../" * depth if depth else "./"
        CUR.update(slug=p["slug"], title=p["title"], n=0)
        main = TEMPLATES[p["tpl"]](p, base)
        CUR["slug"] = None
        rows.append(dict(p, stats=page_stats(main)))
        for url, label in LINK_RE.findall(main):
            strong = re.search(r"<strong>(.*?)</strong>", label, re.S)
            label = re.sub(r"<[^>]+>", " ", strong.group(1) if strong else label)
            label = re.sub(r"\s+", " ", html.unescape(label)).strip()
            entry = links.setdefault(html.unescape(url), [label, []])
            if p["title"] not in entry[1]:
                entry[1].append(p["title"])
        out = ROOT / p["path"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(p, main, base))
    dev_dir = ROOT / "dev"
    if LAUNCH:
        shutil.rmtree(dev_dir, ignore_errors=True)
    else:
        dev = dict(path="dev/", title="Development", slug="dev", tpl="dev", nav=None,
                   desc="Development notes for the Africa Reframed site: generated by the build, removed at launch.")
        dev_dir.mkdir(exist_ok=True)
        over = "".join(f'<li><span>{e(kind)}: {n} words, limit {mx}</span><span>{e(text)}…</span></li>' for (kind, text), (mx, n) in sorted(OVER.items()))
        limits = sec(head("Text over its limit", "Every module checks its words against the limit in Website – modules (Quality rules, rule 4). "
                          "A text listed here is too long and fails the gate, src/check.py.")
                     + (f'<ul class="dev-list">{over}</ul>' if over else "<p>None: every text is within its limit.</p>"))
        (dev_dir / "index.html").write_text(render(dev, tpl_dev(rows, links, "../") + limits, "../"))
        modules = dict(path="dev/modules/", title="Modules", slug="modules", tpl="modules", nav=None,
                       desc="Every module of the Africa Reframed site with its variants, on the grid; generated by the build, removed at launch.")
        (dev_dir / "modules").mkdir(exist_ok=True)
        (dev_dir / "modules" / "index.html").write_text(render(modules, tpl_modules("../../"), "../../"))
        ims = dict(path="dev/images/", title="Images", slug="images", tpl="images", nav=None,
                   desc="Every image position on the Africa Reframed site, with its proportion and the size its file needs; generated by the build, removed at launch.")
        (dev_dir / "images").mkdir(exist_ok=True)
        (dev_dir / "images" / "index.html").write_text(render(ims, tpl_images("../../"), "../../"))
        typ = dict(path="dev/type/", title="Type", slug="type", tpl="type", nav=None,
                   desc="The type scale of the Africa Reframed site and the Home headline at two sizes; generated by the build, removed at launch.")
        (dev_dir / "type").mkdir(exist_ok=True)
        (dev_dir / "type" / "index.html").write_text(render(typ, tpl_type("../../"), "../../"))
        opn = dict(path="dev/opening/", title="The Opening", slug="opening", tpl="opening", nav=None,
                   desc="Three versions of the Opening of the Africa Reframed site, side by side; generated by the build, removed at launch.")
        (dev_dir / "opening").mkdir(exist_ok=True)
        (dev_dir / "opening" / "index.html").write_text(render(opn, tpl_opening("../../"), "../../"))

    # The page for a wrong address (Quality rules, rule 25). Its links are absolute, since it answers at any depth.
    root_path = urlparse(SITE_URL).path
    nf = dict(path="404.html", title="Page not found", slug="not-found", tpl="text", nav=None,
              desc="This page is not on africareframed.com.")
    nf_main = (m_page_head("This page is not here", NOT_FOUND_LINE, statement_draft=True)
               + m_doors("c", links=[button(root_path, "The front page", quiet=True), button(root_path + "themes/", "The five themes", quiet=True),
                                     button(root_path + "collections/", "The collections", quiet=True)], tight=True))
    nf_html = render(nf, nf_main, root_path)
    nf_html = re.sub(r'<link rel="canonical"[^>]*>\n', '', nf_html)
    if 'name="robots"' not in nf_html:
        nf_html = nf_html.replace('<meta property="og:type"', '<meta name="robots" content="noindex">\n<meta property="og:type"', 1)
    (ROOT / "404.html").write_text(nf_html)
    (ROOT / ".nojekyll").write_text("")
    print("built", len(PAGES), "pages" + ("" if LAUNCH else " and /dev/"), "into", ROOT)


if __name__ == "__main__":
    build()
