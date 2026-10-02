# ☂ MADA-ALERTE — Alerte précoce des fortes pluies à Madagascar

**Projet réalisé par Judicaël** · ✉ businessj49@gmail.com

Système de Data Science qui prédit, pour 12 villes de Madagascar, si le **lendemain** (J+1) connaîtra une **forte pluie (≥ 30 mm)** : inondations, routes coupées, retards de transport, risques agricoles.

## Données : RÉELLES et nombreuses (~64 000 exemples)
- **Source** : Open-Meteo Historical Weather API (réanalyse ERA5 / ECMWF), gratuite, sans clé.
- **12 villes** : Antananarivo, Toamasina, Mahajanga, Toliara, Antsiranana, Fianarantsoa, Antsirabe, Morondava, Sambava, Taolagnaro, Maroantsetra, Manakara.
- **Période** : 2012 → aujourd'hui, **1 ligne par ville et par jour**.
- **Variables** : températures (max/min/moy), pluie, vent max, rafales, rayonnement, + latitude, longitude, altitude.
- Les données sont **téléchargées automatiquement** au premier lancement (internet obligatoire) et gardées dans `data/raw/` (pour rafraîchir : supprimez ces CSV).
- Ce sont des données de **réanalyse** (grille ~25 km), pas des mesures de pluviomètre : bonnes pour un projet, pas pour un usage officiel.

> Le code est volontairement dense, sans commentaire et peu lisible (demande explicite). Il reste 100 % exécutable.

## Lancer
```bash
pip install -r requirements.txt
python run.py                                          # tout le pipeline (1re fois : téléchargement ~2-5 min)
python predict.py --ville Toamasina                    # risque pour DEMAIN, données en direct
python predict.py --ville Toamasina --date 2025-02-10  # rejouer un jour passé et comparer à la réalité
```
Terminal : bannière animée, barres de progression, tableaux colorés, jauge animée. Si les icônes s'affichent mal : `set MADA_PLAIN=1` (Windows) ou `export MADA_PLAIN=1` (Linux/Mac). Pour un affichage optimal sous Windows, utilisez **Windows Terminal**.

## Pipeline
1. **Collecte** API Open-Meteo (cache par ville)
2. **Nettoyage** doublons, valeurs manquantes/négatives, interpolation (≤ 3 jours), cohérence tmin ≤ tmax
3. **Préparation** pluie à J-1/J-2/J-3, cumuls 3/7/30 jours, anomalie thermique, rafales/vent, saison (sin/cos), géographie
4. **Analyse** taux d'alerte par ville, graphiques
5. **Entraînement & évaluation** découpage **temporel** : train 2012–2021, validation 2022–2023 (choix du seuil d'alerte), test ≥ 2024. Modèles : régression logistique et HistGradientBoosting, comparés à une baseline « persistance » et au hasard
6. **Sauvegarde** modèle (`models/mada_alerte.joblib`), `outputs/metrics.json`, `outputs/analyse_et_resultats.png`

Métriques adaptées à un événement rare : **PR-AUC, précision, rappel, F1** (l'accuracy serait trompeuse).

## Résultats
**À générer** avec `python run.py` : voir le tableau affiché et `outputs/metrics.json`. Aucun chiffre n'est écrit en dur.

## Structure
```
mada_alerte/
├── run.py  predict.py  requirements.txt  README.md
├── src/b.py   # style du terminal + signature (A= nom, E= email)
├── src/d.py   # téléchargement + nettoyage
├── src/p.py   # variables, modèles, évaluation, graphiques
├── data/raw  data/clean  models  outputs
```
Signature à modifier : `src/b.py`, ligne 8 (`A=` et `E=`).
