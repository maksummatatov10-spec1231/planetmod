#!/usr/bin/env python3
"""Cataclysm — procedural icon/sprite generator.

Draws all mod icons (items, fluids, technologies, achievements, planet, thumbnail)
as PNGs into graphics/. Pure Python + Pillow, deterministic, no external assets.
Palette follows docs/GRAPHICS.md (purple/teal/yellow-green storm identity).
"""
import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "graphics")
random.seed(1337)

# ---- palette ---------------------------------------------------------------
BG_NONE = (0, 0, 0, 0)
PURPLE = (91, 58, 166, 255)
PURPLE_DARK = (43, 27, 84, 255)
PURPLE_LIGHT = (151, 120, 255, 255)
STORM_YELLOW = (216, 255, 58, 255)
STORM_CYAN = (158, 255, 255, 255)
TEAL = (46, 224, 200, 255)
TEAL_DARK = (30, 111, 107, 255)
SILVER = (159, 182, 200, 255)
SILVER_LIGHT = (232, 251, 255, 255)
FLASK = (124, 92, 255, 255)
DARK_LINE = (20, 12, 40, 255)

# ---- helpers ---------------------------------------------------------------

def new_canvas(size):
    size = int(size)
    return Image.new("RGBA", (size, size), BG_NONE)


def poly(draw, pts, fill, outline=None, width=1):
    draw.polygon(pts, fill=fill, outline=outline)
    if outline and width > 1:
        draw.line(pts + [pts[0]], fill=outline, width=width, joint="curve")


def bolt(draw, x0, y0, x1, y1, width=3, color=STORM_YELLOW, glow=True, seed=7):
    """Zig-zag lightning bolt from (x0,y0) to (x1,y1)."""
    rng = random.Random(seed)
    n = 6
    pts = []
    for i in range(n + 1):
        t = i / n
        px = x0 + (x1 - x0) * t + (rng.random() - 0.5) * 10 * (1 - abs(2 * t - 1) * 0.6)
        py = y0 + (y1 - y0) * t
        pts.append((px, py))
    layer = new_canvas(max(x1, x0) + 30)
    d = ImageDraw.Draw(layer)
    d.line(pts, fill=color, width=width, joint="curve")
    if glow:
        layer = layer.filter(ImageFilter.GaussianBlur(2))
        d = ImageDraw.Draw(layer)
        d.line(pts, fill=color, width=width, joint="curve")
    draw.line(pts, fill=color, width=width, joint="curve")


