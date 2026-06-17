"""
Scoring méthode William Higon — Indépendance AM
Source : william_higon_method.md
"""
import urllib3
import requests as std_requests
import yfinance as yf

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_SESSION = std_requests.Session()
_SESSION.verify = False
_SESSION.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})


def _num(v):
    """Convertit en float ou None. yfinance renvoie parfois des chaînes
    ('Infinity', '', etc.) sur certains champs → on sécurise."""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    # NaN / inf ne sont pas exploitables
    if f != f or f in (float("inf"), float("-inf")):
        return None
    return f


def _safe(df, row, col=0):
    """Lit une valeur d'un DataFrame yfinance sans planter."""
    try:
        val = df.loc[row].iloc[col]
        import pandas as pd
        if pd.isna(val):
            return None
        return float(val)
    except Exception:
        return None


def fetch_fundamentals(ticker: str) -> dict | None:
    """Récupère toutes les données fondamentales nécessaires à la méthode Higon."""
    try:
        t = yf.Ticker(ticker, session=_SESSION)
        info = t.info
        bs   = t.balance_sheet    # colonnes = dates (plus récent en premier)
        inc  = t.income_stmt
        cf   = t.cashflow

        name      = info.get("shortName") or ticker
        price     = _num(info.get("currentPrice") or info.get("regularMarketPrice"))
        currency  = info.get("currency", "")
        mkt_cap   = _num(info.get("marketCap"))
        employees = _num(info.get("fullTimeEmployees"))

        # ── Critères principaux ──────────────────────────────────────────
        pe         = _num(info.get("trailingPE"))
        roe_raw    = _num(info.get("returnOnEquity"))
        roe        = roe_raw * 100 if roe_raw is not None else None
        rev_growth = _num(info.get("revenueGrowth"))
        ca_growth  = rev_growth * 100 if rev_growth is not None else None

        # ── BFR / CA (calcul réel depuis bilan) ──────────────────────────
        # BFR = Créances clients + Stocks - Dettes fournisseurs
        receivables = _safe(bs, "Accounts Receivable")
        inventory   = _safe(bs, "Inventory") or 0.0
        payables    = _safe(bs, "Accounts Payable")
        revenue_ann = _safe(inc, "Total Revenue")

        if receivables is not None and payables is not None and revenue_ann and revenue_ann > 0:
            bfr     = receivables + inventory - payables
            bfr_pct = (bfr / revenue_ann) * 100
        else:
            bfr_pct = None

        # ── Détection habillage de bilan ─────────────────────────────────
        # Taux frais fin = Frais financiers / Dette moyenne annuelle
        # Si ce taux >> taux du marché (~4%) → signal habillage
        interest_exp = _safe(inc, "Interest Expense")
        if interest_exp is None:
            interest_exp = _safe(inc, "Interest Expense Non Operating")

        debt_t0 = _safe(bs, "Total Debt", 0)
        debt_t1 = _safe(bs, "Total Debt", 1)
        habillage_taux = None
        if interest_exp and debt_t0 and debt_t1:
            avg_debt = (abs(debt_t0) + abs(debt_t1)) / 2
            if avg_debt > 0:
                # interest_exp est négatif dans yfinance (charge)
                habillage_taux = (abs(interest_exp) / avg_debt) * 100

        # ── CAPEX (signal positif si hausse) ─────────────────────────────
        # Capital Expenditure est négatif dans yfinance (sortie de cash)
        capex_t0 = _safe(cf, "Capital Expenditure", 0)
        capex_t1 = _safe(cf, "Capital Expenditure", 1)
        capex_growth = None
        if capex_t0 is not None and capex_t1 and capex_t1 != 0:
            # Les deux sont négatifs → si capex_t0 < capex_t1, la société investit plus
            capex_growth = ((abs(capex_t0) - abs(capex_t1)) / abs(capex_t1)) * 100

        # ── Cohérence business model ──────────────────────────────────────
        # CA/salarié et Immos nettes/salarié (à comparer aux pairs)
        ca_per_employee   = None
        immo_per_employee = None
        net_ppe = _safe(bs, "Net PPE")
        if employees and employees > 0:
            if revenue_ann:
                ca_per_employee = revenue_ann / employees
            if net_ppe:
                immo_per_employee = net_ppe / employees

        return {
            "ticker":           ticker,
            "name":             name,
            "price":            price,
            "currency":         currency,
            "market_cap":       mkt_cap,
            "employees":        employees,
            # critères principaux
            "pe":               pe,
            "roe":              roe,
            "ca_growth":        ca_growth,
            # BFR
            "bfr_pct":          bfr_pct,
            # habillage bilan
            "habillage_taux":   habillage_taux,
            # CAPEX
            "capex_growth":     capex_growth,
            "capex_abs":        abs(capex_t0) if capex_t0 else None,
            # cohérence business model
            "ca_per_employee":  ca_per_employee,
            "immo_per_employee": immo_per_employee,
        }

    except Exception as e:
        print(f"  [ERREUR] {ticker}: {e}")
        return None


