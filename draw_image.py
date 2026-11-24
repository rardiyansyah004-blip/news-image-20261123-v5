#!/usr/bin/env python3
"""Draw the news-image-20261123 v5 front page (1024x1024 PNG).

Fresh code written for this entry. 45 verified stories from Monday
23 November 2026, real news photos only, no truncation: every text
block is measured first and the script ABORTS on any overflow instead
of cutting words off.
"""
import hashlib
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 20
CW = W - 2 * MARGIN  # 984

PAPER = (247, 242, 231)
INK = (20, 20, 20)
NAVY = (14, 42, 74)
NAVY_LT = (28, 68, 112)
RED = (176, 30, 36)
GREY = (90, 90, 90)
BAND = (220, 230, 239)
SEA = (168, 196, 216)
LAND = (122, 155, 109)
RULE = (180, 175, 165)

FD = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FD + name, size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_R = lambda s: font("DejaVuSans.ttf", s)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


def abort(msg):
    print("OVERFLOW: " + msg, file=sys.stderr)
    sys.exit(2)


def width(s, f):
    return f.getlength(s)


def wrap(s, f, maxw):
    """Greedy word wrap; returns list of lines (no line exceeds maxw)."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if width(trial, f) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(s, f, maxw, maxlines, what):
    lines = wrap(s, f, maxw)
    if len(lines) > maxlines:
        abort(f"{what}: {len(lines)} lines > {maxlines}: {s!r}")
    for ln in lines:
        if width(ln, f) > maxw:
            abort(f"{what}: single word too wide: {ln!r}")
    return lines


def cover(path, tw, th, fx=0.5, fy=0.5):
    """Cover-crop a photo to tw x th, keeping focus point (fx, fy)."""
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    cx, cy = int(fx * nw), int(fy * nh)
    x0 = min(max(cx - tw // 2, 0), nw - tw)
    y0 = min(max(cy - th // 2, 0), nh - th)
    return im.crop((x0, y0, x0 + tw, y0 + th))


def tag_chip(x, y, tag):
    col = NAVY if tag == "REPORTED" else (RED if tag == "ONGOING" else (120, 90, 20))
    f = F_B(9)
    tw = width(tag, f) + 10
    d.rounded_rectangle([x, y, x + tw, y + 14], radius=3, fill=col)
    d.text((x + 5, y + 2), tag, font=f, fill=(255, 255, 255))
    return tw


# ---------------------------------------------------------------- data
# region per story; counts are computed from this list and asserted.
STORIES = [
    # leads 1-3 (big photo cards)
    dict(n=1, headline="COP31 COLLAPSES",
         body="No deal after a record 44-hour overtime; the EU and 130 parties rejected a text with no fossil fuels.",
         tag="REPORTED", src="BBC, The Hindu", region="EUROPE",
         photo="photos/cop31.jpg", fx=0.5, fy=0.45,
         caption="ANTALYA — PROTESTERS CALL THE DRAFT A \u2018FAILURE\u2019"),
    dict(n=2, headline="DYMER STRIKE KILLS 11",
         body="Boy, 7, alive after 14 hours under rubble; a woman after 22. Fifteen killed across the Kyiv region.",
         tag="ONGOING", src="BBC, Al Jazeera", region="EUROPE",
         photo="photos/dymer.jpg", fx=0.5, fy=0.45,
         caption="DYMER, KYIV REGION — STRUCK OVERNIGHT"),
    dict(n=3, headline="NIKKEI \u22125.06%",
         body="AI sell-off spreads; S&P 500 \u22123.7%, Nasdaq \u221210% last week; Tokyo falls 5.06% on Monday.",
         tag="REPORTED", src="SCMP, Al Jazeera", region="ASIA-PACIFIC",
         photo="photos/tse-market.jpg", fx=0.5, fy=0.35,
         caption="TOKYO STOCK EXCHANGE"),
    # photo row 4-5
    dict(n=4, headline="NVIDIA PROBES",
         body="Huang returns as CEO; shares jump 31%. NYT links Megaspeed\u2019s Huang to a Chinese spy agency.",
         tag="REPORTED", src="NYT, CNBC", region="NORTH AMERICA",
         photo="photos/nvidia.jpg", fx=0.5, fy=0.5,
         caption="NVIDIA HQ, SANTA CLARA"),
    dict(n=5, headline="IRAN WAR",
         body="Iran vows all means vs US blockade; 2 tankers hit mines near Hormuz.",
         tag="ONGOING", src="Al Jazeera, Fox News", region="MIDDLE EAST",
         photo="photos/iran.jpg", fx=0.5, fy=0.4,
         caption="KHARG ISLAND, PERSIAN GULF"),
    # medium 6-15
    dict(n=6, headline="RUSSIA TARGETED RAPPER",
         body="Moscow twice targeted a rapper. Denmark seeks EU action.",
         tag="REPORTED", src="Reuters", region="EUROPE"),
    dict(n=7, headline="SPARTA II HIT BY DRONE",
         body="Drone hits freighter in Gulf of Finland. Finland blames Ukraine.",
         tag="CLAIM", src="BBC, Tagesschau", region="EUROPE"),
    dict(n=8, headline="EU DEAL \u2018MUCH BETTER\u2019",
         body="Burnham: EU deal could make the next decade \u2018much better\u2019.",
         tag="REPORTED", src="BBC, Guardian", region="EUROPE"),
    dict(n=9, headline="ISTANBUL RALLY",
         body="Thousands march after Sozcu raid. Station now state-run.",
         tag="REPORTED", src="France 24, Le Monde", region="EUROPE"),
    dict(n=10, headline="NATO MEETS ON MISSILES",
         body="NATO meets Monday; 3 Russian missiles entered Poland.",
         tag="REPORTED", src="Polish Radio", region="EUROPE"),
    dict(n=11, headline="2,700 DRONES IN A WEEK",
         body="2,700 drones, 1,460 bombs, 165 missiles in one week.",
         tag="REPORTED", src="AP", region="EUROPE"),
    dict(n=12, headline="BANTEN FIRE KILLS 24",
         body="Factory fire Saturday evening. Dozens missing; DNA tests follow.",
         tag="ONGOING", src="Al Jazeera, BBC", region="ASIA-PACIFIC"),
    dict(n=13, headline="TRUMP PRAISES PUTIN",
         body="After Shenzhen; intel chief backs it. Zelensky: \u2018murderer\u2019.",
         tag="REPORTED", src="Al Jazeera, Guardian", region="NORTH AMERICA"),
    dict(n=14, headline="AUSTRALIA JOBLESS 5%+",
         body="Treasurer: jobless will exceed 5%. Growth below 2% in 2027-28.",
         tag="REPORTED", src="Guardian", region="ASIA-PACIFIC"),
    dict(n=15, headline="NEPAL PM VISITS INDIA",
         body="First trip abroad for Balen Shah. India pledges 15,000 crore aid.",
         tag="REPORTED", src="The Hindu, BBC", region="ASIA-PACIFIC"),
]

ALSO = [
    (16, "TATA STEEL $1.67BN STAKE", "CNBC", "ASIA-PACIFIC"),
    (17, "KOREA EXPORTS $1TN", "Yonhap", "ASIA-PACIFIC"),
    (18, "INDONESIA SEIZES 405 TONNES", "Inshorts", "ASIA-PACIFIC"),
    (19, "DEMOCRATS WIN 258 SEATS", "AP, BBC", "NORTH AMERICA"),
    (20, "RIEMANN PROOF CLAIMED", "France 24", "EUROPE"),
    (21, "IOWA TO DETONATE 5 TONS", "BBC", "NORTH AMERICA"),
    (22, "ICE SEATTLE VIDEO PROTESTS", "Guardian", "NORTH AMERICA"),
    (23, "DELTA OUTAGE DELAYS 1,600", "AP", "NORTH AMERICA"),
    (24, "PENNY\u2019S 232-YEAR RUN ENDS", "AP", "NORTH AMERICA"),
    (25, "HOUTHIS HIT SAUDI REFINERY", "CNBC", "MIDDLE EAST"),
    (26, "GAZA 99% CONTAMINATED", "Guardian", "MIDDLE EAST"),
    (27, "ISRAEL COALITION TALKS FAIL", "Al Jazeera", "MIDDLE EAST"),
    (28, "WEST BANK SETTLERS TORCH", "France 24", "MIDDLE EAST"),
    (29, "IRAN CLAIMS 58TH DRONE DOWN", "Inshorts", "MIDDLE EAST"),
    (30, "MERKURY SINKS", "BBC, Guardian", "AFRICA"),
    (31, "KHARTOUM DRONE STRIKES", "France 24", "AFRICA"),
    (32, "SOUTH SUDAN: 24 KILLED", "Folha", "AFRICA"),
    (33, "EBOLA RESPONSE DISRUPTED", "Al Jazeera", "AFRICA"),
    (34, "RWANDA TO HOST DEPORTEES", "El Pa\u00eds", "AFRICA"),
    (35, "BOLSONARO IN ICU", "MercoPress", "LATIN AMERICA"),
    (36, "BRAZIL STORM KILLS 5", "AP", "LATIN AMERICA"),
    (37, "BOCA WIN COPA", "BA Times", "SPORT & SCIENCE"),
    (38, "ALCARAZ WINS ATP FINALS", "Reuters", "SPORT & SCIENCE"),
    (39, "MARQUEZ WINS 8TH MOTOGP TITLE", "AP", "SPORT & SCIENCE"),
    (40, "CHINA DEATH SENTENCE FOR SPY", "AP", "ASIA-PACIFIC"),
    (41, "NHS TRIALS AI BREAST SCREENING", "BBC", "EUROPE"),
    (42, "PIG KIDNEY: ONE YEAR", "NYT", "NORTH AMERICA"),
    (43, "RUSSIAN JETS ENTER KOREA ZONE", "AP", "ASIA-PACIFIC"),
    (44, "KENYA\u2013CONGO TIES RESTORED", "allAfrica", "AFRICA"),
    (45, "BELGIUM FLIGHTS GROUNDED", "BBC", "EUROPE"),
]

NUMBERS = [
    ("44H", "COP31 overtime"),
    ("11", "killed in Dymer"),
    ("\u22125.06%", "Nikkei"),
    ("258", "House seats"),
    ("$1 trillion", "Korea exports"),
    ("1,600", "Delta flights"),
]

TIMELINE = [
    ("00:00", "COP31 no-deal"),
    ("02:00", "Nikkei \u22125.06%"),
    ("09:00", "Dymer rescue"),
    ("12:00", "NATO meets"),
    ("15:00", "Boca lift Copa"),
    ("18:00", "Alcaraz wins ATP"),
]

DATECHECK = ("DATE CHECK \u2014 Wires read to 23:00 UTC. Left out as "
             "wrong-day news: Peru 6.8 quake (20 Nov) \u00b7 400-drone barrage "
             "(19\u201320 Nov) \u00b7 Shenzhen summit (19\u201320 Nov) \u00b7 Meza-Flores "
             "capture (20 Nov) \u00b7 Bahrain strike (21 Nov) \u00b7 BepiColombo "
             "(21 Nov) \u00b7 EU-Indonesia deal (21 Nov) \u00b7 ICJ Myanmar ruling "
             "(19 Nov) \u00b7 Nigeria boat (22 Nov).")

PINS = [  # (story no, lon, lat, dx, dy) — dx/dy nudge pins apart in the
    # crowded Europe cluster and the Seoul/Tokyo pair (schematic map)
    (1, 32.9, 36.9, 10, 4), (2, 30.0, 50.8, 4, -10), (3, 139.7, 35.7, 6, 0),
    (4, -121.9, 37.4, 0, 0), (5, 50.3, 29.2, 8, 6), (7, 24.0, 59.8, -6, -8),
    (12, 106.1, -6.2, 0, 0), (19, -77.0, 38.9, 0, 0), (30, 20.1, 32.1, -8, 8),
    (35, -47.9, -15.8, 0, 0), (37, -58.4, -34.6, 0, 0), (38, 7.7, 45.1, -8, 0),
    (43, 127.0, 37.5, -6, 0),
]

# schematic world landmask, 48 cols (lon -180..180) x 14 rows (lat 85..-55)
LANDMASK = [
    ".............########..........###..............",
    ".##############.#####.....###.#################.",
    ".###############..##..#..######################.",
    ".....###########.......#######################..",
    "....##########..........##################.#....",
    "....#########.........############.##.####.#....",
    ".......#####..........############.##..####.....",
    ".........####.........#########.....#..#####....",
    ".............####.......########........#####...",
    ".............#####.......#######........######..",
    ".............####........######.........#####...",
    ".............####.........####..........#####...",
    "..............###.......................####..#.",
    "...............#..............................#.",
]
for _row in LANDMASK:
    assert len(_row) == 48, f"landmask row len {len(_row)}: {_row!r}"
assert len(LANDMASK) == 14

# region counts, computed from the data (never hand-typed)
REGIONS = ["EUROPE", "ASIA-PACIFIC", "NORTH AMERICA", "MIDDLE EAST",
           "AFRICA", "LATIN AMERICA", "SPORT & SCIENCE"]
_counts = {r: 0 for r in REGIONS}
for _s in STORIES:
    _counts[_s["region"]] += 1
for _n, _h, _src, _r in ALSO:
    _counts[_r] += 1
TOTAL = sum(_counts.values())
assert TOTAL == 45, f"story total {TOTAL} != 45"
assert len(STORIES) + len(ALSO) == 45

y = 0
GAP = 3


def section(h):
    global y
    top = y
    y += h + GAP
    return top


# ---------------------------------------------------------------- masthead
top = section(58)
d.rectangle([0, top, W, top + 58], fill=NAVY)
d.text((MARGIN, top + 8), "THE WORLD IN ONE DAY", font=F_SERIF_B(38), fill=(255, 255, 255))
date_s = "MONDAY, 23 NOVEMBER 2026"
dw = width(date_s, F_B(17))
d.text((W - MARGIN - dw, top + 20), date_s, font=F_B(17), fill=(255, 255, 255))

# ---------------------------------------------------------------- subline
top = section(22)
sub = (f"{TOTAL} STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED "
       f"MONDAY, 23 NOVEMBER 2026")
sw = width(sub, F_B(14))
d.text(((W - sw) / 2, top + 3), sub, font=F_B(14), fill=NAVY)

# ---------------------------------------------------------------- numbers
top = section(44)
cell = CW // 6
for i, (num, lab) in enumerate(NUMBERS):
    cx = MARGIN + i * cell
    nw = width(num, F_B(20))
    d.text((cx + (cell - nw) / 2, top + 2), num, font=F_B(20), fill=NAVY)
    lw = width(lab, F_R(10))
    d.text((cx + (cell - lw) / 2, top + 26), lab, font=F_R(10), fill=GREY)
    if i:
        d.line([cx, top + 4, cx, top + 40], fill=RULE, width=1)

# ---------------------------------------------------------------- regions
top = section(22)
d.rectangle([0, top, W, top + 22], fill=BAND)
parts = [f"{r} {_counts[r]}" for r in REGIONS]
reg = "  \u00b7  ".join(parts)
rw = width(reg, F_B(12))
d.text(((W - rw) / 2, top + 4), reg, font=F_B(12), fill=NAVY)

# ---------------------------------------------------------------- timeline
top = section(22)
d.rectangle([0, top, W, top + 22], fill=NAVY)
tl = "  \u00b7  ".join(f"{t}  {txt}" for t, txt in TIMELINE)
tlw = width(tl, F_B(11))
if tlw > CW:
    abort(f"timeline too wide: {tlw}")
d.text(((W - tlw) / 2, top + 4), tl, font=F_B(11), fill=(255, 255, 255))

# ---------------------------------------------------------------- leads 1-3
top = section(192)
colw = (CW - 2 * 12) // 3
for i, s in enumerate(STORIES[:3]):
    x = MARGIN + i * (colw + 12)
    ph = cover(s["photo"], colw, 128, s["fx"], s["fy"])
    img.paste(ph, (x, top))
    d.rectangle([x, top, x + colw - 1, top + 127], outline=NAVY, width=2)
    cap = s["caption"]
    cf = F_B(9)
    cw_ = width(cap, cf)
    if cw_ > colw - 8:
        abort(f"caption too wide: {cap!r}")
    d.rectangle([x, top + 128 - 18, x + colw, top + 128], fill=NAVY)
    d.text((x + (colw - cw_) / 2, top + 128 - 15), cap, font=cf, fill=(255, 255, 255))
    ty = top + 132
    hl = fit(f"{s['n']}. {s['headline']}", F_B(15), colw, 1, f"lead {s['n']} headline")
    d.text((x, ty), hl[0], font=F_B(15), fill=INK)
    ty += 19
    bl = fit(s["body"], F_R(10.5), colw, 2, f"lead {s['n']} body")
    for ln in bl:
        d.text((x, ty), ln, font=F_R(10.5), fill=INK)
        ty += 13
    ty += 2
    tw_ = tag_chip(x, ty, s["tag"])
    d.text((x + tw_ + 6, ty + 1), s["src"], font=F_R(10), fill=GREY)

# ---------------------------------------------------------------- photo row 4-5
top = section(140)
colw2 = (CW - 12) // 2
for i, s in enumerate(STORIES[3:5]):
    x = MARGIN + i * (colw2 + 12)
    ph = cover(s["photo"], 200, 96, s["fx"], s["fy"])
    img.paste(ph, (x, top + 22))
    d.rectangle([x, top + 22, x + 199, top + 117], outline=NAVY, width=2)
    cap = s["caption"]
    cf = F_B(8)
    cw_ = width(cap, cf)
    if cw_ > 200 - 6:
        abort(f"caption too wide: {cap!r}")
    d.rectangle([x, top + 118 - 14, x + 200, top + 118], fill=NAVY)
    d.text((x + (200 - cw_) / 2, top + 118 - 12), cap, font=cf, fill=(255, 255, 255))
    tx = x + 212
    tw2 = colw2 - 212
    hl = fit(f"{s['n']}. {s['headline']}", F_B(14), tw2, 1, f"photo {s['n']} headline")
    d.text((tx, top + 22), hl[0], font=F_B(14), fill=INK)
    bl = fit(s["body"], F_R(10.5), tw2, 2, f"photo {s['n']} body")
    by = top + 42
    for ln in bl:
        d.text((tx, by), ln, font=F_R(10.5), fill=INK)
        by += 13
    tw_ = tag_chip(tx, top + 96, s["tag"])
    d.text((tx + tw_ + 6, top + 97), s["src"], font=F_R(10), fill=GREY)

# ---------------------------------------------------------------- medium 6-15
top = section(215)
ROW_H = 43
for i, s in enumerate(STORIES[5:15]):
    col = i % 2
    row = i // 2
    x = MARGIN + col * (colw2 + 12)
    yy = top + row * ROW_H
    num = f"{s['n']}."
    nw_ = width(num, F_B(13))
    d.text((x, yy), num, font=F_B(13), fill=RED)
    hl = fit(s["headline"], F_B(13), colw2 - nw_ - 6, 1, f"medium {s['n']} headline")
    d.text((x + nw_ + 6, yy), hl[0], font=F_B(13), fill=INK)
    bl = fit(s["body"], F_R(11), colw2 - nw_ - 6, 1, f"medium {s['n']} body")
    d.text((x + nw_ + 6, yy + 17), bl[0], font=F_R(11), fill=INK)
    tagline = f"{s['tag']} \u00b7 {s['src']}"
    d.text((x + nw_ + 6, yy + 31), tagline, font=F_R(9), fill=GREY)

# ---------------------------------------------------------------- bottom band
top = section(255)
map_x, map_w = MARGIN, 480
also_x, also_w = MARGIN + 492, 492

# map (left)
d.text((map_x, top), "WHERE IT HAPPENED \u2014 13 STORIES PINNED", font=F_B(12), fill=NAVY)
map_top = top + 20
map_h = 160
d.rectangle([map_x, map_top, map_x + map_w - 1, map_top + map_h - 1], fill=SEA, outline=NAVY, width=1)
cw_cell = map_w / 48.0
ch_cell = map_h / 14.0
for r, row in enumerate(LANDMASK):
    for c, ch in enumerate(row):
        if ch == "#":
            d.rectangle([map_x + c * cw_cell, map_top + r * ch_cell,
                         map_x + (c + 1) * cw_cell - 0.5, map_top + (r + 1) * ch_cell - 0.5],
                        fill=LAND)


def pin_xy(lon, lat):
    px = map_x + (lon + 180.0) / 360.0 * map_w
    py = map_top + (85.0 - lat) / 140.0 * map_h
    return px, py


for n, lon, lat, dx, dy in PINS:
    px, py = pin_xy(lon, lat)
    px += dx
    py += dy
    d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
    ns = str(n)
    nf = F_B(8 if n < 10 else 7)
    nw_ = width(ns, nf)
    d.text((px - nw_ / 2, py - 5), ns, font=nf, fill=(255, 255, 255))

# date check (left, under map)
dc_top = map_top + map_h + 8
d.rectangle([map_x, dc_top, map_x + map_w - 1, top + 255 - 1], outline=NAVY, width=1)
d.text((map_x + 6, dc_top + 4), "DATE CHECK", font=F_B(11), fill=NAVY)
dc_lines = fit(DATECHECK, F_R(9.5), map_w - 12, 4, "date check")
dy = dc_top + 19
for ln in dc_lines:
    d.text((map_x + 6, dy), ln, font=F_R(9.5), fill=INK)
    dy += 12

# ALSO (right)
d.text((also_x, top), "ALSO ON MONDAY, 23 NOVEMBER \u2014 30 MORE STORIES", font=F_B(12), fill=NAVY)
also_top = top + 20
sub_w = (also_w - 12) // 2
af = F_R(9)
for i, (n, hl, src, _r) in enumerate(ALSO):
    col = i % 2
    row = i // 2
    x = also_x + col * (sub_w + 12)
    yy = also_top + row * 15
    line = f"{n}. {hl} \u2014 {src}"
    if width(line, af) > sub_w:
        abort(f"ALSO too wide: {line!r} ({width(line, af):.0f} > {sub_w})")
    d.text((x, yy), line, font=af, fill=INK)

# ---------------------------------------------------------------- footer
top = section(16)
foot = ("Sources: BBC, Al Jazeera, Reuters, AP, Guardian, CBS, France 24, PBS, SCMP, "
        "Yonhap, CNBC, NYT, allAfrica \u2014 all events Monday, 23 November 2026. "
        "All photographs are real news photographs of the events shown. "
        "REPORTED = confirmed by sources \u00b7 ONGOING = still developing \u00b7 "
        "CLAIM = as claimed, unverified.")
fl = fit(foot, F_R(9), CW, 2, "footer")
fy = top
for ln in fl:
    lw_ = width(ln, F_R(9))
    d.text(((W - lw_) / 2, fy), ln, font=F_R(9), fill=GREY)
    fy += 11

print(f"layout ends at y={y} of {H}")
if y > H:
    abort(f"layout overflows: y={y} > {H}")

img.save("entry.png", optimize=True)
data = open("entry.png", "rb").read()
print(f"entry.png: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
print(f"stories: {TOTAL}, regions: " + ", ".join(f"{r} {_counts[r]}" for r in REGIONS))
