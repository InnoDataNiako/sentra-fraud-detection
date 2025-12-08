#!/usr/bin/env python3
"""
Script pour diagnostiquer les problèmes d'import
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔍 Diagnostic des imports...")

modules_to_test = [
    "src.api.routes.health",
    "src.api.routes.detection", 
    "src.api.routes.transactions",
    "src.api.routes.metrics"
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module} - IMPORT RÉUSSI")
    except Exception as e:
        print(f"❌ {module} - ERREUR: {e}")
        import traceback
        traceback.print_exc()
        print("---")