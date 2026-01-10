# RAPPORT TECHNIQUE DÉTAILLÉ - PARTIE 2
# ARCHITECTURE ET MODULES DÉTAILLÉS

---

## 2.1 Architecture générale du système

Le Documentation Consistency Assistant repose sur une architecture modulaire stratifiée qui organise clairement les différentes responsabilités du système. Cette organisation en couches distinctes facilite grandement la maintenance du code, permet son évolution progressive et simplifie considérablement les tests. L'architecture se compose de quatre couches principales qui interagissent de manière unidirectionnelle pour traiter les données de l'entrée jusqu'à la sortie.

La première couche est celle de l'interface utilisateur, représentée par le fichier app.py qui utilise le framework Streamlit. Cette couche gère les interactions avec l'utilisateur pour l'upload d'archives ZIP et la validation sécuritaire des entrées avant tout traitement. La deuxième couche est celle de l'orchestration, incarnée par le module project_analyzer.py, qui coordonne l'ensemble du processus d'analyse en appelant successivement les différents modules spécialisés. La troisième couche est celle de l'analyse, regroupée dans le dossier analyzer, qui contient tous les modules responsables de l'extraction et de l'interprétation des données du projet. Enfin, la quatrième couche est celle de la génération, située dans le dossier generator, qui produit les suggestions, les visualisations et les diagrammes à partir des résultats d'analyse.

Cette séparation en couches offre plusieurs avantages significatifs pour le développement et la maintenance du projet. Chaque module peut être développé, testé et maintenu de manière indépendante sans affecter les autres parties du système. Les modules peuvent être réutilisés dans différents contextes, que ce soit une interface en ligne de commande, une API REST ou une interface web. L'ajout de nouvelles fonctionnalités se fait par extension plutôt que par modification du code existant, ce qui réduit le risque d'introduire des régressions. La séparation des préoccupations facilite la compréhension du code pour les nouveaux développeurs et simplifie la correction des bugs.

## 2.2 Modules d'analyse du code et de la documentation - Architecture multi-langue

Le cœur du système d'analyse repose sur deux approches complémentaires qui extraient respectivement les informations du code source et de la documentation avec support multi-langue.

### Parsing multi-langue avec SimpleRegexParser

Le module **regex_parser** implementé en version 2.1.0 utilise des expressions régulières spécifiques à chaque langage pour analyser le code sans dépendre de binaires externes. Cette approche offre plusieurs avantages critiques:

1. **Zéro dépendances binaires**: Aucun compilateur ou bibliothèque native requise
2. **Support multi-langue**: Java, Go, JavaScript, TypeScript, C/C++, Rust, C#, PHP, Ruby, Python
3. **Déploiement cloud-ready**: Fonctionne sur toutes les plateformes (Streamlit Cloud, Lambda, Docker, etc.)
4. **Performance**: Analyse O(n) linéaire basée sur le nombre de fichiers

Le SimpleRegexParser parcourt récursivement l'arborescence du projet en cherchant les fichiers supportés selon leur extension. Pour chaque fichier, il applique les patterns regex spécifiques au langage pour extraire:
- Classes et structures
- Fonctions et méthodes
- Numéros de ligne
- Métadonnées par langage

### Parsing Python natif avec Python AST

Pour les projets Python, le système utilise le **module ast** de la bibliothèque standard Python qui offre une analyse plus précise et complète que regex. Le AST parser extrait:
- Classes avec héritage
- Fonctions autonomes et méthodes
- Docstrings complets
- Signatures de fonction et paramètres
- Métadonnées détaillées

Ce parser est activé comme fallback automatique lorsque SimpleRegexParser trouve zéro éléments, garantissant une couverture maximale pour les projets Python.

Le module doc_parser complète cette extraction en parcourant le projet à la recherche de fichiers de documentation. Il supporte plusieurs formats courants comme le Markdown, le texte brut et le reStructuredText. Le système porte une attention particulière aux fichiers spéciaux comme README, CHANGELOG ou CONTRIBUTING qui constituent souvent la documentation principale d'un projet. Pour chaque fichier de documentation trouvé, le contenu est lu, normalisé et indexé par nom de fichier pour faciliter les recherches ultérieures. Les deux parseurs gèrent de manière robuste les erreurs potentielles comme les fichiers illisibles, les erreurs de syntaxe Python ou les problèmes d'encodage, et enregistrent ces événements dans les logs pour assurer la traçabilité.

## 2.3 Comparaison et détection des incohérences

Une fois les données extraites du code et de la documentation, le module comparator entre en jeu pour identifier les incohérences. C'est le cœur de la logique métier du système. Le comparateur examine méthodiquement chaque élément de code identifié et cherche sa mention dans la documentation existante. Pour chaque classe découverte dans le code, le système parcourt tous les fichiers de documentation à la recherche du nom de cette classe. Si aucune mention n'est trouvée, la classe est marquée comme non documentée et une issue est créée avec toutes les informations contextuelles pertinentes comme le nom du fichier, le numéro de ligne et la présence ou absence d'une docstring dans le code.

