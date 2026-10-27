---
name: db-cite
description: From a URL, create the original (typically English) bibliography entry in bib/db.bib, create translation entries in the languages the user names (Es, Zh, It, Ru…) using the Tlön glossary, and push them all to the Tlön database. Use when the user gives a link and wants it added to the database, or asks for translation entries of an existing bibkey.
---

# /db-cite

Import a work from a link into the Tlön database: write the original entry and its
translation entries to `bib/db.bib`, then push them to the server and verify them.

This is the `db.bib` counterpart of `uqbar-en`'s `/cite`. Entry-construction rules
(bibkey form, union-of-fields template, web verification, no fabrication) are the same;
the destination, the field set, the translation step and the push are different.

```
/db-cite <url> [Es Zh It Ru …]
/db-cite <BibKey> [Es Zh It Ru …]     # original already in the database; only translate
```

## Paths

| What | Where |
|---|---|
| Destination | `/Users/cartago/Library/CloudStorage/Dropbox/repos/babel-refs/bib/db.bib` |
| Also search | `bib/stable.bib`, `bib/fluid.bib`, `bib/db-upstream.bib` (same dir) |
| Glossary | `/Users/cartago/Library/CloudStorage/Dropbox/repos/babel-core/glossary.json` |
| Legacy MT abstracts | `json/<lang>/abstract-translations.json` (reference only — see §6c) |
| Push instructions | `babel-refs/CLAUDE.local.md` (authoritative; §7 below follows it) |

`bib/db.bib` is **gitignored** and is a local mirror of the database. Edit it only by
**appending** at the end; never rewrite or reformat neighbouring entries; never commit it.

> **Entries written here are volatile until pushed.** Emacs runs
> `tlon-db-get-entries-no-confirm` after 3 hours idle, which overwrites `db.bib` and
> `db-upstream.bib` with the server's state and **silently destroys any unpushed local
> addition**. There is no git history to recover from.
>
> Therefore:
> - Push in the same run (§7), right after writing. Do not leave entries unpushed.
> - Save a copy of everything you append to `<scratchpad>/db-cite-<date>.bib`, so it can be replayed if a refresh lands before the push.
> - Before appending, re-grep for keys you wrote earlier in the session. If entries you created have vanished, say so rather than silently re-adding them.

## 0. Resolve arguments

Split `$ARGUMENTS` into (a) one target and (b) zero or more two-letter language codes.

- Target starts with `http://` / `https://` → import the original from the web (§1–§5), then translate (§6).
- Target is a bare `AuthorYYYYWords` bibkey → the original already exists; confirm it is on the server (`GET /api/entries/<key>` → 200, see §7d) and skip to §6.
- No target → ask which link to import. Do not guess.

The language codes are **exactly** the translations to create — no more, no fewer. If
none were given, ask with `AskUserQuestion` (multi-select) which translations to create,
offering Es / Zh / It / Ru as the first options. An empty answer means "original only",
which is a valid outcome.

The **original** entry is the work in the language it was first published in — usually
English. If the link points to a translation (e.g. a Spanish version of an English post),
create the entry for the original-language work, and treat the linked version as an
existing translation (with its own `url` and `translator`), not as the original.

## 1. Fetch the work

`WebFetch` the URL. Extract: title, author(s), publishing venue, publication date, and
the real abstract if the page has one. If the page is a redirect, a paywall, or a
JS-only shell, `WebSearch` for the canonical record instead (publisher page, DOI landing
page, Crossref `https://api.crossref.org/works?query.title=…&query.author=…`).

## 2. Check for an existing entry — all four files and the server

Search by **title** (case-insensitive) *and* by the **bibkey pattern** you are about to
propose, across all four bib files. `db.bib` and `db-upstream.bib` routinely hold
entries absent from `stable.bib`/`fluid.bib`; skipping them creates duplicates.

```bash
cd /Users/cartago/Library/CloudStorage/Dropbox/repos/babel-refs/bib
grep -in "<distinctive title fragment>" stable.bib fluid.bib db.bib db-upstream.bib
grep -n "<ProposedBibKey>" stable.bib fluid.bib db.bib db-upstream.bib
```

Then confirm on the server that the proposed key (and each `<Key><Xx>`) returns **404**
(§7d). The server is the authority; the local files may be stale.

