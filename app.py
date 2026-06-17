"""
Site local — simulateur de portefeuille Higon (paper trading en POINTS).
Lancement : python app.py  →  http://127.0.0.1:5000

- Affiche les signaux d'achat (signals.json produit par le scan GitHub).
- Tu ouvres une position (cours réel pré-rempli, modifiable) en investissant des points.
- Les positions ouvertes sont surveillées pour la vente par GitHub Actions (alerte tel).
- Le rendement est calculé sur les vrais cours.
"""
import json
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

import portfolio
import git_sync

app = Flask(__name__)
app.secret_key = "higon-local-paper-trading"

SIGNALS_FILE = Path(__file__).parent / "signals.json"


def load_signals() -> dict:
    if SIGNALS_FILE.exists():
        try:
            with open(SIGNALS_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"date": None, "signaux": []}


@app.route("/")
def index():
    # Récupère les derniers signaux du cloud (best effort, silencieux si pas de remote)
    git_sync.pull()
    data = portfolio.enrich()
    signals = load_signals()
    held = {p["ticker"] for p in data["positions"]}
    return render_template("index.html", d=data, signals=signals, held=held)


@app.route("/prix/<ticker>")
def prix(ticker):
    return jsonify({"ticker": ticker, "prix": portfolio.get_price(ticker)})


@app.route("/ouvrir", methods=["POST"])
def ouvrir():
    try:
        ticker = request.form["ticker"].strip().upper()
        nom    = request.form.get("nom", ticker).strip() or ticker
        prix   = float(request.form["prix_entree"].replace(",", "."))
        points = float(request.form["points"].replace(",", "."))
        score  = request.form.get("score") or None
        score  = int(score) if score not in (None, "", "None") else None
        pos = portfolio.open_position(ticker, nom, prix, points, score)
        ok, out = git_sync.push(f"Ouverture position {ticker} ({points:.0f} pts)")
        if ok:
            flash(f"Position ouverte : {points:.0f} pts sur {ticker} @ {prix}. Synchronisé GitHub.", "ok")
        else:
            flash(f"Position ouverte localement sur {ticker}. Sync GitHub échouée : {out[:120]}", "warn")
    except Exception as e:
        flash(f"Erreur ouverture : {e}", "error")
    return redirect(url_for("index"))


@app.route("/fermer", methods=["POST"])
def fermer():
    try:
        pos_id = int(request.form["pos_id"])
        prix   = float(request.form["prix_sortie"].replace(",", "."))
        raison = request.form.get("raison", "manuelle").strip() or "manuelle"
        trade  = portfolio.close_position(pos_id, prix, raison)
        ok, out = git_sync.push(f"Clôture position {trade['ticker']} (PV {trade['plus_value_pts']:+.1f} pts)")
        signe = "+" if trade["plus_value_pts"] >= 0 else ""
        msg = f"Position {trade['ticker']} clôturée : {signe}{trade['plus_value_pts']:.1f} pts ({signe}{trade['plus_value_pct']:.1f}%)."
        flash(msg + (" Synchronisé GitHub." if ok else f" Sync échouée : {out[:100]}"),
              "ok" if ok else "warn")
    except Exception as e:
        flash(f"Erreur clôture : {e}", "error")
    return redirect(url_for("index"))


@app.route("/sync", methods=["POST"])
def sync():
    ok1, _ = git_sync.pull()
    ok2, out = git_sync.push("Synchronisation manuelle")
    flash("Synchronisation effectuée." if (ok1 and ok2) else f"Sync partielle : {out[:150]}",
          "ok" if (ok1 and ok2) else "warn")
    return redirect(url_for("index"))


if __name__ == "__main__":
    print("=" * 60)
    print("  SITE LOCAL — Portefeuille Higon (points)")
    print("  Ouvre ton navigateur sur : http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)
