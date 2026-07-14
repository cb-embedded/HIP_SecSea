#!/usr/bin/env python3
"""
Génère les fichiers de fabrication JLCPCB pour le projet KiCad badge_secsea.
Usage: python generate_production.py [--drc-only]
"""

import subprocess
import sys
import json
import shutil
from pathlib import Path

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
PROJECT_ROOT = Path(__file__).parents[4]  # scripts/ → kicad-production-export/ → skills/ → .github/ → projet
PCB = PROJECT_ROOT / "badge_secsea_V1_1.kicad_pcb"
SCH = PROJECT_ROOT / "badge_secsea_V1_1.kicad_sch"
OUT_DIR = PROJECT_ROOT / "production"
GERBERS_DIR = OUT_DIR / "gerbers"
DRC_REPORT = PROJECT_ROOT / "drc_report.json"

# Violations connues, non bloquantes
KNOWN_VIOLATIONS = {"lib_footprint_issues", "silk_overlap", "silk_over_copper",
                    "silk_edge_clearance", "text_thickness"}


def run(cmd: list, label: str) -> subprocess.CompletedProcess:
    print(f"\n[{label}]")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    return result


def check_drc() -> bool:
    run([KICAD_CLI, "pcb", "drc",
         "--output", str(DRC_REPORT),
         "--format", "json",
         str(PCB)], "DRC")

    with open(DRC_REPORT, encoding="utf-8") as f:
        report = json.load(f)

    violations = report.get("violations", [])
    blocking = [v for v in violations if v.get("type") not in KNOWN_VIOLATIONS]
    known = [v for v in violations if v.get("type") in KNOWN_VIOLATIONS]

    print(f"\n  Violations connues (ignorées) : {len(known)}")
    if blocking:
        print(f"  VIOLATIONS BLOQUANTES : {len(blocking)}")
        for v in blocking:
            items = ", ".join(i.get("description", "") for i in v.get("items", []))
            print(f"    [{v['type']}] {v.get('description', '')} — {items}")
        return False

    print(f"  DRC OK — aucune violation bloquante.")
    return True


def generate_gerbers():
    GERBERS_DIR.mkdir(parents=True, exist_ok=True)
    run([KICAD_CLI, "pcb", "export", "gerbers",
         "--output", str(GERBERS_DIR), str(PCB)], "Gerbers")
    run([KICAD_CLI, "pcb", "export", "drill",
         "--output", str(GERBERS_DIR),
         "--format", "excellon", "--drill-origin", "absolute",
         str(PCB)], "Drill")


def generate_bom():
    run([KICAD_CLI, "sch", "export", "bom",
         "--output", str(OUT_DIR / "bom_jlcpcb.csv"),
         "--fields", "Value,Reference,Footprint,Supplier Part",
         "--labels", "Comment,Designator,Footprint,LCSC Part #",
         "--group-by", "Value,Footprint,Supplier Part",
         "--exclude-dnp",
         str(SCH)], "BOM")


def generate_cpl():
    cpl_path = OUT_DIR / "cpl_jlcpcb.csv"
    run([KICAD_CLI, "pcb", "export", "pos",
         "--output", str(cpl_path),
         "--format", "csv", "--units", "mm",
         "--side", "both", "--smd-only",
         str(PCB)], "CPL")

    # Renommer le header au format JLCPCB
    lines = cpl_path.read_text(encoding="utf-8").splitlines()
    lines[0] = '"Designator","Val","Package","Mid X","Mid Y","Rotation","Layer"'
    cpl_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  Header CPL mis au format JLCPCB.")


def main():
    drc_only = "--drc-only" in sys.argv

    print(f"Projet : {PROJECT_ROOT}")
    print(f"PCB    : {PCB.name}")

    ok = check_drc()
    if not ok:
        print("\nArrêt : violations bloquantes détectées. Corrigez le PCB avant de générer.")
        sys.exit(1)

    if drc_only:
        print("\nMode --drc-only : terminé.")
        return

    generate_gerbers()
    generate_bom()
    generate_cpl()

    print(f"\nFichiers générés dans : {OUT_DIR}")
    print(f"  Gerbers : {GERBERS_DIR}")
    print(f"  BOM     : {OUT_DIR / 'bom_jlcpcb.csv'}")
    print(f"  CPL     : {OUT_DIR / 'cpl_jlcpcb.csv'}")


if __name__ == "__main__":
    main()
