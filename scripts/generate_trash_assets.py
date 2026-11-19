#!/usr/bin/env python3
"""
Generator script for Scrap-Byte pixel-art trash textures and XML atlas.
Creates:
- assets/trash/trash.png (256x576 sprite sheet, 9 items x 4 frames, 64x64 each)
- assets/trash/trash.xml (Starling/Sparrow TextureAtlas XML)
- assets/trash/individual/*.png (Individual frames)
- assets/trash/preview.png (Combined preview grid with labels)
"""

import math
import os
from pathlib import Path
from PIL import Image, ImageDraw

ASSETS_DIR = Path("assets/trash")
INDIVIDUAL_DIR = ASSETS_DIR / "individual"
FRAME_SIZE = 64


def create_base_canvas():
    return Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))


def draw_contact_shadow(d: ImageDraw.Draw, cx: int, cy: int, rx: int, ry: int):
    """Draws a multi-layered soft contact shadow on the floor under the object."""
    layers = [
        (rx + 4, ry + 2, (4, 6, 10, 45)),
        (rx + 2, ry + 1, (3, 5, 8, 90)),
        (rx, ry, (2, 3, 6, 145)),
        (int(rx * 0.65), int(ry * 0.65), (0, 1, 3, 195)),
    ]
    for r_x, r_y, col in layers:
        d.ellipse([cx - r_x, cy - r_y, cx + r_x, cy + r_y], fill=col)


# ---------------------------------------------------------------------------
# 1. SCRAP CHIP (scrap_chip_0 .. 3)
# ---------------------------------------------------------------------------
def draw_scrap_chip(frame_idx: int) -> Image.Image:
    im = create_base_canvas()
    d = ImageDraw.Draw(im)

    # 1. Soft ground contact shadow
    draw_contact_shadow(d, 32, 53, 19, 6)

    # 2. Metallic pins extending left and right
    pin_y_positions = [20, 26, 32, 38, 44]
    for py in pin_y_positions:
        # Left pin shadow + pin
        d.line([(8, py + 1), (17, py + 1)], fill=(15, 18, 25, 180), width=2)
        d.line([(9, py), (17, py)], fill=(160, 130, 45, 255), width=2)
        d.line([(9, py), (16, py)], fill=(255, 225, 105, 255), width=1)
        d.point((8, py), fill=(225, 195, 80, 255))
        d.point((17, py), fill=(100, 80, 25, 255))
        # Right pin shadow + pin
        d.line([(46, py + 1), (55, py + 1)], fill=(15, 18, 25, 180), width=2)
        d.line([(46, py), (54, py)], fill=(160, 130, 45, 255), width=2)
        d.line([(47, py), (54, py)], fill=(255, 225, 105, 255), width=1)
        d.point((55, py), fill=(225, 195, 80, 255))
        d.point((46, py), fill=(100, 80, 25, 255))

    # 3. Main IC Ceramic Body: (16, 15) to (47, 48)
    # Beveled body outline
    d.rounded_rectangle([16, 15, 47, 48], radius=3, fill=(20, 24, 34, 255))
    # Body dark fill
    d.rounded_rectangle([17, 16, 46, 47], radius=2, fill=(35, 42, 56, 255))
    # Top/left specular highlight
    d.line([(18, 16), (45, 16)], fill=(75, 92, 120, 255))
    d.line([(17, 17), (17, 46)], fill=(65, 80, 105, 255))
    # Bottom/right ambient shadow
    d.line([(18, 47), (46, 47)], fill=(18, 22, 30, 255))
    d.line([(46, 17), (46, 46)], fill=(20, 25, 35, 255))

    # Metallic center heatspreader / die
    d.rectangle([23, 23, 40, 40], fill=(48, 58, 76, 255), outline=(26, 32, 44, 255))
    d.rectangle([24, 24, 39, 39], fill=(58, 70, 92, 255))
    d.line([(24, 24), (39, 24)], fill=(105, 125, 155, 255))
    d.line([(24, 24), (24, 39)], fill=(90, 110, 140, 255))
    d.line([(24, 39), (39, 39)], fill=(28, 35, 48, 255))
    d.line([(39, 24), (39, 39)], fill=(30, 38, 52, 255))

    # Pin 1 index notch (dot)
    d.ellipse([19, 18, 22, 21], fill=(16, 20, 28, 255), outline=(10, 14, 20, 255))
    d.point((20, 19), fill=(10, 14, 20, 255))

    # Circuit traces on chip surface
    d.line([(20, 30), (23, 30)], fill=(80, 100, 130, 255))
    d.line([(20, 36), (23, 36)], fill=(80, 100, 130, 255))
    d.line([(40, 30), (43, 30)], fill=(80, 100, 130, 255))
    d.line([(40, 36), (43, 36)], fill=(80, 100, 130, 255))

    # Silicon core markings
    d.line([(27, 31), (36, 31)], fill=(90, 115, 145, 255))
    d.line([(29, 33), (34, 33)], fill=(80, 105, 135, 255))

    # 3 Status micro-LEDs (Green, Cyan, Amber)
    led_positions = [(27, 27), (31, 27), (36, 27)]
    states = [
        [(2, (50, 255, 120)), (0, (15, 45, 50)), (0, (50, 25, 15))],
        [(1, (40, 180, 90)), (2, (60, 245, 255)), (0, (50, 25, 15))],
        [(0, (15, 50, 25)), (1, (30, 160, 180)), (2, (255, 200, 40))],
        [(2, (50, 255, 120)), (2, (70, 245, 255)), (1, (200, 140, 30))],
    ]

    for (lx, ly), (intensity, col) in zip(led_positions, states[frame_idx]):
        if intensity == 2:
            # Multi-layer radial neon aura glow
            d.ellipse([lx - 3, ly - 3, lx + 4, ly + 4], fill=(col[0], col[1], col[2], 50))
            d.ellipse([lx - 2, ly - 2, lx + 3, ly + 3], fill=(col[0], col[1], col[2], 100))
            d.rectangle([lx, ly, lx + 1, ly + 1], fill=(col[0], col[1], col[2], 255))
            d.point((lx, ly), fill=(255, 255, 255, 255))
        elif intensity == 1:
            d.ellipse([lx - 1, ly - 1, lx + 2, ly + 2], fill=(col[0], col[1], col[2], 60))
            d.rectangle([lx, ly, lx + 1, ly + 1], fill=(col[0], col[1], col[2], 240))
        else:
            d.rectangle([lx, ly, lx + 1, ly + 1], fill=(col[0], col[1], col[2], 180))

    # Animated bus trace pulse along bottom of die
    pulse_x = 24 + frame_idx * 4
    d.line([(24, 37), (39, 37)], fill=(40, 52, 70, 255))
    d.line([max(24, pulse_x - 2), 37, min(39, pulse_x + 2), 37], fill=(140, 240, 255, 255))
    d.point((min(39, pulse_x), 37), fill=(255, 255, 255, 255))

    return im