def higon_score(data: dict) -> dict:
    """
    Score 0-100 + statut + détail selon méthode Higon (william_higon_method.md).
    """
    pe           = data.get("pe")
    roe          = data.get("roe")
    ca_growth    = data.get("ca_growth")
    bfr_pct      = data.get("bfr_pct")
    habillage    = data.get("habillage_taux")
    capex_growth = data.get("capex_growth")

    score    = 0
    detail   = {}
    warnings = []
    alerts   = []   # alertes vente (PE 15 / 17 / 20)

    # ── CRITÈRE 1 : PE ────────────────────────────────────────────────────
    # Seuil strict : PE < 12
    # Idéal        : PE entre 5 et 8
    # Vente        : alléger à 15, encore à 17, sortir à 20
    if pe is None:
        detail["PE"] = "N/D"
        pe_ok = False
    elif pe <= 0:
        detail["PE"] = f"INVALIDE ({pe:.1f}) — perte nette"
        pe_ok = False
    elif pe < 8:
        score += 40
        detail["PE"] = f"EXCELLENT ({pe:.1f}x) — zone ideale Higon (5-8x)"
        pe_ok = True
    elif pe < 12:
        score += 30
        detail["PE"] = f"BON ({pe:.1f}x) — dans le filtre"
        pe_ok = True
    elif pe < 15:
        score += 10
        detail["PE"] = f"LIMITE ({pe:.1f}x) — hors filtre strict"
        pe_ok = False
    elif pe < 17:
        score += 0
        detail["PE"] = f"ELEVE ({pe:.1f}x)"
        alerts.append(f"PE={pe:.1f}x >= 15 → ALLEGER 20% de la position")
        pe_ok = False
    elif pe < 20:
        score -= 10
        detail["PE"] = f"TRES ELEVE ({pe:.1f}x)"
        alerts.append(f"PE={pe:.1f}x >= 17 → ALLEGER encore")
        pe_ok = False
    else:
        score -= 20
        detail["PE"] = f"HORS ZONE ({pe:.1f}x)"
        alerts.append(f"PE={pe:.1f}x >= 20 → SORTIE COMPLETE")
        pe_ok = False

    # ── CRITÈRE 2 : ROE ───────────────────────────────────────────────────
    # Seuil strict : ROE > 10%
    # Idéal        : ROE > 15%
    if roe is None:
        detail["ROE"] = "N/D"
        roe_ok = False
    elif roe >= 15:
        score += 30
        detail["ROE"] = f"EXCELLENT ({roe:.1f}%) — ideale Higon"
        roe_ok = True
    elif roe >= 10:
        score += 20
        detail["ROE"] = f"BON ({roe:.1f}%) — dans le filtre"
        roe_ok = True
    elif roe >= 5:
        score += 5
        detail["ROE"] = f"FAIBLE ({roe:.1f}%) — sous le seuil de 10%"
        roe_ok = False
    else:
        score -= 10
        detail["ROE"] = f"INSUFFISANT ({roe:.1f}%) — eliminatoire"
        roe_ok = False

    # ── CRITÈRE 3 : CROISSANCE CA ─────────────────────────────────────────
    # Seuil strict : CA > 0% YoY (filtre les societes en declin structurel)
    if ca_growth is None:
        detail["CA_Growth"] = "N/D"
        ca_ok = False
    elif ca_growth > 10:
        score += 20
        detail["CA_Growth"] = f"FORTE CROISSANCE (+{ca_growth:.1f}%)"
        ca_ok = True
    elif ca_growth > 0:
        score += 15
        detail["CA_Growth"] = f"EN CROISSANCE (+{ca_growth:.1f}%)"
        ca_ok = True
    elif ca_growth > -5:
        score += 0
        detail["CA_Growth"] = f"STABLE ({ca_growth:.1f}%) — limite"
        ca_ok = False
    else:
        score -= 15
        detail["CA_Growth"] = f"EN DECLIN ({ca_growth:.1f}%) — eliminatoire"
        ca_ok = False

    # ── BFR / CA (indicateur complementaire) ──────────────────────────────
    # < 20% excellent, 20-25% acceptable, > 25% alerte, > 40% risque
    if bfr_pct is None:
        detail["BFR/CA"] = "N/D (bilan indisponible)"
    elif bfr_pct < 20:
        score += 10
        detail["BFR/CA"] = f"EXCELLENT ({bfr_pct:.1f}%) — fort pouvoir de negotiation"
    elif bfr_pct < 25:
        score += 5
        detail["BFR/CA"] = f"CORRECT ({bfr_pct:.1f}%)"
    elif bfr_pct < 40:
        score += 0
        detail["BFR/CA"] = f"ELEVE ({bfr_pct:.1f}%) — a creuser"
        warnings.append(f"BFR/CA={bfr_pct:.1f}% > 25% : verifier le poste client et les stocks")
    else:
        score -= 10
        detail["BFR/CA"] = f"TRES ELEVE ({bfr_pct:.1f}%) — risque eleve"
        warnings.append(f"BFR/CA={bfr_pct:.1f}% > 40% : signal d'alerte fort, souvent a eviter")

    # ── DETECTION HABILLAGE DE BILAN ──────────────────────────────────────
    # Si taux frais fin >> taux du marche (~4%) → possible habillage
    # La societe rembourse de la dette temporairement pour paraitre saine au 31/12
    if habillage is None:
        detail["Habillage_Bilan"] = "N/D"
    elif habillage > 8:
        score -= 10
        detail["Habillage_Bilan"] = f"SUSPECT ({habillage:.1f}%) — taux >> marche, possible habillage"
        warnings.append(f"Taux frais fin={habillage:.1f}% >> ~4% : verifier si la dette au 31/12 est representativeAnne entiere")
    elif habillage > 4:
        detail["Habillage_Bilan"] = f"NORMAL ({habillage:.1f}%)"
    else:
        score += 5
        detail["Habillage_Bilan"] = f"SAIN ({habillage:.1f}%) — dette coherente"

    # ── CAPEX (signal investissement) ─────────────────────────────────────
    # Signal positif : CAPEX en hausse = dirigeants qui croient en leur marche
    # Signal negatif : CAPEX nul + dividende eleve = societe en mode vache a lait
    if capex_growth is None:
        detail["CAPEX"] = "N/D"
    elif capex_growth > 10:
        score += 5
        detail["CAPEX"] = f"EN HAUSSE (+{capex_growth:.1f}%) — dirigeants investissent"
    elif capex_growth > -10:
        detail["CAPEX"] = f"STABLE ({capex_growth:+.1f}%)"
    else:
        score -= 5
        detail["CAPEX"] = f"EN BAISSE ({capex_growth:.1f}%) — possible mode vache a lait"
        warnings.append("CAPEX en forte baisse : verifier si la societe redistribue plutot qu'elle n'investit")

    # ── ELIGIBILITE FINALE ────────────────────────────────────────────────
    # Les 3 criteres DOIVENT etre verts simultanement (regle d'or Higon)
    eligible = pe_ok and roe_ok and ca_ok

    if not eligible:
        statut = "HORS FILTRE"
    elif score >= 80:
        statut = "FORT — initier position (3 tranches)"
    elif score >= 60:
        statut = "INTERESSANT — surveiller, attendre confirmation"
    else:
        statut = "LIMITE — ne pas initier"

    return {
        "score":    score,
        "eligible": eligible,
        "statut":   statut,
        "detail":   detail,
        "warnings": warnings,
        "alerts":   alerts,   # alertes vente PE 15/17/20
    }
