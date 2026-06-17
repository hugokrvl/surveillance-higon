# Méthode William Higon — Value Investing Small & Mid Cap Europe

> Ce fichier décrit la méthode de stock-picking de William Higon (Indépendance AM),
> gérant value européen depuis 1993, +4000% sur son fonds France Small & Mid.
> À utiliser comme référence pour scorer, filtrer ou analyser des actions.

---

## 1. SCREENING INITIAL — LES 3 CRITÈRES OBLIGATOIRES

Une action ne passe le filtre QUE si elle respecte les 3 conditions simultanément.

```
CRITÈRE 1 — Price Earning Ratio (PE)
  Formule  : PE = Cours de bourse / Bénéfice net par action (EPS)
  Seuil    : PE < 12
  Idéal    : PE entre 5 et 8 (zone "bas de cycle" ou "délaissée")
  Source   : derniers chiffres publiés (pas de prévisions)

CRITÈRE 2 — Return on Equity (ROE)
  Formule  : ROE = Bénéfice net / Fonds propres × 100
  Seuil    : ROE > 10 %
  Idéal    : ROE > 15 %
  Logique  : mesure la rentabilité réelle du capital investi

CRITÈRE 3 — Chiffre d'affaires
  Seuil    : CA en croissance (YoY positif)
  Logique  : filtre les sociétés en déclin structurel
```

**Règle d'or :** si les 3 critères sont verts → action éligible au portefeuille.

---

## 2. INDICATEURS COMPLÉMENTAIRES (analyse approfondie)

### 2a. BFR / Chiffre d'affaires
```
Formule : BFR = Créances clients + Stocks - Dettes fournisseurs
Ratio   : BFR_pct = BFR / CA × 100

Interprétation :
  BFR_pct < 20%  → excellent (fort pouvoir de négociation)
  BFR_pct 20-25% → acceptable
  BFR_pct > 25%  → signal d'alerte (creuser pourquoi)
  BFR_pct > 40%  → risque élevé, souvent à éviter
```

### 2b. Détection habillage de bilan
```
Formule : Taux_frais_fin = Frais financiers / Dette moyenne annuelle × 100

Si taux_frais_fin >> taux du marché → possible habillage de bilan au 31/12
  (la société rembourse de la dette temporairement pour paraître moins endettée)
```

### 2c. Cohérence du business model
```
Ratio 1 : CA par salarié = Chiffre d'affaires / Nombre de salariés
Ratio 2 : Immos par salarié = Immobilisations nettes / Nombre de salariés

Usage : comparer avec les pairs du secteur
  → Si "boîte tech" mais immos/salarié très élevées → pas vraiment tech
  → Détecte les sociétés qui se font passer pour ce qu'elles ne sont pas
```

### 2d. Niveau d'investissement (CAPEX)
```
Signal positif : CAPEX en hausse = dirigeants qui croient en leur marché
Signal négatif : CAPEX quasi nul + dividende élevé = société en mode "vache à lait"
  (Higon préfère les sociétés qui investissent plutôt que celles qui redistribuent)
```

---

## 3. RÈGLES D'ACHAT

```
Construction de position :
  - Taille cible par ligne : ~3% du portefeuille total
  - Nombre de lignes idéal : ~33 lignes (portefeuille concentré-diversifié)
  - Achat progressif : 3 tranches de 1/3 chacune, espacées dans le temps
  - Raison : lissage du prix d'entrée, surtout sur small caps peu liquides

Liquidité :
  - Ne jamais dépasser 20% du volume quotidien moyen sur le titre
  - Ex : volume journalier = 100k€ → max 20k€ par jour d'achat
  - Conséquence : une ligne peut prendre 30 à 60 jours à construire

Renforcement :
  - Si résultats > prévisions ET PE encore < 12 → renforcer la position
  - Si résultats > prévisions ET PE proche de 12 → ne rien faire
```

---

## 4. RÈGLES DE VENTE

