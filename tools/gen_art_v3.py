#!/usr/bin/env python3
"""v3 — polished isometric raft + cel-shaded character + fabric sail."""
from __future__ import annotations
import math, random, os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = "/workspace/raft-survive/godot/assets/art"
os.makedirs(OUT, exist_ok=True)

def save(im: Image.Image, name: str, scale=2):
    if scale > 1:
        w, h = im.size
        im = im.resize((max(1, w // scale), max(1, h // scale)), Image.LANCZOS)
    path = os.path.join(OUT, name)
    im.save(path, "PNG", optimize=True)
    print(f"  {name} {im.size} {os.path.getsize(path)}b")

def outline(im, color=(40, 28, 18, 255), width=2):
    """Add dark outline around opaque pixels."""
    alpha = im.split()[-1]
    dilated = alpha
    for _ in range(width):
        dilated = dilated.filter(ImageFilter.MaxFilter(3))
    ring = ImageChops.subtract(dilated, alpha)
    outline_img = Image.new("RGBA", im.size, (0, 0, 0, 0))
    outline_img.paste(color, mask=ring)
    return Image.alpha_composite(outline_img, im)

def soft_shadow(base, offset=(8, 10), blur=8, alpha=70):
    mask = base.split()[-1]
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer = Image.new("RGBA", base.size, (15, 10, 5, alpha))
    layer.putalpha(ImageChops.multiply(mask, Image.new("L", base.size, alpha)))
    # simpler:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    solid = Image.new("RGBA", base.size, (18, 12, 8, alpha))
    solid.putalpha(mask)
    layer.paste(solid, offset, solid)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(layer, base)

def grad_ellipse(draw_im, box, c1, c2):
    """Radial-ish fill by concentric ellipses."""
    d = ImageDraw.Draw(draw_im)
    x0, y0, x1, y1 = box
    steps = 12
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(c1[0] * t + c2[0] * (1 - t))
        g = int(c1[1] * t + c2[1] * (1 - t))
        b = int(c1[2] * t + c2[2] * (1 - t))
        a = c1[3] if len(c1) > 3 else 255
        inset = (1 - t) * ((x1 - x0) / 2) * 0.85
        d.ellipse([x0 + inset, y0 + inset * 0.7, x1 - inset, y1 - inset * 0.7], fill=(r, g, b, a))

# ========== ISOMETRIC RAFT ==========
def make_raft():
    S = 2
    W, H = 520, 400
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # foam under
    foam = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(foam)
    cx, cy = W * S // 2, H * S // 2 + 20
    fd.ellipse([cx - 280, cy - 120, cx + 280, cy + 160], fill=(230, 250, 255, 70))
    fd.ellipse([cx - 220, cy - 80, cx + 220, cy + 110], fill=(255, 255, 255, 50))
    foam = foam.filter(ImageFilter.GaussianBlur(22))
    im = Image.alpha_composite(im, foam)
    d = ImageDraw.Draw(im)

    # Draw raft as thick parallel logs in slight isometric (diamond-ish)
    # Top face: parallelogram of planks
    # Screen coords: origin center-ish
    ox, oy = 80, 120  # top-left of deck in 2x space

    def iso(x, y, z=0):
        # simple 2:1 iso
        sx = ox + (x - y) * 1.15
        sy = oy + (x + y) * 0.58 - z
        return sx, sy

    # Deck size in grid units
    cols, rows = 6, 6
    plank_colors = [
        ((190, 140, 78), (150, 100, 50), (105, 68, 32)),
        ((175, 125, 68), (140, 92, 45), (95, 60, 28)),
        ((200, 155, 95), (160, 112, 58), (115, 75, 38)),
    ]

    # Draw side faces first (depth)
    for c in range(cols):
        # front edge thickness
        x0, y0 = iso(c, rows, 0)
        x1, y1 = iso(c + 1, rows, 0)
        x2, y2 = iso(c + 1, rows, -22)
        x3, y3 = iso(c, rows, -22)
        col = (110, 72, 35, 255)
        d.polygon([(x0, y0), (x1, y1), (x2, y2), (x3, y3)], fill=col, outline=(70, 42, 18, 255))
    for r in range(rows):
        x0, y0 = iso(cols, r, 0)
        x1, y1 = iso(cols, r + 1, 0)
        x2, y2 = iso(cols, r + 1, -22)
        x3, y3 = iso(cols, r, -22)
        d.polygon([(x0, y0), (x1, y1), (x2, y2), (x3, y3)], fill=(95, 60, 28, 255), outline=(60, 35, 15, 255))

    # Top planks as horizontal wood strips (rows)
    for r in range(rows):
        light, mid, dark = plank_colors[r % len(plank_colors)]
        # each row is one long plank across
        pts = [iso(0, r), iso(cols, r), iso(cols, r + 1), iso(0, r + 1)]
        d.polygon(pts, fill=mid + (255,), outline=(70, 45, 22, 255))
        # highlight strip along top edge of plank
        hx0, hy0 = iso(0.15, r + 0.08)
        hx1, hy1 = iso(cols - 0.15, r + 0.08)
        d.line([(hx0, hy0), (hx1, hy1)], fill=light + (220,), width=3)
        # grain
        rng = random.Random(r + 3)
        for g in range(5):
            gx = 0.4 + g * 1.0 + rng.random() * 0.3
            a = iso(gx, r + 0.2)
            b = iso(gx + 0.15, r + 0.85)
            d.line([a, b], fill=dark + (120,), width=1)
        # seam shadow between planks
        sx0, sy0 = iso(0, r + 1)
        sx1, sy1 = iso(cols, r + 1)
        d.line([(sx0, sy0), (sx1, sy1)], fill=(60, 38, 18, 200), width=2)

    # Rope lashings at intersections
    rope = (100, 72, 42, 255)
    rope_h = (150, 115, 75, 255)
    for r in range(rows + 1):
        for c in (0, cols // 2, cols):
            if c == 0 or c == cols or r % 2 == 0:
                px, py = iso(c, r, 2)
                d.ellipse([px - 7, py - 5, px + 7, py + 5], fill=rope)
                d.arc([px - 7, py - 5, px + 7, py + 5], 200, 340, fill=rope_h, width=2)
    for c in range(cols + 1):
        for r in (0, rows // 2, rows):
            px, py = iso(c, r, 2)
            d.ellipse([px - 5, py - 7, px + 5, py + 7], fill=rope)

    # Metal corner plates
    metal = (165, 170, 180, 255)
    metal_d = (95, 100, 110, 255)
    metal_h = (220, 225, 235, 255)
    for (cx, cy) in [(0.3, 0.3), (cols - 0.3, 0.3), (0.3, rows - 0.3), (cols - 0.3, rows - 0.3)]:
        pts = [iso(cx - 0.35, cy - 0.25, 3), iso(cx + 0.35, cy - 0.25, 3),
               iso(cx + 0.35, cy + 0.25, 3), iso(cx - 0.35, cy + 0.25, 3)]
        d.polygon(pts, fill=metal, outline=metal_d)
        mx, my = iso(cx, cy, 4)
        d.ellipse([mx - 3, my - 3, mx + 3, my + 3], fill=metal_d)
        d.line([pts[0], pts[1]], fill=metal_h, width=2)

    # Outer rope border wrap
    border = []
    for c in range(cols + 1):
        border.append(iso(c, 0, 1))
    for r in range(1, rows + 1):
        border.append(iso(cols, r, 1))
    for c in range(cols - 1, -1, -1):
        border.append(iso(c, rows, 1))
    for r in range(rows - 1, 0, -1):
        border.append(iso(0, r, 1))
    if len(border) > 2:
        d.line(border + [border[0]], fill=(85, 55, 30, 255), width=5)

    im = soft_shadow(im, (12, 16), 12, 75)
    im = outline(im, (45, 30, 18, 230), 2)
    save(im, "raft.png", S)

# ========== SAIL ==========
def make_sail():
    S = 2
    W, H = 220, 300
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pole = (145, 100, 55, 255)
    pole_d = (85, 55, 25, 255)
    pole_h = (200, 160, 105, 255)
    # left / right masts with taper
    for x in (50, 380):
        d.polygon([(x - 8, 30), (x + 8, 30), (x + 6, 560), (x - 6, 560)], fill=pole)
        d.line([(x - 4, 35), (x - 3, 550)], fill=pole_h, width=3)
        d.line([(x + 4, 35), (x + 3, 550)], fill=pole_d, width=2)
    # crossbeam
    d.rounded_rectangle([40, 55, 400, 78], radius=4, fill=pole, outline=pole_d, width=2)
    d.line([(45, 60), (395, 60)], fill=pole_h, width=2)

    # cloth with soft folds — draw as filled polygon then overlay translucent bands
    cloth = Image.new("RGBA", im.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloth)
    # billowing sail shape
    pts = [(62, 85), (388, 95), (375, 500), (75, 480)]
    # slight curve via mid control points approximated with trapezoid + arcs
    cd.polygon(pts, fill=(252, 252, 255, 250))
    # soft fold shadows (vertical wavy)
    for i in range(7):
        x = 90 + i * 42
        shade = 35 + (i % 3) * 20
        band = [
            (x, 100), (x + 22, 110), (x + 18, 470), (x - 6, 460)
        ]
        cd.polygon(band, fill=(180, 195, 215, shade))
    # highlight folds
    for i in range(4):
        x = 110 + i * 60
        cd.polygon([(x, 105), (x + 10, 115), (x + 8, 455), (x - 2, 450)], fill=(255, 255, 255, 50))
    # blue patch with stitch
    cd.rounded_rectangle([220, 180, 310, 270], radius=8, fill=(65, 145, 215, 230), outline=(35, 95, 170, 255), width=3)
    for yy in range(190, 260, 10):
        cd.line([(225, yy), (305, yy)], fill=(90, 170, 235, 80), width=1)
    # top/bottom hem
    cd.line([(65, 90), (385, 100)], fill=(200, 205, 215, 200), width=3)
    cd.line([(78, 475), (372, 495)], fill=(190, 195, 205, 200), width=3)
    cloth = cloth.filter(ImageFilter.GaussianBlur(0.8))
    im = Image.alpha_composite(im, cloth)
    d = ImageDraw.Draw(im)
    # rope ties
    for (x, y) in [(50, 85), (380, 95), (55, 475), (375, 500)]:
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(110, 78, 45, 255))
        d.arc([x - 8, y - 8, x + 8, y + 8], 200, 340, fill=(160, 120, 80, 255), width=2)
    im = soft_shadow(im, (10, 12), 10, 55)
    im = outline(im, (50, 35, 20, 200), 2)
    save(im, "sail.png", S)

# ========== PLAYER cel-shaded ==========
def make_player():
    S = 3  # draw 3x for smoother
    W, H = 160, 220
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W * S // 2

    skin = (245, 205, 175, 255)
    skin_s = (215, 165, 135, 255)
    skin_ss = (185, 130, 105, 255)
    skin_h = (255, 230, 210, 255)
    hair = (88, 55, 35, 255)
    hair_m = (120, 78, 48, 255)
    hair_h = (155, 110, 70, 255)
    shirt = (252, 253, 255, 255)
    shirt_s = (200, 210, 225, 255)
    shirt_ss = (170, 180, 198, 255)
    shorts = (175, 135, 82, 255)
    shorts_s = (140, 100, 55, 255)
    shorts_ss = (105, 72, 38, 255)
    boot = (85, 55, 35, 255)
    boot_h = (120, 85, 55, 255)

    # legs
    d.rounded_rectangle([cx - 48, 380, cx - 8, 545], radius=12, fill=skin)
    d.rounded_rectangle([cx + 6, 380, cx + 46, 545], radius=12, fill=skin)
    d.rectangle([cx - 48, 480, cx - 8, 545], fill=skin_s)  # shin shade
    d.rectangle([cx + 6, 480, cx + 46, 545], fill=skin_s)
    # boots with sole
    for bx in (cx - 52, cx + 2):
        d.rounded_rectangle([bx, 530, bx + 50, 585], radius=10, fill=boot)
        d.ellipse([bx - 4, 565, bx + 54, 600], fill=boot)
        d.arc([bx + 4, 535, bx + 40, 565], 200, 340, fill=boot_h, width=3)

    # shorts with folds
    d.rounded_rectangle([cx - 62, 330, cx + 62, 420], radius=14, fill=shorts)
    d.polygon([(cx - 62, 360), (cx - 40, 420), (cx - 62, 420)], fill=shorts_s)  # left shade
    d.polygon([(cx + 62, 360), (cx + 40, 420), (cx + 62, 420)], fill=shorts_s)
    d.line([(cx, 340), (cx, 412)], fill=shorts_ss, width=3)
    d.rounded_rectangle([cx + 22, 350, cx + 52, 390], radius=4, outline=shorts_ss, width=3)
    d.arc([cx - 50, 335, cx - 10, 380], 20, 160, fill=shorts_s, width=3)

    # torso tee
    d.rounded_rectangle([cx - 68, 175, cx + 68, 350], radius=18, fill=shirt)
    # side shade
    d.polygon([(cx + 50, 190), (cx + 68, 190), (cx + 68, 340), (cx + 45, 340)], fill=shirt_s)
    d.polygon([(cx - 68, 200), (cx - 50, 200), (cx - 45, 340), (cx - 68, 340)], fill=shirt_ss)
    # fabric folds
    d.arc([cx - 40, 220, cx + 20, 320], 30, 150, fill=shirt_s, width=4)
    d.arc([cx - 10, 250, cx + 50, 340], 200, 320, fill=shirt_s, width=3)
    d.line([(cx - 30, 280), (cx + 35, 320)], fill=shirt_ss, width=2)

    # left sleeve + arm (down/back)
    d.polygon([(cx - 68, 195), (cx - 68, 260), (cx - 125, 290), (cx - 135, 245)], fill=shirt)
    d.polygon([(cx - 120, 265), (cx - 155, 330), (cx - 125, 350), (cx - 100, 285)], fill=skin)
    d.ellipse([cx - 165, 325, cx - 125, 365], fill=skin)
    d.ellipse([cx - 165, 325, cx - 125, 365], outline=skin_s)
    # shade on arm
    d.polygon([(cx - 140, 280), (cx - 155, 330), (cx - 135, 340)], fill=skin_s)

    # right sleeve + throwing arm up-forward
    d.polygon([(cx + 60, 185), (cx + 68, 250), (cx + 160, 160), (cx + 150, 125)], fill=shirt)
    d.polygon([(cx + 145, 130), (cx + 200, 95), (cx + 215, 130), (cx + 160, 160)], fill=skin)
    d.ellipse([cx + 195, 100, cx + 235, 140], fill=skin)  # hand
    d.arc([cx + 200, 105, cx + 225, 130], 200, 340, fill=skin_h, width=3)
    # fingers hint
    for fx in range(5):
        d.ellipse([cx + 210 + fx * 3, 108, cx + 218 + fx * 3, 122], fill=skin_s)

    # neck
    d.rounded_rectangle([cx - 22, 155, cx + 22, 195], radius=6, fill=skin)
    d.rectangle([cx - 22, 175, cx + 22, 195], fill=skin_s)

    # head back/3q
    d.ellipse([cx - 55, 55, cx + 55, 170], fill=skin)
    # ear
    d.ellipse([cx + 42, 100, cx + 68, 140], fill=skin)
    d.ellipse([cx + 48, 108, cx + 62, 132], fill=skin_s)
    # jaw shade
    d.arc([cx - 45, 100, cx + 45, 165], 15, 165, fill=skin_s, width=5)
    d.arc([cx - 30, 120, cx + 30, 160], 30, 150, fill=skin_ss, width=3)

    # hair volume — layered ellipses + tufts
    d.ellipse([cx - 62, 40, cx + 62, 135], fill=hair)
    for ox, oy, rx, ry in [
        (-40, 50, 28, 35), (-15, 30, 32, 38), (15, 35, 34, 40),
        (40, 55, 26, 32), (-50, 80, 20, 28), (50, 85, 18, 26),
        (0, 25, 30, 28), (-25, 70, 22, 30), (25, 75, 22, 28),
    ]:
        d.ellipse([cx + ox - rx, oy, cx + ox + rx, oy + ry * 2], fill=hair)
    # midtone hair strands
    for ox, oy, rx, ry in [(-20, 55, 18, 22), (10, 50, 20, 24), (35, 70, 14, 18)]:
        d.ellipse([cx + ox - rx, oy, cx + ox + rx, oy + ry * 2], fill=hair_m)
    # highlights
    d.arc([cx - 35, 48, cx + 5, 95], 200, 330, fill=hair_h, width=5)
    d.arc([cx + 8, 55, cx + 40, 100], 210, 310, fill=hair_h, width=4)
    d.arc([cx - 50, 70, cx - 20, 110], 220, 300, fill=hair_h, width=3)

    # rope from hand
    rope = (215, 205, 190, 255)
    d.line([(cx + 225, 115), (cx + 280, 70), (cx + 340, 30)], fill=rope, width=5)
    d.line([(cx + 225, 118), (cx + 280, 73), (cx + 340, 33)], fill=(170, 160, 145, 200), width=2)

    im = soft_shadow(im, (8, 10), 8, 60)
    im = outline(im, (35, 25, 18, 255), 3)
    # mild smooth
    im = im.filter(ImageFilter.SMOOTH)
    save(im, "player.png", S)

# ========== PROPS ==========
def make_grill():
    S = 2
    im = Image.new("RGBA", (160 * S, 150 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # stones
    for (x, y, w, h) in [(50, 180, 70, 50), (110, 185, 80, 55), (180, 180, 70, 50), (70, 210, 160, 40)]:
        d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=(115, 108, 100, 255), outline=(70, 65, 60, 255), width=2)
        d.arc([x + 5, y + 3, x + w - 5, y + 20], 200, 340, fill=(160, 155, 145, 255), width=2)
    # brazier
    d.ellipse([70, 110, 250, 200], fill=(55, 58, 68, 255), outline=(30, 32, 40, 255), width=3)
    d.arc([75, 115, 245, 180], 200, 340, fill=(130, 140, 155, 255), width=3)
    # fire
    for box, col in [([110, 120, 210, 185], (255, 100, 30, 230)),
                     ([125, 125, 195, 175], (255, 180, 50, 220)),
                     ([140, 132, 180, 165], (255, 250, 180, 200))]:
        d.ellipse(box, fill=col)
    for i in range(6):
        d.line([(85, 125 + i * 10), (235, 125 + i * 10)], fill=(40, 42, 50, 230), width=2)
    # fish
    d.ellipse([115, 115, 210, 155], fill=(230, 175, 115, 255), outline=(160, 110, 60, 255), width=2)
    d.ellipse([195, 125, 220, 148], fill=(230, 175, 115, 255))
    d.ellipse([205, 132, 213, 140], fill=(30, 20, 15, 255))
    d.polygon([(115, 135), (95, 120), (95, 150)], fill=(230, 175, 115, 255))
    # smoke
    smoke = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    for x, y, r, a in [(140, 70, 28, 75), (170, 45, 35, 55), (195, 25, 30, 40), (120, 50, 22, 50)]:
        sd.ellipse([x - r, y - r, x + r, y + r], fill=(245, 248, 252, a))
    smoke = smoke.filter(ImageFilter.GaussianBlur(7))
    im = Image.alpha_composite(im, smoke)
    im = soft_shadow(im, (6, 8), 6, 55)
    im = outline(im, (40, 30, 20, 220), 2)
    save(im, "grill.png", S)

def make_chest():
    S = 2
    im = Image.new("RGBA", (150 * S, 130 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wood, wood_d, wood_h = (155, 105, 58, 255), (95, 60, 30, 255), (200, 155, 100, 255)
    # body with side face for depth
    d.polygon([(40, 100), (220, 100), (250, 130), (70, 130), (70, 220), (40, 200)], fill=wood_d)
    d.rounded_rectangle([40, 100, 220, 220], radius=6, fill=wood, outline=wood_d, width=3)
    for y in (130, 160, 190):
        d.line([(50, y), (210, y)], fill=wood_d, width=2)
    d.line([(50, 110), (210, 110)], fill=wood_h, width=3)
    # lid with curve
    d.ellipse([35, 50, 225, 120], fill=wood_h, outline=wood_d, width=3)
    d.rectangle([38, 85, 222, 110], fill=wood_h)
    d.arc([40, 55, 220, 110], 200, 340, fill=(230, 195, 140, 255), width=4)
    metal, metal_d = (160, 165, 175, 255), (95, 100, 110, 255)
    for x in (55, 185):
        d.rectangle([x, 60, x + 22, 215], fill=metal, outline=metal_d, width=2)
        for ry in (80, 130, 180):
            d.ellipse([x + 5, ry, x + 17, ry + 12], fill=metal_d)
    d.rounded_rectangle([115, 125, 150, 165], radius=4, fill=metal, outline=metal_d, width=2)
    d.ellipse([124, 135, 142, 153], outline=metal_d, width=3)
    im = soft_shadow(im, (7, 9), 7, 60)
    im = outline(im, (40, 28, 15, 230), 2)
    save(im, "chest.png", S)

def make_purifier():
    S = 2
    im = Image.new("RGBA", (160 * S, 190 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    barrel, barrel_d = (155, 108, 60, 255), (95, 60, 28, 255)
    d.ellipse([75, 240, 245, 330], fill=barrel_d)
    d.rectangle([75, 140, 245, 285], fill=barrel)
    d.ellipse([75, 105, 245, 185], fill=(180, 135, 82, 255), outline=barrel_d, width=3)
    for y in (160, 210, 260):
        d.arc([80, y - 25, 240, y + 45], 0, 180, fill=barrel_d, width=3)
    metal = (145, 150, 160, 255)
    for y in (150, 240):
        d.rectangle([70, y, 250, y + 14], fill=metal)
    # tarp
    tarp = Image.new("RGBA", im.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(tarp)
    td.polygon([(35, 40), (285, 55), (220, 150), (95, 140)], fill=(50, 135, 210, 235))
    td.line([(70, 55), (150, 135)], fill=(100, 180, 240, 160), width=4)
    td.line([(200, 65), (185, 140)], fill=(30, 90, 160, 140), width=3)
    td.line([(40, 45), (280, 58)], fill=(30, 90, 160, 200), width=2)
    im = Image.alpha_composite(im, tarp)
    d = ImageDraw.Draw(im)
    stick = (125, 88, 48, 255)
    d.line([(50, 45), (95, 250)], fill=stick, width=6)
    d.line([(270, 55), (225, 250)], fill=stick, width=6)
    d.ellipse([150, 142, 170, 165], fill=(130, 210, 255, 190))
    im = soft_shadow(im, (6, 8), 6, 55)
    im = outline(im, (40, 28, 15, 220), 2)
    save(im, "purifier.png", S)

def make_bed():
    S = 2
    im = Image.new("RGBA", (160 * S, 90 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    base, dark, light = (75, 150, 90, 255), (45, 105, 60, 255), (120, 190, 130, 255)
    d.rounded_rectangle([20, 25, 300, 150], radius=12, fill=base, outline=dark, width=3)
    for i in range(10):
        y = 35 + i * 11
        d.line([(30, y), (290, y)], fill=dark if i % 2 == 0 else light, width=2)
    for i in range(14):
        x = 35 + i * 18
        d.line([(x, 30), (x, 145)], fill=(55, 125, 75, 90), width=1)
    for x in range(28, 295, 12):
        d.line([(x, 148), (x + 4, 165)], fill=dark, width=2)
    # soft highlight
    d.arc([40, 30, 160, 80], 200, 340, fill=(180, 230, 190, 100), width=4)
    im = soft_shadow(im, (5, 6), 5, 50)
    im = outline(im, (30, 50, 30, 200), 2)
    save(im, "bed.png", S)

def make_hook():
    S = 3
    im = Image.new("RGBA", (56 * S, 56 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    metal, metal_d, metal_h = (185, 195, 210, 255), (85, 95, 115, 255), (240, 245, 255, 255)
    d.line([(84, 25), (84, 105)], fill=metal, width=14)
    d.line([(78, 28), (78, 102)], fill=metal_h, width=4)
    d.arc([45, 90, 125, 160], 0, 280, fill=metal, width=14)
    d.arc([52, 97, 118, 153], 10, 260, fill=metal_h, width=4)
    d.polygon([(55, 125), (40, 150), (68, 145)], fill=metal_d)
    d.ellipse([70, 12, 98, 40], outline=metal, width=7)
    d.ellipse([76, 18, 92, 34], outline=metal_h, width=2)
    im = soft_shadow(im, (3, 3), 3, 45)
    im = outline(im, (40, 45, 55, 230), 2)
    save(im, "hook.png", S)

def make_debris():
    S = 2
    # wood cluster
    im = Image.new("RGBA", (180 * S, 80 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (y, h, dx) in enumerate([(25, 40, 0), (55, 36, 15), (90, 34, 8)]):
        light = (195, 145, 85, 255)
        mid = (155, 105, 55, 255)
        dark = (100, 65, 30, 255)
        d.rounded_rectangle([20 + dx, y, 330 - dx, y + h], radius=6, fill=mid, outline=dark, width=2)
        d.line([(25 + dx, y + 4), (325 - dx, y + 4)], fill=light, width=3)
        d.line([(25 + dx, y + h - 4), (325 - dx, y + h - 4)], fill=dark, width=2)
        for g in range(4):
            d.line([(60 + g * 60, y + 6), (65 + g * 60, y + h - 6)], fill=dark[:3] + (100,), width=1)
    d.arc([150, 40, 210, 110], 0, 360, fill=(100, 70, 40, 255), width=5)
    foam = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(foam)
    fd.ellipse([15, 110, 340, 155], fill=(230, 250, 255, 70))
    foam = foam.filter(ImageFilter.GaussianBlur(5))
    im = Image.alpha_composite(foam, im)
    im = soft_shadow(im, (4, 5), 5, 50)
    im = outline(im, (50, 35, 18, 220), 2)
    save(im, "debris_wood.png", S)

    # barrel
    im = Image.new("RGBA", (110 * S, 130 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wood, wood_d = (158, 110, 60, 255), (95, 60, 28, 255)
    d.ellipse([45, 180, 175, 245], fill=wood_d)
    d.rectangle([45, 55, 175, 210], fill=wood)
    d.ellipse([45, 30, 175, 100], fill=(185, 140, 85, 255), outline=wood_d, width=3)
    for y in (80, 150):
        d.rectangle([40, y, 180, y + 14], fill=(145, 150, 160, 255))
    d.arc([55, 50, 110, 180], 200, 320, fill=(255, 255, 255, 100), width=5)
    im = soft_shadow(im, (5, 6), 5, 55)
    im = outline(im, (45, 30, 15, 230), 2)
    save(im, "debris_barrel.png", S)

    # crate
    im = Image.new("RGBA", (120 * S, 110 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wood, wood_d = (165, 118, 68, 255), (100, 65, 32, 255)
    d.rounded_rectangle([30, 40, 210, 200], radius=6, fill=wood, outline=wood_d, width=3)
    for y in (75, 120, 165):
        d.line([(40, y), (200, y)], fill=wood_d, width=2)
    d.line([(45, 50), (195, 190)], fill=wood_d, width=4)
    d.line([(195, 50), (45, 190)], fill=wood_d, width=4)
    metal = (155, 160, 170, 255)
    for (x, y) in [(30, 40), (190, 40), (30, 180), (190, 180)]:
        d.rectangle([x, y, x + 22, y + 22], outline=metal, width=4)
    im = soft_shadow(im, (5, 6), 5, 55)
    im = outline(im, (45, 30, 15, 230), 2)
    save(im, "debris_crate.png", S)

    # fish
    im = Image.new("RGBA", (110 * S, 65 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body, body_d, belly = (85, 175, 205, 255), (35, 100, 140, 255), (210, 235, 245, 255)
    d.ellipse([35, 30, 180, 100], fill=body)
    d.ellipse([45, 55, 170, 100], fill=belly)
    d.polygon([(35, 60), (5, 30), (8, 95)], fill=body_d)
    d.polygon([(100, 30), (125, 5), (135, 40)], fill=body_d)
    d.ellipse([155, 52, 172, 70], fill=(20, 30, 40, 255))
    d.ellipse([158, 55, 165, 62], fill=(255, 255, 255, 220))
    for i in range(6):
        d.arc([55 + i * 18, 40, 90 + i * 18, 90], 200, 340, fill=(255, 255, 255, 70), width=2)
    im = soft_shadow(im, (3, 4), 3, 40)
    im = outline(im, (25, 50, 70, 230), 2)
    save(im, "debris_fish.png", S)

    # bottle
    im = Image.new("RGBA", (48 * S, 80 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    glass = (110, 200, 165, 190)
    d.rounded_rectangle([25, 55, 70, 145], radius=10, fill=glass, outline=(50, 140, 110, 230), width=2)
    d.rectangle([35, 22, 60, 60], fill=glass, outline=(50, 140, 110, 230), width=2)
    d.rectangle([32, 15, 63, 28], fill=(185, 105, 60, 255))
    d.line([(30, 65), (30, 135)], fill=(230, 255, 245, 140), width=3)
    im = outline(im, (30, 70, 55, 200), 1)
    save(im, "debris_bottle.png", S)

def make_misc():
    S = 2
    # shark
    im = Image.new("RGBA", (180 * S, 80 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body, dark = (95, 115, 135, 235), (50, 65, 85, 235)
    d.ellipse([50, 45, 290, 125], fill=body)
    d.polygon([(290, 80), (350, 60), (350, 105)], fill=body)
    d.polygon([(50, 80), (5, 40), (20, 115)], fill=dark)
    d.polygon([(150, 45), (175, 5), (200, 50)], fill=dark)
    d.ellipse([70, 85, 270, 125], fill=(185, 200, 215, 190))
    d.ellipse([310, 70, 328, 88], fill=(15, 20, 30, 255))
    im = soft_shadow(im, (4, 4), 4, 40)
    im = outline(im, (30, 40, 55, 230), 2)
    save(im, "shark.png", S)

    # coral
    im = Image.new("RGBA", (180 * S, 140 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    colors = [(210, 95, 130, 170), (70, 165, 145, 160), (230, 145, 85, 150), (165, 85, 185, 140)]
    for i, col in enumerate(colors):
        x = 50 + i * 75
        d.ellipse([x, 140, x + 55, 230], fill=col)
        for j in range(4):
            d.ellipse([x + j * 10 - 8, 70 + j * 18, x + 35 + j * 6, 150 + j * 12], fill=col)
    d.ellipse([20, 210, 340, 275], fill=(55, 65, 75, 150))
    im = im.filter(ImageFilter.GaussianBlur(1.5))
    save(im, "coral.png", S)

    # sky
    W, H = 900, 480
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        r = int(120 + t * 90)
        g = int(185 + t * 45)
        b = int(250 - t * 35)
        a = int(255 - t * 50)
        d.line([(0, y), (W, y)], fill=(r, g, b, a))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([600, -60, 900, 220], fill=(255, 250, 200, 100))
    gd.ellipse([680, 0, 820, 140], fill=(255, 255, 230, 130))
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    im = Image.alpha_composite(im, glow)
    save(im, "sky.png", 1)

    # ocean underlay
    W, H = 900, 1400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(8 + t * 15), int(55 + t * 50), int(85 + t * 30), 255))
    rng = random.Random(11)
    for _ in range(30):
        x, y = rng.randint(0, W), rng.randint(int(H * 0.3), H)
        col = (rng.randint(15, 55), rng.randint(70, 130), rng.randint(60, 100), rng.randint(35, 85))
        rr = rng.randint(18, 65)
        d.ellipse([x - rr, y - rr // 2, x + rr, y + rr], fill=col)
    for _ in range(15):
        x, y = rng.randint(0, W), rng.randint(int(H * 0.45), H)
        ww, hh = rng.randint(40, 130), rng.randint(12, 40)
        d.ellipse([x, y, x + ww, y + hh], fill=(35, 95, 85, 45))
    im = im.filter(ImageFilter.GaussianBlur(2.5))
    save(im, "ocean.png", 1)

    # cloud
    im = Image.new("RGBA", (240 * S, 110 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x, y, r, a in [(90, 90, 60, 210), (150, 75, 70, 220), (220, 90, 55, 200),
                        (290, 80, 65, 210), (360, 95, 50, 190), (200, 120, 45, 160)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    im = im.filter(ImageFilter.GaussianBlur(5))
    save(im, "cloud.png", S)

def main():
    print("v3 art…")
    make_raft()
    make_sail()
    make_player()
    make_grill()
    make_chest()
    make_purifier()
    make_bed()
    make_hook()
    make_debris()
    make_misc()
    print("done")

if __name__ == "__main__":
    main()
