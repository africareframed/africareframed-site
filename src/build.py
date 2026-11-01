#!/usr/bin/env python3
"""Generate the Africa Reframed skeleton site: one header, five pages, the bridge script."""
import os, pathlib

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
<script>
/* Bridge: if we arrived from the archive (?in=1) remember it; ?in=0 forgets. Applied before paint to avoid a flash. */
(function(){{
  var q = new URLSearchParams(location.search);
  if (q.has('in')) {{
    var on = q.get('in') === '1';
    document.cookie = 'ar_in=' + (on ? '1' : '') + '; path=/; max-age=' + (on ? 60*60*24*30 : 0) + '; SameSite=Lax';
    q.delete('in');
    var rest = q.toString();
    history.replaceState(null, '', location.pathname + (rest ? '?' + rest : '') + location.hash);
  }}
  if (/(^|; )ar_in=1/.test(document.cookie)) document.documentElement.classList.add('in');
}})();
</script>
</head>
<body class="page-{slug}">
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="{base}" aria-label="Africa Reframed, home">
      <img src="{base}assets/logo.png" alt="" class="brand-logo" onerror="this.style.display='none';this.nextElementSibling.style.display='inline'">
      <span class="brand-word" style="display:none">Africa<br>Reframed</span>
    </a>
    <nav class="primary" aria-label="Main">
      <a href="{base}themes/" {cur_themes}>Themes</a>
      <a href="{base}partners/" {cur_partners}>Partners</a>
      <a href="{base}about/" {cur_about}>About</a>
    </nav>
    <div class="tools">
      <a class="button btn-request" href="{base}request-access/">Request access</a>
      <a class="button btn-images" href="{archive}/-/galleries/archive?src=main">Images <span aria-hidden="true">&rarr;</span></a>
      <form class="search" action="{archive}/-/galleries/archive" method="get" role="search">
        <label for="q" class="visually-hidden">Search the archive</label>
        <input id="q" type="search" name="search" placeholder="Search the archive" autocomplete="off">
        <input type="hidden" name="src" value="main">
        <button type="submit" aria-label="Search">
          <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"></circle><path d="M20 20l-3.5-3.5"></path></svg>
        </button>
      </form>
      <a class="quiet" href="{archive}/lightbox?src=main">My selection</a>
      <a class="quiet" href="{archive}/client?src=main">Your account</a>
    </div>
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
      <a href="{base}?in=0" class="quiet" title="Forget that I came from the archive">Reset view</a> ·
      <span>&copy; Africa Reframed</span>
    </p>
  </div>
</footer>
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
.wrap{max-width:1280px;margin:0 auto;padding:0 24px}
.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}

/* Header */
.site-header{background:var(--ground);color:var(--text-on-dark)}
.bar{display:flex;align-items:center;gap:32px;min-height:88px;flex-wrap:wrap;padding-top:12px;padding-bottom:12px}
.brand{display:inline-flex;align-items:center;color:#fff}
.brand-logo{height:40px;width:auto;display:block}
.brand-word{font-weight:600;font-size:20px;line-height:1;letter-spacing:.06em;text-transform:uppercase}
nav.primary{display:flex;gap:28px;font-size:16px}
nav.primary a{padding:8px 0;border-bottom:2px solid transparent;color:var(--text-on-dark)}
nav.primary a:hover{color:#fff}
nav.primary a[aria-current="page"]{color:#fff;border-bottom-color:var(--accent)}
.tools{display:flex;align-items:center;gap:16px;margin-left:auto;flex-wrap:wrap}
.tools .quiet{color:var(--text-on-dark);font-size:15px}
.tools .quiet:hover{color:#fff}
.button{display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:0 16px;background:var(--accent);color:var(--ink);font-weight:500;font-size:15px;border-radius:3px}
.button:hover{filter:brightness(1.05)}
.search{display:flex;align-items:center;height:40px;border:1px solid rgba(227,227,227,.35);border-radius:3px;background:rgba(227,227,227,.06);padding:0 6px 0 12px;width:200px}
.search input{flex:1;min-width:0;border:0;background:transparent;color:#fff;font:inherit;font-size:14px;outline:none}
.search input::placeholder{color:rgba(227,227,227,.6)}
.search button{border:0;background:transparent;color:var(--text-on-dark);display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;cursor:pointer}

/* One menu on both sites. The marker from the archive only moves the emphasis: Request access for newcomers, Images for those who came from the archive. */
.button.btn-images{background:transparent;color:var(--text-on-dark);border:1px solid rgba(227,227,227,.35)}
html.in .button.btn-images{background:var(--accent);color:var(--ink);border-color:var(--accent)}
html.in .button.btn-request{background:transparent;color:var(--text-on-dark);border:1px solid rgba(227,227,227,.35)}
.button{border:1px solid var(--accent)}

/* Body */
main{padding:56px 24px 96px;min-height:50vh}
main h1{font-weight:500;font-size:40px;line-height:1.1;margin:0 0 16px;letter-spacing:-.01em}
.placeholder{color:var(--ink-soft);max-width:60ch;margin:0 0 8px}
.note{color:var(--ink-soft);font-size:14px;margin:0}

/* Footer */
.site-footer{border-top:1px solid var(--line);padding:32px 0 48px;color:var(--ink-soft);font-size:14px}
.site-footer p{margin:0 0 8px}
.site-footer a{color:var(--ink)}
.site-footer .quiet{color:var(--ink-soft)}

@media (max-width:900px){
  .bar{gap:16px 24px}
  nav.primary{order:3;width:100%;gap:24px}
  .tools{margin-left:auto}
  .search{width:180px}
}
@media (max-width:600px){
  nav.primary{order:2}
  .tools{order:3;width:100%;margin-left:0;flex-wrap:wrap;gap:12px 16px}
  .search{width:100%;order:9}
  main h1{font-size:32px}
}
"""

def build():
    (ROOT / "assets").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "site.css").write_text(CSS)
    for path, (title, slug, placeholder) in PAGES.items():
        depth = path.count("/")
        base = "../" * depth if depth else "./"
        html = TEMPLATE.format(
            title=title, slug=slug, placeholder=placeholder, base=base, archive=ARCHIVE,
            cur_themes='aria-current="page"' if slug == "themes" else "",
            cur_partners='aria-current="page"' if slug == "partners" else "",
            cur_about='aria-current="page"' if slug == "about" else "",
        )
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
    (ROOT / ".nojekyll").write_text("")
    print("built", len(PAGES), "pages into", ROOT)

if __name__ == "__main__":
    build()
