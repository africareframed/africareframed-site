#!/usr/bin/env python3
"""Generate the Africa Reframed skeleton site: one header, identical to the archive's menu, five pages."""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
ARCHIVE = "https://archive.africareframed.com"

PAGES = {
    "index.html":                 ("Africa Reframed", "home", "Home: the window onto the archive. Statement, three numbers, theme grid, how it works, partners, request access."),
    "themes/index.html":          ("Themes", "themes", "The full theme index: eight themes with a sample strip and a count each; collections at the foot."),
    "partners/index.html":        ("Partners", "partners", "Two doors: Use the images, Fund a theme."),
    "about/index.html":           ("About", "about", "Who is behind Africa Reframed and how the images are made."),
    "request-access/index.html":  ("Request access", "request", "The request form: organisation, role, intended use, email."),
}

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Africa Reframed</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap">
<link rel="stylesheet" href="{base}assets/site.css">
</head>
<body class="page-{slug}">
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="{base}" aria-label="Africa Reframed, home">
      <img src="{base}assets/logo.png" alt="Africa Reframed" class="brand-logo">
    </a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
    <nav class="menu" id="menu" aria-label="Main">
      <a href="{base}themes/" {cur_themes}>Themes</a>
      <a href="{base}partners/" {cur_partners}>Partners</a>
      <a href="{base}about/" {cur_about}>About</a>
      <a href="{base}request-access/" {cur_request}>Request access</a>
      <span class="divider" aria-hidden="true"></span>
      <a href="{archive}/-/galleries/archive?src=main">Images</a>
      <a href="{archive}/lightbox?src=main">Lightbox</a>
      <a href="{archive}/client?src=main">Log in</a>
    </nav>
  </div>
</header>

<main class="wrap">
  <h1>{title}</h1>
  <p class="placeholder">{placeholder}</p>
  <p class="note">Skeleton page: the menu and the link between the two sites are being tested. Content follows.</p>
</main>

<footer class="site-footer">
  <div class="wrap">
    <p>The Africa Reframed archive is open to partners: organisations working with Africa in education, skills, business and climate.</p>
    <p class="links">
      <a href="{base}request-access/">Request access</a> ·
      <a href="{archive}/terms">Terms</a> ·
      <a href="{base}about/">Contact</a> ·
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
  --text-on-dark:#e3e3e3; --accent:#fef98b; --line:#e6e4df;
  --font:"DM Sans",system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font);font-size:16px;line-height:1.5}
a{color:inherit;text-decoration:none}
.wrap{max-width:1280px;margin:0 auto;padding:0 32px}

/* Header: logo left, one flat menu right, as on the archive */
.site-header{background:var(--ground);color:var(--text-on-dark)}
.bar{display:flex;align-items:center;justify-content:space-between;gap:24px;min-height:84px}
.brand{display:inline-flex;align-items:center}
.brand-logo{height:40px;width:auto;display:block}
.menu{display:flex;align-items:center;gap:22px;font-size:15px}
.menu a{padding:6px 0;border-bottom:2px solid transparent;color:var(--text-on-dark);white-space:nowrap}
.menu a:hover{color:#fff}
.menu a[aria-current="page"]{color:#fff;border-bottom-color:var(--accent)}
.divider{display:inline-block;width:1px;height:18px;background:rgba(227,227,227,.4);margin:0 4px}
.menu-toggle{display:none;background:none;border:0;padding:8px;cursor:pointer;width:44px;height:44px;flex-direction:column;justify-content:center;gap:5px}
.menu-toggle span{display:block;height:2px;background:var(--text-on-dark)}

/* Body */
main{padding:56px 32px 96px;min-height:50vh}
main h1{font-weight:500;font-size:40px;line-height:1.1;margin:0 0 16px;letter-spacing:-.01em}
.placeholder{color:var(--ink-soft);max-width:60ch;margin:0 0 8px}
.note{color:var(--ink-soft);font-size:14px;margin:0}

/* Footer */
.site-footer{border-top:1px solid var(--line);padding:32px 0 48px;color:var(--ink-soft);font-size:14px}
.site-footer p{margin:0 0 8px}
.site-footer a{color:var(--ink)}

/* Below tablet width: hamburger, like the archive */
@media (max-width:1023px){
  .menu-toggle{display:flex}
  .menu{display:none;position:absolute;left:0;right:0;top:84px;background:var(--ground);flex-direction:column;align-items:flex-start;gap:0;padding:8px 32px 24px;border-top:1px solid rgba(227,227,227,.15);z-index:10}
  .menu.open{display:flex}
  .menu a{padding:12px 0;font-size:17px;width:100%}
  .divider{width:100%;height:1px;margin:8px 0}
  .site-header{position:relative}
  .wrap{padding:0 24px}
  main{padding:40px 24px 80px}
  main h1{font-size:32px}
}
"""

def build():
    (ROOT / "assets").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "site.css").write_text(CSS)
    for path, (title, slug, placeholder) in PAGES.items():
        depth = path.count("/")
        base = "../" * depth if depth else "./"
        cur = lambda s: 'aria-current="page"' if slug == s else ""
        html = TEMPLATE.format(
            title=title, slug=slug, placeholder=placeholder, base=base, archive=ARCHIVE,
            cur_themes=cur("themes"), cur_partners=cur("partners"), cur_about=cur("about"), cur_request=cur("request"),
        )
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
    (ROOT / ".nojekyll").write_text("")
    print("built", len(PAGES), "pages into", ROOT)

if __name__ == "__main__":
    build()
