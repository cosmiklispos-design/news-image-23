#!/usr/bin/env python3
"""Draw the news-image-20261123 poster: one 1024x1024 PNG summing up the
world news of Monday 23 November 2026, as a newspaper front page.

Run from the repository root:  python3 build/draw_poster.py
Writes entry.png next to main.ts.
"""

import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (22, 22, 22)
NAVY = (22, 35, 63)
RED = (178, 34, 34)
GREY = (90, 88, 82)
RULE = (180, 172, 155)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap using the real rendered widths."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# (kicker, colour, headline, summary)
STORIES = [
    (
        "WAR  ·  LIBYA",
        (150, 30, 30),
        "Ukraine sinks Russian ship off Libya",
        "Sea drones hit two Russian vessels at Benghazi; Kyiv says the "
        "corvette Merkury was sunk.",
    ),
    (
        "MARKETS",
        (20, 110, 60),
        "Nvidia brings back Huang; stocks roar back",
        "Huang returns as CEO 11 days after resigning; Nvidia jumps 33%, "
        "S&P 500 up 4.8%.",
    ),
    (
        "UKRAINE",
        (150, 30, 30),
        "Russian strike kills 11 in Dymer",
        "A drone strike partly destroys an apartment block near Kyiv; "
        "14 people are missing.",
    ),
    (
        "USA  ·  POLITICS",
        (25, 60, 140),
        "Democrats take biggest House majority since 1992",
        "Democrats hold at least 258 seats after flipping a North "
        "Carolina seat.",
    ),
    (
        "DIPLOMACY",
        (90, 40, 120),
        "Trump calls Putin \u2018my friend\u2019 after Shenzhen summit",
        "After meeting Putin and Xi Jinping in Shenzhen, Trump praises "
        "the Russian president.",
    ),
    (
        "MIDDLE EAST",
        (160, 90, 10),
        "Iran vows to fight US blockade",
        "Tehran vows to use all means against the US blockade; its army "
        "says it downed a US drone.",
    ),
    (
        "EUROPE",
        (10, 110, 110),
        "EU proposes 22nd Russia sanctions package",
        "The European Commission puts forward a new round of sanctions "
        "against Moscow.",
    ),
    (
        "USA  ·  TECH",
        (70, 70, 70),
        "FBI probes hack of police database",
        "The National Crime Information Center, used by police nationwide, "
        "was breached.",
    ),
]

LEAD_KICKER = "CLIMATE  ·  ANTALYA"
LEAD_HEAD = "COP31 ends with no deal"
LEAD_SUMMARY = (
    "UN climate talks in Antalya close two days late with no deal on fossil "
    "fuels or finance \u2014 the longest COP ever."
)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# --- masthead -------------------------------------------------------------
d.rectangle([0, 0, W, 92], fill=NAVY)
mast = font(SERIF_B, 58)
d.text((W / 2, 18), "THE WORLD TODAY", font=mast, fill=(255, 255, 255),
       anchor="ma")
date_f = font(SANS_B, 24)
d.text((W / 2, 100), "M O N D A Y ,  2 3  N O V E M B E R  2 0 2 6",
       font=date_f, fill=NAVY, anchor="ma")
d.rectangle([36, 134, W - 36, 138], fill=RED)

# --- lead story -----------------------------------------------------------
y = 156
kick_f = font(SANS_B, 20)
d.text((36, y), LEAD_KICKER, font=kick_f, fill=RED)
head_f = font(SERIF_B, 40)
y = draw_lines(d, wrap(d, LEAD_HEAD, head_f, 640), 36, y + 30, head_f, INK, 48)
sum_f = font(SANS, 23)
y = draw_lines(d, wrap(d, LEAD_SUMMARY, sum_f, 640), 36, y + 8, sum_f,
               (50, 50, 50), 30)

# Globe motif: a cracked globe beside the lead story.
cx, cy, r = 830, 240, 88
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=5)
d.ellipse([cx - r + 26, cy - r, cx + r - 26, cy + r], outline=NAVY, width=3)
d.line([cx - r, cy, cx + r, cy], fill=NAVY, width=3)
d.arc([cx - r, cy - 46, cx + r, cy + 46], start=200, end=340, fill=NAVY, width=3)
d.arc([cx - r, cy - 46, cx + r, cy + 46], start=20, end=160, fill=NAVY, width=3)
# crack across the globe
crack = [(cx - 70, cy - 78), (cx - 38, cy - 40), (cx - 58, cy - 8),
         (cx - 20, cy + 28), (cx - 42, cy + 62), (cx - 8, cy + 88)]
d.line(crack, fill=RED, width=6, joint="curve")
d.text((cx, cy + r + 12), "ANTALYA", font=font(SANS_B, 18), fill=GREY,
       anchor="ma")

# --- story grid: 2 columns x 4 rows ---------------------------------------
d.line([36, 360, W - 36, 360], fill=RULE, width=2)
d.line([W / 2, 372, W / 2, 956], fill=RULE, width=1)
cell_w, cell_h = 452, 146
top = 372
for i, (kicker, colour, head, summary) in enumerate(STORIES):
    col, row = i % 2, i // 2
    x = 36 + col * 488
    cy0 = top + row * cell_h
    d.text((x, cy0), kicker, font=font(SANS_B, 17), fill=colour)
    hf = font(SERIF_B, 24)
    lines = wrap(d, head, hf, cell_w)
    yy = draw_lines(d, lines[:2], x, cy0 + 26, hf, INK, 29)
    sf = font(SANS, 18)
    slines = wrap(d, summary, sf, cell_w)
    draw_lines(d, slines[:2], x, yy + 4, sf, (50, 50, 50), 23)
    if row < 3:
        d.line([36, cy0 + cell_h - 6, W - 36, cy0 + cell_h - 6],
               fill=RULE, width=1)

# --- footer ---------------------------------------------------------------
d.rectangle([0, 960, W, H], fill=NAVY)
foot = font(SANS, 16)
d.text((W / 2, 972), "Sources: Reuters  ·  Associated Press  ·  AFP  ·  Al Jazeera",
       font=foot, fill=(220, 220, 220), anchor="ma")
d.text((W / 2, 994),
       "All nine stories happened or were first reported on Monday 23 November 2026",
       font=foot, fill=(180, 180, 180), anchor="ma")

img.save("entry.png")
print("wrote entry.png")
