"""Render a snippet of Python as a dark editor screenshot.

The bootcamp documents show code as images captured from an editor rather
than as selectable text, so this reproduces that look: dark ground, Consolas,
and enough syntax colour to read at a glance.
"""

from __future__ import annotations

import keyword
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_REGULAR = r"C:\Windows\Fonts\consola.ttf"
FONT_BOLD = r"C:\Windows\Fonts\consolab.ttf"

# VS Code Dark+, near enough to match the captures in the source document.
BG = (30, 30, 30)
FG = (212, 212, 212)
COMMENT = (106, 153, 85)
STRING = (206, 145, 120)
KEYWORD = (86, 156, 214)
BUILTIN = (78, 201, 176)
FUNC = (220, 220, 170)
NUMBER = (181, 206, 168)
DECORATOR = (220, 220, 170)

SCALE = 2  # render at 2x so the image stays crisp when placed in the PDF
FONT_SIZE = 15 * SCALE
LINE_H = 22 * SCALE
PAD = 22 * SCALE

_BUILTINS = {
    "self", "str", "int", "float", "bool", "list", "dict", "set", "tuple",
    "len", "print", "open", "range", "isinstance", "getattr", "super", "None",
    "True", "False", "Exception", "ValueError",
}

_TOKEN = re.compile(
    r"""(?P<comment>\#[^\n]*)
      | (?P<string>(?:'''.*?'''|\"\"\".*?\"\"\"|'[^'\n]*'|\"[^\"\n]*\"))
      | (?P<decorator>@[\w.]+)
      | (?P<number>\b\d+\.?\d*\b)
      | (?P<word>\b\w+\b)
      | (?P<other>.)""",
    re.VERBOSE | re.DOTALL,
)


def _colour_for(kind: str, text: str, following: str) -> tuple[int, int, int]:
    if kind == "comment":
        return COMMENT
    if kind == "string":
        return STRING
    if kind == "decorator":
        return DECORATOR
    if kind == "number":
        return NUMBER
    if kind == "word":
        if keyword.iskeyword(text):
            return KEYWORD
        if text in _BUILTINS:
            return BUILTIN
        if following.lstrip().startswith("("):
            return FUNC
    return FG


def render_code(code: str, destination: Path, max_width_chars: int = 92) -> Path:
    """Write ``code`` to ``destination`` as a PNG and return the path."""
    lines = [ln.rstrip() for ln in code.strip("\n").split("\n")]
    # Hard-wrap anything absurdly long so the image keeps a sane aspect ratio.
    wrapped: list[str] = []
    for line in lines:
        while len(line) > max_width_chars:
            cut = line.rfind(" ", 0, max_width_chars)
            cut = cut if cut > 40 else max_width_chars
            wrapped.append(line[:cut])
            line = "    " + line[cut:].lstrip()
        wrapped.append(line)
    lines = wrapped

    font = ImageFont.truetype(FONT_REGULAR, FONT_SIZE)
    char_w = font.getlength("M")

    width = int(PAD * 2 + char_w * max((len(ln) for ln in lines), default=40))
    width = max(width, 640 * SCALE)
    height = int(PAD * 2 + LINE_H * len(lines))

    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)

    y = PAD
    for line in lines:
        x = PAD
        for match in _TOKEN.finditer(line):
            kind = match.lastgroup or "other"
            text = match.group()
            following = line[match.end():]
            draw.text((x, y), text, font=font, fill=_colour_for(kind, text, following))
            x += font.getlength(text)
        y += LINE_H

    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)
    return destination
