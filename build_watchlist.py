"""
Construction de la watchlist small & mid caps France + Europe
Sources :
  - France  : CAC Mid 60 + CAC Small (liste curatee, verifiee)
  - Europe  : MDAX (DE), AMX/AEX (NL), FTSE MIB (IT), IBEX (ES) via Wikipedia
Filtre final : market_cap < 10 Mds EUR via Yahoo Finance
"""
import io
import time
import urllib3
import requests
import pandas as pd
import yfinance as yf

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_S = requests.Session()
_S.verify = False
_S.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})


# ── 1. FRANCE ────────────────────────────────────────────────────────────────
# CAC Mid 60 (marche cap ~500M - 5Mds EUR)
CAC_MID60 = [
    "AC.PA",     # Accor
    "AF.PA",     # Air France-KLM
    "ALO.PA",    # Alstom
    "AMUN.PA",   # Amundi
    "BEN.PA",    # Beneteau
    "BIM.PA",    # bioMerieux
    "BOL.PA",    # Bollore
    "BVI.PA",    # Bureau Veritas
    "CRI.PA",    # Chargeurs
    "CLARI.PA",  # Clariane (ex-Korian)
    "COFA.PA",   # Coface
    "COV.PA",    # Covivio
    "ELIOR.PA",  # Elior
    "ERA.PA",    # Eramet
    "RF.PA",     # Eurazeo
    "FNAC.PA",   # Fnac Darty
    "GTT.PA",    # Gaztransport & Technigaz
    "GET.PA",    # Getlink
    "GLO.PA",    # GL Events
    "GBT.PA",    # Guerbet
    "ICAD.PA",   # Icade
    "NK.PA",     # Imerys
    "KOF.PA",    # Kaufman & Broad
    "LACR.PA",   # Lacroix Group
    "MMB.PA",    # Lagardere
    "LSS.PA",    # Lectra
    "MDM.PA",    # Maisons du Monde
    "MMT.PA",    # M6 (Metropole Television)
    "MRN.PA",    # Mersen
    "NEX.PA",    # Nexans
    "NXI.PA",    # Nexity
    "POM.PA",    # OPmobility (ex-Plastic Omnium)
    "RCO.PA",    # Remy Cointreau
    "ROTH.PA",   # Rothschild & Co
    "RUI.PA",    # Rubis
    "DIM.PA",    # Sartorius Stedim Biotech
    "SAVE.PA",   # Savencia
    "SCR.PA",    # SCOR
    "SK.PA",     # SEB
    "SPIE.PA",   # SPIE
    "TFFP.PA",   # TFF Group
    "THEP.PA",   # Thermador Groupe
    "TRI.PA",    # Trigano
    "VIRP.PA",   # Virbac
    "WLN.PA",    # Worldline
    "SESG.PA",   # SES-imagotag
    "EMEIS.PA",  # Emeis (ex-Orpea)
    "VIEL.PA",   # Viel & Cie
    "FGR.PA",    # Eiffage
    "TEP.PA",    # Teleperformance
    "EN.PA",     # Bouygues
    "RXL.PA",    # Rexel
    "MF.PA",     # Mercialys
    "SOP.PA",    # Sopra Steria
    "FII.PA",    # Financiere de l'Odet
    "ABCA.PA",   # ABC Arbitrage
    "IDIP.PA",   # IDI
    "SCo.PA",    # Societe de la Tour Eiffel
]

# CAC Small (market cap ~100M - 1Md EUR) — tickers verifies
CAC_SMALL = [
    # Services IT / Tech
    "SII.PA",    # SII (conseil informatique)
    "SQLI.PA",   # SQLI (agence digitale)
    "ATEME.PA",  # Ateme (video encoding)
    "ALBI.PA",   # Bilendi (etudes marche)
    "ALWIT.PA",  # Witbe (monitoring video)
    "MGI.PA",    # MGI Digital Technology (imprimerie)
    "SFT.PA",    # Soft Computing -> SFTW.PA
    "NETG.PA",   # NetGem (IPTV)
    "IPS.PA",    # Ipsos (etudes)
    "IDL.PA",    # ID Logistics (logistique)
    # Industrie / Manufacturing
    "PREC.PA",   # Precia Molen (instruments pesage)
    "DPAM.PA",   # Delfingen (gaines cables)
    "HEX.PA",    # Hexaom (maisons individuelles)
    "MALT.PA",   # Malteries Franco-Belges
    "AURS.PA",   # Aures Technologies (terminaux caisse)
    "ORAP.PA",   # Orapi (produits hygiene pro)
    "BIG.PA",    # BigBen Interactive (peripheriques gaming)
    # Sante / Pharma
    "BOI.PA",    # Boiron (homeopathie)
    "GENFIT.PA", # Genfit (biotech hepatologie)
    "ABIO.PA",   # Albioma (energie biomasse)
    # Immobilier / Finance
    "ACAN.PA",   # Acanthe Developpement (immobilier)
    "SMCP.PA",   # SMCP (mode — Sandro, Maje, Claudie)
    "SFCA.PA",   # Ste Francaise Casinos
    "ELEC.PA",   # Electricite de Strasbourg
    # Media / Distribution
    "ALBLD.PA",  # Bastide le Confort Medical
    "ALTUR.PA",  # Turenne Investissement
    "MLNAM.PA",  # Namr
    "ASY.PA",    # AST Groupe (batiment)
    "GL.PA",     # GL events (deja GLO.PA dans mid — verif)
    "MLAFP.PA",  # AFP
    "OCRI.PA",   # Oc'Via
    "CARP.PA",   # Carpinienne de Participations
    "OEIMF.PA",  # Oeneo (bouchons liege)
    "OENEO.PA",  # Oeneo
    "LGTH.PA",   # Logista (distribution tabac)
]