- Already in the database → do not create a second entry or edit the existing one. Report the existing bibkey and go on to the translations that are missing.
- Only in `fluid.bib`/`stable.bib` → do not duplicate it in `db.bib`; tell the user and offer `tlon-db-move-entry` (which posts it and removes it from the source file).

## 3. Propose the bibkey

`AuthorYYYYFirstThreeSignificantWords`, CamelCase, no spaces or dashes, stopwords
dropped (`to`, `the`, `a`, `and`, `of`, `on`…):

- `Heath2013DecisiveHowTo`
- `Hubbard2014HowMeasureAnything` (drop "to")
- `Christiano2019WhatFailureLooks`
- Corporate author → short org form: `AiDigest2025NewMooresLaw`, `Cbi2012LearningToGrow`

Re-grep the proposed key across all four files before using it (§2) — a `translation =
{...}` field elsewhere may already point at it.

## 4. Build the field template

Read **5 existing entries of the same `@type`** from `db.bib` and take the **union of
their fields**. That union is the template; fill every field that could plausibly apply,
omitting only those that genuinely cannot (`isbn` on a web post, `issn` on a book).

For reference, the observed unions in `db.bib` — but re-derive rather than trusting this
table blindly, since the file changes:

| `@type` | Fields |
|---|---|
| `@online` | langid, title, timestamp, author, alternateurls, journaltitle, file, abstract, date, url, urldate, database |
| `@article` | + doi, volume, number, pages, issn, publisher |
| `@book` | + publisher, location, address, isbn |
| `@incollection` | + booktitle, editor, publisher, location, address, pages, doi, isbn |

**Canonical field order for `@online`** (keep it; the file is consistent):

```
langid > title > timestamp > author > alternateurls > journaltitle > file > abstract > date > url > urldate > database
```

Web-verify every value before writing it. Do not invent DOIs, page ranges, or dates. If
a field is genuinely unfindable, omit it and say so in the report.

## 5. Write the original entry

Append to the **end** of `db.bib` (the file is not sorted; new entries go last), tab-indented,
exactly one blank line between entries. The file usually already ends with `}\n\n`
(check with `tail -c 3 bib/db.bib | od -c`); if so, do not start the appended text with
another blank line.

```bibtex
@online{Christiano2019WhatFailureLooks,
	langid = {english},
	title = {What failure looks like},
	timestamp = {2026-09-16 15:35:29 (GMT)},
	author = {Christiano, Paul},
	alternateurls = {},
	journaltitle = {{LessWrong}},
	abstract = {The stereotyped image of AI catastrophe is a powerful, malicious AI system that takes its creators by surprise. This post argues that failure is more likely to look like a gradual loss of human control …},
	date = {2019-03-17},
	url = {https://www.lesswrong.com/posts/HBxe6wdjxK239zajf/what-failure-looks-like},
	database = {Tlön}
}
```

Rules specific to `db.bib` (these differ from `fluid.bib`):

