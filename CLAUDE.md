# Surveillance Higgons — guide du projet

Outil de surveillance boursière appliquant la **méthode William Higgons**
(Indépendance AM) à un univers de small/mid caps France + Europe, avec
notifications push sur téléphone et un **simulateur de portefeuille en points**
(paper trading).

## Vue d'ensemble

```
                  ┌─────────────────────────────────────┐
                  │   GitHub (source de vérité, versionné) │
                  │  • signals.json    (signaux d'achat)   │
                  │  • alert_state.json (état des alertes)  │
                  │  • portfolio.json  (positions en points)│
                  └──────────┬───────────────┬────────────┘
        git pull/push        │               │   lecture seule
        ┌───────────────────┘               └──────────────────┐
        ▼                                                        ▼
┌──────────────────────┐                      ┌──────────────────────────┐
│  SITE LOCAL (Flask)   │                      │ GitHub Actions — 18h Paris │
│  app.py               │  écrit portfolio.json│ surveillance.py --scan     │
│  • dashboard points   │ ───────────────────► │ • scanne ~314 actions      │
│  • signaux + achat    │                      │ • écrit signals.json       │
│  • clôture (vente)    │ ◄─────────────────── │ • lit portfolio.json        │
│  • historique         │  lit signals.json    │ • résumé quotidien (1 notif)│
└──────────────────────┘                      │ • alertes vente (positions) │
                                               └──────────────────────────┘
```

**Règle anti-conflit git** : le site local ne pousse QUE `portfolio.json` ;
GitHub Actions ne pousse QUE `signals.json` + `alert_state.json`. Fichiers
disjoints → aucun conflit de merge.

## La méthode Higgons (implémentée dans `scorer.py`)

Référence détaillée : [william_higon_method.md](william_higon_method.md).

### 3 critères éliminatoires (les 3 doivent être verts → `eligible`)
- **PE < 12** (idéal 5–8) — seuils dans `config.py`
- **ROE > 10 %** (idéal > 15 %)
- **Croissance du CA > 0 %** (YoY)

### Score 0–100 (`higon_score`), plafonné à 100
| Critère | Points |
|---|---|
| PE < 8 / < 12 | +40 / +30 |
| ROE ≥ 15 % / ≥ 10 % | +30 / +20 |
| CA > 10 % / > 0 % | +20 / +15 |
| BFR/CA < 20 % | +10 |
| Habillage de bilan sain | +5 |
| CAPEX en hausse | +5 |
*(PE/ROE/CA hors zone → malus négatifs ; voir le code.)*

### Indicateurs complémentaires (calculés sur données réelles)
- **BFR/CA** = (Créances + Stocks − Dettes fournisseurs) / CA. Alerte > 25 %.
- **Habillage de bilan** = frais financiers / dette moyenne. Suspect > 8 %
  (la société pourrait rembourser sa dette juste au 31/12 pour paraître saine).
- **CAPEX** : hausse = dirigeants qui investissent (signal positif).

### Signaux de VENTE (paliers PE)
- PE ≥ 15 → alléger 20 %  ·  PE ≥ 17 → alléger encore  ·  PE ≥ 20 → sortie complète.

### Détection des pièges (`classify_traps`) — drapeaux "à vérifier"
La méthode PE/ROE/BFR s'applique mal à certains profils → on les **marque** sans
les exclure (l'humain tranche) :
- **FINANCIERE** — banques/assureurs (secteur "Financial Services") : ratios non comparables.
- **HOLDING** — détecté par le nom (Investor AB, Industrivärden, Prosus, Exor, Wendel…) :
  PE/ROE/croissance faussés par la valeur des participations. *Note : "SGPS" est une
  forme juridique portugaise courante, PAS un critère de holding.*
- **CYCLIQUE** — matériaux/énergie/airlines/auto : bénéfice possiblement au pic, PE bas trompeur.
- **PIC POSSIBLE** — PE < 4 ET ROE > 40 % : capitaux propres minuscules (ex. Air France).

## Logique des notifications (`surveillance.py` + `notifier.py`)

Le scan cloud est **one-shot** (le process redémarre à chaque run), donc l'état
qui doit survivre entre les jours est persisté dans **`alert_state.json`**
(versionné). Cela évite de re-spammer les mêmes alertes chaque soir.

- **Résumé quotidien** (`notify_digest`) : UNE seule notif/jour. Compte total
  des signaux, nombre "sans drapeau", **nouveaux** (= absents du `signals.json`
  de la veille), et le top par score.
- **Alertes vente** (`notify_sell_alert`) : uniquement sur les **positions
  détenues** (`portfolio.held_tickers()`), et seulement au **changement de
  palier** (mémorisé dans `alert_state.json["sell"]`).
- **Avertissements** (`notify_warning`) : uniquement positions détenues, au
  changement (`alert_state.json["warn"]`).

Canal : **ntfy.sh**, topic dans `config.py` (`NTFY_TOPIC`). Pas de compte requis ;
s'abonner au topic dans l'app ntfy sur le téléphone.

## Le portefeuille en points (`portfolio.py`)

Paper trading : départ **1000 points**.
- Ouvrir une position = investir N points au prix d'entrée → on détient
  `parts = N / prix_entree`.
- Valeur live = `parts × cours_actuel` (cours réel via `get_price`, léger : `fast_info`).
- Clôturer = on récupère `parts × prix_sortie` en cash.
- Rendement = `(valeur_totale / 1000 − 1) × 100`.
Source de vérité : `portfolio.json` (`cash_points`, `positions`, `historique`, `next_id`).

## Fichiers

| Fichier | Rôle |
|---|---|
| `config.py` | Watchlist (314 tickers), seuils Higgons, portefeuille manuel optionnel, ntfy |
| `scorer.py` | `fetch_fundamentals` (yfinance), `higon_score`, `classify_traps` |
| `surveillance.py` | Scan cloud `--scan` : produit signals.json + alert_state.json, notifs |
| `notifier.py` | Notifs ntfy : digest, vente, avertissement, test |
| `portfolio.py` | Logique points : open/close/enrich, prix temps réel |
| `app.py` + `templates/index.html` | Site local Flask (dashboard, achat/vente, historique) |
| `git_sync.py` | Sync portfolio.json ↔ GitHub depuis le site local |
| `build_watchlist.py` | (Re)génère la watchlist France + Europe (CAC + Wikipedia) |
| `.github/workflows/surveillance.yml` | Cron 18h Paris (16h+17h UTC pour DST), commit des résultats |

### Fichiers d'état (versionnés, ne pas mettre en .gitignore)
`signals.json`, `alert_state.json`, `portfolio.json` — ce sont le mécanisme de
synchronisation entre le cloud et le site local.

## Lancer

- **Site local** : `lancer_site.bat` → http://127.0.0.1:5000
- **Scan manuel (cloud)** : onglet Actions GitHub → "Run workflow" (branche `main`).
  ⚠️ Ne pas faire "Re-run jobs" (rejoue l'ancien commit) — toujours "Run workflow".
- **Scan local de test** : `python -X utf8 surveillance.py --scan`

## Conventions / pièges connus

- yfinance peut renvoyer des champs en **chaîne** ("Infinity") → toujours passer
  par `scorer._num()` avant comparaison numérique.
- SSL Windows : sessions `requests` avec `verify=False` (déjà fait partout).
- Encodage : lancer avec `python -X utf8` (Windows) ; `PYTHONIOENCODING=utf-8` côté CI.
- Sur GitHub Actions, l'IP datacenter n'est PAS bloquée par Yahoo (testé OK).
- Le scan complet dure ~5 min sur le runner.
