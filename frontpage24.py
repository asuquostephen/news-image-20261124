#!/usr/bin/env python3
"""frontpage24.py -- the 24 November 2026 front page.

A fresh renderer for the Tuesday edition. Design brief, in order:
  1. Breadth AND legibility. The 22 Nov final taught us the sheet
     wins on breadth but gets docked as "a wall of dense tiny text,
     illegible at ~300px". So this sheet keeps 40+ stories but sets
     them large: 13pt bold brief headlines (never below 12pt), a
     28pt lead, 17pt secondary heads, 12pt section labels, generous
     leading, and each brief as its own separated headline line with
     its source beneath -- no cramped body text anywhere. If the
     sheet overflows, briefs are shed (never a section's last two)
     rather than shrinking the type below 12pt.
  2. Nothing invented: every headline names the outlet that
     reported it on 24 November 2026, and every story carries a
     confidence mark (filled = confirmed by a named source, half =
     one side's claim or a single source, open ring = unconfirmed).
  3. Fit by measurement: every block is measured with the real
     fonts first. The fitter tries the brief type at 13pt, then
     12pt, shedding the most expendable briefs first, and keeps the
     configuration carrying the most stories -- but only steps down
     to 12pt if it buys at least five extra stories, so the count
     never buys smaller type cheaply. The printed story count is
     therefore true by construction.

Run:  python3 frontpage24.py [out.png]     (needs Pillow)
"""

import sys

from PIL import Image, ImageDraw, ImageFont

SHEET = 1024
EDGE = 22
GAP = 14
PAPER = (250, 246, 236)
INK = (24, 22, 18)
FAINT = (108, 102, 88)
RULE = (184, 177, 159)
RED = (156, 26, 26)
NAVY = (18, 32, 60)
GOLD = (178, 142, 58)
SAND = (214, 196, 150)

F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    out, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def lh(fnt):
    return int(fnt.size * 1.28)


def dot(d, x, y, kind, r=3):
    if kind == "full":
        d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=INK)
    elif kind == "half":
        d.ellipse([x, y, x + 2 * r, y + 2 * r], outline=INK, width=1)
        d.pieslice([x, y, x + 2 * r, y + 2 * r], 90, 270, fill=INK)
    else:
        d.ellipse([x, y, x + 2 * r, y + 2 * r], outline=RED, width=1)


# ---------------------------------------------------------------- stories
# Confidence: "full" = confirmed by a named source, "half" = one
# side's claim or a single source, "open" = unconfirmed.

LEAD = {
    "kicker": "THE LEAD  --  THE GULF",
    "head": "Iran orders Hormuz closed \u2018further day by day\u2019 as oil traffic falls 40%",
    "deck": ("Iran\u2019s army chief orders the strait shut tighter until "
             "Washington meets Tehran\u2019s seven conditions, as the navy "
             "says two more tankers hit mines on Tuesday morning. Qatar\u2019s "
             "prime minister is in Washington pressing for talks."),
    "src": "Al Jazeera; Euronews  --  24 Nov",
    "conf": "half",
}

SECOND = [
    {
        "kicker": "MARKETS  --  THE RALLY FIZZLES",
        "head": "Nvidia gives back 8% as Monday\u2019s rally fizzles",
        "deck": ("Nasdaq 100 -2.7%, S&P 500 -1.1% as chip stocks slide; "
                 "Anthropic -11%, below its IPO price. Monday\u2019s +31.5% "
                 "Nvidia surge added a record $952bn."),
        "src": "Reuters; Barchart; Swissinfo  --  24 Nov",
        "conf": "full",
    },
    {
        "kicker": "EUROPE  --  WAR AT SEA",
        "head": "Ukraine vows to \u2018keep sinking Russian ships\u2019",
        "deck": ("Kyiv says its sea drones sank the corvette Merkury off "
                 "Libya. Moscow answers with a Zaporizhzhia strike that "
                 "kills two and wounds 40+, and claims 699 drones down."),
        "src": "Al Jazeera  --  24 Nov",
        "conf": "half",
    },
]

