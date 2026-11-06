#!/usr/bin/env python3
"""Generate the Africa Reframed skeleton site (version 2, 6 November 2026).

Structure from "Website – Site map and user flows" (05 Website on the Drive): 16 pages from 9 templates.
Header: Themes · Collections · Partners | Log in (Log in opens the Partner portal); the archive adds its own
tools on its side. Footer: the about line, then About · Press · Contact · Privacy · Request access · Terms.

Content rule: real words only where they already exist in the master documents (each carries its source
in a comment); everything else is a labelled placeholder saying what the section holds at launch.
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

# Who gets access: AR Archive – Status, "Who gets access, and sponsors" (Thomas, 3 Nov 2026)
ACCESS_WHO = ("The archive is free for selected non-profit and public partners: NGOs, media, educational institutions, "
              "embassies, ministries and development finance institutions.")
ACCESS_COMPANIES = ("Companies get access through a collection sponsorship: a sponsor gets the whole archive, "
                    "under the same partner licence as everyone else.")


def archive(path, src):
    """A link into the archive, tagged with where it came from."""
    sep = "&" if "?" in path else "?"
    return f"{ARCHIVE}{path}{sep}src=main-{src}"


# ---------------------------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------------------------
def ph(label, note):
    """A placeholder: what this section holds at launch, still to be written or chosen."""
    return (f'<div class="ph"><span class="ph-tag">To write</span><strong>{e(label)}</strong>'
            f'<p>{e(note)}</p></div>')


def section(title, body, sid=None, lead=None):
    a = f' id="{sid}"' if sid else ""
    lead_html = f'<p class="lead">{e(lead)}</p>' if lead else ""
    return f'<section class="block"{a}><h2>{e(title)}</h2>{lead_html}{body}</section>'


def button(href, label, quiet=False):
    return f'<a class="button{" quiet" if quiet else ""}" href="{href}">{e(label)}</a>'


def numbers():
    items = "".join(f'<div class="num"><b>{n}</b><span>{e(t)}</span></div>' for n, t in NUMBERS)
    return f'<div class="numbers">{items}</div>'


def theme_cards(base, with_numbers=True):
    out = []
    for i, t in enumerate(THEMES, 1):
        count = f'<span class="count">{t["count"]} images</span>' if with_numbers else ""
        out.append(f'<a class="theme-card" href="{base}themes/{t["slug"]}/"><span class="order">{i}</span>'
                   f'<h3>{e(t["name"])}</h3><p>{e(t["statement"])}</p>{count}'
                   f'<span class="strip" aria-hidden="true"></span></a>')
    return f'<div class="themes">{"".join(out)}</div>'


def house_card(base):
    return (f'<a class="collection-card" href="{base}collections/house-collection/">'
            f'<span class="kicker">Collection</span><h3>House Collection</h3>'
            f'<p>Africa Reframed’s own collection: 1,122 images from Mali, Kenya and The Gambia.</p>'
            f'<span class="strip" aria-hidden="true"></span></a>')


# ---------------------------------------------------------------------------------------------
# The nine templates (each returns the inside of <main>)
# ---------------------------------------------------------------------------------------------
def tpl_home(p, base):
    return "".join([
        f'<div class="hero"><h1>{e(CORE_LINE)}</h1>'
        f'<div class="hero-ph">{ph("The opening image and statement", "One real image at full width, and two or three sentences on what Africa Reframed is, who it is for and who is behind it. Answers a funder checking us in the first screen.")}</div>'
        f'{numbers()}<p class="doors">{button(base + "themes/", "Explore the themes")}{button(base + "request-access/", "Request access", quiet=True)}</p></div>',
        section("Themes", theme_cards(base), lead="Read in order, the five themes are the archive’s argument: people learn, put their skills to work, live connected lives in modern cities, and make culture."),
        section("Collections", house_card(base)),
        section("Partners", ph("Named partners", "The organisations using the archive, by name, and one or two examples of use (with consent). Planned: the first partners on board before launch.")
                + f'<p class="doors">{button(base + "partners/", "How partners use the archive", quiet=True)}</p>'),
    ])


def tpl_index_themes(p, base):
    return (f'<h1>{e(p["title"])}</h1><p class="lead">Five themes in story order, each with its point of view and the number of images behind it.</p>'
            + theme_cards(base))


def tpl_index_collections(p, base):
    return (f'<h1>{e(p["title"])}</h1>'
            f'<p class="lead">Each collection is a body of work with its own story and the people behind it.</p>'
            f'<div class="collections">{house_card(base)}</div>'
            + ph("More collections", "Sponsored collections appear here when they exist, each under its full name. Nothing planned is shown."))


def tpl_theme(p, base):
    t = p["theme"]
    n = THEMES.index(t) + 1
    nxt = THEMES[n % len(THEMES)]
    return "".join([
        f'<p class="kicker">Theme {n} of {len(THEMES)}</p><h1>{e(t["name"])}</h1>',
        f'<p class="statement">{e(t["statement"])}</p>',
        f'<div class="meta-row"><span>{t["count"]} images in the archive</span><span>House Collection</span></div>',
        ph("Sample images", "A strip of six to eight images that carry the theme, chosen under the public-sample rule: released images, no minors."),
        f'<p class="doors">{button(archive("/-/galleries/archive?search=" + quote(t["query"]), "theme-" + t["slug"]), "Open in the archive →")}'
        f'{button(base + "request-access/", "Request access", quiet=True)}</p>',
        '<p class="small">Partners open the theme in the archive; others are asked to log in or request access first.</p>',
        section("Next theme", f'<a class="next" href="{base}themes/{nxt["slug"]}/">{e(nxt["name"])} →</a>'),
    ])


def tpl_collection(p, base):
    series = '<ul class="list"><li>Culinary training, Banjul</li><li>Women in trades, Banjul</li></ul>'  # Keywording Guide, section 9
    feeds = "".join(f'<li><a href="{base}themes/{t["slug"]}/">{e(t["name"])}</a></li>' for t in THEMES)
    return "".join([
        '<p class="kicker">Collection</p><h1>House Collection</h1>',
        '<p class="statement">Africa Reframed’s own collection: 1,122 images, AR-1000 to AR-2121, made in own productions in connection with photography workshops with local partners in Mali, Kenya and The Gambia.</p>',  # Keywording Guide, section 2
        '<div class="meta-row"><span>1,122 images</span><span>21 shoots</span><span>Mali · Kenya · The Gambia</span></div>',
        ph("The story", "How the collection was made, where and with whom; the photographers and workshop partners credited as they agree. Written as history and proof, in the present tense of the archive."),
        ph("Sample images", "A strip of images across the five themes; public-sample rule: released images, no minors."),
        section("Series in the collection", series + ph("More series", "The other series by name and city, as the shoot list gives them.")),
        section("Themes it feeds", f'<ul class="list links">{feeds}</ul>'),
        f'<p class="doors">{button(archive("/-/galleries/archive", "collection-house"), "Open in the archive →")}'
        f'{button(base + "partners/", "How partners use the archive", quiet=True)}</p>',
    ])


def tpl_partners(p, base):
    rules = ('<ol class="rules">'
             '<li><strong>Who may use the images.</strong> Approved partners, one licence per organisation. The press set is for editorial use.</li>'
             '<li><strong>What for.</strong> The use you state at download: reports, applications, exhibitions, the press, presentations and your own channels. Free of charge.</li>'
             '<li><strong>Credit.</strong> The credit line on every use, as given with each image.</li>'
             '<li><strong>Editing.</strong> Cropping, resizing and colour are fine; changing what an image shows is not, and neither is altering images with AI or using them to train AI.</li>'
             '<li><strong>The people portrayed.</strong> Accurate captions and contexts they would recognise; never a degrading or misleading one, and never presenting the images as your own operations or results.</li>'
             '<li><strong>No resale.</strong> No resale, sublicensing or use as a logo.</li>'
             '<li><strong>Tell us where they appear.</strong> Report a use through the Partner portal.</li>'
             '</ol>'
             f'<p class="small">Draft, to be checked against the licence; <a href="{ARCHIVE}/terms">Terms</a> on the archive is the legal text.</p>')
    return "".join([
        f'<h1>{e(p["title"])}</h1><p class="lead">How organisations use the archive, who already does, and how to work with us.</p>',
        section("Use the images",
                f'<p>{e(ACCESS_WHO)}</p>'
                + ph("How access works", "Apply, be approved by name, then search and download for free; what we ask in return (report a use, and a yearly question about what you are working on).")
                + f'<p class="doors">{button(base + "request-access/", "Request access")}</p>', sid="use"),
        section("Using the images", rules, sid="using-the-images",
                lead="The rules for use in plain language. Read them before you apply."),
        section("Partners using the archive", ph("Named partners and examples of use", "Organisations by name and published uses, with their consent."), sid="partners"),
        section("Work with us",
                f'<p>{e(ACCESS_COMPANIES)}</p>'
                + ph("Collections with sponsors", "In general terms: we make new collections with sponsors, opening new themes or deepening existing ones, each with its own collection page and credit. The specific offers belong in conversation, not on the site.")
                + f'<p>Write to <a href="mailto:{EMAIL_PARTNERS}">{EMAIL_PARTNERS}</a>.</p>', sid="work-with-us"),
    ])


def tpl_portal(p, base):
    return "".join([
        f'<h1>{e(p["title"])}</h1>',
        f'<p class="lead">The archive is for partners: {e(ACCESS_WHO.split(": ", 1)[1])}</p>',
        f'<p class="doors big">{button(archive("/-/galleries/archive", "portal"), "Partner log in →")}'
        f'{button(base + "request-access/", "Not a partner yet? Request access", quiet=True)}</p>',
        '<p class="small">Signed in already? Partner log in takes you straight to the images.</p>',
        '<div class="desk">',
        section("Report a use", ph("Form", "Where, when, a link, and what you need next. Organisation and email. Lands in the partner database."), sid="report"),
        section("Request imagery", ph("Form: can’t find what you need?", "What you are looking for, for what, by when. Counted by theme."), sid="request-imagery"),
        section("What are you working on?", ph("Form", "The yearly spotlight question: a project you would like to put a light on."), sid="working-on"),
        section("Talk to us", ph("Book a feedback call", "Optional, never required: a short call about what is missing and what you are working on."), sid="call"),
        section("Partner news", ph("News and numbers", "News for partners, the numbers as they grow (partners, downloads, reported uses) and examples of use with consent."), sid="news"),
        '</div>',
        section("Using the images",
                f'<p>Credit every use, never change what an image shows, and tell us where the images appear. '
                f'<a href="{base}partners/#using-the-images">All the rules</a> · '
                f'<a href="{archive("/client", "portal-history")}">Your download history</a></p>', sid="rules"),
    ])


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
    return "".join([
        f'<h1>{e(p["title"])}</h1>',
        f'<p class="lead">{e(ACCESS_WHO)} {e(ACCESS_COMPANIES)}</p>',
        f'<form class="form" aria-label="Request access (not connected yet)">{"".join(rows)}'
        f'<button type="button" class="button" disabled>Send the request</button></form>',
        f'<p class="small">Read <a href="{base}partners/#using-the-images">the rules for using the images</a> first. '
        f'Until this form is connected, requests go through <a href="{archive("/contact", "request")}">the archive’s request form</a>.</p>',
        ph("What happens next", "How soon we answer, and what the welcome email contains. Companies are answered with the sponsorship route."),
    ])


def tpl_press(p, base):
    facts = ('<ul class="list">'
             '<li>1,122 images in the House Collection, from Mali, Kenya and The Gambia</li>'
             '<li>Five themes: Learning, Work and enterprise, Everyday digital, City life, Creativity and culture</li>'
             '<li>Free for selected non-profit and public partners</li>'
             '<li>An independent initiative established by Commerce & Culture</li>'
             '<li>Our images are never AI-generated</li></ul>')
    leads = '<ul class="list"><li>Culinary training, Banjul</li><li>Women in trades, Banjul</li></ul>'
    return "".join([
        f'<h1>{e(p["title"])}</h1><p class="lead">Stories, images for editorial use, and someone to talk to.</p>',
        section("The relaunch", ph("Press release", "The relaunch release, from the Strategic Platform’s draft text, with date and quotes from named people who agreed to them.")),
        section("Fact sheet", facts + ph("The track record", "Exhibitions and collaborations since 2010, as history.")),
        section("Press images", ph("The press set", "A curated set for editorial use with the credit line; no images with minors. Open download or via media access: still to decide.")),
        section("Story leads", leads + ph("The stories", "Each lead in two sentences, with the series, the place and who to talk to.")),
        section("Logos and portrait", ph("Downloads", "Logo files and a portrait of Thomas Damgaard.")),
        section("Press contact", f'<p><a href="mailto:{EMAIL_PRESS}">{EMAIL_PRESS}</a></p>'),
    ])


def tpl_text(p, base):
    k = p["slug"]
    if k == "about":
        body = "".join([
            f'<p class="lead">{e(ABOUT_LINE)}</p>',
            section("Who is behind it", ph("Commerce & Culture and Thomas Damgaard", "Who runs the initiative and why; named people, by example.")),
            section("Principles", ph("How the images are made and used", "Real images, never AI-generated; consent and releases; photographers credited; fair terms; editorial independence.")),
            section("Legacy", ph("History, as proof behind the present", "Africa Reframed at Øksnehallen (2016), Afghan Tales (2014–2017), the artist collaborations and the work since 2010.")),
            section("How it is run", ph("A non-commercial initiative", "Administered through KKArt; no licensing sales; surplus funds new collections.")),
        ])
    elif k == "contact":
        body = (f'<p class="lead">Write to <a href="mailto:{EMAIL_MAIN}">{EMAIL_MAIN}</a>.</p>'
                + ph("LinkedIn", "A link to Africa Reframed on LinkedIn.")
                + f'<p class="small">Press: <a href="mailto:{EMAIL_PRESS}">{EMAIL_PRESS}</a> · Partnerships: <a href="mailto:{EMAIL_PARTNERS}">{EMAIL_PARTNERS}</a></p>')
    else:  # privacy
        body = "".join([
            '<p class="lead">What we collect when you request access or write to us, and why.</p>',
            section("What we collect", ph("Data", "Organisation, contact details, intended use and the answers you give in the partner forms.")),
            section("Why", ph("Purpose", "To approve access, keep in touch, and report how the images are used, without personal details, to the funders who make new collections possible, with your consent.")),
            section("How long, and your rights", ph("Retention and rights", "How long we keep it, and how to see, change or delete it.")),
        ])
    return f'<h1>{e(p["title"])}</h1>' + body


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
         desc="Africa Reframed’s own collection: 1,122 images from Mali, Kenya and The Gambia."),
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
<div class="skeleton-strip"><div class="wrap">Skeleton · structure only · boxes marked “To write” hold what each section will say at launch</div></div>
<main id="main" class="wrap">
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
}})();
</script>
</body>
</html>
"""