# ---------------------------------------------------------------------------
# 2. SCRAP BOARD (scrap_board_0 .. 3)
# ---------------------------------------------------------------------------
def draw_scrap_board(frame_idx: int) -> Image.Image:
    im = create_base_canvas()
    d = ImageDraw.Draw(im)

    # 1. Soft ground contact shadow
    draw_contact_shadow(d, 32, 54, 21, 6)

    # 2. PCB base polygon (clipped corners)
    pcb_poly = [
        (16, 12), (48, 12), (52, 16), (52, 48),
        (48, 52), (16, 52), (12, 48), (12, 16)
    ]
    d.polygon(pcb_poly, fill=(16, 76, 54, 255), outline=(8, 38, 26, 255))

    # Inner bevel / edge track
    inner_poly = [
        (17, 14), (47, 14), (50, 17), (50, 47),
        (47, 50), (17, 50), (14, 47), (14, 17)
    ]
    d.polygon(inner_poly, outline=(30, 118, 82, 255))

    # Bottom edge shadow
    d.line([(16, 51), (48, 51)], fill=(10, 45, 32, 255))
    d.line([(48, 51), (51, 48)], fill=(10, 45, 32, 255))

    # Mounting holes at corners (gold/silver plated ring + hole)
    holes = [(16, 16), (48, 16), (16, 48), (48, 48)]
    for hx, hy in holes:
        d.ellipse([hx - 2, hy - 2, hx + 2, hy + 2], fill=(215, 190, 95, 255), outline=(130, 110, 45, 255))
        d.point((hx, hy), fill=(8, 16, 12, 255))

    # Copper printed traces
    traces = [
        [(16, 26), (22, 26), (26, 30), (26, 36)],
        [(48, 26), (42, 26), (38, 30)],
        [(26, 36), (36, 36), (40, 40), (44, 40)],
        [(30, 16), (30, 22)],
        [(36, 44), (36, 48)],
    ]
    for tr in traces:
        for i in range(len(tr) - 1):
            d.line([tr[i], tr[i + 1]], fill=(185, 145, 55, 255), width=2)
            d.line([tr[i], tr[i + 1]], fill=(240, 200, 90, 255), width=1)

    # Electrolytic capacitor (blue cylinder with silver stripe) at (40, 18)
    d.rectangle([39, 26, 46, 27], fill=(10, 30, 60, 180))  # Capacitor shadow
    d.rounded_rectangle([39, 18, 46, 26], radius=2, fill=(28, 70, 150, 255), outline=(14, 38, 85, 255))
    d.rectangle([44, 19, 45, 25], fill=(215, 225, 240, 255))
    d.line([(40, 19), (43, 19)], fill=(50, 115, 230, 255))

    # Resistor 1 (tan body with color stripes) at (17, 36)
    d.rounded_rectangle([16, 36, 23, 40], radius=1, fill=(215, 185, 145, 255), outline=(115, 95, 65, 255))
    d.line([(18, 36), (18, 40)], fill=(190, 30, 30, 255))
    d.line([(20, 36), (20, 40)], fill=(35, 35, 35, 255))
    d.line([(22, 36), (22, 40)], fill=(225, 185, 45, 255))

    # Resistor 2 at (40, 43)
    d.rounded_rectangle([39, 43, 46, 47], radius=1, fill=(215, 185, 145, 255), outline=(115, 95, 65, 255))
    d.line([(41, 43), (41, 47)], fill=(40, 150, 40, 255))
    d.line([(43, 43), (43, 47)], fill=(190, 30, 30, 255))

    # Main SMD chip in center: (25, 24, 36, 34)
    d.rectangle([25, 24, 36, 34], fill=(26, 32, 42, 255), outline=(14, 18, 25, 255))
    d.point((26, 25), fill=(90, 105, 130, 255))
    for py in [26, 28, 30, 32]:
        d.point((24, py), fill=(220, 225, 235, 255))
        d.point((37, py), fill=(220, 225, 235, 255))

    # Diagnostic LED near chip with radial glow
    led_col = [
        (40, 180, 60),
        (90, 255, 110),
        (40, 180, 60),
        (20, 90, 30)
    ][frame_idx]
    if frame_idx == 1:
        d.ellipse([21, 17, 27, 23], fill=(80, 255, 120, 90))
    d.ellipse([23, 19, 25, 21], fill=led_col)

    # Animated signal pulse moving along traces
    pulse_nodes = [
        (16, 26),
        (26, 30),
        (38, 36),
        (44, 40)
    ]
    px, py = pulse_nodes[frame_idx]
    d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 150, 90))
    d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 220, 255))

    # Capacitor spark in frame 2
    if frame_idx == 2:
        d.ellipse([40, 15, 45, 20], fill=(140, 230, 255, 110))
        d.point((43, 17), fill=(255, 255, 255, 255))

    return im


