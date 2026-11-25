"""News poster for Wednesday 25 November 2026.

Pure-stdlib Python: draws a 1024x1024 broadsheet poster with its own
5x7 bitmap font, its own shape rasteriser and its own PNG writer.
No network, no randomness, no time input: two runs write identical bytes.

Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (244, 239, 228)
INK = (20, 20, 20)
NAVY = (16, 38, 79)
NAVY_DARK = (10, 26, 56)
GOLD = (199, 154, 46)
RED = (179, 35, 27)
TEAL = (15, 107, 110)
TEAL_DARK = (11, 74, 84)
SKY = (184, 201, 217)
SKY_LIGHT = (214, 226, 235)
SEA = (22, 107, 122)
WHITE = (255, 255, 255)
GREY = (107, 111, 117)
GREY_LIGHT = (169, 175, 182)
HULL = (43, 47, 54)
DECK = (223, 227, 230)
FLAME = (232, 122, 26)
FLAME_Y = (245, 196, 66)
CREAM = (250, 246, 236)
PANEL = (255, 255, 255)

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = c[0]
        px[i + 1] = c[1]
        px[i + 2] = c[2]


def fill(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i] = c[0]
            px[i + 1] = c[1]
            px[i + 2] = c[2]


def frame(x, y, w, h, c, t=2):
    fill(x, y, w, t, c)
    fill(x, y + h - t, w, t, c)
    fill(x, y, t, h, c)
    fill(x + w - t, y, t, h, c)


def hline(x, y, w, c, t=1):
    fill(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    fill(x, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        fill(x0 - t // 2, y0 - t // 2, t, t, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def dashline(x0, y0, x1, y1, c, dash=7, gap=5):
    length = math.hypot(x1 - x0, y1 - y0)
    if length == 0:
        return
    ux = (x1 - x0) / length
    uy = (y1 - y0) / length
    d = 0.0
    while d < length:
        ex = x0 + ux * min(d + dash, length)
        ey = y0 + uy * min(d + dash, length)
        line(int(x0 + ux * d), int(y0 + uy * d), int(ex), int(ey), c, 2)
        d += dash + gap


def disc(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        fill(cx - dx, cy + dy, 2 * dx + 1, 1, c)


def ring(cx, cy, r, c, t=3):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        for xx in (cx - dx, cx + dx):
            fill(xx - t // 2, cy + dy, t, 1, c)
    for dx in range(-r, r + 1):
        dy = int(math.sqrt(max(0, r * r - dx * dx)))
        for yy in (cy - dy, cy + dy):
            fill(cx + dx, yy - t // 2, 1, t, c)


def ellipse(cx, cy, rx, ry, c):
    for dy in range(-ry, ry + 1):
        t = 1.0 - (dy * dy) / float(ry * ry)
        dx = int(rx * math.sqrt(max(0.0, t)))
        fill(cx - dx, cy + dy, 2 * dx + 1, 1, c)


def tri(p1, p2, p3, c):
    xs = [p1[0], p2[0], p3[0]]
    ys = [p1[1], p2[1], p3[1]]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)

    def edge(a, b, p):
        return (p[0] - a[0]) * (b[1] - a[1]) - (p[1] - a[1]) * (b[0] - a[0])

    d = edge(p1, p2, p3)
    if d == 0:
        return
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            w1 = edge(p2, p3, (xx, yy))
            w2 = edge(p3, p1, (xx, yy))
            w3 = edge(p1, p2, (xx, yy))
            if (d > 0 and w1 >= 0 and w2 >= 0 and w3 >= 0) or (
                d < 0 and w1 <= 0 and w2 <= 0 and w3 <= 0
            ):
                put(xx, yy, c)


def quad(p1, p2, p3, p4, c):
    tri(p1, p2, p3, c)
    tri(p1, p3, p4, c)


# ---------------------------------------------------------------- 5x7 font
GLYPHS = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", "     ", "  #  "),
    ",": ("     ", "     ", "     ", "     ", "     ", "  #  ", " #   "),
    ":": ("     ", "  #  ", "     ", "     ", "     ", "  #  ", "     "),
    ";": ("     ", "  #  ", "     ", "     ", "     ", "  #  ", " #   "),
    "'": ("  #  ", "  #  ", "     ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "&": (" ##  ", "#  # ", "# #  ", " #   ", "# # #", "#  # ", " ## #"),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "+": ("     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", " ### ", "     ", " ### ", "     ", "     "),
    "*": ("     ", " # # ", "  #  ", " ### ", "  #  ", " # # ", "     "),
}

CW = 6  # advance per character at scale 1


def text_w(s, scale):
    return len(s) * CW * scale


def draw_text(x, y, s, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        g = GLYPHS.get(ch, GLYPHS[" "])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == "#":
                    fill(cx + col * scale, y + row * scale, scale, scale, color)
        cx += CW * scale
    return cx


def text_centre(cx, y, s, scale, color):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_w, scale):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, max_w, scale, color, gap=None):
    if gap is None:
        gap = 9 * scale
    for ln in wrap(s, max_w, scale):
        draw_text(x, y, ln, scale, color)
        y += 7 * scale + gap
    return y


def kicker(x, y, s, scale=2, color=RED):
    fill(x, y - 4, 26, 4, color)
    draw_text(x + 34, y - 8, s, scale, color)
    return y + 7 * scale + 8


# ---------------------------------------------------------------- scenes
def draw_ship_scene(x, y, w, h):
    # sky and sea
    fill(x, y, w, h, SKY)
    sea_y = y + int(h * 0.62)
    fill(x, sea_y, w, h - int(h * 0.62), SEA)
    fill(x, sea_y, w, 3, WHITE)
    # gulls
    line(x + 30, y + 26, x + 44, y + 20, INK, 2)
    line(x + 44, y + 20, x + 58, y + 26, INK, 2)
    line(x + 90, y + 44, x + 102, y + 39, INK, 2)
    line(x + 102, y + 39, x + 114, y + 44, INK, 2)
    # drone top right with dashed spotting line
    dx, dy = x + w - 70, y + 34
    fill(dx - 16, dy - 5, 32, 10, INK)
    fill(dx - 26, dy - 12, 20, 4, GREY)
    fill(dx + 6, dy - 12, 20, 4, GREY)
    fill(dx - 26, dy + 8, 20, 4, GREY)
    fill(dx + 6, dy + 8, 20, 4, GREY)
    disc(dx - 18, dy - 14, 7, INK)
    disc(dx + 18, dy - 14, 7, INK)
    disc(dx - 18, dy + 14, 7, INK)
    disc(dx + 18, dy + 14, 7, INK)
    disc(dx, dy, 4, RED)
    dashline(dx, dy + 16, x + 130, sea_y - 30, GREY, 6, 5)
    # smoke columns
    for sx, sy, r in ((x + 120, sea_y - 66, 16), (x + 132, sea_y - 92, 13),
                      (x + 116, sea_y - 116, 10), (x + 330, sea_y - 58, 14),
                      (x + 342, sea_y - 82, 11)):
        disc(sx, sy, r, GREY)
        disc(sx - 3, sy - 3, max(3, r - 6), GREY_LIGHT)
    # flames on deck
    tri((x + 96, sea_y - 6), (x + 118, sea_y - 58), (x + 140, sea_y - 6), FLAME)
    tri((x + 108, sea_y - 6), (x + 120, sea_y - 40), (x + 132, sea_y - 6), FLAME_Y)
    tri((x + 306, sea_y - 6), (x + 326, sea_y - 48), (x + 346, sea_y - 6), FLAME)
    tri((x + 316, sea_y - 6), (x + 326, sea_y - 32), (x + 336, sea_y - 6), FLAME_Y)
    # hull
    quad((x + 40, sea_y - 4), (x + w - 30, sea_y - 4),
         (x + w - 62, sea_y + 34), (x + 72, sea_y + 34), HULL)
    fill(x + 40, sea_y - 4, w - 70, 4, RED)
    # superstructure
    fill(x + 190, sea_y - 34, 96, 30, DECK)
    fill(x + 190, sea_y - 34, 96, 4, NAVY)
    for wx in range(x + 200, x + 276, 16):
        fill(wx, sea_y - 26, 9, 9, NAVY)
    # funnel
    fill(x + 300, sea_y - 52, 22, 20, HULL)
    fill(x + 300, sea_y - 52, 22, 6, RED)
    # waves
    for wx in range(x + 16, x + w - 20, 46):
        line(wx, sea_y + 52, wx + 22, sea_y + 52, WHITE, 2)
    for wx in range(x + 38, x + w - 20, 52):
        line(wx, sea_y + 72, wx + 20, sea_y + 72, (190, 220, 228), 2)


def draw_awacs(x, y, w, h):
    fill(x, y, w, h, SKY_LIGHT)
    # clouds
    for cx, cy, r in ((x + 60, y + 26, 16), (x + 84, y + 30, 12),
                      (x + w - 90, y + 20, 14), (x + w - 66, y + 26, 10)):
        disc(cx, cy, r, WHITE)
    # contrail
    dashline(x + 8, y + h - 26, x + w // 3, y + h // 2 + 8, WHITE, 8, 6)
    # fuselage
    cy = y + h // 2 + 6
    ellipse(x + w // 2, cy, 150, 17, WHITE)
    frame(x + w // 2 - 150, cy - 17, 300, 34, NAVY, 2)
    # nose
    tri((x + w // 2 + 148, cy - 12), (x + w // 2 + 186, cy), (x + w // 2 + 148, cy + 12), WHITE)
    # tail fin
    tri((x + w // 2 - 148, cy - 8), (x + w // 2 - 122, cy - 8), (x + w // 2 - 146, cy - 40), NAVY)
    # radar dome on top
    disc(x + w // 2 - 8, cy - 26, 18, NAVY)
    fill(x + w // 2 - 13, cy - 12, 10, 12, NAVY)
    # swept wing below the fuselage
    tri((x + w // 2 - 20, cy + 10), (x + w // 2 + 58, cy + 10), (x + w // 2 + 26, cy + 50), NAVY)
    # small tailplane
    tri((x + w // 2 - 118, cy + 8), (x + w // 2 - 78, cy + 8), (x + w // 2 - 100, cy + 30), NAVY)
    # windows
    for wx in range(x + w // 2 + 60, x + w // 2 + 140, 16):
        fill(wx, cy - 6, 8, 6, NAVY)
    # engines
    ellipse(x + w // 2 - 40, cy + 22, 16, 7, GREY)
    ellipse(x + w // 2 + 50, cy + 22, 16, 7, GREY)


def draw_tankers(x, y, w, h):
    fill(x, y, w, h, SKY)
    sea_y = y + int(h * 0.58)
    fill(x, sea_y, w, h - int(h * 0.58), SEA)
    fill(x, sea_y, w, 3, WHITE)
    # distant tanker
    quad((x + 30, sea_y - 2), (x + 150, sea_y - 2),
         (x + 138, sea_y + 20), (x + 42, sea_y + 20), HULL)
    fill(x + 62, sea_y - 18, 34, 16, DECK)
    # middle tanker, hit: flames + smoke
    disc(x + 240, sea_y - 56, 15, GREY)
    disc(x + 252, sea_y - 80, 11, GREY_LIGHT)
    tri((x + 218, sea_y - 4), (x + 238, sea_y - 52), (x + 258, sea_y - 4), FLAME)
    tri((x + 228, sea_y - 4), (x + 238, sea_y - 34), (x + 248, sea_y - 4), FLAME_Y)
    quad((x + 180, sea_y - 4), (x + 330, sea_y - 4),
         (x + 316, sea_y + 26), (x + 194, sea_y + 26), HULL)
    fill(x + 180, sea_y - 4, 150, 4, RED)
    fill(x + 240, sea_y - 26, 44, 22, DECK)
    fill(x + 240, sea_y - 26, 44, 4, NAVY)
    # near tanker
    quad((x + 330, sea_y - 2), (x + w - 24, sea_y - 2),
         (x + w - 36, sea_y + 20), (x + 342, sea_y + 20), (90, 40, 44))
    fill(x + 360, sea_y - 16, 30, 14, DECK)
    # mine in the water
    disc(x + 120, sea_y + 42, 9, INK)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        line(x + 120 + int(9 * math.cos(a)), sea_y + 42 + int(9 * math.sin(a)),
             x + 120 + int(15 * math.cos(a)), sea_y + 42 + int(15 * math.sin(a)), INK, 2)
    # waves
    for wx in range(x + 12, x + w - 20, 48):
        line(wx, sea_y + 62, wx + 22, sea_y + 62, WHITE, 2)


def draw_medal(cx, cy):
    # ribbon
    tri((cx - 34, cy - 66), (cx - 6, cy - 66), (cx - 8, cy - 8), RED)
    tri((cx + 6, cy - 66), (cx + 34, cy - 66), (cx + 8, cy - 8), NAVY)
    fill(cx - 6, cy - 66, 12, 58, WHITE)
    # medal disc
    disc(cx, cy + 22, 46, GOLD)
    ring(cx, cy + 22, 46, (150, 110, 20), 3)
    ring(cx, cy + 22, 34, (150, 110, 20), 2)
    # star
    sx, sy = cx, cy + 22
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        r = 26 if i % 2 == 0 else 11
        pts.append((sx + int(r * math.cos(a)), sy + int(r * math.sin(a))))
    for i in range(10):
        tri((sx, sy), pts[i], pts[(i + 1) % 10], (150, 110, 20))


# ---------------------------------------------------------------- layout
def build():
    fill(0, 0, W, H, PAPER)

    # ---- masthead
    fill(0, 0, W, 112, NAVY)
    fill(0, 108, W, 4, GOLD)
    draw_text(28, 16, "THE WORLD IN ONE DAY", 2, GOLD)
    draw_text(28, 46, "WEDNESDAY 25 NOVEMBER 2026", 4, WHITE)
    draw_text(W - 28 - text_w("NEWS POSTER * NO. 25", 2), 16, "NEWS POSTER * NO. 25", 2, (170, 190, 215))

    # ---- hero: Gulf of Finland ship strike
    hx, hy, hw, hh = 24, 124, 976, 296
    fill(hx, hy, hw, hh, PANEL)
    frame(hx, hy, hw, hh, INK, 2)
    fill(hx, hy, 8, hh, RED)
    draw_ship_scene(hx + 24, hy + 16, 430, hh - 32)
    tx = hx + 478
    ty = kicker(tx, hy + 40, "GULF OF FINLAND")
    ty = para(tx, ty, "UKRAINE HITS A RUSSIAN SHIP", 470, 3, INK, gap=6)
    ty += 6
    ty = para(tx, ty, "Zelenskiy confirms the strike. Norway urges caution after the attack in northern waters.", 470, 2, (60, 60, 60), gap=4)
    draw_text(tx, hy + hh - 34, "TOP STORY", 2, RED)

    # ---- row 2: NATO jets / Hormuz tankers
    ry, rh = 436, 232
    for px0, pw in ((24, 476), (524, 476)):
        fill(px0, ry, pw, rh, PANEL)
        frame(px0, ry, pw, rh, INK, 2)
    # left: NATO
    draw_awacs(40, ry + 12, 444, 108)
    ty = kicker(40, ry + 140, "POLAND")
    ty = para(40, ty, "NATO SENDS EARLY-WARNING JETS", 444, 2, INK, gap=4)
    para(40, ty + 2, "Alliance jets patrol after Russian missiles landed in Poland.", 444, 1, (60, 60, 60), gap=3)
    # right: Hormuz
    draw_tankers(540, ry + 12, 444, 108)
    ty = kicker(540, ry + 140, "STRAIT OF HORMUZ")
    ty = para(540, ty, "THREE OIL TANKERS HIT BY MINES", 444, 2, INK, gap=4)
    para(540, ty + 2, "Blasts strike shipping in the world's busiest oil strait.", 444, 1, (60, 60, 60), gap=3)

    # ---- row 3: death toll / Medal of Freedom
    ry3, rh3 = 684, 172
    for px0, pw in ((24, 476), (524, 476)):
        fill(px0, ry3, pw, rh3, PANEL)
        frame(px0, ry3, pw, rh3, INK, 2)
    # left: 700,000
    ty = kicker(40, ry3 + 34, "THE WAR IN UKRAINE")
    draw_text(40, ty + 2, "700,000", 6, RED)
    ty = para(40, ty + 2 + 7 * 6 + 10, "RUSSIAN SOLDIERS KILLED", 444, 2, INK, gap=4)
    para(40, ty + 2, "A new analysis puts the Russian death toll at 700,000.", 444, 1, (60, 60, 60), gap=3)
    # right: medal
    draw_medal(606, ry3 + 78)
    ty = kicker(676, ry3 + 34, "WASHINGTON")
    ty = para(676, ty, "TRUMP AWARDS GIULIANI MEDAL OF FREEDOM", 308, 2, INK, gap=4)
    para(676, ty + 2, "Rudy Giuliani receives America's highest civilian honour.", 308, 1, (60, 60, 60), gap=3)

    # ---- footer: in brief
    fy = 872
    fill(0, fy, W, H - fy, NAVY_DARK)
    fill(0, fy, W, 4, GOLD)
    draw_text(28, fy + 18, "IN BRIEF", 2, GOLD)
    items = [
        "HUAWEI CONVICTED IN US TRIAL",
        "CIA AND ODNI HIT BY CYBER BREACH",
        "ENGLAND BEAT AUSTRALIA BY 8 WICKETS IN 2ND T20I",
        "BJP-AKALI DAL AGREE PUNJAB 2027 ALLIANCE",
    ]
    col_w = 244
    for i, item in enumerate(items):
        cx = 28 + i * col_w
        fill(cx, fy + 52, 10, 10, GOLD)
        para(cx + 18, fy + 50, item, col_w - 24, 1, WHITE, gap=3)
    draw_text(28, H - 26, "ALL STORIES FIRST REPORTED WEDNESDAY 25 NOVEMBER 2026", 1, (170, 190, 215))


# ---------------------------------------------------------------- png
def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += px[yy * W * 3:(yy + 1) * W * 3]
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    build()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    n = write_png(path)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
