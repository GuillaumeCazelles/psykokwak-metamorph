"""Builds ../index.html from template.html + data sources in src/.

src/cards.json   one entry per binder slot (TCGdex details, Cardmarket FR/EN product, Japanese equivalent product)
src/prices.json  Cardmarket prices scraped per language: "idProduct_lang" -> {n, p: 5 cheapest Near Mint offers}
                 (lang 2 = French, 7 = Japanese; first editions / reverses excluded)
src/pg.json      Cardmarket public price guide (all languages), downloaded on each run (not committed, 15 MB)
../img/          images for cards TCGdex has no picture of (Japanese exclusives, recent promos, cameos)
"""
import json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
ROOT = os.path.join(HERE, "..")
PRICE_GUIDE_URL = "https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_6.json"
def jload(name, default=None):
    p = os.path.join(SRC, name)
    if not os.path.exists(p): return default
    with open(p, encoding="utf-8") as f: return json.load(f)

if "--offline" not in sys.argv or not os.path.exists(os.path.join(SRC, "pg.json")):
    print("Téléchargement du guide des prix Cardmarket…")
    urllib.request.urlretrieve(PRICE_GUIDE_URL, os.path.join(SRC, "pg.json"))

RAW = jload("cards.json")
SCRAPED = jload("prices.json", {}) or {}
PG = {p["idProduct"]: p for p in jload("pg.json")["priceGuides"]}

# French names of cards TCGdex has no French data for
FR_NAMES = {"gym1-54": "Psykokwak d'Ondine", "gym2-90": "Psykokwak d'Ondine", "gym2-99": "Psykokwak de Morgane",
            "gym2-10": "Métamorph de Koga", "gym1-114": "Colère d'Ondine", "gym2-121": "Contrôle psychique de Morgane",
            "gym2-115": "Ruse ninja de Koga", "ex7-70": "Psykokwak", "lc-88": "Psykokwak", "2018sm-2": "Psykokwak"}
SET_FR_FALLBACK = {"gym1": "Gym Heroes", "gym2": "Gym Challenge", "lc": "Legendary Collection",
                   "ex7": "EX Team Rocket Returns", "2018sm": "McDonald's Collection 2018"}
# Never printed in French: Southern Islands, Skyridge, Wizards promos, and the Worlds stadium promos (English only)
EN_ONLY = {"si1-14", "ecard3-51", "basep-20", "np-26", "np-27", "np-36", "dpp-DP05", "dpp-DP25", "dpp-DP48",
           "hgssp-HGSS18", "bwp-BW28", "bwp-BW50", "bwp-BW95", "xyp-XY27", "xyp-XY91", "xyp-XY176", "smp-SM78",
           "smp-SM148", "smp-SM231", "swshp-SWSH296", "svp-045", "svp-150", "svp-224", "mep-092"}
# Japanese equivalents found after the fact (visual check on Cardmarket)
JP_EXTRA = {"mep-106": 907886, "basep-20": 606001}
# Promo sets carry the series start date: use each promo's own release (Worlds year for Worlds stadiums)
PROMO_DATES = {"np-26": "2004-08-01", "np-27": "2004-08-01", "np-36": "2005-08-01", "dpp-DP05": "2007-08-01",
               "dpp-DP25": "2008-08-01", "dpp-DP48": "2009-08-01", "hgssp-HGSS18": "2010-08-01", "bwp-BW28": "2011-08-01",
               "bwp-BW50": "2012-08-01", "bwp-BW95": "2013-08-01", "xyp-XY27": "2014-08-01", "xyp-XY40": "2014-10-01",
               "xyp-XY91": "2015-08-01", "xyp-XY176": "2016-08-01", "smp-SM78": "2017-08-01", "smp-SM148": "2018-08-01",
               "smp-SM199": "2019-05-01", "smp-SM231": "2019-08-01", "swshp-SWSH296": "2022-08-01", "svp-045": "2023-08-01",
               "svp-150": "2024-08-01", "svp-224": "2025-08-01", "mep-007": "2025-10-01", "mep-092": "2026-08-01",
               "mep-106": "2026-09-16"}
RARITY_FR = {"Common": "Commune", "Uncommon": "Peu commune", "Rare": "Rare", "Rare Holo": "Rare holo", "Holo Rare": "Rare holo",
             "Ultra Rare": "Ultra rare", "Secret Rare": "Rare secrète", "Illustration rare": "Illustration rare",
             "Special illustration rare": "Illustration spéciale rare", "Promo": "Promo", "Double rare": "Double rare",
             "Shiny rare": "Chromatique", "Rare Holo LV.X": "Rare holo", "None": "—"}