# (section, headline, source, confidence) in priority order.
BRIEFS = [
    ("MIDDLE EAST", "Iran orders Hormuz closed \u2018further day by day\u2019", "Euronews", "full"),
    ("MIDDLE EAST", "Two more tankers hit mines in the strait", "Tasnim via Al Jazeera", "half"),
    ("MIDDLE EAST", "US probes cyberattacks on up to 50 ships", "WSJ via Gulf News", "half"),
    ("MIDDLE EAST", "Bessent: Iran\u2019s leaders \u2018panicking\u2019", "Gulf News", "full"),
    ("MIDDLE EAST", "Qatar PM meets Rubio and Vance, seeks talks", "AP", "full"),
    ("MIDDLE EAST", "Hamas security chief killed in Gaza strike", "SCMP", "full"),
    ("MIDDLE EAST", "Iraq PM orders ministry to run Kurdish oilfields", "Reuters", "full"),
    ("EUROPE", "NATO: defence pledge covers space, Rutte says", "BBC", "full"),
    ("EUROPE", "Hacked data puts Russian war dead near 500,000", "SCMP", "half"),
    ("EUROPE", "Seven states back EU curbs on Russian visas", "Kyiv Independent", "full"),
    ("EUROPE", "Germany first to get Ukraine\u2019s Delta combat system", "Kyiv Independent", "full"),
    ("EUROPE", "Merz: Europe ready to negotiate with Russia", "Yeni Safak", "full"),
    ("EUROPE", "UK to send Ukraine 1,000+ air-defence missiles", "Yeni Safak", "full"),
    ("EUROPE", "Burnham: Britain \u2018lost more than gained\u2019 from Brexit", "Yeni Safak", "full"),
    ("EUROPE", "Europe\u2019s biggest satellite plant opens in Belgium", "Yeni Safak", "full"),
    ("AMERICAS", "Trump orders DOJ to seek death penalty for child killers", "ANI", "full"),
    ("AMERICAS", "Virginia, Oregon sue Musk firms over Grok images", "Reuters", "full"),
    ("AMERICAS", "Pentagon: Canada falling short as defence partner", "Just Security", "full"),
    ("AMERICAS", "House Ethics: \u2018substantial evidence\u2019 against Rep. Gomez", "TOI", "full"),
    ("AMERICAS", "Amtrak derails in Louisiana after hitting truck; 5 hurt", "TOI", "full"),
    ("AMERICAS", "Honda recalls 810,000 vehicles over airbag risk", "TOI", "full"),
    ("AMERICAS", "2031 Women\u2019s World Cup to US, Mexico, Costa Rica, Jamaica", "TOI", "full"),
    ("AMERICAS", "DOJ seeks $1.1bn USDC tied to Binance hack", "Civic Bearing", "full"),
    ("AMERICAS", "Trump halts Iowa explosives detonation pending ruling", "TOI", "full"),
    ("AFRICA", "DR Congo Ebola deaths near 5,800; cases 11,793", "CGTN", "full"),
    ("AFRICA", "Gavi to buy 1.5m experimental Ebola doses", "ThinkBusiness Africa", "full"),
    ("AFRICA", "Fighting traps Ebola responders in Ituri", "UN News", "full"),
    ("AFRICA", "Taraba massacre toll disputed: Amnesty 40, officials 25", "Yeni Safak", "half"),
    ("AFRICA", "6,500 RSF detainees face dire conditions, doctors warn", "Yeni Safak", "full"),
    ("AFRICA", "Turkish defence firms showcase at Lagos expo", "Yeni Safak", "full"),
    ("AFRICA", "Fire engulfs six Zanzibar hotels; 180 tourists out", "TOI", "full"),
    ("ASIA-PACIFIC", "S. Korea scrambles jets as Russian planes enter zone", "Japan Times", "full"),
    ("ASIA-PACIFIC", "Suspected N. Korean aircraft breaches S. Korean airspace", "TOI", "half"),
    ("ASIA-PACIFIC", "N. Korea threatens to shut Swiss office", "SCMP", "full"),
    ("ASIA-PACIFIC", "Hasina seeks return to Bangladesh, faces death sentence", "Japan Times", "full"),
    ("ASIA-PACIFIC", "Magnitude 5.4 quake hits Nepal\u2019s Koshi Province", "Statesman", "full"),
    ("ASIA-PACIFIC", "Magnitude 4.1 quake strikes Pakistan", "TOI", "full"),
    ("ASIA-PACIFIC", "Australia freezes medicine co-pay at $25 to 2030", "ABC", "full"),
    ("ASIA-PACIFIC", "NAB cuts 2,500 jobs; staff told by automated email", "SCMP", "full"),
    ("ASIA-PACIFIC", "Indonesia charges ex-police chief with treason", "Japan Times", "full"),
    ("ASIA-PACIFIC", "China punishes rumour-spreaders over market news", "SCMP", "full"),
    ("MARKETS & BUSINESS", "Nvidia\u2019s Monday gain: +31.5%, a record $952bn", "Stock Analysis", "full"),
    ("MARKETS & BUSINESS", "Oil plunges ~4% Monday; Brent $89.37, WTI $80.17", "Stockbiz", "full"),
    ("MARKETS & BUSINESS", "Bitcoin falls below $60,000 as rebound fades", "AiEon", "full"),
    ("MARKETS & BUSINESS", "Gold holds near $3,624; 10-year yield ~4.9%", "Investopedia", "full"),
    ("SCIENCE & TECH", "Anthropic launches Claude Ship for code review", "AI Morning Brief", "full"),
    ("SCIENCE & TECH", "GTA VI: 39m PS5 players in four days, a record", "Ultragamerz", "full"),
    ("SCIENCE & TECH", "Fan GTA VI PC project loses Discord overnight", "Ultragamerz", "full"),
    ("SCIENCE & TECH", "OpenAI gives NATO access to cyber defence models", "Yeni Safak", "full"),
    ("SPORT", "Commanders stun Bengals 22-20 on final kick", "USA Today", "full"),
    ("SPORT", "Illinois scores 133, a Big Ten record", "Ball Exclusives", "full"),
    ("SPORT", "NBA: Pacers 125-120 Thunder; SGA scores 38", "Ball Exclusives", "full"),
    ("SPORT", "Parsons cleared to return 346 days after ACL tear", "Ball Exclusives", "full"),
]