def crystal_cluster(draw, cx, cy, s, color, hi, seed=1):
    """Cluster of faceted crystals. s = overall radius."""
    rng = random.Random(seed)
    for _ in range(4):
        offx = rng.randint(-int(s * 0.5), int(s * 0.5))
        offy = rng.randint(-int(s * 0.5), int(s * 0.5))
        h = int(s * rng.uniform(0.7, 1.15))
        w = int(s * rng.uniform(0.25, 0.4))
        tip = (cx + offx, cy - int(s) - offy // 2)
        bl = (cx + offx - w, cy - int(s * 0.25) + offy)
        br = (cx + offx + w, cy - int(s * 0.25) + offy)
        mid = (cx + offx + int(w * 0.3), cy - int(s * 0.55) + offy // 2)
        poly(draw, [tip, bl, mid, br], color, DARK_LINE, 2)
        poly(draw, [tip, mid, br], hi, DARK_LINE, 1)


def shard(draw, cx, cy, s, color, hi):
    """Single elongated shard (astrite)."""
    poly(draw, [(cx, cy - s), (cx - s * 0.35, cy + s * 0.4), (cx, cy + s * 0.15), (cx + s * 0.35, cy + s * 0.4)],
         color, DARK_LINE, 2)
    poly(draw, [(cx, cy - s), (cx, cy + s * 0.15), (cx + s * 0.35, cy + s * 0.4)], hi, DARK_LINE, 1)


def plate(draw, cx, cy, s, color, hi, w=0.32):
    """Isometric metal plate."""
    poly(draw, [(cx, cy - s * 0.75), (cx + s * 0.9, cy - s * 0.45), (cx + s * 0.9, cy + s * 0.35), (cx, cy + s * 0.05)],
         color, DARK_LINE, 2)
    poly(draw, [(cx, cy - s * 0.75), (cx - s * 0.9, cy - s * 0.45), (cx - s * 0.9, cy + s * 0.35), (cx, cy + s * 0.05)],
         color, DARK_LINE, 2)
    poly(draw, [(cx + s * 0.9, cy - s * 0.45), (cx + s * 0.9, cy + s * 0.35), (cx, cy + s * 0.95), (cx, cy + s * 0.05)],
         hi, DARK_LINE, 1)
    poly(draw, [(cx - s * 0.9, cy - s * 0.45), (cx - s * 0.9, cy + s * 0.35), (cx, cy + s * 0.95), (cx, cy + s * 0.05)],
         color, DARK_LINE, 1)


def flask(draw, cx, cy, s, liquid, liquid_hi, glow=None):
    """Science flask with liquid and optional lightning bolt."""
    neck = [(cx - s * 0.18, cy - s), (cx + s * 0.18, cy - s),
            (cx + s * 0.22, cy - s * 0.4), (cx + s * 0.6, cy + s * 0.55),
            (cx + s * 0.5, cy + s * 0.75), (cx - s * 0.5, cy + s * 0.75),
            (cx - s * 0.6, cy + s * 0.55), (cx - s * 0.22, cy - s * 0.4)]
    poly(draw, neck, (180, 200, 255, 90), DARK_LINE, 2)
    poly(draw, [(cx - s * 0.55, cy + s * 0.2), (cx + s * 0.55, cy + s * 0.2),
                (cx + s * 0.5, cy + s * 0.75), (cx - s * 0.5, cy + s * 0.75)],
         liquid, DARK_LINE, 1)
    poly(draw, [(cx - s * 0.4, cy + s * 0.42), (cx + s * 0.4, cy + s * 0.42),
                (cx + s * 0.5, cy + s * 0.75), (cx - s * 0.5, cy + s * 0.75)], liquid_hi, None)
    if glow:
        bolt(draw, cx - s * 0.15, cy - s * 0.55, cx + s * 0.1, cy + s * 0.1, width=2, color=glow, seed=3)


def droplet(draw, cx, cy, s, color, hi):
    poly(draw, [(cx, cy - s), (cx - s * 0.75, cy + s * 0.15), (cx, cy + s), (cx + s * 0.75, cy + s * 0.15)],
         color, DARK_LINE, 2)
    poly(draw, [(cx, cy - s * 0.4), (cx + s * 0.3, cy + s * 0.2), (cx, cy + s * 0.1)], hi, None)


def machine_box(draw, cx, cy, s, color, hi, accent=None, roof=None):
    """Simple isometric machine housing."""
    poly(draw, [(cx, cy - s * 0.7), (cx + s * 0.8, cy - s * 0.35), (cx + s * 0.8, cy + s * 0.35), (cx, cy + s * 0.0)],
         color, DARK_LINE, 2)
    poly(draw, [(cx, cy - s * 0.7), (cx - s * 0.8, cy - s * 0.35), (cx - s * 0.8, cy + s * 0.35), (cx, cy + s * 0.0)],
         hi, DARK_LINE, 2)
    poly(draw, [(cx - s * 0.8, cy - s * 0.35), (cx - s * 0.8, cy + s * 0.35), (cx, cy + s * 0.7), (cx, cy + s * 0.0)],
         color, DARK_LINE, 1)
    poly(draw, [(cx + s * 0.8, cy - s * 0.35), (cx + s * 0.8, cy + s * 0.35), (cx, cy + s * 0.7), (cx, cy + s * 0.0)],
         hi, DARK_LINE, 1)
    if roof:  # spire / chimney
        poly(draw, [(cx, cy - s * 1.15), (cx + s * 0.22, cy - s * 0.75), (cx, cy - s * 0.7), (cx - s * 0.22, cy - s * 0.75)],
             hi, DARK_LINE, 2)
    if accent:
        poly(draw, [(cx - s * 0.5, cy - s * 0.1), (cx + s * 0.5, cy - s * 0.35), (cx + s * 0.5, cy - s * 0.1), (cx - s * 0.5, cy + s * 0.15)],
             accent, DARK_LINE, 1)


def save(img, name):
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG")
    print("wrote", name)


# ---- items (64x64) ---------------------------------------------------------

def icon(name, draw_fn):
    img = new_canvas(64)
    draw_fn(ImageDraw.Draw(img), 32, 32, 22)
    save(img, f"icons/{name}.png")


def item_ore_stormite(d, cx, cy, s):
    crystal_cluster(d, cx, cy - 2, s, PURPLE, (170, 130, 255, 255), seed=11)
    bolt(d, cx + s * 0.5, cy - s * 1.1, cx - s * 0.2, cy - s * 0.1, width=2, color=STORM_YELLOW, seed=5)


def item_ore_astrite(d, cx, cy, s):
    shard(d, cx - 8, cy + 4, 16, SILVER, SILVER_LIGHT)
    shard(d, cx + 10, cy + 2, 13, (120, 140, 165, 255), SILVER_LIGHT)
    shard(d, cx + 1, cy - 8, 11, SILVER_LIGHT, (255, 255, 255, 255))


def item_plate(d, cx, cy, s):
    plate(d, cx, cy, s, (70, 45, 130, 255), (140, 105, 240, 255))
    bolt(d, cx - s * 0.3, cy - s * 0.4, cx + s * 0.35, cy + s * 0.35, width=2, color=STORM_CYAN, seed=9)


def item_crystal(d, cx, cy, s):
    shard(d, cx, cy, s, (110, 140, 180, 255), SILVER_LIGHT)
    poly(d, [(cx - s * 0.2, cy - s * 0.4), (cx, cy + s * 0.1), (cx + s * 0.2, cy - s * 0.4)], STORM_CYAN, None)


def item_lattice(d, cx, cy, s):
    poly(d, [(cx, cy - s), (cx + s * 0.85, cy - s * 0.5), (cx + s * 0.85, cy + s * 0.5), (cx, cy + s),
             (cx - s * 0.85, cy + s * 0.5), (cx - s * 0.85, cy - s * 0.5)], (30, 20, 60, 255), STORM_CYAN, 2)
    for a in range(3):
        ang = a * math.pi / 3
        for sgn in (-1, 1):
            x0 = cx + sgn * math.cos(ang) * s * 0.75
            y0 = cy + sgn * math.sin(ang) * s * 0.75
            d.line([(cx, cy), (x0, y0)], fill=STORM_CYAN, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=STORM_YELLOW, outline=DARK_LINE)


def item_science(d, cx, cy, s):
    flask(d, cx, cy, s * 1.05, (80, 60, 200, 255), FLASK, glow=STORM_YELLOW)


def item_extractor(d, cx, cy, s):
    machine_box(d, cx, cy, s * 1.1, (50, 40, 90, 255), (120, 100, 200, 255), accent=TEAL, roof=True)
    droplet(d, cx, cy + 10, 7, TEAL, STORM_CYAN)


def item_siphon(d, cx, cy, s):
    machine_box(d, cx, cy, s * 1.05, (45, 35, 85, 255), (110, 90, 200, 255), accent=STORM_YELLOW, roof=True)
    bolt(d, cx, cy - s * 1.5, cx, cy - s * 0.3, width=3, color=STORM_YELLOW, seed=4)


def item_foundry(d, cx, cy, s):
    machine_box(d, cx, cy, s * 1.1, (60, 40, 110, 255), (140, 100, 230, 255), accent=(255, 140, 60, 255))
    poly(d, [(cx - s * 0.35, cy - s * 0.1), (cx + s * 0.35, cy - s * 0.35), (cx + s * 0.35, cy - s * 0.1), (cx - s * 0.35, cy + s * 0.15)],
         (255, 140, 60, 255), DARK_LINE, 1)


def item_fabricator(d, cx, cy, s):
    machine_box(d, cx, cy, s * 1.1, (55, 45, 100, 255), (130, 110, 220, 255), accent=STORM_CYAN)
    d.ellipse([cx - 5, cy - 9, cx + 5, cy + 1], fill=STORM_YELLOW, outline=DARK_LINE)


def item_generator(d, cx, cy, s):
    machine_box(d, cx, cy, s * 1.1, (70, 50, 120, 255), (160, 120, 255, 255), accent=STORM_CYAN, roof=True)
    bolt(d, cx - 8, cy + s * 0.35, cx + 8, cy + s * 0.7, width=2, color=STORM_YELLOW, seed=12)


# ---- fluids (64x64) --------------------------------------------------------

def fluid(name, color, hi, seed=2, count=2):
    img = new_canvas(64)
    d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    for i in range(count):
        droplet(d, 20 + i * 24, 26 + (i % 2) * 14, 12, color, hi)
    save(img, f"icons/{name}.png")


# ---- technologies (128x128) --------------------------------------------------

def tech(name, draw_fn):
    img = new_canvas(128)
    d = ImageDraw.Draw(img)
    draw_fn(d, 64, 64, 40)
    save(img, f"technology/{name}.png")


# ---- achievements (128x128) --------------------------------------------------

def ach(name, draw_fn):
    img = new_canvas(128)
    d = ImageDraw.Draw(img)
    draw_fn(d, 64, 64, 44)
    save(img, f"achievement/{name}.png")


# ---- planet ---------------------------------------------------------------

def planet_icon():
    img = new_canvas(128)
    d = ImageDraw.Draw(img)
    d.ellipse([14, 24, 114, 104], fill=(58, 42, 96, 255), outline=DARK_LINE, width=3)
    d.ellipse([34, 34, 94, 94], fill=(74, 56, 120, 255))
    for x in range(22, 106, 10):
        d.line([(x, 60 + (x % 20)), (x + 4, 40 + (x % 16))], fill=(40, 28, 76, 255), width=3)
    bolt(d, 40, 30, 78, 96, width=5, color=STORM_YELLOW, seed=2)
    bolt(d, 84, 20, 96, 60, width=3, color=STORM_CYAN, seed=8)
    save(img, "icons/cataclysm.png")
    save(img.resize((512, 512), Image.LANCZOS), "icons/starmap-cataclysm.png")


def thumbnail():
    img = new_canvas(144)
    d = ImageDraw.Draw(img)
    d.ellipse([8, 26, 136, 118], fill=(46, 34, 80, 255), outline=DARK_LINE, width=4)
    d.ellipse([34, 40, 110, 104], fill=(66, 50, 110, 255))
    bolt(d, 42, 34, 92, 100, width=6, color=STORM_YELLOW, seed=1)
    bolt(d, 100, 28, 116, 70, width=4, color=STORM_CYAN, seed=6)
    d.text((8, 128), "CATACLYSM", fill=(216, 255, 58, 255))
    save(img, "thumbnail.png")


# ---- build everything ------------------------------------------------------

def main():
    os.makedirs(os.path.join(OUT, "icons"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "technology"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "achievement"), exist_ok=True)

    icon("stormite-ore", item_ore_stormite)
    icon("astrite-ore", item_ore_astrite)
    icon("stormite-plate", item_plate)
    icon("astrite-crystal", item_crystal)
    icon("voltaic-lattice", item_lattice)
    icon("cataclysmic-science-pack", item_science)
    icon("condensate-extractor", item_extractor)
    icon("storm-siphon", item_siphon)
    icon("storm-foundry", item_foundry)
    icon("storm-fabricator", item_fabricator)
    icon("storm-generator", item_generator)

    fluid("storm-condensate", TEAL_DARK, TEAL, seed=21)
    fluid("charged-storm-condensate", (120, 210, 255, 255), STORM_CYAN, seed=22, count=3)

    # technologies
    def t_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=STORM_CYAN, width=3)
        item_extractor(d, x, y, s * 0.75)
    tech("condensate-extraction", t_tech)
    def s_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=STORM_YELLOW, width=3)
        item_siphon(d, x, y, s * 0.75)
    tech("storm-siphon", s_tech)
    def f_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=(255, 140, 60, 255), width=3)
        item_foundry(d, x, y, s * 0.75)
    tech("stormite-processing", f_tech)
    def a_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=SILVER, width=3)
        item_crystal(d, x, y, s * 0.85)
    tech("astrite-refining", a_tech)
    def l_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=FLASK, width=3)
        item_lattice(d, x, y, s * 0.8)
    tech("voltaic-lattice", l_tech)
    def sc_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=STORM_YELLOW, width=3)
        item_science(d, x, y, s * 0.85)
    tech("cataclysmic-science-pack", sc_tech)
    def g_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=STORM_CYAN, width=3)
        item_generator(d, x, y, s * 0.75)
    tech("storm-generator", g_tech)
    def p_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=(255, 220, 120, 255), width=3)
        bolt(d, x - 10, y - 30, x + 12, y + 30, width=5, color=STORM_YELLOW, seed=3)
    tech("lightning-protection", p_tech)
    def q_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=(120, 200, 255, 255), width=3)
        bolt(d, x - 14, y - 28, x + 14, y + 28, width=4, color=STORM_CYAN, seed=9)
        bolt(d, x + 14, y - 28, x - 14, y + 28, width=4, color=STORM_CYAN, seed=10)
    tech("seismic-stabilization", q_tech)
    def sh_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=SILVER_LIGHT, width=3)
        poly(d, [(x, y - s), (x + s, y), (x, y + s), (x - s, y)], (60, 50, 110, 255), STORM_CYAN, 3)
    tech("storm-platform-shield", sh_tech)
    def pr_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=STORM_YELLOW, width=3)
        item_plate(d, x, y, s * 0.8)
    tech("cataclysm-productivity", pr_tech)
    def lo_tech(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=TEAL, width=3)
        d.line([(x - s * 0.6, y), (x + s * 0.6, y)], fill=STORM_CYAN, width=4)
        d.line([(x, y - s * 0.6), (x, y + s * 0.6)], fill=STORM_CYAN, width=4)
    tech("storm-logistics", lo_tech)

    # achievements
    def a_visit(d, x, y, s):
        d.ellipse([x - s * 0.7, y - s * 0.7, x + s * 0.7, y + s * 0.7], fill=(58, 42, 96, 255), outline=DARK_LINE, width=3)
        bolt(d, x - 8, y - 28, x + 10, y + 28, width=4, color=STORM_YELLOW, seed=2)
    ach("visit-cataclysm", a_visit)
    def a_research(d, x, y, s):
        flask(d, x, y, s * 0.85, (80, 60, 200, 255), FLASK, glow=STORM_YELLOW)
    ach("research-with-cataclysmic", a_research)
    def a_plate(d, x, y, s):
        item_plate(d, x, y, s * 0.85)
    ach("first-stormite-plate", a_plate)
    def a_charge(d, x, y, s):
        droplet(d, x - 14, y, 16, (120, 210, 255, 255), STORM_CYAN)
        droplet(d, x + 14, y, 16, (120, 210, 255, 255), STORM_CYAN)
    ach("charged-condensate-10k", a_charge)
    def a_siphon(d, x, y, s):
        item_siphon(d, x, y, s * 0.8)
    ach("storm-siphon-network", a_siphon)
    def a_deplete(d, x, y, s):
        item_ore_stormite(d, x, y, s * 0.8)
    ach("deplete-stormite-patch", a_deplete)
    def a_science(d, x, y, s):
        flask(d, x, y, s * 0.9, (80, 60, 200, 255), FLASK)
        d.line([(x - 20, y - 26), (x - 20, y - 34)], fill=STORM_YELLOW, width=4)
        d.line([(x - 12, y - 26), (x - 12, y - 34)], fill=STORM_YELLOW, width=4)
    ach("cataclysmic-science-1000", a_science)
    def a_storm(d, x, y, s):
        bolt(d, x - 8, y - 34, x + 12, y + 34, width=5, color=STORM_YELLOW, seed=5)
        poly(d, [(x - 26, y + 26), (x - 18, y + 18), (x - 10, y + 26)], (200, 200, 200, 255), DARK_LINE, 2)
        poly(d, [(x + 10, y + 26), (x + 18, y + 18), (x + 26, y + 26)], (200, 200, 200, 255), DARK_LINE, 2)
    ach("survive-superstorm", a_storm)
    def a_eye(d, x, y, s):
        d.ellipse([x - 20, y - 20, x + 20, y + 20], outline=STORM_CYAN, width=3)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=STORM_YELLOW)
        bolt(d, x - 24, y - 40, x - 6, y - 22, width=3, color=STORM_YELLOW, seed=6)
    ach("eye-of-the-storm", a_eye)
    def a_ruins(d, x, y, s):
        poly(d, [(x - 14, y + 26), (x - 14, y - 14), (x - 2, y - 26), (x + 10, y - 14), (x + 10, y + 26)], (70, 60, 110, 255), DARK_LINE, 3)
        bolt(d, x - 2, y - 26, x + 4, y + 26, width=2, color=STORM_CYAN, seed=7)
    ach("what-was-here", a_ruins)
    def a_master(d, x, y, s):
        d.ellipse([x - s, y - s, x + s, y + s], outline=STORM_YELLOW, width=4)
        bolt(d, x - 8, y - 30, x + 10, y + 30, width=4, color=STORM_CYAN, seed=8)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=STORM_YELLOW)
    ach("cataclysm-tech-master", a_master)

    planet_icon()
    thumbnail()
    print("done")


