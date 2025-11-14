from pathlib import Path

locales = {
    "ar": "ar-SA",
    "es": "es-ES",
    "fr": "fr-FR",
    "it": "it-IT",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "tr": "tr-TR",
}

csl_filenames = [
    "long-audio-template.csl",
    "long-template.csl",
    "short-audio-template.csl",
    "short-template.csl",
]


current_dir = Path(__file__).resolve().parent
for language, locale in locales.items():
    if not (current_dir / language).exists():
        (current_dir / language).mkdir()
    for csl_filename in csl_filenames:
        with open(current_dir / csl_filename, "r", encoding="utf-8") as f:
            content = f.read()
        localized_content = (
            content.replace("$$FULL_LOCALE$$", locale)
            .replace("${FULL_LOCALE}", locale)
            .replace("${CONTENT_LANGUAGE}", language)
        )
        with open(
            current_dir / language / csl_filename.replace("-template", ""),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(localized_content)
print("Localized CSL styles generated.")
