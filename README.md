# africareframed.com

The public site of Africa Reframed. The archive lives on PhotoDeck at archive.africareframed.com, behind a partner login; this site presents the initiative and leads partners to it.

**Live wireframe, version 4 (6 November 2026).** The five key pages (Home, the theme pages, the collection page, Partners, Partner portal) are arranged by the page priorities in "Website – Site map and user flows", section 6. Grey boxes with a cross are images still to choose, at the size and proportion they will have. Grey bars are text still to write, and yellow notes say what goes there. Real words appear only where they already exist in the master documents. "Clean view" in the yellow strip hides the notes, so a page can be shown as a layout.

- **Build:** `python3 src/build.py` writes all 16 pages, `assets/site.css` and `assets/share-default.png` into the repository root. GitHub Actions publishes to GitHub Pages on every push to `main`.
- **Structure:** follows "Website – Site map and user flows" (05 Website on the Drive), 16 pages from 9 templates. Home; Themes plus five theme pages; Collections plus the House Collection; Partners; Partner portal; Request access; About; Press room; Contact; Privacy.
- **Header:** defined once, in `src/build.py`. It reads Themes · Collections · Partners | Log in, where Log in opens the Partner portal. The archive keeps the same header and adds its own tools (Browse images, Lightbox). Keep the two headers pixel-identical.
- **Footer:** the about line, then About · Press · Contact · Privacy · Request access · Terms (the archive's terms).
- **Links into the archive** carry `src=main-…` so their origin is visible in the archive's statistics. Theme pages use interim searches until each theme has its own keyword (Keywording Guide, section 8b).
- **Link previews:** every page has Open Graph tags. The share image is the logo on black until real images are chosen.
- **Development page:** every build also writes `/dev/`: the order of work, every page with its template, state and what is still to fill, the masters on the Drive and claude.ai, every link into the archive, the launch checklist and recent changes. It is a view, not a log: decisions and the log stay on the Drive. Set a page's state in `STATE` in `src/build.py`.
- **Launch switch:** `LAUNCH = True` in `src/build.py` removes `/dev/`, the wireframe strip and `noindex`.
- **Deploy:** the workflow runs `python3 src/build.py` before publishing, so the live site always matches `src/`.
- **Not indexed:** `noindex` stays on until launch on the real domain.
- **Brief:** "Website – Brief and build plan" (Google Doc, 05 Website on the Africa Reframed Drive).