# ---------------------------------------------------------------------------
# 3. SCRAP CORE (scrap_core_0 .. 3)
# ---------------------------------------------------------------------------
def draw_scrap_core(frame_idx: int) -> Image.Image:
    im = create_base_canvas()
    d = ImageDraw.Draw(im)

    cx, cy = 32, 32

    # 1. Soft ground contact shadow
    draw_contact_shadow(d, cx, 54, 21, 6)

    # 2. Outer Armored Titanium Octagonal Frame
    def oct_points(r):
        pts = []
        for i in range(8):
            ang = math.pi / 8 + i * (math.pi / 4)
            pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
        return pts

    d.polygon(oct_points(23), fill=(35, 42, 54, 255), outline=(16, 20, 28, 255))
    d.polygon(oct_points(21), fill=(52, 60, 78, 255), outline=(75, 88, 110, 255))
    d.polygon(oct_points(17), fill=(20, 24, 34, 255), outline=(12, 16, 22, 255))

    # Frame Bolts with highlights
    for i in range(8):
        ang = math.pi / 8 + i * (math.pi / 4)
        bx = cx + int(19.5 * math.cos(ang))
        by = cy + int(19.5 * math.sin(ang))
        d.point((bx, by), fill=(200, 215, 235, 255))
        d.point((bx, by + 1), fill=(25, 30, 42, 255))

    # 4 Magnetic Containment Prongs (cardinal directions)
    prongs = [
        [(cx - 2, cy - 22), (cx + 2, cy - 22), (cx + 1, cy - 14), (cx - 1, cy - 14)],
        [(cx + 22, cy - 2), (cx + 22, cy + 2), (cx + 14, cy + 1), (cx + 14, cy - 1)],
        [(cx + 2, cy + 22), (cx - 2, cy + 22), (cx - 1, cy + 14), (cx + 1, cy + 14)],
        [(cx - 22, cy + 2), (cx - 22, cy - 2), (cx - 14, cy - 1), (cx - 14, cy + 1)],
    ]
    for p in prongs:
        d.polygon(p, fill=(85, 102, 128, 255), outline=(22, 28, 38, 255))

    # Rotating energy field orbit particles
    angle_offset = frame_idx * (math.pi / 4)
    for i in range(4):
        ang = angle_offset + i * (math.pi / 2)
        ox = cx + int(15 * math.cos(ang))
        oy = cy + int(15 * math.sin(ang))
        d.ellipse([ox - 2, oy - 2, ox + 2, oy + 2], fill=(255, 200, 50, 100))
        d.ellipse([ox - 1, oy - 1, ox + 1, oy + 1], fill=(255, 240, 120, 255))

    radii = [8, 10, 12, 9]
    cr = radii[frame_idx]

    # Outer multi-layer pulsating corona glow
    d.ellipse([cx - cr - 6, cy - cr - 6, cx + cr + 6, cy + cr + 6], fill=(255, 140, 20, 40))
    d.ellipse([cx - cr - 3, cy - cr - 3, cx + cr + 3, cy + cr + 3], fill=(255, 175, 35, 80))

    if frame_idx == 2:
        # Supercharged state: blinding white-gold corona + plasma bolts
        d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(255, 220, 60, 100))
        d.line([(cx, cy - 5), (cx - 3, cy - 11), (cx, cy - 15)], fill=(255, 255, 255, 255), width=2)
        d.line([(cx + 5, cy), (cx + 11, cy + 2), (cx + 15, cy)], fill=(220, 250, 255, 255), width=2)
        d.line([(cx, cy + 5), (cx + 2, cy + 11), (cx, cy + 15)], fill=(255, 255, 255, 255), width=2)
        d.line([(cx - 5, cy), (cx - 11, cy - 2), (cx - 15, cy)], fill=(220, 250, 255, 255), width=2)
    elif frame_idx == 3:
        # Ionization ring
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=(80, 220, 255, 170), width=1)

    # Core sphere
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 175, 30, 255))
    inner_r = max(2, cr - 3)
    d.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=(255, 240, 110, 255))
    hot_r = max(1, inner_r - 2)
    d.ellipse([cx - hot_r, cy - hot_r, cx + hot_r, cy + hot_r], fill=(255, 255, 250, 255))

    return im