- `timestamp` **is** used here — set it to the real current UTC time, `date -u "+%Y-%m-%d %H:%M:%S"`, formatted `{YYYY-MM-DD HH:MM:SS (GMT)}`. Never copy another entry's timestamp.
- `database = {Tlön}` on every entry.
- `alternateurls = {}` unless the work genuinely has mirror URLs (it almost never does).
- `file = {~/My Drive/library-pdf/<BibKey>.pdf}` **only if that PDF actually exists**. Check with `ls` first; omit otherwise.
- `langid = {english}` (or the work's real language) on the original.
- Brace-protect acronyms in titles: `{AI}`, `{AGI}`, `{GPT}`, `{LessWrong}`. Brace-protect corporate authors: `{{Confederation of British Industry}}`.
- Escape a literal percent in prose fields as `\%`. Leave percent-encoding inside `url` alone.

### Abstracts

Prefer the publisher's or author's real abstract. If there is none, write a summary of
3–6 sentences from the work itself: neutral, third person, describing what the work
argues or reports.

**Never** add a label saying the abstract was AI-generated (`– AI-generated abstract.`,
`– Resumen generado por IA.`, `——AI生成的摘要。`, etc.), in the original or in any
translation. Many older entries carry such a closer; do not imitate them.

## 6. Create the translation entries

One entry per requested language, key = `<OriginalBibKey><Xx>`.

### 6a. Language table

Derived from `db.bib`. `Venue` is the Tlön site the translation is published on — used as
`journaltitle`; languages with no Tlön site take **no** `journaltitle` field at all.

| Code | `langid` | `journaltitle` (venue) |
|---|---|---|
| `Es` | spanish | `Altruismo Eficaz` |
| `It` | italian | `Altruismo Efficace` |
| `Fr` | french | `Altruisme Efficace` |
| `Ru` | russian | *(none)* |
| `Zh` | chinese | *(none)* |
| `Ja` | japanese | `効果的利他主義` |
| `Ko` | korean | `효과적 이타주의` |
| `Ar` | arabic | *(none)* |
| `Tr` | turkish | `Efektif Altruizm` |
| `Pl` | polish | *(none)* |
| `Sr` | serbian | `Efektivni altruizam` |
| `He` | hebrew | *(none)* |
| `Pt` | portuguese | *(none)* |
| `Cs` | czech | `Efektivní altruismus` |

Before writing, check the most recent sibling entries of that language in `db.bib` and
follow their field set, in case the convention has changed:

```bash
grep -B2 -A12 'langid = {russian}' bib/db.bib | tail -40
```

For a language not in the table, derive `langid` and venue the same way — from existing
entries with that suffix — and say in the report that you did.

### 6b. Use the glossary — required, and show your work

The glossary, `babel-core/glossary.json`, is the authority on Tlön terminology, as in the
`uqbar-<lang>` repos. Stick to its terms; deviate only for a compelling reason, and
document every deviation in the report. It is a list of ~2,000 objects, each
`{"en": …, "type": "variable"|"invariant", "es": …, "it": …, "ru": …, "zh": …, …}`:

- `variable` → the target-language string is the **mandated** rendering.
- `invariant` → the term is **not** translated (org names, product names); use the target-language field if present, otherwise keep the English.
- A term with **no field for your language** carries no mandate. Fall back to the convention already used in `db.bib` for that language, and flag it in the report rather than inventing a new rendering.

Do not read the file whole. Two ways to query it:

1. **Sweep** the original title + abstract for every glossary term they contain — run before drafting:

```bash
python3 - <<'EOF'
import json, re
GLOSS='/Users/cartago/Library/CloudStorage/Dropbox/repos/babel-core/glossary.json'
SRC = """<paste the original title and abstract here>"""
LANGS = ['es','zh']            # the requested languages, lowercased
d = json.load(open(GLOSS)); hay = SRC.lower()
hits = [e for e in d if len(e.get('en',''))>3
        and re.search(r'(?<![a-z])'+re.escape(e['en'].lower())+r'(?![a-z])', hay)]
hits.sort(key=lambda e: -len(e['en']))
for e in hits:
    print(e['type'].ljust(9), e['en'], '→',
          {l: e.get(l, '—— NO ENTRY ——') for l in LANGS})
EOF
```

2. **Look up** a single term while drafting (catches concepts the literal sweep missed):

```bash
jq -r '.[] | select(.es) | [.en, .es] | @tsv' \
  /Users/cartago/Library/CloudStorage/Dropbox/repos/babel-core/glossary.json | grep -i 'TERM'
```

Then **draft** each translation (title and abstract) applying every mandate, and
**reverse-check** the draft: grep the finished target-language text for any string the
glossary assigns to a *different* English term, which would silently collide. Longer
glossary keys win over shorter ones (`AI safety` beats `safety`).

**Titles** need the same care. The glossary holds terminology, not work titles, so the
title is your own rendering, but every key term in it must follow the glossary (e.g.
AGI → ru `СИИ`, compute governance → es `gobernanza de la computación`, AI alignment →
zh `人工智能对齐`). Where only a compound form exists (`global AI governance` → ru
`всемирная регуляция ИИ`), derive the base term from it and flag that it was derived.

### 6c. Reference, don't copy, the legacy MT

`json/<lang>/abstract-translations.json` may already hold an abstract for this bibkey.
These are **older raw machine translations**. Use them as a starting reference and
improve them (glossary, no AI-generated label); never paste them in verbatim.

### 6d. Write each entry

**Canonical field order for a translation `@online`:**

```
langid > title > timestamp > author > translator > alternateurls > journaltitle > translation > abstract > date > url > database
```

```bibtex
@online{Christiano2019WhatFailureLooksEs,
	langid = {spanish},
	title = {Cómo será el fracaso},
	timestamp = {2026-09-16 15:42:00 (GMT)},
	author = {Christiano, Paul},
	alternateurls = {},
	journaltitle = {Altruismo Eficaz},
	translation = {Christiano2019WhatFailureLooks},
	abstract = {La imagen estereotipada de una catástrofe de la {IA} es la de un sistema de {IA} poderoso y malicioso …},
	date = {2026-09-16},
	database = {Tlön}
}
```

- `author` — the **original** author, unchanged. Never translate or transliterate a name.
- `translation = {<OriginalBibKey>}` — this is what links the entry to its original.
- `date` — the translation's own publication date, i.e. **today** for a newly created one (not the original's date).
- `translator` — only when a named human or org translated it. Omit for a fresh Tlön translation.
- `url` — only if the translation is already published somewhere. Omit otherwise.
- `file` — omit.
- `abstract` — the translated abstract, with no AI-generated label.
- Brace-protect acronyms in the translated title too: `{IA}`, `{ИИ}`, `{AI}`.