```
Vente progressive sur PE croissant :
  PE atteint 15 → commencer à alléger (~20% de la position)
  PE atteint 17 → alléger encore
  PE atteint 20 → sortie complète (sauf exception justifiée)

Vente rationnelle :
  - Vendre 20% de la position à chaque hausse d'1 point de PE (entre 15 et 20)

Exception possible :
  - Thèse "extra-financière" forte (ex: guerre → armement)
  - Dans ce cas, garder malgré PE > 20, mais surveiller de près

Nettoyage semestriel (tous les 6 mois) :
  - Identifier les positions les plus négatives en perf relative
  - Couper les perdants même si on pense "c'est le marché qui a tort"
  - Logique : les titres qui baissent longtemps ont tendance à continuer
  - Source empirique : étude brokers US → les titres vendus surperforment,
    les titres gardés (perdants) continuent de sous-performer
```

---

## 5. CE QU'ON IGNORE DÉLIBÉRÉMENT

```
IGNORÉ                   RAISON
----------------------   -----------------------------------------
Dividendes               Critère statistiquement le moins prédictif
                         (ref: "What Works on Wall Street" v3/v4)
                         Préférer : Price/Book, Price/CF, Price/Earnings

Achats d'initiés         Les dirigeants sont rarement de bons boursiers
                         Exception : dirigeant qui achète massivement
                         APRÈS avoir vendu régulièrement → signal

Portefeuille concurrents Perte de temps, on ne connaît pas leur logique

Macro / taux             La plupart des sociétés cibles sont cash-positives
                         → taux peu impactants entre 1% et 3%

Prévisions analystes     On utilise UNIQUEMENT les derniers chiffres publiés

"Trop bien connaître"    Sur-connaissance = biais de surconfiance
la société               → on admet qu'on ne connaît jamais vraiment une société
```

---

## 6. UNIVERS D'INVESTISSEMENT

```
Géographie  : Europe (France prioritaire ~35% du gisement Small Cap Europe)
Taille      : Small & Mid Cap
  - Small   : capitalisation < 2 milliards €
  - Mid     : capitalisation < 10 milliards €
  - Large   : évité (trop efficient, ex: TotalEnergies = exception liquidité)

Secteurs évités habituellement :
  - Luxe          (valorisations trop élevées structurellement)
  - Pharma        (trop cher, binaire)
  - Tech pure     (tout le monde y va → surévaluation)

Secteurs appréciés :
  - Industriel
  - Services B2B
  - Défense (en période de tensions géopolitiques)
  - Médias (si délaissés et PE < 10)
```

---

## 7. SCORING RAPIDE (implémentation suggérée)

