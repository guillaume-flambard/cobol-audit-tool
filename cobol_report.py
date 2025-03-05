"""
Module de génération de rapports d'audit.
"""
from typing import Dict, Any
import markdown
from pypdf import PdfWriter
from datetime import datetime

class CobolReport:
    def __init__(self):
        self.template = """
# Rapport d'Audit COBOL

Date: {date}
Fichier analysé: {file_path}

## Vue d'Ensemble

Ce rapport présente une analyse détaillée du code COBOL, identifiant les problèmes potentiels
et fournissant des recommandations pour améliorer la qualité du code.

## Métriques de Code

- **Structure du Programme**
  - Lignes totales: {metrics[total_lines]}
  - Procédures: {metrics[procedures]}
  - Éléments de données: {metrics[data_items]}

- **Qualité du Code**
  - Complexité cyclomatique: {metrics[complexity]}
  - Variables non utilisées: {metrics[unused_vars]}
  - Sections vides: {metrics[empty_sections]}

- **Problèmes Détectés**
  - Erreurs: {error_count}
  - Avertissements: {warning_count}
  - Informations: {info_count}

## Détails des Problèmes

{issues}

## Recommandations

{recommendations}

## Bonnes Pratiques COBOL

- Éviter l'utilisation de GOTO au profit de structures de contrôle modernes
- Documenter clairement l'utilisation des FILLER
- Supprimer les variables non utilisées
- Fusionner ou supprimer les sections vides
- Maintenir une complexité cyclomatique raisonnable (< 10 par section)
"""

    def generate(self, analysis_results: Dict[str, Any], file_path: str, output_format: str = 'markdown') -> str:
        """Génère le rapport dans le format spécifié."""
        report_content = self._format_report(analysis_results, file_path)
        
        if output_format == 'markdown':
            return report_content
        elif output_format == 'pdf':
            return self._convert_to_pdf(report_content)
        else:
            raise ValueError(f"Format de sortie non supporté: {output_format}")

    def _format_report(self, results: Dict[str, Any], file_path: str) -> str:
        """Formate les résultats de l'analyse en rapport."""
        metrics = results['metrics']
        issues = results['issues']

        # Compte les problèmes par sévérité
        severity_count = {'ERROR': 0, 'WARNING': 0, 'INFO': 0}
        for issue in issues:
            severity_count[issue['severity']] += 1

        return self.template.format(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_path=file_path,
            metrics=metrics,
            error_count=severity_count['ERROR'],
            warning_count=severity_count['WARNING'],
            info_count=severity_count['INFO'],
            issues=self._format_issues(issues),
            recommendations=self._generate_recommendations(issues)
        )

    def _format_issues(self, issues: list) -> str:
        """Formate la section des problèmes."""
        if not issues:
            return "Aucun problème détecté."

        formatted_issues = []
        for issue in issues:
            formatted_issues.append(f"""
### {issue['severity']}: {issue['message']}
- Type: {issue['type']}
- Ligne: {issue.get('line', 'N/A')}
""")
        return "\n".join(formatted_issues)

    def _generate_recommendations(self, issues: list) -> str:
        """Génère des recommandations basées sur les problèmes détectés."""
        recommendations = set()
        
        for issue in issues:
            if issue['type'] == 'best_practice':
                recommendations.add("- Éviter l'utilisation de GOTO pour améliorer la lisibilité")
            elif issue['type'] == 'documentation':
                recommendations.add("- Améliorer la documentation des éléments FILLER")
            elif issue['type'] == 'structure':
                recommendations.add("- Vérifier la structure des divisions COBOL")
            elif issue['type'] == 'unused_variable':
                recommendations.add("- Supprimer ou utiliser les variables déclarées")
            elif issue['type'] == 'empty_section':
                recommendations.add("- Fusionner ou supprimer les sections vides")

        return "\n".join(recommendations) if recommendations else "Aucune recommandation spécifique."

    def _convert_to_pdf(self, markdown_content: str) -> bytes:
        """Convertit le contenu Markdown en PDF."""
        # Note: Cette méthode nécessiterait une implémentation plus complète
        # avec une bibliothèque de conversion HTML -> PDF
        html = markdown.markdown(markdown_content)
        # TODO: Implémenter la conversion HTML -> PDF
        return html.encode('utf-8') 