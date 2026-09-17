---
name: db-cite
description: From a URL, create a proper bibliography entry in bib/db.bib, then create translation entries (Es, It, Ru, Zh…) for it, consulting the Tlön glossary. Use when the user gives a link and wants it added to db.bib, or asks for translation entries of an existing db.bib bibkey.
---

# /db-cite

Import a work from a link into `bib/db.bib`, then generate translation entries for it.

This is the `db.bib` counterpart of `uqbar-en`'s `/cite`. Entry-construction rules
(bibkey form, union-of-fields template, web verification, no fabrication) are the same;
the destination, the field set, and the translation step are different.

```
/db-cite <url> [Es It Ru Zh …]
/db-cite <BibKey> [Es It Ru Zh …]     # original already in db.bib; only translate
```

## Paths

| What | Where |
|---|---|
| Destination | `/Users/cartago/Library/CloudStorage/Dropbox/repos/babel-refs/bib/db.bib` |
| Also search | `bib/stable.bib`, `bib/fluid.bib`, `bib/db-upstream.bib` (same dir) |
| Glossary | `/Users/cartago/Library/CloudStorage/Dropbox/repos/babel-core/glossary.json` |
| Legacy MT abstracts | `json/<lang>/abstract-translations.json` (reference only — see §6c) |

`bib/db.bib` is **gitignored**. It is normally generated from the database, and the
other repos' instructions say "do not edit". This skill edits it deliberately: the user
writes entries here and pushes them to the database themselves. So: **append, never
rewrite; never commit; never reformat neighbouring entries.**

> **Entries written here are volatile.** `db.bib` is periodically regenerated from the
> database, which **silently destroys any local addition the user has not yet pushed**
> (observed 2026-09-17: a regeneration dropped four translation entries written the day
> before, and reordered the whole file). There is no git history to recover from — the
> file is gitignored — and the Emacs `db.bib~` backup is usually older still.
>
> Therefore:
> - Always **tell the user, at the end of the run, that the new entries must be pushed to the database before the next regeneration**, or they will be lost.
> - Before appending, check whether a regeneration has happened since you last touched the file (`ls -l bib/db.bib`, and re-grep for keys you wrote earlier in the session). If entries you created have vanished, say so rather than silently re-adding them.
> - Save a copy of everything you append to `<scratchpad>/db-cite-<date>.bib` so it can be replayed if a regeneration lands first.

## 0. Resolve arguments

Split `$ARGUMENTS` into (a) one target and (b) zero or more two-letter language codes.

- Target starts with `http://` / `https://` → import from the web (§1–§5).
- Target is a bare `AuthorYYYYWords` bibkey → the original already exists; verify it is in
  `db.bib` and skip to §6.
- No target → ask which link to import. Do not guess.

If no language codes were given, ask with `AskUserQuestion` (multi-select) which
translations to create; offer Es / It / Ru / Zh as the first options, since that is the
current standing set. An empty answer means "original only" — that is a valid outcome.

## 1. Fetch the work

`WebFetch` the URL. Extract: title, author(s), publishing venue, publication date, and
the real abstract if the page has one. If the page is a redirect, a paywall, or a
JS-only shell, `WebSearch` for the canonical record instead (publisher page, DOI landing
page, Crossref `https://api.crossref.org/works?query.title=…&query.author=…`).

## 2. Check for an existing entry — all four files

Search by **title** (case-insensitive) *and* by the **bibkey pattern** you are about to
propose, across all four bib files. `db.bib` and `db-upstream.bib` are generated and
routinely hold entries absent from `stable.bib`/`fluid.bib`; skipping them creates
duplicates.

```bash
cd /Users/cartago/Library/CloudStorage/Dropbox/repos/babel-refs/bib
grep -in "<distinctive title fragment>" stable.bib fluid.bib db.bib db-upstream.bib
grep -n "<ProposedBibKey>" stable.bib fluid.bib db.bib db-upstream.bib
```

If the work is already present anywhere, stop and report the existing bibkey. Do not
create a second entry, and do not edit the existing one. (It may still need
translations — offer §6.)

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
one blank line between entries.

```bibtex
@online{Christiano2019WhatFailureLooks,
	langid = {english},
	title = {What failure looks like},
	timestamp = {2026-09-16 15:35:29 (GMT)},
	author = {Christiano, Paul},
	alternateurls = {},
	journaltitle = {{LessWrong}},
	abstract = {… – AI-generated abstract.},
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
- `abstract`: prefer the publisher's real abstract. Fall back to an AI summary of 3–6 sentences ending ` – AI-generated abstract.`

## 6. Create the translation entries

One entry per requested language, key = `<OriginalBibKey><Xx>`.

### 6a. Language table

Derived from `db.bib`. `Venue` is the Tlön site the translation is published on — used as
`journaltitle`; languages with no Tlön site take **no** `journaltitle` field at all.

| Code | `langid` | `journaltitle` (venue) | AI-abstract closer |
|---|---|---|---|
| `Es` | spanish | `Altruismo Eficaz` | `– Resumen generado por IA.` |
| `It` | italian | `Altruismo Efficace` | `– Abstract generato dall’IA.` |
| `Fr` | french | `Altruisme Efficace` | `– Résumé généré par l'IA.` |
| `Ru` | russian | *(none)* | `— Аннотация, сгенерированная генеративным ИИ.` |
| `Zh` | chinese | *(none)* | `——AI生成的摘要。` |
| `Ja` | japanese | `効果的利他主義` | — |
| `Ko` | korean | `효과적 이타주의` | `– AI 생성 요약문.` |
| `Ar` | arabic | *(none)* | `– ملخص تم إنشاؤه بواسطة الذكاء الاصطناعي.` |
| `Tr` | turkish | `Efektif Altruizm` | `– AI tarafından oluşturulan özet.` |
| `Pl` | polish | *(none)* | `– Streszczenie wygenerowane przez sztuczną inteligencję.` |
| `Sr` | serbian | `Efektivni altruizam` | `– Apstrakt generisan veštačkom inteligencijom.` |
| `He` | hebrew | *(none)* | `– תקציר שנוצר על ידי בינה מלאכותית.` |
| `Pt` | portuguese | *(none)* | `– Resumo gerado por IA.` |
| `Cs` | czech | `Efektivní altruismus` | — |

