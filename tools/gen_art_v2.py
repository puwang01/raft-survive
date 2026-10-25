#!/usr/bin/env python3
"""High-quality procedural art for Raft Survive — match Raft screenshot vibe."""
from __future__ import annotations
import math, random, os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUT = "/workspace/raft-survive/godot/assets/art"
os.makedirs(OUT, exist_ok=True)
RNG = random.Random(42)

def save(im: Image.Image, name: str, scale_down: int = 2):
    """Draw at 2x then downsample for smooth edges."""
    if scale_down > 1:
        w, h = im.size
        im = im.resize((w // scale_down, h // scale_down), Image.LANCZOS)
    path = os.path.join(OUT, name)
    im.save(path, "PNG", optimize=True)
    print(f"  {name} {im.size}")

def aa_new(w, h, scale=2):
    return Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0)), scale

def noise_grain(im, amount=18, seed=0):
    rng = random.Random(seed)
    px = im.load()
    w, h = im.size
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            d = rng.randint(-amount, amount)
            px[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)), a)
            if x + 1 < w:
                px[x + 1, y] = px[x, y]
            if y + 1 < h:
                px[x, y + 1] = px[x, y]
                if x + 1 < w:
                    px[x + 1, y + 1] = px[x, y]
    return im

def soft_shadow(base, offset=(6, 8), blur=6, alpha=80):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    mask = base.split()[-1]
    shadow = Image.new("RGBA", base.size, (20, 12, 8, alpha))
    shadow.putalpha(mask)
    sh.paste(shadow, offset, shadow)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.alpha_composite(sh, base)
    return out