Le processus se répète pour les fonctions et les méthodes, mais avec des niveaux de sévérité différents qui permettent de prioriser les efforts de documentation. Les classes non documentées sont considérées comme des problèmes critiques car elles représentent souvent des composants majeurs de l'architecture du projet. Les fonctions publiques non documentées sont classées comme des avertissements, tandis que les méthodes individuelles constituent des problèmes mineurs. Cette hiérarchisation aide les développeurs à concentrer leurs efforts là où ils auront le plus d'impact.

Le système calcule également un score global de santé documentaire qui offre une métrique rapide et compréhensible de l'état de la documentation. Ce score part de cent et diminue en fonction du nombre et de la gravité des issues détectées. Chaque issue critique retire cinq points au score, chaque avertissement en retire deux et chaque issue mineure en retire un. Le score final est normalisé pour rester dans la plage de zéro à cent, ce qui permet des comparaisons faciles entre différents projets ou différentes versions d'un même projet au fil du temps.

## 2.4 Modules de génération de contenu

Après avoir identifié les problèmes, le système génère automatiquement du contenu pour aider à les résoudre. Le module text_suggester crée des suggestions textuelles personnalisées pour chaque élément non documenté. Si le mode LLM est activé et qu'une clé API OpenAI est disponible, le système utilise l'intelligence artificielle pour analyser le code de chaque élément et générer des descriptions contextuelles pertinentes avec des exemples d'utilisation réalistes. Sans LLM, le système se rabat sur un mode heuristique qui fournit des templates de documentation structurés que le développeur peut adapter à son contexte spécifique.

Le module visual_creator complète ces suggestions textuelles en générant des visualisations graphiques qui rendent les résultats immédiatement compréhensibles. Le système crée des graphiques en barres montrant la distribution des issues par catégorie, des diagrammes circulaires illustrant le ratio entre éléments documentés et non documentés, et des jauges visuelles représentant le score global de santé. Ces visualisations sont exportées en haute définition au format PNG pour être directement utilisables dans des présentations ou des rapports de qualité.

Le module mermaid_generator, ajouté lors des améliorations de la version 2.1.0, génère des diagrammes au format Mermaid qui peuvent être directement intégrés dans des fichiers Markdown. Ces diagrammes incluent un flowchart représentant le processus d'analyse complet, un diagramme de classes montrant la structure du projet analysé, et des graphiques de répartition des issues par type. L'avantage majeur des diagrammes Mermaid est qu'ils sont du texte pur, donc versionables avec Git, et ils sont rendus automatiquement par les plateformes comme GitHub et GitLab sans nécessiter d'images externes.

## 2.5 Orchestration et interface utilisateur

Le module project_analyzer joue le rôle de chef d'orchestre en coordonnant tous les autres modules. Il instancie les parseurs de code et de documentation, exécute les analyses dans le bon ordre, passe les données entre les modules et agrège les résultats finaux dans un format structuré exploitable. Ce module gère également la détection automatique de la disponibilité des composants optionnels comme LangChain et OpenAI pour le mode LLM, et effectue un fallback gracieux vers le mode heuristique si ces dépendances ne sont pas disponibles.

L'interface utilisateur dans app.py expose toutes ces fonctionnalités de manière conviviale grâce au framework Streamlit. Les utilisateurs peuvent uploader un fichier ZIP contenant leur projet et, si besoin, un second ZIP pour la documentation additionnelle.

La sécurité est une préoccupation majeure de la couche interface. Avant d'accepter un fichier ZIP, le système effectue cinq vérifications distinctes. Il vérifie d'abord que la taille du fichier ne dépasse pas la limite configurée pour éviter les uploads excessifs. Il confirme ensuite que le fichier est bien une archive ZIP valide. Une vérification cruciale détecte les ZIP bombs en calculant le ratio de compression et en rejetant toute archive qui dépasserait un facteur de cent fois. Le système examine également chaque nom de fichier dans l'archive pour détecter les tentatives de traversée de répertoire qui pourraient permettre d'écrire en dehors du répertoire prévu. Enfin, une limite sur le nombre total de fichiers dans l'archive protège contre les attaques par épuisement de ressources.

Les résultats sont présentés de manière claire et organisée avec des métriques clés affichées en haut de page offrant une vue d'ensemble instantanée. Les détails sont organisés en onglets thématiques qui séparent les issues détectées, les suggestions générées, les visualisations graphiques, les diagrammes Mermaid et les données brutes au format JSON. Cette organisation facilite la navigation et permet à chaque utilisateur de se concentrer sur les informations qui l'intéressent le plus selon son rôle et ses besoins.

## 2.6 Conclusion de la partie 2

Cette partie a présenté l'architecture technique complète du Documentation Consistency Assistant en détaillant l'organisation en couches, les modules d'analyse et de génération, l'orchestration du pipeline et l'interface utilisateur sécurisée. Cette architecture modulaire garantit la maintenabilité du code, facilite son évolution et simplifie les tests. La prochaine partie explorera en détail le flux d'exécution complet de l'analyse depuis la validation des entrées jusqu'à la présentation des résultats.