if __name__ == "__main__":
    main()

# ---- ore sprite sheets (8x8 cells of 128px = 1024x1024) --------------------

def ore_sheet(name, draw_cell):
    sheet = new_canvas(1024)
    for var in range(8):
        for frame in range(8):
            x, y = frame * 128, var * 128
            cell = new_canvas(128)
            draw_cell(ImageDraw.Draw(cell), 64, 64, 40, seed=1000 + var * 7 + frame)
            sheet.paste(cell, (x, y), cell)
    save(sheet, f"entity/{name}/{name}.png")


def cell_stormite(d, cx, cy, s, seed):
    rng = random.Random(seed)
    for _ in range(3):
        ox = rng.randint(-26, 26)
        oy = rng.randint(-18, 22)
        shard(d, cx + ox, cy + oy, rng.randint(14, 24), PURPLE, (170, 130, 255, 255))
    bolt(d, cx - 20, cy - 26, cx + 16, cy + 24, width=2, color=STORM_YELLOW, seed=seed % 7 + 1)


def cell_astrite(d, cx, cy, s, seed):
    rng = random.Random(seed + 500)
    for _ in range(3):
        ox = rng.randint(-26, 26)
        oy = rng.randint(-18, 22)
        shard(d, cx + ox, cy + oy, rng.randint(12, 22), SILVER, SILVER_LIGHT)


