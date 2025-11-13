# data_generator.py
"""
Générateur de données synthétiques pour tester l'assistant.
Utilise SynthCity pour produire de faux exemples de code et documentation.
"""

from synthcity.plugins import Plugins

def generate_synthetic_data():
    """
    Crée un petit jeu de données synthétiques simulant un projet.
    :return: dictionnaire contenant un 'code' et une 'documentation'
    """
    plugin = Plugins().get("adsgan")
    X, _ = plugin.generate(count=10)

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
