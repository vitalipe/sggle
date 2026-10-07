# Project history and recovery notes

## Original project

SGGLE was written as a solo side project between January and November 2012 and hosted
on Bitbucket as a Mercurial repository at `https://bitbucket.org/vitalipe/sggle`
(repository UUID `ee1ceb4c-5325-41d6-86d1-dbb0add28d30`).

| | |
|---|---|
| First commit | 2012-01-06 ("import") |
| Last commit | 2012-11-30 ("Added tag 0.2.0") |
| Changesets | 207 on a single `default` branch, two merges |
| Tags | `0.1.0` (2012-01-25), `0.2.0` (2012-11-30) |
| License | LGPL 3 (see `LICENSE`) |
| Stack | Python 2, PySide 1 (Qt 4) |

Bitbucket removed all Mercurial repositories in mid 2020, which took the original
project offline. The wiki that served as the project page went with it.

## Where the code was recovered from

The git history in this repository was rebuilt on 2026-10-07 from the
Mercurial Bitbucket Archive run by Software Heritage and Octobus. The recovery,
conversion and verification described in this file were performed by Claude
(Anthropic's Claude Code, model Claude Fable 5.1), working under the direction of
the project's author, who reviewed the results.

Sources:

- Project page: <https://bitbucket-archive.softwareheritage.org/projects/vi/vitalipe/sggle>
- Repository tarball: <https://bitbucket-archive.softwareheritage.org/new-static/ee/ee1ceb4c-5325-41d6-86d1-dbb0add28d30/ee1ceb4c-5325-41d6-86d1-dbb0add28d30-repository.tar.gz>
- Metadata tarball: <https://bitbucket-archive.softwareheritage.org/new-static/ee/ee1ceb4c-5325-41d6-86d1-dbb0add28d30/ee1ceb4c-5325-41d6-86d1-dbb0add28d30-metadata.tar.gz>

The archived `.hg` store passed `hg verify` (207 changesets, 526 file revisions,
140 files). The archive did not include the wiki, issues or downloads.

An independent copy of the same repository exists in the Internet Archive's
Wayback Machine, which crawled Bitbucket's Mercurial wire protocol shortly before
the shutdown:

- <https://web.archive.org/web/20200616050825/https://bitbucket.org/vitalipe/sggle?cmd=getbundle>

That capture is a zlib-compressed HG20 stream bundle. Applied to an empty
Mercurial repository it yields the same 207 changesets, the same tip
(`b27b5ce540a4`) and the same tags as the Software Heritage copy.

## How the git conversion was done

- Tooling: `hg-fast-export` (<https://github.com/frej/fast-export>, commit `71541d4`),
  Mercurial 7.2.4, git 2.34.1.
- The Mercurial `default` branch became `main`.
- Commit messages, author timestamps and file contents are unchanged. Every one of the
  207 commits was diffed against an `hg archive` of its source changeset, and the
  message and timestamp compared, with zero mismatches. `git fsck` reports no issues.
- The four author spellings used in the Mercurial history (`vitali`, `vitali_pe`,
  `"vitali"` and `"Vitali Perchonok <vitali.pe@gmail.com>"`) all belong to the same
  person and were normalized to `Vitali Perchonok <vitali.pe@gmail.com>`.
- Both tags were carried over as git tags. The Mercurial `.hgtags` file was left out of
  the tree, as is standard for such conversions.
- Each git commit carries its original Mercurial changeset id as a git note in the
  `hg` namespace. If the notes were pushed, view them with `git log --notes=hg`.

Key changeset ids, in case the notes are not available:

| Point in history | Mercurial changeset | Git commit |
|---|---|---|
| First commit ("import") | `0992bf0df1f0d6c841784a40754ae114698ff35e` | `7448457fc5a654d6a5fb9f46cb975928432d44b0` |
| Tag `0.1.0` | `8329bb0f15fe1d54feb487edc451c8cbabb897f6` | `05ce86530d4c9e401f1e920b500eaec7ae10d418` |
| Tag `0.2.0` | `823003c09d94207588d3031bb4070f8a8b4b0279` | `dd7e8fb605c4a96ccded22dbda773d648c125153` |
| Last commit (tip) | `b27b5ce540a47b4df5470773ccb6a1d75fa2298d` | `3480c129cfea5bc2000c582ccaace24402cc894d` |

## Where the README and screenshots came from

The repository never contained a README. The project description lived on the
Bitbucket wiki Home page, last edited 2012-12-01. It was recovered from two Wayback
Machine captures:

- The rendered page, captured 2020-07-07:
  <https://web.archive.org/web/20200707053216/https://bitbucket.org/vitalipe/sggle/wiki/Home>
- A stream bundle of the wiki's own Mercurial repository, captured 2020-06-21:
  <https://web.archive.org/web/20200621194040/https://bitbucket.org/vitalipe/sggle/wiki?cmd=getbundle>

The bundle contains the wiki's full 10-commit history with `Home.wiki` (Creole markup)
and the screenshots `s1.png` to `s3.png` (1366x744) and `ss1.png` to `ss3.png`
(900x490). `README.md` is a Markdown port of `Home.wiki`; the only content change is
the download step, which pointed at a Bitbucket tarball URL that no longer exists and
now refers to the `0.2.0` tag. `docs/screenshots/` holds the three 900x490 images the
wiki page displayed.

`README.md`, `HISTORY.md` and `docs/screenshots/` were added in 2026 as part of the
recovery; the Markdown port of the wiki page and this file were written by Claude.
Everything else in this repository is the 2012 code as committed.