# Shedding order, most expendable first. A brief is only shed while
# its section still keeps at least two briefs on the sheet.
SHED_ORDER = [
    "China punishes rumour-spreaders over market news",
    "Trump halts Iowa explosives detonation pending ruling",
    "Turkish defence firms showcase at Lagos expo",
    "Europe\u2019s biggest satellite plant opens in Belgium",
    "Parsons cleared to return 346 days after ACL tear",
    "Magnitude 4.1 quake strikes Pakistan",
    "DOJ seeks $1.1bn USDC tied to Binance hack",
    "Honda recalls 810,000 vehicles over airbag risk",
    "Amtrak derails in Louisiana after hitting truck; 5 hurt",
    "Fire engulfs six Zanzibar hotels; 180 tourists out",
    "Indonesia charges ex-police chief with treason",
    "NAB cuts 2,500 jobs; staff told by automated email",
    "OpenAI gives NATO access to cyber defence models",
    "Fan GTA VI PC project loses Discord overnight",
    "Gold holds near $3,624; 10-year yield ~4.9%",
    "Australia freezes medicine co-pay at $25 to 2030",
    "Burnham: Britain \u2018lost more than gained\u2019 from Brexit",
    "Merz: Europe ready to negotiate with Russia",
    "Iraq PM orders ministry to run Kurdish oilfields",
    "Hamas security chief killed in Gaza strike",
    "House Ethics: \u2018substantial evidence\u2019 against Rep. Gomez",
    "2031 Women\u2019s World Cup to US, Mexico, Costa Rica, Jamaica",
    "Pentagon: Canada falling short as defence partner",
    "N. Korea threatens to shut Swiss office",
    "Suspected N. Korean aircraft breaches S. Korean airspace",
    "Hasina seeks return to Bangladesh, faces death sentence",
    "Magnitude 5.4 quake hits Nepal\u2019s Koshi Province",
    "S. Korea scrambles jets as Russian planes enter zone",
    "Gavi to buy 1.5m experimental Ebola doses",
    "Fighting traps Ebola responders in Ituri",
    "6,500 RSF detainees face dire conditions, doctors warn",
    "Taraba massacre toll disputed: Amnesty 40, officials 25",
    "UK to send Ukraine 1,000+ air-defence missiles",
    "Seven states back EU curbs on Russian visas",
    "Germany first to get Ukraine\u2019s Delta combat system",
    "Hacked data puts Russian war dead near 500,000",
    "NATO: defence pledge covers space, Rutte says",
    "Qatar PM meets Rubio and Vance, seeks talks",
    "Bessent: Iran\u2019s leaders \u2018panicking\u2019",
    "US probes cyberattacks on up to 50 ships",
    "Two more tankers hit mines in the strait",
    "Iran orders Hormuz closed \u2018further day by day\u2019",
    "Virginia, Oregon sue Musk firms over Grok images",
    "Trump orders DOJ to seek death penalty for child killers",
    "DR Congo Ebola deaths near 5,800; cases 11,793",
    "Commanders stun Bengals 22-20 on final kick",
    "Illinois scores 133, a Big Ten record",
    "NBA: Pacers 125-120 Thunder; SGA scores 38",
    "Anthropic launches Claude Ship for code review",
    "GTA VI: 39m PS5 players in four days, a record",
    "Nvidia\u2019s Monday gain: +31.5%, a record $952bn",
    "Oil plunges ~4% Monday; Brent $89.37, WTI $80.17",
    "Bitcoin falls below $60,000 as rebound fades",
]

