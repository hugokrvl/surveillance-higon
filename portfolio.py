"""
Couche données du portefeuille en POINTS (paper trading).
Source de vérité unique : portfolio.json (versionné sur GitHub).

Logique des points :
  - On démarre avec POINTS_DEPART points (1000 par défaut).
  - Ouvrir une position = investir N points au prix d'entrée.
      -> on détient parts = N / prix_entree
  - Valeur live d'une position = parts * cours_actuel (données réelles Yahoo).
  - Clôturer = on récupère parts * prix_sortie en cash.
  - Rendement = (valeur_totale / POINTS_DEPART - 1) * 100
"""
import json
import datetime
from pathlib import Path

import urllib3
import requests
import yfinance as yf

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PORTFOLIO_FILE = Path(__file__).parent / "portfolio.json"
POINTS_DEPART  = 1000.0

_S = requests.Session()
_S.verify = False
_S.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})


# ── Persistance ────────────────────────────────────────────────────────────

def _default() -> dict:
    return {
        "points_depart": POINTS_DEPART,
        "cash_points":   POINTS_DEPART,
        "positions":     [],   # positions ouvertes
        "historique":    [],   # trades clôturés
        "next_id":       1,
    }


def load() -> dict:
    if PORTFOLIO_FILE.exists():
        try:
            with open(PORTFOLIO_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    p = _default()
    save(p)
    return p


def save(p: dict) -> None:
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)


# ── Prix temps réel (léger) ──────────────────────────────────────────────────

def get_price(ticker: str) -> float | None:
    """Cours actuel — utilise fast_info (léger) avec repli sur info."""
    try:
        t = yf.Ticker(ticker, session=_S)
        try:
            px = t.fast_info.get("last_price") or t.fast_info.get("lastPrice")
            if px:
                return float(px)
        except Exception:
            pass
        info = t.info
        px = info.get("currentPrice") or info.get("regularMarketPrice")
        return float(px) if px else None
    except Exception as e:
        print(f"  [PRIX ERREUR] {ticker}: {e}")
        return None


# ── Opérations ────────────────────────────────────────────────────────────

def held_tickers() -> set[str]:
    """Tickers actuellement détenus (positions ouvertes)."""
    return {pos["ticker"] for pos in load().get("positions", [])}


def open_position(ticker: str, nom: str, prix_entree: float,
                  points: float, score: int | None = None) -> dict:
    p = load()
    if points <= 0:
        raise ValueError("Le nombre de points doit être positif.")
    if points > p["cash_points"] + 1e-9:
        raise ValueError(f"Points insuffisants : {points:.1f} demandés, "
                         f"{p['cash_points']:.1f} disponibles.")
    if prix_entree <= 0:
        raise ValueError("Le prix d'entrée doit être positif.")

    pos = {
        "id":              p["next_id"],
        "ticker":          ticker,
        "nom":             nom,
        "prix_entree":     round(prix_entree, 4),
        "points_investis": round(points, 2),
        "parts":           round(points / prix_entree, 6),
        "date_entree":     datetime.date.today().isoformat(),
        "score_entree":    score,
    }
    p["cash_points"] = round(p["cash_points"] - points, 2)
    p["positions"].append(pos)
    p["next_id"] += 1
    save(p)
    return pos


def close_position(pos_id: int, prix_sortie: float, raison: str = "manuelle") -> dict:
    p = load()
    pos = next((x for x in p["positions"] if x["id"] == pos_id), None)
    if pos is None:
        raise ValueError(f"Position {pos_id} introuvable.")
    if prix_sortie <= 0:
        raise ValueError("Le prix de sortie doit être positif.")

    points_recuperes = pos["parts"] * prix_sortie
    plus_value       = points_recuperes - pos["points_investis"]
    pv_pct           = (prix_sortie / pos["prix_entree"] - 1) * 100

    trade = {
        **pos,
        "prix_sortie":      round(prix_sortie, 4),
        "points_recuperes": round(points_recuperes, 2),
        "plus_value_pts":   round(plus_value, 2),
        "plus_value_pct":   round(pv_pct, 2),
        "date_sortie":      datetime.date.today().isoformat(),
        "raison_sortie":    raison,
    }
    p["cash_points"] = round(p["cash_points"] + points_recuperes, 2)
    p["positions"]   = [x for x in p["positions"] if x["id"] != pos_id]
    p["historique"].append(trade)
    save(p)
    return trade


# ── Calculs d'affichage ──────────────────────────────────────────────────────

def enrich(p: dict | None = None, prix_cache: dict | None = None) -> dict:
    """Renvoie un dico complet avec valeurs live pour le dashboard."""
    if p is None:
        p = load()
    prix_cache = prix_cache or {}

    positions = []
    valeur_positions = 0.0
    for pos in p["positions"]:
        cours = prix_cache.get(pos["ticker"]) or get_price(pos["ticker"])
        if cours:
            valeur = pos["parts"] * cours
            pv     = valeur - pos["points_investis"]
            pv_pct = (cours / pos["prix_entree"] - 1) * 100
        else:
            valeur = pv = pv_pct = None
        positions.append({
            **pos,
            "cours_actuel": round(cours, 4) if cours else None,
            "valeur_pts":   round(valeur, 2) if valeur is not None else None,
            "plus_value_pts": round(pv, 2) if pv is not None else None,
            "plus_value_pct": round(pv_pct, 2) if pv_pct is not None else None,
        })
        valeur_positions += valeur if valeur is not None else pos["points_investis"]

    cash  = p["cash_points"]
    total = cash + valeur_positions
    depart = p["points_depart"]
    rendement_pct = (total / depart - 1) * 100 if depart else 0.0

    pv_realisee = sum(t["plus_value_pts"] for t in p["historique"])

    return {
        "points_depart":   depart,
        "cash_points":     round(cash, 2),
        "valeur_positions": round(valeur_positions, 2),
        "valeur_totale":   round(total, 2),
        "rendement_pct":   round(rendement_pct, 2),
        "pv_realisee_pts": round(pv_realisee, 2),
        "positions":       positions,
        "historique":      list(reversed(p["historique"])),
        "nb_positions":    len(positions),
    }
