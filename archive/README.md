# archive/

Files that are no longer used by the app, kept for reference instead of being deleted (pass 7, Oct 2026).
Each one was grepped across the repo first; nothing imports, renders, serves or links to them.
They are outside `templates/` and `static/`, so Flask can neither render nor serve them.

| Path here | Was | Why it is archived |
|---|---|---|
| `app 2.py` | `app 2.py` | An old copy of `app.py` (Finder-style duplicate name); never imported. |
| `templates/*(1).html` | `templates/` | Download duplicates of `admin_tqi`, `tqi`, `tqi_official` and `tqi_report`; the app renders the un-suffixed files. |
| `static/img/navy-n.png` | `static/img/` | 2.1 MB original logo; pages use `navy-n-256.png`, `navy-n-512.webp` and `favicon-32.png`. |
| `static/img/navy-interior-live.webp` | `static/img/` | 604 KB image no page or stylesheet references. |
| `root-zips/*.zip` | repo root | Patch bundles from earlier hand-offs (landing, TQI, chapter nav, run class, embeds…). Their contents are already in the tree. |

To restore something: `git mv archive/<path> <original path>`.
`archive/` is marked `export-ignore` in `.gitattributes`, so `git archive` (the release zip) leaves it out.
