# Updates

## 2026-10-28 — Initial Bible reader

- Added Korean and English interfaces with six public-domain Scripture editions, each containing 66 books and 1,189 chapters.
- Generated separate version landing pages and chapter HTML pages. Added book/chapter navigation, book filtering, previous/next chapter links, and version switching that preserves the book/chapter/verse.
- Prioritized Korean editions on Korean screens and English editions on English screens. Interface language links remain in the footer.
- Added verse-level Copy and Share buttons, canonical chapter URLs with verse anchors, and selected-verse sharing. Included clipboard fallback and a manual-copy dialog; preserved cancellation behavior.
- Added responsive reading layout, font-size controls, optional dark mode, source/rights notices, and privacy notices. No slogans, NaNa Lab header branding, external fonts, or unrelated app changes.
- Preserved source snapshots, attribution, source hashes, original verse wording and numbering. Source-absent verses receive a bracketed UI note, never replacement text from another edition.
- Added GA4, GTM plus noscript, AdSense, and Cloudflare integrations to every generated HTML page. Preview execution is guarded; custom input/verse analytics are absent.
- Added two leaf sitemaps (7,143 URLs each), an app sitemap index, open robots.txt, ads.txt, and the small More Apps footer link.
- Local validation: source checksums, every generated verse, all internal links, canonical/hreflang, language ordering, and publisher integrations checked across 14,286 pages. Runtime behavior tests cover 11 navigation/copy/share/fallback/settings cases.
- Browser observations cover book search, chapter navigation, same-chapter version changes, English default ordering, verse anchors, and desktop/mobile layout without horizontal overflow. Browser Use virtual clipboard cannot read back the OS clipboard; native sharing remains pending in this in-app browser. Native share payload/cancel/error behavior is covered with platform API mocks; no third-party share message was sent.
- Publication status and exact commit are recorded separately in `evidence/release.json` after GitHub Pages deployment and response verification.
