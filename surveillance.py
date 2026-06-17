#!/usr/bin/env python3
"""
Surveillance marche — Methode William Higon (Independance AM)
Scan automatique toutes les heures en heures de bourse (9h-17h30 Paris, lun-ven).
Notifs push via app ntfy (gratuit).
"""
import sys
import time
import schedule
import datetime
import pytz

from config import WATCHLIST, SCAN_INTERVAL_MINUTES, SCAN_TIME, SCORE_NOTIF_MIN, NTFY_TOPIC
from scorer import fetch_fundamentals, higon_score
from notifier import notify_signal, notify_sell_alert, notify_warning, notify_test

PARIS_TZ = pytz.timezone("Europe/Paris")

# Anti-doublon : on memorise le dernier statut envoye par ticker
_last_signal:    dict[str, str]   = {}   # ticker -> statut
_last_sell_lvl:  dict[str, str]   = {}   # ticker -> "15"/"17"/"20"
_last_warn_hash: dict[str, str]   = {}   # ticker -> hash des warnings


def is_market_hours() -> bool:
    now = datetime.datetime.now(PARIS_TZ)
    if now.weekday() >= 5:
        return False
    o = now.replace(hour=9,  minute=0,  second=0, microsecond=0)
    c = now.replace(hour=17, minute=30, second=0, microsecond=0)
    return o <= now <= c


def _sell_level(pe: float) -> str | None:
    if pe >= 20:  return "20"
    if pe >= 17:  return "17"
    if pe >= 15:  return "15"
    return None


def scan_all():
    print(f"\n{'='*65}")
    print(f"[{_now()}] SCAN — {len(WATCHLIST)} actions")
    print(f"{'='*65}")

    for ticker in WATCHLIST:
        print(f"\n  > {ticker}")
        data = fetch_fundamentals(ticker)
        if data is None:
            continue

        result = higon_score(data)
        score  = result["score"]
        statut = result["statut"]
        elig   = result["eligible"]
        pe     = data.get("pe")

        # Affichage console complet
        def f(v, s=""): return f"{v:.1f}{s}" if v is not None else "N/D"
        print(f"     {data['name'][:38]:<38} | PE={f(pe,'x'):>7} | ROE={f(data.get('roe'),'%'):>7} | CA={f(data.get('ca_growth'),'%'):>7} | Score={score:>3}")
        print(f"     BFR/CA={f(data.get('bfr_pct'),'%'):>8} | Habillage={f(data.get('habillage_taux'),'%'):>8} | CAPEX={f(data.get('capex_growth'),'%'):>7}")
        print(f"     --> {statut}")
        for w in result.get("warnings", []):
            print(f"     [!] {w}")
        for a in result.get("alerts", []):
            print(f"     [VENTE] {a}")

        # ── Notif signal achat ────────────────────────────────────────────
        if elig and score >= SCORE_NOTIF_MIN:
            if _last_signal.get(ticker) != statut:
                notify_signal(data, result)
                _last_signal[ticker] = statut
        elif ticker in _last_signal and not elig:
            del _last_signal[ticker]   # reset si l'action n'est plus eligible

        # ── Notif alertes vente (3 paliers : 15 / 17 / 20) ──────────────
        if pe is not None:
            lvl = _sell_level(pe)
            if lvl and _last_sell_lvl.get(ticker) != lvl:
                notify_sell_alert(data, pe)
                _last_sell_lvl[ticker] = lvl
            elif not lvl and ticker in _last_sell_lvl:
                del _last_sell_lvl[ticker]   # PE redescend sous 15 → reset

        # ── Notif warnings secondaires (BFR, habillage, CAPEX) ───────────
        warnings = result.get("warnings", [])
        if warnings:
            h = "|".join(sorted(warnings))
            if _last_warn_hash.get(ticker) != h:
                notify_warning(data, warnings)
                _last_warn_hash[ticker] = h

    print(f"\n[{_now()}] Scan termine. Prochain scan demain a {SCAN_TIME}.\n")


def _now() -> str:
    return datetime.datetime.now(PARIS_TZ).strftime("%d/%m/%Y %H:%M")


def main():
    print("=" * 65)
    print("  SURVEILLANCE MARCHE — METHODE WILLIAM HIGON")
    print("=" * 65)
    print(f"  Watchlist  : {len(WATCHLIST)} actions")
    print(f"  Scan       : 1x/jour a {SCAN_TIME} (apres cloture marches)")
    print(f"  Score mini : {SCORE_NOTIF_MIN}/100 pour signal achat")
    print(f"  Notifs     : app ntfy → abonne-toi au topic '{NTFY_TOPIC}'")
    print(f"  Paliers PE : 15 alleger / 17 alleger encore / 20 sortir")
    print()

    print("  Test notification ntfy...")
    if notify_test():
        print("  OK — notification test envoyee sur ton telephone !\n")
    else:
        print("  ECHEC — verifie ta connexion ou le topic ntfy\n")

    scan_all()

    schedule.every().day.at(SCAN_TIME).do(scan_all)
    print(f"Prochain scan automatique chaque jour a {SCAN_TIME}\n")

    print("En ecoute... (Ctrl+C pour arreter)\n")
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nArret de la surveillance.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scan":
        scan_all()
    else:
        main()
