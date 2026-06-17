# ── Configuration outil de surveillance Higon ──────────────────────────────

# Ta liste d'actions à surveiller (tickers Yahoo Finance)
# Format : "TICKER.EXCHANGE" — exemples :
#   Paris   → ".PA"   (ex: RNO.PA, DG.PA)
#   Londres → ".L"    (ex: BATS.L)
#   USA     → pas de suffixe (ex: AAPL)
WATCHLIST = [
    # Small/Mid caps France (univers Higon par défaut)
    "RNO.PA",    # Renault
    "DG.PA",     # Vinci
    "TFI.PA",    # TF1
    "VIEL.PA",   # Viel & Cie (ticker Yahoo : VIEL.PA)
    "MRN.PA",    # Mersen
    "PUB.PA",    # Publicis
    "AIR.PA",    # Airbus
    "AM.PA",     # Dassault Aviation
    "RHM.DE",    # Rheinmetall
    "SOP.PA",    # Sopra Steria
    # "HARF.PA",   # Haropa — pas cote en bourse
    "IDL.PA",    # ID Logistics
    "MTX.DE",    # Stratec Biomedical
    # Ajoute tes propres tickers ici
]

# ── Critères Higon (modifiable) ────────────────────────────────────────────
PE_MAX        = 12    # PE strict (éliminatoire si dépassé)
PE_IDEAL_MAX  = 8     # PE "zone idéale"
ROE_MIN       = 10    # ROE minimum en % (éliminatoire si inférieur)
ROE_IDEAL     = 15    # ROE "zone idéale"
CA_GROWTH_MIN = 0     # Croissance CA minimum en % (YoY)
BFR_ALERT     = 25    # BFR/CA % au-dessus duquel on alerte

# ── Notification téléphone via ntfy.sh (GRATUIT) ──────────────────────────
# 1. Télécharge l'app "ntfy" sur ton téléphone (Android/iOS)
# 2. Abonne-toi au topic ci-dessous dans l'app
# 3. Tu recevras les alertes en temps réel
NTFY_TOPIC    = "higon-surveillance-hugo"   # Change ce nom (doit être unique)
NTFY_SERVER   = "https://ntfy.sh"

# ── Fréquence de scan ──────────────────────────────────────────────────────
# PE change avec le cours (quotidien), ROE/CA/BFR changent trimestriellement
# -> 1 scan par jour apres cloture suffit largement
SCAN_INTERVAL_MINUTES = 1440   # 1 fois par jour (24h)
SCAN_TIME = "18:00"            # heure de declenchement (apres cloture Paris)

# ── Seuil de score pour déclencher une notif ──────────────────────────────
# Score calculé selon william_higon_method.md
SCORE_NOTIF_MIN = 60   # notif si score >= 60 ET critères de base respectés
