---
name: kicad-production-export
description: "Générer les fichiers de fabrication KiCad pour JLCPCB : DRC, Gerbers, BOM et CPL (placement). Utiliser pour préparer une commande JLCPCB, vérifier les DRC, exporter la BOM avec les numéros LCSC, ou regénérer les fichiers de production."
argument-hint: "Optionnel : 'drc-only' pour ne faire que la vérification"
---

# KiCad Production Export (JLCPCB)

## Contexte projet

- **Fichier PCB** : `badge_secsea_V1_1.kicad_pcb`
- **Fichier schéma** : `badge_secsea_V1_1.kicad_sch`
- **kicad-cli** : `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`
- **Numéros LCSC** : stockés dans le champ `Supplier Part` du schéma
- **Sortie** : `production/gerbers/` (Gerbers + drill), `production/bom_jlcpcb.csv`, `production/cpl_jlcpcb.csv`

## Avertissements DRC connus (non bloquants)

Les violations suivantes sont **attendues et non problématiques** :
- `lib_footprint_issues` → empreintes de la **Partek Library** (custom, embarquées dans le PCB). La lib est enregistrée dans `fp-lib-table` mais certains noms ne matchent pas exactement. Aucun impact sur la fabrication.
- `silk_overlap`, `silk_over_copper`, `silk_edge_clearance`, `text_thickness` → problèmes cosmétiques sérigraphie uniquement.

**Bloquer si** : `unconnected`, `clearance`, `via_dangling`, `courtyard_overlap` apparaissent.

## Procédure

### 1. DRC
Lancer le script Python ou la commande CLI, vérifier qu'aucune violation bloquante n'est présente.

### 2. Gerbers + Drill
```
kicad-cli pcb export gerbers --output production/gerbers <pcb>
kicad-cli pcb export drill --output production/gerbers --format excellon --drill-origin absolute <pcb>
```

### 3. BOM (format JLCPCB)
```
kicad-cli sch export bom
  --fields "Value,Reference,Footprint,Supplier Part"
  --labels "Comment,Designator,Footprint,LCSC Part #"
  --group-by "Value,Footprint,Supplier Part"
  --exclude-dnp
  --output production/bom_jlcpcb.csv <sch>
```

### 4. CPL / Placement (format JLCPCB)
```
kicad-cli pcb export pos --format csv --units mm --side both --smd-only
  --output production/cpl_jlcpcb.csv <pcb>
```
Puis renommer le header en : `"Designator","Val","Package","Mid X","Mid Y","Rotation","Layer"`

## Script automatisé

Utiliser [generate_production.py](./scripts/generate_production.py) pour tout faire en une commande :
```
python .github/skills/kicad-production-export/scripts/generate_production.py
```

> **Note** : `PROJECT_ROOT` est calculé via `Path(__file__).parents[4]` pour remonter de
> `scripts/ → kicad-production-export/ → skills/ → .github/ → racine projet`.
> Le script doit être invoqué depuis la racine du projet.

## Upload JLCPCB

1. Zipper `production/gerbers/*.g*` + `*.drl` → upload comme fichiers Gerber
2. `production/bom_jlcpcb.csv` → BOM
3. `production/cpl_jlcpcb.csv` → CPL/Positions