CSS = """:root{
  --ground:#151515; --paper:#ffffff; --ink:#151515; --ink-soft:#5c5a55;
  --text-on-dark:#e3e3e3; --accent:#fef98b; --line:#e6e4df; --wash:#f6f5f2;
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
.skeleton-strip{background:var(--accent);color:var(--ink);font-size:13px;padding:6px 0}

/* Body */
main.wrap{padding-top:56px;padding-bottom:96px;min-height:50vh}
h1{font-weight:500;font-size:44px;line-height:1.08;margin:0 0 16px;letter-spacing:-.015em;max-width:22ch;text-wrap:balance}
h2{font-weight:500;font-size:24px;line-height:1.2;margin:0 0 12px}
h3{font-weight:600;font-size:18px;line-height:1.25;margin:0 0 6px}
p{margin:0 0 12px;max-width:68ch}
.lead{font-size:19px;color:var(--ink);max-width:60ch}
.statement{font-size:24px;line-height:1.35;max-width:40ch;margin:0 0 20px}
.kicker{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-soft);margin:0 0 8px}
.small{font-size:14px;color:var(--ink-soft)}
.block{margin-top:56px;padding-top:28px;border-top:1px solid var(--line)}
.list{margin:0 0 16px;padding-left:20px}
.list li{margin:4px 0}
.list.links{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px 20px}
.meta-row{display:flex;flex-wrap:wrap;gap:8px 24px;font-size:14px;color:var(--ink-soft);margin:0 0 24px}
.next{font-size:20px;text-decoration:none;border-bottom:2px solid var(--accent)}

/* Buttons */
.doors{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0 12px}
.button{display:inline-flex;align-items:center;min-height:44px;padding:0 20px;background:var(--accent);color:var(--ink);font:inherit;font-weight:500;font-size:15px;border-radius:3px;border:0;text-decoration:none;cursor:pointer}
.button.quiet{background:transparent;border:1px solid var(--line-strong, #c9c6bf);color:var(--ink)}
.button[disabled]{opacity:.5;cursor:not-allowed}
.doors.big .button{min-height:52px;font-size:17px;padding:0 24px}

/* Placeholders */
.ph{border:1.5px dashed #c9c6bf;border-radius:6px;padding:16px 18px;margin:12px 0 16px;background:var(--wash);max-width:72ch}
.ph strong{display:block;font-weight:600;margin:6px 0 4px}
.ph p{margin:0;color:var(--ink-soft);font-size:15px}
.ph-tag{font-size:11px;letter-spacing:.08em;text-transform:uppercase;background:var(--ink);color:var(--paper);padding:2px 6px;border-radius:3px}

/* Home */
.hero{padding-bottom:8px}
.hero h1{font-size:52px;max-width:18ch}
.numbers{display:flex;flex-wrap:wrap;gap:12px 40px;margin:24px 0 8px}
.num b{display:block;font-size:40px;font-weight:500;line-height:1;font-variant-numeric:tabular-nums}
.num span{font-size:14px;color:var(--ink-soft)}

/* Theme and collection cards */
.themes{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,230px),1fr));gap:16px;margin-top:16px}
.theme-card,.collection-card{display:flex;flex-direction:column;gap:6px;text-decoration:none;border:1px solid var(--line);border-radius:6px;padding:18px;min-height:220px;position:relative}
.theme-card:hover,.collection-card:hover{border-color:var(--ink)}
.theme-card p,.collection-card p{font-size:15px;color:var(--ink-soft);margin:0}
.order{font-size:13px;color:var(--ink-soft);font-variant-numeric:tabular-nums}
.count{font-size:13px;margin-top:auto}
.strip{display:block;height:56px;border-radius:3px;background:repeating-linear-gradient(90deg,var(--wash) 0 22%,#fff 22% 25%);border:1px dashed #d6d3cc;margin-top:12px}
.collections{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr));gap:16px;margin:16px 0}
.collection-card{max-width:420px}

/* Partners: rules */
.rules{padding-left:22px;max-width:72ch}
.rules li{margin:10px 0}

/* Partner portal desk */
.desk .block{margin-top:36px}

/* Form */
.form{display:grid;gap:6px;max-width:560px;margin:24px 0}
.form label{font-size:14px;font-weight:500;margin-top:10px}
.form input,.form select,.form textarea{font:inherit;padding:10px 12px;border:1px solid #c9c6bf;border-radius:4px;background:#fff}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;color:var(--ink-soft)}
.form .button{justify-self:start;margin-top:16px}

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
  main.wrap{padding-top:40px;padding-bottom:80px}
  h1,.hero h1{font-size:34px}
  .statement{font-size:20px}
}
@media (max-width:480px){
  .wrap{padding:0 16px}
  main.wrap{padding-top:32px;padding-bottom:64px}
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