## 7. Check locally, push, verify on the server

### 7a. Local check

```bash
python3 - <<'EOF'
import re, collections
txt = open('/Users/cartago/Library/CloudStorage/Dropbox/repos/babel-refs/bib/db.bib').read()
keys = re.findall(r'^@\w+\{([^,]+),', txt, re.M)
print('entries:', len(keys),
      '| duplicates:', [k for k,v in collections.Counter(keys).items() if v>1])
for key in ['<list every key you wrote>']:
    m = re.search(r'@\w+\{'+re.escape(key)+r',\n(.*?)\n\}\n', txt, re.S)
    if not m: print(key, 'MISSING'); continue
    b = m.group(1)
    print(key, 'braces', 'ok' if b.count('{')==b.count('}') else 'UNBALANCED',
          '|', re.findall(r'^\t(\w+) = ', b, re.M),
          '| AI label' if re.search(r'generad|generated|生成的摘要|сгенерирован|generato', b) else '')
EOF
```

Check: entry count rose by exactly the number you appended (run this same script before
appending to get the baseline — other counting methods, like `grep -c '^@'`, give a
different total); **zero** duplicate keys;
braces balanced in every new entry; no AI label; each translation's field list matches
its siblings (Es/It carry `journaltitle`, Ru/Zh do not); every `translation = {…}`
target exists. Fix anything wrong before pushing.

### 7b. Find the Emacs server

All pushing goes through the user's running Emacs (package `tlon`), which holds the API
credentials. The socket is not the default one:

```bash
ls $TMPDIR/emacs$(id -u)/        # e.g. server54720 — use it as -s NAME
```

Calling `emacsclient --eval` is not a signal to the process. **Never kill or restart Emacs.**

### 7c. Push — original first, then translations

The original must be on the server before any translation that points to it, so put it
first in the list. If the original already existed (bibkey target), list only the
translations.

First refresh the key cache of the `db.bib` buffer. If Emacs has `db.bib` open, it
reverts the buffer when you append, but its `bibtex-reference-keys` cache still lists
only the old keys. `tlon-db-post-entry` looks keys up through that cache, so it finds
nothing, POSTs an empty body and returns `nil` (see the table below). Re-parse the keys
and check the count matches the §7a total, and that a new key is found:

```bash
emacsclient -s <SOCKET> --eval '
(format "%S"
  (with-current-buffer (find-file-noselect tlon-file-db)
    (setq bibtex-reference-keys (lazy-completion-table bibtex-reference-keys bibtex-parse-keys))
    (bibtex-parse-keys)
    (list (length bibtex-reference-keys)
          (let ((bibtex-files (list tlon-file-db)))
            (substring (bibtex-extras-get-entry-as-string "OriginalKey" nil) 0 40)))))'
```

Then push:

```bash
emacsclient -s <SOCKET> --eval '
(let ((bibtex-files (list tlon-file-db))
      (tlon-db--sync-in-progress t))
  (mapcar (lambda (k) (cons k (condition-case e (tlon-db-post-entry k) (error (format "ERR %S" e)))))
          (list "OriginalKey" "OriginalKeyEs" "OriginalKeyZh")))'
```

- `bibtex-files` bound to `tlon-file-db` makes it post the version you just wrote in `db.bib`.
- `tlon-db--sync-in-progress` set to `t` stops `tlon-db-post-entry` from asking with `y-or-n-p` (which would block emacsclient) when the server rejects an entry because an author is not in the name table.

