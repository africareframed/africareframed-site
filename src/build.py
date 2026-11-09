#!/usr/bin/env python3
"""Generate the Africa Reframed main site as a live wireframe (version 4, 6 November 2026: arranged by the page priorities).

Structure from "Website – Site map and user flows" (05 Website on the Drive): 16 pages from 9 templates.
Header: Themes · Collections · Partners · About | Log in (Log in opens the Partner portal; About moved up from the footer, Thomas, 9 November 2026); the archive adds its own
tools on its side. Footer: the about line, then About · Press · Contact · Privacy · Request access · Terms.

Wireframe conventions: grey boxes with a cross are images still to choose, at the size and proportion they will
have; grey bars are text still to write; yellow notes say what goes there. Real words appear only where they
already exist in the master documents (each carries its source in a comment). "Clean view" in the strip under
the header hides the notes.
Run: python3 src/build.py  (writes the pages and assets/ into the repository root)
"""
import html
import pathlib
import re
import shutil
import subprocess
import time
from urllib.parse import quote

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
NUMBERS = [("1,122", "images"), ("3", "countries"), ("5", "themes")]                        # Website brief, Home; AR Metadata, 2 Nov 2026
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
HOUSE_STATEMENT = ("Africa Reframed’s own collection: 1,122 images, AR‑1000 to AR‑2121, made in own productions in connection "
                   "with photography workshops with local partners in Mali, Kenya and The Gambia.")   # Keywording Guide, section 2
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
         statement="Phones, laptops and money on a screen, used for work, study and keeping in touch as a normal part of the day."),
    dict(slug="city-life", name="City life", count=237, query="urban life",
         statement="Cafés, campuses, rooftops and busy streets: the everyday rhythm of Bamako, Banjul and Nairobi."),
    dict(slug="creativity-and-culture", name="Creativity and culture", count=137, query="creativity and culture",
         statement="Portraits, style and street art."),
]
THEMES_LEAD = ("Read in order, the five themes are the archive’s argument: people learn, put their skills to work, "
               "live connected lives in modern cities, and make culture.")                            # Keywording Guide, 8b

# Who gets access: AR Archive – Status, "Who gets access, and sponsors" (Thomas, 3 Nov 2026)
ACCESS_WHO = ("The archive is free for selected non-profit and public partners: NGOs, media, educational institutions, "
              "embassies, ministries and development finance institutions.")
ACCESS_COMPANIES = ("Companies get access through a collection sponsorship: a sponsor gets the whole archive, "
                    "under the same partner licence as everyone else.")
PUBLIC_SAMPLE = "Public-sample rule: released images, no minors."


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
    return f'<a class="button{" quiet" if quiet else ""}" href="{href}">{e(label)}</a>'


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


