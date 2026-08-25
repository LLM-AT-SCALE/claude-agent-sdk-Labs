"""Page furniture and layout primitives for the lab guide.

Geometry and colours are measured from the existing bootcamp document so the
two sit side by side: 1080x1500pt page, hairline rule under the top edge, the
robot mascot carrying the page number at top right, and the blue/green/purple
bar across the foot.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

# ---------------------------------------------------------------- geometry --

PAGE_W, PAGE_H = 1080.0, 1500.0

MARGIN_L = 68.0
MARGIN_R = 68.0
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

TOP_Y = PAGE_H - 150.0      # first baseline of body content
BOTTOM_Y = 95.0             # stop before the footer

TOP_RULE_Y = PAGE_H - 31.0
MASCOT_RECT = (943.2, PAGE_H - 158.6, 107.7, 107.7)   # x, y, w, h
MASCOT_SHADOW = (954.6, PAGE_H - 174.3, 84.9, 7.2)

# The green chevron under the mascot's head is drawn as vector art in the
# source document, not baked into the image. Measured from its page 3.
# Grown ~2pt beyond the measured rect: the mascot JPEG has its own amber
# chevron underneath, and an exact-size overlay leaves an orange fringe.
MASCOT_CHEVRON = (985.0, 1009.3, PAGE_H - 118.0, PAGE_H - 130.2)  # x0, x1, y_top, y_tip
CHEVRON_GREEN = HexColor("#3FBA8D")

# Page number: DMSans-Bold 12pt, #333333, baseline 145pt from the top edge.
PAGE_NUM_XY = (997.1, PAGE_H - 145.0)

FOOTER_BAR_H = 22.0
FOOTER_TEXT_Y = 38.0

# ------------------------------------------------------------------ colours --

GREEN = HexColor("#29B28C")        # banner fill
GREEN_DEEP = HexColor("#1DAE85")   # chevron / accents
GREEN_TINT = HexColor("#C7E5D5")   # card headers
GREY_HEAD = HexColor("#E5E5E5")    # step heading background
RULE = HexColor("#E5E5E5")
INK = HexColor("#333333")
INK_SOFT = HexColor("#5A5A5A")
WHITE = HexColor("#FFFFFF")
FOOTER_BLUE = HexColor("#5671BB")
FOOTER_GREEN = HexColor("#1DAE85")
FOOTER_PURPLE = HexColor("#826DC4")
CARD_BORDER = HexColor("#D8D8D8")
CALLOUT_BG = HexColor("#F4F8F6")

FOOTER_TEXT = (
    "\u00a9 LLM at Scale.AI | Confidential and Proprietary | Not for Distribution | "
    "A step-by-step guide to designing, developing, and deploying an application. | "
    "admin@llmatscale.ai"
)

# -------------------------------------------------------------------- fonts --

def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Segoe", r"C:\Windows\Fonts\segoeui.ttf"))
    pdfmetrics.registerFont(TTFont("Segoe-Bold", r"C:\Windows\Fonts\segoeuib.ttf"))
    pdfmetrics.registerFont(TTFont("Mono", r"C:\Windows\Fonts\consola.ttf"))
    pdfmetrics.registerFont(TTFont("Mono-Bold", r"C:\Windows\Fonts\consolab.ttf"))


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    """Greedy wrap that measures with the real font metrics."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if pdfmetrics.stringWidth(trial, font, size) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Doc:
    """A y-cursor over a canvas, with the page chrome drawn automatically."""

    def __init__(self, path: Path, assets: Path) -> None:
        register_fonts()
        self.path = path
        self.assets = assets
        self.c = rl_canvas.Canvas(str(path), pagesize=(PAGE_W, PAGE_H))
        self.c.setTitle("Lab 1 - Loan Application Evaluation")
        self.c.setAuthor("LLM at Scale.AI")
        self.page = 0
        self.y = TOP_Y
        self._chrome = True

    # -- page furniture ----------------------------------------------------

    def _draw_chrome(self) -> None:
        c = self.c

        c.setStrokeColor(RULE)
        c.setLineWidth(1.2)
        c.line(20, TOP_RULE_Y, PAGE_W - 20, TOP_RULE_Y)

        mascot = self.assets / "mascot.jpg"
        if mascot.exists():
            x, y, w, h = MASCOT_RECT
            c.drawImage(ImageReader(str(mascot)), x, y, w, h, mask="auto")
        shadow = self.assets / "stripe.png"
        if shadow.exists():
            x, y, w, h = MASCOT_SHADOW
            c.drawImage(ImageReader(str(shadow)), x, y, w, h, mask="auto")

        x0, x1, y_top, y_tip = MASCOT_CHEVRON
        chevron = c.beginPath()
        chevron.moveTo(x0, y_top)
        chevron.lineTo(x1, y_top)
        chevron.lineTo((x0 + x1) / 2, y_tip)
        chevron.close()
        c.setFillColor(CHEVRON_GREEN)
        c.drawPath(chevron, stroke=0, fill=1)

        c.setFillColor(INK)
        c.setFont("Segoe-Bold", 13)
        c.drawCentredString(PAGE_NUM_XY[0], PAGE_NUM_XY[1], str(self.page))

        # dotted rule above the footer text
        c.setStrokeColor(HexColor("#CFCFCF"))
        c.setLineWidth(0.8)
        c.setDash(1, 3)
        c.line(MARGIN_L, FOOTER_TEXT_Y + 18, PAGE_W - MARGIN_R, FOOTER_TEXT_Y + 18)
        c.setDash()

        c.setFillColor(HexColor("#6A6A6A"))
        c.setFont("Segoe", 9.5)
        c.drawString(MARGIN_L, FOOTER_TEXT_Y, FOOTER_TEXT)

        third = PAGE_W / 3.0
        for index, colour in enumerate((FOOTER_BLUE, FOOTER_GREEN, FOOTER_PURPLE)):
            c.setFillColor(colour)
            c.rect(index * third, 0, third + 1, FOOTER_BAR_H, stroke=0, fill=1)

    def new_page(self, chrome: bool = True) -> None:
        if self.page:
            self.c.showPage()
        self.page += 1
        self.y = TOP_Y
        if chrome:
            self._draw_chrome()

    def need(self, height: float) -> None:
        """Break to a new page when ``height`` will not fit."""
        if self.y - height < BOTTOM_Y:
            self.new_page()

    def space(self, height: float) -> None:
        self.y -= height

    # -- content -----------------------------------------------------------

    def running_head(self, text: str) -> None:
        """The angled green/white banner used at the top of a section page."""
        c = self.c
        y = PAGE_H - 118.0
        c.setFillColor(GREEN_DEEP)
        c.rect(MARGIN_L - 26, y, 14, 62, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Segoe-Bold", 30)
        c.drawString(MARGIN_L, y + 18, "")
        c.setFillColor(INK)
        c.drawString(MARGIN_L, y + 18, text)
        self.y = y - 46

    def banner(self, text: str, width: float = 300.0) -> None:
        """Green banner heading with the clipped corner, e.g. 'Disclaimer'."""
        self.need(90)
        c = self.c
        h = 52.0
        y = self.y - h
        notch = 22.0
        path = c.beginPath()
        path.moveTo(MARGIN_L, y)
        path.lineTo(MARGIN_L + width - notch, y)
        path.lineTo(MARGIN_L + width, y + h / 2)
        path.lineTo(MARGIN_L + width - notch, y + h)
        path.lineTo(MARGIN_L, y + h)
        path.close()
        c.setFillColor(GREEN)
        c.drawPath(path, stroke=0, fill=1)

        c.setFillColor(WHITE)
        c.setFont("Segoe-Bold", 26)
        c.drawString(MARGIN_L + 22, y + 16, text)
        self.y = y - 26

    def grey_head(self, text: str, size: float = 24.0) -> None:
        """Grey-backed step heading, e.g. 'Step 7: Understanding src/validate.py'."""
        self.need(96)
        c = self.c
        pad_x, pad_y = 18.0, 12.0
        text_w = pdfmetrics.stringWidth(text, "Segoe-Bold", size)
        h = size + pad_y * 2
        y = self.y - h
        c.setFillColor(GREY_HEAD)
        c.rect(MARGIN_L, y, text_w + pad_x * 2, h, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Segoe-Bold", size)
        c.drawString(MARGIN_L + pad_x, y + pad_y + 3, text)
        self.y = y - 26

    def heading(self, text: str, size: float = 26.0) -> None:
        self.need(70)
        self.c.setFillColor(INK)
        self.c.setFont("Segoe-Bold", size)
        self.y -= size + 6
        self.c.drawString(MARGIN_L, self.y, text)
        self.y -= 16

    def body(self, text: str, size: float = 15.5, colour: Color = INK,
             font: str = "Segoe", leading: float = 25.0, indent: float = 0.0) -> None:
        lines = wrap(text, font, size, CONTENT_W - indent)
        self.need(len(lines) * leading + 8)
        self.c.setFillColor(colour)
        self.c.setFont(font, size)
        for line in lines:
            self.y -= leading
            self.c.drawString(MARGIN_L + indent, self.y, line)
        self.y -= 10

    def rich(self, parts: list[tuple[str, bool]], size: float = 15.5,
             leading: float = 25.0, indent: float = 0.0) -> None:
        """A paragraph mixing regular and bold runs: [(text, is_bold), ...]."""
        words: list[tuple[str, bool]] = []
        for text, bold in parts:
            for word in text.split(" "):
                if word:
                    words.append((word, bold))

        lines: list[list[tuple[str, bool]]] = [[]]
        widths = [0.0]
        space_w = pdfmetrics.stringWidth(" ", "Segoe", size)
        for word, bold in words:
            font = "Segoe-Bold" if bold else "Segoe"
            w = pdfmetrics.stringWidth(word, font, size)
            extra = w if not lines[-1] else space_w + w
            if widths[-1] + extra > CONTENT_W - indent and lines[-1]:
                lines.append([(word, bold)])
                widths.append(w)
            else:
                lines[-1].append((word, bold))
                widths[-1] += extra

        self.need(len(lines) * leading + 8)
        for line in lines:
            self.y -= leading
            x = MARGIN_L + indent
            for i, (word, bold) in enumerate(line):
                font = "Segoe-Bold" if bold else "Segoe"
                self.c.setFont(font, size)
                self.c.setFillColor(INK)
                self.c.drawString(x, self.y, word)
                x += pdfmetrics.stringWidth(word, font, size)
                if i != len(line) - 1:
                    x += space_w
        self.y -= 10

    def bullets(self, items: list[str], size: float = 15.5, indent: float = 26.0,
                bullet: str = "\u2022") -> None:
        for item in items:
            lines = wrap(item, "Segoe", size, CONTENT_W - indent - 20)
            self.need(len(lines) * 24 + 6)
            self.c.setFillColor(INK)
            self.c.setFont("Segoe", size)
            for i, line in enumerate(lines):
                self.y -= 24
                if i == 0:
                    self.c.drawString(MARGIN_L + indent, self.y, bullet)
                self.c.drawString(MARGIN_L + indent + 20, self.y, line)
            self.y -= 6
        self.y -= 6

    def numbered(self, items: list[str], size: float = 15.5, start: int = 1,
                 indent: float = 8.0) -> None:
        for n, item in enumerate(items, start=start):
            label = f"{n}."
            lines = wrap(item, "Segoe", size, CONTENT_W - indent - 30)
            self.need(len(lines) * 24 + 6)
            self.c.setFillColor(INK)
            for i, line in enumerate(lines):
                self.y -= 24
                if i == 0:
                    self.c.setFont("Segoe-Bold", size)
                    self.c.drawString(MARGIN_L + indent, self.y, label)
                self.c.setFont("Segoe", size)
                self.c.drawString(MARGIN_L + indent + 30, self.y, line)
            self.y -= 6
        self.y -= 6

    def card_row(self, cards: list[tuple[str, str]]) -> None:
        """The green-headed cards used for 'Source Code Organization'."""
        gap = 30.0
        n = len(cards)
        w = (CONTENT_W - gap * (n - 1)) / n

        bodies = [wrap(text, "Segoe", 14.5, w - 36) for _, text in cards]
        body_h = max(len(b) for b in bodies) * 23 + 34
        head_h = 48.0
        total = head_h + body_h

        self.need(total + 30)
        top = self.y

        for i, ((title, _), lines) in enumerate(zip(cards, bodies)):
            x = MARGIN_L + i * (w + gap)
            c = self.c
            c.setFillColor(GREEN_TINT)
            c.roundRect(x, top - total, w, total, 12, stroke=0, fill=1)
            c.setFillColor(WHITE)
            c.setStrokeColor(HexColor("#E2E2E2"))
            c.setLineWidth(1)
            c.roundRect(x + 6, top - total + 8, w - 12, body_h, 10, stroke=1, fill=1)

            c.setFillColor(INK)
            c.setFont("Segoe-Bold", 20)
            c.drawCentredString(x + w / 2, top - 34, title)

            c.setFont("Segoe", 14.5)
            c.setFillColor(INK)
            ty = top - head_h - 16
            for line in lines:
                c.drawString(x + 24, ty, line)
                ty -= 23

        self.y = top - total - 26

    def outlined_box(self, label: str, value: str) -> None:
        """Rounded outline box, as used for the GitHub link."""
        self.need(120)
        c = self.c
        h = 104.0
        y = self.y - h
        c.setStrokeColor(HexColor("#BFBFBF"))
        c.setFillColor(WHITE)
        c.setLineWidth(1.4)
        c.roundRect(MARGIN_L, y, CONTENT_W, h, 14, stroke=1, fill=1)
        c.setFillColor(INK)
        c.setFont("Segoe-Bold", 21)
        c.drawString(MARGIN_L + 26, y + h - 38, label)
        c.setFont("Segoe", 16)
        c.drawString(MARGIN_L + 26, y + 26, value)
        self.y = y - 26

    def chevron(self, text: str) -> None:
        """Green arrow banner, e.g. 'Summary of Steps Performed in the Document'."""
        self.need(90)
        c = self.c
        h = 54.0
        y = self.y - h
        w = pdfmetrics.stringWidth(text, "Segoe-Bold", 24) + 70
        tip = 26.0
        path = c.beginPath()
        path.moveTo(MARGIN_L, y)
        path.lineTo(MARGIN_L + w, y)
        path.lineTo(MARGIN_L + w + tip, y + h / 2)
        path.lineTo(MARGIN_L + w, y + h)
        path.lineTo(MARGIN_L, y + h)
        path.close()
        c.setFillColor(GREEN)
        c.drawPath(path, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Segoe-Bold", 24)
        c.drawString(MARGIN_L + 24, y + 17, text)
        self.y = y - 28

    def picture(self, path: Path, caption: str | None = None,
                max_w: float | None = None) -> None:
        """Place a screenshot inside the grey mount the source document uses."""
        if not path.exists():
            return
        reader = ImageReader(str(path))
        iw, ih = reader.getSize()
        target_w = min(max_w or CONTENT_W, CONTENT_W)
        scale = target_w / iw
        target_h = ih * scale

        mount = 16.0
        self.need(target_h + mount * 2 + (30 if caption else 0) + 20)

        x = MARGIN_L + (CONTENT_W - target_w) / 2
        y = self.y - target_h - mount

        self.c.setFillColor(HexColor("#D9D9D9"))
        self.c.rect(x - mount, y - mount, target_w + mount * 2,
                    target_h + mount * 2, stroke=0, fill=1)
        self.c.drawImage(reader, x, y, target_w, target_h, mask="auto")

        self.y = y - mount - 18
        if caption:
            self.body(caption, size=13, colour=INK_SOFT, leading=20)

    def callout(self, text: str) -> None:
        lines = wrap(text, "Segoe", 15, CONTENT_W - 60)
        h = len(lines) * 24 + 34
        self.need(h + 20)
        c = self.c
        y = self.y - h
        c.setFillColor(CALLOUT_BG)
        c.rect(MARGIN_L, y, CONTENT_W, h, stroke=0, fill=1)
        c.setFillColor(GREEN_DEEP)
        c.rect(MARGIN_L, y, 6, h, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Segoe", 15)
        ty = y + h - 28
        for line in lines:
            c.drawString(MARGIN_L + 28, ty, line)
            ty -= 24
        self.y = y - 24

    def save(self) -> None:
        self.c.showPage()
        self.c.save()


    def prompt_box(self, label: str, text: str, who: str = "Human") -> None:
        """A verbatim prompt, quoted. Used to show what was actually typed."""
        lines = wrap(text, "Segoe", 15.5, CONTENT_W - 74)
        h = len(lines) * 26 + 66
        self.need(h + 20)
        c = self.c
        y = self.y - h

        c.setFillColor(HexColor("#F7F9F8"))
        c.rect(MARGIN_L, y, CONTENT_W, h, stroke=0, fill=1)
        c.setFillColor(GREEN_DEEP)
        c.rect(MARGIN_L, y, 6, h, stroke=0, fill=1)

        c.setFillColor(HexColor("#7A7A7A"))
        c.setFont("Segoe-Bold", 11)
        c.drawString(MARGIN_L + 30, y + h - 26, label.upper())

        tag_w = pdfmetrics.stringWidth(who, "Segoe-Bold", 11) + 22
        c.setFillColor(GREEN_TINT)
        c.roundRect(MARGIN_L + CONTENT_W - tag_w - 24, y + h - 32, tag_w, 22, 4,
                    stroke=0, fill=1)
        c.setFillColor(HexColor("#1F6B4E"))
        c.setFont("Segoe-Bold", 11)
        c.drawCentredString(MARGIN_L + CONTENT_W - tag_w / 2 - 24, y + h - 26, who)

        c.setFillColor(INK)
        c.setFont("Segoe", 15.5)
        ty = y + h - 54
        for line in lines:
            c.drawString(MARGIN_L + 30, ty, line)
            ty -= 26
        self.y = y - 24

    def table(self, headers: list[str], rows: list[list[str]],
              widths: list[float], size: float = 13.5) -> None:
        """A plain ruled table, as used for results and defect lists."""
        total = sum(widths)
        scale = CONTENT_W / total
        widths = [w * scale for w in widths]

        wrapped_rows = []
        for row in rows:
            cells = [wrap(str(cell), "Segoe", size, widths[i] - 20)
                     for i, cell in enumerate(row)]
            wrapped_rows.append((cells, max(len(cl) for cl in cells)))

        head_h = 34.0
        needed = head_h + sum(n * 21 + 16 for _, n in wrapped_rows)
        self.need(needed + 20)

        c = self.c
        y = self.y

        c.setFillColor(HexColor("#EFEFEF"))
        c.rect(MARGIN_L, y - head_h, CONTENT_W, head_h, stroke=0, fill=1)
        c.setFillColor(HexColor("#4A4A4A"))
        c.setFont("Segoe-Bold", 12)
        x = MARGIN_L
        for i, header in enumerate(headers):
            c.drawString(x + 10, y - head_h + 12, header)
            x += widths[i]
        y -= head_h

        for cells, n in wrapped_rows:
            row_h = n * 21 + 16
            c.setStrokeColor(HexColor("#DCDCDC"))
            c.setLineWidth(0.8)
            c.line(MARGIN_L, y - row_h, MARGIN_L + CONTENT_W, y - row_h)
            x = MARGIN_L
            for i, cell_lines in enumerate(cells):
                c.setFillColor(INK)
                c.setFont("Segoe", size)
                ty = y - 20
                for line in cell_lines:
                    c.drawString(x + 10, ty, line)
                    ty -= 21
                x += widths[i]
            y -= row_h

        self.y = y - 22