Read each result:

| Result | Meaning | Action |
|---|---|---|
| `t` | posted (HTTP 200); the entry in `db.bib` was rewritten with the server's version | verify (§7d) |
| `nil` | skipped: an author is missing from the name table, or another non-200 | read the log (below) |
| `"ERR (buffer-read-only #<buffer db.bib>)"` | the POST succeeded; only the local mirror failed because `db.bib` is open read-only (Ebib makes it so on load/reload). Fixed in `tlon.el` 82086107, so this means Emacs is running older code | verify (§7d); tell the user, and expect `db-upstream.bib` to be stale until the next refresh |
| other `"ERR …"` | failed | report it; do not retry blindly |

On `nil`, read the log:

```bash
emacsclient -s <SOCKET> --eval '(with-current-buffer (get-buffer-create tlon-db--sync-log-buffer-name) (buffer-substring-no-properties (max (point-min) (- (point-max) 2000)) (point-max)))'
```

If the log says nothing about your keys, the failure was some other non-200, shown in
the `*Db API Result*` buffer:

```bash
emacsclient -s <SOCKET> --eval '(with-current-buffer "*Db API Result*" (buffer-substring-no-properties (point-min) (min (point-max) 2000)))'
```

`422` with `Field: body, Error: Field required` means the entry text was empty: the key
was not found because the key cache was stale. Nothing reached the server. Refresh the
cache (above) and push again.

If it says an author is missing, first check that the name is spelled exactly as on the
work's byline, then add it and push that entry (and its translations) again:

```bash
emacsclient -s <SOCKET> --eval '(tlon-db-set-name "Last, First")'
```

Do **not** pass the FORCE argument without asking the user: a conflict means a similar
name already exists (maybe the same person spelled differently), and the user decides.

### 7d. Verify against the server — required

Do not report success from the local files. For every key you pushed:

```bash
emacsclient -s <SOCKET> --eval '
(let ((r (tlon-db--handle-entry-request "GET" "/api/entries/KEY" nil (quote (("accept" . "text/plain"))) nil)))
  (list (plist-get r :status) (tlon-db--get-response-body (plist-get r :raw-text))))'
```

The body comes back as undecoded UTF-8 bytes. To compare many entries, write them to
files from Emacs, but decode first and bind the write coding system:

```bash
emacsclient -s <SOCKET> --eval '
(let* ((r (tlon-db--handle-entry-request "GET" "/api/entries/KEY" nil (quote (("accept" . "text/plain"))) nil))
       (body (decode-coding-string (or (tlon-db--get-response-body (plist-get r :raw-text)) "") (quote utf-8)))
       (coding-system-for-write (quote utf-8-unix)))
  (with-temp-file "<scratchpad>/srv-KEY.txt"
    (insert (format "%s\n" (plist-get r :status)) body))
  nil)'
```

Without the decoding, any non-ASCII character (the `ö` in `Tlön` is in every entry)
makes Emacs open a "select coding system" prompt in the user's session. That blocks
Emacs, and every later `emacsclient` call, until the user dismisses it. Wrap each call
in `timeout 30` so a blocked Emacs fails fast instead of hanging.

Status 200 plus the BibTeX means the entry is in the database. Compare the returned
fields with what you wrote (title, author, `translation`, abstract) — the server may
normalize some fields; report anything it dropped or changed. Status 404 means the push
did not land.

Afterwards, make sure no key you pushed also lives in `fluid.bib`/`stable.bib` (a key
must live in only one place). If one does, remove it there and commit that change
(those files are tracked). Never commit `db.bib`.

Delete the scratchpad copy once every entry is verified on the server.

## 8. Report

1. The bibkeys created, the `@type` used, and the server status of each (200 / not pushed and why).
2. Any bibliographic field you could not verify and omitted — explicitly, so the user can spot-check.
3. Whether the abstract is the publisher's/author's or a summary you wrote.
4. **Glossary findings**: which terms matched, which mandated renderings you applied (title and abstract), which languages had no glossary entry for a matched term and what convention you followed instead, and any place you deliberately departed from the glossary (with the reason).
5. The limits of your glossary check — literal English-substring matching misses concepts phrased differently — and whether you ran the reverse-check of §6b.
6. Any name you added to the name table, and anything that needs the user's decision (e.g. a name conflict).