Some of these closers are split in the corpus (It also has "…dall'intelligenza
artificiale.", Ru also "…сгенерированная ИИ.", Zh also "– 由 AI 生成的摘要。"). Before
writing, check what the **most recent** sibling entries use and follow that:

```bash
grep -A2 'langid = {russian}' bib/db.bib | grep -o '[–—][^}]\{0,45\}$' | tail -20
```

For a language not in the table, derive `langid`, venue and closer the same way — from
existing entries with that suffix — and say in the report that you did.

### 6b. Consult the glossary — required, and show your work

Load `babel-core/glossary.json`: a list of ~2,000 objects, each `{"en": …, "type":
"variable"|"invariant", "es": …, "it": …, "ru": …, "zh": …, …}`.

- `variable` → the given target-language string is the **mandated** rendering.
- `invariant` → the term is **not** translated (org names, product names); use the target-language field if present, otherwise keep the English.
- A term with **no field for your language** carries no mandate — choose freely, and flag it in the report.

Run this before drafting, on the original title + abstract:

```bash
python3 - <<'EOF'
import json, re
GLOSS='/Users/cartago/Library/CloudStorage/Dropbox/repos/babel-core/glossary.json'
SRC = """<paste the English title and abstract here>"""
LANGS = ['es','it','ru','zh']            # adjust to the requested set
d = json.load(open(GLOSS)); hay = SRC.lower()
hits = [e for e in d if len(e.get('en',''))>3
        and re.search(r'(?<![a-z])'+re.escape(e['en'].lower())+r'(?![a-z])', hay)]
hits.sort(key=lambda e: -len(e['en']))
for e in hits:
    print(e['type'].ljust(9), e['en'], '→',
          {l: e.get(l, '—— NO ENTRY ——') for l in LANGS})
EOF
```

Then **draft** each translation applying every mandate, and **reverse-check** the draft:
grep your finished target-language text for any string the glossary assigns to a
*different* English term, which would silently collide. Longer glossary keys win over
shorter ones (`AI safety` beats `safety`).

Titles are **not** in the glossary — it holds terminology, not work titles. So a title is
your own rendering; where a glossary compound contains the key word (e.g. `malignant AI
failure mode` → ru `провал`, it `fallimento`), follow it unless the sense differs, and
say so in the report when you depart from it.

### 6c. Reference, don't copy, the legacy MT

`json/<lang>/abstract-translations.json` may already hold an abstract for this bibkey.
These are **older raw machine translations**; every sampled overlap with `db.bib`
differs, and the `db.bib` versions are visibly better edited. Use them as a starting
reference and improve; never paste them in verbatim.

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
	abstract = {… – Resumen generado por IA.},
	date = {2026-09-16},
	database = {Tlön}
}
```

- `author` — the **original** author, unchanged. Never translate or transliterate a name.
- `translation = {<OriginalBibKey>}` — this is what links the entry to its original.
- `date` — the translation's own publication date, i.e. **today** for a newly created one (not the original's date).
- `translator` — only when a named human or org translated it. Omit for a fresh Tlön translation.
- `url` — only if the translation is already published somewhere. Omit otherwise; most recent Tlön translation entries have no `url`.
- `file` — omit.
- Brace-protect acronyms in the translated title too: `{IA}`, `{ИИ}`, `{AI}`.

## 7. Verify, then report

Run these; do not report success without them:

```bash
python3 - <<'EOF'
import re, collections
txt = open('bib/db.bib').read()
keys = re.findall(r'^@\w+\{([^,]+),', txt, re.M)
print('entries:', len(keys),
      '| duplicates:', [k for k,v in collections.Counter(keys).items() if v>1])
for key in ['<list every key you wrote>']:
    m = re.search(r'@\w+\{'+re.escape(key)+r',\n(.*?)\n\}\n', txt, re.S)
    if not m: print(key, 'MISSING'); continue
    b = m.group(1)
    print(key, 'braces', 'ok' if b.count('{')==b.count('}') else 'UNBALANCED',
          '|', re.findall(r'^\t(\w+) = ', b, re.M))
EOF
```

Check: entry count rose by exactly the number you appended; **zero** duplicate keys;
braces balanced in every new entry; each translation's field list matches its siblings
(Es/It carry `journaltitle`, Ru/Zh do not); every `translation = {…}` target exists.

Do **not** commit — `db.bib` is gitignored and the user pushes it to the database.

Report:

1. The new bibkeys, and the `@type` used.
2. Any bibliographic field you could not verify and omitted — explicitly, so the user can spot-check.
3. Whether the abstract is the publisher's or AI-generated.
4. **Glossary findings**: which terms matched, which mandated renderings you applied, which languages had no glossary entry for a matched term, and any place you deliberately departed from a glossary compound (with the reason).
5. The limits of your glossary check — literal English-substring matching misses concepts phrased differently, and state whether you ran the reverse-check of §6b.
