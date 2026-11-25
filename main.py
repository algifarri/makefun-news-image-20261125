"""news-image-20261125: a broadsheet front page summing up Wednesday 25 Nov 2026.

Pure Python stdlib. Draws a 1024x1024 newspaper poster from scratch:
own 5x7 bitmap letterface, own rasteriser (rects, discs, triangles, lines)
and a hand-rolled PNG writer. No network, no clock, no randomness, so
every run writes the exact same bytes to /output/entry.png.

Stories (all first reported on Wednesday 25 November 2026):
  HERO  Zelenskiy confirms Ukraine hit a Russian ship in the Gulf of
        Finland; Norway, a staunch Kyiv ally, urges caution.
  NATO  NATO plans to deploy early-warning aircraft in Poland after
        Russian missiles landed in Polish territory.
  SEA   Iran says three oil tankers were hit by naval mines in the
        Strait of Hormuz; shipping on alert.
  TOLL  More than 700,000 Russian soldiers killed in the Ukraine war,
        a new analysis finds.
  MEDAL Trump awards Rudy Giuliani the Presidential Medal of Freedom.
  BRIEF Huawei convicted in a US criminal trial over its Iran business;
        CIA and ODNI hit by a cyber breach; England beat Australia by
        8 wickets in the 2nd T20I; BJP and Akali Dal agree an alliance
        for the 2027 Punjab elections.
"""

import os
import struct
import zlib
from math import sqrt

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (22, 22, 26)
NAVY = (18, 33, 61)
RED = (178, 34, 34)
GOLD = (198, 148, 52)
WHITE = (255, 255, 255)
GREY = (96, 96, 100)
SEA = (11, 42, 74)
SEA_LT = (24, 78, 122)
ORANGE = (232, 116, 24)
YELLOW = (244, 196, 48)
TEAL = (16, 120, 110)
SMOKE = (150, 150, 150)
DARK = (40, 44, 52)
SKY = (158, 196, 224)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "..#..", ".#...", "#..##", "#..##", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}
FONT["\u00b7"] = (".....", ".....", ".....", ".##..", ".##..", ".....", ".....")
FONT["\u2014"] = FONT["-"]
FONT["\u2013"] = FONT["-"]
FONT["\u2019"] = FONT["'"]
FONT["\u00d7"] = (".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", ".....")


def text_width(text, s):
    return len(text) * 6 * s - s