# ---------------------------------------------------------------------------
# 4. SCRAP CRYSTAL (scrap_crystal_0 .. 3)
# ---------------------------------------------------------------------------
def draw_scrap_crystal(frame_idx: int) -> Image.Image:
    im = create_base_canvas()
    d = ImageDraw.Draw(im)

    # 1. Soft ground contact shadow
    draw_contact_shadow(d, 32, 54, 17, 5)

    # 2. Left satellite shard
    left_shard_poly = [(16, 26), (23, 19), (25, 44), (18, 48)]
    d.polygon(left_shard_poly, fill=(90, 25, 120, 255), outline=(32, 8, 45, 255))
    d.line([(23, 19), (25, 44)], fill=(160, 50, 190, 255))

    # Right satellite shard
    right_shard_poly = [(48, 24), (41, 17), (39, 44), (46, 48)]
    d.polygon(right_shard_poly, fill=(65, 20, 115, 255), outline=(22, 8, 40, 255))
    d.line([(41, 17), (39, 44)], fill=(130, 45, 200, 255))

    # Main Central Crystal Facets:
    # Top-Left
    d.polygon([(32, 8), (22, 28), (32, 33)], fill=(145, 38, 165, 255))
    # Top-Right
    d.polygon([(32, 8), (42, 28), (32, 33)], fill=(205, 65, 215, 255))
    # Mid-Left
    d.polygon([(22, 28), (26, 44), (32, 33)], fill=(85, 22, 115, 255))
    # Mid-Right
    d.polygon([(42, 28), (38, 44), (32, 33)], fill=(170, 48, 195, 255))
    # Bottom-Left
    d.polygon([(26, 44), (32, 54), (32, 33)], fill=(65, 16, 95, 255))
    # Bottom-Right
    d.polygon([(38, 44), (32, 54), (32, 33)], fill=(115, 32, 150, 255))

    # Facet specular ridges
    ridge_color = (245, 140, 255, 255)
    d.line([(32, 8), (32, 33)], fill=ridge_color)
    d.line([(32, 33), (32, 54)], fill=(190, 85, 220, 255))
    d.line([(32, 33), (22, 28)], fill=ridge_color)
    d.line([(32, 33), (42, 28)], fill=(255, 190, 255, 255))
    d.line([(32, 33), (26, 44)], fill=(170, 65, 200, 255))
    d.line([(32, 33), (38, 44)], fill=(220, 110, 240, 255))

    # Outer crisp dark silhouette outline
    d.polygon([(32, 8), (42, 28), (38, 44), (32, 54), (26, 44), (22, 28)], outline=(36, 10, 50, 255))

    # Shimmer / Glint / Data Lattice Animation
    if frame_idx == 0:
        d.ellipse([29, 37, 35, 43], fill=(60, 220, 255, 110))
        d.ellipse([30, 38, 34, 42], fill=(80, 230, 255, 200))
        d.point((32, 40), fill=(255, 255, 255, 255))
        d.point((23, 20), fill=(245, 200, 255, 255))
    elif frame_idx == 1:
        d.line([(24, 25), (31, 15)], fill=(255, 195, 255, 255), width=2)
        d.line([(28, 32), (36, 32)], fill=(80, 240, 255, 210), width=1)
        d.ellipse([29, 23, 35, 29], fill=(80, 240, 255, 120))
        d.point((32, 26), fill=(255, 255, 255, 255))
    elif frame_idx == 2:
        # Peak star glint + radial aura
        d.ellipse([24, 0, 40, 16], fill=(120, 230, 255, 90))
        d.line([(32, 2), (32, 14)], fill=(255, 255, 255, 255), width=2)
        d.line([(26, 8), (38, 8)], fill=(255, 255, 255, 255), width=2)
        d.line([(30, 6), (34, 10)], fill=(210, 250, 255, 255))
        d.line([(34, 6), (30, 10)], fill=(210, 250, 255, 255))
        d.point((32, 8), fill=(255, 255, 255, 255))
        d.line([(32, 8), (42, 28)], fill=(255, 255, 255, 255))
    elif frame_idx == 3:
        d.line([(35, 18), (40, 25)], fill=(255, 210, 255, 255))
        particles = [(20, 22), (44, 34), (32, 48)]
        for px, py in particles:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(80, 230, 255, 100))
            d.point((px, py), fill=(255, 255, 255, 255))

    return im