# ---------- WOOD HELPERS ----------
def wood_fill(draw, box, light, mid, dark, grain=True):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=max(2, (y1 - y0) // 8), fill=mid)
    # top highlight edge
    draw.rectangle([x0 + 2, y0 + 2, x1 - 2, y0 + max(3, (y1 - y0) // 6)], fill=light)
    # bottom shade
    draw.rectangle([x0 + 2, y1 - max(3, (y1 - y0) // 5), x1 - 2, y1 - 2], fill=dark)
    if grain:
        for i in range(x0 + 6, x1 - 4, 7):
            yy = y0 + 4 + (i * 3) % max(1, (y1 - y0 - 10))
            draw.line([(i, y0 + 5), (i + 2, y1 - 5)], fill=dark + (90,), width=1)

def plank_rect(im, box, seed=0):
    """Draw a single wood plank with grain and edge bevel."""
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    rng = random.Random(seed)
    mid = (168, 118, 62, 255)
    light = (210, 168, 105, 255)
    dark = (110, 72, 36, 255)
    edge = (78, 48, 22, 255)
    d.rounded_rectangle(box, radius=3, fill=mid, outline=edge, width=2)
    # bevel
    d.line([(x0 + 3, y0 + 3), (x1 - 3, y0 + 3)], fill=light, width=2)
    d.line([(x0 + 3, y1 - 3), (x1 - 3, y1 - 3)], fill=dark, width=2)
    # grain lines
    for i in range(4):
        gx = x0 + 8 + i * ((x1 - x0) // 5) + rng.randint(-2, 2)
        col = (dark[0] + rng.randint(-10, 10), dark[1] + rng.randint(-8, 8), dark[2], 140)
        d.line([(gx, y0 + 6), (gx + rng.randint(-3, 3), y1 - 6)], fill=col, width=1)
    # knots
    if rng.random() > 0.55:
        kx = rng.randint(x0 + 10, x1 - 10)
        ky = rng.randint(y0 + 6, y1 - 6)
        d.ellipse([kx - 3, ky - 2, kx + 3, ky + 2], fill=(90, 55, 28, 200))

# ---------- RAFT ----------
def make_raft():
    W, H, S = 420, 340, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # soft water foam under raft
    foam = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(foam)
    cx, cy = W * S // 2, H * S // 2 + 10
    fd.ellipse([cx - 200, cy - 140, cx + 200, cy + 150], fill=(220, 245, 255, 55))
    foam = foam.filter(ImageFilter.GaussianBlur(18))
    im = Image.alpha_composite(im, foam)
    d = ImageDraw.Draw(im)

    # 3x3-ish plank grid (screenshot style square platform)
    margin_x, margin_y = 40, 50
    pw, ph = (W * S - margin_x * 2), (H * S - margin_y * 2)
    rows, cols = 5, 5
    plank_h = ph // rows
    plank_w = pw // cols
    ox, oy = margin_x, margin_y
    for r in range(rows):
        for c in range(cols):
            x0 = ox + c * plank_w + 2
            y0 = oy + r * plank_h + 2
            x1 = x0 + plank_w - 4
            y1 = y0 + plank_h - 4
            # slight stagger for organic look
            x0 += (r % 2) * 2
            plank_rect(im, [x0, y0, x1, y1], seed=r * 10 + c)
    d = ImageDraw.Draw(im)

    # rope lashings across joints
    rope = (92, 64, 36, 255)
    rope_hi = (140, 105, 70, 255)
    for r in range(1, rows):
        y = oy + r * plank_h
        for c in range(cols):
            x = ox + c * plank_w + plank_w // 2
            d.ellipse([x - 10, y - 8, x + 10, y + 8], fill=rope)
            d.arc([x - 10, y - 8, x + 10, y + 8], 200, 340, fill=rope_hi, width=2)
    for c in range(1, cols):
        x = ox + c * plank_w
        for r in range(rows):
            y = oy + r * plank_h + plank_h // 2
            d.ellipse([x - 8, y - 10, x + 8, y + 10], fill=rope)

    # metal reinforcement bands at corners
    metal = (150, 155, 165, 255)
    metal_d = (90, 95, 105, 255)
    metal_h = (210, 215, 225, 255)
    for (bx, by) in [(ox + 8, oy + 8), (ox + pw - 50, oy + 8), (ox + 8, oy + ph - 40), (ox + pw - 50, oy + ph - 40)]:
        d.rounded_rectangle([bx, by, bx + 42, by + 28], radius=3, fill=metal, outline=metal_d, width=2)
        d.line([(bx + 4, by + 4), (bx + 38, by + 4)], fill=metal_h, width=2)
        # rivets
        for rx in (bx + 8, bx + 34):
            d.ellipse([rx - 3, by + 12, rx + 3, by + 18], fill=metal_d)

    # outer rim darker logs
    rim = (95, 60, 30, 255)
    d.rounded_rectangle([ox - 6, oy - 6, ox + pw + 6, oy + ph + 6], radius=10, outline=rim, width=6)

    im = noise_grain(im, 12, 7)
    im = soft_shadow(im, (10, 14), 10, 70)
    save(im, "raft.png", S)

# ---------- SAIL ----------
def make_sail():
    W, H, S = 200, 260, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # poles
    pole = (130, 90, 48, 255)
    pole_d = (80, 52, 24, 255)
    pole_h = (180, 140, 90, 255)
    # left mast
    d.rounded_rectangle([36, 20, 52, 480], radius=4, fill=pole, outline=pole_d, width=2)
    d.line([(38, 24), (38, 470)], fill=pole_h, width=2)
    # right mast
    d.rounded_rectangle([340, 40, 356, 480], radius=4, fill=pole, outline=pole_d, width=2)
    d.line([(342, 44), (342, 470)], fill=pole_h, width=2)
    # crossbeam
    d.rounded_rectangle([30, 50, 360, 66], radius=3, fill=pole, outline=pole_d, width=2)

    # sail cloth — soft white with folds
    sail = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sail)
    pts = [(55, 70), (335, 85), (330, 420), (60, 400)]
    sd.polygon(pts, fill=(248, 250, 252, 245))
    # cloth folds (vertical soft bands)
    for i, a in enumerate([40, 70, 50, 80, 45]):
        x = 80 + i * 55
        sd.polygon([(x, 80), (x + 18, 90), (x + 14, 400), (x - 4, 390)], fill=(220, 228, 238, a))
    # blue patch like screenshot
    sd.rounded_rectangle([200, 160, 270, 230], radius=6, fill=(70, 140, 210, 220), outline=(40, 90, 160, 255), width=2)
    # stitching
    sd.line([(55, 75), (335, 90)], fill=(200, 205, 215, 180), width=2)
    sd.line([(60, 395), (330, 415)], fill=(200, 205, 215, 180), width=2)
    sail = sail.filter(ImageFilter.GaussianBlur(0.6))
    im = Image.alpha_composite(im, sail)
    # rope ties
    d = ImageDraw.Draw(im)
    for (x, y) in [(44, 75), (348, 90), (44, 400), (348, 420)]:
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(100, 70, 40, 255))
    im = soft_shadow(im, (8, 10), 8, 50)
    save(im, "sail.png", S)

# ---------- PLAYER (anime-ish, back/3q, white tee + tan shorts) ----------
def make_player():
    W, H, S = 180, 240, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # scale coords: draw in *S space
    # body proportions — young male, screenshot style
    # head
    skin = (242, 198, 168, 255)
    skin_s = (210, 160, 128, 255)
    skin_h = (255, 225, 200, 255)
    hair = (92, 58, 36, 255)
    hair_h = (140, 95, 55, 255)
    shirt = (250, 252, 255, 255)
    shirt_s = (210, 218, 230, 255)
    shorts = (168, 128, 78, 255)
    shorts_d = (120, 85, 48, 255)
    boot = (92, 62, 40, 255)

    cx = W * S // 2

    # legs (standing, slight lean back for throw)
    d.rounded_rectangle([cx - 38, 280, cx - 8, 400], radius=8, fill=skin)
    d.rounded_rectangle([cx + 6, 280, cx + 36, 400], radius=8, fill=skin)
    # boots
    d.rounded_rectangle([cx - 42, 390, cx - 4, 430], radius=6, fill=boot)
    d.rounded_rectangle([cx + 2, 390, cx + 40, 430], radius=6, fill=boot)
    d.ellipse([cx - 44, 418, cx - 2, 440], fill=boot)
    d.ellipse([cx + 0, 418, cx + 42, 440], fill=boot)

    # shorts
    d.rounded_rectangle([cx - 48, 250, cx + 48, 310], radius=10, fill=shorts, outline=shorts_d, width=2)
    d.line([(cx, 255), (cx, 305)], fill=shorts_d, width=2)  # center seam
    # pocket
    d.rounded_rectangle([cx + 18, 265, cx + 40, 290], radius=3, outline=shorts_d, width=2)

    # torso white tee
    d.rounded_rectangle([cx - 50, 130, cx + 50, 265], radius=14, fill=shirt)
    # sleeve left (throwing arm extended back-right in screenshot - arm out)
    d.polygon([(cx - 50, 145), (cx - 50, 195), (cx - 95, 210), (cx - 100, 175)], fill=shirt)
    # sleeve right / throwing arm raised forward-right
    d.polygon([(cx + 48, 140), (cx + 55, 185), (cx + 130, 120), (cx + 125, 95)], fill=shirt)
    # shirt shading folds
    d.arc([cx - 30, 160, cx + 10, 230], 20, 160, fill=shirt_s, width=3)
    d.line([(cx - 20, 200), (cx + 25, 240)], fill=shirt_s, width=2)
    # neck
    d.ellipse([cx - 16, 115, cx + 16, 145], fill=skin)

    # throwing arm (right) — skin forearm + hand gripping rope
    d.polygon([(cx + 115, 100), (cx + 145, 85), (cx + 160, 110), (cx + 125, 125)], fill=skin)
    d.ellipse([cx + 148, 95, cx + 172, 120], fill=skin)  # hand
    # left arm slight back
    d.polygon([(cx - 95, 185), (cx - 120, 230), (cx - 100, 245), (cx - 80, 205)], fill=skin)
    d.ellipse([cx - 130, 225, cx - 105, 250], fill=skin)

    # head (from behind / 3q — mostly hair, ear, jaw hint)
    d.ellipse([cx - 42, 40, cx + 42, 125], fill=skin)
    # ear
    d.ellipse([cx + 32, 75, cx + 50, 100], fill=skin_s)
    # jaw shade
    d.arc([cx - 35, 70, cx + 35, 120], 10, 170, fill=skin_s, width=3)

    # hair — brown, volume, anime style from behind
    d.ellipse([cx - 48, 28, cx + 48, 100], fill=hair)
    # bangs / tufts
    for ox, oy, r in [(-30, 35, 22), (-10, 22, 24), (15, 28, 26), (35, 40, 20), (-40, 55, 16), (40, 60, 15)]:
        d.ellipse([cx + ox - r, oy, cx + ox + r, oy + r * 2], fill=hair)
    # hair highlight
    d.arc([cx - 25, 35, cx + 5, 70], 200, 320, fill=hair_h, width=4)
    d.arc([cx + 5, 40, cx + 30, 75], 200, 300, fill=hair_h, width=3)

    # rope in hand
    rope = (210, 200, 185, 255)
    d.line([(cx + 165, 108), (cx + 210, 70), (cx + 250, 40)], fill=rope, width=4)

    im = soft_shadow(im, (6, 8), 6, 55)
    # slight sharpen after soft edges
    im = im.filter(ImageFilter.SMOOTH_MORE)
    save(im, "player.png", S)

# ---------- GRILL ----------
def make_grill():
    W, H, S = 140, 130, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # stone base
    stone = (110, 105, 100, 255)
    stone_d = (70, 65, 60, 255)
    d.rounded_rectangle([40, 140, 240, 230], radius=12, fill=stone, outline=stone_d, width=3)
    for i in range(3):
        d.line([(50 + i * 60, 150), (50 + i * 60, 220)], fill=stone_d, width=2)
    # metal bowl
    metal = (70, 75, 85, 255)
    metal_h = (140, 150, 165, 255)
    d.ellipse([55, 90, 225, 170], fill=metal, outline=(40, 45, 55, 255), width=3)
    d.arc([60, 95, 220, 155], 200, 340, fill=metal_h, width=3)
    # fire / coals
    for col, box in [
        ((255, 120, 40, 230), [100, 110, 180, 155]),
        ((255, 200, 60, 200), [115, 115, 165, 145]),
        ((255, 250, 180, 180), [125, 120, 155, 138]),
    ]:
        d.ellipse(box, fill=col)
    # grill grate
    for i in range(5):
        y = 105 + i * 10
        d.line([(70, y), (210, y)], fill=(50, 50, 55, 220), width=2)
    # fish cooking
    fish = (220, 170, 110, 255)
    d.ellipse([95, 95, 185, 130], fill=fish, outline=(160, 110, 60, 255), width=2)
    d.ellipse([170, 105, 190, 122], fill=fish)  # head
    d.ellipse([178, 110, 184, 116], fill=(40, 30, 20, 255))  # eye
    d.polygon([(95, 112), (80, 100), (80, 124)], fill=fish)  # tail
    # smoke
    smoke = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    for i, (x, y, r, a) in enumerate([(120, 60, 22, 70), (145, 40, 28, 55), (165, 25, 24, 40), (100, 45, 18, 45)]):
        sd.ellipse([x - r, y - r, x + r, y + r], fill=(240, 245, 250, a))
    smoke = smoke.filter(ImageFilter.GaussianBlur(6))
    im = Image.alpha_composite(im, smoke)
    im = soft_shadow(im, (5, 6), 5, 60)
    save(im, "grill.png", S)

# ---------- CHEST ----------
def make_chest():
    W, H, S = 130, 110, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wood = (150, 100, 55, 255)
    wood_d = (95, 60, 30, 255)
    wood_h = (195, 150, 95, 255)
    metal = (155, 160, 170, 255)
    metal_d = (90, 95, 105, 255)
    # body
    d.rounded_rectangle([30, 80, 230, 190], radius=8, fill=wood, outline=wood_d, width=3)
    d.line([(35, 95), (225, 95)], fill=wood_h, width=3)
    # wood planks
    for y in (110, 140, 170):
        d.line([(40, y), (220, y)], fill=wood_d, width=2)
    # lid
    d.rounded_rectangle([28, 45, 232, 95], radius=10, fill=wood_h, outline=wood_d, width=3)
    d.arc([28, 30, 232, 90], 200, 340, fill=(220, 185, 130, 255), width=4)
    # metal bands
    for x in (50, 200):
        d.rectangle([x, 50, x + 18, 185], fill=metal, outline=metal_d, width=2)
        for ry in (65, 100, 150):
            d.ellipse([x + 4, ry, x + 14, ry + 10], fill=metal_d)
    # lock
    d.rounded_rectangle([115, 100, 145, 135], radius=4, fill=metal, outline=metal_d, width=2)
    d.ellipse([122, 108, 138, 124], outline=metal_d, width=2)
    im = soft_shadow(im, (6, 8), 6, 65)
    save(im, "chest.png", S)

# ---------- PURIFIER ----------
def make_purifier():
    W, H, S = 150, 170, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # barrel
    barrel = (150, 105, 60, 255)
    barrel_d = (95, 60, 28, 255)
    d.ellipse([70, 200, 230, 280], fill=barrel_d)
    d.rectangle([70, 120, 230, 240], fill=barrel)
    d.ellipse([70, 90, 230, 160], fill=(175, 130, 80, 255), outline=barrel_d, width=3)
    for y in (140, 180, 220):
        d.arc([75, y - 20, 225, y + 40], 0, 180, fill=barrel_d, width=3)
    # metal rings
    metal = (140, 145, 155, 255)
    for y in (130, 200):
        d.rectangle([65, y, 235, y + 12], fill=metal)
    # blue tarp funnel
    tarp = (55, 130, 200, 230)
    tarp_d = (30, 80, 150, 255)
    d.polygon([(40, 40), (260, 50), (200, 130), (100, 125)], fill=tarp, outline=tarp_d)
    # tarp folds
    d.line([(80, 55), (140, 120)], fill=(90, 170, 230, 160), width=3)
    d.line([(180, 60), (170, 125)], fill=(40, 100, 170, 140), width=2)
    # support sticks
    stick = (120, 85, 45, 255)
    d.line([(55, 45), (90, 200)], fill=stick, width=5)
    d.line([(245, 55), (210, 200)], fill=stick, width=5)
    # drip
    d.ellipse([140, 125, 155, 145], fill=(120, 200, 255, 180))
    im = soft_shadow(im, (5, 7), 6, 55)
    save(im, "purifier.png", S)

# ---------- BED / MAT ----------
def make_bed():
    W, H, S = 140, 80, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # green woven mat
    base = (70, 140, 85, 255)
    dark = (45, 100, 60, 255)
    light = (110, 180, 120, 255)
    d.rounded_rectangle([20, 30, 260, 140], radius=10, fill=base, outline=dark, width=3)
    # weave pattern
    for i in range(8):
        y = 40 + i * 12
        d.line([(30, y), (250, y)], fill=dark if i % 2 == 0 else light, width=2)
    for i in range(12):
        x = 35 + i * 18
        d.line([(x, 35), (x, 135)], fill=(55, 120, 70, 100), width=1)
    # fringe
    for x in range(30, 255, 14):
        d.line([(x, 138), (x + 3, 150)], fill=dark, width=2)
    im = soft_shadow(im, (4, 5), 4, 50)
    save(im, "bed.png", S)

# ---------- HOOK ----------
def make_hook():
    W, H, S = 64, 64, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    metal = (180, 190, 205, 255)
    metal_d = (90, 100, 120, 255)
    metal_h = (235, 240, 250, 255)
    # shank
    d.line([(64, 20), (64, 80)], fill=metal, width=10)
    d.line([(60, 22), (60, 78)], fill=metal_h, width=3)
    # curve
    d.arc([40, 70, 100, 120], 0, 270, fill=metal, width=10)
    d.arc([44, 74, 96, 116], 10, 250, fill=metal_h, width=3)
    # tip
    d.polygon([(48, 95), (40, 110), (55, 108)], fill=metal_d)
    # eye
    d.ellipse([54, 10, 74, 30], outline=metal, width=5)
    im = soft_shadow(im, (3, 3), 3, 50)
    save(im, "hook.png", S)

# ---------- DEBRIS ----------
def make_debris_wood():
    W, H, S = 160, 70, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    for i, (y, h, seed) in enumerate([(20, 35, 1), (55, 32, 2), (90, 30, 3)]):
        plank_rect(im, [20 + i * 8, y, 300 - i * 10, y + h], seed=seed)
    # ropes
    d = ImageDraw.Draw(im)
    d.ellipse([140, 40, 180, 100], outline=(100, 70, 40, 255), width=4)
    im = soft_shadow(im, (4, 5), 5, 55)
    # foam hint
    foam = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(foam)
    fd.ellipse([10, 100, 310, 140], fill=(230, 250, 255, 60))
    foam = foam.filter(ImageFilter.GaussianBlur(4))
    im = Image.alpha_composite(foam, im)
    save(im, "debris_wood.png", S)

def make_debris_barrel():
    W, H, S = 100, 120, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wood = (155, 108, 58, 255)
    wood_d = (95, 60, 28, 255)
    d.ellipse([40, 160, 160, 220], fill=wood_d)
    d.rectangle([40, 50, 160, 190], fill=wood)
    d.ellipse([40, 30, 160, 90], fill=(180, 135, 80, 255), outline=wood_d, width=3)
    metal = (140, 145, 155, 255)
    for y in (70, 140):
        d.rectangle([35, y, 165, y + 14], fill=metal)
    # wet highlight
    d.arc([50, 45, 100, 160], 200, 320, fill=(255, 255, 255, 90), width=4)
    im = soft_shadow(im, (5, 6), 5, 60)
    save(im, "debris_barrel.png", S)

def make_debris_crate():
    W, H, S = 110, 100, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wood = (160, 115, 65, 255)
    wood_d = (100, 65, 32, 255)
    d.rounded_rectangle([30, 40, 190, 180], radius=6, fill=wood, outline=wood_d, width=3)
    # planks
    for y in (70, 110, 150):
        d.line([(40, y), (180, y)], fill=wood_d, width=2)
    # X brace
    d.line([(45, 50), (175, 170)], fill=wood_d, width=3)
    d.line([(175, 50), (45, 170)], fill=wood_d, width=3)
    # metal corners
    metal = (150, 155, 165, 255)
    for (x, y) in [(30, 40), (170, 40), (30, 160), (170, 160)]:
        d.rectangle([x, y, x + 20, y + 20], outline=metal, width=3)
    im = soft_shadow(im, (5, 6), 5, 60)
    save(im, "debris_crate.png", S)

def make_debris_fish():
    W, H, S = 100, 60, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = (90, 170, 200, 255)
    body_d = (40, 100, 140, 255)
    belly = (200, 230, 240, 255)
    d.ellipse([30, 30, 160, 90], fill=body)
    d.ellipse([40, 50, 150, 90], fill=belly)
    d.polygon([(30, 55), (5, 30), (5, 85)], fill=body_d)  # tail
    d.polygon([(90, 30), (110, 10), (120, 35)], fill=body_d)  # fin
    d.ellipse([140, 50, 155, 65], fill=(20, 30, 40, 255))  # eye
    d.ellipse([142, 52, 148, 58], fill=(255, 255, 255, 200))
    # scale shimmer
    for i in range(5):
        d.arc([50 + i * 18, 40, 80 + i * 18, 80], 200, 340, fill=(255, 255, 255, 60), width=1)
    im = soft_shadow(im, (3, 4), 3, 40)
    save(im, "debris_fish.png", S)

def make_debris_bottle():
    W, H, S = 48, 80, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    glass = (120, 200, 170, 180)
    d.rounded_rectangle([25, 50, 70, 140], radius=8, fill=glass, outline=(60, 140, 110, 220), width=2)
    d.rectangle([35, 20, 60, 55], fill=glass, outline=(60, 140, 110, 220), width=2)
    d.rectangle([32, 15, 63, 28], fill=(180, 100, 60, 255))  # cork
    d.line([(30, 60), (30, 130)], fill=(220, 255, 240, 120), width=3)
    save(im, "debris_bottle.png", S)

def make_shark():
    W, H, S = 160, 70, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = (90, 110, 130, 230)
    dark = (50, 65, 85, 230)
    d.ellipse([40, 40, 260, 110], fill=body)
    d.polygon([(260, 70), (310, 55), (310, 90)], fill=body)  # nose
    d.polygon([(40, 70), (5, 40), (15, 100)], fill=dark)  # tail
    d.polygon([(140, 40), (160, 5), (180, 45)], fill=dark)  # dorsal
    d.ellipse([270, 60, 285, 75], fill=(20, 20, 30, 255))
    # belly
    d.ellipse([60, 75, 240, 110], fill=(180, 195, 210, 180))
    im = soft_shadow(im, (4, 4), 4, 40)
    save(im, "shark.png", S)

def make_coral():
    W, H, S = 160, 120, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    colors = [(200, 90, 120, 160), (80, 160, 140, 150), (220, 140, 80, 140), (160, 80, 180, 130)]
    for i, col in enumerate(colors):
        x = 40 + i * 70
        d.ellipse([x, 120, x + 50, 200], fill=col)
        for j in range(3):
            d.ellipse([x + j * 12 - 5, 60 + j * 15, x + 30 + j * 8, 130 + j * 10], fill=col)
    # rocks
    d.ellipse([20, 180, 300, 240], fill=(60, 70, 80, 140))
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    save(im, "coral.png", S)

def make_sky():
    W, H = 900, 420
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # gradient sky — bright clear day
    for y in range(H):
        t = y / H
        # top soft blue -> horizon pale cyan
        r = int(135 + t * 80)
        g = int(190 + t * 40)
        b = int(245 - t * 30)
        a = int(255 - t * 40)
        d.line([(0, y), (W, y)], fill=(r, g, b, a))
    # soft sun glow top-right
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([620, -40, 860, 200], fill=(255, 250, 210, 90))
    gd.ellipse([680, 10, 800, 130], fill=(255, 255, 230, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    im = Image.alpha_composite(im, glow)
    save(im, "sky.png", 1)

def make_ocean_underlay():
    """Deep ocean texture with coral silhouettes for under water shader."""
    W, H = 900, 1400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        r = int(12 + t * 8)
        g = int(70 + t * 40)
        b = int(95 + t * 25)
        d.line([(0, y), (W, y)], fill=(r, g, b, 255))
    # coral / rock silhouettes
    rng = random.Random(9)
    for _ in range(25):
        x, y = rng.randint(0, W), rng.randint(int(H * 0.35), H)
        col = (rng.randint(20, 60), rng.randint(80, 140), rng.randint(70, 110), rng.randint(40, 90))
        r = rng.randint(20, 70)
        d.ellipse([x - r, y - r // 2, x + r, y + r], fill=col)
        for _k in range(3):
            d.ellipse([x + rng.randint(-r, r), y - rng.randint(10, 60),
                       x + rng.randint(-r // 2, r // 2), y], fill=col)
    # sand patches
    for _ in range(12):
        x, y = rng.randint(0, W), rng.randint(int(H * 0.5), H)
        d.ellipse([x, y, x + rng.randint(40, 120), y + rng.randint(15, 40)],
                  fill=(40, 100, 90, 50))
    im = im.filter(ImageFilter.GaussianBlur(2))
    save(im, "ocean.png", 1)

def make_cloud():
    W, H, S = 220, 100, 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for (x, y, r, a) in [(80, 80, 55, 200), (140, 70, 65, 210), (200, 85, 50, 190),
                          (260, 75, 60, 200), (320, 90, 45, 180), (180, 110, 40, 150)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    im = im.filter(ImageFilter.GaussianBlur(4))
    save(im, "cloud.png", S)

def make_hud_bits():
    # panel
    im = Image.new("RGBA", (64, 64), (25, 35, 55, 200))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 2, 61, 61], radius=10, outline=(140, 110, 70, 255), width=3)
    save(im, "hud_panel.png", 1)
    # slot
    im = Image.new("RGBA", (72, 72), (20, 28, 45, 210))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 2, 69, 69], radius=8, outline=(160, 125, 75, 255), width=3)
    d.rounded_rectangle([6, 6, 65, 65], radius=6, outline=(60, 70, 90, 180), width=2)
    save(im, "inv_slot.png", 1)
    # icons
    for name, col, shape in [
        ("icon_health", (230, 70, 90), "heart"),
        ("icon_hunger", (240, 190, 60), "fork"),
        ("icon_thirst", (70, 180, 240), "drop"),
    ]:
        im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if shape == "heart":
            d.ellipse([4, 6, 16, 18], fill=col)
            d.ellipse([14, 6, 26, 18], fill=col)
            d.polygon([(5, 14), (15, 28), (27, 14)], fill=col)
        elif shape == "fork":
            d.rectangle([14, 8, 18, 26], fill=col)
            d.rectangle([8, 6, 12, 16], fill=col)
            d.rectangle([20, 6, 24, 16], fill=col)
            d.rectangle([10, 22, 22, 26], fill=col)
        else:
            d.ellipse([8, 12, 24, 28], fill=col)
            d.polygon([(16, 4), (8, 16), (24, 16)], fill=col)
        save(im, f"{name}.png", 1)

def main():
    print("Generating high-quality art…")
    make_raft()
    make_sail()
    make_player()
    make_grill()
    make_chest()
    make_purifier()
    make_bed()
    make_hook()
    make_debris_wood()
    make_debris_barrel()
    make_debris_crate()
    make_debris_fish()
    make_debris_bottle()
    make_shark()
    make_coral()
    make_sky()
    make_ocean_underlay()
    make_cloud()
    make_hud_bits()
    print("Done.")

if __name__ == "__main__":
    main()