# ---- decorative entity art (128x128 single frames) -------------------------

def entity_art(name, draw_fn):
    img = new_canvas(128)
    draw_fn(ImageDraw.Draw(img), 64, 64, 52)
    save(img, f"entity/{name}/{name}.png")


def art_tree(d, cx, cy, s):
    poly(d, [(cx - 8, cy + 40), (cx - 5, cy - 30), (cx + 6, cy - 40), (cx + 10, cy + 40)],
         (70, 55, 120, 255), DARK_LINE, 3)
    poly(d, [(cx - 6, cy - 36), (cx + 6, cy - 46), (cx + 14, cy - 18), (cx + 2, cy - 12)], (120, 90, 220, 255), DARK_LINE, 2)
    poly(d, [(cx + 2, cy - 12), (cx - 18, cy - 22), (cx - 6, cy - 36)], (95, 70, 180, 255), DARK_LINE, 2)
    bolt(d, cx - 12, cy - 48, cx + 4, cy - 30, width=2, color=STORM_CYAN, seed=4)


def art_rock(d, cx, cy, s):
    poly(d, [(cx - 34, cy + 26), (cx - 26, cy - 8), (cx - 6, cy - 26), (cx + 20, cy - 18), (cx + 34, cy + 6), (cx + 26, cy + 26)],
         (55, 42, 96, 255), DARK_LINE, 3)
    poly(d, [(cx - 26, cy - 8), (cx - 6, cy - 26), (cx + 6, cy - 4), (cx - 14, cy + 6)], (95, 75, 160, 255), None)
    d.line([(cx - 6, cy - 26), (cx - 2, cy + 4)], fill=DARK_LINE, width=2)
    d.line([(cx - 2, cy + 4), (cx + 12, cy + 14)], fill=DARK_LINE, width=2)