JP_ONLY = [  # (poke, set label, code, number, date, cardmarket id, rarity)
    ("psy", "ADV-P Promos", "ADV-P", "056/ADV-P", "2004-06-01", 571043, "Promo"),
    ("psy", "Silver Deck Kit", "pcgE", "001/032", "2004-11-01", 783258, "—"),
    ("psy", "XY-P Promos (PokéKyun Collection)", "XY-P", "XY-P", "2016-03-01", 664952, "Promo"),
    ("psy", "SM-P Promos (« Le Cri »)", "SM-P", "286/SM-P", "2018-10-27", 469989, "Promo"),
    ("psy", "Detective Pikachu", "smP2", "009/024", "2019-03-01", 557149, "Commune"),
    ("psy", "SM Family Pokémon Card Game", "smL", "013/051", "2019-06-01", 564707, "Commune"),
    ("psy", "Start Deck 100", "sI", "076/414", "2021-12-17", 587786, "—"),
    ("ditto", "Expansion Sheet", "EXS", "No. 132", "1998-06-01", 548896, "—"),
    ("ditto", "PCG-P Promos", "PCG-P", "108/PCG-P", "2005-06-01", 570654, "Promo"),
]
CAMEO_JP = [  # cameos printed only in Japanese and not sold on Cardmarket
    ("psy", "Machoc", "ワンリキー", "Expansion Sheet 2", "1998-09-01", "Machoc"),
    ("psy", "Vent tropical", "トロピカルウインド", "Promo Tropical Mega Battle 1999", "1999-08-01", "Vent tropical"),
    ("psy", "Vent tropical (VS)", "トロピカルウインド", "Promo VS (P Promo 008)", "2001-08-01", "Brise tropicale"),
    ("psy", "Gobou du PokéPark", "ポケパークのミズゴロウ", "PCG-P Promos 048", "2005-07-01", "Gobou du PokéPark"),
    ("psy", "Évoli", "イーブイ", "SM-P Promos 287 (« Le Cri »)", "2018-10-27", "Évoli"),
    ("ditto", "Machopeur", "ゴーリキー", "Expansion Sheet 3", "1999-01-01", "Machopeur"),
    ("ditto", "Présentation de l'influenceur", "インフルエンサーの紹介", "Start Deck 100 CoroCiao 019", "2025-06-01",
     "Présentation de l'influenceur"),
]
POKE_FR = {"psy": "Psykokwak", "ditto": "Métamorph"}
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]

def date_fr(d): return f"{MOIS[int(d[5:7]) - 1]} {d[:4]}"
def local_img(name):
    p = f"img/{name}.jpg"
    return p if os.path.exists(os.path.join(ROOT, p)) else None

GROUPS, CARDS = [], []

def add(group, cards):
    GROUPS.append(group); CARDS.extend(cards)

for poke, rows in RAW.items():
    for c in rows:
        cid = c.get("id")
        if not cid: continue
        cameo = c["kind"] == "cameo"
        dup = next((g for g in GROUPS if g["id"] == cid), None)
        if dup:  # cameo of both Pokémon (e.g. Twilight Masquerade Chansey): one page mentioning both
            dup["s"] = dup["s"].replace(f"caméo : {POKE_FR[dup['poke']]}", "caméo : Psykokwak et Métamorph")
            continue
        date = PROMO_DATES.get(cid, c["date"])
        name_fr = FR_NAMES.get(cid) or c.get("name_fr") or c["name_en"]
        set_fr = c.get("set_fr") or SET_FR_FALLBACK.get(cid.split("-")[0]) or c["set_en"]
        num = c["num"] + (f"/{c['total']}" if c.get("total") and c["num"].isdigit() and int(c["num"]) <= int(c["total"]) else "")
        abbr = f" ({c['abbr']})" if c.get("abbr") else ""
        img = c.get("img_fr") or c.get("img_en") or local_img(cid)
        rar = RARITY_FR.get(c.get("rarity") or "None", c.get("rarity") or "—")
        sub = [f"n° {num}", date_fr(date)]
        if cameo: sub.append(f"caméo : {POKE_FR[poke]}" + (f" ({c['notes']})" if c.get("notes") else ""))
        g = {"id": cid, "poke": poke, "cameo": cameo, "y": int(date[:4]), "d": date,
             "t": f"{name_fr} · {set_fr}{abbr}", "s": " · ".join(sub)}
        cards = []
        lang = "en" if cid in EN_ONLY else "fr"
        if lang == "en": g["t"] = f"{c['name_en']} · {c['set_en']}{abbr}"
        cards.append({"id": f"{lang}:{cid}", "g": cid, "l": lang, "n": name_fr if lang == "fr" else c["name_en"],
                      "s": set_fr if lang == "fr" else c["set_en"], "num": num, "r": rar, "y": int(date[:4]),
                      "img": img, "cm": c.get("cm_fr"), "o": 0})
        jp = c.get("cm_jp") or JP_EXTRA.get(cid)
        if jp:
            cards.append({"id": f"ja:{cid}", "g": cid, "l": "ja", "n": POKE_FR[poke] if not cameo else name_fr,
                          "s": f"Version japonaise de {set_fr}", "num": "", "r": rar, "y": int(date[:4]),
                          "img": None, "cm": jp, "o": 1})
        add(g, cards)