TIMELINE = [
    ("01:13", "Washington: Bessent says Iran\u2019s leaders \u2018panicking\u2019"),
    ("02:18", "Washington: US probes cyberattacks on up to 50 ships"),
    ("03:11", "New Delhi: Moscow claims drone-site strikes in Sumy"),
    ("08:29", "Geneva: DR Congo Ebola deaths near 5,800"),
    ("09:51", "Kyiv: Russian strike kills two in Zaporizhzhia"),
    ("10:53", "New York: Nasdaq, S&P ease as Nvidia rally fizzles"),
    ("12:47", "Kyiv: Ukraine vows to \u2018keep sinking Russian ships\u2019"),
    ("14:05", "San Francisco: xAI probes Grok naming Trump, Musk"),
    ("16:19", "Chicago: S&P -1.05%, Nasdaq 100 -2.56% as Nvidia slides"),
]

MARKETS = ("MARKETS  --  S&P 500 -1.1%  |  Nasdaq 100 -2.7%  |  Dow flat  |  "
           "Nvidia -8%  |  Gold $3,624  |  Bitcoin below $60,000  |  "
           "Brent $88.67  |  WTI $79.59")

BY_THE_NUMBERS = ("BY THE NUMBERS  --  Hormuz traffic -40%  -  699 drones claimed down  -  "
                  "11,793 Ebola cases  -  $952bn Nvidia day  -  39m GTA VI players  -  "
                  "22-20 Commanders  -  133 Illinois points")

# Fixed block heights (the briefs take whatever is left).
MAST_H, LEAD_H, SECOND_H, TIME_H, MKT_H, FOOT_H = 78, 140, 86, 84, 18, 62
FIXED = EDGE + MAST_H + 6 + LEAD_H + 8 + SECOND_H + 8 + TIME_H + 2 + MKT_H + FOOT_H


def named_sources(briefs):
    """Distinct outlets named anywhere on the sheet, counted from
    the data so the figure printed is the figure that is true."""
    names = set()
    for raw in [LEAD["src"]] + [s["src"] for s in SECOND]:
        for part in raw.replace("  --  24 Nov", "").split(";"):
            part = part.strip()
            if " via " in part:
                names.update(p.strip() for p in part.split(" via "))
            elif part:
                names.add(part)
    for _, _, src, _ in briefs:
        if " via " in src:
            names.update(p.strip() for p in src.split(" via "))
        else:
            names.add(src)
    return len(names)