def art_vent(d, cx, cy, s):
    poly(d, [(cx - 20, cy + 34), (cx - 14, cy - 6), (cx + 14, cy - 6), (cx + 20, cy + 34)], (48, 36, 88, 255), DARK_LINE, 3)
    poly(d, [(cx - 26, cy - 6), (cx + 26, cy - 6), (cx + 16, cy - 22), (cx - 16, cy - 22)], (80, 62, 140, 255), DARK_LINE, 2)
    d.ellipse([cx - 14, cy - 22, cx + 14, cy - 2], fill=TEAL_DARK, outline=DARK_LINE, width=2)
    bolt(d, cx - 6, cy - 40, cx + 8, cy - 24, width=2, color=STORM_YELLOW, seed=5)
    poly(d, [(cx - 10, cy + 10), (cx + 10, cy + 10), (cx + 6, cy + 22), (cx - 6, cy + 22)], (30, 22, 60, 255), None)


def art_spire(d, cx, cy, s):
    poly(d, [(cx - 12, cy + 40), (cx - 6, cy - 34), (cx + 8, cy - 44), (cx + 14, cy + 40)],
         (90, 70, 150, 255), DARK_LINE, 3)
    poly(d, [(cx - 6, cy - 34), (cx + 8, cy - 44), (cx + 20, cy - 20), (cx + 4, cy - 12)], (150, 120, 255, 255), DARK_LINE, 2)
    bolt(d, cx - 18, cy - 56, cx + 2, cy - 34, width=3, color=STORM_CYAN, seed=8)
    poly(d, [(cx - 26, cy + 24), (cx - 14, cy + 40), (cx - 2, cy + 30), (cx - 14, cy + 18)], (70, 55, 120, 255), DARK_LINE, 2)


def main2():
    ore_sheet("stormite-ore", cell_stormite)
    ore_sheet("astrite-ore", cell_astrite)
    entity_art("cataclysm-crystal-tree", art_tree)
    entity_art("cataclysm-rock", art_rock)
    entity_art("cataclysm-vent", art_vent)
    entity_art("cataclysm-ancient-spire", art_spire)
    print("done2")


if __name__ == "__main__":
    main()
    main2()
