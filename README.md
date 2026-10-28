# 성경 뷰어 / Bible Reader

Static Bible reader with real pages for every version and chapter. The Korean interface is at `/bible-viewer/`; the English interface is at `/bible-viewer/en/`.

## Reading and navigation

- Six public-domain editions: Korean Revised Version (1961), World English Bible, Berean Standard Bible, American Standard Version (1901), Reina-Valera 1909, and Louis Segond 1910.
- Each edition contains 66 books and 1,189 chapters. Version pages list all books and their chapter links.
- The home page opens books with chapter buttons. Book-name filtering accepts Korean names, English names, or book codes.
- The version dropdown preserves the current book, chapter, and verse anchor. Korean editions appear first in the Korean interface; English editions appear first in the English interface.
- Every verse has Copy and Share. Copy includes its reference, edition, complete verse text, and canonical chapter URL with a verse anchor. Share sends the same text and URL to the native share sheet. If sharing is unavailable or rejected, the app offers clipboard copying; if copying is denied, a manual-copy dialog opens.
- The chapter-level Share a verse button uses the selected verse. Font size and theme preferences remain in browser storage.

## URLs

```text
/bible-viewer/                      Korean home
/bible-viewer/en/                   English home
/bible-viewer/krv/                  Korean Revised Version landing page
/bible-viewer/krv/jhn/3/#v16         John 3:16, Korean interface
/bible-viewer/en/web/jhn/3/#v16      John 3:16, English interface
```

There are 14,268 chapter pages, 12 version pages, two home pages, and four source/privacy pages: 14,286 HTML pages total. No full-corpus JSON is requested by the browser. Each page contains only that chapter’s text and navigation.

## Sources and rights

Source snapshots are retained in `data/source/`; `data/versions.json` records the download location, attribution, rights link, source hash, normalized hash, and counts. Original verse text, source placeholders, combined verses, and numbering are retained. Blank verses in the supplied edition receive an explicitly bracketed UI note rather than text invented or borrowed from another edition. Notes, original-language editions, modern copyrighted translations, third-party artwork, and recorded audio are not imported.

Korean Revised Version economic copyright expiry and attribution/integrity requirements were verified against the Korean Bible Society FAQ. The digital text is `thiagobodruk/bible/json/ko_krv.json`; its MIT license is preserved in `data/source/thiagobodruk-LICENSE` and on both source pages. A different Korean export inspected during research was excluded. World English Bible and Berean edition-name conditions are preserved on the source pages; verse wording is unchanged.

## Build and validation

Python 3.10+ and Node.js 18+ are sufficient; no application dependencies or remote APIs are required.

```text
python scripts/import_sources.py
python scripts/build_site.py
python scripts/check_site.py
node --check src/app.js
node scripts/check_runtime.mjs
python scripts/preview.py --port 8773
```

Importing normally uses the retained snapshots. `--download` explicitly refreshes upstream input files and their hashes. After refreshing, rebuild and review both the sources and checks.

Preview serves `http://127.0.0.1:8773/bible-viewer/` with a test-only CSP blocking external tracking and advertising. The production-host guard also prevents publisher bootstrap execution on preview hosts.

## Publishing and search

GitHub Pages serves `main:/docs`. The project has no CNAME file and uses the organization’s `nanalab.kr` domain. `sitemap.xml` references `sitemap-ko.xml` and `sitemap-en.xml`, each containing 7,143 URLs. When integrating with the main NaNa Lab sitemap index, link these two leaf maps directly, without nesting the app’s index.

All HTML pages include GA4, GTM plus noscript fallback, AdSense, and Cloudflare Web Analytics from the source build. Search input, shared/copied verse text, and reading preferences are not sent as custom analytics events. Every page includes the small More Apps footer link.

Verification artifacts distinguish exhaustive source/HTML checks, mocked platform API tests, browser navigation/layout observations, and production response comparisons. OS share destinations and actual analytics ingestion are not implied by a passed source check.