for poke, setn, code, num, date, pid, rar in JP_ONLY:
    gid = f"jp-{pid}"
    add({"id": gid, "poke": poke, "cameo": False, "y": int(date[:4]), "d": date,
         "t": f"{POKE_FR[poke]} · {setn} ({code})", "s": f"{'' if num.startswith('No.') else 'n° '}{num} · {date_fr(date)} · exclusivité japonaise"},
        [{"id": f"ja:{gid}", "g": gid, "l": "ja", "n": POKE_FR[poke], "s": setn, "num": num, "r": rar,
          "y": int(date[:4]), "img": local_img(gid), "cm": pid, "o": 0}])

for poke, name, name_ja, setn, date, imgname in CAMEO_JP:
    gid = f"cameo-{re.sub(r'[^a-z0-9]+', '-', name.lower())}"
    add({"id": gid, "poke": poke, "cameo": True, "y": int(date[:4]), "d": date,
         "t": f"{name} · {setn}", "s": f"{date_fr(date)} · caméo : {POKE_FR[poke]} · exclusivité japonaise"},
        [{"id": f"ja:{gid}", "g": gid, "l": "ja", "n": f"{name} ({name_ja})", "s": setn, "num": "", "r": "—",
          "y": int(date[:4]), "img": local_img("ph-" + imgname), "o": 0,
          "np": "Pas vendue sur Cardmarket"}])

GROUPS.sort(key=lambda g: (g["d"], g["t"]))
for i, g in enumerate(GROUPS): g["o"] = i

# prices: scraped language-specific average when available, else the all-language Cardmarket price guide
PRICES = {}
for c in CARDS:
    cm = c.get("cm")
    if not cm: continue
    lang_code = {"fr": 2, "ja": 7}.get(c["l"])
    sc = SCRAPED.get(f"{cm}_{lang_code}") if lang_code else None
    pg = PG.get(cm) or {}
    entry = {"g": [pg.get("avg30"), pg.get("trend"), pg.get("low")]}
    if sc is not None:
        vals = sc["p"][:5]
        entry["s"] = [round(sum(vals) / len(vals), 2) if vals else None, len(vals), sc.get("nall", len(vals))]
    PRICES[f"{c['l']}:{cm}"] = entry
    c["pk"] = f"{c['l']}:{cm}"

ids = [c["id"] for c in CARDS]
dup = {i for i in ids if ids.count(i) > 1}
if dup: sys.exit(f"duplicate ids: {sorted(dup)[:10]}")
pg_date = jload("pg.json").get("createdAt", "")[:10]
scrape_date = (jload("prices_meta.json", {}) or {}).get("date", "")
data = ("const SNAP_DATE = " + json.dumps(pg_date) + ";\n"
        "const SCRAPE_DATE = " + json.dumps(scrape_date) + ";\n"
        "const GROUPS = " + json.dumps(GROUPS, ensure_ascii=False, separators=(",", ":")) + ";\n"
        "const CARDS = " + json.dumps([{k: v for k, v in c.items() if v not in (None, "")} for c in CARDS],
                                      ensure_ascii=False, separators=(",", ":")) + ";\n"
        "const PRICES = " + json.dumps(PRICES, separators=(",", ":")) + ";")
with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f: tpl = f.read()
import base64  # home-screen icon embedded so iOS picks it up with no extra file
with open(os.path.join(SRC, "icon.png"), "rb") as f: icon = "data:image/png;base64," + base64.b64encode(f.read()).decode()
out = tpl.replace("/*__DATA__*/", data).replace("__ICON__", icon)
with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f: f.write(out)
from collections import Counter
print("groups", len(GROUPS), "cards", len(CARDS), dict(Counter(c["l"] for c in CARDS)),
      "scraped", sum(1 for p in PRICES.values() if "s" in p), "/", len(PRICES))
