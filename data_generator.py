# data_generator.py
"""
Générateur de données synthétiques pour tester l'assistant.
Utilise SynthCity pour produire de faux exemples de code et documentation.
"""

try:
    from synthcity.plugins import Plugins
except Exception:
    # Fallback dummy Plugins implementation when synthcity is not installed
    class Plugins:
        def __init__(self):
            pass

        def get(self, name):
            class DummyPlugin:
                def generate(self, count=1):
                    # Return a simple fake dataframe-like object with head().to_dict()
                    class FakeDataFrame:
                        def __init__(self, rows):
                            self._rows = rows

                        def head(self):
                            return self

                        def to_dict(self):
                            # represent as dict similar to pandas.DataFrame.to_dict()
                            return {i: row for i, row in enumerate(self._rows)}

                    rows = [{
                        'file': 'example.py',
                        'code': "def calculate_total(price, tax):\n    return price + (price * tax)"
                    }] * count
                    return FakeDataFrame(rows), None
            return DummyPlugin()

def generate_synthetic_data():
    """
    Crée un petit jeu de données synthétiques simulant un projet.
    :return: dictionnaire contenant un 'code' et une 'documentation'
    """
    try:
        plugin = Plugins().get("adsgan")
        X, _ = plugin.generate(count=10)
    except Exception as e:
        print(f"Warning: Could not generate synthetic data: {e}")
        X = None

    code_example = """
    def calculate_total(price, tax):
        '''Calcule le total avec taxe'''
        return price + (price * tax)
    """

    doc_example = """
    ## Fonction : calculate_total
    - Description : Calcule le prix total d'un produit avec la taxe incluse.
    - Paramètres :
        - price (float) : Prix de base
        - tax (float) : Taux de taxe
    """

    return {
        "code": code_example,
        "docs": doc_example,
        "synthetic_data": X.head().to_dict()
    }