FRANCE = sorted(set(CAC_MID60 + CAC_SMALL))


# ── 2. EUROPE — Wikipedia ────────────────────────────────────────────────────

def wiki_tickers(page: str, default_suffix: str) -> list[str]:
    """Extrait les tickers d'un tableau Wikipedia."""
    try:
        r = _S.get(f"https://en.wikipedia.org/wiki/{page}", timeout=15)
        if r.status_code != 200:
            return []
        tables = pd.read_html(io.StringIO(r.text), flavor="lxml")
        best = []
        for t in tables:
            cols = [str(c).lower() for c in t.columns]
            for i, c in enumerate(cols):
                if any(k in c for k in ["ticker", "symbol", "abbr"]):
                    raw = t.iloc[:, i].dropna().astype(str).tolist()
                    clean = [
                        x.strip().split()[0]
                        for x in raw
                        if 1 < len(x.strip()) <= 12
                        and x.strip() not in ("nan", "Ticker", "Symbol", "Abbr")
                        and not x.strip()[0].isdigit()
                    ]
                    if len(clean) > len(best):
                        best = clean
        result = []
        for t in best:
            if "." not in t:
                result.append(t + default_suffix)
            else:
                result.append(t)   # ticker deja avec suffixe (ex: ABN.AS)
        return result
    except Exception as e:
        print(f"  [!] Wikipedia {page}: {e}")
        return []


EUROPE_SOURCES = [
    # (page Wikipedia, suffixe Yahoo Finance, description)
    ("MDAX",                 ".DE",  "Allemagne mid cap (50)"),
    ("SDAX",                 ".DE",  "Allemagne small cap (70)"),
    ("AMX_index",            ".AS",  "Pays-Bas mid cap (25)"),
    ("AEX_index",            ".AS",  "Pays-Bas large — filtre ensuite"),
    ("AScX_(stock_index)",   ".AS",  "Pays-Bas small cap"),
    ("BEL_Mid",              ".BR",  "Belgique mid cap"),
    ("BEL_Small",            ".BR",  "Belgique small cap"),
    ("IBEX_35",              ".MC",  "Espagne (filtre market cap)"),
    ("FTSE_MIB",             ".MI",  "Italie (filtre market cap)"),
    ("OMX_Stockholm_30",     ".ST",  "Suede (filtre market cap)"),
    ("PSI_20",               ".LS",  "Portugal"),
]


def build_europe() -> list[str]:
    all_tickers = []
    for page, suffix, desc in EUROPE_SOURCES:
        tickers = wiki_tickers(page, suffix)
        print(f"  {desc:<35}: {len(tickers):>3} tickers")
        all_tickers.extend(tickers)
        time.sleep(0.5)
    return sorted(set(all_tickers))


# ── 3. FILTRAGE market cap ───────────────────────────────────────────────────

_YF_S = requests.Session()
_YF_S.verify = False
_YF_S.headers.update({"User-Agent": "Mozilla/5.0"})


def filter_by_market_cap(tickers: list[str], max_cap: float = 10e9) -> list[str]:
    """Conserve les tickers avec market_cap < max_cap (en EUR)."""
    ok, skipped, errors = [], [], []
    total = len(tickers)
    for idx, ticker in enumerate(tickers, 1):
        print(f"  [{idx:>3}/{total}] {ticker:<15}", end=" ", flush=True)
        try:
            info = yf.Ticker(ticker, session=_YF_S).info
            cap = info.get("marketCap")
            name = (info.get("shortName") or "")[:25]
            if cap is None:
                ok.append(ticker)
                print(f"cap=N/D  → GARDE   {name}")
            elif cap < max_cap:
                ok.append(ticker)
                print(f"cap={cap/1e9:>5.1f}Mds → OK     {name}")
            else:
                skipped.append(ticker)
                print(f"cap={cap/1e9:>5.1f}Mds → SKIP   {name} (large cap)")
        except Exception as e:
            errors.append(ticker)
            print(f"ERREUR: {str(e)[:35]}")
        if idx % 10 == 0:
            time.sleep(2)   # pause tous les 10 pour eviter rate limit

    print(f"\n  Retenus: {len(ok)} | Skipped (large): {len(skipped)} | Erreurs: {len(errors)}")
    return ok


# ── 4. MAIN ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  CONSTRUCTION WATCHLIST SMALL & MID CAPS EUROPE")
    print("  Critere Higon : univers France + Europe, market cap < 10Mds")
    print("=" * 65)

    print(f"\n[1/4] France : {len(FRANCE)} tickers (CAC Mid 60 + CAC Small)")

    print("\n[2/4] Europe (Wikipedia)...")
    europe = build_europe()
    print(f"       Total Europe hors France : {len(europe)} tickers")

    all_raw = sorted(set(FRANCE + europe))
    print(f"\n[3/4] Merge : {len(all_raw)} tickers bruts au total")

    print(f"\n[4/4] Filtrage market cap < 10 Mds EUR...")
    print("      (appuie Ctrl+C pour sauter le filtre et garder tout)\n")
    try:
        final = filter_by_market_cap(all_raw, max_cap=10e9)
    except KeyboardInterrupt:
        print("\n  Filtre saute — liste brute conservee.")
        final = all_raw

    # Sauvegarde
    with open("watchlist_generated.txt", "w", encoding="utf-8") as f:
        for t in final:
            f.write(t + "\n")

    print(f"\n{'='*65}")
    print(f"  WATCHLIST FINALE : {len(final)} actions")
    print(f"  Fichier sauvegarde : watchlist_generated.txt")
    print(f"{'='*65}")
    print("\nColle dans config.py :")
    print("WATCHLIST = [")
    for t in final:
        print(f'    "{t}",')
    print("]")
