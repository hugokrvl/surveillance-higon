"""
Notifications push via ntfy.sh (gratuit, app dispo Android/iOS).
"""
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from config import NTFY_SERVER, NTFY_TOPIC


def _post(title: str, body: str, priority: str = "default", tags: list[str] | None = None) -> bool:
    headers = {
        "Title":    title.encode("utf-8"),
        "Priority": priority,
    }
    if tags:
        headers["Tags"] = ",".join(tags)
    try:
        r = requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data=body.encode("utf-8"),
            headers=headers,
            timeout=10,
            verify=False,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"  [NOTIF ERREUR] {e}")
        return False


def notify_signal(data: dict, result: dict):
    """Alerte achat : les 3 criteres Higon sont verts."""
    ticker = data["ticker"]
    name   = data["name"]
    score  = result["score"]
    statut = result["statut"]

    def _fmt(v, suffix=""):
        return f"{v:.1f}{suffix}" if v is not None else "N/D"

    lines = [
        f"{name}",
        f"Prix : {_fmt(data.get('price'))} {data.get('currency','')}",
        f"PE   : {_fmt(data.get('pe'), 'x')}  |  ROE : {_fmt(data.get('roe'), '%')}  |  CA : {_fmt(data.get('ca_growth'), '%')}",
    ]
    if data.get("bfr_pct") is not None:
        lines.append(f"BFR/CA : {_fmt(data.get('bfr_pct'), '%')}")
    if result.get("warnings"):
        lines.append("⚠ " + " | ".join(result["warnings"][:2]))
    lines.append(statut)

    priority = "high" if score >= 80 else "default"
    tags = ["chart_increasing", "moneybag"] if score >= 80 else ["chart_increasing"]

    sent = _post(f"SIGNAL {ticker} — Score {score}/100", "\n".join(lines), priority, tags)
    if sent:
        print(f"  [NOTIF] Signal achat envoye pour {ticker} (score={score})")


def notify_sell_alert(data: dict, pe: float):
    """Alertes vente selon les paliers PE 15 / 17 / 20 de la methode Higon."""
    ticker = data["ticker"]
    name   = data["name"]

    if pe >= 20:
        title    = f"SORTIE COMPLETE {ticker} — PE={pe:.1f}x"
        body     = f"{name}\nPE={pe:.1f}x >= 20 → sortie complete selon Higon"
        tags     = ["rotating_light", "chart_decreasing"]
        priority = "urgent"
    elif pe >= 17:
        title    = f"ALLEGER {ticker} — PE={pe:.1f}x"
        body     = f"{name}\nPE={pe:.1f}x >= 17 → alleger encore"
        tags     = ["warning", "chart_decreasing"]
        priority = "high"
    else:  # pe >= 15
        title    = f"DEBUT ALLEGER {ticker} — PE={pe:.1f}x"
        body     = f"{name}\nPE={pe:.1f}x >= 15 → alleger 20% de la position"
        tags     = ["warning"]
        priority = "high"

    sent = _post(title, body, priority, tags)
    if sent:
        print(f"  [NOTIF] Alerte vente envoyee pour {ticker} (PE={pe:.1f}x)")


def notify_warning(data: dict, warnings: list[str]):
    """Alerte sur indicateurs secondaires (BFR eleve, habillage bilan, CAPEX en baisse)."""
    ticker = data["ticker"]
    name   = data["name"]
    body   = f"{name}\n" + "\n".join(f"- {w}" for w in warnings)
    sent = _post(f"ATTENTION {ticker} — indicateurs secondaires", body, priority="default", tags=["eyes"])
    if sent:
        print(f"  [NOTIF] Avertissement envoye pour {ticker}")


def notify_test() -> bool:
    return _post(
        title="Surveillance Higon — Connexion OK",
        body=f"L'outil est actif. Topic : {NTFY_TOPIC}",
        tags=["white_check_mark"],
    )
