# COBOL Audit Tool

Un outil d'audit pour analyser et évaluer la qualité du code COBOL.

## Fonctionnalités

- Analyse statique du code COBOL
- Détection des erreurs courantes et des anti-patterns
- Vérification des règles de codage
- Génération de rapports détaillés (Markdown/PDF)

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python main.py audit <fichier_cobol> [options]
```

Options disponibles:
- `--output-format`: Format du rapport (markdown/pdf)
- `--rules-config`: Fichier de configuration des règles
- `--verbose`: Mode verbeux pour plus de détails

## Structure du Projet

```
📁 cobol-audit-tool/
│── 📜 cobol_parser.py        # Parseur COBOL
│── 📜 cobol_analyzer.py      # Analyse des erreurs
│── 📜 cobol_report.py        # Génération du rapport
│── 📜 cli.py                 # Interface CLI
│── 📜 main.py                # Script principal
│── 📁 tests/                 # Tests
│── 📜 requirements.txt       # Dépendances
│── 📜 README.md             # Documentation
```

## Développement

Pour contribuer au projet:

1. Cloner le dépôt
2. Installer les dépendances de développement
3. Exécuter les tests: `pytest tests/`
4. Soumettre une pull request

## Licence

MIT License 