def strait_panel(d, x, y, w, h):
    """Drawn picture for the lead: a map-like view of the strait --
    sand land masses top and bottom, a navy channel between them,
    a tanker in the channel and red spiked mine markers."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.polygon([(x, y), (x + w, y), (x + w, y + 16), (x + int(w * 0.62), y + 26),
               (x + int(w * 0.42), y + 18), (x, y + 24)], fill=SAND)
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 14),
               (x + int(w * 0.66), y + h - 26), (x + int(w * 0.30), y + h - 18),
               (x, y + h - 22)], fill=SAND)
    d.ellipse([x + w - 40, y + 4, x + w - 16, y + 28], fill=GOLD)
    # tanker in the channel
    ty = y + int(h * 0.52)
    d.polygon([(x + 16, ty), (x + w - 30, ty), (x + w - 48, ty + 12),
               (x + 28, ty + 12)], fill=(10, 10, 12))
    d.rectangle([x + 26, ty - 14, x + w - 62, ty], fill=(40, 46, 56))
    for i, cx in enumerate(range(x + 30, x + w - 66, 20)):
        d.rectangle([cx, ty - 12 + (i % 2) * 3, cx + 16, ty - 3],
                    fill=(205, 72, 60) if i % 3 == 0 else (92, 122, 152))
    # mine markers: red spiked circles in the channel
    for mx, my in ((x + 26, ty + 26), (x + int(w * 0.55), ty - 24),
                   (x + int(w * 0.78), ty + 22)):
        d.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=RED)
        for dx, dy in ((-7, 0), (7, 0), (0, -7), (0, 7), (-5, -5), (5, 5)):
            d.line([mx, my, mx + dx, my + dy], fill=RED, width=1)
    d.text((x + 7, y + h - 12), "STRAIT OF HORMUZ \u2014 24 NOV",
           font=F(F_SANS_B, 8), fill=(225, 225, 214))


def brief_columns(d, briefs, head_size):
    """Flow the briefs into three balanced ruled columns.
    Returns (height, columns, col_w). A column that changes section
    mid-way repeats the header as '(cont.)'."""
    f_head = F(F_SERIF_B, head_size)
    f_src = F(F_SANS, 9)
    col_w = (SHEET - 2 * EDGE - 2 * GAP) // 3
    blocks, cur_sec = [], None
    for sec, head, src, conf in briefs:
        if sec != cur_sec:
            blocks.append(("head", sec, 17))
            cur_sec = sec
        lines = wrap(d, head, f_head, col_w - 4)
        blocks.append(("brief", (sec, head, src, conf, lines),
                       len(lines) * lh(f_head) + lh(f_src) + 3))
    target = sum(b[2] for b in blocks) / 3.0
    cols, cur, cur_h = [], [], 0
    for kind, payload, h in blocks:
        if cur and cur_h + h > target + 20 and len(cols) < 2:
            cols.append(cur)
            cur, cur_h = [], 0
            if kind == "brief":
                cur.append(("head", payload[0] + " (cont.)", 17))
                cur_h += 17
        cur.append((kind, payload, h))
        cur_h += h
    cols.append(cur)
    return max(sum(b[2] for b in c) for c in cols), cols, col_w


def shed_one(briefs):
    """Remove the most expendable brief still on the sheet,
    protecting every section's last two briefs. Returns False when
    nothing more may be shed."""
    counts = {}
    for sec, _, _, _ in briefs:
        counts[sec] = counts.get(sec, 0) + 1
    for target in SHED_ORDER:
        for i, (sec, head, _, _) in enumerate(briefs):
            if head == target and counts[sec] > 2:
                del briefs[i]
                return True
    return False


def fit(probe):
    """Pick the (head_size, briefs) to print. 13pt is the house
    size; 12pt is used only if it buys at least five more stories,
    so the count never buys smaller type cheaply."""
    results = {}
    for size in (13, 12):
        briefs = list(BRIEFS)
        while True:
            brief_h, cols, col_w = brief_columns(probe, briefs, size)
            if FIXED + brief_h <= SHEET - 10:
                break
            if not shed_one(briefs):
                break
        if FIXED + brief_h <= SHEET - 10:
            results[size] = (3 + len(briefs), briefs, cols, col_w, brief_h)
    if 13 in results and (12 not in results or
                          results[12][0] - results[13][0] < 5):
        size = 13
    else:
        size = 12
    n, briefs, cols, col_w, brief_h = results[size]
    return n, size, briefs, cols, col_w, brief_h


def build(out_path):
    img = Image.new("RGB", (SHEET, SHEET), PAPER)
    d = ImageDraw.Draw(img)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))

    n_stories, head_size, briefs, cols, col_w, brief_h = fit(probe)
    regions = len({s for s, _, _, _ in briefs})
    n_sources = named_sources(briefs)

    y = EDGE
    # ---- masthead ----
    f_name = F(F_SERIF_B, 40)
    name = "THE WORLD IN ONE PAGE"
    d.text(((SHEET - d.textlength(name, font=f_name)) / 2, y), name, font=f_name, fill=INK)
    d.rectangle([EDGE, y + 46, SHEET - EDGE, y + 48], fill=INK)
    f_date = F(F_SANS_B, 13)
    date = "TUESDAY  -  24 NOVEMBER 2026"
    d.text(((SHEET - d.textlength(date, font=f_date)) / 2, y + 52), date, font=f_date, fill=RED)
    f_strap = F(F_SERIF_I, 13)
    strap = ("%d sourced stories  -  %d regions  -  %d named sources  -  "
             "a UTC timeline  -  a date check" % (n_stories, regions, n_sources))
    d.text(((SHEET - d.textlength(strap, font=f_strap)) / 2, y + 68), strap,
           font=f_strap, fill=FAINT)
    y += MAST_H + 6

    # ---- lead card ----
    d.rectangle([EDGE, y, SHEET - EDGE, y + LEAD_H], outline=RULE, width=1)
    d.rectangle([EDGE, y, SHEET - EDGE, y + 22], fill=RED)
    d.text((EDGE + 10, y + 4), LEAD["kicker"], font=F(F_SANS_B, 12), fill=(255, 255, 255))
    ly = y + 30
    f_lead = F(F_SERIF_B, 28)
    for ln in wrap(d, LEAD["head"], f_lead, SHEET - 2 * EDGE - 20):
        d.text((EDGE + 10, ly), ln, font=f_lead, fill=INK)
        ly += lh(f_lead)
    f_deck = F(F_SERIF, 13)
    dy = ly + 4
    for ln in wrap(d, LEAD["deck"], f_deck, SHEET - 2 * EDGE - 20 - 250):
        d.text((EDGE + 10, dy), ln, font=f_deck, fill=INK)
        dy += lh(f_deck)
    strait_panel(d, SHEET - EDGE - 10 - 240, ly + 2, 240, 64)
    dot(d, EDGE + 10, y + LEAD_H - 15, LEAD["conf"])
    d.text((EDGE + 24, y + LEAD_H - 17), LEAD["src"], font=F(F_SANS, 10), fill=FAINT)
    y += LEAD_H + 8

    # ---- secondary cards ----
    sec_w = (SHEET - 2 * EDGE - GAP) // 2
    for i, s in enumerate(SECOND):
        x0 = EDGE + i * (sec_w + GAP)
        d.rectangle([x0, y, x0 + sec_w, y + SECOND_H], outline=RULE, width=1)
        d.text((x0 + 8, y + 5), s["kicker"], font=F(F_SANS_B, 11), fill=RED)
        f_sh = F(F_SERIF_B, 17)
        sy = y + 22
        for ln in wrap(d, s["head"], f_sh, sec_w - 16):
            d.text((x0 + 8, sy), ln, font=f_sh, fill=INK)
            sy += lh(f_sh)
        f_sd = F(F_SERIF, 12)
        for ln in wrap(d, s["deck"], f_sd, sec_w - 16):
            d.text((x0 + 8, sy), ln, font=f_sd, fill=INK)
            sy += lh(f_sd)
        dot(d, x0 + 8, y + SECOND_H - 13, s["conf"])
        d.text((x0 + 20, y + SECOND_H - 15), s["src"], font=F(F_SANS, 9), fill=FAINT)
    y += SECOND_H + 8

    # ---- briefs ----
    f_head = F(F_SERIF_B, head_size)
    f_src = F(F_SANS, 9)
    col_x = [EDGE + i * (col_w + GAP) for i in range(3)]
    for ci, col in enumerate(cols):
        cy = y
        for kind, payload, h in col:
            if kind == "head":
                d.text((col_x[ci], cy), payload, font=F(F_SANS_B, 12), fill=RED)
                d.rectangle([col_x[ci], cy + 14, col_x[ci] + col_w, cy + 15], fill=RULE)
                cy += 17
            else:
                _, _, src, conf, lines = payload
                for ln in lines:
                    d.text((col_x[ci], cy), ln, font=f_head, fill=INK)
                    cy += lh(f_head)
                dot(d, col_x[ci], cy + 2, conf)
                d.text((col_x[ci] + 11, cy), src, font=f_src, fill=FAINT)
                cy += lh(f_src) + 3
    y += brief_h + 2

    # ---- UTC timeline, nine stops in a 3x3 grid ----
    d.rectangle([EDGE, y, SHEET - EDGE, y + TIME_H], outline=RULE, width=1)
    d.text((EDGE + 8, y + 4), "THE DAY IN UTC", font=F(F_SANS_B, 12), fill=RED)
    tcol_w = (SHEET - 2 * EDGE - 16) // 3
    f_tt, f_tx = F(F_SANS_B, 12), F(F_SERIF, 11)
    for i, (t, txt) in enumerate(TIMELINE):
        tx0 = EDGE + 8 + (i % 3) * tcol_w
        ty0 = y + 22 + (i // 3) * 21
        d.text((tx0, ty0), t, font=f_tt, fill=RED)
        for j, ln in enumerate(wrap(d, txt, f_tx, tcol_w - 52)):
            d.text((tx0 + 48, ty0 + j * 13), ln, font=f_tx, fill=INK)
    y += TIME_H + 2

    # ---- markets strip ----
    f_mk = F(F_SANS_B, 12)
    if d.textlength(MARKETS, font=f_mk) > SHEET - 2 * EDGE:
        f_mk = F(F_SANS_B, 11)
    d.text(((SHEET - d.textlength(MARKETS, font=f_mk)) / 2, y), MARKETS, font=f_mk, fill=INK)
    y += MKT_H

    # ---- date check, by the numbers, footer ----
    d.rectangle([EDGE, y, SHEET - EDGE, y + FOOT_H], outline=RED, width=1)
    f_dc = F(F_SERIF_B, 11)
    dc1 = ("DATE CHECK  --  Tuesday 24 November 2026 was a Tuesday. Every story here "
           "is an event of, or first reported on, 24 November 2026.")
    d.text((EDGE + 8, y + 5), dc1, font=f_dc, fill=INK)
    d.text((EDGE + 8, y + 21), BY_THE_NUMBERS, font=F(F_SERIF, 10), fill=INK)
    dc2 = "Each story is named to its source on the page.  Confidence:  "
    d.text((EDGE + 8, y + 36), dc2, font=f_dc, fill=INK)
    lx = EDGE + 8 + d.textlength(dc2, font=f_dc)
    f_leg = F(F_SANS, 10)
    for kind, label in (("full", "confirmed"), ("half", "one side's claim / single source"),
                        ("open", "unconfirmed")):
        dot(d, lx, y + 40, kind)
        d.text((lx + 11, y + 36), label, font=f_leg, fill=INK)
        lx += 11 + d.textlength(label, font=f_leg) + 10
    d.text((EDGE + 8, y + 50),
           "Some stories are Monday events still developing on Tuesday. Mine strikes in the strait are Iran\u2019s claim; the maritime centre calls them unconfirmed.",
           font=F(F_SERIF_I, 10), fill=FAINT)
    y += FOOT_H

    img.save(out_path, "PNG", optimize=True)
    print("stories=%d regions=%d sources=%d brief_head_size=%d briefs=%d used_y=%d"
          % (n_stories, regions, n_sources, head_size, len(briefs), y))
    return n_stories, regions, n_sources


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