# ---------------------------------------------------------------------------
# 5. HAZARD BARREL (hazard_barrel_0 .. 3)
# ---------------------------------------------------------------------------
def draw_hazard_barrel(frame_idx: int) -> Image.Image:
    im = create_base_canvas()
    d = ImageDraw.Draw(im)

    # 1. Soft ground contact shadow
    draw_contact_shadow(d, 32, 54, 18, 6)

    # 2. Main Barrel Body: yellow-ochre metal cylinder
    d.rectangle([18, 18, 46, 50], fill=(225, 155, 20, 255))
    for y in range(18, 51):
        d.line([(18, y), (21, y)], fill=(140, 85, 10, 255))
        d.line([(22, y), (25, y)], fill=(185, 120, 15, 255))
        d.line([(29, y), (35, y)], fill=(255, 200, 50, 255))
        d.line([(42, y), (46, y)], fill=(150, 95, 12, 255))

    # Top Rim Oval
    d.ellipse([18, 14, 46, 22], fill=(235, 170, 30, 255), outline=(125, 75, 10, 255))
    d.ellipse([21, 16, 43, 20], fill=(210, 145, 18, 255))

    # Bottom Rim Oval
    d.ellipse([18, 47, 46, 53], fill=(160, 100, 12, 255), outline=(105, 60, 8, 255))

    # Steel Hoops / Rings with top bevel and bottom shadow
    for ry in [28, 39]:
        d.line([(18, ry + 1), (46, ry + 1)], fill=(25, 30, 36, 255), width=1)
        d.line([(18, ry), (46, ry)], fill=(50, 56, 65, 255), width=2)
        d.line([(18, ry), (46, ry)], fill=(95, 105, 120, 255), width=1)
        d.line([(28, ry), (36, ry)], fill=(155, 170, 195, 255), width=1)

    # Radiation Hazard Trefoil Symbol
    cx, cy = 32, 34
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(20, 22, 26, 255))
    for i in range(3):
        ang = -math.pi / 2 + i * (2 * math.pi / 3)
        p1 = (cx + int(4 * math.cos(ang - 0.4)), cy + int(4 * math.sin(ang - 0.4)))
        p2 = (cx + int(7 * math.cos(ang - 0.3)), cy + int(7 * math.sin(ang - 0.3)))
        p3 = (cx + int(7 * math.cos(ang + 0.3)), cy + int(7 * math.sin(ang + 0.3)))
        p4 = (cx + int(4 * math.cos(ang + 0.4)), cy + int(4 * math.sin(ang + 0.4)))
        d.polygon([p1, p2, p3, p4], fill=(20, 22, 26, 255))

    # Strobe Warning Beacon
    d.rectangle([29, 13, 35, 16], fill=(50, 56, 66, 255), outline=(22, 25, 32, 255))

    if frame_idx == 0:
        d.rounded_rectangle([28, 8, 36, 13], radius=3, fill=(150, 25, 25, 255), outline=(75, 12, 12, 255))
        d.point((32, 10), fill=(215, 60, 60, 255))
    elif frame_idx == 1:
        d.ellipse([23, 3, 41, 18], fill=(255, 60, 40, 50))
        d.ellipse([25, 5, 39, 16], fill=(255, 60, 40, 90))
        d.rounded_rectangle([28, 8, 36, 13], radius=3, fill=(255, 75, 45, 255), outline=(160, 30, 20, 255))
        d.ellipse([30, 9, 34, 12], fill=(255, 210, 160, 255))
    elif frame_idx == 2:
        # Massive flash aura
        d.ellipse([18, -2, 46, 24], fill=(255, 50, 40, 60))
        d.ellipse([22, 2, 42, 20], fill=(255, 140, 80, 100))
        d.rounded_rectangle([28, 7, 36, 13], radius=3, fill=(255, 255, 255, 255), outline=(255, 130, 90, 255))
        d.line([(18, 14), (46, 14)], fill=(255, 245, 160, 255))
    elif frame_idx == 3:
        d.rounded_rectangle([28, 8, 36, 13], radius=3, fill=(160, 30, 30, 255), outline=(85, 15, 15, 255))
        d.point((32, 10), fill=(225, 75, 75, 255))
        # Toxic green ooze drip on bottom
        d.line([(24, 49), (24, 55)], fill=(50, 245, 65, 255), width=2)
        d.ellipse([21, 52, 27, 57], fill=(80, 255, 95, 255))
        d.ellipse([19, 54, 29, 58], fill=(40, 210, 55, 200))

    return im


# ---------------------------------------------------------------------------
# 6. HAZARD BATTERY (hazard_battery_0 .. 3)
# ---------------------------------------------------------------------------
def draw_hazard_battery(frame_idx: int) -> Image.Image:
    im = create_base_canvas()
    d = ImageDraw.Draw(im)

    # 1. Soft ground contact shadow
    draw_contact_shadow(d, 32, 54, 17, 5)

    # 2. Terminal poles
    d.rectangle([23, 9, 27, 13], fill=(175, 180, 190, 255), outline=(65, 70, 80, 255))
    d.line([(23, 11), (27, 11)], fill=(240, 40, 40, 255))
    d.rectangle([37, 9, 41, 13], fill=(175, 180, 190, 255), outline=(65, 70, 80, 255))
    d.line([(37, 11), (41, 11)], fill=(20, 22, 28, 255))

    # Top Armored Cap
    d.rounded_rectangle([19, 13, 45, 21], radius=2, fill=(48, 55, 68, 255), outline=(20, 24, 32, 255))
    d.line([(20, 14), (44, 14)], fill=(90, 105, 130, 255))

    # Bottom Armored Cap with Hazard Stripes
    d.rounded_rectangle([19, 43, 45, 52], radius=2, fill=(230, 180, 25, 255), outline=(20, 24, 32, 255))
    d.line([(22, 52), (28, 43)], fill=(22, 25, 32, 255), width=2)
    d.line([(31, 52), (37, 43)], fill=(22, 25, 32, 255), width=2)
    d.line([(40, 52), (45, 45)], fill=(22, 25, 32, 255), width=2)

    # Glass Chamber in Center
    d.rectangle([21, 21, 43, 43], fill=(10, 42, 20, 255), outline=(18, 22, 30, 255))
    d.rectangle([22, 26, 42, 42], fill=(42, 210, 65, 255))
    d.line([(22, 26), (42, 26)], fill=(130, 255, 150, 255))

    d.line([(20, 21), (20, 43)], fill=(80, 95, 115, 255), width=2)
    d.line([(44, 21), (44, 43)], fill=(80, 95, 115, 255), width=2)
    d.line([(23, 22), (23, 42)], fill=(255, 255, 255, 100))

    d.line([(31, 30), (33, 34), (30, 34), (32, 38)], fill=(12, 55, 22, 230), width=1)

    if frame_idx == 0:
        d.ellipse([27, 37, 31, 41], fill=(110, 255, 130, 255), outline=(18, 115, 38, 255))
        d.point((28, 38), fill=(255, 255, 255, 255))
        d.ellipse([33, 51, 36, 54], fill=(65, 245, 80, 255))
    elif frame_idx == 1:
        d.ellipse([28, 30, 32, 34], fill=(110, 255, 130, 255), outline=(18, 115, 38, 255))
        d.point((29, 31), fill=(255, 255, 255, 255))
        d.ellipse([34, 38, 36, 40], fill=(85, 235, 105, 230))
        d.line([(35, 51), (35, 56)], fill=(50, 235, 68, 255), width=2)
        d.ellipse([34, 54, 36, 57], fill=(85, 255, 95, 255))
    elif frame_idx == 2:
        d.point((29, 25), fill=(230, 255, 240, 255))
        d.ellipse([28, 24, 31, 27], outline=(160, 255, 180, 210))
        d.ellipse([34, 31, 37, 34], fill=(110, 255, 130, 255), outline=(18, 115, 38, 255))
        d.ellipse([34, 57, 36, 60], fill=(75, 255, 90, 255))
    elif frame_idx == 3:
        d.rectangle([22, 26, 42, 42], fill=(70, 245, 90, 255))
        d.line([(22, 26), (42, 26)], fill=(190, 255, 205, 255))
        d.ellipse([32, 59, 38, 62], fill=(55, 230, 70, 230))
        d.point((35, 60), fill=(190, 255, 205, 255))

    return im


