# Russian citation styles

These four styles follow the shared `../*-template.csl` structure rather than
introducing a different bibliography standard:

- `long.csl`: full, linked bibliography entry.
- `short.csl`: title-only linked entry.
- `long-audio.csl`: authors and title, without Markdown links.
- `short-audio.csl`: title only, without Markdown links.

Russian adaptations use `ru-RU`, «outer quotes» and „inner quotes“, `и` between
names, `и др.` in written citations, and `и другие` in audio. Contributor labels,
volume labels and literal template phrases are translated. English-style title
casing is removed so titles retain their supplied capitalization. Full dates in
the long style use genitive months (e.g. `15 марта`). The existing template's
citation layout and type-specific behavior are otherwise retained; this is a
best-effort localization, not a claim of GOST compliance.

`../../locales/locales-ru-RU.xml` is the upstream CSL Russian locale:
https://github.com/citation-style-language/locales/blob/master/locales-ru-RU.xml
Its contributor and license metadata are preserved. The citation API also needs
the identical file at `uqbar-api-node/locales/locales-ru-RU.xml`, since its bundled
citation-js locales do not include Russian. The API registers it at startup.

Smoke-tested with the project's citation-js engine using book, journal article,
webpage, edited chapter, missing-date, and four-author examples across all four
styles. Native-speaker review is still welcome. Template quirks unrelated to
Russian (such as trailing punctuation on sparse records) are not changed here.

Deployment: publish the babel-refs files and the uqbar-api-node submodule change,
pin that submodule in uqbar, then rebuild Russian content. Merely editing this
checkout does not change the git-fetcher's remote content. Missing Russian
abstract translations are separate from these citation styles.
