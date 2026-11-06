#!/usr/bin/env python3
"""Generate the Africa Reframed main site as a live wireframe (version 3, 6 November 2026).

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
import time
from urllib.parse import quote

ROOT = pathlib.Path(__file__).parent.parent
ARCHIVE = "https://archive.africareframed.com"
SITE_URL = "https://africareframed.github.io/africareframed-site/"   # becomes https://africareframed.com/ at launch
STAMP = time.strftime("%Y%m%d%H%M")
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
            '<li><strong>What for.</strong> The use you state at download: reports, applications, exhibitions, the press, presentations and your own channels. Free of charge.</li>'
            '<li><strong>Credit.</strong> The credit line on every use, as given with each image.</li>'
            '<li><strong>Editing.</strong> Cropping, resizing and colour are fine; changing what an image shows is not, and neither is altering images with AI or using them to train AI.</li>'
            '<li><strong>The people portrayed.</strong> Accurate captions and contexts they would recognise; never a degrading or misleading one, and never presenting the images as your own operations or results.</li>'
            '<li><strong>No resale.</strong> No resale, sublicensing or use as a logo.</li>'
            '<li><strong>Tell us where they appear.</strong> Report a use through the Partner portal.</li>'
            '</ol>')


# ---------------------------------------------------------------------------------------------
# The nine templates (each returns the inside of <main>)
# ---------------------------------------------------------------------------------------------
def tpl_home(p, base):
    hero = (f'<section class="hero-full">{img("Opening image · one real image at full width · released, no minors", None, dark=True, cls="hero-img")}'
            f'<div class="hero-text"><div class="wrap"><h1>{e(CORE_LINE)}</h1></div></div></section>')
    intro = sec(f'<div class="grid-2"><div>'
                + note("Two or three sentences: what Africa Reframed is, who it is for and who is behind it. A funder checking us gets it here, in the first screen.")
                + lines(3)
                + doors(button(base + "themes/", "Explore the themes"), button(base + "request-access/", "Request access", quiet=True))
                + f'</div><div class="intro-num">{numbers()}</div></div>', "intro")
    cards = "".join(theme_card(t, base, i) for i, t in enumerate(THEMES, 1))
    themes = sec(head("Five themes", THEMES_LEAD) + f'<div class="theme-row">{cards}</div>')
    coll = sec(head("Collections") + house_split(base))
    partners = sec(head("Partners")
                   + note("The organisations using the archive, by name, with their consent; one published example of use. The first partners are on board before launch.")
                   + logos()
                   + f'<div class="split">{img("Example of use: a report, an exhibition or an article", "3/2")}<div>'
                   + lines(3) + ph_text("Partner · where it appeared · when")
                   + doors(button(base + "partners/", "How partners use the archive", quiet=True)) + "</div></div>")
    return hero + intro + themes + coll + partners


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
    return top + lead_img + samples + action + nav


def tpl_collection(p, base):
    facts = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in HOUSE_FACTS)
    top = sec(f'<p class="kicker">Collection</p><h1>House Collection</h1><p class="statement">{e(HOUSE_STATEMENT)}</p>', "page-head")
    hero = sec(img("Collection image", "21/9", cls="wide"), "tight")
    story = sec('<div class="grid-2"><div>' + head("The story")
                + note("How the collection was made, where and with whom. Written as history and proof, in the present tense of the archive.")
                + lines(6) + '</div><aside class="facts-box">'
                + f'<dl class="facts">{facts}</dl>'
                + note("Photographers and workshop partners, credited as they agree.") + lines(2) + "</aside></div>")
    places = []
    for country in ("Mali", "Kenya", "The Gambia"):
        series = ('<ul class="list">' + "".join(f"<li>{e(s)}</li>" for s in GAMBIA_SERIES) + "</ul>") if country == "The Gambia" else ""
        places.append(f'<div class="place">{img("Image from " + country, "3/2")}<h3>{e(country)}</h3>{series}{lines(2)}</div>')
    places_sec = sec(head("Places and series") + note("Series by name and place, as the shoot list gives them.")
                     + f'<div class="cards-3">{"".join(places)}</div>')
    samples = sec(head("From the collection") + note("A spread across the five themes. " + PUBLIC_SAMPLE) + sample_grid())
    chips = "".join(f'<a class="chip" href="{base}themes/{t["slug"]}/">{e(t["name"])}</a>' for t in THEMES)
    feeds = sec(head("Themes it feeds") + f'<div class="chips">{chips}</div>')
    action = sec(f'<div class="action"><div class="num"><b>1,122</b><span>images in the House Collection</span></div>'
                 + doors(button(archive("/-/galleries/archive", "collection-house"), "Open in the archive →"),
                         button(base + "partners/", "How partners use the archive", quiet=True)) + "</div>", "band")
    return top + hero + story + places_sec + samples + feeds + action


def tpl_partners(p, base):
    top = sec(head(p["title"], "How organisations use the archive, who already does, and how to work with us.", level=1), "page-head")
    use = sec(head("Use the images") + f"<p>{e(ACCESS_WHO)}</p>"
              + steps([("Request access", "Tell us who you are and how you will use the images."),
                       ("Approved by name", "We approve each organisation by name."),
                       ("Search and download", "Find what you need and download it under the free partner licence.")])
              + note("What we ask in return: report a use, and a yearly question about what you are working on.")
              + doors(button(base + "request-access/", "Request access")), sid="use")
    rules = sec(head("Using the images", "The rules for use in plain language. Read them before you apply.") + rules_list()
                + f'<p class="small">Draft, to be checked against the licence; <a href="{ARCHIVE}/terms">Terms</a> on the archive is the legal text.</p>',
                "band", sid="using-the-images")
    examples = "".join(f'<div class="example">{img("Example of use", "3/2")}{lines(2)}{ph_text("Partner · where it appeared · when")}</div>' for _ in range(3))
    inuse = sec(head("Partners using the archive") + note("Organisations by name and published uses, with their consent.")
                + logos(10) + f'<div class="cards-3">{examples}</div>', sid="partners")
    work = sec('<div class="grid-2"><div>' + head("Work with us") + f"<p>{e(ACCESS_COMPANIES)}</p>"
               + note("In general terms: we make new collections with sponsors, opening new themes or deepening existing ones, each with its own collection page and credit. The specific offers belong in conversation, not on the site.")
               + lines(2) + f'</div><div class="contact-box"><p class="kicker">Partnerships</p>'
               f'<p class="h-big"><a href="mailto:{EMAIL_PARTNERS}">{EMAIL_PARTNERS}</a></p></div></div>', sid="work-with-us")
    return top + use + rules + inuse + work


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
               + '<div class="cards-4">'
               + f'<div class="card" id="report"><h3>Report a use</h3>{mini_form([("Where it appeared", False), ("Link", False), ("Date", False), ("What you need next", True)], "Send")}</div>'
               + f'<div class="card" id="request-imagery"><h3>Request imagery</h3>{mini_form([("What you are looking for", True), ("For what", False), ("By when", False)], "Send")}</div>'
               + f'<div class="card" id="working-on"><h3>What are you working on?</h3>{mini_form([("Your project", True), ("Link", False)], "Send")}</div>'
               + f'<div class="card" id="call"><h3>Talk to us</h3>{lines(3)}{note("Optional, never required: a short call about what is missing and what you are working on.")}{dead_button("Book a feedback call", quiet=True)}</div>'
               + "</div>", sid="desk")
    news_cards = "".join(f'<div class="example">{img("News image", "3/2")}{ph_text("Date")}{lines(2)}</div>' for _ in range(3))
    news = sec(head("Partner news")
               + note("News for partners and the numbers as they grow; aggregates and consented examples only. Shown once there is something to show.")
               + numbers([("—", "partners"), ("—", "images downloaded"), ("—", "uses reported")])
               + f'<div class="cards-3">{news_cards}</div>', sid="news")
    rules = sec(head("Using the images")
                + f'<p>Credit every use, never change what an image shows, and tell us where the images appear.</p>'
                + doors(button(base + "partners/#using-the-images", "All the rules", quiet=True),
                        button(archive("/client", "portal-history"), "Your download history", quiet=True)), "band", sid="rules")
    return top + desk + news + rules


def tpl_form(p, base):
    fields = [("Organisation", "text"), ("Type of organisation", "select"), ("Country", "text"), ("Focus of your work", "text"),
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
             + '<ol class="next-steps"><li>We read your request.</li><li>You get a welcome email.</li><li>You log in and download.</li></ol>'
             + note("How soon we answer: to decide. Companies are answered with the sponsorship route.") + "</aside>")
    return (sec(head(p["title"], level=1) + f'<p class="lead">{e(ACCESS_WHO)} {e(ACCESS_COMPANIES)}</p>', "page-head")
            + sec(f'<div class="grid-2">{"<div>" + form + "</div>"}{aside}</div>', "tight"))


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
             ("How long, and your rights", "How long we keep it, and how to see, change or delete it.")]
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
         desc="How organisations use the Africa Reframed archive, the rules for using the images, and how to work with us."),
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
# Layout
# ---------------------------------------------------------------------------------------------
LAYOUT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{doc_title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex">
<link rel="canonical" href="{url}">
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
<div class="wire-strip"><div class="wrap">
  <span>Live wireframe · grey boxes are images to choose · grey bars are text to write · yellow notes say what goes there</span>
  <button class="notes-toggle" type="button" aria-pressed="false">Clean view</button>
</div></div>
<main id="main">
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
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font);font-size:16px;line-height:1.55}
a{color:inherit}
.wrap{max-width:1280px;margin:0 auto;padding:0 32px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:8px;background:var(--accent);color:var(--ink);padding:8px 12px;z-index:20}
:focus-visible{outline:2px solid var(--ink);outline-offset:2px}

/* Header: logo left, one flat menu right, as on the archive (keep pixel-identical to PhotoDeck) */
.site-header{background:var(--ground);color:var(--text-on-dark)}
.bar{display:flex;align-items:center;justify-content:space-between;gap:24px;min-height:84px}
.brand{display:inline-flex;align-items:center}
.brand-logo{height:40px;width:auto;display:block}
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
p{margin:0 0 12px;max-width:68ch}
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

/* Sections */
main{padding-bottom:96px}
.sec{padding-top:72px}
.sec.page-head{padding-top:56px}
.sec.tight{padding-top:28px}
.sec.band{background:var(--wash);padding:48px 0;margin-top:72px}
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

/* Home */
.hero-full{position:relative}
.hero-img{aspect-ratio:16/7;max-height:78vh;border-radius:0}
.hero-img span{position:absolute;top:16px;right:16px}
.hero-text{position:absolute;left:0;right:0;bottom:0;padding-bottom:48px}
.hero-text h1{color:#fff;font-size:58px;max-width:15ch;margin:0}
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

/* Footer */
.site-footer{border-top:1px solid var(--line);padding:32px 0 48px;color:var(--ink-soft);font-size:14px}
.site-footer p{margin:0 0 8px;max-width:none}
.site-footer a{color:var(--ink)}
.about-line{color:var(--ink)}

/* Below tablet width: hamburger, like the archive */
@media (max-width:1023px){
  .menu-toggle{display:flex}
  .menu{display:none;position:absolute;left:0;right:0;top:84px;background:var(--ground);flex-direction:column;align-items:flex-start;gap:0;padding:8px 32px 24px;border-top:1px solid rgba(227,227,227,.15);z-index:10}
  .menu.open{display:flex}
  .menu a{padding:12px 0;font-size:17px;width:100%}
  .divider{width:100%;height:1px;margin:8px 0}
  .site-header{position:relative}
  .wrap{padding:0 24px}
  .theme-row{grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:minmax(220px,40%);overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:8px}
  .cards-4,.cards-5{grid-template-columns:repeat(2,minmax(0,1fr))}
  .sample-grid{columns:3}
  .hero-text h1{font-size:44px}
}
@media (max-width:767px){
  h1{font-size:34px}
  h2{font-size:24px}
  .statement{font-size:20px}
  .sec{padding-top:56px}
  .sec.page-head{padding-top:40px}
  .hero-img{aspect-ratio:4/5}
  .hero-text{padding-bottom:28px}
  .hero-text h1{font-size:34px}
  .grid-2,.split,.door-panels,.steps,.theme-nav,.cards-2,.cards-3{grid-template-columns:1fr}
  .grid-2{gap:32px}
  .split{gap:20px}
  .theme-line{grid-template-columns:44px 1fr;gap:12px 16px}
  .theme-line .strip3{grid-column:1 / -1}
  .order.big{font-size:28px}
  .sample-grid{columns:2;column-gap:10px}
  .sample-grid .img{margin-bottom:10px}
  .contact-box{margin-top:0}
  .theme-row{grid-auto-columns:78%}
}
@media (max-width:480px){
  .wrap{padding:0 16px}
  .cards-4,.cards-5{grid-template-columns:1fr}
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


def build():
    (ROOT / "assets").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "site.css").write_text(CSS)
    share_image()
    for p in PAGES:
        depth = p["path"].count("/")
        base = "../" * depth if depth else "./"
        cur = lambda s: ' aria-current="page"' if p["nav"] == s else ""
        main = TEMPLATES[p["tpl"]](p, base)
        doc_title = "Africa Reframed" if p["slug"] == "home" else f'{p["title"]} · Africa Reframed'
        page = LAYOUT.format(
            doc_title=e(doc_title), og_title=e(p["title"] if p["slug"] != "home" else "Africa Reframed"),
            desc=e(p["desc"]), url=SITE_URL + p["path"], share=SITE_URL + "assets/share-default.png",
            base=base, stamp=STAMP, slug=p["slug"], tpl=p["tpl"], main=main, about_line=e(ABOUT_LINE), archive=ARCHIVE,
            cur_themes=cur("themes"), cur_collections=cur("collections"), cur_partners=cur("partners"), cur_portal=cur("portal"))
        out = ROOT / p["path"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page)
    (ROOT / ".nojekyll").write_text("")
    print("built", len(PAGES), "pages into", ROOT)


if __name__ == "__main__":
    build()