# ---------------------------------------------------------------------------
# 7. HAZARD PLASMA (hazard_plasma_0 .. 3)
# ---------------------------------------------------------------------------
def draw_hazard_plasma(frame_idx: int) -> Image.Image:
    im = create_base_canvas()
    d = ImageDraw.Draw(im)

    # 1. Soft ground contact shadow
    draw_contact_shadow(d, 32, 54, 18, 5)

    # Top Manifold
    d.rounded_rectangle([18, 11, 46, 19], radius=3, fill=(42, 46, 58, 255), outline=(18, 20, 28, 255))
    d.line([(19, 12), (45, 12)], fill=(85, 95, 115, 255))
    d.polygon([(30, 19), (34, 19), (32, 23)], fill=(215, 190, 95, 255))

    # Bottom Manifold
    d.rounded_rectangle([18, 45, 46, 53], radius=3, fill=(42, 46, 58, 255), outline=(18, 20, 28, 255))
    d.line([(19, 46), (45, 46)], fill=(80, 90, 110, 255))
    d.polygon([(30, 45), (34, 45), (32, 41)], fill=(215, 190, 95, 255))

    # Glass Cylinder
    d.rectangle([21, 19, 43, 45], fill=(12, 10, 28, 255), outline=(20, 22, 34, 255))
    d.line([(22, 20), (22, 44)], fill=(255, 255, 255, 80))
    d.line([(23, 21), (23, 43)], fill=(190, 220, 255, 50))

    cx, cy = 32, 32

    if frame_idx == 0:
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(180, 40, 255, 60))
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(235, 75, 255, 255))
        d.point((cx, cy), fill=(255, 255, 255, 255))
        d.line([(cx, cy), (36, 27), (32, 22)], fill=(150, 230, 255, 255), width=2)
        d.line([(cx, cy), (36, 27), (32, 22)], fill=(255, 255, 255, 255), width=1)
    elif frame_idx == 1:
        d.ellipse([18, 24, 28, 36], fill=(220, 80, 255, 100))
        d.line([(32, 22), (25, 26), (22, 30)], fill=(210, 60, 255, 255), width=2)
        d.line([(22, 30), (28, 36), (32, 42)], fill=(130, 230, 255, 255), width=2)
        d.point((22, 30), fill=(255, 255, 255, 255))
        d.point((26, 25), fill=(255, 255, 255, 255))
        d.point((25, 34), fill=(170, 245, 255, 255))
    elif frame_idx == 2:
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(210, 60, 255, 80))
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 150, 255, 180))
        d.line([(32, 22), (27, 28), (37, 36), (32, 42)], fill=(255, 255, 255, 255), width=2)
        d.line([(32, 22), (37, 27), (26, 37), (32, 42)], fill=(170, 245, 255, 255), width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255, 255))
    elif frame_idx == 3:
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=(170, 60, 255, 180), width=2)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(230, 90, 255, 255))
        d.point((cx, cy), fill=(255, 255, 255, 255))
        d.line([(cx, cy - 4), (cx + 5, cy - 8)], fill=(130, 235, 255, 220))
        d.line([(cx, cy + 4), (cx - 5, cy + 8)], fill=(130, 235, 255, 220))

    return im