def heading(title, level=2, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f"<h{level}{c}>{e(title)}</h{level}>"


# 2.2 Opening: the full Opening on Home. Words on white in columns 1–4; the photograph from the line of column 5 off the
# right edge (below 1,024 px from column 2, the words under it). Stripes and triangles come in step 3.
def m_opening(title, line=None, label="Opening photograph · released, no minors"):
    words = f"<h1>{e(title)}</h1>" + (draft(line, "p", "lead") if line else "")
    return mod("opening", "a, full", f'<div class="cols"><div class="opening-words c1-4">{words}</div>'
               f'<div class="c5-off">{img(label + " · from the line of column 5 off the right edge (2 below desktop)", None, cls="opening-img")}</div></div>',
               cls="opening")


# 2.3 Page head: kicker, title, statement, meta; variants (a) plain, (b) with two doors under it, (c) with the lead photograph.
def m_page_head(title, statement=None, kicker=None, meta=None, doors=None, lead=None, statement_draft=False):
    k = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
    m = ('<p class="meta-row">' + "".join(f"<span>{e(x)}</span>" for x in meta) + "</p>") if meta else ""
    s = (draft(statement, "p", "statement") if statement_draft else f'<p class="statement">{e(statement)}</p>') if statement else ""
    variant = "b, with doors" if doors else "c, with the lead photograph" if lead else "a"
    inner = f'<div class="cols"><div class="c1-4">{k}<h1>{e(title)}</h1></div><div class="c6-12 head-right">{s}{m}</div></div>'
    if doors:
        inner += doors
    if lead:
        inner += f'<div class="lead-photo">{lead}</div>'
    return mod("page-head", variant, inner, cls="page-head")


# 2.4 Text section: title left, text right; (b) with a facts box, (c) with a contact, (d) the intro on Home.
def m_text(title, paras, variant="a", box=None, contact=None, links=None, is_draft=True, sid=None, level=2, meta=None):
    body = "".join(draft(p) if is_draft else f"<p>{e(p)}</p>" for p in paras if p)
    if meta:
        body += '<p class="meta-row">' + "".join(f"<span>{e(x)}</span>" for x in meta) + "</p>"
    if links:
        body += f'<p class="doors">{"".join(links)}</p>'
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


def credit_line(caption=None, credit=None):
    c = f'<span class="caption">{e(caption)}</span> ' if caption else ""
    return f'<p class="credit">{c}<span>{e(credit or CREDIT)}</span></p>'


def m_photo(label, ratio="3/2", variant="b", caption=None, text=None, side="left", span="c1-12", credit=None, sid=None):
    if variant == "a":
        inner = f'<div class="bleed">{img(label, ratio, cls="bleed-img")}</div><div class="wrap">{credit_line(caption, credit)}</div>'
        return mod("photo", "a, full bleed", inner, wrap=False)
    if variant == "c":
        photo = f'<div class="c-half">{img(label, ratio)}{credit_line(caption, credit)}</div>'
        words = f'<div class="c-half">{text}</div>'
        order = photo + words if side == "left" else words + photo
        return mod("photo", f"c, photograph and text, photograph {side}", f'<div class="cols">{order}</div>', sid=sid)
    return mod("photo", "b, on the columns", f'<div class="cols"><div class="{span}">{img(label, ratio)}{credit_line(caption, credit)}</div></div>')


# 2.6 Image grid: (a) three in a row, (b) four portraits, (c) a strip of three squares, (d) six to eight mixed.
def m_grid(variant="d", n=None, label="Image", line=None, link=None, title=None, credit=None, level=2):
    if variant == "a":
        cells = "".join(img(label, "3/2") for _ in range(n or 3)); cls = "grid-3"; name = "a, three in a row"
    elif variant == "b":
        cells = "".join(img(label, "4/5") for _ in range(n or 4)); cls = "grid-4"; name = "b, four portraits"
    elif variant == "c":
        cells = "".join(img(label, "1/1") for _ in range(3)); cls = "grid-strip"; name = "c, a strip of three"
    else:
        n = n or 6
        ratio, cls = ("3/2", "grid-3") if n <= 6 else ("4/5", "grid-4")
        cells = "".join(img(label, ratio) for _ in range(n)); name = f"d, {n} in rows of {3 if n <= 6 else 4}"
    top = heading(title, level, "project-title" if level == 3 else "") if title else ""
    top += f'<p class="small">{e(line)}</p>' if line else ""
    foot = (f'<p class="doors">{link}</p>' if link else "") + credit_line(None, credit)
    return mod("grid", name, f'{top}<div class="imgs {cls}">{cells}</div>{foot}')


# 2.7 Theme sequence: (a) five entries in a row (Home), (b) five rows (Themes index), (c) previous and next.
def theme_entry(t, base, i, row=False, ratio="4/5"):
    strip = f'<div class="imgs grid-strip">{"".join(img("Image", "1/1") for _ in range(3))}</div>' if row else img("Theme image", ratio)
    return (f'<a class="theme-entry{" row" if row else ""}" href="{base}themes/{t["slug"]}/">'
            f'<span class="order">{i}</span>{"" if row else strip}<div><h3>{e(t["name"])}</h3><p>{e(t["statement"])}</p>'
            f'<span class="count">{t["count"]} images</span></div>{strip if row else ""}</a>')


def m_themes(base, variant="a", current=None):
    if variant == "c":
        n = THEMES.index(current)
        prv, nxt = THEMES[n - 1], THEMES[(n + 1) % len(THEMES)]
        inner = (f'<div class="cols"><div class="c-half theme-nav"><span class="dir">← Previous theme</span>{theme_entry(prv, base, THEMES.index(prv) + 1, ratio="5/2")}</div>'
                 f'<div class="c-half theme-nav"><span class="dir">Next theme →</span>{theme_entry(nxt, base, THEMES.index(nxt) + 1, ratio="5/2")}</div></div>')
        return mod("themes", "c, previous and next", inner)
    lead = f'<p class="lead">{e(THEMES_LEAD)}</p>'
    if variant == "b":
        rows = "".join(theme_entry(t, base, i, row=True) for i, t in enumerate(THEMES, 1))
        return mod("themes", "b, five rows", f'<div class="theme-rows">{rows}</div>')
    cards = "".join(theme_entry(t, base, i) for i, t in enumerate(THEMES, 1))
    return mod("themes", "a, five in a row", f'<div class="cols"><div class="c1-4">{heading("Five themes")}</div><div class="c6-12">{lead}</div></div>'
               f'<div class="theme-row">{cards}</div>')


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
    words = state_label(x) + heading(x["title"], 3, "project-title")
    body = "".join(draft(t) for t in x["text"]) + (note(x["note"]) if x.get("note") else "")
    if x["layout"] == "bleed":
        out = m_photo(x["image"], "21/9", "a", caption=x["caption"], credit=x["credit"])
        out += mod("text", "a, the project", f'<div class="cols"><div class="c1-4">{words}</div><div class="c6-12">{body}{extra}</div></div>', tight=True)
        if x.get("second"):
            y = x["second"]
            out += m_photo(y["image"], "3/2", "b", span="c6-12", caption=y["caption"], credit=y["credit"])
        return out
    return m_photo(x["image"], "3/2", "c", text=words + body + extra, side="left", caption=x["caption"], credit=x["credit"])


def collection_entry(x, base):
    """A collection in the archive (the collection card, 2.8), as proof of the archive."""
    meta = "".join(f"<span>{e(m)}</span>" for m in x["meta"])
    return (f'<a class="collection-card cols" href="{base}{x["href"]}"><div class="c-half">{img(x["image"], "3/2")}{credit_line(None, x.get("credit"))}</div>'
            f'<div class="c-half">{state_label(x) if x.get("state") else ""}<p class="kicker">{e(x["kicker"])}</p><h3 class="h-big">{e(x["title"])}</h3>{draft(x["line"])}'
            f'<p class="meta-row">{meta}</p><span class="textlink">Open the collection</span></div></a>')


# 2.8 Collection card: (a) one card at the full width, (b) a list of cards. The cards come from COLLECTIONS.
def collection_card(c, base):
    return collection_entry(dict(c["card"], title=c["title"], href=f'collections/{c["slug"]}/'), base)


def m_collection(base, variant="a", title=True):
    top = f'<div class="cols"><div class="c1-4">{heading("Collections")}</div></div>' if title else ""
    n = note("A new sponsored collection appears here once it is signed, shown as in production with behind-the-scenes material; never as a plan.")
    cards = "".join(collection_card(c, base) for c in COLLECTIONS)
    return mod("collection", "b, a list of cards", f'{top}<div class="collection-list">{cards}</div>{n}')


# 2.9 Numbers and counts: (a) a row of three, (b) one count with its action (used inside Doors b), (c) by country.
def numbers_row(values=NUMBERS, asof="as of 2 November 2026"):
    items = "".join(f'<div class="num"><b>{n}</b><span>{e(t)}</span></div>' for n, t in values)
    return f'<div class="numbers">{items}</div><p class="credit">{e(asof)}</p>'


def m_numbers(values=NUMBERS, asof="as of 2 November 2026", variant="a", title=None, note_text=None, tight=False, sid=None):
    top = f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">{note(note_text) if note_text else ""}</div></div>' if title else ""
    if variant == "c":
        rows = "".join(f'<div class="num small-num"><b>{n}</b><span>{e(t)}</span></div>' for n, t in values)
        return mod("numbers", "c, counts in a row", f'{top}<div class="numbers by-kind">{rows}</div>', tight=tight, sid=sid)
    return mod("numbers", "a, a row", top + numbers_row(values, asof), tight=tight, sid=sid)


# 2.10 Partner strip: shown only once there are partners; here in grey so the layout exists.
def m_partners(n=6, title="In use by", tight=False):
    logos = '<div class="logos">' + '<span class="logo">Partner logo</span>' * n + "</div>"
    return mod("partners", "", f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">'
               + note("Partners and sponsors by name, with their consent, from the closed preview. Until there are any, this module is left out of the live page.")
               + f'</div></div>{logos}', tight=tight)


# 2.11 Use example: (a) one, side by side; (b) three in a row; (c) partner news.
def use_card(kind="use"):
    if kind == "news":
        return f'<div class="example">{img("News image", "3/2")}<p class="kicker">Date</p>{lines(2)}</div>'
    return (f'<div class="example">{img("The use: a page, a slide, a post or an exhibition wall", "3/2")}'
            f'<p class="credit">AR-ID · {CREDIT}</p><p class="small">Partner · publication · use · month, year</p>{lines(2)}</div>')


def m_use(variant="a", title="In use", tight=False):
    n = note("Images in use, reported back by partners with their consent. Shown once there are any; until then left out of the live page.")
    if variant == "a":
        inner = (f'<div class="cols"><div class="c1-4">{heading(title)}</div><div class="c6-12">{n}</div></div>'
                 f'<div class="cols"><div class="c-half">{img("The use: a page, a slide, a post or an exhibition wall", "3/2")}<p class="credit">AR-ID · {CREDIT}</p></div>'
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
    return (f'<a class="panel{" dark" if dark else ""}" href="{href}"><span class="kicker">{e(kicker)}</span>'
            f'<strong>{e(title)}</strong><span>{e(line)}</span></a>')


def m_doors(variant, *, doors=None, count=None, count2=None, main=None, quiet=None, line=None, address=None, kicker=None, links=None, sid=None, tight=False):
    if variant == "a":
        return mod("doors", "a, two doors", f'<div class="door-panels">{"".join(doors)}</div>', sid=sid, tight=tight)
    if variant == "b":
        c = f'<div class="num"><b>{count[0]}</b><span>{e(count[1])}</span></div>'
        if count2:
            c = f'<div class="numbers">{c}<div class="num"><b>{count2[0]}</b><span>{e(count2[1])}</span></div></div>'
        inner = f'<div class="action">{c}<p class="doors">{main}{quiet or ""}</p></div>' + (draft(line, "p", "small") if line else "")
        return mod("doors", "b, the action band", inner, cls="band", sid=sid, tight=tight)
    if variant == "d":
        inner = f'<div class="cols"><div class="c1-4">{heading(kicker)}</div><div class="c6-12"><p class="h-big"><a href="mailto:{address}">{address}</a></p>{draft(line, "p", "small") if line else ""}</div></div>'
        return mod("doors", "d, the contact band", inner, cls="band", sid=sid, tight=tight)
    return mod("doors", "c, the ways on", f'<div class="cols"><div class="c6-12 c-offset"><p class="doors">{"".join(links)}</p></div></div>', sid=sid, tight=tight)


# 2.13 Item list: (a) plain under rules, (b) numbered steps, (c) accordion, (d) with images, (e) chips.
def m_items(title, items, variant="a", lead=None, is_draft=True, sid=None, image_ratio="3/2", image_label="Image", tight=False, cols=3, level=2, cls=""):
    h = heading(title, level, "project-title" if level == 3 else "") if title else ""
    top = f'<div class="cols"><div class="c1-4">{h}</div><div class="c6-12">{lead or ""}</div></div>' if title else ""
    t = (lambda s: draft(s)) if is_draft else (lambda s: f"<p>{e(s)}</p>")
    if variant == "b":
        li = "".join(f'<li><span class="step-n">{i}</span><h3>{e(a)}</h3>{t(b)}</li>' for i, (a, b) in enumerate(items, 1))
        return mod("items", "b, numbered steps", f'{top}<ol class="steps">{li}</ol>', sid=sid, tight=tight)
    if variant == "c":
        li = "".join(f'<details class="acc"><summary>{e(a)}<span class="plus" aria-hidden="true"></span></summary>{t(b)}</details>' for a, b in items)
        return mod("items", "c, accordion", f'{top}<div class="cols"><div class="c6-12 c-offset">{li}</div></div>', sid=sid, tight=tight)
    if variant == "d":
        li = "".join(f'<div class="item">{img(x[2] if len(x) > 2 and x[2] else image_label, image_ratio)}<h3>{e(x[0])}</h3>{t(x[1]) if x[1] else ""}</div>' for x in items)
        return mod("items", "d, with images", f'{top}<div class="cards-{cols}">{li}</div>', sid=sid, tight=tight)
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
                 f'<div class="c6-12"><div class="logos"><span class="logo">Sponsor logo</span></div>{draft(sponsor["text"])}{note(sponsor["note"])}</div></div>')
        return mod("sponsor", "collection page", inner, tight=tight)
    if variant == "collection":
        inner = (f'<div class="cols"><div class="c1-4"><p class="kicker">Collection</p><h2>Africa Reframed / [Full collection name]</h2></div>'
                 f'<div class="c6-12"><div class="logos"><span class="logo">Sponsor logo</span></div>{lines(3)}<p class="small">The sponsor’s contact</p></div></div>'
                 + note("The sponsor’s statement (at most 80 words) and contact, after the work. Only once a collection is sponsored."))
        return mod("sponsor", "collection page", inner, tight=tight)
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
        inner = f'<div class="cols"><div class="c1-4">{heading(title, 3)}</div><div class="c6-12">{lead or ""}{dead_button(button_label, quiet=True)}</div></div>'
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
    "Africa Reframed is a partner archive of photographs of modern life in Mali, Kenya and The Gambia, made in our own productions with photographers in Bamako, Nairobi and Banjul.",
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
    "We make new collections with companies and foundations as sponsors. A sponsored collection is led by a theme close to the sponsor’s work, or one it wants to support, never by its own operations: it opens a theme the archive does not yet hold, or deepens one of the five.",
    "The sponsor is named on the collection’s page and credited on the theme page, and gets the whole archive for its own channels, for good, under the same partner licence as everyone else.",
]
ACCESS_STEPS = [  # Partners 2: how access works (AR Archive – Status, 3 and 6 November 2026)
    ("Request access", "Tell us who you are and how you will use the images. We reply within a working day."),
    ("Approved by name", "We approve each organisation by name; your account opens for the email address you give."),
    ("Collect, then download", "Gather images in the Lightbox and share them with colleagues. Each download is a free licence for the one use you state."),
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
PORTAL_LEAD = "The archive is for partners: NGOs, media, educational institutions, embassies, ministries and development finance institutions. Signed in already? Partner log in takes you straight to the images."
PORTAL_RULES = "One download is one licence, for the use you state. Credit every use, never change what an image shows, and tell us where the images appear."
REQUEST_NEXT = [("We read your request", "and reply within a working day."), ("You get a welcome email", "with your login; the account opens for the address you give."),
                ("You log in", "collect in the Lightbox and download for each use, free.")]
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
    slug="house-collection", title="House Collection", kicker="Collection", statement=HOUSE_STATEMENT, statement_draft=False,
    lead="Collection image", story_title="The story", story=HOUSE_STORY, facts=HOUSE_FACTS,
    grid_line="A spread across the five themes; released, no minors.",
    access=dict(count=("1,122", "images in the House Collection"), src="collection-house", line=f"Sponsoring a collection? Write to {EMAIL_PARTNERS}."),
    sections=["story", "grid", "places", "themes", "goals", "access", "uses"],
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
WTV_COMPANIES = [  # strongest first, and the first four show the four kinds
    dict(name="Gjenge Makers", kind="Waste to building materials", where="Nairobi, Kenya · Nzambi Matee, founder", photographer="Paul Mbugua",
         text="Makes paving blocks and tiles from recycled plastic and sand in Nairobi’s Industrial Area. Its founder, the materials engineer Nzambi Matee, was named a UN Environment Programme Young Champion of the Earth in 2020.",
         since="Since then: a gavel she made from recycled plastic was used at the UN Environment Assembly in 2022, and she joined the Explorers Club 50 in 2025."),
    dict(name="Yo-Waste", kind="Technology for waste", where="Kampala, Uganda · Martin Tumusiime, founder", photographer="Jjumba Martin",
         text="An app that lets homes and businesses in Kampala book their waste collection, connecting them with independent collectors. It started as a project at Makerere University.",
         since="Since then: runner-up for the Royal Academy of Engineering’s Africa Prize for Engineering Innovation, 2024."),
    dict(name="Gracela Ventures", kind="Waste to energy", where="Kampala, Uganda · Grace Nalugwa, founder", photographer="Jjumba Martin",
         text="Makes cooking briquettes from organic waste for households, schools and hotels, in place of charcoal and firewood.",
         since="Since then: Grace Nalugwa has been a Mandela Washington Fellow, 2022, and a One Young World scholar, 2024."),
    dict(name="Umuti", kind="Waste to packaging", where="Kigali, Rwanda · founded by four students of the African Leadership University", photographer="Muhire Rukundo Dieudonné",
         text="When we photographed it in 2021, Umuti made paper bags from the banana and plantain trunks left after the harvest."),
    dict(name="Zijani", kind="Waste to energy", where="Nairobi, Kenya · Bryan Lukano, founder", photographer="Paul Mbugua",
         text="When we photographed it in 2021, Zijani collected used cooking oil from hotels and restaurants, to be turned into biodiesel and other products."),
    dict(name="Green Charcoal Uganda", kind="Waste to energy", where="Tororo, Uganda · Geoffrey Okoth Yoga, founder", photographer="Jjumba Martin",
         text="When we photographed it in 2021, the company made cooking briquettes from farm waste such as rice and palm kernel husks, bought from smallholder farmers in eastern Uganda."),
    dict(name="Vuma Biofuels", kind="Waste to energy", where="Awendo, western Kenya · Aaron Pattillo and Ian Otula, founders", photographer="Paul Mbugua",
         text="When we photographed it in 2021, Vuma made briquettes and pellets from sugarcane waste, as fuel for industrial boilers, schools and homes."),
]
WTV_COLLECTION = dict(
    slug="waste-to-value", title=WTV, kicker="Sponsored collection", statement_draft=True,
    statement="Seven young companies in Kenya, Uganda and Rwanda turning waste into fuel, building materials, packaging and services, photographed by photographers from their own countries.",
    meta=["7 companies", "Kenya · Uganda · Rwanda", "3 photographers"],
    lead="Lead image: a founder at work, from the collection", lead_credit=WTV_CREDIT, credit=WTV_CREDIT,
    story_title="The theme",
    story=["Waste is a raw material. Across East Africa, young companies build businesses on it: cooking fuel from husks and sugarcane, paving from plastic, paper bags from banana trunks, and an app that gets the rubbish collected. This collection shows seven of them, the people who run them and the work they do, in their own places.",
           "The companies came through BESTSELLER FOUNDATION’s Waste to Value Challenge, launched with Intellecap in December 2019 across Kenya, Uganda, Tanzania and Rwanda. From more than 400 applications, six were chosen for an accelerator that ran from August 2020 to March 2021, with up to USD 100,000 each and support on markets, products, business planning and finance. Alongside it, the foundation invested in a seventh: Vuma Biofuels."],
    facts=[("Companies", "7, six of them from the accelerator"), ("Countries", "Kenya, Uganda, Rwanda"),
           ("Photographers", "Paul Mbugua, Jjumba Martin, Muhire Rukundo Dieudonné"), ("Photographed", "February 2020 to May 2021"),
           ("Programme", "Waste to Value, BESTSELLER FOUNDATION with Intellecap"), ("Access", "By request, for partners and the press")],
    companies=WTV_COMPANIES,
    companies_lead="Four turn waste into energy, one into building materials and one into packaging; one builds the technology to collect it.",
    grid_line="Founders, workers and products: in workshops, yards, markets and kitchens.",
    making=[("A brief with every founder", "A video call with each company first, then a brief and a shot list around what it needed to show: its product, its people and its place."),
            ("Photographers from each country", "Photographers from Nairobi, Kampala and Kigali, hired and briefed by us, with every shoot prepared together with the company’s team."),
            ("A gallery for everyone involved", "The foundation and each founder got a gallery of their own, to use across all their channels.")],
    photographers=[("Paul Mbugua", "Nairobi · Rubanipix. Photographed the programme’s kick-off bootcamp in February 2020, then Gjenge Makers, Zijani and Vuma Biofuels.", "Behind the scenes: Paul Mbugua at work"),
                   ("Jjumba Martin", "Kampala. Photographed Yo-Waste, Gracela Ventures and Green Charcoal Uganda.", "Behind the scenes: Jjumba Martin at work"),
                   ("Muhire Rukundo Dieudonné", "Kigali · CornWine Films. Photographed Umuti in Kigali and Musanze.", "Behind the scenes: Muhire Rukundo Dieudonné at work")],
    photographers_lead="Three photographers, one in each country, each credited by name.",
    bts="Every shoot came with images of the photographer at work, for the foundation’s and the founders’ social media. The first post, from Yo-Waste in Kampala in February 2021, named the photographer and invited other companies to take part.",
    went=[("The founders", "Each company used its gallery in its own channels. Green Charcoal Uganda entered ten of the photographs in the Sankalp virtual exhibition, the month of its shoot."),
          ("The foundation", "BESTSELLER FOUNDATION used them in its newsletter and on its new website."),
          ("The sector", "Intellecap took the full Yo-Waste set, and its white paper on the waste-to-value sector in East Africa, published in July 2021, carries our photographs of Zijani, Yo-Waste and Gjenge Makers."),
          ("What followed", "The foundation asked us back: to photograph more circular-economy entrepreneurs around Kigali, and to document a waste-to-art project in Nairobi and Cape Town.")],
    words=[("I have begun benefiting from the photoshoots already.", "Geoffrey Okoth Yoga, Green Charcoal Uganda, February 2021"),
           ("Paul and his assistant were very professional, organized, and had a great eye for what to shoot.", "Aaron Pattillo, Vuma Biofuels, May 2021")],
    sponsor=dict(name="BESTSELLER FOUNDATION",
                 text="BESTSELLER FOUNDATION invests in inclusive and circular businesses across Africa. The collection was made in a strategic partnership with Africa Reframed, which the foundation announced in November 2020.",
                 note="The foundation’s own statement, at most 80 words, and its logo, as the foundation approves them."),
    invite=dict(title="A collection on your theme",
                text=["This collection began with a theme close to the foundation’s own work: waste turned into value. A collection can start from any theme close to a funder’s work, or one it wants to support: a sector, a skill, a city, a change under way.",
                      "We find the people and places that show it, work with photographers from the countries concerned, and deliver the collection with its stories and its behind-the-scenes material: for the funder’s channels, for the people in it, and for the press. The funder’s name stands on the collection; the work stays independent."]),
    access=dict(count=("7", "companies in the collection"), request=True, line="Access to this collection is by request, for partners and the press."),
    sections=["story", "companies", "grid", "making", "photographers", "bts", "went", "words", "access", "sponsor", "invite"],   # ends on the invitation
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
ABOUT_ARCHIVE = [
    "We run an archive of photographs of contemporary Africa for the organisations that work with the continent: NGOs, media, educational institutions, embassies, development finance institutions and companies. It is free for the non-profit and public partners we approve; companies take part by sponsoring a collection.",
    "Partners browse the archive, gather images and share them with colleagues, and download what they need. Every download is a licence for one stated use, so we know where the images go. The archive grows by collections.",
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
ABOUT_EXHIBITIONS = [
    "We show African artists and our own photographs to European audiences: in halls and on screens, with programmes of film, talks and workshops around the work.",
    "An exhibition is curated from our network of artists, made with a venue and public funders, and can take a physical or a digital form. A collection can open as an exhibition.",
]
EXHIBITION_PROJECTS = [  # strongest first; a new exhibition is one more entry, shown first while in production or open
    dict(title="Africa Reframed at Øksnehallen", state="record", layout="bleed",
         image="Installation view, Africa Reframed at Øksnehallen", caption="Africa Reframed at Øksnehallen, Copenhagen, 2016", credit="Photo: DGI-byen",
         text=["In the summer of 2016 the exhibition filled the 5,000 square metres of Øksnehallen in Copenhagen with more than 300 works by artists and designers from across the continent: Omar Victor Diop, Namsa Leuba, Fabrice Monteiro, Dillon Marsh, Lien Botha and Tahir Carl Karmali, with furniture by Yinka Ilori and fashion by ChiChia. Shown alongside them: Bamako Nights, made by the students of CFP Bamako.",
               "It was produced with DGI-byen and supported by Danida and Augustinus Fonden. Ten display modules built in oriented strand board carried the works through the hall; two cinemas and a programme of talks and workshops ran alongside. The Danish Ministry of Foreign Affairs later put Namsa Leuba’s image from the show on the cover of its own evaluation. The exhibition gave Africa Reframed its name."],
         second=dict(image="Installation view: the display modules with framed works", caption="The display modules, built for the hall", credit="Photo: DGI-byen")),
    dict(title="The digital edition at PixlArt", state="record", layout="side",
         image="PixlArt: the exhibition on large screens", caption="PixlArt, Østervrå, North Jutland, 2018", credit="Photo: Africa Reframed",
         text=["The same exhibition in another form: a converted church in North Jutland fitted with large screens, with new work from a workshop with our team in Nairobi."]),
]
ABOUT_EXHIBITION_DOOR = "A collection can open as an exhibition"   # open: now, or once a sponsored collection exists (Thomas)
ABOUT_ARTISTS_LEAD = ("Our exhibitions are curated from a network of artists across the continent, which we have followed and published "
                      "for more than a decade, first through the African Photography Network. Their works are shown here by agreement, "
                      "with their galleries’ credits where they apply. They are not part of the archive and are not available to partners.")
ARTISTS_SHOWN = [  # (name, origin · series · one line, image label); shown at Øksnehallen; artists, never "photographers"
    ("Omar Victor Diop", "Senegal · Studio des Vanités, Diaspora · Portraits that place African history inside the present. Courtesy MAGNIN-A, Paris.", "Omar Victor Diop, Diaspora"),
    ("Namsa Leuba", "Switzerland and Guinea · Khoi San, Zulu Kids, The Kingdom of Mountains · Staged photographs on how cultures see one another; the exhibition’s poster.", "Namsa Leuba, Khoi San"),
    ("Fabrice Monteiro", "Belgium and Senegal · The Prophecy, A Gorean Summer · Staged images on the environment and on heritage, made in Senegal.", "Fabrice Monteiro, The Prophecy"),
    ("Dillon Marsh", "South Africa · For What It’s Worth, Assimilation · The mines of South Africa and what they yielded.", "Dillon Marsh, For What It’s Worth"),
    ("Lien Botha", "South Africa · Parrot Jungle · Photographs of return and memory.", "Lien Botha, Parrot Jungle"),
    ("Tahir Carl Karmali", "Kenya · Jua Kali · Composites built from found objects in Nairobi.", "Tahir Carl Karmali, Jua Kali"),
    ("Yinka Ilori", "Nigeria and the United Kingdom · Furniture rebuilt from discarded chairs, telling Nigerian parables.", "Yinka Ilori, furniture"),
    ("ChiChia", "Tanzania and the United Kingdom · Fashion by Christine Mhando.", "ChiChia, fashion"),
]
ARTISTS_NETWORK = [  # from the network, profiled in our journal; one line each, in our words
    ("Osborne Macharia", "Kenya · Staged commercial photography with a story in every frame."), ("Élise Fitte-Duval", "Martinique and Senegal · Contemporary dance, and the floods of Dakar."),
    ("Fatoumata Diabaté", "Mali · Sutigi: the night belongs to the young."), ("Isaac Kasamani", "Kenya and Uganda · Photojournalism of Uganda’s politics."),
    ("Antonia Steyn", "South Africa · Portraits of South African figures."), ("Ala Kheir", "Sudan · Landscapes and lives across the country."),
    ("Adeola Olagunju", "Nigeria · Performance photographs: Resurgence, a manifesto."), ("Jon Riordan", "South Africa · Landscapes shaped by memory."),
    ("Mpho Mokgadi", "South Africa · Everyday life, on film."), ("Charles Okereke", "Nigeria · Go-Slow: Lagos at a standstill."),
    ("Hélène Amouzou", "Togo and Belgium · Self-portraits on displacement."), ("Sydelle Willow Smith", "South Africa · Migration and identity."),
    ("Jac Kritzinger", "South Africa · The ordinary, made visible."), ("Mouna Karray", "Tunisia · Murmurer; Noir."),
]

# 3 Workshops: the activity, then the projects, the voices, Bamako Nights, the partners
ABOUT_WORKSHOPS = [
    "We connect African photographers with the international picture market. Our workshops are built with photography schools, photographers’ unions and press associations, with a funder and a market partner in the same programme, so that training leads to work that sells, and to income.",
    "Photographers learn what buyers look for, how to brief and shoot for it, and how their work is licensed.",
]
WORKSHOP_PROJECTS = [  # strongest first; a new workshop is one more entry, shown first while in production or open
    dict(title="CFP Bamako and Getty Images", state="record", layout="side",
         image="Photography students at CFP Bamako", caption="Photography students at CFP Bamako", credit="Photo: Africa Reframed",
         text=["Our first workshop programme ran for six years with the photography school CFP Bamako and Getty Images, funded through the Danish Embassy in Mali. Students photographed for the world market and licensed their work through Getty while still in training, with feedback from Getty’s creative team.",
               "Their images were licensed by EY, NBC, Cambridge University Press, McKinsey & Company, Pearson, Orange and Vodacom, among others. Project Everyone chose two of them, by Gaoussou and Abdoulaye Sogodogo, for the launch campaign of the UN Global Goals. An independent review for the Danish Centre for Culture and Development found that the programme “promotes positive images of Africa, moving away from editorial or ‘development’ photography”."],
         note="The review’s words are quoted from a report on the Drive: to be cleared by Thomas before launch."),
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

# 4 Who is behind it
ABOUT_WHO = [
    "Africa Reframed is an independent, non-commercial initiative established by Commerce & Culture, the Copenhagen studio founded in 2010 by Thomas Damgaard. Trained in design and art history, he advised the Danish Ministry of Foreign Affairs on culture and development from 2010 to 2014, and has produced photography and exhibitions with partners in Africa and Europe since.",
    "The visual identity is by the Danish designer Rune Høgsberg, first drawn for the exhibition at Øksnehallen. The archive’s photographs are made by our team.",
]
ABOUT_PEOPLE = [("Thomas Damgaard", "Founder.", "Portrait"), ("Rune Høgsberg", "The identity.", "Portrait or the mark"),
                ("CFP Bamako", "Partner school.", "The school"), ("The Nairobi team", "Photographers.", "The team")]


def by_state(items):
    """Projects in production or open first, then the rest in the order given (strongest first)."""
    order = list(STATES)
    return sorted(items, key=lambda x: order.index(x["state"]))

PRESS_FACTS = [("1,122 images", "in the House Collection, from Mali, Kenya and The Gambia"), ("Five themes", "Learning, Work and enterprise, Everyday digital, City life, Creativity and culture"),
               ("Free for partners", "selected non-profit and public partners; companies through a collection sponsorship"), ("Established by", "Commerce & Culture, Copenhagen"),
               ("Real images", "our images are never AI-generated")]
PRIVACY = [("What we collect", "Your organisation, your name and role, your email address, how you expect to use the images, and the answers you give in the partner forms."),
           ("Why", "To approve access and keep in touch, and to report how the images are used, without personal details, to the funders who make new collections possible, with your consent."),
           ("How long, and your rights", "We keep your details while your organisation has access and for one year after. You can ask to see, change or delete them at any time."),
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
            + m_numbers(MOMENTUM, "from the archive’s records; updated monthly", title="In use",
                        note_text="The momentum numbers (Thomas, 8 November 2026): partners, and uses, one per download, each with its stated kind (PhotoDeck’s orders). They grow, where the stock numbers do not. Partners by name and one example of use come from the closed preview, with consent. Until there are any, these modules are left out of the live page.")
            + m_numbers([("—", k) for k in USE_KINDS], None, "c", title="Uses by kind", tight=True,
                        note_text="The eight licence categories, counted from PhotoDeck’s orders: where the images go. In the wireframe a row of counts in the catalogue form; whether it becomes a drawn graphic is decided in step 3.")
            + m_partners(tight=True) + m_use("a", tight=True)
            + m_themes(base, "a")
            + m_collection(base)
            + m_items("Principles", PRINCIPLES, "a", lead=note("One line each; the full story is on About."), sid="principles")
            + m_doors("c", links=[button(base + "about/", "About Africa Reframed", quiet=True)], tight=True))


def tpl_index_themes(p, base):
    return m_page_head(p["title"], THEMES_LEAD) + m_themes(base, "b")


def tpl_index_collections(p, base):
    return (m_page_head(p["title"], "Each collection is a body of work with its own story and the people behind it.", statement_draft=True)
            + m_collection(base, "b", title=False)
            + m_doors("c", links=[button(base + "partners/#sponsor", "Sponsor a collection on your theme →", quiet=True)], tight=True))


def tpl_theme(p, base):
    t = p["theme"]
    n = THEMES.index(t)
    # 1 name, statement, count; 2 the evidence: a lead image and six to eight samples; 3 Open in the archive; 4 the text;
    # 5 the sponsor credit; 6 previous and next.
    lead = m_photo(f"Lead image for {t['name']}", "21/9", "b")
    return (m_page_head(t["name"], t["statement"], kicker=f"Theme {n + 1} of {len(THEMES)}", meta=[f'{t["count"]} images in the archive', "House Collection"], lead=lead)
            + m_grid("d", 6, "Image from the theme", line="Six images that carry the theme; released, no minors.", title="From the archive")
            + m_doors("b", count=(t["count"], f'images on {t["name"].lower()} in the archive'), count2=("—", "uses"),
                      main=button(archive("/-/galleries/archive?search=" + quote(t["query"]), "theme-" + t["slug"]), "Open in the archive →"),
                      quiet=button(base + "request-access/", "Request access", quiet=True), line=THEME_ACTION_LINE)
            + m_text("What it shows", [THEME_TEXTS[t["slug"]]], "a")
            + m_sponsor("theme", tight=True)
            + m_themes(base, "c", current=t))


def company_card(x):
    """A company in a sponsored collection: its photograph, the kind of work, name, place and founder, what it does
    (in the tense its status allows) and, where there is one, what has happened since."""
    since = draft(x["since"], "p", "small since") if x.get("since") else ""
    return (f'<div class="item company">{img(x["name"] + ": the founder or the work, from the collection", "3/2")}'
            f'{credit_line(None, "Photo: " + x["photographer"] + " / Africa Reframed")}'
            f'<p class="kicker">{e(x["kind"])}</p><h3>{e(x["name"])}</h3><p class="small where">{e(x["where"])}</p>{draft(x["text"])}{since}</div>')


def cs_quotes(rows, title):
    q = "".join(f'<figure class="quote"><blockquote>{draft("“" + a + "”")}</blockquote><figcaption class="small">{e(b)}</figcaption></figure>' for a, b in rows)
    inner = (f'<div class="cols"><div class="c1-4">{heading(title, 3, "project-title")}</div><div class="c6-12 quotes">{q}'
             f'{note("From the founders’ emails; published once each has agreed.")}</div></div>')
    return mod("text", "a, in their words", inner, tight=True)


# The collection page's sections. Each takes the collection and the base path; a collection names the ones it uses, in order.
COLLECTION_SECTIONS = {
    "story": lambda c, base: m_text(c["story_title"], c["story"], "b",
                                    box='<dl class="facts">' + "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in c["facts"]) + "</dl>"),
    "companies": lambda c, base: mod("items", "d, the companies",
                                     f'<div class="cols"><div class="c1-4">{heading("The companies")}</div><div class="c6-12">{draft(c["companies_lead"])}'
                                     f'{note("Present tense where a company’s current activity is confirmed; otherwise as photographed in 2021, until its founder confirms.")}</div></div>'
                                     f'<div class="companies">{"".join(company_card(x) for x in c["companies"])}</div>', sid="companies"),
    "grid": lambda c, base: m_grid("d", 8, "Image from the collection", line=c["grid_line"], title="From the collection", credit=c.get("credit")),
    "making": lambda c, base: m_items("How it was made", c["making"], "b", lead=draft("From the first call with a founder to the last gallery.")),
    "photographers": lambda c, base: m_items("The photographers", c["photographers"], "d", lead=draft(c["photographers_lead"]), image_ratio="4/5", sid="photographers"),
    "bts": lambda c, base: m_grid("c", label="Behind the scenes: a photographer at work", line=c["bts"], title="Behind the scenes", level=3, credit=c.get("credit")),
    "went": lambda c, base: m_items("Where the images went", c["went"], "a", sid="where"),
    "words": lambda c, base: cs_quotes(c["words"], "In the founders’ words"),
    "sponsor": lambda c, base: m_sponsor("collection", sponsor=c["sponsor"]),
    "invite": lambda c, base: m_text(c["invite"]["title"], c["invite"]["text"], "c", contact=("Partnerships", EMAIL_PARTNERS), sid="your-theme",
                                     links=[button(base + "partners/#sponsor", "How sponsoring a collection works →", quiet=True)]),
    "places": lambda c, base: m_items("Places and series", [(k, t, f"Image from {k}") for k, t in PLACES], "d"),
    "themes": lambda c, base: m_items("Themes it feeds", [(t["name"], f'{base}themes/{t["slug"]}/') for t in THEMES], "e"),
    "goals": lambda c, base: m_items("Goals it serves", [(g, None) for g in ("SDG 4 – Quality Education", "SDG 8 – Decent Work and Economic Growth", "SDG 5 – Gender Equality")], "e", tight=True,
                                     lead=note("From the SDG field in the metadata; the three most frequent for now, to confirm from the AR Metadata sheet.")),
    "access": lambda c, base: (
        m_doors("b", count=c["access"]["count"], main=button(base + "request-access/", "Request access to the collection"),
                quiet=button(f"mailto:{EMAIL_PRESS}", "Press", quiet=True), line=c["access"]["line"], sid="access")
        if c["access"].get("request") else
        m_doors("b", count=c["access"]["count"], main=button(archive("/-/galleries/archive", c["access"]["src"]), "Open in the archive →"),
                quiet=button(base + "partners/", "How partners use the archive", quiet=True), line=c["access"]["line"], sid="access")),
    "uses": lambda c, base: (m_numbers([("—", k) for k in USE_KINDS], None, "c", title="Uses of this collection", tight=True,
                                       note_text="The collection’s own uses by kind, from PhotoDeck’s orders for its gallery: what a sponsored collection’s page carries, and what the sponsor’s report draws on. Live above the threshold.")
                             + m_use("b", tight=True)),
}


def tpl_collection(p, base):
    # The head (name, statement, the lead photograph), then the collection's own sections in its order. House Collection:
    # the story, the evidence, places and series, themes and goals, Open in the archive, in use. A sponsored collection:
    # the theme, the companies, the evidence, how it was made, the photographers and behind the scenes, where the images
    # went, the sponsor, the invitation to a collection on another theme, and access by request.
    c = p["collection"]
    head = m_page_head(c["title"], c["statement"], kicker=c["kicker"], meta=c.get("meta"), statement_draft=c.get("statement_draft", False),
                       lead=m_photo(c["lead"], "21/9", "b", credit=c.get("lead_credit")))
    return head + "".join(COLLECTION_SECTIONS[s](c, base) for s in c["sections"])


def tpl_partners(p, base):
    doors = [door("#use", "Organisations", "Use the images", "Free for selected non-profit and public partners.", dark=True),
             door("#sponsor", "Companies", "Sponsor a collection", "Companies get access through a collection sponsorship.")]
    # 1 the two doors; 2 how access works; 3 using the images; 4 sponsor a collection; 5 who already uses the archive; 6 request access, contact.
    return (m_page_head(p["title"], doors=m_doors("a", doors=doors))
            + m_text("Use the images", [ACCESS_WHO], "a", is_draft=False, sid="use")
            + m_items(None, ACCESS_STEPS, "b", tight=True)
            + m_doors("c", links=[button(base + "request-access/", "Request access", quiet=True)], tight=True)
            + m_items("Using the images", RULES, "c", lead=draft("The rules for use in plain language. Read them before you apply. Terms on the archive is the legal text.", "p", "small"), sid="using-the-images")
            + m_text("Sponsor a collection", SPONSOR_TEXT, "c", contact=("Partnerships", EMAIL_PARTNERS), sid="sponsor",
                     links=[button(base + "collections/waste-to-value/", "An example: the Waste to Value Collection →", quiet=True)])
            + m_numbers([("—", t) for t in PARTNER_TYPES], None, "c", title="Partners using the archive", sid="partners",
                        note_text="Partners by type, counted from the Request access form: an aggregate, so it can be shown before any partner is named (Thomas, 8 November 2026). Updated with each approval.")
            + m_numbers([("—", w) for w in PARTNER_WHERE], None, "c", title="Where they are", tight=True,
                        note_text="Partners by country, from the form’s Country field: a second aggregate, for the development finance institutions and the embassies.")
            + m_partners(10, "By name", tight=True) + m_use("b", "In use", tight=True))


def tpl_portal(p, base):
    doors = [door(archive("/-/galleries/archive", "portal"), "Partners", "Partner log in →", "Signed in already? This takes you straight to the images.", dark=True),
             door(base + "request-access/", "Not a partner yet?", "Request access", "Free for selected non-profit and public partners.")]
    forms = [("Report a use", "Where an image appeared, and what you need next.", [("Where it appeared", "text"), ("Link", "url"), ("Date", "text"), ("What you need next", "textarea"), ("Organisation and email", "email")]),
             ("Request imagery", "Can’t find what you need?", [("What you are looking for", "textarea"), ("For what", "text"), ("By when", "text"), ("Organisation and email", "email")]),
             ("What are you working on?", "The yearly question, any time.", [("Your project", "textarea"), ("Link", "url"), ("Organisation and email", "email")])]
    # 1 who it is for and the two doors; 2 report a use; 3 request imagery and what are you working on; 4 news and numbers; 5 the rules reminder; 6 a feedback call.
    return (m_page_head(p["title"], PORTAL_LEAD, statement_draft=True, doors=m_doors("a", doors=doors))
            + m_form("b", title="The partner’s desk", forms=forms, sid="desk",
                     lead=draft("The one place to tell us how the images are used and what you need next. Every answer lands with us, and we answer.", "p"))
            + m_numbers(MOMENTUM + [("—", "types of partner"), ("—", "kinds of use")], "once there is something to show", title="Partner news",
                        note_text="The numbers as they grow and news for partners; aggregates and consented examples only. Shown once there is something to show; until then left out of the live page.")
            + m_use("c", "News", tight=True)
            + m_text("Using the images", [PORTAL_RULES], "a", links=[button(base + "partners/#using-the-images", "All the rules", quiet=True),
                                                                    button(archive("/client", "portal-history"), "Your download history", quiet=True)], sid="rules")
            + m_form("c", title="Talk to us", button_label="Book a feedback call", sid="call", tight=True,
                     lead=draft("Optional, never required: a short call about what is missing and what you are working on.", "p", "small")))


def tpl_form(p, base):
    fields = [("Organisation", "text"), ("Your role", "text"), ("Type of organisation", "select"), ("Country", "text"), ("Focus of your work", "text"),
              ("How you will use the images", "textarea"), ("What imagery you are looking for", "textarea"), ("Email", "email")]
    aside = heading("What happens next", 3) + '<ol class="next-steps">' + "".join(f"<li><strong>{e(a)}</strong> <span class=\"draft\">{e(b)}</span></li>" for a, b in REQUEST_NEXT) + "</ol>" + draft(REQUEST_FOOT, "p", "small")
    after = (f'<p class="small">Read <a href="{base}partners/#using-the-images">the rules for using the images</a> first. '
             f'Until this form is connected, requests go through <a href="{archive("/contact", "request")}">the archive’s request form</a>.</p>')
    return (m_page_head(p["title"], f"{ACCESS_WHO} {ACCESS_COMPANIES}")
            + m_form("a", title="Request access", fields=fields, aside=aside, consent=REQUEST_CONSENT, button_label="Send the request", after=after)
            + m_text("Thank you", ["Your request is with us. We reply within a working day, and the welcome email that follows opens your account."], "a", sid="thanks"))


def tpl_press(p, base):
    facts = [(a, b) for a, b in PRESS_FACTS]
    release_text = heading("The relaunch", 3, "kicker-h") + draft("The press release, from the Strategic Platform’s draft, with date and quotes from named people who agreed to them.", "p") + f'<p class="doors">{dead_button("Download the release (PDF)", quiet=True)}</p>'
    return (m_page_head(p["title"], "Stories, images for editorial use, and someone to talk to.", statement_draft=True)
            + m_photo("Press image for the relaunch", "3/2", "c", text=release_text, side="left")
            + m_items("Fact sheet", facts, "a", is_draft=True)
            + m_text("Track record", ["Exhibitions and collaborations since 2010, told as history: the proof behind the present."], "a")
            + m_grid("a", 3, "Press image", line="A curated set for editorial use with the credit line; no images with minors.", title="Press images",
                     link=dead_button("Download the press set", quiet=True))
            + m_items("Story leads", [(s, "Two sentences on the series, the place and who to talk to.", "Image from the series") for s in GAMBIA_SERIES], "d")
            + m_items("Logos and portrait", [("Logo, black on white", "", "Logo"), ("Logo, white on black", "", "Logo"), ("Thomas Damgaard", "", "Portrait")], "d", is_draft=False)
            + m_doors("d", kicker="Press contact", address=EMAIL_PRESS, line="We answer the same day."))


def tpl_text(p, base):
    k = p["slug"]
    if k == "about":
        register = ('<div class="register">' + draft(ABOUT_GETTY_BEFORE, "p", "register-lead")
                    + '<p class="register-names">' + "".join(f"<span>{e(n)}</span>" for n in ARCHIVE_LICENSEES) + "</p>"
                    + draft(ABOUT_GETTY_AFTER, "p", "register-after")
                    + note("Companies that bought our team’s images, the images now in the archive. Institutional names (the UN, the World Bank, the BBC and others) are added once Thomas has checked they bought the team’s images.") + "</div>")
        return (m_page_head(p["title"], ABOUT_STATEMENT, statement_draft=True)
                + m_channels(ABOUT_CHANNELS)
                # 1 The archive: always on. The activity, then the proof: its collections, where its images have been, the way in.
                + m_text("The archive", ABOUT_ARCHIVE, "a", sid="archive")
                + mod("collection", "a, the collections in the archive", "".join(collection_entry(x, base) for x in by_state(ARCHIVE_COLLECTIONS)), tight=True)
                + mod("text", "the register", f'<div class="cols"><div class="c6-12">{register}'
                      f'<p class="doors">{button(base + "partners/#use", "How partners use the archive →", quiet=True)}</p></div></div>', tight=True)
                + mod("text", "the hinge", f'<div class="cols"><div class="c6-12">{draft(ABOUT_HINGE, "p", "hinge")}</div></div>', tight=True)
                # 2 Exhibitions: a medium we activate. The activity, then the projects, the door, the artists.
                + m_text("Exhibitions", ABOUT_EXHIBITIONS, "a", sid="exhibitions")
                + "".join(m_project(x) for x in by_state(EXHIBITION_PROJECTS))
                + m_doors("c", links=[button(f"{base}partners/#sponsor", ABOUT_EXHIBITION_DOOR + " →", quiet=True)], tight=True)
                + m_items("The artists", [(n, d, l) for n, d, l in ARTISTS_SHOWN], "d", lead=draft(ABOUT_ARTISTS_LEAD), image_ratio="4/5", cols=4, sid="artists", level=3)
                + m_items("From the network", [(n, d, n) for n, d in ARTISTS_NETWORK], "d", image_ratio="1/1", cols=6, tight=True, level=3,
                          lead=note("Artists profiled in our journal; one work each, with the artist’s name and series as the credit."))
                # 3 Workshops: a medium we activate. The activity, then the projects, Bamako Nights, the partners.
                + m_text("Workshops", ABOUT_WORKSHOPS, "a", sid="workshops")
                + "".join(m_project(x) for x in by_state(WORKSHOP_PROJECTS))
                + m_items("In their words", ABOUT_INTERVIEWS, "d", image_ratio="16/9", tight=True, level=3,
                          lead=draft("Three of the programme’s photographers, on what it meant to them.")
                          + note("Short films of interviews with the photographers; played on click with a poster frame, never autoplaying (the one-motion rule)."))
                + m_grid("d", 6, "Bamako Nights", line=BAMAKO_NIGHTS, title="Bamako Nights", credit="Students of CFP Bamako, Bamako Nights, 2011", level=3)
                + m_items("Workshop partners", WORKSHOP_PARTNERS, "a", tight=True, level=3, cls="five")
                + mod("text", "the way to the collection", f'<div class="cols"><div class="c6-12">{draft(ABOUT_WORKSHOPS_TO_COLLECTION)}'
                      f'<p class="doors">{button(base + "collections/house-collection/", "The House Collection →", quiet=True)}</p></div></div>', tight=True)
                # 4 Who is behind it
                + m_text("Who is behind it", ABOUT_WHO, "a", sid="who")
                + m_items(None, ABOUT_PEOPLE, "d", image_ratio="1/1", tight=True, cols=4)
                + m_items("Principles", PRINCIPLES + [("Fair terms", "One download, one licence, free of charge; no resale, no sublicensing.")], "a")
                + m_doors("d", kicker="Write to us", address=EMAIL_MAIN, line=f"Partnerships: {EMAIL_PARTNERS} · Press: {EMAIL_PRESS}"))
    if k == "contact":
        return (m_page_head(p["title"], "One quiet way to reach us.", statement_draft=True)
                + m_doors("d", kicker="Write to us", address=EMAIL_MAIN, line=f"Press: {EMAIL_PRESS} · Partnerships: {EMAIL_PARTNERS} · Africa Reframed on LinkedIn."))
    return (m_page_head(p["title"], "What we collect when you request access or write to us, and why.", statement_draft=True)
            + "".join(m_text(h, [t], "a") for h, t in PRIVACY))


TEMPLATES = {"home": tpl_home, "themes": tpl_index_themes, "collections": tpl_index_collections, "theme": tpl_theme,
             "collection": tpl_collection, "partners": tpl_partners, "portal": tpl_portal, "form": tpl_form,
             "press": tpl_press, "text": tpl_text}


# ---------------------------------------------------------------------------------------------
# /dev/modules: every module with each of its variants on one page (step 2), generated by every build.
# ---------------------------------------------------------------------------------------------
def tpl_modules(base):
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
            + m_page_head("Page head with the lead photograph", "The page opening of the theme and collection pages.", lead=m_photo("Lead image", "21/9", "b"))
            + m_text("Text section", ["Title left, text right: 60 to 160 words of text in the right columns, the measure capped at about 70 characters a line."], "a")
            + m_text("With a facts box", ["The text, then the facts box in the right columns under it."], "b", box=sample_box)
            + m_text("With a contact", ["The text, then the contact as the right column’s end."], "c", contact=("Partnerships", EMAIL_PARTNERS))
            + m_text(None, ["The intro on Home: two or three sentences in columns 1–8 under the Opening, with the ways on."], "d",
                     links=[button("#", "Explore the themes", quiet=True), button("#", "How partners use the archive", quiet=True)])
            + m_photo("Full bleed", "21/9", "a", caption="AR-ID · The caption, at most 40 words, led by the AR ID where the image is featured.")
            + m_photo("On the columns", "3/2", "b", caption="AR-ID · The caption.")
            + m_photo("Photograph and text", "3/2", "c", text=heading("Beside the photograph", 3) + draft("The text in the other half of the columns; the next one alternates."), side="left")
            + m_photo("Photograph and text", "4/5", "c", text=heading("Alternating", 3) + draft("The photograph on the right this time."), side="right")
            + m_grid("a", 3, "Image", title="Image grid: three in a row")
            + m_grid("b", 4, "Portrait", title="Four portraits")
            + m_grid("c", title="A strip of three")
            + m_grid("d", 8, "Image", title="Six to eight, mixed", line="Equal frames with 8 px gaps.")
            + m_themes(base, "a") + m_themes(base, "b") + m_themes(base, "c", current=t)
            + m_collection(base)
            + m_numbers(title="Numbers: a row of three")
            + m_doors("b", count=("198", "images on learning in the archive"), main=button("#", "Open in the archive →"), quiet=button("#", "Request access", quiet=True), line=THEME_ACTION_LINE)
            + m_numbers([("72", "Mali"), ("21", "Kenya"), ("105", "The Gambia")], None, "c", title="A count by country", note_text="Illustrative figures; the real counts come from the AR Metadata sheet.")
            + m_partners(6)
            + m_use("a") + m_use("b") + m_use("c", "Partner news")
            + m_doors("c", links=[button("#", "The ways on", quiet=True), button("#", "A second quiet link", quiet=True)])
            + m_doors("d", kicker="Contact band", address=EMAIL_PRESS, line="A line of at most 15 words.")
            + m_items("Item list: plain", PRINCIPLES[:3], "a")
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


# ---------------------------------------------------------------------------------------------
# The development page (/dev/): a view generated by every build, removed at launch (LAUNCH = True).
# Decisions and the log live on the Drive; this page only shows the state of the build and points to the masters.
# The repository and this site are public: nothing internal goes here, only links (which need sign-in).
# ---------------------------------------------------------------------------------------------
STAGES = ["Wireframe", "Copy", "Design", "Ready"]
STATE = {}            # slug -> stage; every page is at "Wireframe" until it moves on
TEMPLATE_NAMES = {"home": "Home", "themes": "Index", "collections": "Index", "theme": "Theme page",
                  "collection": "Collection page", "partners": "Partners", "portal": "Partner portal",
                  "form": "Form", "press": "Press room", "text": "Text page"}
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
        ("Measure", "running text up to 36 em, about 70 characters, inside its columns", "the same", "the same"),
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
# tablet, 64 px with the 128 px logo on phones. The measure: running text caps at 36 em (about 70 characters at 17 px),
# because the guide's text columns 6–12 are 752 px at the full width, about 95 characters, more than its own 60–75.
GRID_CSS_VARS = """  --cols:12; --gutter:32px; --margin:64px; --content-max:1312px;
  --page-max:calc(var(--content-max) + 2*var(--margin));
  --off-edge:calc((min(100vw,var(--page-max)) - 100vw)/2 - var(--margin));
  --header-h:128px; --logo-w:192px; --section:96px; --section-head:64px; --section-tight:32px; --measure:36em;
"""
# Photographs relate to the grid in three ways (the guide's four image layouts all use the second):
# 1. full bleed (.bleed): edge to edge of the page, ignoring the margins; its caption and credit sit on the grid below;
# 2. on the columns (.cols with c1-12, c6-12 or any span): the photograph starts and ends on column lines;
# 3. off one edge (.c5-off, the Opening): the photograph starts on a column line and runs off one edge of the page,
#    so the words stand on white beside it in columns 1–4 (desktop); below 1,024 px the words move under it and the
#    photograph starts on the line of column 2 (tablet and phone), still running off the right edge.

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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap">
<link rel="stylesheet" href="{base}assets/site.css?v={stamp}">
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
      <a href="{base}partner-portal/"{cur_portal}>Log in</a>
    </nav>
  </div>
</header>
{strip}<main id="main">
{main}
</main>
<footer class="site-footer">
  <div class="wrap">
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

CSS = """:root{
  --ground:#151515; --paper:#ffffff; --ink:#151515; --ink-soft:#5c5a55;
  --text-on-dark:#e3e3e3; --accent:#fef98b; --line:#e6e4df; --wash:#f6f5f2;
  --wire:#ecebe7; --wire-line:#cfccc5; --bar:#e3e1dc;
  --font:"DM Sans",system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
""" + GRID_CSS_VARS + """}
*{box-sizing:border-box}
html,body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font);font-size:16px;line-height:1.55}
a{color:inherit}
.wrap{max-width:var(--page-max);margin:0 auto;padding:0 var(--margin)}
/* The 12-column grid as a utility: children name their columns (c1-4: columns 1 to 4; c6-12: 6 to 12; c5-off: from column 5 off the right edge of the page) */
.cols{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));column-gap:var(--gutter)}
.c1-4{grid-column:1/5}.c6-12{grid-column:6/-1}.c1-12{grid-column:1/-1}.c1-8{grid-column:1/9}.c1-6{grid-column:1/7}.c7-12{grid-column:7/-1}
.c-half{grid-column:span 6}.c-offset{grid-column:6/-1}
.c5-off{grid-column:5/-1;margin-right:var(--off-edge)}
.bleed{width:100vw;margin-left:calc(50% - 50vw);max-width:none}
.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:8px;background:var(--accent);color:var(--ink);padding:8px 12px;z-index:20}
:focus-visible{outline:2px solid var(--ink);outline-offset:2px}

/* Header: white, the black logo top left, the menu in black (the guide, Header; Thomas, 8 November 2026: pulled forward
   from step 4 so both live sites match). Logo left, one flat menu right, pixel-identical to the archive's.
   On the grid: the logo's left edge on the line of column 1, the menu's right edge on the right edge of column 12. */
.site-header{background:var(--paper);color:var(--ink)}
.bar{display:flex;align-items:center;justify-content:space-between;gap:24px;min-height:var(--header-h)}
.brand{display:inline-flex;align-items:center}
.brand-logo{width:var(--logo-w);height:auto;display:block}
.menu{display:flex;align-items:center;gap:24px;font-size:17px}
.menu a{padding:6px 0;border-bottom:2px solid transparent;color:var(--ink);white-space:nowrap;text-decoration:none}
.menu a:hover{color:var(--ink-soft)}
.menu a[aria-current="page"]{border-bottom-color:var(--ink)}
.divider{display:inline-block;width:1px;height:18px;background:var(--ink);margin:0 4px}
.menu-toggle{display:none;background:none;border:0;padding:8px;cursor:pointer;width:44px;height:44px;flex-direction:column;justify-content:center;gap:5px}
.menu-toggle span{display:block;height:2px;background:var(--ink)}

/* The wireframe strip */
.wire-strip{background:var(--accent);color:var(--ink);font-size:13px;padding:6px 0}
.wire-strip .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px}
.strip-tools{display:flex;align-items:center;gap:14px;white-space:nowrap}
.strip-tools a{color:var(--ink)}
.notes-toggle{font:inherit;font-size:13px;background:transparent;border:1px solid rgba(21,21,21,.4);border-radius:0;padding:3px 10px;cursor:pointer;white-space:nowrap;color:var(--ink)}

/* Wireframe parts */
.img{position:relative;width:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:0;
  background:
    linear-gradient(to top right,transparent calc(50% - .7px),var(--wire-line) calc(50% - .7px),var(--wire-line) calc(50% + .7px),transparent calc(50% + .7px)),
    linear-gradient(to bottom right,transparent calc(50% - .7px),var(--wire-line) calc(50% - .7px),var(--wire-line) calc(50% + .7px),transparent calc(50% + .7px)),
    var(--wire)}
.img span{background:var(--wire);color:#6b6862;font-size:12px;line-height:1.35;padding:4px 8px;max-width:80%;text-align:center;border-radius:0}
.img.dark{background:
    linear-gradient(to top right,transparent calc(50% - .7px),#454545 calc(50% - .7px),#454545 calc(50% + .7px),transparent calc(50% + .7px)),
    linear-gradient(to bottom right,transparent calc(50% - .7px),#454545 calc(50% - .7px),#454545 calc(50% + .7px),transparent calc(50% + .7px)),
    #2a2a2a}
.img.dark span{background:#2a2a2a;color:#a9a6a0}
.note{display:block;width:fit-content;max-width:62ch;font-size:13px;line-height:1.45;background:#fff8c2;border-left:3px solid #e0cf3c;padding:6px 10px;color:#4b4943;margin:4px 0 16px}
.lines{max-width:60ch;margin:8px 0 16px}
.lines i{display:block;height:10px;background:var(--bar);border-radius:0;margin:0 0 12px}
.lines i:last-child{width:62%}
.ph-text{color:#9a978f;font-style:italic;font-size:14px;margin:0 0 8px}
body.clean .note,body.clean .img span{display:none}
/* Draft copy: written from the masters, marked until Thomas approves it; the mark hides in clean view */
.draft{text-decoration:underline dotted #b8a62a;text-decoration-thickness:1px;text-underline-offset:3px}
body.clean .draft{text-decoration:none}
/* Modules: each section carries its number and variant as a label (Website – modules); hidden in clean view */
.mod{position:relative;padding-top:var(--section)}
.mod::before{content:attr(data-mod);box-sizing:border-box;position:absolute;left:0;top:calc(var(--section) - 22px);font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:#8a877f;background:#fff8c2;padding:1px 6px;border-radius:0;z-index:2;max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mod.page-head::before,.mod.opening::before{top:8px}
body.clean .mod::before{display:none}
.mod.band{background:var(--wash);padding:var(--section-head) 0;margin-top:var(--section)}
.mod.band::before{top:4px}
.mod .mod{padding-top:32px}
.mod .mod .wrap{padding:0;max-width:none}
.mod .mod::before{top:8px}
.mod.tight{padding-top:calc(var(--section)/2)}  /* grouped with the module before it: half the distance */
.mod.tight::before{top:calc(var(--section)/2 - 22px)}
.mod.band + .mod.band{margin-top:0}
.mod .cols + .cols{margin-top:24px}
.head-right{padding-top:8px}
.lead-photo{margin-top:32px}
.credit{font-size:12px;line-height:1.4;color:var(--ink-soft);margin:6px 0 0}
.credit .caption{color:var(--ink)}
.kicker-h{margin-top:0}
.imgs{display:grid;gap:8px;margin-top:8px}
.grid-3{grid-template-columns:repeat(3,minmax(0,1fr))}
.grid-4{grid-template-columns:repeat(4,minmax(0,1fr))}
.grid-strip{grid-template-columns:repeat(3,minmax(0,1fr))}
.grid-mixed{grid-template-columns:repeat(4,minmax(0,1fr));align-items:start}
.bleed-img{border-radius:0}
.theme-entry{display:flex;flex-direction:column;text-decoration:none;scroll-snap-align:start}
.theme-entry h3{margin:4px 0 6px}
.theme-entry p{font-size:15px;color:var(--ink-soft);margin:0 0 8px}
.theme-entry:hover h3{text-decoration:underline}
.theme-rows{margin-top:8px}
.theme-entry.row{display:grid;grid-template-columns:72px 1fr 1.3fr;gap:32px;align-items:center;padding:28px 0;border-top:1px solid var(--line)}
.theme-entry.row .order{font-size:40px;line-height:1;margin:0;color:var(--ink)}
.theme-entry.row h3{font-size:28px;font-weight:500;margin:0 0 8px}
.theme-nav .dir{display:block;font-size:13px;color:var(--ink-soft);margin-bottom:8px}
.collection-card{text-decoration:none;align-items:center;margin-top:8px}
.collection-card:hover .h-big{text-decoration:underline}
.item .img{margin-bottom:10px}
.acc{border-top:1px solid var(--ink);padding:0}
.acc:last-child{border-bottom:1px solid var(--ink)}
.acc summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;padding:14px 0;font-size:17px}
.acc summary::-webkit-details-marker{display:none}
.acc .plus{width:14px;height:14px;position:relative;flex:none}
.acc .plus::before,.acc .plus::after{content:"";position:absolute;background:var(--ink);left:0;top:6px;width:14px;height:2px}
.acc .plus::after{transform:rotate(90deg)}
.acc[open] .plus::after{display:none}
.acc p{margin:0 0 16px}

/* About: the three lines of activity, the register, the projects (About page – build brief) */
.channels{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
.channels a{display:block;text-decoration:none;border-top:2px solid var(--ink);padding-top:14px;height:100%}
.channels strong{display:block;font-weight:500;font-size:24px;line-height:1.2;margin:0 0 8px}
.channels a:hover strong{text-decoration:underline}
.channels .channel-line{font-size:15px;color:var(--ink-soft)}
.register{margin:0 0 8px;padding:20px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.register-lead{font-size:14px;color:var(--ink-soft);margin:0 0 8px}
.register-names{display:flex;flex-wrap:wrap;gap:4px 28px;font-size:20px;line-height:1.4;margin:0 0 12px;max-width:none}
.register-after{margin:0}
.hinge{font-size:22px;line-height:1.35;max-width:32ch;margin:0}
.project-title{font-size:22px;font-weight:500;line-height:1.25;margin:0 0 10px}
.kicker.state{display:inline-block;color:var(--ink);background:var(--accent);padding:2px 8px;margin-bottom:10px}
.principles.five{grid-template-columns:repeat(5,minmax(0,1fr))}
.cards-6{display:grid;gap:20px;margin-top:8px;grid-template-columns:repeat(6,minmax(0,1fr))}
.cards-6 .item h3{font-size:15px;margin:8px 0 4px}
.cards-6 .item p{font-size:13px;line-height:1.4}

/* Collections: the list of cards, and a sponsored collection's companies and the founders' words (the collection template) */
.collection-list .collection-card + .collection-card{margin-top:var(--section-tight);padding-top:var(--section-tight);border-top:1px solid var(--line)}
.companies{display:grid;gap:44px 24px;margin-top:8px;grid-template-columns:repeat(4,minmax(0,1fr))}
.company .kicker{margin:14px 0 4px}
.company h3{font-size:20px;font-weight:500;margin:0 0 4px}
.company .where{margin:0 0 10px}
.company p{font-size:15px;line-height:1.45}
.company .since{border-top:1px solid var(--line);padding-top:10px;margin-top:4px}
.quote{margin:0 0 28px}
.quote blockquote{margin:0}
.quote blockquote p{font-size:22px;line-height:1.35;max-width:36ch;margin:0 0 8px}

/* Type */
h1{font-weight:500;font-size:48px;line-height:1.06;margin:0 0 16px;letter-spacing:-.015em;max-width:20ch;text-wrap:balance}
h2{font-weight:500;font-size:28px;line-height:1.2;margin:0 0 12px;letter-spacing:-.01em}
h3{font-weight:600;font-size:18px;line-height:1.25;margin:12px 0 6px}
p{margin:0 0 12px;max-width:var(--measure)}  /* the measure: about 70 characters, whatever the column span */
.lead{font-size:19px;max-width:60ch;color:var(--ink)}
.statement{font-size:24px;line-height:1.35;max-width:40ch;margin:0 0 20px;text-wrap:pretty}
.kicker{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft);margin:0 0 8px}
.small{font-size:14px;color:var(--ink-soft)}
.h-big{font-size:24px;font-weight:500;line-height:1.25;margin:4px 0 12px}
.h-big a{overflow-wrap:anywhere}
.list{margin:0 0 16px;padding-left:20px}
.list li{margin:4px 0}
.meta-row{display:flex;flex-wrap:wrap;gap:6px 22px;font-size:14px;color:var(--ink-soft);margin:0 0 16px}
.textlink{font-weight:500;border-bottom:2px solid var(--accent)}

/* Sections: the vertical rhythm on the 8 px scale (96 px between sections on desktop, 80 on tablets, 64 on phones) */
main{padding-bottom:var(--section)}
.sec{padding-top:var(--section)}
.sec.page-head{padding-top:var(--section-head)}
.sec.tight{padding-top:var(--section-tight)}
.sec.band{background:var(--wash);padding:var(--section-head) 0;margin-top:var(--section)}
.sec.band + .sec.band{margin-top:0}
.grid-2{display:grid;grid-template-columns:1.4fr 1fr;gap:56px;align-items:start}
.split{display:grid;grid-template-columns:1.2fr 1fr;gap:40px;align-items:center;text-decoration:none;margin-top:8px}
.card-link:hover .h-big{text-decoration:underline}
.cards-2,.cards-3,.cards-4,.cards-5{display:grid;gap:24px;margin-top:8px}
.cards-2{grid-template-columns:repeat(2,minmax(0,1fr))}
.cards-3{grid-template-columns:repeat(3,minmax(0,1fr))}
.cards-4{grid-template-columns:repeat(4,minmax(0,1fr))}
.cards-5{grid-template-columns:repeat(5,minmax(0,1fr))}
.card{border:1px solid var(--line);border-radius:0;padding:20px;background:#fff}
.card h3{margin-top:0}
.example .img{margin-bottom:10px}

/* Buttons */
.doors{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0 12px}
.button{display:inline-flex;align-items:center;min-height:44px;padding:0 20px;background:var(--accent);color:var(--ink);font:inherit;font-weight:500;font-size:15px;border-radius:0;border:0;text-decoration:none;cursor:pointer}
.button.quiet{background:transparent;border:1px solid #c9c6bf;color:var(--ink)}
.button[disabled],.button.dead{opacity:.55;cursor:not-allowed}

/* Home: the Opening on the grid (the third photograph case). The photograph starts on the line of column 5 and runs off
   the right edge; the words stand on white in columns 1–4. Proportions after the guide's hero at 1440 × 720: under the
   128 px header the photograph is 928 × 512 (29:16) with 80 px of white below it; the words start 160 px below the header.
   The stripes and triangles are drawn in step 3; here only the geometry. */
.opening{overflow-x:hidden;padding-bottom:80px;padding-top:0}
.opening .cols{row-gap:24px}
.opening-words{padding-top:160px}
.opening-words h1{font-size:40px;max-width:none}
.opening-img{aspect-ratio:29/16;max-height:80vh;border-radius:0}
.opening-img span{position:absolute;top:16px;left:16px;max-width:60%}
.intro{padding-top:48px}
.intro-num{padding-top:8px}
.numbers{display:flex;flex-wrap:wrap;gap:16px 44px;margin:8px 0}
.num b{display:block;font-size:44px;font-weight:500;line-height:1;font-variant-numeric:tabular-nums}
.num span{font-size:14px;color:var(--ink-soft)}
.numbers.by-kind{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px 32px;border-top:1px solid var(--ink);padding-top:16px;margin-top:16px}
.small-num b{font-size:32px}
.theme-row{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:32px;margin-top:32px}
.order{font-size:13px;color:var(--ink-soft);font-variant-numeric:tabular-nums;margin-top:12px}
.count{font-size:13px;font-weight:500;margin-top:auto}
.logos{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px;margin:8px 0 32px}
.logo{aspect-ratio:5/2;border:1px dashed #c9c6bf;border-radius:0;display:flex;align-items:center;justify-content:center;font-size:12px;color:#8a877f}


/* Theme and collection pages */
.wide{max-height:62vh}
.action{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px 32px}
.action .doors{margin:0}
.facts-box{border:1px solid var(--line);border-radius:0;padding:24px;background:#fff}
.facts{display:grid;grid-template-columns:auto 1fr;gap:8px 20px;font-size:15px;margin:0 0 16px}
.facts dt{color:var(--ink-soft)}
.facts dd{margin:0}
.place h3{margin-top:12px}
.chips{display:flex;flex-wrap:wrap;gap:10px;align-content:start}
.chip{border:1px solid #c9c6bf;border-radius:0;padding:8px 16px;text-decoration:none;font-size:15px}
.chip:hover{border-color:var(--ink)}
.chip.ghost{display:inline-block;width:120px;height:38px;padding:0;background:var(--bar);border-color:transparent}
.thanks{max-width:560px}
.person .img{margin-bottom:10px;max-width:260px}
.narrow{max-width:62ch}
.principles{list-style:none;padding:0;margin:8px 0 20px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}
.principles li{border-top:2px solid var(--ink);padding-top:12px}
.principles strong{display:block;font-weight:500;font-size:18px;line-height:1.3;margin-bottom:6px}
.principles .lines{margin:6px 0 0}

/* Partners */
.steps{list-style:none;padding:0;margin:24px 0 16px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.steps li{border-top:2px solid var(--ink);padding-top:14px}
.steps h3{margin:6px 0 4px}
.steps p{font-size:15px;color:var(--ink-soft);margin:0}
.step-n{font-size:13px;color:var(--ink-soft)}
.rules{padding-left:22px;columns:2 320px;column-gap:56px;margin:8px 0 20px}
.rules li{margin:0 0 14px;break-inside:avoid}
.contact-box{border-left:3px solid var(--accent);padding:8px 0 8px 24px;margin-top:44px}

/* Partner portal */
.door-panels{display:grid;grid-template-columns:1fr 1fr;gap:var(--gutter);margin-top:32px}
.panel{display:flex;flex-direction:column;justify-content:flex-end;gap:6px;min-height:200px;padding:28px;border:1px solid #c9c6bf;border-radius:0;text-decoration:none}
.panel strong{font-size:30px;font-weight:500;line-height:1.15}
.panel span:last-child{font-size:15px;color:var(--ink-soft)}
.panel.dark{background:var(--ground);border-color:var(--ground);color:#fff}
.panel.dark strong{color:var(--accent)}
.panel.dark .kicker,.panel.dark span:last-child{color:#bdbab3}
.panel:hover strong{text-decoration:underline}
.mini-form{display:flex;flex-direction:column;gap:4px}
.f-label{font-size:13px;color:var(--ink-soft);margin-top:6px}
.field{display:block;height:38px;border:1px solid #d6d3cc;border-radius:0;background:#fff}
.field.tall{height:76px}
.mini-form .button,.card .button{align-self:flex-start;margin-top:14px}
.call-card{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 32px}
.call-card .button{margin-top:0;align-self:center}
.logo-tile{background:var(--ground);aspect-ratio:3/2;display:flex;align-items:center;justify-content:center;border-radius:0;margin-bottom:10px}
.logo-tile img{width:62%}

/* Form */
.form{display:grid;gap:6px;max-width:560px;margin:8px 0 16px}
.form label{font-size:14px;font-weight:500;margin-top:10px}
.form input,.form select,.form textarea{font:inherit;padding:10px 12px;border:1px solid #c9c6bf;border-radius:0;background:#fff}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;color:var(--ink-soft)}
.form .button{justify-self:start;margin-top:16px}
.next-steps{padding-left:20px;margin:8px 0 16px}
.next-steps li{margin:6px 0}

/* Development page */
.table-scroll{overflow-x:auto;margin-top:8px}
.dev-table{width:100%;border-collapse:collapse;font-size:14px;min-width:640px}
.dev-table th,.dev-table td{text-align:left;padding:10px 12px 10px 0;border-bottom:1px solid var(--line);vertical-align:top}
.dev-table th{font-weight:500;color:var(--ink-soft);font-size:13px}
.dev-table tfoot td{font-weight:500;border-bottom:0}
.dev-table .n{text-align:right;font-variant-numeric:tabular-nums}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;overflow-wrap:anywhere}
.stepper{display:inline-flex;gap:3px;flex-wrap:wrap}
.stepper span{font-size:11px;padding:2px 6px;border-radius:0;background:var(--wash);color:#9a978f}
.stepper span.done{background:#e3e1dc;color:var(--ink)}
.stepper span.on{background:var(--ink);color:#fff}
.dev-list{list-style:none;padding:0;margin:8px 0 0;max-width:900px}
.dev-list li{display:grid;grid-template-columns:minmax(0,260px) 1fr;gap:4px 24px;padding:12px 0;border-top:1px solid var(--line)}
.dev-list li > span:last-child{color:var(--ink-soft)}
.dev-list .where{font-size:12px;color:#8a877f}
.dev-list li:has(.tag){grid-template-columns:64px minmax(0,300px) 1fr}
.dev-list li:has(.where){grid-template-columns:minmax(0,300px) 140px 1fr}
.tag{display:inline-block;font-size:11px;letter-spacing:.04em;padding:2px 7px;border-radius:0;height:fit-content;width:fit-content}
.tag.done{background:#e3e1dc}.tag.next{background:var(--accent)}.tag.later,.tag.open{border:1px solid #c9c6bf;color:var(--ink-soft)}

/* Footer */
.site-footer{border-top:1px solid var(--line);padding:32px 0 48px;color:var(--ink-soft);font-size:14px}
.site-footer p{margin:0 0 8px;max-width:none}
.site-footer a{color:var(--ink)}
.about-line{color:var(--ink)}

/* The grid overlay: switched on with the Grid button in the wireframe strip, ?grid in the address or the key G.
   Columns in blue, margins in red; the readout gives the values at the current width. Not built at launch. */
.grid-overlay{display:none;position:fixed;inset:0;pointer-events:none;z-index:999}
body.show-grid .grid-overlay{display:block}
.grid-overlay .wrap{height:100%;position:relative;background:
  linear-gradient(to right,rgba(220,60,60,.10) 0 var(--margin),transparent var(--margin) calc(100% - var(--margin)),rgba(220,60,60,.10) calc(100% - var(--margin)))}
.grid-overlay .cols{height:100%}
.grid-overlay .col{background:rgba(40,110,220,.10);border-left:1px solid rgba(40,110,220,.45);border-right:1px solid rgba(40,110,220,.45);font-size:11px;color:rgba(40,110,220,.9);padding:4px 0 0 4px;font-variant-numeric:tabular-nums}
.grid-overlay .col.col-5{background:rgba(40,110,220,.16)}  /* the Opening starts here on desktop */
.grid-read{position:absolute;left:0;right:0;bottom:16px;width:fit-content;background:rgba(21,21,21,.9);color:#fff;font-size:12px;line-height:1.4;padding:6px 10px;border-radius:0;font-variant-numeric:tabular-nums}
.grid-toggle{font:inherit;font-size:13px;background:transparent;border:1px solid rgba(21,21,21,.4);border-radius:0;padding:3px 10px;cursor:pointer;white-space:nowrap;color:var(--ink)}
.grid-toggle[aria-pressed="true"],.notes-toggle[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}

/* Tablet (768–1,023 px): 8 columns, 24 px gutters, 32 px margins; the menu folds, like the archive's below tablet width */
@media (max-width:1023px){
  :root{--cols:8;--gutter:24px;--margin:32px;--section:80px;--section-head:56px;--section-tight:28px}
  .cards-6{grid-template-columns:repeat(3,minmax(0,1fr))}
  .principles.five{grid-template-columns:repeat(2,minmax(0,1fr))}
  .menu-toggle{display:flex}
  .menu{display:none;position:absolute;left:0;right:0;top:var(--header-h);background:var(--paper);flex-direction:column;align-items:flex-start;gap:0;padding:8px var(--margin) 24px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);z-index:10}
  .menu.open{display:flex}
  .menu a{padding:12px 0;font-size:17px;width:100%}
  .divider{width:100%;height:1px;margin:8px 0}
  .site-header{position:relative}
  .c1-4{grid-column:1/4}.c6-12,.c-offset{grid-column:4/-1}.c1-8{grid-column:1/7}.c1-6{grid-column:1/5}.c7-12{grid-column:5/-1}.c-half{grid-column:span 4}
  .grid-4,.grid-mixed{grid-template-columns:repeat(2,minmax(0,1fr))}
  .grid-overlay .col.col-5{background:rgba(40,110,220,.10)}.grid-overlay .col.col-2{background:rgba(40,110,220,.16)}
  .wire-strip .wrap{flex-wrap:wrap}
  .theme-row{grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:minmax(220px,40%);overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:8px;gap:24px}
  .cards-4,.cards-5,.principles,.companies{grid-template-columns:repeat(2,minmax(0,1fr))}
  /* the Opening below desktop: the photograph first, from the line of column 2 off the right edge; the words under it */
  .opening{padding-bottom:0}
  .opening-words{grid-column:1/-1;order:2;padding-top:8px}
  .opening-words h1{font-size:34px;max-width:24ch}
  .c5-off{grid-column:2/-1;order:1}
  .opening-img{aspect-ratio:3/2}
}
/* Phone (below 768 px): the guide's 4 columns, 16 px gutters and 16 px margins; one column, the title first */
@media (max-width:767px){
  :root{--cols:4;--gutter:16px;--margin:16px;--header-h:64px;--logo-w:128px;--section:64px;--section-head:40px;--section-tight:24px}
  .channels{grid-template-columns:1fr;gap:16px}
  .cards-6{grid-template-columns:repeat(2,minmax(0,1fr))}
  .mod-items .cards-4{grid-template-columns:repeat(2,minmax(0,1fr));gap:20px 16px}
  .principles.five{grid-template-columns:1fr}
  .mod-items .cards-4 .item p{font-size:14px;line-height:1.4}
  .hinge{font-size:19px}
  h1{font-size:34px}
  h2{font-size:24px}
  .statement{font-size:20px}
  .c1-4,.c6-12,.c1-8,.c1-6,.c7-12,.c-half,.c-offset{grid-column:1/-1}
  .grid-3,.grid-4,.grid-mixed{grid-template-columns:repeat(2,minmax(0,1fr))}
  .mod .cols + .cols{margin-top:16px}
  .theme-entry.row{grid-template-columns:44px 1fr;gap:12px 16px}
  .theme-entry.row .imgs{grid-column:1 / -1}
  .theme-entry.row .order{font-size:28px}
  .theme-entry.row h3{font-size:24px}
  .numbers{gap:16px 32px}
  .numbers.by-kind{grid-template-columns:repeat(2,minmax(0,1fr))}
  .opening-img{aspect-ratio:3/2}  /* 3:2 on phones so the core line sits in the first screen (4:5 pushed it below) */
  .opening-words h1{font-size:30px}
  .grid-2,.split,.door-panels,.steps,.theme-nav,.cards-2,.cards-3{grid-template-columns:1fr}
  .grid-2{gap:32px}
  .split{gap:20px}
  .contact-box{margin-top:0}
  .panel{min-height:132px;padding:22px}
  .dev-list li,.dev-list li:has(.tag),.dev-list li:has(.where){grid-template-columns:1fr}
  .strip-tools{gap:10px}
  .theme-row{grid-auto-columns:78%}
}
@media (max-width:480px){
  .cards-4,.cards-5,.principles,.companies{grid-template-columns:1fr}
  .companies{gap:36px}
  .quote blockquote p{font-size:19px}
  .wire-strip .wrap{align-items:flex-start}
  .panel strong{font-size:26px}
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
            f'<a href="{base}dev/">Development</a><a href="{base}dev/modules/">Modules</a>'
            f'<button class="grid-toggle" type="button" aria-pressed="false" title="Show the grid (or press G)">Grid</button>'
            f'<button class="notes-toggle" type="button" aria-pressed="false">Clean view</button></span></div></div>\n'
            f'<div class="grid-overlay" aria-hidden="true"><div class="wrap"><div class="cols"></div><div class="grid-read"></div></div></div>\n')


def render(p, main, base):
    cur = lambda s: ' aria-current="page"' if p["nav"] == s else ""
    doc_title = "Africa Reframed" if p["slug"] == "home" else f'{p["title"]} · Africa Reframed'
    return LAYOUT.format(
        doc_title=e(doc_title), og_title=e(p["title"] if p["slug"] != "home" else "Africa Reframed"),
        desc=e(p["desc"]), url=SITE_URL + p["path"], share=SITE_URL + "assets/share-default.png",
        robots="" if LAUNCH else '<meta name="robots" content="noindex">\n', strip=strip_html(base),
        base=base, stamp=STAMP, slug=p["slug"], tpl=p["tpl"], main=main, about_line=e(ABOUT_LINE), archive=ARCHIVE,
        cur_themes=cur("themes"), cur_collections=cur("collections"), cur_partners=cur("partners"), cur_about=cur("about"), cur_portal=cur("portal"))


def build():
    (ROOT / "assets").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "site.css").write_text(CSS)
    share_image()
    rows, links = [], {}
    for p in PAGES:
        depth = p["path"].count("/")
        base = "../" * depth if depth else "./"
        main = TEMPLATES[p["tpl"]](p, base)
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
        (dev_dir / "index.html").write_text(render(dev, tpl_dev(rows, links, "../"), "../"))
        modules = dict(path="dev/modules/", title="Modules", slug="modules", tpl="modules", nav=None,
                       desc="Every module of the Africa Reframed site with its variants, on the grid; generated by the build, removed at launch.")
        (dev_dir / "modules").mkdir(exist_ok=True)
        (dev_dir / "modules" / "index.html").write_text(render(modules, tpl_modules("../../"), "../../"))
    (ROOT / ".nojekyll").write_text("")
    print("built", len(PAGES), "pages" + ("" if LAUNCH else " and /dev/"), "into", ROOT)


if __name__ == "__main__":
    build()
