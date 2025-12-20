# data_generator.py
"""
Générateur de données synthétiques pour tester l'assistant.
Utilise SynthCity si disponible pour produire des exemples de code et documentation.
"""

from typing import Any, Dict

# 🔹 Import SynthCity Plugins avec fallback
try:
    from synthcity.plugins import Plugins
except ImportError:
    class Plugins:
        def __init__(self):
            pass

        def get(self, name: str):
            class DummyPlugin:
                def generate(self, count: int = 1):
                    class FakeDataFrame:
                        def __init__(self, rows: list):
                            self._rows = rows

                        def head(self) -> "FakeDataFrame":
                            return self

                        def to_dict(self) -> dict:
                            return {i: row for i, row in enumerate(self._rows)}

                    rows = [{
                        "file": "example.py",
                        "code": "def calculate_total(price, tax): return price + price*tax"
                    }] * count
                    return FakeDataFrame(rows), None
            return DummyPlugin()


# 🔹 Génération des données synthétiques
def generate_synthetic_data(count: int = 10) -> Dict[str, Any]:
    """
    Crée un petit jeu de données synthétiques simulant un projet.
    :param count: nombre d'exemples à générer
    :return: dictionnaire contenant 'code', 'docs' et 'synthetic_data'
    """
    try:
        plugin = Plugins().get("adsgan")
        X, _ = plugin.generate(count=count)
    except Exception:
        X = None

    code_example = """\
def calculate_total(price, tax):
    '''Calcule le total avec taxe'''
    return price + (price * tax)
"""

    doc_example = """\
## Fonction : calculate_total
- Description : Calcule le prix total d'un produit avec la taxe incluse.
- Paramètres :
    - price (float) : Prix de base
    - tax (float) : Taux de taxe
"""

    return {
        "code": code_example,
        "docs": doc_example,
        "synthetic_data": X.head().to_dict() if X is not None else None
    }


# 🔹 Test rapide
if __name__ == "__main__":
    data = generate_synthetic_data()
    print(data["code"])
    print(data["docs"])
    print(data["synthetic_data"])