# ---------------------------------------------------------------------------
# 8. TRASH BIN (trash_bin_0 .. 3)
# ---------------------------------------------------------------------------
def draw_trash_bin(frame_idx: int) -> Image.Image:
    im = create_base_canvas()
    d = ImageDraw.Draw(im)

    # 1. Soft ground contact shadow
    draw_contact_shadow(d, 32, 55, 20, 6)

    # 2. Outer Bin Housing
    bin_poly = [
        (20, 15), (43, 15), (47, 19), (47, 49),
        (43, 53), (20, 53), (16, 49), (16, 19)
    ]
    d.polygon(bin_poly, fill=(40, 48, 62, 255), outline=(16, 20, 26, 255))

    # Top Hood Bevel / Trim
    d.line([(20, 16), (43, 16)], fill=(80, 95, 120, 255))
    d.line([(17, 19), (20, 16)], fill=(70, 85, 110, 255))

    # Recessed Intake Hatch Door
    d.rectangle([21, 21, 37, 33], fill=(14, 18, 24, 255), outline=(24, 30, 40, 255))

    cx, cy = 29, 27
    recy_colors = [
        (40, 185, 205),
        (65, 235, 255),
        (230, 255, 255),
        (65, 235, 255),
    ]
    r_col = recy_colors[frame_idx]
    d.line([(cx, cy - 4), (cx + 4, cy + 3)], fill=r_col, width=1)
    d.line([(cx + 4, cy + 3), (cx - 4, cy + 3)], fill=r_col, width=1)
    d.line([(cx - 4, cy + 3), (cx, cy - 4)], fill=r_col, width=1)
    d.point((cx, cy - 4), fill=(255, 255, 255, 255))

    # Segmented status LED bar
    segments = [(22, 24), (25, 27), (28, 30), (31, 33)]
    for seg_idx, (y1, y2) in enumerate(reversed(segments)):
        is_lit = seg_idx <= frame_idx
        if is_lit:
            col = (50, 245, 145) if seg_idx == 0 else ((65, 225, 255) if seg_idx < 3 else (255, 215, 45))
            d.rectangle([41, y1, 43, y2], fill=col)
            d.point((42, y1), fill=(255, 255, 255, 255))
        else:
            d.rectangle([41, y1, 43, y2], fill=(20, 25, 34, 255))

    # Vent Grille
    d.rectangle([21, 39, 37, 47], fill=(20, 24, 32, 255), outline=(12, 16, 22, 255))
    for vy in [41, 43, 45]:
        d.line([(23, vy), (35, vy)], fill=(10, 12, 18, 255))
        d.line([(23, vy + 1), (35, vy + 1)], fill=(55, 65, 80, 255))

    # Bottom Neon Glow Trim
    neon_base_glow = [
        (30, 140, 160),
        (55, 215, 235),
        (95, 255, 255),
        (55, 215, 235),
    ][frame_idx]
    d.line([(20, 50), (43, 50)], fill=neon_base_glow, width=1)

    if frame_idx == 1:
        d.rectangle([20, 20, 38, 34], outline=(55, 225, 255, 130))
    elif frame_idx == 2:
        d.rectangle([22, 22, 36, 32], fill=(45, 185, 225, 160))
        d.point((cx, cy), fill=(255, 255, 255, 255))
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=(110, 245, 255, 150))
    elif frame_idx == 3:
        d.ellipse([12, 42, 15, 45], fill=(160, 195, 215, 170))
        d.ellipse([48, 42, 51, 45], fill=(160, 195, 215, 170))

    return im


# ---------------------------------------------------------------------------
# 9. TRASH BASKET (trash_basket_0 .. 3)
# ---------------------------------------------------------------------------
def draw_trash_basket(frame_idx: int) -> Image.Image:
    im = create_base_canvas()
    d = ImageDraw.Draw(im)

    # 1. Soft ground contact shadow
    draw_contact_shadow(d, 32, 55, 19, 6)

    # 2. Inner dark cavity behind mesh
    cavity_poly = [(18, 18), (46, 18), (42, 50), (22, 50)]
    d.polygon(cavity_poly, fill=(14, 18, 26, 255))

    # Scrap pieces visible inside:
    # Circuit board fragment
    pcb_inside = [(23, 29), (29, 27), (31, 41), (25, 43)]
    d.polygon(pcb_inside, fill=(20, 85, 55, 240), outline=(10, 45, 30, 255))
    trace_col = (255, 235, 90, 255) if frame_idx == 1 else (190, 150, 60, 240)
    d.line([(24, 33), (29, 31), (28, 38)], fill=trace_col, width=1)

    # Microchip fragment
    d.rectangle([33, 32, 40, 38], fill=(35, 42, 54, 255), outline=(18, 22, 30, 255))
    chip_led_col = [
        (255, 140, 30),
        (50, 240, 255),
        (255, 255, 255),
        (220, 100, 20),
    ][frame_idx]
    d.point((35, 34), fill=chip_led_col)

    # Copper coil wire
    d.arc([25, 41, 35, 47], start=0, end=180, fill=(215, 130, 50, 255), width=2)

    # Wireframe Mesh Grid
    mesh_color = (55, 68, 85, 210)
    for x0 in range(12, 52, 6):
        d.line([(x0, 20), (x0 + 12, 50)], fill=mesh_color, width=1)
    for x0 in range(20, 60, 6):
        d.line([(x0, 20), (x0 - 12, 50)], fill=mesh_color, width=1)

    # Heavy Vertical Reinforcement Struts
    struts = [
        [(18, 19), (22, 50)],
        [(25, 20), (27, 50)],
        [(32, 21), (32, 50)],
        [(39, 20), (37, 50)],
        [(46, 19), (42, 50)],
    ]
    for s in struts:
        d.line(s, fill=(32, 38, 50, 255), width=2)
        d.line(s, fill=(80, 95, 118, 255), width=1)

    # Horizontal reinforcement hoops
    d.ellipse([19, 31, 45, 36], outline=(28, 34, 46, 255), width=2)
    d.arc([20, 31, 44, 36], start=0, end=180, fill=(95, 110, 135, 255), width=1)
    d.ellipse([21, 41, 43, 46], outline=(28, 34, 46, 255), width=2)
    d.arc([21, 41, 43, 46], start=0, end=180, fill=(85, 100, 125, 255), width=1)

    # Bottom Pedestal Base
    d.ellipse([20, 48, 44, 54], fill=(36, 44, 56, 255), outline=(16, 20, 28, 255))
    d.arc([21, 49, 43, 53], start=0, end=180, fill=(80, 95, 120, 255), width=1)

    # Top Reinforced Collar / Rim
    d.ellipse([16, 13, 48, 22], fill=(46, 55, 70, 255), outline=(18, 22, 30, 255))
    d.ellipse([18, 14, 46, 21], fill=(60, 72, 90, 255))
    d.ellipse([19, 15, 45, 20], fill=(16, 20, 28, 255))

    # Top Neon Glowing Rim Ring
    neon_rim_colors = [
        (45, 195, 225),
        (75, 245, 255),
        (255, 255, 255),
        (55, 215, 235),
    ]
    rim_col = neon_rim_colors[frame_idx]
    d.ellipse([17, 13, 47, 21], outline=rim_col, width=1)

    # Handles on left & right rim
    d.rectangle([14, 16, 16, 20], fill=(62, 75, 94, 255), outline=(18, 22, 30, 255))
    d.rectangle([48, 16, 50, 20], fill=(62, 75, 94, 255), outline=(18, 22, 30, 255))

    if frame_idx == 1:
        d.ellipse([15, 11, 49, 23], outline=(65, 235, 255, 120), width=1)
        d.point((28, 14), fill=(255, 255, 255, 255))
        d.point((36, 14), fill=(255, 255, 255, 255))
        d.ellipse([31, 8, 33, 10], fill=(85, 245, 255, 230))
        d.point((32, 9), fill=(255, 255, 255, 255))
    elif frame_idx == 2:
        d.line([(28, 34), (32, 31), (34, 35)], fill=(255, 255, 255, 255), width=2)
        d.line([(28, 34), (32, 31), (34, 35)], fill=(150, 235, 255, 255), width=1)
        d.point((20, 17), fill=(255, 255, 255, 255))
        d.point((44, 17), fill=(255, 255, 255, 255))
        d.ellipse([29, 28, 35, 34], fill=(130, 225, 255, 140))
    elif frame_idx == 3:
        d.ellipse([26, 9, 29, 12], fill=(145, 225, 245, 170))
        d.point((27, 10), fill=(225, 255, 255, 230))
        d.ellipse([35, 7, 37, 9], fill=(145, 225, 245, 150))

    return im