def wrap(text, s, maxw):
    words = text.split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_width(trial, s) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def border(self, x, y, w, h, c, t=3):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(sqrt(r * r - dy * dy))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=3):
        for dy in range(-r, r + 1):
            dx = int(sqrt(r * r - dy * dy))
            self.fill_rect(cx - dx, cy + dy, t, 1, c)
            self.fill_rect(cx + dx - t + 1, cy + dy, t, 1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        steps = max(dx, dy, 1)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            self.disc(x, y, max(1, t // 2), c)

    def triangle(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for y in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by):
                    xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.fill_rect(xa, y, xb - xa + 1, 1, c)

    def text(self, x, y, s, c, txt):
        cx = x
        for ch in txt.upper():
            g = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == "#":
                        self.fill_rect(cx + col * s, y + r * s, s, s, c)
            cx += 6 * s
        return cx

    def text_c(self, cx, y, s, c, txt):
        return self.text(cx - text_width(txt, s) // 2, y, s, c, txt)

    def block(self, x, y, s, c, txt, maxw, lead=None):
        lead = lead if lead is not None else 9 * s
        for ln in wrap(txt, s, maxw):
            self.text(x, y, s, c, ln)
            y += lead
        return y


# ---------------------------------------------------------------- pictures
def draw_ship(cv, x, y, w):
    # A cargo ship listing after a drone strike: hull, bridge, funnel,
    # flames amidships and smoke drifting up.
    cv.triangle([(x, y), (x + w, y), (x + w - 26, y + 34)], DARK)
    cv.fill_rect(x + 8, y, w - 34, 34, DARK)
    cv.fill_rect(x + 8, y, w - 34, 6, (70, 76, 88))
    cv.fill_rect(x + w // 2 - 10, y - 34, 70, 34, (88, 92, 100))
    cv.fill_rect(x + w // 2 + 66, y - 52, 14, 52, (60, 64, 72))
    cv.line(x + w // 2 - 30, y - 34, x + w // 2 - 30, y - 74,
            (200, 200, 200), 3)
    for (fx, fw, fh) in ((x + w // 2 - 46, 30, 46), (x + w // 2 - 8, 24, 62),
                         (x + w // 2 + 22, 26, 40)):
        cv.triangle([(fx, y), (fx + fw // 2, y - fh),
                     (fx + fw, y)], ORANGE)
        cv.triangle([(fx + 6, y), (fx + fw // 2, y - fh + 18),
                     (fx + fw - 6, y)], YELLOW)
    for (sx, sy, sr) in ((x + w // 2 - 20, y - 80, 14),
                         (x + w // 2 + 6, y - 105, 18),
                         (x + w // 2 + 30, y - 128, 20)):
        cv.disc(sx, sy, sr, SMOKE)


def draw_drone(cv, cx, cy, s):
    # small quad-rotor drone, seen from below
    cv.fill_rect(cx - 6 * s, cy - 2 * s, 12 * s, 4 * s, INK)
    cv.fill_rect(cx - 2 * s, cy - 6 * s, 4 * s, 12 * s, INK)
    for (ax, ay) in ((-9, -9), (9, -9), (-9, 9), (9, 9)):
        cv.disc(cx + ax * s, cy + ay * s, 3 * s, DARK)
        cv.fill_rect(cx + ax * s - 6 * s, cy + ay * s - 1, 12 * s, 2, GREY)


def draw_awacs(cv, x, y, w):
    # early-warning aircraft: fuselage, radar dome on a stalk, swept
    # wings and tail fin, flying left to right.
    h = 34
    cv.fill_rect(x + 20, y, w - 60, h, (226, 232, 238))
    cv.disc(x + 20, y + h // 2, h // 2, (226, 232, 238))
    cv.disc(x + w - 40, y + h // 2, h // 2, (226, 232, 238))
    cv.fill_rect(x + w - 96, y + 6, 46, 10, SKY)
    cv.fill_rect(x + w - 140, y + 6, 30, 10, SKY)
    # radar dome
    cv.fill_rect(x + w // 2 - 4, y - 26, 8, 26, (180, 186, 194))
    cv.disc(x + w // 2, y - 34, 30, (200, 206, 214))
    cv.disc(x + w // 2, y - 34, 30, (200, 206, 214))
    cv.ring(x + w // 2, y - 34, 30, (140, 146, 154), 3)
    # wings and tail
    cv.triangle([(x + w // 2 - 30, y + h), (x + w // 2 + 30, y + h),
                 (x + w // 2 + 70, y + h + 52)], (180, 186, 194))
    cv.triangle([(x + 10, y), (x + 40, y), (x + 16, y - 40)],
                (180, 186, 194))
    # engines
    cv.fill_rect(x + w // 2 - 50, y + h - 4, 26, 12, (120, 126, 134))
    cv.fill_rect(x + w // 2 + 30, y + h - 4, 26, 12, (120, 126, 134))


def draw_tanker(cv, x, y, w):
    # oil tanker with three deck tanks, a small fire on the middle one
    cv.triangle([(x, y), (x + w, y), (x + w - 22, y + 30)], (96, 30, 26))
    cv.fill_rect(x + 6, y, w - 28, 30, (140, 44, 36))
    cv.fill_rect(x + 6, y, w - 28, 5, (176, 62, 48))
    for i in range(3):
        tx = x + 24 + i * (w // 3)
        cv.fill_rect(tx, y - 30, 44, 30, (200, 205, 210))
        cv.border(tx, y - 30, 44, 30, (140, 146, 154), 2)
    fx = x + 24 + (w // 3) + 22
    cv.triangle([(fx - 14, y - 30), (fx, y - 62), (fx + 14, y - 30)],
                ORANGE)
    cv.triangle([(fx - 7, y - 30), (fx, y - 48), (fx + 7, y - 30)],
                YELLOW)
    cv.fill_rect(x + w - 34, y - 44, 16, 44, (70, 76, 88))


def draw_medal(cv, cx, y):
    # Presidential Medal of Freedom: red-white-blue ribbon, gold disc
    cv.triangle([(cx - 26, y), (cx + 26, y), (cx, y + 44)], RED)
    cv.triangle([(cx - 13, y), (cx + 13, y), (cx, y + 44)], WHITE)
    cv.triangle([(cx - 5, y), (cx + 5, y), (cx, y + 44)], (18, 33, 61))
    cv.disc(cx, y + 78, 36, GOLD)
    cv.ring(cx, y + 78, 36, (150, 108, 30), 3)
    cv.ring(cx, y + 78, 26, (150, 108, 30), 2)
    cv.text_c(cx, y + 66, 3, (120, 84, 20), "*")


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)

    # masthead
    cv.fill_rect(0, 0, W, 96, NAVY)
    cv.text_c(W // 2, 14, 5, WHITE, "THE WORLD IN ONE DAY")
    cv.text_c(W // 2, 64, 2, GOLD, "WEDNESDAY \u00b7 25 NOVEMBER 2026")
    cv.fill_rect(0, 96, W, 6, RED)

    # ---- hero: Gulf of Finland ship strike ------------------ x16 y112
    cv.fill_rect(16, 112, 616, 380, WHITE)
    cv.border(16, 112, 616, 380, INK, 3)
    cv.text(32, 128, 2, RED, "GULF OF FINLAND \u00b7 UKRAINE WAR")
    cv.block(32, 156, 3, INK, "ZELENSKYY CONFIRMS UKRAINE HIT RUSSIAN SHIP",
             584, lead=26)
    cv.block(32, 220, 2, GREY,
             "KYIV TAKES RESPONSIBILITY FOR SATURDAY DRONE STRIKE "
             "ON CARGO SHIP \u00b7 NORWAY URGES CAUTION", 584, lead=20)
    cv.fill_rect(32, 292, 584, 168, SEA)
    cv.text(48, 306, 2, WHITE, "GULF OF FINLAND")
    draw_drone(cv, 556, 330, 1)
    draw_ship(cv, 128, 408, 300)
    cv.fill_rect(32, 446, 584, 14, SEA_LT)
    cv.text(48, 468, 1, GREY, "SHIP TOWED FROM FINNISH WATERS AFTER STRIKE")

    # ---- NATO panel ----------------------------------------- x648 y112
    cv.fill_rect(648, 112, 360, 380, NAVY)
    cv.border(648, 112, 360, 380, INK, 3)
    cv.text(664, 128, 2, GOLD, "NATO \u00b7 POLAND")
    cv.block(664, 156, 3, WHITE, "NATO SENDS EARLY-WARNING JETS TO POLAND",
             328, lead=26)
    cv.block(664, 252, 2, GOLD, "AFTER RUSSIAN MISSILES LAND IN POLAND",
             328, lead=20)
    cv.fill_rect(664, 306, 328, 138, (28, 52, 92))
    draw_awacs(cv, 682, 356, 292)
    cv.text(664, 466, 1, WHITE, "RUTTE: EVERY INCH DEFENDED")

    # ---- row B: three panels -------------------------------- y508 h284
    # Hormuz tanker
    cv.fill_rect(16, 508, 320, 284, WHITE)
    cv.border(16, 508, 320, 284, INK, 3)
    cv.text(32, 524, 2, RED, "STRAIT OF HORMUZ")
    cv.block(32, 550, 3, INK, "THREE OIL TANKERS HIT BY MINES", 288, lead=26)
    cv.block(32, 636, 2, GREY, "IRAN BLAMES NAVAL MINES \u00b7 SHIPPING ON ALERT",
             288, lead=20)
    draw_tanker(cv, 56, 736, 240)

    # 700,000 toll
    cv.fill_rect(352, 508, 320, 284, DARK)
    cv.border(352, 508, 320, 284, INK, 3)
    cv.text(368, 524, 2, GOLD, "UKRAINE WAR \u00b7 THE TOLL")
    cv.text_c(512, 556, 6, WHITE, "700,000")
    cv.block(368, 620, 3, WHITE, "RUSSIAN SOLDIERS KILLED, STUDY FINDS",
             288, lead=26)
    cv.block(368, 706, 2, GOLD, "NEARLY FIVE YEARS OF WAR \u00b7 NEW ANALYSIS",
             288, lead=20)

    # Giuliani medal
    cv.fill_rect(688, 508, 320, 284, WHITE)
    cv.border(688, 508, 320, 284, INK, 3)
    cv.text(704, 524, 2, RED, "WASHINGTON")
    cv.block(704, 550, 3, INK, "TRUMP AWARDS GIULIANI MEDAL OF FREEDOM",
             288, lead=26)
    cv.block(704, 636, 2, GREY, "HIGHEST CIVILIAN HONOUR \u00b7 FORMER NYC MAYOR",
             288, lead=20)
    draw_medal(cv, 848, 676)

    # ---- in brief strip ------------------------------------- y808
    cv.fill_rect(16, 808, 992, 168, NAVY)
    cv.border(16, 808, 992, 168, INK, 3)
    cv.text(32, 822, 2, GOLD, "IN BRIEF")
    briefs = [
        (32, 852, "HUAWEI CONVICTED IN US TRIAL OVER IRAN BUSINESS"),
        (520, 852, "CIA AND ODNI HIT BY CYBER BREACH, SOURCE SAYS"),
        (32, 916, "ENGLAND BEAT AUSTRALIA BY 8 WICKETS IN 2ND T20I"),
        (520, 916, "BJP AND AKALI DAL AGREE ALLIANCE FOR PUNJAB 2027"),
    ]
    for (bx, by, txt) in briefs:
        cv.text(bx, by, 2, GOLD, "\u00b7")
        cv.block(bx + 20, by, 2, WHITE, txt, 440, lead=20)

    cv.text_c(W // 2, 988, 1, GREY,
              "DRAWN FROM REPORTS OF WEDNESDAY 25 NOVEMBER 2026")
    return cv


def png_bytes(cv):
    raw = b"".join(b"\x00" + bytes(cv.px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
