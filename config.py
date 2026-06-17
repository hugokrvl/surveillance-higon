# ── Configuration outil de surveillance Higon ──────────────────────────────

# Ta liste d'actions à surveiller (tickers Yahoo Finance)
# Format : "TICKER.EXCHANGE" — exemples :
#   Paris   → ".PA"   (ex: RNO.PA, DG.PA)
#   Londres → ".L"    (ex: BATS.L)
#   USA     → pas de suffixe (ex: AAPL)
# Univers Higon : small & mid caps France + Europe (314 actions)
# Genere via build_watchlist.py (CAC Mid60+Small + indices Wikipedia EU)
WATCHLIST = [
    # ── France (93) ──────────────────────────────────
    "ABCA.PA", "ABIO.PA", "AC.PA", "ACAN.PA", "AF.PA", "ALBI.PA",
    "ALBLD.PA", "ALO.PA", "ALTUR.PA", "ALWIT.PA", "AMUN.PA", "ASY.PA",
    "ATEME.PA", "AURS.PA", "BEN.PA", "BIG.PA", "BIM.PA", "BOI.PA",
    "BOL.PA", "BVI.PA", "CARP.PA", "CLARI.PA", "COFA.PA", "COV.PA",
    "CRI.PA", "DIM.PA", "DPAM.PA", "ELEC.PA", "ELIOR.PA", "EMEIS.PA",
    "EN.PA", "ERA.PA", "FGR.PA", "FII.PA", "FNAC.PA", "GBT.PA",
    "GENFIT.PA", "GET.PA", "GL.PA", "GLO.PA", "GTT.PA", "HEX.PA",
    "ICAD.PA", "IDIP.PA", "IDL.PA", "IPS.PA", "KOF.PA", "LACR.PA",
    "LGTH.PA", "LSS.PA", "MALT.PA", "MDM.PA", "MF.PA", "MGI.PA",
    "MLAFP.PA", "MLNAM.PA", "MMB.PA", "MMT.PA", "MRN.PA", "NETG.PA",
    "NEX.PA", "NK.PA", "NXI.PA", "OCRI.PA", "OEIMF.PA", "OENEO.PA",
    "ORAP.PA", "POM.PA", "PREC.PA", "RCO.PA", "RF.PA", "ROTH.PA",
    "RUI.PA", "RXL.PA", "SAVE.PA", "SCR.PA", "SCo.PA", "SESG.PA",
    "SFCA.PA", "SFT.PA", "SII.PA", "SK.PA", "SMCP.PA", "SOP.PA",
    "SPIE.PA", "SQLI.PA", "TEP.PA", "TFFP.PA", "THEP.PA", "TRI.PA",
    "VIEL.PA", "VIRP.PA", "WLN.PA",
    # ── Allemagne (49) ───────────────────────────────
    "AFX.DE", "AIXA.DE", "AT1.DE", "BC8.DE", "BFSA.DE", "BOSS.DE",
    "DHER.DE", "ECV.DE", "EVD.DE", "EVK.DE", "EVT.DE", "FNTN.DE",
    "FPE3.DE", "FRA.DE", "FRE.DE", "G1A.DE", "G24.DE", "GBF.DE",
    "GXI.DE", "HAG.DE", "HFG.DE", "HLE.DE", "HOT.DE", "JEN.DE",
    "JUN3.DE", "KBX.DE", "KGX.DE", "KRN.DE", "LEG.DE", "LHA.DE",
    "LXS.DE", "NDA.DE", "NDX1.DE", "NEM.DE", "PUM.DE", "RAA.DE",
    "RDC.DE", "RRTL.DE", "SAX.DE", "SDF.DE", "STM.DE", "TEG.DE",
    "TKA.DE", "TLX.DE", "TMV.DE", "TUI1.DE", "UTDI.DE", "WAF.DE",
    "WCH.DE",
    # ── Pays-Bas (49) ────────────────────────────────
    "AALB.AS", "ABN.AS", "AD.AS", "ADYEN.AS", "AF.AS", "AGN.AS",
    "AKZA.AS", "ALFEN.AS", "AMG.AS", "APAM.AS", "ARCAD.AS", "ASM.AS",
    "ASML.AS", "ASRNL.AS", "BESI.AS", "BFIT.AS", "BOKA.AS", "CRBN.AS",
    "DSFIR.AS", "ECMPA.AS", "EXO.AS", "FAGR.AS", "FLOW.AS", "FUR.AS",
    "GLPG.AS", "GVNV.AS", "HEIA.AS", "IMCD.AS", "INGA.AS", "INPST.AS",
    "INTER.AS", "JDEP.AS", "KPN.AS", "MT.AS", "NN.AS", "OCI.AS",
    "PHIA.AS", "PNL.AS", "PRX.AS", "RAND.AS", "REN.AS", "SBMO.AS",
    "SHELL.AS", "TWEKA.AS", "UMG.AS", "UNA.AS", "VPK.AS", "WDP.AS",
    "WKL.AS",
    # ── Espagne (35) ─────────────────────────────────
    "ACS.MC", "ACX.MC", "AENA.MC", "AMS.MC", "ANA.MC", "ANE.MC",
    "BBVA.MC", "BKT.MC", "CABK.MC", "CLNX.MC", "COL.MC", "ELE.MC",
    "ENG.MC", "FDR.MC", "FER.MC", "GRF.MC", "IAG.MC", "IBE.MC",
    "IDR.MC", "ITX.MC", "LOG.MC", "MAP.MC", "MRL.MC", "MTS.MC",
    "NTGY.MC", "PUIG.MC", "RED.MC", "REP.MC", "ROVI.MC", "SAB.MC",
    "SAN.MC", "SCYR.MC", "SLR.MC", "TEF.MC", "UNI.MC",
    # ── Italie (40) ──────────────────────────────────
    "A2A.MI", "AMP.MI", "AVIO.MI", "AZM.MI", "BAMI.MI", "BC.MI",
    "BMED.MI", "BMPS.MI", "BPE.MI", "BZU.MI", "CPR.MI", "DIA.MI",
    "ENEL.MI", "ENI.MI", "FBK.MI", "FCT.MI", "G.MI", "HER.MI",
    "IG.MI", "INW.MI", "ISP.MI", "IVG.MI", "LDO.MI", "LTMC.MI",
    "MB.MI", "MONC.MI", "NEXI.MI", "PRY.MI", "PST.MI", "RACE.MI",
    "REC.MI", "SPM.MI", "SRG.MI", "STLAM.MI", "STMMI.MI", "TEN.MI",
    "TIT.MI", "TRN.MI", "UCG.MI", "UNI.MI",
    # ── Suede (30) ───────────────────────────────────
    "ABB.ST", "ADDT-B.ST", "ALFA.ST", "ASSA-B.ST", "ATCO-A.ST", "AZN.ST",
    "BOL.ST", "EPI-A.ST", "EQT.ST", "ERIC-B.ST", "ESSITY-B.ST", "EVO.ST",
    "HEXA-B.ST", "HM-B.ST", "INDU-C.ST", "INVE-B.ST", "LIFCO-B.ST", "NDA-SE.ST",
    "NIBE-B.ST", "SAAB-B.ST", "SAND.ST", "SCA-B.ST", "SEB-A.ST", "SHB-A.ST",
    "SKA-B.ST", "SKF-B.ST", "SWED-A.ST", "TEL2-B.ST", "TELIA.ST", "VOLV-B.ST",
    # ── Portugal (18) ────────────────────────────────
    "ALTR.LS", "BCP.LS", "COR.LS", "CTT.LS", "EDP.LS", "EDPR.LS",
    "EGL.LS", "GALP.LS", "IBS.LS", "JMT.LS", "NBA.LS", "NOS.LS",
    "NVG.LS", "PHR.LS", "RENE.LS", "SEM.LS", "SON.LS", "SONC.LS",
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