# ---------------------------------------------------------------------------
# ATLAS BUILDER & EXPORTER
# ---------------------------------------------------------------------------
SPRITE_SPECS = [
    ("scrap_chip", draw_scrap_chip),
    ("scrap_board", draw_scrap_board),
    ("scrap_core", draw_scrap_core),
    ("scrap_crystal", draw_scrap_crystal),
    ("hazard_barrel", draw_hazard_barrel),
    ("hazard_battery", draw_hazard_battery),
    ("hazard_plasma", draw_hazard_plasma),
    ("trash_bin", draw_trash_bin),
    ("trash_basket", draw_trash_basket),
]


def generate_all():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    INDIVIDUAL_DIR.mkdir(parents=True, exist_ok=True)

    num_rows = len(SPRITE_SPECS)  # 9
    num_cols = 4                  # 4 frames each
    atlas_w = num_cols * FRAME_SIZE  # 256
    atlas_h = num_rows * FRAME_SIZE  # 576

    atlas_img = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<TextureAtlas imagePath="trash.png">',
    ]

    print(f"Generating {num_rows * num_cols} frames ({atlas_w}x{atlas_h} atlas)...")

    for row_idx, (prefix, gen_func) in enumerate(SPRITE_SPECS):
        y = row_idx * FRAME_SIZE
        for frame_idx in range(num_cols):
            x = frame_idx * FRAME_SIZE
            frame_name = f"{prefix}_{frame_idx}"
            frame_img = gen_func(frame_idx)

            atlas_img.paste(frame_img, (x, y))

            indiv_path = INDIVIDUAL_DIR / f"{frame_name}.png"
            frame_img.save(indiv_path)

            xml_lines.append(
                f'    <SubTexture name="{frame_name}" x="{x}" y="{y}" width="{FRAME_SIZE}" height="{FRAME_SIZE}" />'
            )

            if prefix == "trash_basket":
                alt_name = f"basket_{frame_idx}"
                xml_lines.append(
                    f'    <SubTexture name="{alt_name}" x="{x}" y="{y}" width="{FRAME_SIZE}" height="{FRAME_SIZE}" />'
                )
                alt_path = INDIVIDUAL_DIR / f"{alt_name}.png"
                frame_img.save(alt_path)

    xml_lines.append("</TextureAtlas>")
    xml_content = "\n".join(xml_lines) + "\n"

    atlas_path = ASSETS_DIR / "trash.png"
    atlas_img.save(atlas_path, "PNG")
    print(f"Saved atlas texture: {atlas_path} ({atlas_path.stat().st_size} bytes)")

    xml_path = ASSETS_DIR / "trash.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"Saved atlas XML: {xml_path}")

    # Generate labeled preview
    preview_w = atlas_w + 140
    preview_h = atlas_h + 30
    preview_img = Image.new("RGBA", (preview_w, preview_h), (20, 24, 32, 255))
    pdraw = ImageDraw.Draw(preview_img)

    for py in range(0, preview_h, 16):
        pdraw.line([(0, py), (preview_w, py)], fill=(28, 34, 46, 255))
    for px in range(0, preview_w, 16):
        pdraw.line([(px, 0), (px, preview_h)], fill=(28, 34, 46, 255))

    offset_x = 130
    offset_y = 15
    preview_img.paste(atlas_img, (offset_x, offset_y), atlas_img)

    for row_idx, (prefix, _) in enumerate(SPRITE_SPECS):
        ry = offset_y + row_idx * FRAME_SIZE + 24
        pdraw.text((10, ry), prefix, fill=(200, 220, 255, 255))

    preview_path = ASSETS_DIR / "preview.png"
    preview_img.save(preview_path, "PNG")
    print(f"Saved preview sheet: {preview_path}")

    print("All trash assets generated successfully with enhanced shadows and glows!")


if __name__ == "__main__":
    generate_all()
