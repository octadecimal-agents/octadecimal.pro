import re

_STRIP_LINE = re.compile(r"^\s*<link\s+rel=.stylesheet.*>\s*$", re.MULTILINE | re.IGNORECASE)
_HTML_TAG = re.compile(r"<[^>]+>")
_NAV_LINE = re.compile(r"^\s*\[←.*\]\(.*\)\s*$", re.MULTILINE)
_SECTION_BREAK = re.compile(r'<div class="section-break">[^<]*</div>', re.IGNORECASE)


def clean_markdown_for_embed(raw: str) -> str:
    text = _STRIP_LINE.sub("", raw)
    text = _SECTION_BREAK.sub("\n", text)
    text = _HTML_TAG.sub(" ", text)
    text = _NAV_LINE.sub("", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
