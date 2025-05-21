import sys

print(f"Running smoke test with Python {sys.version}")

try:
    import resnap
except ImportError as e:
    raise RuntimeError("❌ Échec de l'import du module principal.") from e

# Vérifions qu’une fonction ou classe clé est présente
assert hasattr(resnap, "resnap"), "❌ La fonction 'resnap' est manquante dans le package."

print("✅ Smoke test passed.")
