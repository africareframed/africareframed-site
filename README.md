# africareframed.com

The public site of Africa Reframed. The archive lives on PhotoDeck at archive.africareframed.com, behind a partner login; this site presents the initiative and leads partners to it.

**Skeleton, version 2 (6 November 2026):** structure only. Real words appear where they already exist in the master documents. Every other section is a box marked "To write" that says what it holds at launch.

- **Build:** `python3 src/build.py` writes all 16 pages, `assets/site.css` and `assets/share-default.png` into the repository root. GitHub Actions publishes to GitHub Pages on every push to `main`.
- **Structure:** follows "Website – Site map and user flows" (05 Website on the Drive), 16 pages from 9 templates. Home; Themes plus five theme pages; Collections plus the House Collection; Partners; Partner portal; Request access; About; Press room; Contact; Privacy.
- **Header:** defined once, in `src/build.py`. It reads Themes · Collections · Partners | Log in, where Log in opens the Partner portal. The archive keeps the same header and adds its own tools (Browse images, Lightbox). Keep the two headers pixel-identical.
- **Footer:** the about line, then About · Press · Contact · Privacy · Request access · Terms (the archive's terms).
- **Links into the archive** carry `src=main-…` so their origin is visible in the archive's statistics. Theme pages use interim searches until each theme has its own keyword (Keywording Guide, section 8b).
- **Link previews:** every page has Open Graph tags. The share image is the logo on black until real images are chosen.
- **Not indexed:** `noindex` stays on until launch on the real domain.
- **Brief:** "Website – Brief and build plan" (Google Doc, 05 Website on the Africa Reframed Drive).
