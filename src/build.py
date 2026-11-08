#!/usr/bin/env python3
"""Generate the Africa Reframed main site as a live wireframe (version 4, 6 November 2026: arranged by the page priorities).

Structure from "Website – Site map and user flows" (05 Website on the Drive): 16 pages from 9 templates.
Header: Themes · Collections · Partners | Log in (Log in opens the Partner portal); the archive adds its own
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
# Wireframe parts
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
    """Text still to write."""
    return '<div class="lines" aria-hidden="true">' + "<i></i>" * n + "</div>"


def ph_text(text):
    return f'<p class="ph-text">{e(text)}</p>'


def sec(inner, cls="", sid=None):
    a = f' id="{sid}"' if sid else ""
    return f'<section class="sec {cls}"{a}><div class="wrap">{inner}</div></section>'


def head(title, lead=None, kicker=None, level=2):
    k = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
    l = f'<p class="lead">{e(lead)}</p>' if lead else ""
    return f'{k}<h{level}>{e(title)}</h{level}>{l}'


def button(href, label, quiet=False):
    return f'<a class="button{" quiet" if quiet else ""}" href="{href}">{e(label)}</a>'


def dead_button(label, quiet=False):
    return f'<span class="button{" quiet" if quiet else ""} dead" aria-disabled="true">{e(label)}</span>'


def doors(*buttons):
    return f'<p class="doors">{"".join(buttons)}</p>'


def numbers(values=NUMBERS):
    items = "".join(f'<div class="num"><b>{n}</b><span>{e(t)}</span></div>' for n, t in values)
    return f'<div class="numbers">{items}</div>'


def sample_grid(n=8, label="Image"):
    ratios = ["4/5", "3/2", "3/2", "4/5", "3/2", "4/5", "3/2", "3/2"]
    return '<div class="sample-grid">' + "".join(img(label, ratios[i % 8]) for i in range(n)) + "</div>"


def logos(n=5):
    return '<div class="logos">' + '<span class="logo">Partner logo</span>' * n + "</div>"


def theme_card(t, base, i):
    return (f'<a class="theme-card" href="{base}themes/{t["slug"]}/">{img("Theme image", "4/5")}'
            f'<span class="order">{i}</span><h3>{e(t["name"])}</h3><p>{e(t["statement"])}</p>'
            f'<span class="count">{t["count"]} images</span></a>')


def house_split(base):
    meta = "".join(f"<span>{x}</span>" for x in ("1,122 images", "21 shoots", "Mali · Kenya · The Gambia"))
    return (f'<a class="split card-link" href="{base}collections/house-collection/">{img("Collection image", "3/2")}'
            f'<div><p class="kicker">Collection</p><h3 class="h-big">House Collection</h3><p>{e(HOUSE_LINE)}</p>'
            f'<p class="meta-row">{meta}</p><span class="textlink">Open the collection →</span></div></a>')


def mini_form(fields, label):
    out = "".join(f'<span class="f-label">{e(l)}</span><span class="field{" tall" if tall else ""}"></span>' for l, tall in fields)
    return f'<div class="mini-form">{out}{dead_button(label)}</div>'


def steps(items):
    out = "".join(f'<li><span class="step-n">{i}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>' for i, (t, d) in enumerate(items, 1))
    return f'<ol class="steps">{out}</ol>'


def rules_list():
    return ('<ol class="rules">'
            '<li><strong>Who may use the images.</strong> Approved partners, one licence per organisation. The press set is for editorial use.</li>'
            '<li><strong>One download, one use.</strong> Each download is a free licence for the use you state there: a report, an application, an exhibition, the press, a presentation or your own channels. Collect and share images in the Lightbox; download when you know the use. A new use, a new download.</li>'
            '<li><strong>Credit.</strong> The credit line on every use, on or beside the image, as given with each image. For a sponsored collection it names the collection in full, sponsor included.</li>'
            '<li><strong>Editing.</strong> Cropping, resizing and colour are fine; changing what an image shows is not, and neither is altering images with AI or using them to train AI.</li>'
            '<li><strong>The people portrayed.</strong> Accurate captions and contexts they would recognise; never a degrading or misleading one, and never presenting the images as your own operations or results.</li>'
            '<li><strong>No resale.</strong> No resale, sublicensing or use as a logo.</li>'
            '<li><strong>Tell us where they appear.</strong> Report a use through the Partner portal.</li>'
            '</ol>')


# ---------------------------------------------------------------------------------------------
# The nine templates (each returns the inside of <main>)
# ---------------------------------------------------------------------------------------------
# Section order on the five key pages follows the page priorities: Website – Site map and user flows, section 6 (6 Nov 2026).
# Engine brief, "For design": the principles a company needs before it puts its name on the work.
PRINCIPLES_HOME = ["Real images", "Consent", "Credited, fairly paid photographers", "Editorial independence"]


def tpl_home(p, base):
    # 1 What this is: the Opening (design guide, Opening): the core line on white in columns 1–4, one real photograph from
    #   the line of column 5 off the right edge of the page. Geometry only; the stripes and triangles come in step 3.
    hero = (f'<section class="opening"><div class="wrap cols">'
            f'<div class="opening-words c1-4"><h1>{e(CORE_LINE)}</h1>'
            + note("The Opening: the words on white beside the photograph, never on it. The stripes and triangles cut in from the white edges in step 3.")
            + f'</div><div class="c5-off">{img("Opening photograph · from a column line off the right edge (5 on desktop, 2 below) · released, no minors", None, cls="opening-img")}</div>'
            f'</div></section>')
    # 2 Who it is for and who is behind it; the ways on (7) sit with it, and Request access stays quiet (6 Nov decision)
    intro = sec('<div class="narrow">'
                + note("Two or three sentences: what Africa Reframed is, who it is for and who is behind it (Commerce & Culture). A funder checking us gets it here, in the first screen.")
                + lines(3)
                + doors(button(base + "themes/", "Explore the themes"), button(base + "partners/", "How partners use the archive", quiet=True))
                + "</div>", "intro")
    # 3 That it is in use: partners by name, one example of use, the three numbers
    inuse = sec(head("In use")
                + note("The organisations using the archive, by name and with their consent, and one published example of use. They come from the closed preview; until there are any, this section is left out.")
                + numbers() + logos()
                + f'<div class="split">{img("Example of use: a report, an exhibition or an article", "3/2")}<div>'
                + lines(3) + ph_text("Partner · where it appeared · when") + "</div></div>")
    # 4 The five themes in story order
    cards = "".join(theme_card(t, base, i) for i, t in enumerate(THEMES, 1))
    themes = sec(head("Five themes", THEMES_LEAD) + f'<div class="theme-row">{cards}</div>')
    # 5 The collections
    coll = sec(head("Collections") + house_split(base)
               + note("A sponsored collection appears here once it is signed, shown as in production; never as a plan."))
    # 6 The principles, one line each, linked to About
    pr = "".join(f'<li><strong>{e(x)}</strong>{lines(1)}</li>' for x in PRINCIPLES_HOME)
    principles = sec(head("Principles") + note("One line each, in plain words; the full story is on About.")
                     + f'<ul class="principles">{pr}</ul>'
                     + doors(button(base + "about/", "About Africa Reframed", quiet=True)), "band")
    return hero + intro + inuse + themes + coll + principles


def tpl_index_themes(p, base):
    rows = []
    for i, t in enumerate(THEMES, 1):
        strip = "".join(img("Image", "1/1") for _ in range(3))
        rows.append(f'<a class="theme-line" href="{base}themes/{t["slug"]}/"><span class="order big">{i}</span>'
                    f'<div><h2>{e(t["name"])}</h2><p>{e(t["statement"])}</p><span class="count">{t["count"]} images →</span></div>'
                    f'<div class="strip3">{strip}</div></a>')
    return (sec(head(p["title"], THEMES_LEAD, level=1), "page-head")
            + sec(note("Each row shows three images from the theme. " + PUBLIC_SAMPLE) + "".join(rows), "tight"))


def tpl_index_collections(p, base):
    return (sec(head(p["title"], "Each collection is a body of work with its own story and the people behind it.", level=1), "page-head")
            + sec(house_split(base), "tight")
            + sec(note("Sponsored collections appear here when they exist, each under its full name. Nothing planned is shown.")))


def tpl_theme(p, base):
    t = p["theme"]
    n = THEMES.index(t)
    prv, nxt = THEMES[n - 1], THEMES[(n + 1) % len(THEMES)]
    meta = f'<p class="meta-row"><span>{t["count"]} images in the archive</span><span>House Collection</span></p>'
    top = sec(f'<p class="kicker">Theme {n + 1} of {len(THEMES)}</p><h1>{e(t["name"])}</h1>'
              f'<p class="statement">{e(t["statement"])}</p>{meta}', "page-head")
    lead_img = sec(img("Lead image for the theme", "21/9", cls="wide"), "tight")
    samples = sec(head("From the archive") + note("Six to eight images that carry the theme. " + PUBLIC_SAMPLE) + sample_grid())
    action = sec(f'<div class="action"><div class="num"><b>{t["count"]}</b><span>images on {e(t["name"].lower())} in the archive</span></div>'
                 + doors(button(archive("/-/galleries/archive?search=" + quote(t["query"]), "theme-" + t["slug"]), "Open in the archive →"),
                         button(base + "request-access/", "Request access", quiet=True))
                 + '</div><p class="small">Partners open the theme in the archive; others are asked to log in or request access first.</p>', "band")
    nav = sec(f'<div class="theme-nav">'
              f'<a href="{base}themes/{prv["slug"]}/">{img("Theme image", "5/2")}<span class="dir">← Previous theme</span><strong>{e(prv["name"])}</strong></a>'
              f'<a href="{base}themes/{nxt["slug"]}/">{img("Theme image", "5/2")}<span class="dir">Next theme →</span><strong>{e(nxt["name"])}</strong></a></div>')
    shows = sec(head("What it shows") + note("A short text on what the theme shows and why it matters to partners.") + lines(4))
    credit = sec(note("The sponsor credit, “made possible by …”, linked to the collection page, once a sponsor has funded the theme. "
                      "Until then nothing is shown here."), "tight")
    # Page priorities: name and statement, the evidence, Open in the archive, the text, the sponsor credit, previous and next
    return top + lead_img + samples + action + shows + credit + nav


def tpl_collection(p, base):
    facts = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in HOUSE_FACTS)
    top = sec(f'<p class="kicker">Collection</p><h1>House Collection</h1><p class="statement">{e(HOUSE_STATEMENT)}</p>', "page-head")
    hero = sec(img("Collection image", "21/9", cls="wide"), "tight")
    story = sec('<div class="grid-2"><div>' + head("The story")
                + note("How the collection was made, where and with whom. Written as history and proof, in the present tense of the archive.")
                + lines(6) + '</div><aside class="facts-box">'
                + f'<dl class="facts">{facts}</dl></aside></div>')
    people_cards = "".join(f'<div class="person">{img("Portrait", "1/1")}{ph_text("Name · role")}{lines(1)}</div>' for _ in range(3))
    people = sec(head("The people")
                 + note("Photographers and workshop partners, credited as each agrees. For a sponsored collection, the sponsor’s credit and its own statement sit here, after the work.")
                 + f'<div class="cards-3">{people_cards}</div>')
    places = []
    for country in ("Mali", "Kenya", "The Gambia"):
        series = ('<ul class="list">' + "".join(f"<li>{e(s)}</li>" for s in GAMBIA_SERIES) + "</ul>") if country == "The Gambia" else ""
        places.append(f'<div class="place">{img("Image from " + country, "3/2")}<h3>{e(country)}</h3>{series}{lines(2)}</div>')
    places_sec = sec(head("Places and series") + note("Series by name and place, as the shoot list gives them.")
                     + f'<div class="cards-3">{"".join(places)}</div>')
    samples = sec(head("From the collection") + note("A spread across the five themes. " + PUBLIC_SAMPLE) + sample_grid())
    chips = "".join(f'<a class="chip" href="{base}themes/{t["slug"]}/">{e(t["name"])}</a>' for t in THEMES)
    ghosts = '<span class="chip ghost"></span>' * 4
    feeds = sec('<div class="grid-2"><div>' + head("Themes it feeds") + f'<div class="chips">{chips}</div></div><div>'
                + head("Goals it serves") + note("The Sustainable Development Goals the collection serves, from the SDG field in the metadata.")
                + f'<div class="chips">{ghosts}</div></div></div>')
    action = sec(f'<div class="action"><div class="num"><b>1,122</b><span>images in the House Collection</span></div>'
                 + doors(button(archive("/-/galleries/archive", "collection-house"), "Open in the archive →"),
                         button(base + "partners/", "How partners use the archive", quiet=True)) + "</div>"
                 + f'<p class="small">Sponsoring a collection? Write to <a href="mailto:{EMAIL_PARTNERS}">{EMAIL_PARTNERS}</a>.</p>', "band")
    uses = "".join(f'<div class="example">{img("Example of use", "3/2")}{lines(2)}{ph_text("Partner · where it appeared · when")}</div>' for _ in range(3))
    inuse = sec(head("In use") + note("Images from this collection in use, with consent. Shown once there are any.")
                + f'<div class="cards-3">{uses}</div>')
    # Page priorities: name and image, story, people, evidence, places, themes and goals, Open in the archive, in use.
    # The same template holds a collection in production and, where it applies, the rights note (editorial use only).
    return top + hero + story + people + samples + places_sec + feeds + action + inuse


def tpl_partners(p, base):
    # Brief, Partners: one page, two doors on the first screen, nothing else above them.
    panels = (f'<div class="door-panels">'
              f'<a class="panel dark" href="#use"><span class="kicker">Organisations</span>'
              f'<strong>Use the images</strong><span>Free for selected non-profit and public partners.</span></a>'
              f'<a class="panel" href="#sponsor"><span class="kicker">Companies</span>'
              f'<strong>Sponsor a collection</strong><span>Companies get access through a collection sponsorship.</span></a></div>')
    top = sec(head(p["title"], level=1) + panels, "page-head")
    use = sec(head("Use the images") + f"<p>{e(ACCESS_WHO)}</p>"
              + steps([("Request access", "Tell us who you are and how you will use the images."),
                       ("Approved by name", "We approve each organisation by name."),
                       ("Collect, then download", "Gather images in the Lightbox and share them with colleagues. Each download is a free licence for the one use you state.")])
              + note("What we ask in return: report a use, and a yearly question about what you are working on.")
              + doors(button(base + "request-access/", "Request access")), sid="use")
    rules = sec(head("Using the images", "The rules for use in plain language. Read them before you apply.") + rules_list()
                + f'<p class="small">Draft, to be checked against the licence; <a href="{ARCHIVE}/terms">Terms</a> on the archive is the legal text.</p>',
                "band", sid="using-the-images")
    examples = "".join(f'<div class="example">{img("Example of use", "3/2")}{lines(2)}{ph_text("Partner · where it appeared · when")}</div>' for _ in range(3))
    inuse = sec(head("Partners using the archive") + note("Organisations by name and published uses, with their consent.")
                + logos(10) + f'<div class="cards-3">{examples}</div>', sid="partners")
    sponsor = sec('<div class="grid-2"><div>' + head("Sponsor a collection") + f"<p>{e(ACCESS_COMPANIES)}</p>"
                  + note("In general terms: we make new collections with companies as sponsors, theme-led and never about the sponsor’s own activities, opening new themes or deepening existing ones, each with its own collection page and credit on the theme page. The specific offers and prices belong in conversation, not on the site.")
                  + lines(2) + f'</div><div class="contact-box"><p class="kicker">Partnerships</p>'
                  f'<p class="h-big"><a href="mailto:{EMAIL_PARTNERS}">{EMAIL_PARTNERS}</a></p></div></div>', sid="sponsor")
    # Page priorities: the two doors, how access works, using the images, sponsor a collection, who already uses it
    return top + use + rules + sponsor + inuse


def tpl_portal(p, base):
    panels = (f'<div class="door-panels">'
              f'<a class="panel dark" href="{archive("/-/galleries/archive", "portal")}"><span class="kicker">Partners</span>'
              f'<strong>Partner log in →</strong><span>Signed in already? This takes you straight to the images.</span></a>'
              f'<a class="panel" href="{base}request-access/"><span class="kicker">Not a partner yet?</span>'
              f'<strong>Request access</strong><span>Free for selected non-profit and public partners.</span></a></div>')
    top = sec(head(p["title"], level=1)
              + f'<p class="lead">The archive is for partners: {e(ACCESS_WHO.split(": ", 1)[1])}</p>' + panels, "page-head")
    desk = sec(head("The partner’s desk", "The one place to tell us how the images are used and what you need next.")
               + note("Every answer lands in the partner database; the forms ask for organisation and email. The welcome email, the download email and a three-month check-in point here.")
               + '<div class="cards-3">'
               + f'<div class="card" id="report"><h3>Report a use</h3>{mini_form([("Where it appeared", False), ("Link", False), ("Date", False), ("What you need next", True)], "Send")}</div>'
               + f'<div class="card" id="request-imagery"><h3>Request imagery</h3><p class="small">Can’t find what you need?</p>{mini_form([("What you are looking for", True), ("For what", False), ("By when", False)], "Send")}</div>'
               + f'<div class="card" id="working-on"><h3>What are you working on?</h3>{mini_form([("Your project", True), ("Link", False)], "Send")}</div>'
               + "</div>", sid="desk")
    call = sec('<div class="card call-card" id="call"><div><h3>Talk to us</h3>'
               + note("Optional, never required: a short call about what is missing and what you are working on.")
               + lines(2) + f'</div>{dead_button("Book a feedback call", quiet=True)}</div>', "tight")
    news_cards = "".join(f'<div class="example">{img("News image", "3/2")}{ph_text("Date")}{lines(2)}</div>' for _ in range(3))
    news = sec(head("Partner news")
               + note("News for partners and the numbers as they grow; aggregates and consented examples only. Shown once there is something to show.")
               + numbers([("—", "partners"), ("—", "images downloaded"), ("—", "uses reported")])
               + f'<div class="cards-3">{news_cards}</div>', sid="news")
    rules = sec(head("Using the images")
                + f'<p>One download is one licence, for the use you state. Credit every use, never change what an image shows, and tell us where the images appear.</p>'
                + doors(button(base + "partners/#using-the-images", "All the rules", quiet=True),
                        button(archive("/client", "portal-history"), "Your download history", quiet=True)), "band", sid="rules")
    # Page priorities: the gate, report a use, request imagery and what you are working on, news, the rules, a feedback call
    return top + desk + news + rules + call


def tpl_form(p, base):
    fields = [("Organisation", "text"), ("Your role", "text"), ("Type of organisation", "select"), ("Country", "text"), ("Focus of your work", "text"),
              ("How you will use the images", "textarea"), ("What imagery you are looking for", "textarea"), ("Email", "email")]
    rows = []
    for i, (label, kind) in enumerate(fields):
        fid = f"f{i}"
        if kind == "select":
            ctl = (f'<select id="{fid}" disabled><option>NGO</option><option>Media</option><option>Educational institution</option>'
                   f'<option>Embassy or ministry</option><option>Development finance institution</option><option>Company</option></select>')
        elif kind == "textarea":
            ctl = f'<textarea id="{fid}" rows="3" disabled></textarea>'
        else:
            ctl = f'<input id="{fid}" type="{kind}" disabled>'
        rows.append(f'<label for="{fid}">{e(label)}</label>{ctl}')
    rows.append('<label class="check"><input type="checkbox" disabled> I agree that how we use the images may be reported, '
                'without personal details, to the funders who make new collections possible.</label>')
    form = (f'<form class="form" aria-label="Request access (not connected yet)">{"".join(rows)}'
            f'<button type="button" class="button" disabled>Send the request</button></form>'
            f'<p class="small">Read <a href="{base}partners/#using-the-images">the rules for using the images</a> first. '
            f'Until this form is connected, requests go through <a href="{archive("/contact", "request")}">the archive’s request form</a>.</p>')
    aside = ('<aside class="facts-box">' + head("What happens next", level=3)
             + '<ol class="next-steps"><li>We read your request.</li><li>You get a welcome email.</li><li>You log in, collect in the Lightbox and download for each use.</li></ol>'
             + note("How soon we answer: to decide. Companies are answered with the sponsorship route.") + "</aside>")
    return (sec(head(p["title"], level=1) + f'<p class="lead">{e(ACCESS_WHO)} {e(ACCESS_COMPANIES)}</p>', "page-head")
            + sec(f'<div class="grid-2">{"<div>" + form + "</div>"}{aside}</div>', "tight")
            + sec('<div class="card thanks">' + head("Thank you", level=3) + lines(2) + '</div>'
                  + note("The thank-you state, shown in place of the form after sending: what happens next and how soon.")))


def tpl_press(p, base):
    facts = ('<ul class="list">'
             '<li>1,122 images in the House Collection, from Mali, Kenya and The Gambia</li>'
             '<li>Five themes: Learning, Work and enterprise, Everyday digital, City life, Creativity and culture</li>'
             '<li>Free for selected non-profit and public partners</li>'
             '<li>An independent initiative established by Commerce & Culture</li>'
             '<li>Our images are never AI-generated</li></ul>')
    top = sec(head(p["title"], "Stories, images for editorial use, and someone to talk to.", level=1), "page-head")
    release = sec(f'<div class="split">{img("Press image for the relaunch", "3/2")}<div>'
                  + head("The relaunch", kicker="Press release")
                  + note("From the Strategic Platform’s draft text, with date and quotes from named people who agreed to them.")
                  + lines(3) + doors(dead_button("Download the release (PDF)", quiet=True)) + "</div></div>", "tight")
    factsheet = sec('<div class="grid-2"><div>' + head("Fact sheet") + facts + "</div><div>" + head("Track record")
                    + note("Exhibitions and collaborations since 2010, as history.") + lines(4) + "</div></div>")
    pressset = sec(head("Press images")
                   + note("A curated set for editorial use with the credit line; no images with minors. Open download or through media access: to decide.")
                   + sample_grid(6, "Press image") + doors(dead_button("Download the press set", quiet=True)))
    leads = "".join(f'<div class="example">{img("Image from the series", "3/2")}<h3>{e(s)}</h3>{lines(2)}{ph_text("Series · place · who to talk to")}</div>'
                    for s in GAMBIA_SERIES)
    leads_sec = sec(head("Story leads") + note("Each lead in two sentences, with the series, the place and who to talk to.")
                    + f'<div class="cards-2">{leads}</div>')
    kit = sec(head("Logos and portrait") + '<div class="cards-3">'
              + f'<div class="example"><div class="logo-tile"><img src="{base}assets/logo.png" alt="Africa Reframed logo"></div><p class="small">Logo, white on black</p></div>'
              + f'<div class="example">{img("Logo, black on white", "3/2")}<p class="small">Logo, black on white</p></div>'
              + f'<div class="example">{img("Portrait: Thomas Damgaard", "3/2")}<p class="small">Portrait</p></div></div>')
    contact = sec(head("Press contact") + f'<p class="h-big"><a href="mailto:{EMAIL_PRESS}">{EMAIL_PRESS}</a></p>', "band")
    return top + release + factsheet + pressset + leads_sec + kit + contact


def tpl_text(p, base):
    k = p["slug"]
    if k == "about":
        principles = ["Real images, never AI-generated", "Consent and releases", "Photographers credited", "Fair terms",
                      "Editorial independence"]
        pr = "".join(f'<div class="card"><h3>{e(x)}</h3>{lines(2)}</div>' for x in principles)
        legacy = [("Since 2010", "Exhibitions and collaborations"), ("2014–2017", "Afghan Tales"),
                  ("2016", "Africa Reframed at Øksnehallen"), ("", "Artist collaborations")]
        lg = "".join(f'<div class="example">{img("Archive image", "3/2")}<p class="kicker">{e(y)}</p><h3>{e(t)}</h3>{lines(2)}</div>'
                     for y, t in legacy)
        return (sec(head(p["title"], ABOUT_LINE, level=1), "page-head")
                + sec(f'<div class="split">{img("Portrait: Thomas Damgaard", "4/5")}<div>' + head("Who is behind it")
                      + note("Commerce & Culture and Thomas Damgaard: who runs the initiative and why.") + lines(4) + "</div></div>", "tight")
                + sec(head("Principles") + note("How the images are made and used.") + f'<div class="cards-5">{pr}</div>')
                + sec(head("Legacy") + note("History, as proof behind the present.") + f'<div class="cards-4">{lg}</div>')
                + sec(head("How it is run") + note("A non-commercial initiative, administered through KKArt; no licensing sales; surplus funds new collections.")
                      + lines(2), "band"))
    if k == "contact":
        return sec(head(p["title"], level=1)
                   + f'<p class="h-big"><a href="mailto:{EMAIL_MAIN}">{EMAIL_MAIN}</a></p>'
                   + note("A link to Africa Reframed on LinkedIn.")
                   + f'<p class="small">Press: <a href="mailto:{EMAIL_PRESS}">{EMAIL_PRESS}</a> · '
                     f'Partnerships: <a href="mailto:{EMAIL_PARTNERS}">{EMAIL_PARTNERS}</a></p>', "page-head")
    parts = [("What we collect", "Organisation, contact details, intended use and the answers you give in the partner forms."),
             ("Why", "To approve access, keep in touch, and report how the images are used, without personal details, to the funders who make new collections possible, with your consent."),
             ("How long, and your rights", "How long we keep it, and how to see, change or delete it."),
             ("Contact", "Who to write to about your data, and how.")]
    body = "".join(sec(head(h) + note(n) + lines(3), "tight") for h, n in parts)
    return sec(head(p["title"], "What we collect when you request access or write to us, and why.", level=1), "page-head") + body


TEMPLATES = {"home": tpl_home, "themes": tpl_index_themes, "collections": tpl_index_collections, "theme": tpl_theme,
             "collection": tpl_collection, "partners": tpl_partners, "portal": tpl_portal, "form": tpl_form,
             "press": tpl_press, "text": tpl_text}

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
         desc=HOUSE_LINE),
    dict(path="partners/", title="Partners", slug="partners", tpl="partners", nav="partners",
         desc="How organisations use the Africa Reframed archive, the rules for using the images, and how companies sponsor a collection."),
    dict(path="partner-portal/", title="Partner portal", slug="portal", tpl="portal", nav="portal",
         desc="Log in to the Africa Reframed archive, report a use, request imagery and see what is new for partners."),
    dict(path="request-access/", title="Request access", slug="request", tpl="form", nav=None,
         desc="Request access to the Africa Reframed archive: free for selected non-profit and public partners."),
    dict(path="about/", title="About", slug="about", tpl="text", nav=None, desc=ABOUT_LINE),
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
                 ("Step 1: the grid, the module list and the header test", "next",
                  "The grid's values in the code with the overlay (below); the module list, Website – modules; what PhotoDeck's Custom CSS/HTML can carry"),
                 ("Step 2: low-resolution modules and the story mockup", "later",
                  "The wireframe rebuilt from the modules, every module at /dev/modules, the five key pages with draft copy, the phone first"),
                 ("Step 3: the look", "later", "The open visual questions in Claude Design canvases: the Opening, the close, the yellow and the black sections"),
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
    ("Copy written for every note", "{notes} notes open"),
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


def page_stats(main):
    return dict(notes=main.count('class="note"'), images=main.count('class="img'), bars=main.count('class="lines"'))


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
    tot = {k: sum(r["stats"][k] for r in rows) for k in ("notes", "images", "bars")}
    body = "".join(
        f'<tr><td><a href="{base}{r["path"]}">{e(r["title"])}</a></td><td class="mono">/{e(r["path"])}</td>'
        f'<td>{e(TEMPLATE_NAMES[r["tpl"]])}</td><td>{stepper(r["slug"])}</td>'
        f'<td class="n">{r["stats"]["notes"]}</td><td class="n">{r["stats"]["images"]}</td><td class="n">{r["stats"]["bars"]}</td></tr>'
        for r in rows)
    inventory = (f'<div class="table-scroll"><table class="dev-table"><thead><tr><th>Page</th><th>Address</th><th>Template</th>'
                 f'<th>State</th><th class="n">Notes</th><th class="n">Images to choose</th><th class="n">Text to write</th></tr></thead>'
                 f'<tbody>{body}</tbody><tfoot><tr><td colspan="4">{len(rows)} pages from {len(set(TEMPLATE_NAMES[r["tpl"]] for r in rows))} templates</td>'
                 f'<td class="n">{tot["notes"]}</td><td class="n">{tot["images"]}</td><td class="n">{tot["bars"]}</td></tr></tfoot></table></div>')
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
            + sec(head("Pages", "Every page, its template and its state. The counts are what is still to fill: yellow notes, image boxes and text bars.")
                  + inventory)
            + sec(head("How to read the wireframe")
                  + '<ul class="dev-list"><li><strong>Grey box with a cross</strong><span>An image still to choose, at the size and proportion it will have.</span></li>'
                    '<li><strong>Grey bars</strong><span>Text still to write.</span></li>'
                    '<li><strong>Yellow note</strong><span>What goes there, and where it comes from.</span></li>'
                    '<li><strong>Clean view</strong><span>In the yellow strip: hides the notes and labels, so a page can be shown as a layout.</span></li>'
                    '<li><strong>Grid</strong><span>In the yellow strip, or the key G, or ?grid in the address: draws the columns (blue) and margins (red) of the current width, with the values in a readout.</span></li></ul>')
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
      <img src="{base}assets/logo.png" alt="Africa Reframed" class="brand-logo">
    </a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
    <nav class="menu" id="menu" aria-label="Main">
      <a href="{base}themes/"{cur_themes}>Themes</a>
      <a href="{base}collections/"{cur_collections}>Collections</a>
      <a href="{base}partners/"{cur_partners}>Partners</a>
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
.c1-4{grid-column:1/5}.c6-12{grid-column:6/-1}.c1-12{grid-column:1/-1}
.c5-off{grid-column:5/-1;margin-right:var(--off-edge)}
.bleed{width:100vw;margin-left:calc(50% - 50vw);max-width:none}
.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:8px;background:var(--accent);color:var(--ink);padding:8px 12px;z-index:20}
:focus-visible{outline:2px solid var(--ink);outline-offset:2px}

/* Header: logo left, one flat menu right, as on the archive (keep pixel-identical to PhotoDeck) */
.site-header{background:var(--ground);color:var(--text-on-dark)}
/* On the grid: the logo's left edge on the line of column 1, the menu's right edge on the right edge of column 12;
   the height and the logo width are the grid's header values (the header turns white in step 4) */
.bar{display:flex;align-items:center;justify-content:space-between;gap:24px;min-height:var(--header-h)}
.brand{display:inline-flex;align-items:center}
.brand-logo{width:var(--logo-w);height:auto;display:block}
.menu{display:flex;align-items:center;gap:22px;font-size:15px}
.menu a{padding:6px 0;border-bottom:2px solid transparent;color:var(--text-on-dark);white-space:nowrap;text-decoration:none}
.menu a:hover{color:#fff}
.menu a[aria-current="page"]{color:#fff;border-bottom-color:var(--accent)}
.divider{display:inline-block;width:1px;height:18px;background:rgba(227,227,227,.4);margin:0 4px}
.menu-toggle{display:none;background:none;border:0;padding:8px;cursor:pointer;width:44px;height:44px;flex-direction:column;justify-content:center;gap:5px}
.menu-toggle span{display:block;height:2px;background:var(--text-on-dark)}
.menu-toggle:focus-visible{outline-color:var(--accent)}

/* The wireframe strip */
.wire-strip{background:var(--accent);color:var(--ink);font-size:13px;padding:6px 0}
.wire-strip .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px}
.strip-tools{display:flex;align-items:center;gap:14px;white-space:nowrap}
.strip-tools a{color:var(--ink)}
.notes-toggle{font:inherit;font-size:13px;background:transparent;border:1px solid rgba(21,21,21,.4);border-radius:3px;padding:3px 10px;cursor:pointer;white-space:nowrap;color:var(--ink)}

/* Wireframe parts */
.img{position:relative;width:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:2px;
  background:
    linear-gradient(to top right,transparent calc(50% - .7px),var(--wire-line) calc(50% - .7px),var(--wire-line) calc(50% + .7px),transparent calc(50% + .7px)),
    linear-gradient(to bottom right,transparent calc(50% - .7px),var(--wire-line) calc(50% - .7px),var(--wire-line) calc(50% + .7px),transparent calc(50% + .7px)),
    var(--wire)}
.img span{background:var(--wire);color:#6b6862;font-size:12px;line-height:1.35;padding:4px 8px;max-width:80%;text-align:center;border-radius:2px}
.img.dark{background:
    linear-gradient(to top right,transparent calc(50% - .7px),#454545 calc(50% - .7px),#454545 calc(50% + .7px),transparent calc(50% + .7px)),
    linear-gradient(to bottom right,transparent calc(50% - .7px),#454545 calc(50% - .7px),#454545 calc(50% + .7px),transparent calc(50% + .7px)),
    #2a2a2a}
.img.dark span{background:#2a2a2a;color:#a9a6a0}
.note{display:block;width:fit-content;max-width:62ch;font-size:13px;line-height:1.45;background:#fff8c2;border-left:3px solid #e0cf3c;padding:6px 10px;color:#4b4943;margin:4px 0 16px}
.lines{max-width:60ch;margin:8px 0 16px}
.lines i{display:block;height:10px;background:var(--bar);border-radius:2px;margin:0 0 12px}
.lines i:last-child{width:62%}
.ph-text{color:#9a978f;font-style:italic;font-size:14px;margin:0 0 8px}
body.clean .note,body.clean .img span{display:none}

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
.card{border:1px solid var(--line);border-radius:6px;padding:20px;background:#fff}
.card h3{margin-top:0}
.example .img{margin-bottom:10px}

/* Buttons */
.doors{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0 12px}
.button{display:inline-flex;align-items:center;min-height:44px;padding:0 20px;background:var(--accent);color:var(--ink);font:inherit;font-weight:500;font-size:15px;border-radius:3px;border:0;text-decoration:none;cursor:pointer}
.button.quiet{background:transparent;border:1px solid #c9c6bf;color:var(--ink)}
.button[disabled],.button.dead{opacity:.55;cursor:not-allowed}

/* Home: the Opening on the grid (the third photograph case). The photograph starts on the line of column 5 and runs off
   the right edge; the words stand on white in columns 1–4. Proportions after the guide's hero at 1440 × 720: under the
   128 px header the photograph is 928 × 512 (29:16) with 80 px of white below it; the words start 160 px below the header.
   The stripes and triangles are drawn in step 3; here only the geometry. */
.opening{overflow-x:hidden;padding-bottom:80px}
.opening .wrap{row-gap:24px}
.opening-words{padding-top:160px}
.opening-words h1{font-size:40px;max-width:none}
.opening-img{aspect-ratio:29/16;max-height:80vh;border-radius:0}
.opening-img span{position:absolute;top:16px;left:16px;max-width:60%}
.intro{padding-top:48px}
.intro-num{padding-top:8px}
.numbers{display:flex;flex-wrap:wrap;gap:16px 44px;margin:8px 0}
.num b{display:block;font-size:44px;font-weight:500;line-height:1;font-variant-numeric:tabular-nums}
.num span{font-size:14px;color:var(--ink-soft)}
.theme-row{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px;margin-top:20px}
.theme-card{display:flex;flex-direction:column;text-decoration:none;scroll-snap-align:start}
.theme-card h3{margin:4px 0 6px}
.theme-card p{font-size:15px;color:var(--ink-soft);margin:0 0 8px}
.order{font-size:13px;color:var(--ink-soft);font-variant-numeric:tabular-nums;margin-top:12px}
.count{font-size:13px;font-weight:500;margin-top:auto}
.theme-card:hover h3,.theme-line:hover h2{text-decoration:underline}
.logos{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px;margin:8px 0 32px}
.logo{aspect-ratio:5/2;border:1px dashed #c9c6bf;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:12px;color:#8a877f}

/* Themes index */
.theme-line{display:grid;grid-template-columns:72px 1fr 1.3fr;gap:32px;align-items:center;padding:28px 0;border-top:1px solid var(--line);text-decoration:none}
.theme-line h2{margin:0 0 8px}
.theme-line p{color:var(--ink-soft);margin:0 0 8px}
.order.big{font-size:40px;line-height:1;margin:0;color:var(--ink)}
.strip3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}

/* Theme and collection pages */
.wide{max-height:62vh}
.sample-grid{columns:4;column-gap:14px;margin-top:8px}
.sample-grid .img{margin-bottom:14px;break-inside:avoid}
.action{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px 32px}
.action .doors{margin:0}
.theme-nav{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.theme-nav a{display:flex;flex-direction:column;gap:4px;text-decoration:none}
.theme-nav .img{margin-bottom:8px}
.theme-nav .dir{font-size:13px;color:var(--ink-soft)}
.theme-nav strong{font-weight:500;font-size:20px}
.facts-box{border:1px solid var(--line);border-radius:6px;padding:24px;background:#fff}
.facts{display:grid;grid-template-columns:auto 1fr;gap:8px 20px;font-size:15px;margin:0 0 16px}
.facts dt{color:var(--ink-soft)}
.facts dd{margin:0}
.place h3{margin-top:12px}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chip{border:1px solid #c9c6bf;border-radius:999px;padding:8px 16px;text-decoration:none;font-size:15px}
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
.door-panels{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:28px}
.panel{display:flex;flex-direction:column;justify-content:flex-end;gap:6px;min-height:200px;padding:28px;border:1px solid #c9c6bf;border-radius:6px;text-decoration:none}
.panel strong{font-size:30px;font-weight:500;line-height:1.15}
.panel span:last-child{font-size:15px;color:var(--ink-soft)}
.panel.dark{background:var(--ground);border-color:var(--ground);color:#fff}
.panel.dark strong{color:var(--accent)}
.panel.dark .kicker,.panel.dark span:last-child{color:#bdbab3}
.panel:hover strong{text-decoration:underline}
.mini-form{display:flex;flex-direction:column;gap:4px}
.f-label{font-size:13px;color:var(--ink-soft);margin-top:6px}
.field{display:block;height:38px;border:1px solid #d6d3cc;border-radius:3px;background:#fff}
.field.tall{height:76px}
.mini-form .button,.card .button{align-self:flex-start;margin-top:14px}
.call-card{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 32px}
.call-card .button{margin-top:0;align-self:center}
.logo-tile{background:var(--ground);aspect-ratio:3/2;display:flex;align-items:center;justify-content:center;border-radius:2px;margin-bottom:10px}
.logo-tile img{width:62%}

/* Form */
.form{display:grid;gap:6px;max-width:560px;margin:8px 0 16px}
.form label{font-size:14px;font-weight:500;margin-top:10px}
.form input,.form select,.form textarea{font:inherit;padding:10px 12px;border:1px solid #c9c6bf;border-radius:4px;background:#fff}
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
.stepper span{font-size:11px;padding:2px 6px;border-radius:3px;background:var(--wash);color:#9a978f}
.stepper span.done{background:#e3e1dc;color:var(--ink)}
.stepper span.on{background:var(--ink);color:#fff}
.dev-list{list-style:none;padding:0;margin:8px 0 0;max-width:900px}
.dev-list li{display:grid;grid-template-columns:minmax(0,260px) 1fr;gap:4px 24px;padding:12px 0;border-top:1px solid var(--line)}
.dev-list li > span:last-child{color:var(--ink-soft)}
.dev-list .where{font-size:12px;color:#8a877f}
.dev-list li:has(.tag){grid-template-columns:64px minmax(0,300px) 1fr}
.dev-list li:has(.where){grid-template-columns:minmax(0,300px) 140px 1fr}
.tag{display:inline-block;font-size:11px;letter-spacing:.04em;padding:2px 7px;border-radius:3px;height:fit-content;width:fit-content}
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
.grid-read{position:absolute;left:0;right:0;bottom:16px;width:fit-content;background:rgba(21,21,21,.9);color:#fff;font-size:12px;line-height:1.4;padding:6px 10px;border-radius:3px;font-variant-numeric:tabular-nums}
.grid-toggle{font:inherit;font-size:13px;background:transparent;border:1px solid rgba(21,21,21,.4);border-radius:3px;padding:3px 10px;cursor:pointer;white-space:nowrap;color:var(--ink)}
.grid-toggle[aria-pressed="true"],.notes-toggle[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}

/* Tablet (768–1,023 px): 8 columns, 24 px gutters, 32 px margins; the menu folds, like the archive's below tablet width */
@media (max-width:1023px){
  :root{--cols:8;--gutter:24px;--margin:32px;--section:80px;--section-head:56px;--section-tight:28px}
  .menu-toggle{display:flex}
  .menu{display:none;position:absolute;left:0;right:0;top:var(--header-h);background:var(--ground);flex-direction:column;align-items:flex-start;gap:0;padding:8px var(--margin) 24px;border-top:1px solid rgba(227,227,227,.15);z-index:10}
  .menu.open{display:flex}
  .menu a{padding:12px 0;font-size:17px;width:100%}
  .divider{width:100%;height:1px;margin:8px 0}
  .site-header{position:relative}
  .c1-4{grid-column:1/4}.c6-12{grid-column:4/-1}
  .grid-overlay .col.col-5{background:rgba(40,110,220,.10)}.grid-overlay .col.col-2{background:rgba(40,110,220,.16)}
  .wire-strip .wrap{flex-wrap:wrap}
  .theme-row{grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:minmax(220px,40%);overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:8px}
  .cards-4,.cards-5,.principles{grid-template-columns:repeat(2,minmax(0,1fr))}
  .sample-grid{columns:3}
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
  h1{font-size:34px}
  h2{font-size:24px}
  .statement{font-size:20px}
  .c1-4,.c6-12{grid-column:1/-1}
  .opening-img{aspect-ratio:4/5}
  .opening-words h1{font-size:30px}
  .grid-2,.split,.door-panels,.steps,.theme-nav,.cards-2,.cards-3{grid-template-columns:1fr}
  .grid-2{gap:32px}
  .split{gap:20px}
  .theme-line{grid-template-columns:44px 1fr;gap:12px 16px}
  .theme-line .strip3{grid-column:1 / -1}
  .order.big{font-size:28px}
  .sample-grid{columns:2;column-gap:10px}
  .sample-grid .img{margin-bottom:10px}
  .contact-box{margin-top:0}
  .panel{min-height:132px;padding:22px}
  .dev-list li,.dev-list li:has(.tag),.dev-list li:has(.where){grid-template-columns:1fr}
  .strip-tools{gap:10px}
  .theme-row{grid-auto-columns:78%}
}
@media (max-width:480px){
  .cards-4,.cards-5,.principles{grid-template-columns:1fr}
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
            f'<a href="{base}dev/">Development</a>'
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
        cur_themes=cur("themes"), cur_collections=cur("collections"), cur_partners=cur("partners"), cur_portal=cur("portal"))


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
    (ROOT / ".nojekyll").write_text("")
    print("built", len(PAGES), "pages" + ("" if LAUNCH else " and /dev/"), "into", ROOT)


if __name__ == "__main__":
    build()
