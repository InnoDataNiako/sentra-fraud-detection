"""
Script pour exécuter tous les tests avec reporting complet
Usage: python scripts/run_tests.py [options]
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def print_banner(text: str):
    """Affiche un banner"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_command(cmd: list, description: str) -> bool:
    """Exécute une commande et retourne le succès"""
    print(f"▶️  {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} - SUCCÈS\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ÉCHEC (code: {e.returncode})\n")
        return False


def main():
    parser = argparse.ArgumentParser(description="Exécute les tests SÉNTRA")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "api", "coverage"],
        default="all",
        help="Type de tests à exécuter"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mode verbeux"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Tests rapides uniquement"
    )
    
    args = parser.parse_args()
    
    print_banner(f"🧪 TESTS SÉNTRA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 1️⃣ Tests unitaires
    if args.type in ["all", "unit"]:
        print_banner("1️⃣  TESTS UNITAIRES")
        cmd = ["pytest", "tests/test_services.py", "-v"]
        if args.verbose:
            cmd.append("-vv")
        if args.fast:
            cmd.extend(["-m", "not slow"])
        
        results.append(("Tests Unitaires", run_command(cmd, "Tests unitaires des services")))
    
    # 2️⃣ Tests d'intégration API
    if args.type in ["all", "integration", "api"]:
        print_banner("2️⃣  TESTS D'INTÉGRATION API")
        cmd = ["pytest", "tests/test_api_integration.py", "-v"]
        if args.verbose:
            cmd.append("-vv")
        
        results.append(("Tests API", run_command(cmd, "Tests d'intégration API")))
    
    # 3️⃣ Couverture de code
    if args.type in ["all", "coverage"]:
        print_banner("3️⃣  COUVERTURE DE CODE")
        cmd = [
            "pytest",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=json"
        ]
        if args.verbose:
            cmd.append("-v")
        
        results.append(("Couverture", run_command(cmd, "Analyse de couverture")))
    
    # 4️⃣ Résumé
    print_banner("📊 RÉSUMÉ DES TESTS")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    for name, success in results:
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"{status:15} - {name}")
    
    print(f"\n{'=' * 70}")
    print(f"Total: {total} | Réussis: {passed} | Échoués: {failed}")
    print(f"Taux de réussite: {(passed/total)*100:.1f}%")
    print(f"{'=' * 70}\n")
    
    # 5️⃣ Rapport de couverture
    if args.type in ["all", "coverage"]:
        print("📈 Rapport de couverture HTML généré dans: htmlcov/index.html")
        print("💡 Ouvrir avec: python -m http.server 8080 --directory htmlcov\n")
    
    # 6️⃣ Code de sortie
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()