```python
def higon_score(pe, roe, ca_growth_pct, bfr_pct):
    """
    Retourne un score 0-100 et une recommandation.
    
    Paramètres:
        pe             : Price Earning Ratio (float)
        roe            : Return on Equity en % (float)
        ca_growth_pct  : Croissance CA YoY en % (float, négatif si baisse)
        bfr_pct        : BFR / CA en % (float)
    
    Retourne:
        dict avec score, statut, et détail par critère
    """
    score = 0
    detail = {}

    # --- Critère 1 : PE ---
    if pe <= 0:
        detail["PE"] = "INVALIDE (perte nette)"
    elif pe < 7:
        score += 40
        detail["PE"] = f"EXCELLENT ({pe:.1f}x) — zone bas de cycle"
    elif pe < 12:
        score += 30
        detail["PE"] = f"BON ({pe:.1f}x) — dans le filtre"
    elif pe < 15:
        score += 10
        detail["PE"] = f"LIMITE ({pe:.1f}x) — surveiller, commencer à alléger"
    elif pe < 20:
        score += 0
        detail["PE"] = f"ÉLEVÉ ({pe:.1f}x) — alléger progressivement"
    else:
        score -= 20
        detail["PE"] = f"TROP CHER ({pe:.1f}x) — sortir"

    # --- Critère 2 : ROE ---
    if roe >= 15:
        score += 30
        detail["ROE"] = f"EXCELLENT ({roe:.1f}%)"
    elif roe >= 10:
        score += 20
        detail["ROE"] = f"BON ({roe:.1f}%) — dans le filtre"
    elif roe >= 5:
        score += 5
        detail["ROE"] = f"FAIBLE ({roe:.1f}%) — sous le seuil"
    else:
        score -= 10
        detail["ROE"] = f"INSUFFISANT ({roe:.1f}%) — éliminatoire"

    # --- Critère 3 : Croissance CA ---
    if ca_growth_pct > 10:
        score += 20
        detail["CA"] = f"FORTE CROISSANCE (+{ca_growth_pct:.1f}%)"
    elif ca_growth_pct > 0:
        score += 15
        detail["CA"] = f"EN CROISSANCE (+{ca_growth_pct:.1f}%)"
    elif ca_growth_pct > -5:
        score += 0
        detail["CA"] = f"STABLE ({ca_growth_pct:.1f}%) — limite"
    else:
        score -= 15
        detail["CA"] = f"EN DÉCLIN ({ca_growth_pct:.1f}%) — éliminatoire"

    # --- Bonus/Malus BFR ---
    if bfr_pct < 20:
        score += 10
        detail["BFR"] = f"EXCELLENT ({bfr_pct:.1f}%) — fort pouvoir de négociation"
    elif bfr_pct < 25:
        score += 5
        detail["BFR"] = f"CORRECT ({bfr_pct:.1f}%)"
    elif bfr_pct < 35:
        score += 0
        detail["BFR"] = f"ÉLEVÉ ({bfr_pct:.1f}%) — creuser"
    else:
        score -= 10
        detail["BFR"] = f"TRÈS ÉLEVÉ ({bfr_pct:.1f}%) — signal d'alerte"

    # --- Recommandation finale ---
    eligible = pe > 0 and pe < 12 and roe >= 10 and ca_growth_pct > 0
    
    if not eligible:
        statut = "❌ HORS FILTRE — ne passe pas le screening de base"
    elif score >= 80:
        statut = "🟢 FORT — initier une position (3 tranches)"
    elif score >= 60:
        statut = "🟡 INTÉRESSANT — surveiller, attendre confirmation"
    else:
        statut = "🟠 LIMITE — ne pas initier, reconsidérer"

    return {
        "score": score,
        "eligible": eligible,
        "statut": statut,
        "detail": detail
    }


# Exemple : SAF-Holland (cas cité par Higon)
result = higon_score(pe=7, roe=13, ca_growth_pct=3, bfr_pct=22)
print(result)
# → score élevé, eligible True, statut FORT
```

---

## 8. EXEMPLES RÉELS CITÉS PAR HIGON

| Société | PE à l'achat | ROE | Thèse | Résultat |
|---|---|---|---|---|
| SAF-Holland | 7x | ~13% | Attelages camions, marché déprimé = bas de cycle | En portefeuille |
| Publicis | 8x | 17% | Covid = dépression temporaire, marge 17% | ×3 (30€ → 100€+) |
| TF1 | 7x | — | Reach publicitaire unique, TF1+ en développement | En portefeuille |
| Rheinmetall | Acheté bas | — | Guerre Ukraine → budgets défense | 120€ → 920€ |
| Dassault Aviation | Som of parts | — | Carnet plein 10 ans, production ×1.5 | +29% en 1 an |
| Viel & Cie | 6-7x | — | Croissance résultats depuis 2015, cours ×4 | Toujours en portefeuille |
| Mersen | 7x | — | Décalage 2 ans sur voiture élec = temporaire | Bien performé ensuite |

---

## 9. PHILOSOPHIE RÉSUMÉE EN 5 POINTS

```
1. ACHETER PAS CHER   → PE < 12, idéalement < 8
2. TRÈS RENTABLE      → ROE > 10%, idéalement > 15%
3. EN CROISSANCE      → CA qui monte (même légèrement)
4. SE LAISSER PORTER  → si bonnes nouvelles, renforcer ; ne pas trader
5. COUPER LES PERTES  → nettoyage semestriel, vendre les perdants sans pitié

"Il faut être discipliné : acheter des choses pas chères et très rentables,
 puis vous laisser porter par la vague."
                                        — William Higon
```

---

*Source : transcription interview FinTalk, épisode 2 avec William Higon (Indépendance AM)*
